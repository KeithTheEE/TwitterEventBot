# About TweetNetworkExploration
And associated files, functions, values, and notes on the project

# Write up of current progress
Right so lets quickly summarize the program in its current form, then we can evaluate the results with various settings

## Program Structure
### Inputs, Initials, and Background
#### Tweets

The program requires input sample tweets, as this is a focused version of top shelf (built before topshelf as a tool to discover what topshelf needs vs what should be application specific) where topshelf is a homebrewed topology exploration tool. 

The sample tweets are pulled from a recorded instance of the twitter event bot, where every tweet that passed the naive spam filter was saved. These tweets span around a solid week, then there's a break in time of around another week, then resumes for another period [NOTE: get exact dates and time spans]
    

#### Text Models and Profiling

    
The modeling process itself works in three phases, 
    
 * first a reference text is used to populate a dictionary, and that dictionary is treated as the profile/vector model, and word counts are the specific elements of the vector, with n total elements. A constraint on this dictionary is that for each element of length greater than 1 there must also be every prefix of that element elsewhere in the dictionary.
 * Second the actual model is built on a corpus. An empty  n by n matrix of zeros is generated. Then for each text, a dictionary based profile is built using the model profile (in this process the output profile is normalized by the sequence length), and for each profile, the dot product of its transformed self and itself is taken (`np.dot(p.T, p)`) and is added to the matrix. This process is repeated for each text in the corpus. Once the raw matrix has been built, Inverse Document Frequency weighting is applied on each row such that the idf weight for a given element in the dictionary is equal to the log of the number of words in the dictionary over the number of other words that occur in a text sample with the current word being weighted (`np.log(n/words_also_in_text)`). It should be noted that `words_also_in_text` can be simplified as the number of nonzero elements in that row. Once this value has been calculated it is applied to the row as a whole as a scalar value. This is repeated for each row in the matrix, and with that the full model over the corpus has been built and can be saved. 
 * The full model is large and unwiedly so for the final phase the model is reduced using Non negative matrix factorization with `n_components=k`, a user defined value (which for this program has a default of 12) and then a projection from the embedded space can be built. NMF returns a matrix P from fit_transform on an input matrix (in the sklearn documentation this is W, however for consistency with previous programs it is treated as P here). This matrix is n by k in size, and has some measured error when combined with its sibling matrix, Q, and compared to its source matrix. From P a projection matrix B can be built. `B = np.dot(np.linalg.inv(np.dot(x.T, x)),x.T)` With B, the modeling process is complete and has been reduced to a much more managable memory footprint, at the cost of some measured error. 
 
To profile a sequence `s` the model maps it to a dictionary based profile `x`, multiplies its elements by their associated IDF scores, and transposes it: `p = np.multiply(IDF, x).transpose()`. Finally the dot product of the projection matrix and the profiled sequence is taken and returned as the profile: `np.dot(B, p)`

  Currently there is a high likelyhood that this uses some flawed math but based on a umap projection it seems that even with the possible flaws it generates fairly useful profiles that allows similar text to be grouped together.
     

At the moment there are three low (or reduced dimensionality) word relationship models used to profile tweets and map them to a vector space: One using blocked text from gutenberg, and one using the youngest 1% of the tweets described above. 
     
  Gutenberg Blocked text is made up of a compilation of about 99 of gutenbergs 'most popular books' (downloaded at night between the 2nd and 3rd of April 2016). A list of the text currently lives on my database harddrive under GutTop100Books. (One is either missing or was never downloaded and off by one due to human error during downloading). The blocks are defined by splitting the text on double newline characters: `blocks = text.split('\n\n')` which reduces to about every paragraph given that format. 
    
  The Gutenberg texts were used for a period to help build the visualization tools described below, and in doing so a few biases were noticed. Tweets starting with 'RT', containing an '@' sybmol, numerials, and t.co.. urls as well as non english character sets were overly grouped together. While the grouping of non enlish character sets isn't unreasonable, the other features lead to clusters grouped by those features alone and not by any semantic similarity. As a simple means to solve for this, a subsection of the tweets themselves were used to build a new word relationship model. Due to time constraints on building the model, the first 1% and first 10% of the tweets from the recorded sample tweets were used. This selection does promote baises as any event that occurs will have an over representation of features associated with that event: time, day of the week, location it took place in, specific numerics, and other examples such as magnitude if it were an earthquake, etc. This over representation is accepted to reduce the over amplification of other twitter focused features mentioned earlier.
  
  Another issue from the gutenberg model that the twitter model attempted to address is the descrepancy between capitalized words and lowercased words. To address this every tweet in the subsection of the sample was added to the model three times: once as is, once using `.upper()` and once using `.lower()` on the string. There are a number of different ways this could have been addressed, but for the purpose of exploration and to address the previously noticed biases this solution was used. 
  
With the models reduced order representaiton comes associated error values of 42.46028715871472, 1138.9589823549384, and 4909.469678290722 for the gutenberg block model, 1% twitter sample model, and 10% twitter sample model respectively. 

The error values can be speculated on, and further experimentation focused on exploring this topic should take place but for the time being they are simply noted and looked past. 


### Clustering
While this topic should fall under *Inputs, initials, and background*, it's importance to topology makes it deserve extra focus. Unfortunately because this is my first exploration into the topic, I don't yet have much to say on the topic, and even less that I think I've got right on the subject. 

Two clustering methods were used.

Agglomerative Clustering is currently used to divide up the space. No cluster count is defined so the program auto selects this value based off of distance threshold. Distance Threshold has a large impact on the quality of the result clusters: if it's too large the clusters lack 




## Variations and Impacts





# Future Exploration
While I don't necessarily want to filter out tweets that don't conform to some predefined version of "This is a tweet about this event" I could use that methodolgy to filter the clusters, in hopes that I end up with a cluster of easily parsable tweets that have accessible information. 

The bot as a whole can continue to use [signal] + [noise] to determine an event, and the 'explaination' can filter for signals it's anticipating. (It can also fitler out for anticipated polysemy noise)



### Build Polysemy Filter
It's actually probably going to be a word embeddings model

End goal:

`Command/Line$ python buildPolysemyFilter.py -kw "thunder" -t "Lightning, thunder, severe weather storms" -p "OKC Thunder Basketball team. Basketball News" -rt ~/path/to/hhguideIntro.txt -o thunderPoly_word_embedding.tar.gz -or thunderPoly_Reduced_WE.tar.gz`

Where
 - `-kw`: Keyword, the shared word the filter pivots on
 - `-t`: Target, a sentence or collection of phrases with the intended true use of the word
 - `-p`: Polysemy, a sentence or collection of phrase with the polysemy use of the keyword
 - `-rt`: Reference Text used to profile text in embeddings
 - `-o`: output file for the raw word embedding model
 - `-or`: output file for the reduced word embedding model

 This structure should be broken up into two sections, the get/organize target/polysemy data, and the generate the word model section. The generate the word model portion is largely already built, so this should focus 

