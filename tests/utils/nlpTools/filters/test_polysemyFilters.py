


import tweepy
import json

from utils.nlpTools.filters.polysemyFilters import *

from lsalib.utils import wordRelationTools


def load_a_filter():

    #return load_filters('misc/polysemyFilterModels/', ['thunder'])
    from lsalib.utils import wordRelationTools
    wm = wordRelationTools.embedding_projection()
    wm.load('utils/experimental/topology/sample_reduced_model_v2_k50.tar.gz')

    return {'thunder': wm}

def load_a_nn_classifier(): 
    polyf = load_a_filter()
    knn = build_knn_classifier_model('utils/nlpTools/filters/poly_ref_texts/', polyf, ['thunder'])
    return knn


def get_tweepy_status_populated(tweetsFilePath='tests/testTweetOut.json'):

    # Load sample data in place
    with open(tweetsFilePath, 'r') as ifl:
        tweetSet = json.load(ifl)


    tweets_from_disk = []
    for x in tweetSet:
        tweets_from_disk.append(tweepy.models.Status().parse(None, x))

    return tweets_from_disk
    


def test_load_filters():
    models = load_filters('misc/polysemyFilterModels/', ['tornado'])


# def test_polysemyFilter_none_model():
#     polysemyFilter(['fake', 'tweets'], None)


# def test_polysemyFilter_with_model():
#     wm = 
#     polysemyFilter(['fake', 'tweets'], wordRelationTools.embedding_projection())

def test_build_knn_model():

    polyf = load_a_filter()
    knn = build_knn_classifier_model('utils/nlpTools/filters/poly_ref_texts/', polyf, ['thunder'])

    #build_knn_classifier_model('utils/nlpTools/filters/poly_ref_texts/', {'thunder': []}, ['thunder'])



def test_polysemyFilter_with_model():
    polyf = load_a_filter()
    knn = build_knn_classifier_model('utils/nlpTools/filters/poly_ref_texts/', polyf, ['thunder'])

    tweets = get_tweepy_status_populated()[:100]
    print(tweets[0].full_text)

    ptweets = polysemyFilter(tweets, polyf['thunder'], knn['thunder'])

    print(len(tweets), len(ptweets))
