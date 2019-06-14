


from utils.nlpTools.filters.twitterSpecific import *

# Test is up to date June 4 2019


def test_cleanTweetText():
    text = 'Go to https://t.co/123456798a to search for something!'
    cleanText = cleanTweetText(text)
    assert type(cleanText) == str
    assert 't.co' not in cleanText 

def test_cleanTweetTextOfAts():
    text = 'look at the @keith_event bots latest tweet.'
    cleanText = cleanTweetTextofAts(text)
    assert type(cleanText) == str
    assert 'keith_event' not in cleanText