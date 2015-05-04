#!/usr/bin/env python

'''
Keith Murray

This is to plot and visualize the data recorded in the [event].txt files
'''
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import matplotlib.dates as mdates
import math

def plotEvent(eventF):
    eventHistory = open(str(eventF) + ".txt", 'r')
    theTimes = []
    theAvgs = []
    theVar = []
    for line in eventHistory:
	if line == "":
	    break
	line = line.split('\t')
	theTimes.append(line[0])
	theAvgs.append(1/float(line[1]))
	theVar.append(float(line[2]))

    eventHistory.close()
    dates = theTimes
    x = np.array([dt.datetime.strptime(d,'%Y-%m-%d %H:%M') for d in dates])
    


    # look to see
    #  1: how the current average compares to the old avg of the std of old avg
    #  2: how the old average compares to the current avg and std

    histAvg = [theAvgs[0]]
    zSc1 = [0]
    zSc2 = [0]
    for i in range(1,len(theAvgs)):
	curAvg = theAvgs[i]
	curVar = theVar[i]
	curStd = math.sqrt(curVar)
	oldAvg = np.mean(histAvg)
	oldStd = np.std(histAvg)
	histAvg.append(curAvg)
	zSc1.append((curAvg - oldAvg)/oldStd)
	zSc2.append((oldAvg - curAvg)/curStd)


    # Draw "EVENT OCCURRED" estimation
    xVlinesZs = []
    for i in range(len(zSc1)):
	#print zSc1[i]*zSc2[i]
	if (zSc1[i]*zSc2[i]) <= -2:
	    xVlinesZs.append(x[i])

    print len(xVlinesZs)
    '''
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    #plt.gca().xaxis.set_major_locator(mdates.MinuteLocator())
    plt.plot(x,theAvgs)
    plt.gcf().autofmt_xdate()
    plt.show()
    plt.close()
    '''
    plt.figure(1)
    ax1 = plt.subplot(211)
    plt.title(eventF[0].upper() + eventF[1:].lower())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    #plt.gca().xaxis.set_major_locator(mdates.MinuteLocator())
    plt.gcf().autofmt_xdate()
    ax1.plot(x,theAvgs)
    plt.ylabel("Average Tweets Per Second")
    for xc in xVlinesZs:
	plt.axvline(x=xc, color='r')

    ax2 = plt.subplot(212, sharex=ax1)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    #plt.gca().xaxis.set_major_locator(mdates.MinuteLocator())
    ax2.plot(x,theVar)
    plt.gcf().autofmt_xdate()
    plt.ylabel("Variance of \nthe Average")
    for xc in xVlinesZs:
	plt.axvline(x=xc, color='r')

    plt.show()
    plt.close()


    plt.figure(2)
    ax1 = plt.subplot(211)
    plt.title(eventF[0].upper() + eventF[1:].lower())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    #plt.gca().xaxis.set_major_locator(mdates.MinuteLocator())
    plt.gcf().autofmt_xdate()
    ax1.plot(x,zSc1)
    for xc in xVlinesZs:
	plt.axvline(x=xc, color='r')
    plt.ylabel("Current set of tweets wrt \nthe past averages and std")
    ax2 = plt.subplot(212, sharex=ax1)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    #plt.gca().xaxis.set_major_locator(mdates.MinuteLocator())
    ax2.plot(x,zSc2)
    plt.gcf().autofmt_xdate()
    for xc in xVlinesZs:
	plt.axvline(x=xc, color='r')
    plt.ylabel("Past Average compared to the average\n current set and the std of that set")

    plt.show()
    plt.close()


    
    return
def main(eventF):
    eventList = open("listOfTwitterEvents.txt", 'r')
    eL = []
    for line in eventList:
	eL.append(str(line))
    print "*********************************"
    while True:
	for i in range(len(eL)):
	    print "*\t ",eL[i].strip(), "\t\t*"
	eventF = raw_input("* Please enter the event name:  *\n\t")
	for i in range(len(eL)):
	    tempE = eL[i].strip()
	    if eventF.lower() == tempE.lower():
		eventF = tempE
	try:
	    plotEvent(eventF)
	except IOError:
	    pass

main('earthquake')



'''
Assumptions
The number of earbuds in the US is a function of owning ipods and cellphones 
knot complexity directly correlates with how much time is wasted
knot complexity is a function of 'time since earbud use', and earbud length. However, 90% of earbuds are between 1.3 and 1.43 yd, with the median at 1.3 yd, so it's safe to assume the length is a constant 1.3 yd, and therefore not a varible. 




Relationships:

Time Wasted = (Number of earbuds, proportion of frequent use, knot complexity)

Number of earbuds in US:
79.4 mill people with earbuds: http://www.statista.com/topics/1405/ipod/




'''
