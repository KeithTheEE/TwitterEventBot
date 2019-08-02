

# ROADMAP: Crowd Source Twitter: an Event Bot Version 0.7.02
Future expansions are considered in this file. 
Their presence is not a promise that they'll exist, but rather this file serves as an
early outline of features this project hopes to add, as well as changes in directions


The format is adapted from [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
It wont adhere perfectly, but it's a start. 


Dates follow YYYY-MM-DD format

 > "Once men turned their thinking over to machines in the hope      
 >  that this would set them free. But that only permitted other     
 >  men with machines to enslave them."                              
 > " 'Thou shalt not make a machine in the likeness of a man's       
 >  mind,' " Paul quoted.                                            
 > "Right out of the Butlerian Jihad and the Orange Catholic         
 >  Bible," she said. "But what the O.C. Bible should've said is:    
 >  'Thou shalt not make a machine to counterfeit a human mind.'..." 
 >                                                                   
   --from Dune, by Frank Herbert     





 
## [0.7.02] 2019-XX-XX
In Progress

### Contributors
Keith Murray

email: kmurrayis@gmail.com |
twitter: [@keithTheEE](https://twitter.com/keithTheEE) |
github: [CrakeNotSnowman](https://github.com/CrakeNotSnowman)

Unless otherwise noted, all changes by @kmurrayis

### Short Term Roadmap

The targets of this update are:
  - Delete old/broken/unused code (Currently deprectating it)
  - Add and Update Documentation 
  - [X] Evaluate the need for the 'uncorrupt files' (Probably good to have as a longevity check)
  - structure bot to run off of a flashdrive rather than sd card (probably pi hardware specific) for longevity of the os/sd card
  

#### Add
 - Logging. Logging everywhere.
 - Tests. Not as many are as needed, but more than none
 - Populate the polysemy filter. Given the issues are thunder basketball and blizzard ent, focus on those and have it be empty for other topics
#### Change
 - Timestamps should change from time.time() to datetime objects, and explicitly call either cdt or utc
 - [X] unCorruptFiles needs an overhaul too, it's not consistent with itself
#### Deprecate
 - Old/Broken/Unused code: Flag and list
 - crowdsourceEvents 
#### Remove
 - nothing specific yet, this will change shortly
#### Fix
 - [X] Fix unicode/hex error in predicted locations. This is a byproduct of the 2->3 upgrade + poor string handling. Location is tweeting hex codes due to unicode characters slipping in. The real cause is poor handeling of unicode strings on my part, but a quick bodge could be to just search for all strings matching a hex pattern using re and invalidate that as a location. 
 - [X] unCorruptFiles: due to python 3 vs 2 string typing, cleanIt() deletes the entire history file. Fix the byte verificcation and add a condition that the function never adjusts a file if >1% of the file needs adjustment. This should prevent a bad comparison from deleting everything
#### Security
#### Consider
 - Adding a new visual comparing recent tweets to recent historical tweets (past week/day)
 - Add a logging flag to monitor memory usage
 - Write up an install explaination/requirements [tweepy==3.5.0, numpy==1.14.3, matplotlib==3.0.3, nltk==3.3, scipy==1.1.0, scikit_learn==0.21.2]
#### Testing
 - Build "simulate twitter" from recorded events. Adjust to recent events. Sepperate out all api calls and file saves to prevent rerecording already seen data. 
 - Add a quietMode flag to all api calls, making testing easier




---

### General to Long Term Expansion

 - Drop the tweet rate significantly. Either with HMM or Kalman filter or some other classifier. Either way, drop the tweet rate. However as a constraint don't miss multiple tornados because of this. 


### Libraries:
### OTHER
#### Reasoning Behind Tweet
 - Building 'explaination forms' which can be filled in adlib style to explain an event. 
 - Flag toxic/energized/inflamatory language/tweets to be ignored. Probably need some form of NER to sepperate objects from emotions, and sentiment analysis for the emotions.  
 - Plot semantic/topology of recent tweets. Expect this to fail. 
### Tests 
 - Build fake api to load sample tweets from demo folder 
 - Cover more functions 
 - Structure tests so it's easy to slap in a new function and run a simulated day of twitter on it




## [0.7.01] 2019-07-07
Completed

### Contributors
Keith Murray

email: kmurrayis@gmail.com |
twitter: [@keithTheEE](https://twitter.com/keithTheEE) |
github: [CrakeNotSnowman](https://github.com/CrakeNotSnowman)

Unless otherwise noted, all changes by @kmurrayis

### Short Term Roadmap

The Twitter bot is getting a long awaited overhaul. The bot should behave the same but the code underneath it should be better. 

The targets of this update are:
  - Delete old/broken/unused code (Currently deprectating it)
  - Add and Update Documentation 
  - Evaluate the need for the 'uncorrupt files' (Probably good to have as a longevity check)
  - structure bot to run off of a flashdrive rather than sd card (probably pi hardware specific) for longevity of the os/sd card
  

#### Add
 - Logging. Logging everywhere.
 - Tests. Not as many are as needed, but more than none
 - Populate the polysemy filter. Given the issues are thunder basketball and blizzard ent, focus on those and have it be empty for other topics
#### Change
 - Timestamps should change from time.time() to datetime objects, and explicitly call either cdt or utc
#### Deprecate
 - Old/Broken/Unused code: Flag and list
 - crowdsourceEvents 
#### Remove
 - nothing specific yet, this will change shortly
#### Fix
 - Fix unicode/hex error in predicted locations. This is a byproduct of the 2->3 upgrade + poor string handling. Location is tweeting hex codes due to unicode characters slipping in. The real cause is poor handeling of unicode strings on my part, but a quick bodge could be to just search for all strings matching a hex pattern using re and invalidate that as a location. 
#### Security
#### Consider
 - Adding a new visual comparing recent tweets to recent historical tweets (past week/day)
 - Add a logging flag to monitor memory usage
 - Write up an install explaination/requirements [tweepy==3.5.0, numpy==1.14.3, matplotlib==3.0.3, nltk==3.3, scipy==1.1.0, scikit_learn==0.21.2]
#### Testing
 - Build "simulate twitter" from recorded events. Adjust to recent events. Sepperate out all api calls and file saves to prevent rerecording already seen data. 
 - Add a quietMode flag to all api calls, making testing easier




---

### General to Long Term Expansion

 - Drop the tweet rate significantly. Either with HMM or Kalman filter or some other classifier. Either way, drop the tweet rate. However as a constraint don't miss multiple tornados because of this. 


### Libraries:
### OTHER
#### Reasoning Behind Tweet
 - Building 'explaination forms' which can be filled in adlib style to explain an event. 
 - Flag toxic/energized/inflamatory language/tweets to be ignored. Probably need some form of NER to sepperate objects from emotions, and sentiment analysis for the emotions.  
 - Plot semantic/topology of recent tweets. Expect this to fail. 
### Tests 
 - Build fake api to load sample tweets from demo folder 
 - Cover more functions 
 - Structure tests so it's easy to slap in a new function and run a simulated day of twitter on it



## [0.7.00] 2019-06-28
Completed
### Contributors
Keith Murray

email: kmurrayis@gmail.com |
twitter: [@keithTheEE](https://twitter.com/keithTheEE) |
github: [CrakeNotSnowman](https://github.com/CrakeNotSnowman)

Unless otherwise noted, all changes by @kmurrayis

### Short Term Roadmap
This is deemed version 0.7.00 because there are six previous periods of high commits in my git history. It's a bit handwavy, but it'll do for a line in the sand version wise. 

The Twitter bot is getting a long awaited overhaul. The bot should behave the same but the code underneath it should be better. 
The targets of this update are:
  - [X] Upgrade to python 3
  - [X] Reorganize code into a reasonable fashion (start from a main, break into modules)
  - Delete old/broken/unused code (Currently deprectating it)
  - [X] Add logging via the logging module
  - Add and Update Documentation 
  - Evaluate the need for the 'uncorrupt files' (Probably good to have as a longevity check)
  - structure bot to run off of a flashdrive rather than sd card (probably pi hardware specific) for longevity of the os/sd card
  
This will largerly be a behind the scenes update, with little visible change on the bot's twitter facing side of things.

#### Add
 - Logging. Logging everywhere.
 - Tests. Not as many are as needed, but more than none
#### Change
 - [X] Parse through crowdSourceEvents and add code to a main, and to util modules
 - [X] Redirect most generated files to their new subdirectory structure
 - In utils/plotManager ~line 325/326 Deprecation Warning: xmin,xmax,ymin,ymax will be dropped and changed to left, (right?), bottom, top respectively 
 - Timestamps should change from time.time() to datetime objects
#### Deprecate
 - Old/Broken/Unused code: Flag and list
#### Remove
 - nothing specific yet, this will change shortly
#### Fix
 - Fix unicode/hex error in predicted locations. This is a byproduct of the 2->3 upgrade + poor string handling. Location is tweeting hex codes due to unicode characters slipping in. The real cause is poor handeling of unicode strings on my part, but a quick bodge could be to just search for all strings matching a hex pattern using re and invalidate that as a location. 
#### Security
#### Consider
 - Adding a new visual comparing recent tweets to recent historical tweets (past week/day)
 - Add a logging flag to monitor memory usage
 - Write up an install explaination/requirements 
#### Testing
 - Build "simulate twitter" from recorded events. Adjust to recent events. Sepperate out all api calls and file saves to prevent rerecording already seen data. 




---

### General to Long Term Expansion

 - Drop the tweet rate significantly. Either with HMM or Kalman filter or some other classifier. Either way, drop the tweet rate. However as a constraint don't miss multiple tornados because of this. 

### Libraries:
### OTHER
#### Reasoning Behind Tweet
 - Building 'explaination forms' which can be filled in adlib style to explain an event. 
 - Flag toxic/energized/inflamatory language/tweets to be ignored. Probably need some form of NER to sepperate objects from emotions, and sentiment analysis for the emotions.  
### Tests 
 - Build fake api to load sample tweets from demo folder 
 - Cover more functions 
 - Structure tests so it's easy to slap in a new function and run a simulated day of twitter on it

