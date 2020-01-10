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
import sys
# Required to get program to run at boot on pi
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')

from utils import startupLoggingCharacteristics
import logging


import tweepy
import time
import math
import numpy as np
import nltk
nltk.data.path.append('/home/pi/nltk_data')
import datetime
import socket
#import sys
import os
import re # http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
import threading
from sklearn.neighbors import KernelDensity


'''

if __name__ == "__main__":
    # Logging Stuff
    dirName = "logs"
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    logFileName =   'LOG_'+ datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'
    filePath = os.path.join(dirName, logFileName) 
    logging.basicConfig(filename=filePath, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s():%(lineno)s - %(message)s')
'''

from utils import botHelperFunctions
from utils import manageHardware
from utils import plotManager
from utils import rpiGPIOFunctions
from utils import twitterInteractions
from utils import unCorruptFiles
from utils.nlpTools import locationFromText

from utils.experimental.topology import tweetNetworkExploration
from lsalib.utils import wordRelationTools


# Filters 
from utils.nlpTools.filters import unspam, polysemyFilters, grammarFilters

# Classifiers
from utils.eventClassifiers.simpleDistrobution import simpleClassifier

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
BUTTON-	7   8  
  VCC--	9  10  
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
    '''
    Thread manages LED which acts as a visual verification that
    the bot is still functioning
    '''
    def __init__(self):
        threading.Thread.__init__(self)
        self.name="HeartBeatThread"
        self.daemon = True
    def run(self):
        logging.debug( "STARTING THAT SICK BEAT YO")
        rpiGPIOFunctions.heartBeat()
    #def stop(self):
    #    self._stop.set()
    #def stopped(self):
    #    return self._stop.isSet()

class twitterThread(threading.Thread):
    '''
    Runs the twitter bot proper, currently not in use
    '''
    def __init__(self):
        threading.Thread.__init__(self)
        self.name="TwitterBotThread"
        self.daemon = True
    def run(self):
        logging.debug("Starting to Tweet")
        api, searchEV, eventKDEs, polyF, knn_models = startup() 
        runBot(api, searchEV, eventKDEs, polyF, knn_models)
        logging.debug("I ESCAPED")
    #def stop(self):
    #    self._stop.set()
    #def stopped(self):
    #    return self._stop.isSet()

class restartButtonThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name="restartButtonThread"
        self.daemon = True
    def run(self):
        logging.debug( "Button is active")
        rpiGPIOFunctions.buttonListener()
    #def stop(self):
    #    self._stop.set()
    #def stopped(self):
    #    return self._stop.isSet()


def buildMsg(event, timeStamp, locations):
    loc = locationFromText.getLocation(locations)
    event = event[0].upper()+event[1:].lower()
    msg = "I think Event: " + str(event) + " has occurred" + str(loc) + "\n" + str(timeStamp) + " CDT"
    return msg




def piMain():
    heartB = heartBeatThread()
    powerButton = restartButtonThread()
    tweetStuff = twitterThread()

    try:
        heartB.start()
        powerButton.start()
        #unCorruptFiles.main()
        tweetStuff.start()
    except(KeyboardInterrupt, SystemExit):
        #heartB.stop()
        #tweetStuff.stop()
        #powerButton.stop()
        pass
    return
	


def startup():

    #rpiGPIOFunctions.ledCycle()
    searchEV = botHelperFunctions.eventLists()
    polyF = polysemyFilters.load_filters(filter_root_fp="misc/polysemyFilterModels/", events=searchEV)
    knn_models = polysemyFilters.build_knn_classifier_model(text_root_fp='utils/nlpTools/filters/poly_ref_texts/', polyF=polyF, events=searchEV)
    eventKDEs = plotManager.updateKDE(None)
    
    # Get API last to avoid repeated pings if other startup modes fail
    api = getTwitterAPI()
    return api, searchEV, eventKDEs, polyF, knn_models



def runBot(api, searchEV, eventKDEs, polyF, knn_models):


    rppSize = 50
    tweetTracker = 0
    oldEvent = ""
    #eventKDEs = None
    rpiGPIOFunctions.myLED("GREEN")

    # **** Topology Network Stuff ****
    lowWRG = wordRelationTools.embedding_projection()
    lowWRG.load('utils/experimental/topology/sample_reduced_model_v2_k50.tar.gz')
    lowWRT10 = wordRelationTools.embedding_projection()
    lowWRT10.load('utils/experimental/topology/twitter_text_model_reduced_k50_10perc.tar.gz')
    networks = {}
    
    # event = 'Shipwreck'
    # ttn = tweetNetworkExploration.twitter_recent_history_network(lowWRG=lowWRG, lowWRT10=lowWRT10)
    # if os.path.isfile('temp/'+event+'_save.json'):
    #     logging.debug("Loading Network for Event " + event)
    #     ttn.load('temp/'+event+'_save.json')
    # networks[event] =  ttn#tweetNetworkExploration.twitter_Top_Network(lowWRG=lowWRG, lowWRT10=lowWRT10)

    for event in searchEV:
        ttn = tweetNetworkExploration.twitter_recent_history_network(lowWRG=lowWRG, lowWRT10=lowWRT10)
        if os.path.isfile('temp/'+event+'_save.json'):
            logging.debug("Loading Network for Event " + event)
            ttn.load('temp/'+event+'_save.json')
        networks[event] =  ttn#tweetNetworkExploration.twitter_Top_Network(lowWRG=lowWRG, lowWRT10=lowWRT10)

    # Start the state machine  

    try:
        while True:
            # Run Time based checks        
            eventKDEs = plotManager.updateKDE(eventKDEs) #  Load kde values      
            # [(X_plot, log_dens), allHistAvgs, histAvg, histStd]]  
            plotManager.plotSummaries(api) #  Check if tweet trends haven't been tweet
            for i, event in enumerate(searchEV): # Perform a search on all events
                rpiGPIOFunctions.myLED("GREEN")
                #print event, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                # Get historical data
                #allWeekAvgs, weekAvg, weekStd, sampleTimes = getEventLastWeek(event)
                sampleTimes, allWeekAvgs= botHelperFunctions.getEventHistoryTimeLimit(event, weeks=1, days=0, hours=0, minutes=0)
                weekAvg, weekStd = botHelperFunctions.getEventHistoryStats(allWeekAvgs)
                kdePlots, allHistAvgs, histAvg, histStd = eventKDEs[i]

                # Get tweets And Filter
                tweets = twitterInteractions.getTweets(api, event)
                tweets_all = tweets[:]
                eventTimestamp = time.time() 
                olen = len(tweets)
                tweets = polysemyFilters.polysemyFilter(tweets, polyF[event], knn_models[event]) # Cool I've got tweets. We need to filter out tweets about polysems
                plen = len(tweets)
                if olen != plen:
                    print("Purged ", (olen-plen) /olen * 100, '% of tweets')
                tweets = grammarFilters.negationFilter(tweets, event)

                # **** Add to topology Structure ****
                networks = tweetNetworkExploration.add_sample_to_network(networks, event, eventTimestamp, tweets)


                # Time to get all of the features
                tweetCount = len(tweets)
                tweetMean, tweetStd, tbtwTweets = simpleClassifier.getTweetsDistrobution(tweets)

                # Feature Vector
                fv = [ \
                tweetCount, tweetMean, tweetStd, 
                weekAvg, weekStd,
                histAvg, histStd]
                #print weekAvg, weekStd
                if math.isnan(weekAvg) or math.isnan(weekStd):
                    isEvent = False
                else:
                    isEvent = simpleClassifier.classifyEvent(event, fv, oldEvent)


                # Save Sampled Distrobution
                botHelperFunctions.saveToHistoryFile(tweetMean, tweetStd, tweetCount, event)

                #isEvent = False ### HEY DELETE THIS YOU DOLT
                # I should probably ignore it if there aren't enough tweets, but we'll see
                if isEvent:
                    rpiGPIOFunctions.myLED("EVENT")
                    logging.debug(event + "IT'S AN EVENT HOT DOG!")
                    locations = locationFromText.processLocations(tweets, event)
                    timeStamp, media = plotManager.makeDistPlot(event, fv, tbtwTweets, allWeekAvgs, allHistAvgs, kdePlots)
                    try:
                        topFilePath = tweetNetworkExploration.make_Image(networks[event])
                    except:
                        # Startup bodge when nework has only an initial amount of samples
                        print("MAKING STARTUP BODGE IMAGE SWAP")
                        topFilePath = media
                    msg = buildMsg(event, timeStamp, locations)
                    twitterInteractions.tryToTweet(api, msg, media)
                    #twitterInteractions.tryToTweet(api, msg, topFilePath) # Not used when not in experimental
                    logging.debug(msg)

                #media = makeDistPlot(event, fv, tbtwTweets, allWeekAvgs, allHistAvgs, kdePlots)
                botHelperFunctions.save_recent_tweets(tweets_all)

                #locations = processLocations(tweets, event)
                #print event, tweetCount, '\n\t', locations
            #print "Sleeping...", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            rpiGPIOFunctions.myLED("SLEEP")
            time.sleep(5*60)
    except KeyboardInterrupt:
        print("Exiting and Saving...")
        for event in searchEV:
            ttn = networks[event]
            ttn.save('temp/'+event+'_save.json')

        
    return



def getTwitterAPI():
    # Determine Hardware
    onRPi = rpiGPIOFunctions.checkHardware()
    if onRPi:
        from asecretplace import getKMKeys
    else:
        from asecretplace import getChatBotKeys as getKMKeys
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



if __name__ == "__main__":
    print("Cool")
    #api, searchEV= startup()
    #runBot(api, searchEV)

    heartB = heartBeatThread()
    powerButton = restartButtonThread()
    tweetStuff = twitterThread()

    try:
        print("Starting threads")
        heartB.start()
        powerButton.start()
        unCorruptFiles.main()
        #tweetStuff.start()
        api, searchEV, eventKDEs, polyF, knn_models = startup()
        logging.debug("Startup complete, running bot..")
        runBot(api, searchEV, eventKDEs, polyF, knn_models)
    except(KeyboardInterrupt, SystemExit):
        #heartB.stop()
        #tweetStuff.stop()
        #powerButton.stop()
        pass


print("Works")
logging.debug('test')