#!/usr/bin/env python

'''
Keith Murray


 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * "Once men turned their thinking over to machines in the hope      *
 *  that this would set them free. But that only permitted other     *
 *  men with machines to enslave them."                              *
 * " 'Thou shalt not make a machine in the likeness of a man's       *
 *  mind,' " Paul quoted.                                            *
 * "Right out of the Butlerian Jihad and the Orange Catholic         *
 *  Bible," she said. "But what the O.C. Bible should've said is:    *
 *  'Thou shalt not make a machine to counterfeit a human mind.'..." *
 *                                                                   *
 *  --from Dune, by Frank Herbert                                    *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *



Using tweepy: http://tweepy.readthedocs.org/
Uses list of events and list of loctations around world

Read in a list of key events

Search twitter for events, and search results for location ID's
If event and location are present with enough frequency, 
tweet about event

Later have user go back and adjust results, perhaps using something
to 'learn' about actual events occuring.

**********************************************
explination for setting up api
http://www.74by2.com/2014/06/easily-get-twitter-api-key-api-secret-access-token-access-secret-pictures/

status Object Structure:
http://tkang.blogspot.com/2011/01/tweepy-twitter-api-status-object.html

 'contributors': None, 
 'truncated': False, 
 'text': 'My Top Followers in 2010: @tkang1 @serin23 @uhrunland @aliassculptor @kor0307 @yunki62. Find yours @ http://mytopfollowersin2010.com',
 'in_reply_to_status_id': None,
 'id': 21041793667694593,
 '_api': <tweepy.api.api object="" at="" 0x6bebc50="">,
 'author': <tweepy.models.user object="" at="" 0x6c16610="">,
 'retweeted': False,
 'coordinates': None,
 'source': 'My Top Followers in 2010',
 'in_reply_to_screen_name': None,
 'id_str': '21041793667694593',
 'retweet_count': 0,
 'in_reply_to_user_id': None,
 'favorited': False,
 'retweeted_status': <tweepy.models.status object="" at="" 0xb2b5190="">,
 'source_url': 'http://mytopfollowersin2010.com', 
 'user': <tweepy.models.user object="" at="" 0x6c16610="">,
 'geo': None, 
 'in_reply_to_user_id_str': None, 
 'created_at': datetime.datetime(2011, 1, 1, 3, 15, 29), 
 'in_reply_to_status_id_str': None, 
 'place': None
}

'''

import tweepy
#import getKMKeys # Format of CK, CS, AK, AS
import getChatBotKeys as getKMKeys
#[CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]
import time
import math
import numpy as np
import datetime
import socket
import sys
import os
import threading
from sklearn.neighbors import KernelDensity
import unCorruptFiles



'''
Pin Numbers	RPi.GPIO	Raspberry Pi Name	BCM2835		USED AS
P1_01		1		3V3	 
P1_02		2		5V0	 
P1_03		3		SDA0			GPIO0
P1_04		4		DNC	 
P1_05		5		SCL0			GPIO1
P1_06		6		GND	 				GND
P1_07		7		GPIO7			GPIO4
P1_08		8		TXD			GPIO14		TXD
P1_09		9		DNC	 
P1_10		10		RXD			GPIO15		RXD
P1_11		11		GPIO0			GPIO17	
P1_12		12		GPIO1			GPIO18
P1_13		13		GPIO2		 	GPIO21
P1_14		14		DNC	 
P1_15		15		GPIO3			GPIO22
P1_16		16		GPIO4			GPIO23
P1_17		17		DNC	 
P1_18		18		GPIO5			GPIO24
P1_19		19		SPI_MOSI		GPIO10
P1_20		20		DNC	 
P1_21		21		SPI_MISO		GPIO9
P1_22		22		GPIO6			GPIO25
P1_23		23		SPI_SCLK		GPIO11
P1_24		24		SPI_CE0_N		GPIO8
P1_25		25		DNC	 
P1_26		26		SPI_CE1_N		GPIO7

pin setup on PI 
	1   2 
	3   4
	5   6  --GND
	7   8  
	9  10  
	11 12  --RED 
YELLOW-	13 14
 BLUE--	15 16  --HEARTBEAT
	17 18  --GREEN
	19 20
	21 22 
	23 24
	25 26
'''


class heartBeatThread(threading.Thread):
    def __init__(self):
	threading.Thread.__init__(self)
	self.name="HeartBeatThread"
	self.daemon = True
    def run(self):
	print "STARTING THAT SICK BEAT YO"
	heartBeat()
    def stop(self):
	self._stop.set()
    def stopped(self):
	return self._stop.isSet()

class twitterThread(threading.Thread):
    def __init__(self):
	threading.Thread.__init__(self)
	self.name="TwitterBotThread"
	#self.daemon = True
    def run(self):
	print "Starting to Tweet"
	main()
	print "I ESCAPED"
    def stop(self):
	self._stop.set()
    def stopped(self):
	return self._stop.isSet()

class restartButtonThread(threading.Thread):
    def __init__(self):
	threading.Thread.__init__(self)
	self.name="restartButtonThread"
	self.daemon = True
    def run(self):
	print "Button is active"
	buttonListener()
    def stop(self):
	self._stop.set()
    def stopped(self):
	return self._stop.isSet()

def ledCycle():
    def blink(pin):
        pinState = False
        for i in range(6):
            pinState = not pinState
            GPIO.output(pin, pinState)
            time.sleep(0.15)
        GPIO.output(pin, False)

    white = 16
    red = 12
    yellow = 13
    blue = 15
    green = 18
    blink(white)
    blink(red)
    blink(yellow)
    blink(blue)
    blink(green)
    return


def myLED(theLED):
    red = 12
    yellow = 13
    blue = 15
    green = 18
    if rPI == True:
	if theLED == "RED":
	    GPIO.output(red, True)
	    GPIO.output(yellow, False)
	    GPIO.output(blue, False)
	    GPIO.output(green, False)
	    #print "RED"
	if theLED == "YELLOW":
	    GPIO.output(red, False)
	    GPIO.output(yellow, True)
	    GPIO.output(blue, False)
	    GPIO.output(green, False)
	    #print "YELLOW"
	if theLED == "GREEN":
	    GPIO.output(red, False)
	    GPIO.output(yellow, False)
	    GPIO.output(blue, True)
	    GPIO.output(green, False)
	    #print "BLUE"
	if theLED == "EVENT":
	    GPIO.output(red, False)
	    GPIO.output(yellow, False)
	    GPIO.output(green, False)
	    GPIO.output(blue, True)
	    time.sleep(0.15)
	    GPIO.output(blue, False)
	    time.sleep(0.15)
	    GPIO.output(blue, True)
	    time.sleep(0.15)
	    GPIO.output(blue, False)
	    time.sleep(0.15)
	    GPIO.output(blue, True)
	    time.sleep(0.15)
	    GPIO.output(blue, False)
	    time.sleep(0.15)
	    GPIO.output(blue, True)
	    #print "EVENT"
	if theLED == "SLEEP":
	    GPIO.output(red, False)
	    GPIO.output(yellow, False)
	    GPIO.output(blue, False)
	    GPIO.output(green, True)
	    #print "GREEN"
    return

def heartBeat():
    # Toggles an LED to verify the program is running
    # Lets the pi run without owner needing a monitor 
    while True:
	GPIO.output(16, True)
	# print "BEAT"
	time.sleep(1)
	GPIO.output(16, False)
	time.sleep(1)
	    
def buttonListener():
    red = 12
    yellow = 13
    blue = 15
    green = 18
    # For restart and shutdown
    # This is super inelegant. But I think it'll work so there we go
    oldState = GPIO.input(7)
    buttonPress = False
    while True:
	curState = GPIO.input(7)
	if curState != oldState:
	    # Debounce
	    time.sleep(0.003)
	    if curState != oldState:
		if buttonPress == True:
		    buttonPress = False
		    duration = time.time() - startTime
		    if duration <= 7:	
			GPIO.output(yellow, True)
			time.sleep(.1)
			os.system("sudo reboot")
		else:		
		    buttonPress = True
		oldState = curState
		startTime = time.time()
		# Turn on "I'm responding" LED Combo
		GPIO.output(green, True)
		GPIO.output(blue, True)
	time.sleep(.001)
	if buttonPress:
	    duration = time.time() - startTime
	    if duration > 7:
		# Shutdown condition
		GPIO.output(red, True)
		time.sleep(.1)
		GPIO.output(red, False)
		time.sleep(.1)
		GPIO.output(red, True)
		time.sleep(.5)
		os.system("sudo shutdown -h now")
    return
	


def is_connected():
    REMOTE_SERVER = "www.google.com"
    try:
	print "Testing Internet Connection"
	# see if we can resolve the host name -- tells us if there is
	# a DNS listening
	host = socket.gethostbyname(REMOTE_SERVER)
	# connect to the host -- tells us if the host is actually
	# reachable
	s = socket.create_connection((host, 80), 2)
	return True
    except:
	pass
    return False


def isItAnEvent(event, theMean, var, uniqTweets, timeBTWTweets):
    # open event db
    # Date/Time \t theMean \t var
    try:
    	eventHistory = open(str(event) + ".txt", 'r')
    except IOError:
	eventHistory = open(str(event) + ".txt", 'a')
	eventHistory.close()
	eventHistory = open(str(event) + ".txt", 'r')
    theTimes = []
    theAvgs = []
    theVar = []
    for line in eventHistory:
	if line == "":
	    break
	try:
	    line = line.split('\t')
	    theTimes.append(line[0])
	    theAvgs.append(float(line[1]))
	    theVar.append(float(line[2]))
	except:
	    print "Average File Error"
	
    eventHistory.close()
    
    
	
    # compare eventDB to most recent event
    didEventOccur = False
    compAvg = np.mean(theAvgs)
    compVar = np.var(theAvgs)
    compStd = np.std(theAvgs)
    zSc = (theMean-compAvg)/compStd
    zSc2 = (compAvg-theMean)/math.sqrt(var)
    #if (theMean < (compAvg - compStd*1.3)) and (theMean < 2.75) :#and (var < 10):
    #if (math.fabs(zSc) > 2):
    print event, (zSc * zSc2), compAvg, theMean
    if ((zSc * zSc2) <= -2) and (theMean < compAvg) and uniqTweets > 14:#and (theMean < 2.75):
	didEventOccur = True 
	# Build a plot to visualize Impact
	x1 = np.linspace(0, compAvg+(3*compStd), 100*(6*compStd))
	newstd = math.sqrt(var)
	x2 = np.linspace(0, theMean+(3*newstd), 100*(6*newstd))

	# Fit with KDE 
	theAvgs = np.array(theAvgs)
	theAvgs = theAvgs[:, None]
	X_plot = np.linspace(0, compAvg+(3*compStd), len(theAvgs))[:, None]
	# KDE For Event
	theTweets = np.array(timeBTWTweets)
	theTweets = theTweets[:, None]
	#X_plot2 =  np.linspace(0, theMean+(3*newstd), 100*(6*newstd))[:, None]
	#kde = KernelDensity(kernel='epanechnikov', bandwidth=3.0)
	#kde.fit(theTweets)
	#log_dens2 = kde.score_samples(X_plot2)
	
    
	plt.subplot(2, 1, 1)
	plt.title(event[0].upper()+event[1:] + " " + str(time.ctime(time.time())) + " CDT")
	plt.ylabel("Frequency Density\nof Historic Averages")
	plt.hist(theAvgs, bins=1000)
	plt.axvline(x=theMean, color='r', label="Current Mean")
	plt.legend(loc='upper right')
	axes = plt.gca()
	tempSet = axes.get_xlim()

	bw = float(tempSet[1])*0.012
	kde = KernelDensity(kernel='epanechnikov', bandwidth=bw)
	kde.fit(theAvgs)
	log_dens = kde.score_samples(X_plot)

	plt.subplot(2, 1, 2)
	plt.plot(x1,mlab.normpdf(x1, compAvg, compStd),label='Historic Gaussian Distribution')
	plt.plot(x2,mlab.normpdf(x2, theMean, newstd),label='Current Gaussian Distribution')
	plt.plot(X_plot, np.exp(log_dens), 'r',label='KDE Fit using Epanechnikov')
	#plt.axhline(y=0, xmin=0, xmax=1, hold=None, c='k') # Black line to sepperate tweet dots
	axes = plt.gca()
	ymin, ymax = axes.get_ylim()
	plt.plot(theTweets[:, 0], ymax/12.0 * np.random.random(theTweets.shape[0]) + ymax/20., '+k')
	#plt.plot(X_plot2, np.exp(log_dens2), 'm',label='KDE Fit on Current Tweets', linestyles[':'])
	plt.legend(loc='upper right')
	plt.ylabel('Modeled Approximate\nProbability Density')
	axes = plt.gca()
	plt.axvline(x=theMean, color='r')
	#print axes.get_xlim()
	axes.set_xlim(tempSet)
	plt.xlabel("Average Time Between Tweets (Seconds)")
	plt.savefig("tweetProof.png", bbox_inches='tight')
	plt.close()


    # Save new data to DB
    eventHistory = open(str(event) + ".txt", 'a')
    eventHistory.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '\t' + str(theMean) + '\t' + str(var) +'\t' + str(zSc) + '\t' + str(zSc2) +"\t"+ str(uniqTweets) +'\n')
    eventHistory.close()

    return didEventOccur, (zSc * zSc2)

def getLocation(locBestGuess):
    if len(locBestGuess) == 0:
	return " but I can't find where"
    elif len(locBestGuess) == 1:
	return " in " +str(locBestGuess[0])
    else:
	d = dict((i,locBestGuess.count(i)) for i in locBestGuess)
	return " in " +str(max(d, key=d.get))
	

def processTweet(tweet, tweetDict):
    # Basic Spam Rejection:
    if tweet[0:2] == "RT":
	# Reject Retweets
	return False, tweetDict
    cleanTweet = tweet.split("http://t.co/")
    cleanTweet = tweet[0]
    cleanTweet = cleanTweet.split("goo.gl/")
    cleanTweet = tweet[0]
    if cleanTweet in tweetDict:
	# Reject Repeats
	return False, tweetDict
    else:
	tweetDict[cleanTweet] = 1
	return True, tweetDict

def main():
    # Get twitter reqs 
    myKeys = getKMKeys.GETTWITTER()
    CONSUMER_KEY = myKeys[0]
    CONSUMER_SECRET = myKeys[1]
    ACCESS_KEY = myKeys[2]
    ACCESS_SECRET = myKeys[3]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)

    locDB = "extendedCityDatabase.txt"
    keyEventsDB = "listOfTwitterEvents.txt" 

    # Load cities and events into memory
    #   Cities
    cities = {}
    cityIn = open(locDB, 'r')
    maxSpace = 0
    for line in cityIn:
	city = line.split('\t')
	cities[str(city[0])] = city[1:]
	city = city[0]
	spaces = len(city.split(' '))
	if spaces > maxSpace:
	    maxSpace = spaces # maxSpace is the number of spaces that will have to be read in to read a city
	    thatCity = city
	    #print city
    cityIn.close()

    #   Events
    eventL = open(keyEventsDB, 'r')
    searchEV = []
    for event in eventL:
	searchEV.append(event.strip())
    eventL.close()
    
    # Time To TWEET IT UP :D
    rppSize = 50
    tweetTracker = 0
    oldEvent = ""
    #dbSample = open('TornadoIsOccuring.txt', 'a')
    while True: # Always running
	for event in range(len(searchEV)): # Perform a search on all events
	    tweetList = tweepy.Cursor(api.search,
                           q=searchEV[event],
                           rpp=rppSize,
                           result_type="recent",
                           include_entities=True).items()
	    #dbSample.write(str(searchEV[event]) + "\n")
	    timeBTWTweets = []
	    theTweets = []
	    #for tweet in tweetList:
	    tweetTracker = 0
	    tweetTries = 0
	    tweetDict = {}
	    while True:
		try: # This 'try' is to catch 'rate limit exceeded' errors
		    myLED("GREEN")
		    tweet = tweetList.next()
		    tweetAge = time.time() - (tweet.created_at - datetime.datetime(1970,1,1)).total_seconds()
		    #print tweetAge/(float(60*60))
		    newTweet, tweetDict = processTweet(tweet.text.encode('utf-8'), tweetDict)
		    tweetTries += 1
		    
		    handle = tweet.user.screen_name.encode('utf-8')
		    text = tweet.text.encode('utf-8')
		    #print handle
		    #print text
		    if (not tweet.retweeted) and (tweetAge < 24*60*60) and newTweet: # Make sure original tweet and fairly new (24 hours)
			if tweetTracker == 0:
			    oldTime = tweet.created_at
			timeDiff = oldTime - tweet.created_at
			timeFloat = timeDiff.total_seconds()
			timeBTWTweets.append(timeFloat) # list of time between tweets occurence 		
			oldTime = tweet.created_at
			tweetTracker +=1
			theTweets.append((tweet.text.encode('utf-8')))
			if tweetTracker > rppSize or tweetTries > 100:
			    tweetTracker = 0
			    break
		except tweepy.TweepError: 
		    # check if the error is internet connection based
		    connected = is_connected()
		    #connected = True
		    if connected:
			print "I started to annoy twitter, now I have to wait a bit"
			myLED("YELLOW")
		    else:
			print "I'm not connected to the network at the moment, sorry"
			myLED("RED")
		    time.sleep(60*5)
		    continue
		except StopIteration:
		    break

	    # Now I've got timeBTWTweets, and theTweets:
	    #  Based on tbtwtweets, decide if an event occured. 
	    eventStatus, zscored = isItAnEvent(searchEV[event], np.mean(timeBTWTweets), np.var(timeBTWTweets), len(theTweets), timeBTWTweets)
	    #eventStatus = True #DEBUGGING
	    print len(theTweets)
	    if eventStatus == True:
		# Now we get ready to tweet!! :D
		locBestGuess = []
		tweetProof = open('tweetProof.txt', 'a')
		tweetProof.write(searchEV[event]+ " " +str(time.ctime(time.time())) + "\n")
		for aTweet in theTweets:
		    words = aTweet.split(" ")
		    guessCity = "" # No idea if this will stop sydney 
		    for j in range(maxSpace):
			for i in range(len(words)-j):
			    try:
				guessCity = " ".join(words[i:i+j+1])
				if str(guessCity) in cities:
				    cityName = guessCity
			    	    locBestGuess.append(str(guessCity))
			    except UnicodeEncodeError:
			        '''
				Traceback (most recent call last):
				  File "crowdSourceEvents.py", line 238, in <module>
				    main()
				  File "crowdSourceEvents.py", line 189, in main
				    if str(words[i]) in cities:
				UnicodeEncodeError: 'ascii' codec can't encode character u'\U0001f64f' in position 0: ordinal not in range(128)

			        '''
			        pass

		    
		    try:
			#print aTweet
			saveThis = str(aTweet.decode('utf8'))
			saveThis = saveThis.translate(None, "\n")
			tweetProof.write("\t"+saveThis+"\n")
		    except UnicodeEncodeError:
			pass
		tweetProof.write("\n")
		tweetProof.close()
		    # ^ This area is where the city name needs to be fixed 

		# now we've looked at the tweets and tried to guess a location
		locBestGuess1 = getLocation(locBestGuess)
		msg = "I think Event: " + str(searchEV[event]) + " has occurred" + str(locBestGuess1) + "\n" + str(time.ctime(time.time())) + " CDT" 
		if (len(msg) > 116):
		    msg = msg[0:115]
		# Only tweet if it's not repeating OR (zSc * zSc2) under isItAnEvent is less than -10 
		#   zscored is used to prevent the bot from remaining quiet when new events occur
		#   even if they are the same event type as before
		if (oldEvent != searchEV[event]) or (zscored < -10):
		    #api.update_status(status=msg)
		    fn = os.path.abspath('tweetProof.png')
		    '''
		    Traceback (most recent call last):
		    Erro path:
		        raise TweepError(error_msg, resp, api_code=api_error_code)
		    tweepy.error.TweepError: [{u'message': u'Internal error', u'code': 131}]

		    Basically, according to the twitter api,
		    "131	Internal error	Corresponds with an HTTP 500 - An unknown internal error occurred."
		    Something went wrong, we don't know what or why. 
		    
		    wait a short period, try again, and if that fails, give up with an error message and 
		    continue on your merry way
		    '''
		    try:
			api.update_with_media(fn, status=msg)
		    except TweepError:
			time.sleep(2)
			try:
			    api.update_with_media(fn, status=msg)
			except TweepError:
			    print "It's fucked man, two Tweep Errors in a row\n\tCheck what's up with twitter"
		    pass
		oldEvent = searchEV[event]
		msg = "I think Event: " + str(searchEV[event]) + " has occurred" + str(locBestGuess) + str(time.ctime(time.time()))
		testTweetAsText = open('testTweetAsText.txt', 'a')
		testTweetAsText.write(msg + "\n")
		testTweetAsText.close
		print msg
		myLED("EVENT")
	    
	# We've gone through all events, recorded their data, and determined if an event occured
	#   Time to relax
	#break
	print "Time to rest up a bit, be back soon"
	myLED("SLEEP")
	# This is where I should clean all the files
	#unCorruptFiles.main()

	time.sleep(5*60)

    return

def getTwitterAPI():
    # Get twitter reqs 
    myKeys = getKMKeys.GETTWITTER()
    CONSUMER_KEY = myKeys[0]
    CONSUMER_SECRET = myKeys[1]
    ACCESS_KEY = myKeys[2]
    ACCESS_SECRET = myKeys[3]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def cityData(): 
    locDB = "extendedCityDatabase.txt"
    # Load cities and events into memory
    #   Cities
    cities = {}
    cityIn = open(locDB, 'r')
    maxSpace = 0
    for line in cityIn:
	city = line.split('\t')
	cities[str(city[0])] = city[1:]
	city = city[0]
	spaces = len(city.split(' '))
	if spaces > maxSpace:
	    maxSpace = spaces # maxSpace is the number of spaces that will have to be read in to read a city
	    thatCity = city
	    #print city
    cityIn.close()
    return cities, maxSpace

def eventLists():

    keyEventsDB = "listOfTwitterEvents.txt"
    #   Events
    eventL = open(keyEventsDB, 'r')
    searchEV = []
    for event in eventL:
	searchEV.append(event.strip())
    eventL.close()
    return searchEV



def main1():
    # Header 
    api = getTwitterAPI()
    cities, maxSpace = cityData()
    searchEV = eventLists()
    
    # Time To TWEET IT UP :D
    rppSize = 50
    tweetTracker = 0
    oldEvent = ""
    
    while True:
	for event in searchEV:
	    pass
    return















def piMain():
    #Start two threads, one heartbeat, one standard
    # Setup rpi pins
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.setup(16, GPIO.OUT)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(7, GPIO.IN)

    ledCycle()

    heartB = heartBeatThread()
    powerButton = restartButtonThread()
    tweetStuff = twitterThread()

    try:
    	heartB.start()
	powerButton.start()
	unCorruptFiles.main()
    	tweetStuff.start()
    except(KeyboardInterrupt, SystemExit):
	heartB.stop()
	tweetStuff.stop()
	powerButton.stop()
    return
	

 
rPI = False
try: 
    import RPi.GPIO as GPIO
    rPI = True
    # These two lines are for the pi graphics handling the plots
    import matplotlib as mpl
    mpl.use('Agg')
    # Image Data
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    # Actual twitter bot info
    import getKMKeys # Format of CK, CS, AK, AS
#[CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]
except:
    # Image Data
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    rPI = False
    # Demo bot info since testing uses @keithChatterBot
    import getChatBotKeys as getKMKeys

if (rPI == True):
    print "PI"
    piMain()
else:
    unCorruptFiles.main()
    main()
    #print "Cool, double check shit"



