

import numpy as np



import logging



def getTweetsDistrobution(tweets):
    tbtwTweets = []
    for i in range(1, len(tweets)):
        delta = tweets[i-1].created_at - tweets[i].created_at
        delta = delta.total_seconds()
        tbtwTweets.append(delta)
    #print tbtwTweets

    return np.mean(tbtwTweets), np.std(tbtwTweets), tbtwTweets



def classifyEvent(event, featureVector, oldEvent):
    tweetCount = featureVector[0]
    tweetMean = featureVector[1]
    tweetStd = featureVector[2]
    weekAvg = featureVector[3]
    weekStd = featureVector[4]
    histAvg = featureVector[5]
    histStd = featureVector[6]
    #fiveHrAvg
    #fiveHrStd

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


    if CuWu_Wo*WuCu_Co > -2:
        #print "Failed that one test\n\t" + str(isEvent) +'\t'+ str(CuWu_Wo*WuCu_Co)
        isEvent = False
    #else:
    #    print "PASSED IT\n\t" + str(isEvent) +'\t'+ str(CuWu_Wo*WuCu_Co)





    # Should save classifier (Will take care of it after filters are online

    return isEvent
    