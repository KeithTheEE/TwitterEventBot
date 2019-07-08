

# CHANGELOG: Crowd Source Twitter: an Event Bot Version 0.7.01
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


