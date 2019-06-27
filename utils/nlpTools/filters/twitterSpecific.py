


import re

import logging

	
def cleanTweetText(text):
    #removes urls
    text = str(text)
    return re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text, flags=re.MULTILINE)

def cleanTweetTextofAts(text):
    #removes urls and @ mentions
    # Though it doesn't really.. It misses 'there' in @here_there 
    text = str(text)
    text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text, flags=re.MULTILINE)
    text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",text).split())
    # Consider this mod if I end up getting lots of unicode errors. Weeee.....
    #printable = set(string.printable)
    #text = filter(lambda x: x in printable, text)
    return text
