Crowd Sourcing Twitter Bot
==========================

Author(s): Keith Murray
Wed Apr 22 14:59:45 2015

This bot is created to search twitter for key events, and 
decide when an event has occured.

This decision is based on the average time between tweets 
about an event. It assumes that if an event, say an earthquake,
is currently taking place many people will be tweeting about 
it and those tweets will take place in a small period of time.
It also keeps a log of the average time between tweets, and 
compares the current time between tweets. This comparison lets
the bot see on average how long it takes to tweet, and when 
there are many tweets in an unusually short amount of time, the
bot decides that an event must have occured.

The 'unusually short amount of time' is a bit of guesswork, and
will need some time to perfect. During the time it was being written,
a tornado was occuring in pennsylviania near Lehigh County, and I was
able to get some sampeling of the time between tweets, and based 
the 'short amount of time' on that event. 


Files in Project
================
Files TornadoIsOccuring.txt, tornadoVEarthquake.txt and
tornadoVother.txt all show comparisons between tweets about a tornado
and the other events.
Specifically for TornadoIsOccuring.txt, the file shows tweets and 
time of tweets for 50 of each event. Looking at the tornado and 
comparing it to earthquake, there is a clear difference in which 
event is occuring based on the amount of time that passes between 
each tweet. 

FailedCitiest.txt is a list of cities that the program 
'expandCityDB.py' was unable to find more info on. 
listOfCities100000PlusPeople.txt is a list of cities with a population
size great that 100,000 according to wikipedia. Unfortunately, this is
very incomplete and needed to be expanded on, which prompted the 
creation of 'expandCityDB.py'

testTweetAsText.txt is the file I forced the bot to 'tweet' too before
I actually let it use twitter. There are a few interesting things to 
note here: 

  Boston Bombing: (April 20th was the marathon)
  The Boston marathon took place a day earlier, so people were tweeting
  about that event, and about the boston marathon bombing. This caused
  the program to think there was a bombing in boston, and it would have
  tweeted that. I still have not figured out what to do about it, and
  am unsure if I want to let that event be apart of the bot.

  Asteroid and Meteoroid:
  This wasn't quite wrong. On Tuesday morning April 21, an asteroid 
  passed the earth, narrowly missing us. This event was picked up by
  the bot, and it would have tweeted it. However, it thought the event
  took place in Hiroshima. This is where human language gets funny. 
  When talking (or tweeting) about the size and danger of this 
  asteroid, it was compared to the atomic bomb dropped on Hiroshima. 
  Thanks to the fondness of that comparison, Hiroshima is the only 
  location the bot could guess, and it therefore thought that an 
  asteroid hit Hiroshima.

  Rain
  Rain is the most common of events (thankfully) and I might nix it 
  from the event list. However, for some reason when it tweets about 
  rain in Boston, the real weather has been beautiful. Something is
  skewing the results, but because I don't save a list of tweets that
  the bot made the decision on, I don't have a way to go back and 
  verify. I will probably add that function soon though. 


