#!/usr/bin/env python

'''
Keith Murray

Using http://tweepy.readthedocs.org/
Uses list of events and list of loctations around world


Read in a list of key events

Search twitter for events, and search results for location ID's
If event and location are present with enough frequency, 
tweet about event

Later have user go back and adjust results, perhaps using neural
nets to 'learn' about actual events occuring.

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
import getKMKeys # Format of CK, CS, AK, AS
#[CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]
import time
import math
import numpy as np
import datetime
import socket
import sys




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
GREEN--	15 16  --HEARTBEAT
	17 18
	19 20
	21 22 
	23 24
	25 26
'''
import threading
import RPi.GPIO as GPIO
rPI = False
def rPIsetup():
    rPI = True
    return True

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
	self.daemon = True
    def run(self):
	print "Starting to Tweet"
	main()
    def stop(self):
	self._stop.set()
    def stopped(self):
	return self._stop.isSet()

def myLED(theLED):
    red = 12
    yellow = 13
    green = 15
    if rPI == True:
	if theLED == "RED":
	    GPIO.output(red, True)
	    GPIO.output(yellow, False)
	    GPIO.output(green, False)
	if theLED == "YELLOW":
	    GPIO.output(red, False)
	    GPIO.output(yellow, True)
	    GPIO.output(green, False)
	if theLED == "GREEN":
	    GPIO.output(red, False)
	    GPIO.output(yellow, False)
	    GPIO.output(green, True)
	if theLED == "EVENT":
	    GPIO.output(red, False)
	    GPIO.output(yellow, False)
	    GPIO.output(green, True)
	    time.sleep(0.15)
	    GPIO.output(green, False)
	    time.sleep(0.15)
	    GPIO.output(green, True)
	    time.sleep(0.15)
	    GPIO.output(green, False)
	    time.sleep(0.15)
	    GPIO.output(green, True)
	    time.sleep(0.15)
	    GPIO.output(green, False)
	    time.sleep(0.15)
	    GPIO.output(green, True)
    return

def heartBeat():
    while True:
	GPIO.output(16, True)
	print "Thub"
	time.sleep(1)
	GPIO.output(16, False)
	print "\tDub"
	time.sleep(1)
	    


def is_connected():
    REMOT_SERVER = "www.google.com"
    try:
	print "Truing"
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


def isItAnEvent(event, theMean, var, uniqTweets):
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
	line = line.split('\t')
	theTimes.append(line[0])
	theAvgs.append(float(line[1]))
	theVar.append(float(line[2]))
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
    if ((zSc * zSc2) <= -2) and (theMean < compAvg) :#and (theMean < 2.75):
	didEventOccur = True 

    # Save new data to DB
    eventHistory = open(str(event) + ".txt", 'a')
    eventHistory.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '\t' + str(theMean) + '\t' + str(var) +'\t' + str(zSc) + '\t' + str(zSc2) +"\t"+ str(uniqTweets) +'\n')
    eventHistory.close()

    if uniqTweets < 15:
	didEventOccur = False

    return didEventOccur

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
		    #connected = is_connected()
		    connected = True
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
	    eventStatus = isItAnEvent(searchEV[event], np.mean(timeBTWTweets), np.var(timeBTWTweets), len(theTweets))
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
		msg = "I think Event: " + str(searchEV[event]) + " has occured" + str(locBestGuess1) + "\n" + str(time.ctime(time.time())) + "CDT"
		if (len(msg) > 140):
		    msg = msg[0:139]
		if oldEvent != searchEV[event]:
		    api.update_status(status=msg)
		    pass
		oldEvent = searchEV[event]
		msg = "I think Event: " + str(searchEV[event]) + " has occured" + str(locBestGuess) + str(time.ctime(time.time()))
		testTweetAsText = open('testTweetAsText.txt', 'a')
		testTweetAsText.write(msg + "\n")
		testTweetAsText.close
		print msg
		myLED("EVENT")
	    
	# We've gone through all events, recorded their data, and determined if an event occured
	#   Time to relax
	#break
	print "Time to rest up a bit, be back soon"
	time.sleep(5*60)

    return


def piMain():
    #Start two threads, one heartbeat, one standard
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.setup(16, GPIO.OUT)
    heartB = heartBeatThread()
    tweetStuff = twitterThread()
    try:
	heartB.start()
	tweetStuff.start()
    except(KeyboardInterrupt, SystemExit):
	heartB.stop()
	tweetStuff.stop()
    return
	



rPI = rPIsetup() # Comment out if not using a rPi, this is for LEDs


if (rPI == True):
    print "PI"
    piMain()
else:
    main()




