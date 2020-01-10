

# CHANGELOG: Crowd Source Twitter: an Event Bot Version 0.7.02
All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
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


## [0.7.02] 2020-XX-XX
In Progress

### Contributors
Keith Murray

email: kmurrayis@gmail.com |
twitter: [@keithTheEE](https://twitter.com/keithTheEE) |
github: [CrakeNotSnowman](https://github.com/CrakeNotSnowman)

Unless otherwise noted, all changes by @kmurrayis

This project is not currently looking for other contributors

### Big Picture: What happened, what was worked on

Uncorrupt Files is now a part of the standard program, and has conditions where if too much of the file is deemed invalid, it does not delete it and flags it for user input. (This of course is a byproduct of not having that check in place, running the corrupt file correction, having an error in the correction, and then having the program deem the entire file is invalid and deleting it all. Thankfully a backup existed and I didn't have to abandon this project in self-rage.)

`utils/Experimental` has been added and now houses various experimental directions of the bot. This will hopefully make it easier to explore more complex ideas, without putting the core functionality of the bot at risk of being accidentaly deleted.

#### Added
 - main now calls unCorruptFiles at startup
 - Uncorrupt Files now logs changes if they occur
 - Uncorrupt Files no longer allows changes to greater than 0.1% of the lines in the file
 - Uncorrupt Files does not auto rewrite if there are no changes
 - botHelperFunctions how has a load_tweets function 
 - There is now a test for unCorruptFiles
 - In tests, there is now a clean and corrupted history file to use. Incidentally, corrupted_missile would be an awesome punk rock band name/album name.
 - nltkReqs now exists to ensure the needed NLTK modules are downloaded.
 - Under utils/experimental there is now a folder `polysemy_builder` to explore autogeneration of a polysemy filter. 
 - Main startup() now loads a polysemy filter and an associated k nearest neighbors classifier. This is an experiemental function, and if there are no files to load these will be empty dictionaries. 
 - Experimental Topology Network functions have been added under runBot(). This should be wrapped in an 'if experimental_mode == True:' statement soon. 
 - Actually put code in utils/nlpTools/filters/polysemyFilters. If it exists, it was added.
#### Changed
 - Uncorrupt Files encodes each of the defined 'valid bytes' to make the comparison with the characters from the event log file comparable 
 - In Uncorrupt Files: Function isItAnEvent has been changed to validate_Event_History_File
 - In Uncorrupt Files: Function cleanIt has been renamed to clear_corrupted_bytes
 - In Main: import sys has been moved to allow for an addition package path to be appended to sys.path on the pi
 - Main startup() now loads and builds the eventKDEs. This was in runBot, but it was moved because it functionally makes more sense in startup.
 - In Main, prior to removing polysemy tweets, the returned tweets are copied to a `tweets_all` variable, so all originally returned tweets are recorded, making it easier to rerun tests on different filters without accidentally stacking the effects of whatever filter was online 
 - in utils/plotManager every use of np.linspace() now casts the time range to be linearized as an int
 - In utils/bothHelperFunctions `load_recent_tweets` is now called `load_tweets_from_disk` to help reduce ambiguity
 - in Main, lsalib and utils/experimental/topology imports are made. This should shortly be wrapped in an if statement to prevent the pi from trying to enact these modes. 
 - In Main, `startup()` now returns `api, searchEV, eventKDEs, polyF, knn_models`, and `runBot` now takes those as inputs. This makes testing easier and helps organize functions which need to be done on startup. 
 - The main runBot() loop is now in a try/except to allow for keyboard interrupts so the bot can save an exit its current state. 

#### Deprecated
#### Removed
#### Fixed
#### Security
 - NLTK Req now set to >=3.4.5 to fix security issue `CVE-2019-14751`, a vulenerability with the NLTK downloader. 
#### Testing

### More focused Changes
#### Main
#### Util Libraries
#### Tests 


## [0.7.01] 2019-07-07
Completed

### Contributors
Keith Murray

email: kmurrayis@gmail.com |
twitter: [@keithTheEE](https://twitter.com/keithTheEE) |
github: [CrakeNotSnowman](https://github.com/CrakeNotSnowman)

Unless otherwise noted, all changes by @kmurrayis

This project is not currently looking for other contributors

### Big Picture: What happened, what was worked on
Files were deleted, reorganized, and altered. 

Most everything that changed will not be recorded in this specific version, as so much changed. If it exists, it was either changed or moved or created this round. I don't know that there was a single region that was untouched. The next changelog version will have the changes listed more explicitly. 

#### Added
 - locationFromText.extractLocation has a bodge at the end to strip any guessed locations that have a hex string in it, xXX
#### Changed
 - matplotlib uses in plotManager have been updated for deprecation issues, uses of xmin, ymin, xmax, ymax have been changed to left, bottom, right, top respectively 
 - plotManager now uses scipy.stats to generate a pdf rather than mlab.normpdf
 - plotManager.makeDistPlot now has a check for tweet standard deviation of 0.0: in the event that every tweet returned by twitter is from the same second timestamp, std is redefined as 0.05
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Testing

### More focused Changes
#### Main
#### Util Libraries
#### Tests 


## [0.7.00] 2019-06-28
Complete

### Contributors
Keith Murray

email: kmurrayis@gmail.com |
twitter: [@keithTheEE](https://twitter.com/keithTheEE) |
github: [CrakeNotSnowman](https://github.com/CrakeNotSnowman)

Unless otherwise noted, all changes by @kmurrayis

This project is not currently looking for other contributors

### Big Picture: What happened, what was worked on
Files were deleted, reorganized, and altered. 

Most everything that changed will not be recorded in this specific version, as so much changed. If it exists, it was either changed or moved or created this round. I don't know that there was a single region that was untouched. The next changelog version will have the changes listed more explicitly. 

#### Added
#### Changed
 - crowdSourceEvents.py has been broken up and the program now starts from main.py 
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Testing

### More focused Changes
#### Main
#### Util Libraries
#### Tests 


