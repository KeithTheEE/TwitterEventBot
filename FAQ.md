
# FREQUENTLY ASKED QUESTIONS


## What is this
This is a bot that watches twitter for keywords. When there's more tweets about a topic than usual, this bot will assume that keyword event has occured, and tweet about it. 

It doesn't have the ability to verify, and isn't an authority on the subject. Instead, it crowd sources the news using twitter to get an early jump on the information. 

## Is it accurate
No. 

It tries to be accurate, but is purposefully limited to the information returned by twitter when it searches for the latest tweets with a keyword. This constraint prevents it from being able to verify and confirm any of it's guesses: hence the use of "I think event X has occured"

But it is this constraint that makes the bot a fun challenge to execute. While it isn't strictly accurate, its performance is fairly solid and can be treated as a good 'pulse' of events. If it starts tweeting about something strongly enough, it's worth delving into for more information. 

## What about the location it tweets about, is that accurate
Also no. 

The locations are extracted using a really basic part of speech parser and after being built it became clear it was really just parsing capitalized words. It leverages the information from multiple tweets to get a signal to resolve from the noise. So in the same way it tries to be accurate about events, it tries to be accurate about the locations. But the constraint limits its abilities. 

## How does it get this information
Every few minutes it searches twitter for the most recent tweets with a given keyword. All of its information comes from the text of those tweets and the distrobution of time between tweets in that sample. It saves this distrobution and can draw on its historic records to compare the current sample against the historic samples. 


## What do the plots mean
The plots are a messy way for me to tell how 'real' an event is. It shows the current sample compared to the historic sample in the background plot, and the 

## Can you tell me more about a specific event the bot tweeted about
That's a future goal, but sifting through the spam and uninformative tweets is a challenge. 

## What is the story behind it/Why build this
In April 2015 I was living in an apartment on the second floor and the tornado sirens went off. The storm was behind the building on a wall we didn't have windows for, so we couldn't see if it was approaching us or moving parallel. In addition to the radio and news, my roommates and I pulled up twitter and searched for the latest tweets with 'tornado' in it.

While scrolling through the tweets, I noticed I was only paying attention to two varibles: the time between each of the tweets (to see how big of a deal the tornado was) and if anyone also mentioned where the tornado was (to see if it was near us). 

Later on in an effort to procrastinate from studying for finals I decided to build a bot to automate this process. Since then it's been a platform that I can use to test out and explore algorithms I don't fully understand before implementing them elsewhere. 

## Where is the bot in development

The bot is currently waiting for some large updates. It performance is satisfactory, but there's so much more I want to add to it. Still, at the end of the day the bot is a toy and hobby project, so it has been waiting for the updates for a while, and probably will continue to do so. 


---
#### Crowd Source Twitter: an Event Bot Version  0.7.00