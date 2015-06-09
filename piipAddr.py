#!/usr/bin/env python

'''


'''



import getKMKeys # Format of CK, CS, AK, AS
import sendMessage
import socket
import fcntl
import struct
import time


def is_connected():
    REMOTE_SERVER = "www.google.com"
    #host = socket.gethostbyname(REMOTE_SERVER)
    #s = socket.create_connection((host, 80), 2)
    try:
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

def manageIPaddr():
    oldIP = "000.000.0.000"
    emKeys = getKMKeys.GETEMAIL()
    username = emKeys[0] 
    password = emKeys[1]
    fromaddr = emKeys[2]
    toaddrsSMS  = emKeys[3]
    toaddrsMMS  = emKeys[4]
    toaddrEmail = emKeys[5]

    try:
    	ipLog = open("lastIP.log", 'r')
    except IOError:
	ipLog = open("lastIP.log", 'w')
	ipLog.write(oldIP)
	ipLog.close()
	ipLog = open("lastIP.log", 'r')
    oldIP = ipLog.readline()
    ipLog.close()

    currIP = ([(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
    if str(currIP)!= oldIP:
	ipLog = open("lastIP.log", 'w')
	ipLog.write(str(currIP))
	ipLog.close()
	msg = "The Pi's IP address is:\n" + str(currIP)
	try:
	    sendMessage.message_Send(toaddrsSMS, msg)
	    sendMessage.message_Send_Full_Email([toaddrEmail], "Raspberry Pi IP", msg)
	except:
	    print "Could not send Message"
	print msg
	print "Now exiting watchdog"
	print str(time.ctime(time.time()))





def main():
    if is_connected():
	manageIPaddr()
    return

main()



































