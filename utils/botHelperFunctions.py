
import numpy as np
import datetime
import logging
import os
import math
import json

import logging


def eventLists():
    """
    Load defined event names

    Returns
    -------
    searchEV : list of strings (event names) 
        Just grabs every event defined in the file in 
        (hardcoded) `keyEventDB` str varible
        as of this, that file is listOfTwitterEvents.txt

    Notes
    -----
    


    """

    keyEventsDB = "misc/listOfTwitterEvents.txt"
    #   Events
    eventL = open(keyEventsDB, 'r')
    searchEV = []
    for event in eventL:
        searchEV.append(event.strip())
    eventL.close()
    return searchEV

def getEventHistoryStats(sampleAvgs):
    timeSpanAvg = np.mean(sampleAvgs)
    timeSpanStd = np.std(sampleAvgs)
    return timeSpanAvg, timeSpanStd


def getEventHistoryTimeLimit(event, weeks=1, days=0, hours=0, minutes=0):
    """
    Functionally similar to `getEventHistory`, this grabs only the 
    history of the last week (might be modified to last month) to 
    create a rolling comparision, preventing continous event tweets
    about the same subject (see spikes in tweet post NK Missile Tests)

    

    Parameters
    ----------
    event: string
        keyword used for data files
    weeks: int, default = 1
        Number of weeks back from now 
    days=0
    hours=0
    minutes=0


    Returns
    -------
    sampleTimes: list of Datetimes

    sampleAvgs: list of floats
        


    Notes
    -----
    I'm not sure how well this will work when it's a new feature
    It also might need to be redone with `getEventHistory`, because 
    improved filtering might make it rare that the bot tweets about
    events (old average time between tweets being significantly 
    smaller, causing new samples to look insignificant in comparision
    
    also downtime is much more noticable in this method. 

    Still, this will be how the bot tweets week history so we'll see

    weekMaxSize = 2016 is determined by the 5 minute wait after each 
    event cycle. This means the max number of times the bot will ping
    twitter is 60/5*24*7 

    There is almost certainly never going to be more elements in the 
    week history than this, and reduces search space making computations
    simpler on the pi

    ...which is useful becase I can't promise that this will run smoothly
    on the pi..
    
    """
    
    # Grab all history
    try:
    	eventHistory = open("misc/hist_data/"+str(event) + ".txt", 'r')
    except IOError:
        eventHistory = open("misc/hist_data/"+str(event) + ".txt", 'a')
        eventHistory.close()
        eventHistory = open("misc/hist_data/"+str(event) + ".txt", 'r')
    sampleTimes = []
    allSampleAvgs = []
    theVar = []
    for line in eventHistory:
        if line == "":
            break
        try:
            line = line.split('\t')
            sampleTimes.append(line[0])
            allSampleAvgs.append(float(line[1]))
            theVar.append(float(line[2]))
        except:
            logging.error("Average File Error")
	
    eventHistory.close()
    #theTimes, allHistAvgs, histAvg, histStd = getEventHistory(event)
    
    # Check if all info needs to be returned
    #  This is shown by inputing a -1 in any time entry
    inMin = min(minutes, hours, days, weeks)
    if inMin == -1:
        sampleTimes = np.array([datetime.datetime.strptime(d,'%Y-%m-%d%H:%M') for d in sampleTimes])
        return sampleTimes, allSampleAvgs
    # else adjust the returned array size


    # Reduce search space
    
    weekMaxSize = 2016
    maxSize = 1+ \
                int(minutes/5)+ \
                int(hours*60/5)+ \
                int(days*24*60/5)+ \
                int(weeks*7*24*60/5)
    
    
    if len(sampleTimes) - maxSize < 0:
        maxSize = 0
    #maxSize = max(0, len(sampleTimes) - maxSize)
    if len(sampleTimes) > maxSize:
        sampleTimes = sampleTimes[-maxSize:]
    if len(allSampleAvgs) > maxSize:
        allSampleAvgs = allSampleAvgs[-maxSize:]

    # Parse theTimes for correct oldest sample
    x = np.array([datetime.datetime.strptime(d,'%Y-%m-%d%H:%M') for d in sampleTimes])
    i = 0
    while i < len(sampleTimes):
        if  x[i] > datetime.datetime.now()-datetime.timedelta(weeks=weeks,\
                 days=days, hours=hours, minutes=minutes):
            break
        i+=1

    sampleTimes = x[i:]
    allSampleAvgs = allSampleAvgs[i:]

    #timeSpanAvg = np.mean(allSampleAvgs)
    #timeSpanStd = np.std(allSampleAvgs)




    return sampleTimes, allSampleAvgs 


def getEventHistoryDateRange(event, startDateTime, endDateTime):
    x = datetime.datetime.now()-startDateTime
    minutes = x.total_seconds() / 60

    sampleTimes, allSampleAvgs = getEventHistoryTimeLimit(event, weeks=0, days=0, hours=0, minutes=minutes)


    # Parse theTimes for correct most recent sample
    i = 0
    while i < len(sampleTimes):
        if  sampleTimes[i] > endDateTime:
            break
        i+=1

    sampleTimes = sampleTimes[:i]
    allSampleAvgs = allSampleAvgs[:i]

    return sampleTimes, allSampleAvgs



def saveToHistoryFile(sampledMean, sampledVar, tweetCount, event):
    # zSc is a holdover of legacy code. One of these updates will 
    #   remove it completely, it's not actually used anymore
    #   and can be calculated readily from all previous data
    zSc1 = 'x'
    zSc2 = 'z'
    if tweetCount > 3:
        if (not math.isnan(sampledMean)) and (not math.isnan(sampledVar)):
            eventHistory = open("misc/hist_data/"+str(event) + ".txt", 'a')
            eventHistory.write(datetime.datetime.now().strftime("%Y-%m-%d%H:%M") \
                + '\t' + str(sampledMean) + '\t' + str(sampledVar) +'\t' + str(zSc1) + 
                '\t' + str(zSc2) +"\t"+ str(tweetCount) +'\n')
            eventHistory.close()
    return 





def startupLogFile():
    newStartup = "Last Startup:\t" + \
                str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) 
    updateLogFile(newStartup)
    
    return


def updateLogFile(newLine):
    """
    Takes `newLine` and inserts it into the correct line in
    the log file, sucessfully updating that feature

    Parameters
    ----------
    

    Raises 
    ------
    


    Notes
    -----



    """
    try:
        logFile = open("logs/crowdSource.log", 'r')
        data = logFile.read()
        logFile.close()
        flSize = os.path.getsize("logs/crowdSource.log")
        if flSize == 0:
            raise BaseException # Cheap trigger for the except condition 
        if data == "":
            raise BaseException 
    except:
        # I'm being extra fancy, it's pointless, but I'm pleased with it
        # The time of the very first tweet from this twitter account
        firstTweetTime = "11:55 PM - 15 Apr 2015"
        firstTweetTime = firstTweetTime.replace('- ', '')
        from dateutil.parser import parse
        parsedTweetTime = parse(firstTweetTime)
        logFile = open("logs/crowdSource.log", 'a')
        logFile.write("Last Startup:\t" + 
                str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + '\n')
        logFile.write("Last KDE Update:\t" +
                str(parsedTweetTime.strftime("%Y-%m-%d %H:%M")) + '\n')
        logFile.write("Last Weekly Summary:\t" +
                str(parsedTweetTime.strftime("%Y-%m-%d %H:%M")) + '\n')
        logFile.close()




    lineAdded = False
    lineID = newLine.split('\t')[0]

    logFile = open("logs/crowdSource.log", 'r')
    allLog = logFile.read()
    logFile.close()
    logFile = open("logs/crowdSource.log", 'w')
    statements = allLog.split('\n')
    for line in statements:
        if line != "":
            key, value = line.split('\t')
            if key in lineID:
                line = newLine
                lineAdded = True
            logFile.write(line+'\n')
    logFile.close()

    if lineAdded == False:
        logFile = open("logs/crowdSource.log", 'w')
        logFile.write(allLog)
        logFile.close()
        raise SyntaxError("Given string '%s' did not align with a log entry" % lineID)

    return 
        

def getLoggedData(lineID):
    """
    Takes `newLine` and inserts it into the correct line in
    the log file, sucessfully updating that feature

    Parameters
    ----------
    lineID: string
        a string with a log name the user wants to find

    Returns
    -------
    theValue: string

    Raises 
    ------
    SyntaxError:
        If the program can't parse the input string to find the 
        correct log entry, it'll raise this error. I'll fix this
        phrasing later on.


    Notes
    -----



    """

    lineFound = False
    logFile = open("logs/crowdSource.log", 'r')
    for line in logFile:
        if line != "":
            line = line.strip()
            key, value = line.split('\t')
            if key in lineID:
                theValue = value 
                lineFound = True

    logFile.close()
   

    if lineFound == False:
        logFile = open("logs/crowdSource.log", 'w')
        logFile.write(allLog) # This code should never execute (I think) 
        logFile.close() # Unless something else is going wrong
        raise SyntaxError("Given string '%s' not found in log entry" % lineID)

    return theValue
        



def save_recent_tweets(tweets):

    dirName = "misc/sample_tweets"
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    logFileName =   'LOG_'+ datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.json'
    filePath = os.path.join(dirName, logFileName) 

    jsonSet = [x._json for x in tweets]
    with open(filePath, 'w') as outfile:
        json.dump(jsonSet, outfile)

    return