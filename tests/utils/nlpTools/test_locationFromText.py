


from utils.nlpTools.locationFromText import *

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
    


def getLocation_Empty_List_Test():
    '''
    Test the return of an empty list with get Location
    '''
    empty_List_Return = getLocation([])
    assert type(empty_List_Return) == str
    assert " but I can't find where" == empty_List_Return


def getLocation_One_Element_List_Test():
    one_Element_List_Return = getLocation(['Magrathea'])
    assert type(one_Element_List_Return) == str
    assert " in Magrathea" == one_Element_List_Return



def getLocation_Multi_Element_List_No_Winner_Test():
    no_Winner_Element_List_Return = getLocation(['Betelgeuse', 'Islington'])
    assert type(no_Winner_Element_List_Return) == str
    assert (" in Betelgeuse" == no_Winner_Element_List_Return) or \
        (" in Islington" == no_Winner_Element_List_Return)


def getLocation_Multi_Element_List_With_Winner_Test():
    with_Winner_Element_List_Return = getLocation(['Ursa Minor Alpha', 'Ursa Minor Beta', 'Krikkit', 'Krikkit'])
    assert type(with_Winner_Element_List_Return) == str
    assert " in Krikkit" == with_Winner_Element_List_Return



def test_getLocation():
    getLocation_Empty_List_Test()
    getLocation_One_Element_List_Test()
    getLocation_Multi_Element_List_No_Winner_Test()
    getLocation_Multi_Element_List_With_Winner_Test()



def test_extractLocation():
    '''
    This is difficult to actually test. As long as the function returns a list
    of strings it's good. If it returns 'Omaha Nebraska' and 'Millard' that's 
    even better
    '''
    sampleText = "There was a tornado in Omaha Nebraska yesterday. I drove north of Millard for safety."
    locationGuesses = extractLocation(sampleText)
    assert type(locationGuesses) == list
    if len(locationGuesses) > 0:
        assert type(locationGuesses[0])  == str

    emptyGuesses = extractLocation("")
    assert type(emptyGuesses) == list
    if len(emptyGuesses) > 0:
        assert type(emptyGuesses[0])  == str



def test_processLocations():
    tweets = get_tweepy_status_populated()
    
    processLocations(tweets, 'Tornado')
    pass