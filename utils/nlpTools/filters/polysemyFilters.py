




import logging




def polysemyFilter(tweets, event):
    '''
    Remove polyseme's of the event (OKC Thunder, Blizzard from DQ, or the gaming company)

    Parameters
    ----------
    tweets: list
        A list of tweets (tweepy tweet struct) 
    event: str
        A string for the event

    Returns
    -------
    tweets: list
        A list of all tweets (tweepy tweet object), filtered to remove polyseme's


    Notes
    -----
    Currently incomplete. Just a dummy function until I build the projection matrix

    Right. Well. Hmm
    First, I need a collection (for each event) of tweets (I mean strings) With the 
    correct data, and some with the polyseme.

    Dairy Queen Ads and Ice cream lists
    Blizzard Gaming Anything. Overwatch, LoL, WoW, whatever.
        Especially Sale talk
    Pokemon--Less of a event happening trigger, but it really messes with Location
        Pokemon go bots tweeting where a pokemon with the move earthquake is happening
        more
    OKC Thunder. Anything with basketball, and probably any sports ball. 

    Also hail. Tweets about football Hail Mary's, Hail Varsity, and Hail any body of 
        worship, whether serious or sarcastic, is a huge pain. Most hail tweet distrobutions
        are fairly wide apart unless there's a tornado somewhere

    Lightning: I need soo many filters on that one. Ligthning sale, lightning charger, so
        on and so forth. Jan 2018 the bot uses the word lightening, but until the polyseme
        filter is online, I'm not going to fix this. 

    Since we're talking about what would be nice, maybe look to see if "No Tsunami" is also
        posible to polyseme filter. 


    It might be most useful to build in a notebook page, and then port the final projection
        matrix over here. There will be a lot of testing, but once the projection matrix
        is built, it's just a matter of loading it, projecting, and either running a cluster
        centroid test, or a SVM, or any other method. Either way, it's nothing compared to
        generating the matrix. 

    Finally, I don't yet know if I'll be building a projection for each event, or one hyper
        projection which hopefully would work on all 


    '''
    


    return tweets
