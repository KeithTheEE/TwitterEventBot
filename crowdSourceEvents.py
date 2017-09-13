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
import time
import math
import numpy as np
import nltk
nltk.data.path.append('/home/pi/nltk_data')
import datetime
import socket
import sys
import os
import re # http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
import threading
from sklearn.neighbors import KernelDensity
import unCorruptFiles
#import getKMKeys # Format of CK, CS, AK, AS
import getChatBotKeys as getKMKeys
#[CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]



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
	main1()
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
        logFile = open("crowdSource.log", 'r')
        data = logFile.read()
        logFile.close()
        flSize = os.path.getsize("crowdSource.log")
        if flSize == 0:
            raise EmptyFile # Cheap trigger for the except condition 
        if data == "":
            raise EmptyFile 
    except:
        # I'm being extra fancy, it's pointless, but I'm pleased with it
        # The time of the very first tweet from this twitter account
        firstTweetTime = "11:55 PM - 15 Apr 2015"
        firstTweetTime = firstTweetTime.replace('- ', '')
        from dateutil.parser import parse
        parsedTweetTime = parse(firstTweetTime)
        logFile = open("crowdSource.log", 'a')
        logFile.write("Last Startup:\t" + 
                str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + '\n')
        logFile.write("Last KDE Update:\t" +
                str(parsedTweetTime.strftime("%Y-%m-%d %H:%M")) + '\n')
        logFile.write("Last Weekly Summary:\t" +
                str(parsedTweetTime.strftime("%Y-%m-%d %H:%M")) + '\n')
        logFile.close()




    lineAdded = False
    lineID = newLine.split('\t')[0]

    logFile = open("crowdSource.log", 'r')
    allLog = logFile.read()
    logFile.close()
    logFile = open("crowdSource.log", 'w')
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
        logFile = open("crowdSource.log", 'w')
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

    Raises 
    ------
    


    Notes
    -----



    """

    lineFound = False
    logFile = open("crowdSource.log", 'r')
    for line in logFile:
        if line != "":
            line = line.strip()
            key, value = line.split('\t')
            if key in lineID:
                theValue = value 
                lineFound = True

    logFile.close()
   

    if lineFound == False:
        logFile = open("crowdSource.log", 'w')
        logFile.write(allLog)
        logFile.close()
        raise SyntaxError("Given string '%s' not found in log entry" % lineID)

    return theValue
        




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
            # Consider running a wifi reconnect script now
            
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
        if theLED == "KDEPREP":
	    GPIO.output(red, False)
	    GPIO.output(yellow, True)
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
			os.system("sudo reboot")			
		buttonPress = True
		oldState = curState
		startTime = time.time()
	time.sleep(.001)
	if buttonPress:
	    duration = time.time() - startTime
	    if duration > 7:
		# Shutdown condition
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
	return False


def getLocation(locBestGuess):
    if len(locBestGuess) == 0:
	return " but I can't find where"
    elif len(locBestGuess) == 1:
	return " in " +str(locBestGuess[0])
    else:
	d = dict((i,locBestGuess.count(i)) for i in locBestGuess)
	return " in " +str(max(d, key=d.get))


	
def extractLocation(text):
    '''
    An NLTK based location extractor. 

    Parameters
    ----------
    text : string
        input text from tweets

    Returns
    -------
    locations : list of strings
        A list of strings from `text` that were extracted using the grammar 
        outlined 


    Notes
    -----
    A really basic and probably bug prone + hard to follow location extracter
    
    But hey, if it stops washington post from popping up all the damn time..
    
    Aaaaand at this point I realize that I basically wrote a program to find
    words that are capitalized...
    
    whoop... whoop.
    
    :|
    
    NLTK That bitchaz
    
    From what I can tell, this will have almost (if not more) false positives
    when compared to true positives. However these grammar rules that extract
    locations were written so their false negatives were minimal. I want to 
    miss as little information as possible. From other portions of the code
    (Event Feature Set) the bot should only trigger when an event occurs. From
    there there's an assumption that there will be more similar true positives 
    than similar false positives: the location signal can be extracted from the 
    background noise. 

    This also uses the nltk pos tagger, which assumes propper english rules are
    being followed (as was the case in its training data). That assumption is 
    invalid with twitter data. So 

    '''
    # Do the nltk stuff
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]

    locations = []
    
    for sent in tagged_sentences:
    
        words, pos = map(list, zip(*sent))
        #print "\t"+" ".join(words)
        #print "\t"+" ".join(pos)
        startC= ["NNP", "JJ"]
        validExtend = [ "NNP", ',', '#', "IN", "CC", "DT"]
        afterIN = ["NNP", "JJ"]
        validTerminal = ["NNP"]
        startHere = ["IN"] # Had JJ, JJ requires more grammer rules to be added. This is a bad formate for that


        locStart = -1
        locEnd = -1

        # Right, ok, I need to read CH7 of the NLTK book and make a better method.
        #   But, this will at least establish a baseline for CH7 performance
        nnpChar = False
        if pos[0] in startC:
            if pos[0] == "NNP":
                nnpChar = True
            locStart =0
            tail = 1
            if len(pos)>1:
                i = 1
                while (pos[i] in validExtend) and i+1<len(pos): # Double check that, might be off by 1
                    if pos[i] == "NNP":
                        nnpChar = True
                    tail = i+1
                    i += 1
            #print sent[locStart][0], locStart
            #print tail
            #print sent[0:0]
            #print sent[locStart:tail][0]
            if nnpChar == True:
                locations.append(" ".join(words[locStart:tail]))


        # Oh great Off By One Gods, I know you must have a sacrifice of IndexErrors,
        #   But I pray you are satasfied with my offerings early on, rather than 
        #   late
        #      into the night
        #           when I am furious at the code
        #               and delerious from adding and subtracting 1's from all lines
        # Oh great Off By One Gods
        #   Hear my plea

        #print len(sent)
        i = 0
        locStart = -1
        tail = -1
        lastNNPindex = -1
        # Edit to start on nnp so if you have vb something, in, it'll start on nnp
        while i < len(sent):
            if pos[i] in startHere:
                # Sweet! Step Forward one character if possible
                if i+1 >= len(pos):
                    break
                i += 1
                # Check if post startHere is a valid afterIN or validExtend
                if (pos[i] in afterIN) or (pos[i] in validExtend):
                    locStart = i
                    if pos[i] == "NNP":
                        lastNNPindex = i
                    # Woo, it was, that's the start of our location!
                    while len(pos) > i+1:
                        if i+1 >= len(pos):
                            break
                        i+=1
                        if pos[i]=="NNP":
                            lastNNPindex = i
                        if pos[i] not in validExtend:
                            break
                            
                    # ummmm
                    # How about we reverse to find
                    #if i > locStart+1:
                    tail = lastNNPindex+1  # That should be allowed via sent[locStart:tail]
                    #else:
                    #    tail = i
                    if tail > locStart:
                        locations.append(" ".join(words[locStart:tail]))
                    locStart = -1
                    tail = -1
                    lastNNPindex = -1
                    # *should*
            i += 1

    # You are the worst gods ever OBO gods.
    #    A genie would grant my prayer with fewer strings attached...

    #if locStart > -1:
        #print sent[locStart:tail]
    
    return locations

def processLocations(tweets, event):

    # Now we get ready to tweet!! :D
    locBestGuess = []
    for tweet in tweets:
        aTweet = tweet.text.encode('utf-8')
        words = aTweet.split(" ")
        try:
            guessLocation = []
            guessLocationTemp = extractLocation(cleanTweetTextofAts(aTweet))
            for location in guessLocationTemp:
                if event.lower() not in location.lower(): # Stop saying a tornado occured in tornado
                    guessLocation.append(location)
        except UnicodeDecodeError:
            print "Got unicodeDecodeError.."
            guessLocation = []
        if len(guessLocation)>0:
            for loc in guessLocation:
                locBestGuess.append(loc)

    # now we've looked at the tweets and tried to guess a location
    
    #locBestGuess1 = getLocation(locBestGuess)
    return locBestGuess

	
def cleanTweetText(text):
    #removes urls
    return re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text, flags=re.MULTILINE)

def cleanTweetTextofAts(text):
    #removes urls and @ mentions
    # Though it doesn't really.. It misses 'there' in @here_there 
    text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text, flags=re.MULTILINE)
    text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",text).split())
    # Consider this mod if I end up getting lots of unicode errors. Weeee.....
    #printable = set(string.printable)
    #text = filter(lambda x: x in printable, text)
    return text

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

    handle = tweet.user.screen_name.encode('utf-8')
    name = tweet.user.name.encode('utf-8')
    text = tweet.text.encode('utf-8')
    
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
        if event.lower() not in cleanTweetTextofAts(text.lower()):
            '''
            Only risk throwing the tweet out if the twitter handle has the event
            in their name. That way if twitter does translate queries, they're
            less likely to be omited. And if twitter doesn't, nothing changes
            '''
            return False, tweetDict, userDict
    # Usernames in Replies have also been a problem
    if tweet.in_reply_to_screen_name:
        if event.lower() in tweet.in_reply_to_screen_name.lower():
            if event.lower() not in cleanTweetTextofAts(text.lower()):
                return False, tweetDict, userDict

    # re based url stripper: see re import comment
    cleanTweet = cleanTweetText(text)

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

def polysemeFilter(tweets, event):
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

    Since we're talking about what would be nice, maybe look to see if "No Tsunami" is also
        posible to polyseme filter. 


    It might be most useful to build in a notebook page, and then port the final projection
        matrix over here. There will be a lot of testing, but once the projection matrix
        is built, it's just a matter of loading it, projecting, and either running a cluster
        centroid test, or a SVM, or any other method. Either way, it's nothing compared to
        generating the matrix. 

    Also, I don't yet know if I'll be building a projection for each event, or one hyper
        projection which hopefully 


    '''
    


    return tweets
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
    ''' 


    return tweets

def gotTweepError():
    # check if the error is internet connection based
    connected = is_connected()
    #connected = True
    if connected:
        print "I started to annoy twitter, now I have to wait a bit"
        myLED("YELLOW")
        time.sleep(60*5)
    else:
        print "I'm not connected to the network at the moment, sorry"
        myLED("RED")
        time.sleep(60*1)
    return

def getTweets(api, event, rppSize=50):
    '''
    Remove blantantly spam tweets, nothing else

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
                       include_entities=True).items()
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
            myLED("GREEN")
            tweet = tweetList.next()
            # most of this block needs to be added to processSpam
            tweetAge = time.time() - (tweet.created_at - datetime.datetime(1970,1,1)).total_seconds()
            # Process the Tweet
            newTweet, tweetDict, userDict = processSpam(tweet, tweetDict, userDict, event, myHandle)
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

def getEventHistory(event):

    try:
    	eventHistory = open(str(event) + ".txt", 'r')
    except IOError:
	eventHistory = open(str(event) + ".txt", 'a')
	eventHistory.close()
	eventHistory = open(str(event) + ".txt", 'r')
    theTimes = []
    allHistAvgs = []
    theVar = []
    for line in eventHistory:
	if line == "":
	    break
	try:
	    line = line.split('\t')
	    theTimes.append(line[0])
	    allHistAvgs.append(float(line[1]))
	    theVar.append(float(line[2]))
	except:
	    print "Average File Error"
	
    eventHistory.close()

    histAvg = np.mean(allHistAvgs)
    histStd = np.std(allHistAvgs)

    return allHistAvgs, histAvg, histStd

def getEventLastWeek(event):
    """
    Functionally similar to `getEventHistory`, this grabs only the 
    history of the last week (might be modified to last month) to 
    create a rolling comparision, preventing continous event tweets
    about the same subject (see spikes in tweet post NK Missile Tests)

    

    Parameters
    ----------
    event : string
        keyword used for data files


    Returns
    -------


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
    	eventHistory = open(str(event) + ".txt", 'r')
    except IOError:
	eventHistory = open(str(event) + ".txt", 'a')
	eventHistory.close()
	eventHistory = open(str(event) + ".txt", 'r')
    sampleTimes = []
    allWeekAvgs = []
    theVar = []
    for line in eventHistory:
	if line == "":
	    break
	try:
	    line = line.split('\t')
	    sampleTimes.append(line[0])
	    allWeekAvgs.append(float(line[1]))
	    theVar.append(float(line[2]))
	except:
	    print "Average File Error"
	
    eventHistory.close()

    # Reduce search space
    weekMaxSize = 2016
    if len(sampleTimes) > weekMaxSize:
        sampleTimes = sampleTimes[-weekMaxSize:]
    if len(allWeekAvgs) > weekMaxSize:
        allWeekAvgs = allWeekAvgs[-weekMaxSize:]

    # Parse theTimes for correct oldest sample
    x = np.array([datetime.datetime.strptime(d,'%Y-%m-%d%H:%M') for d in sampleTimes])
    i = 0
    while i < len(sampleTimes):
        if  x[i] > datetime.datetime.now()-datetime.timedelta(weeks=1):
            break
        i+=1

    sampleTimes = x[i:]
    allWeekAvgs = allWeekAvgs[i:]

    weekAvg = np.mean(allWeekAvgs)
    weekStd = np.std(allWeekAvgs)

    return allWeekAvgs, weekAvg, weekStd, sampleTimes

def updateKDE(kdeOld, runTime='3_AM', runWindow=3, minAgeHours=8):
    """
    Generates the KDE over the event history for each events
    This is done at startup, and once per day at approximately 
    2 am CDT (VERIFY/SET AS VARIBLE) 

    Parameters
    ----------
    kdeOld : list or Nonetype
    

    Returns
    -------

    Other Parameters
    ----------------

    Raises
    ------

    See Also
    --------

    Notes
    -----
    Start condition should be if `kdeOld` == "None"
    Suggested condition should be if time is greater than 2 and 
    last set is greater than 23, reset kde OR if time is greater 
    than two and last reboot is less than 23

    * Consider triggering this instead of time.sleep 
    in the state machine 

    ** Consider updating only one KDE at a time, then running through
       the event search space. That way there isn't massive downtime 
       on the pi, minimizing missed events. 
         Should be simple enough to do. 
         This would naturally be ignored on startup KDE (kdeOld == None)


    """
    def convertRunTime(rt):
        time, ampm = rt.split('_')
        if ':' in time:
            hour, minute = time.split(':')
        else:
            hour = time
            minute = '00'
        if ampm.upper() == 'PM':
            hour = int(hour) + 12
        hour = int(hour)
        minute = int(minute)
        dt = datetime.datetime.now()
        dt = dt.replace(hour=hour, minute=minute)
        return dt


    conditional = False

    # Decide if condition is met
    if kdeOld == None:
        # This only runs on startup
        conditional = True
        kdeOld = []
    else:
        # Checks if it's After 3 am, and has been more than 8 hours since last update
        runTime = convertRunTime(runTime)
        dontRunAfter=runTime+datetime.timedelta(seconds=runWindow*3600)

        lastRun = getLoggedData("Last KDE Update:")
        lastRun = datetime.datetime.strptime(lastRun,'%Y-%m-%d %H:%M')

        delta = datetime.datetime.now() - lastRun

        if delta.seconds >= minAgeHours*3600:
            if datetime.datetime.now() > runTime:
                if datetime.datetime.now() < dontRunAfter:
                    conditional = True


    if conditional:
	myLED("KDEPREP")
        searchEV = eventLists()
        for event in searchEV:
            theAvgs, compAvg, compStd = getEventHistory(event)
            allHistAvgs, histAvg, histStd = getEventHistory(event)


            x1 = np.linspace(0, histAvg+(3*histStd), 100*(6*histStd))
            allHistAvgs = np.array(allHistAvgs)
            allHistAvgs = allHistAvgs[:, None]
            X_plot = np.linspace(0, histAvg+(3*histStd), len(allHistAvgs))[:, None]
            # KDE For Event
            maxPoint = max(allHistAvgs)
            bw = float(maxPoint)*0.012
            kde = KernelDensity(kernel='epanechnikov', bandwidth=bw)
            kde.fit(allHistAvgs)
            log_dens = kde.score_samples(X_plot)
            kdeOld.append([(X_plot, log_dens), allHistAvgs, histAvg, histStd])

        print "Updated KDE"
        logLine = "Last KDE Update:\t"+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        updateLogFile(logLine)


    
    return kdeOld

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
    myLED("EVENT")
    return success

def plotSummaries(api, runOn='FRI', runTime='6_PM', minAgeDays=4):
    """
    If it's Sunday Night and the system has been online for
    most of the last week, tweet a 'trends' plot for each event

    Notes
    -----
    I need to figure out the timing between the tweets
    as well as an acceptable measure of down time

    Also, if I miss the time it triggers on, but come online a few 
    hours later, should I tweet? I think so.

    minAgeDays = 4 : Basically, never consider building plots if the 
    last plot was tweeted less than 4 days ago 
    """
    def adjustAverage(x):
        #return math.log(1+1/float(x + 0.0001))
        return 1/float(x + 0.01)
    def convertRunTime(rt):
        time, ampm = rt.split('_')
        if ':' in time:
            hour, minute = time.split(':')
        else:
            hour = time
            minute = '00'
        if ampm.upper() == 'PM':
            hour = int(hour) + 12
        hour = int(hour)
        minute = int(minute)
        dt = datetime.datetime.now()
        dt = dt.replace(hour=hour, minute=minute)
        return dt
    def adjustTimes(sampleTimes, allWeekAvgs):
        # This should just find long gaps in data, and
        # force the plot to zero it out
        segments = []
        adjSampleTimes = []
        adjAllWeekAvgs = []
        lastSampleTime = sampleTimes[0]
        lastAvg = allWeekAvgs[0]
        tooLongofAwait = 2 # hours

        for i in range(1, len(sampleTimes)):
            delta = sampleTimes[i] - lastSampleTime 
            adjSampleTimes.append(lastSampleTime)
            adjAllWeekAvgs.append(adjustAverage(lastAvg))
            if delta.seconds > tooLongofAwait*3600:
                segments.append([adjSampleTimes, adjAllWeekAvgs])
                adjSampleTimes = []
                adjAllWeekAvgs = []
                
            lastSampleTime = sampleTimes[i]
            lastAvg = allWeekAvgs[i]

        adjSampleTimes.append(sampleTimes[-1])
        adjAllWeekAvgs.append(adjustAverage(allWeekAvgs[-1]))
        segments.append([adjSampleTimes, adjAllWeekAvgs])
        
        return segments
        
       
    # SETTINGS 
    # Moved to inputs with expected values
    #runOn = 'SUN'
    #runTime = '6_PM' # Hour(:minute)_DayHalf
    #minAgeDays = 4 # Basically, never consider building plots if the last plot 

    weekSet = ['MON', 'TUE', 'WED', 'THR', 'FRI', 'SAT', 'SUN']

    itsGoTime = False
    runTime = convertRunTime(runTime)

    lastRun = getLoggedData("Last Weekly Summary:")
    lastRun = datetime.datetime.strptime(lastRun,'%Y-%m-%d %H:%M')

    delta = datetime.datetime.now() - lastRun
    
    if delta.days >= minAgeDays:
        if datetime.datetime.today().weekday() == weekSet.index(runOn):
            if datetime.datetime.now() > runTime:
                itsGoTime = True



    #itsGoTime = True
    if itsGoTime == True:
        searchEV = eventLists()
        for event in searchEV:
            
            allWeekAvgs, weekAvg, weekStd, sampleTimes = getEventLastWeek(event)
            segments = adjustTimes(sampleTimes, allWeekAvgs)

            msg = "Weekly Summary for " + event[0].upper() + event[1:].lower()
            media = "weeklySummary"+event[0].upper() + event[1:].lower()+".png"
            plt.title(event[0].upper() + event[1:].lower())
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.gcf().autofmt_xdate()
            for seg in segments:
                x = seg[0]
                y = seg[1]
                plt.plot(x, y, linewidth=1.0, color='b')
            plt.title(msg)
            plt.ylabel("Tweets Per Second")
            #plt.show()
	    plt.savefig(media, bbox_inches='tight')
            plt.close()
            success = tryToTweet(api, msg, media)
            time.sleep(3)
        logLine = "Last Weekly Summary:\t"+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        updateLogFile(logLine)

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

    keyEventsDB = "listOfTwitterEvents.txt"
    #   Events
    eventL = open(keyEventsDB, 'r')
    searchEV = []
    for event in eventL:
	searchEV.append(event.strip())
    eventL.close()
    return searchEV

def getTweetsDistrobution(tweets):
    tbtwTweets = []
    for i in range(1, len(tweets)):
        delta = tweets[i-1].created_at - tweets[i].created_at
        delta = delta.total_seconds()
        tbtwTweets.append(delta)
    #print tbtwTweets

    return np.mean(tbtwTweets), np.std(tbtwTweets), tbtwTweets



def saveToHistoryFile(sampledMean, sampledVar, tweetCount, event):
    # zSc is a holdover of legacy code. One of these updates will 
    #   remove it completely, it's not actually used anymore
    #   and can be calculated readily from all previous data
    zSc1 = 'x'
    zSc2 = 'z'
    eventHistory = open(str(event) + ".txt", 'a')
    eventHistory.write(datetime.datetime.now().strftime("%Y-%m-%d%H:%M") \
        + '\t' + str(sampledMean) + '\t' + str(sampledVar) +'\t' + str(zSc1) + 
        '\t' + str(zSc2) +"\t"+ str(tweetCount) +'\n')
    eventHistory.close()
    return 

def classifyEvent(event, featureVector, oldEvent):
    tweetCount = featureVector[0]
    tweetMean = featureVector[1]
    tweetStd = featureVector[2]
    weekAvg = featureVector[3]
    weekStd = featureVector[4]
    histAvg = featureVector[5]
    histStd = featureVector[6]

    # Cu: Current mean 
    # Co: Current St. Deviation

    # Wu: Week Mean
    # Wo: Week St. Deviation

    # Hu: Historical Mean
    # Ho: Historical St. Deviation

    # Probability technically z score) sampled mean could be 
    # randomly generated given a normal function using the historical 
    # average and historical standard deviation

    isEvent = True

    if tweetCount < 14:
        isEvent = False
    if tweetMean > histAvg:
        isEvent = False
    if tweetMean > weekAvg:
        isEvent = False
        

    # (Cu - Hu)/Ho
    CuHu_Ho = (tweetMean-histAvg)/histStd

    # (Cu - Wu)/Wo
    CuWu_Wo = (tweetMean-weekAvg)/weekStd

    # (Hu - Cu)/Co
    HuCu_Co = (histAvg-tweetMean)/tweetStd

    # (Wu - Cu)/Co
    WuCu_Co = (weekAvg-tweetMean)/tweetStd

    if CuHu_Ho*HuCu_Co > -2:
        isEvent = False

    if (oldEvent == event) and (CuHu_Ho*HuCu_Co) > -10:
        isEvent = False


    if CuWu_Wo*WuCu_Co > -0.1:
        #print "Failed that one test\n\t" + str(isEvent) +'\t'+ str(CuWu_Wo*WuCu_Co)
        isEvent = False
    #else:
    #    print "PASSED IT\n\t" + str(isEvent) +'\t'+ str(CuWu_Wo*WuCu_Co)

    # Should save classifier (Will take care of it after filters are online

    return isEvent
    

    
    
    
def makeDistPlot(event, featureVector, tbtwTweets, allWeekAvgs, allHistAvgs, kdePlots):
    media = "tweetProof.png"
    timeStamp = time.ctime(time.time())

    tweetCount = featureVector[0]
    tweetMean = featureVector[1]
    tweetStd = featureVector[2]
    weekAvg = featureVector[3]
    weekStd = featureVector[4]
    histAvg = featureVector[5]
    histStd = featureVector[6]
   
    xHist = np.linspace(0, histAvg+(3*histStd), 100*(6*histStd))
    xWeek = np.linspace(0, weekAvg+(3*weekStd), 100*(6*weekStd))
    xCur = np.linspace(0, tweetMean+(3*tweetStd), 100*(6*tweetStd))

    # Historic KDE (prebuilt)
    histKdeX = kdePlots[0]
    histKdeY = kdePlots[1]

    # Build Current KDE
    xmax = max(allHistAvgs)
    kdeC = KernelDensity(kernel='epanechnikov', bandwidth=float(tweetMean+(3*tweetStd))*.1) # 0.065 is alright
    kdeC.fit(np.array(tbtwTweets)[:, np.newaxis])
    kdeCx = np.linspace(0, int(xmax), 1000)[:, np.newaxis]
    log_densC = kdeC.score_samples(kdeCx)

    # Build weekKDE
    kdeW = KernelDensity(kernel='epanechnikov', bandwidth=float(weekAvg+(3*weekStd))*.1) # 0.065 is alright
    kdeW.fit(np.array(allWeekAvgs)[:, np.newaxis])
    kdeWx = np.linspace(0, int(xmax), 1000)[:, np.newaxis]
    log_densW = kdeW.score_samples(kdeWx)

    # Prep + marks
    tbtwTweets = np.array(tbtwTweets)[:, np.newaxis]


    # Finally at the plotting point..

    # Subplot 1
    plt.subplot(2, 1, 1)
    plt.title(event[0].upper()+event[1:] + " " + str(timeStamp) + " CDT")
    plt.ylabel("Frequency Density\nof Historic Averages")
    plt.hist(allHistAvgs, bins=1000)
    plt.axvline(x=tweetMean, color='r', label="Current Mean", linewidth=1.0)
    plt.legend(loc='upper right')
    plt.xlim(xmin=0)
    axes = plt.gca()
    tempSet = axes.get_xlim()

    # Subplot 2
    plt.subplot(2, 1, 2)
    plt.plot(xHist,mlab.normpdf(xHist, histAvg, histStd),'b',label='Historic Gaussian Distribution', linewidth=1.0)
    plt.plot(xCur,mlab.normpdf(xCur, tweetMean, tweetStd), 'g', label='Current Gaussian Distribution', linewidth=1.0)
    plt.plot(histKdeX, np.exp(histKdeY), 'r',label='KDE Fit of Historic Averages', linewidth=1.0)
    # Cap off top of current kde
    axes = plt.gca()
    ymin, ymaxOld = axes.get_ylim()
    
    # New KDE
    plt.plot(kdeCx, np.exp(log_densC), 'g', ls=':',label='KDE Fit of Current Tweets', linewidth=1.0)
    plt.plot(kdeWx, np.exp(log_densW), 'm', ls=':',label='KDE Fit of Past Week', linewidth=1.0)
    
    # Adjust y axis limits
    ymin, ymaxNew = axes.get_ylim()
    if ymaxOld*1.5 < ymaxNew:
        ymaxSet = ymaxOld*1.25
        plt.ylim(ymax=ymaxSet)
    plt.ylim(ymin=0)
    axes = plt.gca()
    ymin, ymax = axes.get_ylim()

    plt.plot(tbtwTweets[:, 0], ymax/12.0 * np.random.random(tbtwTweets.shape[0]) + ymax/20., '+k')

    # Finally, pretty up the plot, make things align
    plt.legend(loc='upper right')
    plt.ylabel('Modeled Approximate\nProbability Density')
    axes = plt.gca()
    plt.axvline(x=tweetMean, color='r', linewidth=1.0)
    #print axes.get_xlim()
    axes.set_xlim(tempSet)
    plt.xlabel("Average Time Between Tweets (Seconds)")
    plt.savefig(media, bbox_inches='tight')
    #plt.show()
    plt.close()

    return timeStamp, media

def buildMsg(event, timeStamp, locations):
    loc = getLocation(locations)
    event = event[0].upper()+event[1:].lower()
    msg = "I think Event: " + str(event) + " has occurred" + str(loc) + "\n" + str(timeStamp) + " CDT"
    return msg





def main1():



    # Header 
    api = getTwitterAPI()
    cities, maxSpace = cityData()
    searchEV = eventLists()
    
    # Time To TWEET IT UP :D
    rppSize = 50
    tweetTracker = 0
    oldEvent = ""
    eventKDEs = None
    myLED("GREEN")
    

    # Start the state machine  
    while True:
        # Run Time based checks        
        eventKDEs = updateKDE(eventKDEs) #  Load kde values      
        # [(X_plot, log_dens), allHistAvgs, histAvg, histStd]]  
        plotSummaries(api) #  Check if tweet trends haven't been tweet
	for i, event in enumerate(searchEV): # Perform a search on all events
            print event, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # Get historical data
            allWeekAvgs, weekAvg, weekStd, sampleTimes = getEventLastWeek(event)
            kdePlots, allHistAvgs, histAvg, histStd = eventKDEs[i]

            # Get tweets
            tweets = getTweets(api, event)
            eventTimestamp = time.time() 
            tweets = polysemeFilter(tweets, event) # Cool I've got tweets. We need to filter out tweets about polysems
            tweets = negationFilter(tweets, event)


            # Time to get all of the features
            tweetCount = len(tweets)
            tweetMean, tweetStd, tbtwTweets = getTweetsDistrobution(tweets)
            # Save Sampled Distrobution
            saveToHistoryFile(tweetMean, tweetStd, tweetCount, event)

            # Feature Vector
            fv = [ \
              tweetCount, tweetMean, tweetStd, 
              weekAvg, weekStd,
              histAvg, histStd]
            isEvent = classifyEvent(event, fv, oldEvent)

            # I should probably ignore it if there aren't enough tweets, but we'll see
            if isEvent:
                print "IT'S AN EVENT HOT DOG!"
                locations = processLocations(tweets, event)
                timeStamp, media = makeDistPlot(event, fv, tbtwTweets, allWeekAvgs, allHistAvgs, kdePlots)
                msg = buildMsg(event, timeStamp, locations)
                tryToTweet(api, msg, media)

            #media = makeDistPlot(event, fv, tbtwTweets, allWeekAvgs, allHistAvgs, kdePlots)


            #locations = processLocations(tweets, event)
            #print event, tweetCount, '\n\t', locations
        print "Sleeping...", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	time.sleep(5*60)
        
    return












def piMain():
    #Start three threads, one heartbeat, one standard, one for button reboot
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
    unCorruptFiles.main()
    powerButton = restartButtonThread()
    tweetStuff = twitterThread()

    try:
    	heartB.start()
	powerButton.start()
    	tweetStuff.start()
    except(KeyboardInterrupt, SystemExit):
	heartB.stop()
	tweetStuff.stop()
	powerButton.stop()
    return
	

 


# More or less, the program begins here
startupLogFile()
rPI = False
try: 
    import RPi.GPIO as GPIO 
    # Currently on the raspberry pi, or have a fake pi gpio library running
    rPI = True
    # These two lines are for the pi graphics handling the plots
    import matplotlib as mpl
    mpl.use('Agg')
    # Image Data
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    import matplotlib.dates as mdates
    # Actual twitter bot info
    import getKMKeys # Format of CK, CS, AK, AS
    #[CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]
except:
    # Image Data
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    import matplotlib.dates as mdates
    rPI = False
    # Demo bot info since testing uses @keithChatterBot
    #   Basically, I won't be using keith_event on the computer unless specific cir.
    import getChatBotKeys as getKMKeys

if (rPI == True):
    print "PI"
    piMain()
else:
    unCorruptFiles.main() # Sometimes files accrue errors
    main1()
    #print "Cool, double check shit"









def sampleNumpyDefDocstring():
    """A one-line summary that does not use variable names or the
    function name.
    Several sentences providing an extended description. Refer to
    variables using back-ticks, e.g. `var`.
    Parameters
    ----------
    var1 : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    var2 : int
        The type above can either refer to an actual Python type
        (e.g. ``int``), or describe the type of the variable in more
        detail, e.g. ``(N,) ndarray`` or ``array_like``.
    long_var_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.
    Returns
    -------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.
    Other Parameters
    ----------------
    only_seldom_used_keywords : type
        Explanation
    common_parameters_listed_above : type
        Explanation
    Raises
    ------
    BadException
        Because you shouldn't have done that.
    See Also
    --------
    otherfunc : relationship (optional)
    newfunc : Relationship (optional), which could be fairly long, in which
              case the line wraps here.
    thirdfunc, fourthfunc, fifthfunc
    Notes
    -----
    Notes about the implementation algorithm (if needed).
    This can have multiple paragraphs.
    You may include some math:
    .. math:: X(e^{j\omega } ) = x(n)e^{ - j\omega n}
    And even use a greek symbol like :math:`omega` inline.
    References
    ----------
    Cite the relevant literature, e.g. [1]_.  You may also cite these
    references in the notes section above.
    .. [1] O. McNoleg, "The integration of GIS, remote sensing,
       expert systems and adaptive co-kriging for environmental habitat
       modelling of the Highland Haggis using object-oriented, fuzzy-logic
       and neural-network techniques," Computers & Geosciences, vol. 22,
       pp. 585-588, 1996.
    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.
    >>> a = [1, 2, 3]
    >>> print [x + 3 for x in a]
    [4, 5, 6]
    >>> print "a\n\nb"
    a
    b

    """


    """

    Parameters
    ----------

    Returns
    -------

    Other Parameters
    ----------------

    Raises
    ------

    See Also
    --------

    Notes
    -----

    References
    ----------

    Examples
    --------

    """
    return






























