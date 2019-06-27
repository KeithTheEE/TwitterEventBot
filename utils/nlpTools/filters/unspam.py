

from utils.nlpTools.filters import twitterSpecific


import logging


def processSpam(tweet, tweetDict, userDict, event, myHandle):
    '''
    Remove blantantly spam tweets, nothing else

    Parameters
    ----------
    tweet: tweepy tweet structure
        Just the tweet itself, all of its data
    tweetDict: dict
        previous tweet text stored in it
    userDict: dict
        usernames, allowed 5 total appearences
    event: str
        The event we're trying to talk about, removes "@JohnnyTsunami tweeted this"
    myHandle: str
        The twitter handle of this bot

    Returns
    -------
    uniqueTweet: Bool
        Boolean value, True if  it's not a retweet (by "RT...")
                                the event is mentioned, not just in username
                                After URL removal, it is still a tweet not previously seen
                                userhandle has been seen less than 5 times in this set
                       False otherwise
    tweetDict: dict
        Dictionary of all previous tweets
    userDict: dict
        Dictionary of all previous user handles, and counts of the number of times that 
        handle has appeared


    Notes
    -----
    I have yet to decide, but I might remove all @[generichandle42] because the grammer 
        calls it a location  if I do that, I might have to sub in a name to make the tweet 
        maintain grammer. High on the list to be considered is Slartybartfast.
        Still though, that might cause other problems. So we'll ease into that improvement

    I could filter out "Basketball", "DairyQueen", and "Blizzard Entertainment" tweets here, 
        but I think I'd really annoy twitter a lot this way. (If the tweet is "invalid" I 
        ask for another. So during an OKC, I'd get a ton of tweets talking about basketball,
        chuck them, ask for a ton more, and repeat. Better to just grab a set of unique 
        tweets, look at them, and make note if there's not enough "event" focused tweets)

    in testEvent/crowdSourceEvents (as of Aug 29 2017) this function is named 'processTweets'
        not processSpam

    '''

    handle = str(tweet.user.screen_name.encode('utf-8'))
    name = str(tweet.user.name.encode('utf-8'))
    try:
        text = str(tweet.text.encode('utf-8'))
    except AttributeError:
        text = str(tweet.full_text.encode('utf-8'))
    
    # Basic Spam Rejection:
    #   Reject Retweets
    if text[0:2] == "RT" or tweet.retweeted:
        return False, tweetDict, userDict
    # And I shouldn't influence myself (feedback isn't useful)
    if handle == myHandle:
        return False, tweetDict, userDict
    # Usernames have caused a problem for me..
    #   Keep an eye on this, see if twitter does translation for us in search
    if (event.lower() in handle.lower()) or (event.lower() in name.lower()):
        if event.lower() not in twitterSpecific.cleanTweetTextofAts(text.lower()):
            '''
            Only risk throwing the tweet out if the twitter handle has the event
            in their name. That way if twitter does translate queries, they're
            less likely to be omited. And if twitter doesn't, nothing changes
            '''
            return False, tweetDict, userDict
    # Usernames in Replies have also been a problem
    if tweet.in_reply_to_screen_name:
        if event.lower() in str(tweet.in_reply_to_screen_name.lower()):
            if event.lower() not in twitterSpecific.cleanTweetTextofAts(text.lower()):
                return False, tweetDict, userDict

    # re based url stripper: see re import comment
    cleanTweet = twitterSpecific.cleanTweetText(text)

    # Check Duplicate Tweets, and tweets from same account
    if cleanTweet in tweetDict:
        # Reject Repeats
        return False, tweetDict, userDict
    else:
        # This whole handle buisness is to reduce bot spam (see meteoroid lyrics bots)
        if handle in userDict:
            # Only let a single account have a max of 5 tweets
            # in case it's a user freaking out about an event
            if userDict[handle] > 5:
                return False, tweetDict, userDict
            userDict[handle] += 1
        userDict[handle] = 1
        tweetDict[cleanTweet] = 1
        return True, tweetDict, userDict