


import socket
import logging

import time
import datetime
import tweepy
import os

from utils import rpiGPIOFunctions
from utils.nlpTools.filters import unspam
from utils.nlpTools import locationFromText



class reclassTweet(object):
    def __init__(self, tweet=None):
        if 'None' not in str(type(tweet)):
            pass

    def convert_to_json(self):
        pass
    def load_from_json(self):
        pass


def is_connected():
    REMOTE_SERVER = "www.google.com"
    try:
        logging.info("Testing Internet Connection")
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




def gotTweepError():
    '''
    Just kill some time. 5 minutes for tweepy, 1 for no internet

    Notes
    -----
    I need to add a condition that reboots if wifi is down for too long

    '''
    # check if the error is internet connection based on
    connected = is_connected()

    if connected:
        logging.debug( "I started to annoy twitter, now I have to wait a bit" + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        rpiGPIOFunctions.myLED("YELLOW")
        time.sleep(60*5)
    else:
        logging.warning("I'm not connected to the network at the moment, sorry")
        rpiGPIOFunctions.myLED("RED")
        time.sleep(60*1)
    rpiGPIOFunctions.myLED("GREEN")
    return



def getTweets(api, event, rppSize=50):
    '''
    Grabs around 50 tweets (most recent) from twitter
    Blantantly spam tweets are removed (exact copies)

    Parameters
    ----------
    api: twitter api
        this is needed for all twitter communciation
    event: str
        A string that is the keyword in a twitter search
    rppSize: int
        Default = 50
        the number of tweets you want twitter to return to you (max is 50)

    Returns
    -------
    listOfTweets: list
        A list of all tweets (tweepy tweet object), filtered to remove basic spam


    Notes
    -----


    '''

    # Get a set of tweets, and filter them
    # Tweets are events, filters such that 
    #    Retweets are removed
    #    URLs are stripped of the tweet
    #    Accounts with the event in their name are removed from the set (Not yet working)
    #    

    # Grab my handle to avoid grabbing my own tweets

    while True:
        try:
            myHandle = api.me().screen_name.encode('utf-8')
            break
        except tweepy.TweepError:
            gotTweepError()
    


    # Grab Cursor tweets from the API, wrap in try/except for safety
    while True:
        try:
            tweetList = tweepy.Cursor(api.search,
                       q=event,
                       rpp=rppSize,
                       result_type="recent",
                       include_entities=True, 
                       tweet_mode='extended').items()
            break
        except tweepy.TweepError:
            gotTweepError()
    
            
        

    listOfTweets = []
    #for tweet in tweetList:
    tweetTracker = 0
    tweetTries = 0
    tweetDict = {}
    userDict = {}
    # We're just going to cycle through until we get enough tweets
    #   To make a judgement on event likelyhood.
    while True:
        try: # This 'try' is to catch 'rate limit exceeded' errors
            rpiGPIOFunctions.myLED("GREEN")
            tweet = tweetList.next()
            # most of this block needs to be added to processSpam
            tweetAge = time.time() - (tweet.created_at - datetime.datetime(1970,1,1)).total_seconds()
            # Process the Tweet
            newTweet, tweetDict, userDict = unspam.processSpam(tweet, tweetDict, userDict, event, myHandle)
            tweetTries += 1
            if newTweet:
                listOfTweets.append(tweet)
                tweetTracker += 1
                if (tweetTracker > rppSize) or (tweetTries > 100):
                    tweetTracker = 0
                    break
            if tweetAge > 24*60*60:
                # No sense in asking for more tweets, they'll all be older than this
                break

        except tweepy.TweepError: 
            gotTweepError()
        except StopIteration:
            break

    return listOfTweets




def tryToTweet(api, msg, media):
    fn = os.path.abspath(media)
    if (len(msg) > 116):
        msg = msg[0:115]
    attempts = 0
    limit = 3
    while True:
        success = False
        try:
            api.update_with_media(fn, status=msg)
            success = True
            break
        except tweepy.TweepError:
            gotTweepError()
        if attempts > limit:
            break
        attempts += 1
    rpiGPIOFunctions.myLED("EVENT")
    return success
