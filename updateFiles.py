#!/usr/bin/env python

'''
Keith Murray

'''

import subprocess
import traceback
import socket
import sys
import os
import time



def is_connected():
    REMOTE_SERVER = "www.google.com"
    try:
	print "Testing Internet Connection"
	# see if we can resolve the host name -- tells us if there is
	# a DNS listening
	host = socket.gethostbyname(REMOTE_SERVER)
	# connect to the host -- tells us if the host is actually
	# reachable
	s = socket.create_connection((host, 80), 2)
	return True
    except:
	pass
    return False


online = is_connected()

while not online:
    online = is_connected()
    time.sleep(30)


process = subprocess.Popen(["git", "pull", "origin", "master"], stdout=subprocess.PIPE)
output = process.communicate()[0]
print output

emailCount = 0
emailLimit = 5

while True:
    try:
        import crowdSourceEvents
    except KeyboardInterrupt:
        break
    except:
        ln = traceback.format_exc()
        flname = 'errorReport.log'
        fl = open(flname, 'w')
        fl.write(ln)
        fl.close()
        import kmmessage        
        recip = 'kmurrayis@gmail.com'
        subject = 'Error on the Twitter Bot'
        text = ln
        if emailCount < emailLimit:
            try:
                kmmessage.message_Send_Full_Email([recip], subject, text, files=[flname])
            except:
                trace = traceback.format_exc()
                flname = 'moreErrors.log'
                fl = open(flname, 'a')
                fl.write(ln + '\n' + trace + '\n')
                fl.close()
            emailCount += 1
        if emailCount == emailLimit:
            text = text + '\n' + "EMAIL LIMIT REACHED FOR THIS BOOT"
            try:
                kmmessage.message_Send_Full_Email([recip], subject, text, files=[flname])
            except:
                trace = traceback.format_exc()
                flname = 'moreErrors.log'
                fl = open(flname, 'a')
                fl.write(ln + '\n' + trace + '\n')
                fl.close()
            emailCount += 1
            
        

        
