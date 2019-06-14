

from utils.nlpTools.filters.unspam import *
import tweepy
import json


def get_tweepy_status_populated():

    # Load sample data in place
    with open('tests/testTweetOut.json', 'r') as ifl:
        tweetSet = json.load(ifl)


    tweets_from_disk = []
    for x in tweetSet:
        tweets_from_disk.append(tweepy.models.Status().parse(None, x))

    return tweets_from_disk
    

def test_processSpam():
    tweets = get_tweepy_status_populated()
    tweet = tweets[0]
    spamTruth, tweetDict, userDict = processSpam(tweet, {}, {}, 'tornado', u'Keith_Event')
    pass


def test_processSpam_Multiple():
    tweets = get_tweepy_status_populated()
    tweetDict  = {}
    userDict = {}
    for tweet in tweets:
        spamTruth, tweetDict, userDict = processSpam(tweet, tweetDict, userDict, 'tornado', u'Keith_Event')
    pass