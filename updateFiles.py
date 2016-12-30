#!/usr/bin/env python

'''
Keith Murray

'''

import subprocess
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

import crowdSourceEvents
