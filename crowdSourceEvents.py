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


def isItAnEvent(event, theMean, var):
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
    compVar = np.var(theVar)
    if (theMean < (compAvg - compVar/2.0)) and (theMean < 2.75) :#and (var < 10):
	didEventOccur = True 

    # Save new data to DB
    eventHistory = open(str(event) + ".txt", 'a')
    eventHistory.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '\t' + str(theMean) + '\t' + str(var) + '\n')
    eventHistory.close()

    return didEventOccur

def getLocation(locBestGuess):
    if len(locBestGuess) == 0:
	return " but I can't find where"
    elif len(locBestGuess) == 1:
	return " in " +str(locBestGuess[0])
    else:
	d = dict((i,locBestGuess.count(i)) for i in locBestGuess)
	return " in " +str(max(d, key=d.get))
	

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
	    while True:
		try: # This 'try' is to catch 'rate limit exceeded' errors
		    tweet = tweetList.next()
		    tweetAge = time.time() - (tweet.created_at - datetime.datetime(1970,1,1)).total_seconds()
		    print tweetAge/(float(60*60))
		    if not tweet.retweeted and (tweetAge < 24*60*60): # Make sure original tweet and fairly new (24 hours)
			if tweetTracker == 0:
			    oldTime = tweet.created_at
			timeDiff = oldTime - tweet.created_at
			timeFloat = timeDiff.total_seconds()
			timeBTWTweets.append(timeFloat) # list of time between tweets occurence 		
			oldTime = tweet.created_at
			tweetTracker +=1
			theTweets.append(unicode(tweet.text))
			if tweetTracker > rppSize:
			    tweetTracker = 0
			    break
		except tweepy.TweepError: 
		    time.sleep(60*5)
		    continue

	    # Now I've got timeBTWTweets, and theTweets:
	    #  Based on tbtwtweets, decide if an event occured. 
	    eventStatus = isItAnEvent(searchEV[event], np.mean(timeBTWTweets), np.var(timeBTWTweets))
	    if eventStatus == True:
		# Now we get ready to tweet!! :D
		locBestGuess = []
		for aTweet in theTweets:
		    # v Right now we'll only do 1 word city names, fix this later
		    words = aTweet.split(" ")
		    for i in range(len(words)):
			try:
			    if str(words[i]) in cities:
				cityName = words[i]
			    	locBestGuess.append(str(words[i]))
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
		    # ^ This area is where the city name needs to be fixed 

		# now we've looked at the tweets and tried to guess a location
		locBestGuess1 = getLocation(locBestGuess)
		msg = "I think Event: " + str(searchEV[event]) + " has occured " + str(locBestGuess1) + "\n" + str(time.ctime(time.time()))
		api.update_status(status=msg)
		msg = "I think Event: " + str(searchEV[event]) + " has occured " + str(locBestGuess) + str(time.ctime(time.time()))
		testTweetAsText = open('testTweetAsText.txt', 'a')
		testTweetAsText.write(msg + "\n")
		testTweetAsText.close

	    
	# We've gone through all events, recorded their data, and determined if an event occured
	#   Time to relax
	#break
	time.sleep(5*60)

    return

main()




