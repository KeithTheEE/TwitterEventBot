


from utils.plotManager import *


def test_plotSummaries():

    #plotSummaries(None, runOn='FRI', runTime='6_PM', minAgeDays=4, quietMode=True)
    pass


def test_makeDistPlot():
    
    featureVector = [14, 1.2, 1.2, 2.4, 1.2, 4.8, 1.2] # tweet count, tweet mean, tweet std,
                                                       # week avg, week std, hist avg, hist std
    tbtwTweets = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    allWeekAvgs = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
    allHistAvgs=[4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4]
    kdePlots = [[1,2,3,4], [1,2,3,4]]
    
    
    timeStamp, media = makeDistPlot('tornado', featureVector, tbtwTweets, allWeekAvgs, allHistAvgs, kdePlots)

