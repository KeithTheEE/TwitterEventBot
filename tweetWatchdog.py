#!/usr/bin/env python

import sendMessage
import getKMKeys
import os.path
import time

'''
Keith Murray
This program will serve as a watchdog to my twitter bot
In the event that an error arises and the tbot is killed
the log files will no longer be updated.
If that's the case, their last modification time will be 
< 5 minutes, (for ease I'll set the WD to 20 or greater)

If there is no internet connection, this program fails too.
But I'm ok with that

Another possible solution would be to put the tbot program in 
a try except condition and put that in a while loop, that way
any time the program failed, it would restart.

However, I would like to see what errors arrise for a while
before I do that, since this is still a new bot

'''


def main():
    emKeys = getKMKeys.GETEMAIL()
    username = emKeys[0] 
    password = emKeys[1]
    fromaddr = emKeys[2]
    toaddrsSMS  = emKeys[3]
    toaddrsMMS  = emKeys[4]
    toaddrEmail = emKeys[5]
    checkDelay = 20
    maxAgeLimit = 20
    msg = "I think the twitter bot died.."
    logFile = "tornado.txt"

    while True:
	time.sleep(checkDelay*60)
	lastUpdate = os.path.getmtime(logFile)
	if ((time.time() - lastUpdate)/60) > maxAgeLimit:
	    try:
		sendMessage.message_Send(toaddrsSMS, msg)
		sendMessage.message_Send_Full_Email([toaddrEmail], "Tweet Error", msg)
	    except:
		print "Could not send Message"
	    print msg
	    print "Now exiting watchdog"
	    print str(time.ctime(time.time()))
	    break
	else : # This is in place to reduce processor speed
	    #    In the event that the time.sleep(checkDelay*60) is removed
	    time.sleep(0.01)

main()
