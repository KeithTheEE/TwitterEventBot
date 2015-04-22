Crowd Sourcing Twitter Bot
==========================

Author(s): Keith Murray
Contact: kmurrayis@gmail.com

This is the brains of a twitter bot called Keith Event Tracker: https://twitter.com/Keith_Event

The keys, passwords, and anything else security wise is stored in 
  a seperate file accessed via getKMKeys.py, which returns the keys formated
  in an array [CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]

Requirements
============
Using Python 2.7.6
This program reqires the standard libraries of time, math, and datetime,
the extra libraries of numpy, and tweepy.

If the watchdog program is also in use, it will require smtplib, poplib,
email, and imaplib 

Usage
=====
For the twitter bot, you will need to add a file to return your keys, 
as outlined above. After you have the keys, you can run using 
'python crowdSourceEvents.py'

Specifics
=========
the file requires an events database 'listOfTwitterEvents.txt', a
city database 'ExtendedCityDatabase.txt', and if there is no history
for the events, it will create a file labeled [event].txt

Events are deemed true if they pass the isItAnEvent(event, theMean, var)
function, which will return true or false. If true, the program will
try to identify the location using the city database, and will send a
tweet accordingly. 

After this is done for all tweets, the program sleeps for a certain 
amount of time, then runs again.

Watchdog
========
A watchdog program is provided because this code has been up and running
for less than a full 24 hours. There have been errors the program has
thrown that took hours for me to notice, so the watchdog allows me a
crude way of checking that the program is still running. In a seperate
terminal, run 'python tweetWatchdog.py' and once every n minutes, (I 
suggest at least 20) the program will check the last modification time
for one of the log files. If it has not been modified recently, the 
watchdog assumes a failure, and sends a text message and email to the 
user letting them know. 
If that occurs, the watchdog exits. 

