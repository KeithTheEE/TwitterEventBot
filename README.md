# Crowd Source Twitter: an Event Bot
---

Author(s): Keith Murray

Contact: kmurrayis@gmail.com

This is the brains of a twitter bot called [Event Tracker](https://twitter.com/Keith_Event)

Basic Opperation:
---

Every few minutes the bot runs and searches twitter for recent tweets with a given keyword, (the 'event') in it. The tweets timestamps are sorted, and the time between each neighboring tweet is recorded. It then takes the average amount of time in seconds between each of the returned tweets as well as the standard deviation and uses that value to determine if an event has occured compared to historical averages. At the end of each run, it archives the averge time between tweets.

To compare against the historical averages, the program pulls the archived sample values and gets the historic average and standard deviation over all recorded samples. 

Reading the Plots
---

![sample_plot](https://pbs.twimg.com/media/D9TjRZoXkAAxI6n.png)



The plot is divided up into two halves, a historic histogram, and a modeled distrobution plot. 

### Focusing on the top plot:
 
The blue values in the plot show a histogram over all recorded average 'time between tweets'. In that plot, there is a verticle red line which represents the current sample average, that way you can tell how it stacks up against what the bot usually measures. 



### Focusing on the bottom plot:

Stripping away the noisy histogram data, the second plot provides modeled distrobutions.

The **solid blue curve** takes all archived historical averages and generates a guassian distrobution using the average of the historical averages and the standard deviation of the historical averages. 

The **solid green curve** shows a gaussian distrobution for the current collection of tweets, organized by the time between those current tweets. 

The **verticle red line** extends from the top plot showing the current sample average time between tweets. 

From the solid green and blue curves, it's apperent that gaussian distrobuitons are not the necessarily best way to model the current and historic distrobutions of the time between tweets. To try to get a better visual model, Kernel Density Estimation (KDE) is used. 

Each KDE distrobution uses the Epanechnikov to distribute a curve around each sample, then the curves are added together and normalized for every sample 

The **solid red curve** is made from the past year of historic records and modeled using KDE.

The **dotted green curve** is made from the current twitter sample, where the tweets timestamps are sorted, and the time between each neighboring tweet is recorded. This is distinct from the historic values, as the average of this set of samples is recorded and the set of averages make up the historic distrobutions. 

The **little black crosses** at the bottom are the individual time between tweet samples. The dotted greed curve should fit over these crosses, offering more insight into how time between tweet values are distrobuted. 

The **dotted pink line** is made from the recorded averages of the past week of samples. This shows how different the current distrobution is from what has been recently happening on twitter. 


### Weekly Summary Plot
![sample_weekly_summary](https://pbs.twimg.com/media/D9DuJIIWwAoVAwu.png)

This plot shows how many tweets per second about an event occurred over the past week.
Each time the bot ran in the past week, it recorded the average value of the time between tweets in that runtime sample. This plot displays the inverse value, tweets per second so that the higher the value in this plot, the more tweets were made. 