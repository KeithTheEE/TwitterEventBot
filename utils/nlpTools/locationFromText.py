


import nltk
from utils.nlpTools.filters import twitterSpecific
print("this works too")


import logging


def getLocation(locBestGuess): 
    """
    Gets the best guess for location the event took place in

    Parameters
    ----------
    locBestGuess: list of strings
        locBestGuess should be made up of parsed substrings 
        from tweets. The parsing is handled by `extractLocations`
        or a similar function

    Returns
    -------
    bestGuess: str
        string will be "in X" where x is the guess or " but I can't 
        find where" according to the presence of any guess in the input
        parameter

    Notes
    -----
    `ExtractLocation` might be moved to its own file, as might `getLocation`
    I'm not yet sure if I want it, but the location extraction would be a 
    useful standalone program.

    """
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
    invalid with twitter data. So... yeah. Fun thing about that is that it still
    generally works 

    It works under the assumption that locations are grammatically similar to 
    state machines when used in english language.

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
        validTerminal = ["NNP"] # CURRENTLY NOT IN USE. REMOVE SOON
        startHere = ["IN"] # Had JJ, JJ requires more grammer rules to be added. This is a bad format for that


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
        try:
            aTweet = str(tweet.text.encode('utf-8'))
        except AttributeError:
            aTweet = str(tweet.full_text.encode('utf-8'))
        words = aTweet.split(" ")
        try:
            guessLocation = []
            guessLocationTemp = extractLocation(twitterSpecific.cleanTweetTextofAts(aTweet))
            for location in guessLocationTemp:
                if event.lower() not in location.lower(): # Stop saying a tornado occured in tornado
                    guessLocation.append(location)
        except UnicodeDecodeError:
            print("Got unicodeDecodeError..")
            guessLocation = []
        if len(guessLocation)>0:
            for loc in guessLocation:
                locBestGuess.append(loc)

    # now we've looked at the tweets and tried to guess a location
    
    #locBestGuess1 = getLocation(locBestGuess)
    return locBestGuess
