



'''
Goals:
For each batch of new tweets:
    prune out tweets already present


'''

import networkx as nx


import bokeh.plotting as bk
from bokeh.plotting import figure, output_file, save

#from bokeh.io import show#, output_file
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool, BoxZoomTool, ResetTool, PanTool, LinearColorMapper
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4, Plasma256


if '#EFF821' in Plasma256[0]:
    # Bright yellow, should be the highest value not lowest
    Plasma256.reverse()




import bokeh.plotting as bk
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, CustomJS, Slider
from bokeh.layouts import row, widgetbox



from scipy.spatial import distance_matrix
from sklearn.manifold import SpectralEmbedding
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import scipy


from lsalib.utils import dictionaryAidedFeatureVectorExtraction as dafve
from lsalib.utils import wordRelationTools
import copy

import datetime


from bokeh.io import export_svgs
from bokeh.io import export_png
import cairosvg

import tweepy
import json

try:
    from utils.eventClassifiers.simpleDistrobution import simpleClassifier
except:
    class simpleClassifier(object):
        # Faking a function in another file
        def getTweetsDistrobution(self, tweets):
            tbtwTweets = []
            for i in range(1, len(tweets)):
                delta = tweets[i-1].created_at - tweets[i].created_at
                delta = delta.total_seconds()
                tbtwTweets.append(delta)
            #print tbtwTweets
            return np.mean(tbtwTweets), np.std(tbtwTweets), tbtwTweets


class fake_fit_profiles(object):
    # To pretend there's a cluster in the event
    # There's only one tweet to add to the network
    def __init__(self):
        self.labels_ = [0]

class twitter_sample(object):
    def __init__(self, tweets):
        self.tweets = tweets
        self.get_timestamp() # Populates self._most_recent, self._oldest_tweet
        try:
            tweetMean, tweetStd, tbtwTweets = simpleClassifier.getTweetsDistrobution(self.tweets)
        except: 
            tbtwTweets = []
            for i in range(1, len(self.tweets)):
                delta = self.tweets[i-1].created_at - self.tweets[i].created_at
                delta = delta.total_seconds()
                tbtwTweets.append(delta)
            #print tbtwTweets

            tweetMean = np.mean(tbtwTweets)
            tweetStd = np.std(tbtwTweets)

        self.tweetmean = tweetMean
        self.tweetStd = tweetStd
        pass

    def get_timestamp(self):
        # Find the youngest and oldest tweets
        mostRecent = None
        self._oldest_tweet = self.tweets[0]
        mostRecent = self.tweets[0]
        for tweet in self.tweets:
            if tweet.created_at > mostRecent.created_at:
                mostRecent = tweet
            elif tweet.created_at < self._oldest_tweet.created_at:
                self._oldest_tweet = tweet
        self._most_recent = mostRecent
        return
    def age_difference(self, timeStamp):
        return timeStamp.created_at - self._most_recent.created_at
    def add_profiles(self, lowWRG, lowWRT10):
        self.profiles = profile_tweets(self.tweets, lowWRG, lowWRT10, selector=1)
    def cluster_tweets(self):
        '''
        Right now I don't really care about specifics of the clusters,
        so it's save to just create a list of cluster_labels

        '''
        if len(self.tweets) > 1:
            fit_profiles = clust_dbscan(self.profiles, esp_scale=.4)#0.25 .5
        else:
            fit_profiles = fake_fit_profiles()
        self.cluster_labels = fit_profiles.labels_
    def assign_nodes(self, node_label_start):
        self.nodes = []
        max_clust_label = max(self.cluster_labels)
        unclust_count = 0 
        # Be capable of adjusting for 'unclustered' -1 nodes
        for label in self.cluster_labels:
            if label == -1:
                unclust_count +=1
            self.nodes.append(label+unclust_count+node_label_start)
        return max_clust_label+unclust_count+node_label_start+1
    def json_the_tweets(self):
        return [tweet._json for tweet in self.tweets]

class twitter_recent_history_network(object):
    def __init__(self, lowWRG=None, lowWRT10=None):
        self.G = nx.Graph()
        self.display_G = nx.Graph()
        self._cur_node_index = 0
        self._total_sample_count = 0
        self._max_node_size = 0
        self._twitter_sample_count = 0
        self._tweet_ids = []
        self._twitter_samples = []
        self.age_limit_hours = 12
        self._age_limit = datetime.timedelta(hours=self.age_limit_hours)
        self.min_display_node_size = 4

        self._load_text_profiler(lowWRG, lowWRT10)

        pass
    def add_new_tweets(self, tweets):
        '''
        Removes tweets from sample that are already in network,
        Adds tweets to the network and 
        filters out samples that are too old


        (there's a bug where if an event is unpopular, it will get removed
        and added back in later: explain this more in depth but it is an edge 
        case so this is low priority)
        '''
        filt_tweets = self._filter_duplicates(tweets)
        if len(filt_tweets) > 0:
            samp = twitter_sample(filt_tweets)
            self.purge_old_tweets(samp._most_recent)
            samp.add_profiles(self.lowWRG, self.lowWRT10)
            samp.cluster_tweets()
            self._cur_node_index = samp.assign_nodes(self._cur_node_index)
            self._twitter_samples.append(samp)
            return(samp)
        else:
            return None
    def _filter_duplicates(self, tweets):
        filt_tweets = []
        for tweet in tweets:
            if tweet.id not in self._tweet_ids:
                filt_tweets.append(tweet)
                self._tweet_ids.append(tweet.id)
        #print("Preserved Tweets:", len(filt_tweets), "of", len(tweets))
        return filt_tweets
    def purge_old_tweets(self, mostRecent):

        # Find samples to purge and remove from self._twitter_samples
        if len(self._twitter_samples) > 0:
            purgeSamples = []
            while self._twitter_samples[0].age_difference(mostRecent) > self._age_limit:
                purgeSamples.append(self._twitter_samples[0])
                self._twitter_samples = self._twitter_samples[1:]
                if len(self._twitter_samples) == 0:
                    break

            # Remove tweet ids from self._tweet_ids and collect list of nodes involved
            purge_nodes = []
            for samp in purgeSamples:
                nodes = list(set(samp.nodes))
                purge_nodes+=nodes
                self._twitter_sample_count -= 1
                for i in range(len(samp.tweets)):
                    tweet = samp.tweets[i]
                    try:
                        del self._tweet_ids[self._tweet_ids.index(tweet.id)]
                    except:
                        #print("**delete error**")
                        #print('\t', tweet.id)
                        pass


            # Remove involved nodes from the graph 
            for node in purge_nodes:
                node_id = str(node)
                self.G.remove_node(node_id)
        return

    def build_Nodes(self, samp):
        for i in range(len(samp.tweets)):
            node_label = str(samp.nodes[i])
            if self.G.has_node(node_label):
                self.G.nodes[node_label]['member_count'] += 1
                if self.G.nodes[node_label]['member_count'] > self._max_node_size:
                    self._max_node_size = self.G.nodes[node_label]['member_count']
                self.G.nodes[node_label]['text_Samples'] += '>'+samp.tweets[i].full_text
                self.G.nodes[node_label]['tweet_sources'].append(samp.tweets[i])

            else:
                self.G.add_node(str(node_label))
                self.G.nodes[node_label]['mean'] = samp.tweetmean
                self.G.nodes[node_label]['stdiv'] = samp.tweetStd
                self.G.nodes[node_label]['pos'] = (samp.tweets[i].created_at.timestamp(),samp.nodes[i])# self._total_sample_count+random.random()*0.4-0.2, label)
                self.G.nodes[node_label]['total_sample_index'] = self._total_sample_count
                self.G.nodes[node_label]['member_count'] = 1
                self.G.nodes[node_label]['text_Samples'] = samp.tweets[i].full_text
                self.G.nodes[node_label]['tweet_sources'] = [samp.tweets[i]]
    def build_Edges(self):

        lookBack_Size = 2
        tweets = []
        source_nodes = []
        if len(self._twitter_samples) > lookBack_Size:
            subset = self._twitter_samples[-1*lookBack_Size:]
            for samp in subset:
                tweets += samp.tweets
                source_nodes += samp.nodes

            profiles = profile_tweets(tweets,self.lowWRG, self.lowWRT10, selector=0)
            #avDist = np.sum(scipy.spatial.distance.cdist(profiles, profiles))/(len(profiles)**2)
            fit_profiles = clust_dbscan(profiles, esp_scale=.35) #0.15 35
            #fit_profiles = clust_test(profiles) 

            clust_Sets = {}
            for i in range(len(tweets)):
                edge_label = fit_profiles.labels_[i]
                if edge_label > -1:
                    if edge_label in clust_Sets:
                        clust_Sets[edge_label].append(source_nodes[i])
                    else:
                        clust_Sets[edge_label] = [source_nodes[i]]
                
            for edge_block in clust_Sets:
                compact_group = list(set(clust_Sets[edge_block]))
                #print(compact_group)
                compact_group = [str(i) for i in compact_group]
                for i in range(len(compact_group)-1):
                    for j in range(i+1, len(compact_group)):
                        self.G.add_edges_from([(compact_group[i], compact_group[j])])

    def update_Graph(self, tweets):
        samp = self.add_new_tweets(tweets)
        if "none" not in str(type(samp)).lower():
            self._twitter_sample_count += 1
            self.build_Nodes(samp)
            self._total_sample_count += 1
            self.build_Edges()



    def _load_text_profiler(self, lowWRG=None, lowWRT10=None):
        if lowWRG != None:
            self.lowWRG = lowWRG
            self.lowWRT10 = lowWRT10
        else:
            self.lowWRG = wordRelationTools.embedding_projection()
            self.lowWRG.load('twitter_text_model_reduced_k50.tar.gz')
            self.lowWRT10 = wordRelationTools.embedding_projection()
            self.lowWRT10.load('twitter_text_model_reduced_k50_10perc.tar.gz')
        

   
    def populate_display_graph(self, allowed_graph_node_size = 10):
        
        self.display_G = self.G.copy()
        #print('X', list(nx.connected_components(self.G)))
        #print('Y', nx.number_connected_components(self.G))
        #print("HI")
        
        #self.G.nodes[node_label]['total_sample_index']
        # Highlighting most recent tweets
        max_index = 0
        for node in self.G.nodes:
            if self.G.nodes[node]['total_sample_index'] > max_index:
                max_index = self.G.nodes[node]['total_sample_index']



        node_connections = list(nx.connected_components(self.display_G))
        for g in node_connections:
            if len(list(g)) < allowed_graph_node_size:
                #print(g)
                self.display_G.remove_nodes_from(g)
        #max_memb_count = max(dict(self.display_G.nodes).items(), key=lambda x: x[1]['member_count'])
        #print('>>', max_memb_count)
        
        for node in self.display_G.nodes:
            #print(node)
            memb_count = self.display_G.nodes[node]['member_count']
            #size = np.log2(memb_count)+self.min_display_node_size
            size = memb_count+self.min_display_node_size-1
            self.display_G.nodes[node]['size']=size
        #pass


        # recurse with dropped threshold
        if len(self.display_G.nodes) == 0:
            newGraphSize =int(allowed_graph_node_size/5)
            if newGraphSize > 0:
                print("Dropping Graph Size: ", newGraphSize)
                self.populate_display_graph(allowed_graph_node_size = newGraphSize )
        

    def save(self, save_filename):
        all_tweets = [samp.json_the_tweets() for samp in self._twitter_samples]
        with open(save_filename, 'w') as outfile:
            json.dump(all_tweets, outfile)
        return
    def load(self, load_filename):
        with open(load_filename) as ifl:
            all_tweets = json.load(ifl)
        n = len(all_tweets)
        i = 0
        perc = 0
        for tweets_json_list in all_tweets:
            if int(i/n*10) > perc: # Show in 10% chunks
                print('\tLoading... ' + str(100*i/n) + '%')
                perc = int(i/n)*10
            tweets = [tweepy.models.Status().parse(None, tweet) for tweet in tweets_json_list]
            self.update_Graph(tweets)
        
        return

class twitter_Top_Network(object):
    def __init__(self, lowWRG=None, lowWRT10=None):
        self.G = nx.Graph()
        self.display_G = nx.Graph()
        self._cur_node_index = 0
        self._max_node_size = 0
        self.min_display_node_size = 4
        self.age_limit_hours = 12
        self._age_limit = datetime.timedelta(hours=self.age_limit_hours)
        
        self._tweet_buckets = []
        self._most_recents = []
        self._labels_buckets = []
        self._tweet_ids = []
        self._twitter_sample_count = 0
        self._total_sample_count = 0
        self._oldest_tweet = None
        
        self._load_text_profiler(lowWRG, lowWRT10)
        
        pass
    def _load_text_profiler(self, lowWRG=None, lowWRT10=None):
        if lowWRG != None:
            self.lowWRG = lowWRG
            self.lowWRT10 = lowWRT10
        else:
            self.lowWRG = wordRelationTools.embedding_projection()
            self.lowWRG.load('twitter_text_model_reduced_k50.tar.gz')
            self.lowWRT10 = wordRelationTools.embedding_projection()
            self.lowWRT10.load('twitter_text_model_reduced_k50_10perc.tar.gz')
        

    def build_Nodes(self, tweets):
        
        # Profile
        profiles = profile_tweets(tweets,self.lowWRG, self.lowWRT10, selector=1)

        # Cluster
        if len(profiles) > 1:
            fit_profs = clust_agglo(profiles)
        else:
            fit_profs = fake_fit_profiles()
            pass
        #fit_profs = clust_dbscan(profiles)
        
        # Add Nodes
        labels = []
        for i in range(len(fit_profs.labels_)):
            label = fit_profs.labels_[i]
            maxLabel = label
            if label > maxLabel:
                maxLabel = label
            if label > -1:
                node_num = self._cur_node_index+label
                labels.append(node_num)
                node_label = str(node_num)
                tweets[i].clust_label = node_label
                if self.G.has_node(node_label):
                    self.G.nodes[node_label]['member_count'] += 1
                    if self.G.nodes[node_label]['member_count'] > self._max_node_size:
                        self._max_node_size = self.G.nodes[node_label]['member_count']
                    self.G.nodes[node_label]['text_Samples'] += '>'+tweets[i].full_text


                else:
                    self.G.add_node(str(node_label))
                    self.G.nodes[node_label]['pos'] = (tweets[i].created_at.timestamp(),label)# self._total_sample_count+random.random()*0.4-0.2, label)
                    self.G.nodes[node_label]['total_sample_index'] = self._total_sample_count
                    self.G.nodes[node_label]['member_count'] = 1
                    self.G.nodes[node_label]['text_Samples'] = tweets[i].full_text
                
            
        try:
            self._cur_node_index += fit_profs.n_clusters_
            #print(fit_profs.n_clusters_)
        except:
            self._cur_node_index += maxLabel+1
            #print(maxLabel)
            
        self._labels_buckets.append(labels)
        return labels
    def build_edges(self, labels):
        lookBack_Size = 2
        tweets = []
        olabels = []
        #print("Size of Evaluation Space:", len(self._tweet_buckets)-lookBack_Size)
        #print("Samples in Class", self._twitter_sample_count)
        if self._twitter_sample_count > lookBack_Size:
            max_len = len(self._tweet_buckets)
            #print(len(self._tweet_buckets))
            #print(len(self._labels_buckets))
            for i in range(max_len-lookBack_Size-1, max_len):
                grab_index =  i
                #print("\t>Grabbing tweets from sample group: ", grab_index)
                tweets += self._tweet_buckets[grab_index][:]
                olabels += self._labels_buckets[grab_index][:]
            #print("tweets in Edges", len(tweets))
            
            profiles = profile_tweets(tweets,self.lowWRG, self.lowWRT10, selector=2)
            # Optional Dim Reduct to vary the clustering
            # embedding = SpectralEmbedding(n_components=10)
            # X_transformed = embedding.fit_transform(profiles)
            # Cluster
            fit_profs = clust_agglo(profiles)
            # fit_profs = clust_agglo(X_transformed)
            clust_Sets = {}
            for i in range(len(tweets)):
                if olabels[i] > -1:
                    edge_label = fit_profs.labels_[i]
                    if edge_label in clust_Sets:
                        clust_Sets[edge_label].append(olabels[i])
                    else:
                        clust_Sets[edge_label] = [olabels[i]]
            
            for edge_block in clust_Sets:
                compact_group = list(set(clust_Sets[edge_block]))
                #print(compact_group)
                compact_group = [str(i) for i in compact_group]
                for i in range(len(compact_group)-1):
                    for j in range(i+1, len(compact_group)):
                        self.G.add_edges_from([(compact_group[i], compact_group[j])])
                
    
    def populate_display_graph(self):
        allowed_graph_node_size = 10
        self.display_G = self.G.copy()
        #print('X', list(nx.connected_components(self.G)))
        #print('Y', nx.number_connected_components(self.G))
        #print("HI")
        node_connections = list(nx.connected_components(self.display_G))
        for g in node_connections:
            if len(list(g)) < allowed_graph_node_size:
                #print(g)
                self.display_G.remove_nodes_from(g)
        max_memb_count = max(dict(self.display_G.nodes).items(), key=lambda x: x[1]['member_count'])
        #print('>>', max_memb_count)
        
        for node in self.display_G.nodes:
            #print(node)
            memb_count = self.display_G.nodes[node]['member_count']
            #size = np.log2(memb_count)+self.min_display_node_size
            size = memb_count+self.min_display_node_size-1
            self.display_G.nodes[node]['size']=size
        #pass
        
    def purge_old_tweets(self, mostRecent):
        # Purge twitter samples when the most recent tweet of that sample
        #  is too old
        removed = 0
        purge_index = []
        post_purge_MR = []
        removed_tweets = []
        removed_labels_lists = []
        post_purge_tweets = []
        post_purge_labels = []
        for i in range(len(self._most_recents)-1):
            if mostRecent.created_at - self._most_recents[i].created_at > self._age_limit:
                #print("\tPurge Age:", mostRecent.created_at - self._most_recents[i].created_at)
                purge_index.append(i)
                removed_tweets.append(self._tweet_buckets[i])
                removed_labels_lists.append(self._labels_buckets[i])
                self._twitter_sample_count -= 1
            else:
                post_purge_MR.append(self._most_recents[i])
                post_purge_tweets.append(self._tweet_buckets[i])
                post_purge_labels.append(self._labels_buckets[i])
        for tweets in removed_tweets:
            for tweet in tweets:
                try:
                    del self._tweet_ids[self._tweet_ids.index(tweet.id)]
                except:
                    #print("**delete error**")
                    #print('\t', tweet.id)
                    pass
                removed += 1
                
        removed_labels = []
        for ll in removed_labels_lists:
            for label in ll:
                removed_labels.append(label)
        for label in list(set(removed_labels)):
            self.G.remove_node(str(label))
            
                
        post_purge_MR.append(self._most_recents[-1])
        post_purge_tweets.append(self._tweet_buckets[-1])
        post_purge_labels.append(self._labels_buckets[-1])
                
        self._most_recents = post_purge_MR
        self._tweet_buckets = post_purge_tweets
        self._labels_buckets = post_purge_labels
        
        return removed
    
        
    def _most_recent_tweet(self, tweets):
        mostRecent = None
        if self._oldest_tweet == None:
            self._oldest_tweet = tweets[0]
        if mostRecent == None:
            mostRecent = tweets[0]
        for tweet in tweets:
            if tweet.created_at > mostRecent.created_at:
                mostRecent = tweet
            elif tweet.created_at < self._oldest_tweet.created_at:
                self._oldest_tweet = tweet
        self._most_recents.append(mostRecent)
        return mostRecent
    def _filter_duplicates(self, tweets):
        filt_tweets = []
        for tweet in tweets:
            if tweet.id not in self._tweet_ids:
                filt_tweets.append(tweet)
                self._tweet_ids.append(tweet.id)
        #print("Preserved Tweets:", len(filt_tweets), "of", len(tweets))
        return filt_tweets
            
    def update_Graph(self, tweets):
        #print("Starting tweet bucket", len(self._tweet_buckets))
        tweets = self._filter_duplicates(tweets)
        if len(tweets) > 0:
            # Get Most Recent Tweet
            mostRecent = self._most_recent_tweet(tweets)
            #print(mostRecent.created_at, self._oldest_tweet.created_at, mostRecent.created_at - self._oldest_tweet.created_at)
            
            
            # Remove Old Tweets
            if self._twitter_sample_count > 0:
                removed = self.purge_old_tweets(mostRecent)
                #print("\tPurged ", removed)
                
            
            # Add tweets to bucket:
            #print("Adding to tweet bucket", len(self._tweet_buckets))
            self._tweet_buckets.append(tweets)
            #print("Added to tweet bucket", len(self._tweet_buckets))
            self._twitter_sample_count += 1
            self._total_sample_count += 1
            
            
            # Make and Add Nodes
            node_labels = self.build_Nodes(tweets)
            # Process and Add Edges
            self.build_edges(node_labels)
            
            #for node 
        
        
        pass
    

def hex_to_rgb_int_tuple(color):
    h = color.lstrip('#')
    return  tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def rgb_int_tuple_to_hex(color):
    # It's ugly, but functional and I've sunk too much time already in this
    return '#'+"".join([str(hex(int(x))[2:].zfill(2)).split('0x')[-1].upper() for x in color])


def make_color_scale(steps, color_step_list):
    blocks = len(color_step_list) - 1
    i = 0
    carry_over_remainder = 0
    colorMap = []
    for segment in range(blocks):
        start_color = hex_to_rgb_int_tuple(color_step_list[segment])
        r1, g1, b1 = start_color
        stop_color = hex_to_rgb_int_tuple(color_step_list[segment+1])
        r2, g2, b2 = stop_color
        segment_size = int(steps/blocks)+carry_over_remainder
        segment_remainder = steps%blocks-carry_over_remainder
        rdelta, gdelta, bdelta = (r2-r1)/steps, (g2-g1)/steps, (b2-b1)/steps
        for step in range(segment_size):
            r1 += rdelta
            g1 += gdelta
            b1 += bdelta
            colorMap.append(rgb_int_tuple_to_hex((int(r1), int(g1), int(b1))))
            #if step == 0:
            #    colorMap[-1] = start_color
        #colorMap[-1] = stop_color
        carry_over_remainder = segment_remainder

    assert len(colorMap) == steps
    return colorMap


def node_color_spectrum():
    '''
    # Basketball polysemy 


    Note: if value you're coloring is not 
    linearly distrubted, things will suck somewhat
    '''
    steps = 256
    weather_color = "#008000"# "green"
    unclear = '#808080' #"gray"
    basketball_color = "#FA8320" #"YellowOrange"
    color_step_list = [weather_color, weather_color, unclear, basketball_color, basketball_color]


    color_map = make_color_scale(steps, color_step_list)



    return color_map

from sklearn.neighbors import KNeighborsClassifier
import kmlistfi


def special_classify_node(nnClassifier, tweets, twit_top):
    rawScore = 0
    for tweet in tweets:
        text = tweet.full_text
        p = twit_top.lowWRG.profile_sequences(text)
        p_class = nnClassifier.predict([p])[0]
        rawScore += p_class



    return rawScore/len(tweets)
    

def build_network_visualization(twit_top):
    color_nodes_on = 'mean'#'group_class'
    twit_top.populate_display_graph(allowed_graph_node_size=10)
    G = twit_top.display_G
    if len(G.nodes) == 0:
        # The standard G doesn't have the display values 
        # populated, so if a graph doesn't 
        # have enough info for a display, it can't be returned
        raise ValueError("The Graph is unable to display as there are not enough edges")
    #G = twit_top.G
    source = ColumnDataSource(data=dict(
        node_labels=list(G.nodes)
    ))
    TOOLTIPS = [
        ("index", "$index"),
        ("(x,y)", "($x, $y)"),
        ("Standard Div", "@stdiv"),
        ("Mean", "@mean"),
        ("Sample Group", "@total_sample_index"),
        ("size", "@member_count"),
        ("Class", "@group_class"),
        ("text_Samples", "@text_Samples")
    ]


    # Add extra classification to nodes
    # Building Classifier
    sample_path_weather = '/home/keith/Documents/filesForProgramming/Twitter/polysemeTesting/polysemeRawData/actual/Thunder/'
    sample_path_basketball = '/home/keith/Documents/filesForProgramming/Twitter/polysemeTesting/polysemeRawData/polysemes/Thunder/'
    bb_weather_featurev = []
    bb_weather_labels = []
    fls = kmlistfi.les(sample_path_weather)
    for flpath in fls:
        with open(flpath, 'r') as fl:
            text = fl.read()
        p = twit_top.lowWRG.profile_sequences(text)
        bb_weather_featurev.append(p)
        bb_weather_labels.append(0)
    
    fls = kmlistfi.les(sample_path_basketball)
    for flpath in fls:
        with open(flpath, 'r') as fl:
            text = fl.read()
        p = twit_top.lowWRG.profile_sequences(text)
        bb_weather_featurev.append(p)
        bb_weather_labels.append(1)
    nnClassifier = KNeighborsClassifier(n_neighbors=3)
    nnClassifier.fit(bb_weather_featurev, bb_weather_labels)
    # Classify and Score all tweets in each node
    classes = []
    for node in G.nodes:
        tweets = G.nodes[node]['tweet_sources']
        score = special_classify_node(nnClassifier, tweets, twit_top)
        G.nodes[node]["group_class"] = score
        classes.append(score)
        del G.nodes[node]['tweet_sources'] # Removed to make node json serializable



    min_color_val = None
    max_color_val = None
    for node in G.nodes:
        if min_color_val == None or G.nodes[node][color_nodes_on] < min_color_val:
            min_color_val = G.nodes[node][color_nodes_on]
        if max_color_val == None or G.nodes[node][color_nodes_on] > max_color_val:
            max_color_val = G.nodes[node][color_nodes_on]

    # print(min_color_val, max_color_val)
    # print(classes)


    if '#EFF821' in Plasma256[-1]:
        print("Reversing")
        # Bright yellow, should be the highest value not lowest
        Plasma256.reverse()
    else:
        print("Keeping")


    bbThunder256 = node_color_spectrum()
    #print(bbThunder256)

    mapper = LinearColorMapper(palette=Plasma256, low=min_color_val, high=max_color_val)
    #print(len(mapper))
    plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1), )

    graph_renderer = from_networkx(G, nx.spring_layout,  center=(0,0))
    graph_renderer.node_renderer.glyph = Circle(size = 'size', fill_color={'field': color_nodes_on, 'transform': mapper}, line_color=None)
    graph_renderer.edge_renderer.glyph = MultiLine(line_color="#616161", line_alpha=0.8, line_width=1)
    plot.add_tools(HoverTool(tooltips=TOOLTIPS), TapTool(), BoxSelectTool(), BoxZoomTool(), ResetTool(), PanTool())

    plot.renderers.append(graph_renderer)
    #save(plot, filename="test")
    #export_png(plot, filename="plot_test_save.png")
    
    
    return plot


def clust_agglo(profiles, avDist=None):
    if avDist == None:
        avDist = np.sum(scipy.spatial.distance.cdist(profiles, profiles))/(len(profiles)**2)
    aggloC = AgglomerativeClustering(n_clusters=None, 
                                         distance_threshold=avDist*.81,
                                         compute_full_tree=True)
    return aggloC.fit(profiles)

def clust_dbscan(profiles, avDist=None, esp_scale=0.1): # Was 0.5
    if avDist == None:
        avDist = np.sum(scipy.spatial.distance.cdist(profiles, profiles))/(len(profiles)**2)
        if avDist <= 0 :
            avDist = 1   
    try:
        dbscan = DBSCAN(eps=avDist*esp_scale, min_samples=2)
        return dbscan.fit(profiles)
    except ValueError:
        print('\tAvg Dist for Esp: ', avDist*esp_scale)
        dbscan = AgglomerativeClustering(n_clusters=None, 
                                         distance_threshold=avDist*.81,
                                         compute_full_tree=True)
        return dbscan.fit(profiles)
    

def clust_test(profiles, avDist=None):


    from sklearn.cluster import AffinityPropagation
    affProp = AffinityPropagation()
    affProp.fit(profiles)
    if len(affProp.cluster_centers_) == 0:
        # Does not converge
        return clust_dbscan(profiles)
    else:
        return affProp.fit(profiles)

def profile_tweets(tweets, lowWRG, lowWRT10, selector=0):
    profiles = []
    for tweet in tweets:
        text = tweet.full_text
        text = text + '\n' + text.upper() + '\n' + text.lower()
        if selector == 0:
            p1 = lowWRG.profile_sequences(text)
            profiles.append(p1)
        elif selector == 1:
            p2 = lowWRT10.profile_sequences(text)
            profiles.append(p2)
            
        elif selector == 2:
            p1 = lowWRG.profile_sequences(text)
            p2 = lowWRT10.profile_sequences(text)
            assert len(p1) == len(p1+p2)
            profiles.append(p1+p2)
    return profiles

def render_to_png(my_plot):

    # my_plot.output_backend = "svg"
    # flsvg = "temp/plot_test_save.svg"
    flpng = "temp/topology_plot_save.png"
    # export_svgs(my_plot, filename=flsvg)
    # cairosvg.svg2png(url=flsvg, write_to=flpng)
    export_png(my_plot, filename=flpng)

    return flpng


def make_Image(ttn):
    my_plot = build_network_visualization(ttn)




    flp = render_to_png(my_plot)



    output_file("temp/top_plot_source/topology_plot_"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".html")
    save(my_plot)
    return flp




def add_sample_to_network(networks, event_name, timestamp, tweets):
    ttn = networks[event_name]
    ttn.update_Graph(tweets)
    networks[event_name] = ttn

    return networks


# **************************************




def make_Fake_TTNAnd_Plot():
    def load_recent_tweets(filePath):
        with open(filePath, 'r') as ifl:
            tweetSet = json.load(ifl)

        tweets_from_disk = []
        for x in tweetSet:
            tweets_from_disk.append(tweepy.models.Status().parse(None, x))

        return tweets_from_disk
    import kmlistfi
    import tweepy
    import json






    
    sampleTweetLoc = "/home/keith/Documents/filesForProgramming/Twitter/EventBot/misc/sample_tweets2/sample_tweets/"
    i = 0
    sample_by_time = sorted(kmlistfi.les(sampleTweetLoc))
    #print(sample_by_time[:3])
    for sample_Tweets in kmlistfi.les(sampleTweetLoc):
        i +=1

    event_Name = 'tornado'
    event_list = []
    files_of_interest = []

    with open('/home/keith/Documents/filesForProgramming/Twitter/EventBot/misc/listOfTwitterEvents.txt', 'r') as efl:
        for line in efl:
            event_list.append(line.strip())
            files_of_interest.append([])
            
    for i in range(len(sample_by_time)):
        cur_fl_path = sample_by_time[i]
        counts = [0]*len(event_list)
        tweets = load_recent_tweets(cur_fl_path)
        for tweet in tweets:
            text = tweet.full_text.lower()
            for j in range(len(event_list)):
                event = event_list[j].lower()
                if event in text:
                    counts[j] += 1
        index = counts.index(max(counts))
        files_of_interest[index].append(sample_by_time[i])
        if i > 500:
            break

    lowWRG = wordRelationTools.embedding_projection()
    lowWRG.load('sample_reduced_model_v2_k50.tar.gz')
    #lowWR.load('twitter_text_model_reduced_k50.tar.gz')
    lowWRT10 = wordRelationTools.embedding_projection()
    lowWRT10.load('twitter_text_model_reduced_k50_10perc.tar.gz')
        



    # ttn = twitter_recent_history_network(lowWRG=lowWRG, lowWRT10=lowWRT10)
    # sh_path = '/home/keith/Documents/filesForProgramming/Twitter/EventBot/temp/Shipwreck_save.json'
    # ttn.load(sh_path)
    # my_plot = make_Image(ttn)
    
    #sampleTweetLoc = "/home/keith/Documents/filesForProgramming/Twitter/EventBot/misc/sample_tweets/"
    #sample_by_time = sorted(kmlistfi.les(sampleTweetLoc))
    sample_by_time = files_of_interest[0]
    start=0
    steps=10
    sample_by_time = sorted(sample_by_time)
    tweets = load_recent_tweets(sample_by_time[0])
    tweet = tweets[0]
    #print(tweet.created_at)
    #print(type(tweet.created_at))
    
    twit_top = twitter_recent_history_network(lowWRG=lowWRG, lowWRT10=lowWRT10)
    #twit_top.build_Nodes(tweets)
    '''
    Note: super interesting graph with earthquake data
    Start: 660
    Step: 50
    Start of point of interest: 670
    '''
#     steps = 30
#     start = 100
    #print(start, start+len(sample_by_time))
    for i in range(start, start+steps):
        #twit_top.update_Graph(tweets)
        print(i)
        twit_top.update_Graph(load_recent_tweets(sample_by_time[i]))


    twit_top.save('temp/test.json')
    twit_top2 = twitter_recent_history_network(lowWRG=lowWRG, lowWRT10=lowWRT10)
    twit_top2.load('temp/test.json')

    import time
    my_plot = make_Image(twit_top2)
    time.sleep(1)
    my_plot = make_Image(twit_top2)
    time.sleep(1)
    my_plot = make_Image(twit_top2)
    time.sleep(1)
    my_plot = make_Image(twit_top2)

    twit_top2.save('temp/test.json')

        
    pass




if __name__ == "__main__":
    make_Fake_TTNAnd_Plot()