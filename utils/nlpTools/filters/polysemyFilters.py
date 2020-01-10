




import logging
import os

from sklearn.neighbors import KNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF


from lsalib.utils import dictionaryAidedFeatureVectorExtraction as dafve
from lsalib.utils import wordRelationTools
import kmlistfi


'''
Keith Murray

Contact: kmurrayis@gmail.com


Associated functions for building, loading, 



'''

def load_filters(filter_root_fp, events):
    model_suffix = '_p.tar.gz'
    models = {} 
    for i in range(len(events)):
        flpath = filter_root_fp+events[i]+model_suffix
        if os.path.isfile(flpath):
            model = wordRelationTools.embedding_projection()
            model.load(flpath)
            model.build_projection_matrix()
            models[events[i]] = model
        else:
            models[events[i]] = None
    return models

def build_poly_filter_word_model(text_root_fp, ref_text, event, out_file_dir):
    '''
    Generates a word model and the associated reduced embedding projection
    model given: a directory with sub directories containing reference texts
    for the true use of the word and polysemy uses of the word, a reference 
    text to build a dictionary based profile (grammar) out of, and an event
    name. 

    This assumes the text_root_fp is structured such that it's contents 
    have a `ref` directory, a noise directory, and one or more poly 
    directories, (in the event there are multiple polysemy's: 
    Blizzard: Snow (ref), Entertainment, Dairy Queen)

    So it'll look like:

    text_root_fp/ref/
    text_root_fp/noise/
    text_root_fp/poly1/
    text_root_fp/poly2/
    ...
    And so on

    It also assumes the event name is in the same casing as it appears in the 
    event bots event list
    '''
    corpus_fp = kmlistfi.les(text_root_fp)
    corpus = []
    for file_path in corpus_fp:
        with open(file_path, 'r') as ifl:
            corpus.append(ifl.read())
    wm = wordRelationTools.WordEmbeddingRelationshipModel()
    wm.build(model_text=ref_text, corpus=corpus)

    return

def make_knn_classifier(profiles, labels, knn_neighbor_count=4):
    nnClassifier = KNeighborsClassifier(n_neighbors=knn_neighbor_count)
    nnClassifier.fit(profiles, labels)
    return nnClassifier

def make_GaussianP_Classifier(profiles, labels):
    kernel = 1.0 * RBF(1.0)
    gpc = GaussianProcessClassifier(kernel=kernel,
            random_state=0)
    gpc.fit(profiles, labels)
    gpc.score(profiles, labels) 
    return gpc

def build_knn_classifier_model(text_root_fp, polyF, events):

    '''
    Requires a ref class, noise class, and a number of poly classes
    '''

    knn_neighbor_count = 4

    knn_models = {}
    for i in range(len(events)):
        if polyF[events[i]] == None:
            knn_models[events[i]] = None
        else:
            model = polyF[events[i]]
            # Grab Files
            

            file_path = text_root_fp + events[i] + '/'
            #extra_prefix = '/home/keith/Documents/filesForProgramming/Twitter/EventBot/'
            #file_path = extra_prefix+file_path
            #print(file_path)
            fls = kmlistfi.les(file_path)
            #print(fls)
            
            # Dir
            fls_dir = [os.path.dirname(x) for x in fls]
            classes = list(set(fls_dir))
            
            # Allow for multiple polysemy classes to be present
            k = 2
            class_labels = [-1]*len(classes)
            dir_to_class_map = {}
            for j in range(len(classes)):
                a_class = classes[j]
                if 'ref' in a_class.split(events[i])[-1]:
                    class_labels[j] = 0
                elif 'noise' in a_class.split(events[i])[-1]:
                    class_labels[j] = 1
                else:
                    class_labels[j] = k
                    k+=1
                dir_to_class_map[a_class] = class_labels[j]
            #print(classes)
            #print(class_labels)
            #print(dir_to_class_map)
            

            profiles = []
            labels = []
            for j in range(len(fls)):
                try:
                    with open(fls[j], 'r') as ifl:
                        text = ifl.read()
                except UnicodeDecodeError:
                    with open(fls[j], 'rb') as ifl:
                        text = ifl.read()
                p = model.profile_sequences(text)
                c = dir_to_class_map[fls_dir[j]]
                profiles.append(p)
                labels.append(c)

            
            # Given profiles and labels, make classifier
            #knn_models[events[i]] = make_knn_classifier(profiles, labels, knn_neighbor_count=knn_neighbor_count)
            #knn_models[events[i]] = make_GaussianP_Classifier(profiles, labels)
            knn = make_knn_classifier(profiles, labels, knn_neighbor_count=knn_neighbor_count)
            gpc = make_GaussianP_Classifier(profiles, labels)
            knn_models[events[i]] = [knn, gpc]


    return knn_models

def bufferVal(class_count):
    '''
    Given a count for the number of classes,
    calculates a bodge value for a required confidence level
    that the polysemy class must attain for it to be labeled 
    as the polysemy
    '''
    # Base vals for cc=3
    base_buffer =  0.4 
    buffer_c3 =base_buffer- 1/3
    buffer = buffer_c3*(3+1)
    score_threshold = buffer/(class_count+1)+1/class_count
    return score_threshold


def polysemyFilter(tweets, model, nnClassifier):
    '''
    Remove polyseme's of the event (OKC Thunder, Blizzard from DQ, or the gaming company)

    Parameters
    ----------
    tweets: list
        A list of tweets (tweepy tweet struct) 
    event: str
        A string for the event

    Returns
    -------
    tweets: list
        A list of all tweets (tweepy tweet object), filtered to remove polyseme's


    Notes
    -----
    Currently incomplete. Just a dummy function until I build the projection matrix



    '''
    

    if type(model) == type(None):
        return tweets


    #model, nnClassifier
    nnClassifier1 = nnClassifier[0]
    gpc = nnClassifier[1]

    filtered_tweets = []
    for tweet in tweets:
        text = tweet.full_text
        p = model.profile_sequences(text)
        p_class1 = nnClassifier1.predict([p])[0]
        p_class2 = gpc.predict([p])[0]
        print(p_class1, p_class2)
        # gpc Bodge: Set threshold for class>1 to be accepted


        passed_filter = True
        if p_class1 > 1 and p_class2 > 1:
            # Matched to Polysemy, decide if it's strong enough to chuck
            print(text)
            gpc_pprob = gpc.predict_proba([p])[0]
            print(gpc_pprob)
            score_threshold = bufferVal(len(gpc_pprob))

            if any([x for x in gpc_pprob[2:] if x >= score_threshold]):
                # By this point we know it's not the noise or ref val
                passed_filter = False
                print("CONFIDENT")


        if passed_filter:
            filtered_tweets.append(tweet)


    return filtered_tweets

