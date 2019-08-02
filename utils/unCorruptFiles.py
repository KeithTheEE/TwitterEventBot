#!/usr/bin/env python



import time
import math
import numpy as np
import datetime
import logging







def clear_corrupted_bytes(infile, allowedToEdit=False):
    validBytes = ["0","1","2","3","4","5","6","7","8","9",".","-",":","e","i","n","f","a","\t","\n", "x", "y", "z"]
    validBytes = [bytes(x.encode()) for x in validBytes]
    
    
    flString = ""
    flBytes = bytearray()
    invalidBytesCount = 0
    validBytesCount = 0
    totalBytesCount = 0
    #invalids = [] Used to see what characters it's saying are invalid
    with open(infile, 'rb') as fl:
        while 1:
            byte_s = fl.read(1)
            if not byte_s:
                break
            if byte_s in validBytes:
                #flString = flString + byte_s
                flBytes += byte_s
                validBytesCount += 1
            else:
                invalidBytesCount += 1
                #if byte_s not in invalids:
                #    invalids.append(byte_s)
            totalBytesCount += 1

    #print(invalids)
    # Ensure file isn't altering too much automatically
    #  To make sure I'm not deleting too much with a poorly defined string
    edited = False
    if invalidBytesCount/float(totalBytesCount) < 0.001:
        if allowedToEdit:
            if invalidBytesCount > 0:
                with open(infile, 'wb') as fl:
                    fl.write(flBytes)
            edited = True


        logging.info("Stripped out "+str(invalidBytesCount)+" invalid bytes from file of " +str(totalBytesCount))
    else:
        logging.warning("Too much of the file is flagged as invalid. Automated correction is turned off\n\t"
            +str(invalidBytesCount)+" invalid bytes from file of " +str(totalBytesCount))

    return invalidBytesCount, validBytesCount, totalBytesCount, edited


def validate_Event_History_File(event, allowedToEdit=False):
    # open event db
    # Date/Time \t theMean \t var
    folderPrefix = "misc/hist_data/"
    try:
    	eventHistory = open(folderPrefix+str(event) + ".txt", 'r')
    except IOError:
        eventHistory = open(folderPrefix+str(event) + ".txt", 'a')
        eventHistory.close()
        eventHistory = open(folderPrefix+str(event) + ".txt", 'r')
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


    if errorCount/float(lineCount) < 0.001:
        if allowedToEdit:
            if errorCount > 0:
                #eventHistory = open(folderPrefix+str(event) + ".txt", 'w')
                with open(folderPrefix+str(event) + ".txt", 'w') as eventHistory:
                    for i in range(len(lines)):
                        eventHistory.write(lines[i])
                logging.info("Cleaned "+str(errorCount)+" Errors over "+str(lineCount)+" lines")
    else:
        logging.warning("Too much of the file is flagged as invalid. Automated correction is turned off\n\t"
            +str(errorCount)+" invalid lines from file of " +str(lineCount))
	



def main():

    keyEventsDB = "misc/listOfTwitterEvents.txt" 

    #   Events
    eventL = open(keyEventsDB, 'r')
    searchEV = []
    for event in eventL:
        searchEV.append(event.strip())
    eventL.close()
    

    for event in range(len(searchEV)):
        logging.debug("Cleaning " + searchEV[event])
        validate_Event_History_File(searchEV[event])
        invalidBytesCount, validBytesCount, totalBytesCount, edited = clear_corrupted_bytes("misc/hist_data/"+str(searchEV[event]) + ".txt")
        break























































