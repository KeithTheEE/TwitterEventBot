

# THE PLOT BLOCK
from utils import rpiGPIOFunctions
rPI = rpiGPIOFunctions.checkHardware()

if rPI:
    import matplotlib as mpl
    mpl.use('Agg') # Backend for plotting on the pi 
    
import matplotlib.pyplot as plt
#import matplotlib.mlab as mlab
import matplotlib.dates as mdates

# And now back to your regularly scheduled imports
import time
import datetime
import numpy as np
import scipy.stats
import logging





from sklearn.neighbors import KernelDensity

from utils import botHelperFunctions
from utils import twitterInteractions



def updateKDE(kdeOld, runTime='3_AM', runWindow=3, minAgeHours=8):
    """
    Generates the KDE over the event history for each events
    This is done at startup, and once per day at approximately 
    3 am CDT (VERIFY/SET AS VARIBLE)
    `updateKDE` also functions as the source of historical averages 

    Parameters
    ----------
    kdeOld : list or Nonetype
    

    Returns
    -------

    Other Parameters
    ----------------

    Raises
    ------

    See Also
    --------

    Notes
    -----
    Start condition should be if `kdeOld` == "None"
    Suggested condition should be if time is greater than 2 and 
    last set is greater than 23, reset kde OR if time is greater 
    than two and last reboot is less than 23

    * Consider triggering this instead of time.sleep 
    in the state machine 

    ** Consider updating only one KDE at a time, then running through
       the event search space. That way there isn't massive downtime 
       on the pi, minimizing missed events. 
         Should be simple enough to do. 
         This would naturally be ignored on startup KDE (kdeOld == None)


    """
    def convertRunTime(rt):
        time, ampm = rt.split('_')
        if ':' in time:
            hour, minute = time.split(':')
        else:
            hour = time
            minute = '00'
        if ampm.upper() == 'PM':
            hour = int(hour) + 12
        hour = int(hour)
        minute = int(minute)
        dt = datetime.datetime.now()
        dt = dt.replace(hour=hour, minute=minute)
        return dt

    logging.debug( "Updating KDE..")

    conditional = False

    # Decide if condition is met
    if kdeOld == None:
        # This only runs on startup
        conditional = True
        kdeOld = []
    else:
        # Checks if it's After 3 am, and has been more than 8 hours since last update
        runTime = convertRunTime(runTime)
        dontRunAfter=runTime+datetime.timedelta(seconds=runWindow*3600)

        lastRun = botHelperFunctions.getLoggedData("Last KDE Update:")
        lastRun = datetime.datetime.strptime(lastRun,'%Y-%m-%d %H:%M')

        delta = datetime.datetime.now() - lastRun

        if delta.seconds >= minAgeHours*3600:
            if datetime.datetime.now() > runTime:
                if datetime.datetime.now() < dontRunAfter:
                    conditional = True
                    kdeOld = []


    if conditional:
        rpiGPIOFunctions.myLED("KDEPREP")
        searchEV = botHelperFunctions.eventLists()
        for event in searchEV:
            theTimesX, allHistAvgsX = botHelperFunctions.getEventHistoryTimeLimit(event, weeks=-1, days=0, hours=0, minutes=0)
            histAvg, histStd = botHelperFunctions.getEventHistoryStats(allHistAvgsX)
            # adjsut all hist avgs to last year here
            theTimes, allHistAvgs = botHelperFunctions.getEventHistoryTimeLimit(event, weeks=0, days=365, hours=0, minutes=0)
            yearAvg, yearStd = botHelperFunctions.getEventHistoryStats(allHistAvgs)

            x1 = np.linspace(0, int(yearAvg+(3*yearStd)), int(100*(6*yearStd)))
            allHistAvgs = np.array(allHistAvgs)
            allHistAvgs = allHistAvgs[:, None]
            X_plot = np.linspace(0, int(yearAvg+(3*yearStd)), len(allHistAvgs))[:, None]
            # KDE For Event
            maxPoint = max(allHistAvgs)
            bw = float(maxPoint)*0.012
            kde = KernelDensity(kernel='epanechnikov', bandwidth=bw)
            kde.fit(allHistAvgs)
            log_dens = kde.score_samples(X_plot)
            kdeOld.append([(X_plot, log_dens), allHistAvgsX, histAvg, histStd])

        logging.debug( "Updated KDE")
        logLine = "Last KDE Update:\t"+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        botHelperFunctions.updateLogFile(logLine)
        logging.info(logLine)


    
    return kdeOld



def plotSummaries(api, runOn='FRI', runTime='6_PM', minAgeDays=4, quietMode=False):
    """
    If it's Sunday Night and the system has been online for
    most of the last week, tweet a 'trends' plot for each event

    Notes
    -----
    I need to figure out the timing between the tweets
    as well as an acceptable measure of down time

    Also, if I miss the time it triggers on, but come online a few 
    hours later, should I tweet? I think so.

    minAgeDays = 4 : Basically, never consider building plots if the 
    last plot was tweeted less than 4 days ago 
    """
    def adjustAverage(x):
        #return math.log(1+1/float(x + 0.0001))
        return 1/float(x + 0.01)
    def convertRunTime(rt):
        time, ampm = rt.split('_')
        if ':' in time:
            hour, minute = time.split(':')
        else:
            hour = time
            minute = '00'
        if ampm.upper() == 'PM':
            hour = int(hour) + 12
        hour = int(hour)
        minute = int(minute)
        dt = datetime.datetime.now()
        dt = dt.replace(hour=hour, minute=minute)
        return dt
    def adjustTimes(sampleTimes, allWeekAvgs):
        # This should just find long gaps in data, and
        # force the plot to zero it out
        segments = []
        adjSampleTimes = []
        adjAllWeekAvgs = []
        lastSampleTime = sampleTimes[0]
        lastAvg = allWeekAvgs[0]
        tooLongofAwait = 2 # hours

        for i in range(1, len(sampleTimes)):
            delta = sampleTimes[i] - lastSampleTime 
            adjSampleTimes.append(lastSampleTime)
            adjAllWeekAvgs.append(adjustAverage(lastAvg))
            if delta.seconds > tooLongofAwait*3600:
                segments.append([adjSampleTimes, adjAllWeekAvgs])
                adjSampleTimes = []
                adjAllWeekAvgs = []
                
            lastSampleTime = sampleTimes[i]
            lastAvg = allWeekAvgs[i]

        adjSampleTimes.append(sampleTimes[-1])
        adjAllWeekAvgs.append(adjustAverage(allWeekAvgs[-1]))
        segments.append([adjSampleTimes, adjAllWeekAvgs])
        
        return segments
        
       
    # SETTINGS 
    # Moved to inputs with expected values
    #runOn = 'SUN'
    #runTime = '6_PM' # Hour(:minute)_DayHalf
    #minAgeDays = 4 # Basically, never consider building plots if the last plot 

    weekSet = ['MON', 'TUE', 'WED', 'THR', 'FRI', 'SAT', 'SUN']

    itsGoTime = False
    runTime = convertRunTime(runTime)

    lastRun = botHelperFunctions.getLoggedData("Last Weekly Summary:")
    lastRun = datetime.datetime.strptime(lastRun,'%Y-%m-%d %H:%M')

    delta = datetime.datetime.now() - lastRun
    
    if delta.days >= minAgeDays:
        if datetime.datetime.today().weekday() == weekSet.index(runOn):
            if datetime.datetime.now() > runTime:
                itsGoTime = True



    #itsGoTime = True
    if itsGoTime == True:
        searchEV = botHelperFunctions.eventLists()
        for event in searchEV:
            
            #allWeekAvgs, weekAvg, weekStd, sampleTimes 
            sampleTimes, allWeekAvgs = botHelperFunctions.getEventHistoryTimeLimit(event, weeks=1, days=0, hours=0, minutes=0)
            weekAvg, weekStd = botHelperFunctions.getEventHistoryStats(allWeekAvgs)
            segments = adjustTimes(sampleTimes, allWeekAvgs)

            msg = "Weekly Summary for " + event[0].upper() + event[1:].lower()
            media = "temp/weeklySummary"+event[0].upper() + event[1:].lower()+".png"
            plt.title(event[0].upper() + event[1:].lower())
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.gcf().autofmt_xdate()
            for seg in segments:
                x = seg[0]
                y = seg[1]
                plt.plot(x, y, linewidth=1.0, color='b')
            plt.title(msg)
            plt.ylabel("Tweets Per Second")
            #plt.show()
            plt.savefig(media, bbox_inches='tight')
            plt.close()
            if not quietMode:
                success = twitterInteractions.tryToTweet(api, msg, media)
            time.sleep(3)
        logLine = "Last Weekly Summary:\t"+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        botHelperFunctions.updateLogFile(logLine)

    return





    
def makeDistPlot(event, featureVector, tbtwTweets, allWeekAvgs, allHistAvgs, kdePlots):
    media = "temp/tweetProof.png"
    timeStamp = time.ctime(time.time())

    tweetCount = featureVector[0]
    tweetMean = featureVector[1]
    tweetStd = featureVector[2]
    weekAvg = featureVector[3]
    weekStd = featureVector[4]
    histAvg = featureVector[5]
    histStd = featureVector[6]

    # BODGE: The Almost Big One
    if tweetStd == 0.0:
        tweetStd = 0.05

    # Add some sort of catch here, if bot has been down for a week
    # Week data is useless
    # if (weekAvg):
        
   
    xHist = np.linspace(0, int(histAvg+(3*histStd)), int(100*(6*histStd)))
    xWeek = np.linspace(0, int(weekAvg+(3*weekStd)), int(100*(6*weekStd)))
    xCur = np.linspace(0, int(tweetMean+(3*tweetStd)), int(100*(6*tweetStd)))

    # Historic KDE (prebuilt)
    histKdeX = kdePlots[0]
    histKdeY = kdePlots[1]

    # Build Current KDE
    xmax = max(allHistAvgs)
    kdeC = KernelDensity(kernel='epanechnikov', bandwidth=float(tweetMean+(3*tweetStd))*.1) # 0.065 is alright
    kdeC.fit(np.array(tbtwTweets)[:, np.newaxis])
    kdeCx = np.linspace(0, int(xmax), 1000)[:, np.newaxis]
    log_densC = kdeC.score_samples(kdeCx)

    # Build weekKDE
    kdeW = KernelDensity(kernel='epanechnikov', bandwidth=float(weekAvg+(3*weekStd))*.1) # 0.065 is alright
    kdeW.fit(np.array(allWeekAvgs)[:, np.newaxis])
    kdeWx = np.linspace(0, int(xmax), 1000)[:, np.newaxis]
    log_densW = kdeW.score_samples(kdeWx)

    # Prep + marks
    tbtwTweets = np.array(tbtwTweets)[:, np.newaxis]


    # Finally at the plotting point..

    # Subplot 1
    plt.subplot(2, 1, 1)
    plt.title(event[0].upper()+event[1:] + " " + str(timeStamp) + " CDT")
    plt.ylabel("Frequency Density\nof Historic Averages")
    plt.hist(allHistAvgs, bins=1000)
    plt.axvline(x=tweetMean, color='r', label="Current Mean", linewidth=1.0)
    plt.legend(loc='upper right')
    plt.xlim(left=0)
    axes = plt.gca()
    tempSet = axes.get_xlim()

    # Subplot 2
    plt.subplot(2, 1, 2)
    plt.plot(xHist,scipy.stats.norm.pdf(xHist, histAvg, histStd),'b',label='Historic Gaussian Distribution', linewidth=1.0)
    plt.plot(xCur,scipy.stats.norm.pdf(xCur, tweetMean, tweetStd), 'g', label='Current Gaussian Distribution', linewidth=1.0)
    plt.plot(histKdeX, np.exp(histKdeY), 'r',label='KDE Fit of Past Year', linewidth=1.0)
    # Cap off top of current kde
    axes = plt.gca()
    ymin, ymaxOld = axes.get_ylim()
    
    # New KDE
    plt.plot(kdeCx, np.exp(log_densC), 'g', ls=':',label='KDE Fit of Current Tweets', linewidth=1.0)
    plt.plot(kdeWx, np.exp(log_densW), 'm', ls=':',label='KDE Fit of Past Week', linewidth=1.0)
    
    # Adjust y axis limits
    ymin, ymaxNew = axes.get_ylim()
    if ymaxOld*1.5 < ymaxNew:
        ymaxSet = ymaxOld*1.25
        plt.ylim(top=ymaxSet)
    plt.ylim(bottom=0)
    axes = plt.gca()
    ymin, ymax = axes.get_ylim()

    plt.plot(tbtwTweets[:, 0], ymax/12.0 * np.random.random(tbtwTweets.shape[0]) + ymax/20., '+k')

    # Finally, pretty up the plot, make things align
    plt.legend(loc='upper right')
    plt.ylabel('Modeled Approximate\nProbability Density')
    axes = plt.gca()
    plt.axvline(x=tweetMean, color='r', linewidth=1.0)
    #print axes.get_xlim()
    axes.set_xlim(tempSet)
    plt.xlabel("Average Time Between Tweets (Seconds)")
    plt.savefig(media, bbox_inches='tight')
    #plt.show()
    plt.close()

    return timeStamp, media