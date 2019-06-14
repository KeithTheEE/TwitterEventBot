



from utils.botHelperFunctions import *


# Incomplete 


def test_eventList():
    searchEV = eventLists()
    assert type(searchEV) == list
    assert len(searchEV) > 0
    assert type(searchEV[0]) == str



def test_getEventHistoryStats():
    sampleAvgs = [.13,.12,.11]
    timeSpanAvg, timeSpanStd = getEventHistoryStats(sampleAvgs)
    assert 'numpy' in str(type(timeSpanAvg))
    assert timeSpanAvg == .12
    assert 'numpy' in str(type(timeSpanStd))


def test_getEventHistoryTimeLimit():
    sampleTimes, allSampleAvgs = getEventHistoryTimeLimit('tornado', weeks=0, days=1, hours=0, minutes=0)

    assert type(list(sampleTimes)) == list
    assert len(sampleTimes) > 0, "List may be older than 1 day"
    #assert type(sampleTimes[0]) == str # datetime object


    assert type(allSampleAvgs) == list
    assert len(allSampleAvgs) > 0
    assert type(allSampleAvgs[0]) == float