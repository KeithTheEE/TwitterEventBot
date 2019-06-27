

import logging


def negationFilter(tweets, event):
    '''
    Remove tweets which say the event didn't happen. 
        "No tsunami threat present" 

    Parameters
    ----------
    tweets: list
        A list of tweets (tweepy tweet struct) 
    event: str
        A string for the event

    Returns
    -------
    tweets: list
        A list of all tweets (tweepy tweet object), filtered to remove tweets
        which say the event won't or didn't occur


    Notes
    -----
    Currently incomplete. Just a dummy function until I build the projection matrix
    Really this is a grammar filter, and the polyseme filter is a semantic filter
    ''' 


    return tweets