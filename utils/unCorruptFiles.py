#!/usr/bin/env python



import time
import math
import numpy as np
import datetime
import logging







def cleanIt(infile):
    validBytes = ["0","1","2","3","4","5","6","7","8","9",".","-",":","e","i","n","f","a","\t","\n"]
    fl = open(infile, 'r')
    flString = ""
    with open(infile, 'rb') as fl:
        while 1:
            byte_s = fl.read(1)
            if not byte_s:
                break
            if byte_s in validBytes:
                flString = flString + byte_s
    fl.close()
    fl = open(infile, 'w')
    fl.write(flString)
    fl.close()



def isItAnEvent(event):
    # open event db
    # Date/Time \t theMean \t var
    try:
    	eventHistory = open(str(event) + ".txt", 'r')
    except IOError:
        eventHistory = open(str(event) + ".txt", 'a')
        eventHistory.close()
        eventHistory = open(str(event) + ".txt", 'r')
    theTimes = []
    theAvgs = []
    theVar = []
    lines = []
    errorCount = 0 
    lineCount = 0
    for line in eventHistory:
        if line == "":
            break
        lineCount += 1
        try:
            holdLine = line
            line = line.split('\t')
            times = line[0]
            avgs = float(line[1])
            varss = float(line[2])
            #print times, avgs, varss
            if (str(avgs) == "nan") or (str(varss) == "nan"):
                raise ValueError
            theTimes.append(times)
            theAvgs.append(avgs)
            theVar.append(varss)
            lines.append(holdLine)
        except:
            #print "Average File Error"
            errorCount += 1
    #print "Errors:\t", errorCount
    #print "Lines:\t", lineCount
	
    eventHistory.close()
    compAvg = np.mean(theAvgs)
    compVar = np.var(theAvgs)
    compStd = np.std(theAvgs)
    #print compAvg, compVar, compStd, len(theTimes)

    eventHistory = open(str(event) + ".txt", 'w')
    for i in range(len(lines)):
        eventHistory.write(lines[i])
    eventHistory.close()
	



    ''' 
	
    # compare eventDB to most recent event
    didEventOccur = False
    compAvg = np.mean(theAvgs)
    compVar = np.var(theAvgs)
    compStd = np.std(theAvgs)
    zSc = (theMean-compAvg)/compStd
    zSc2 = (compAvg-theMean)/math.sqrt(var)
    #if (theMean < (compAvg - compStd*1.3)) and (theMean < 2.75) :#and (var < 10):
    #if (math.fabs(zSc) > 2):
    print event, (zSc * zSc2), compAvg, theMean
    if ((zSc * zSc2) <= -2) and (theMean < compAvg) and uniqTweets > 14:#and (theMean < 2.75):
	didEventOccur = True 

    # Save new data to DB
    eventHistory = open(str(event) + ".txt", 'a')
    eventHistory.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '\t' + str(theMean) + '\t' + str(var) +'\t' + str(zSc) + '\t' + str(zSc2) +"\t"+ str(uniqTweets) +'\n')
    eventHistory.close()
    '''


def main():

    keyEventsDB = "listOfTwitterEvents.txt" 

    #   Events
    eventL = open(keyEventsDB, 'r')
    searchEV = []
    for event in eventL:
        searchEV.append(event.strip())
    eventL.close()
    

    for event in range(len(searchEV)):
        logging.debug("Cleaning " + searchEV[event])
        isItAnEvent(searchEV[event])
        cleanIt(str(searchEV[event]) + ".txt")























































