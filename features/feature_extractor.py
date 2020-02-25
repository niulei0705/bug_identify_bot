#
#
# Nokia Copyright...
############################################################

import pandas as pd
import numpy as np
import math
import re
from utils.log2_df import DFCreator
from utils.read_config import ConfigLoader
from nltk import word_tokenize
from nltk import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from gensim import corpora, models, similarities
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split
from sklearn import svm
import yaml
from product_specified import fetch_product_specified

def feature_wcount(token, input_df):
    if token == 'wcount':
        count_df = input_df.applymap(wordcount)
    elif token == 'expcount':
        count_df = input_df.applymap(expcount)
    elif token == 'dbgcount':
        count_df = input_df.applymap(dbgcount)
    return count_df

def wordcount (log):
    matched = re.findall(r'(\w+)',log)
    return len(matched)

def expcount (log):
    matched = re.findall(r'exception|error|failure|warning',log,re.IGNORECASE)
    return len(matched)

def dbgcount (log):
    matched = re.findall(r'debug|info',log,re.IGNORECASE)
    return len(matched)

def extract_feature(input_df):
    wcount_df = feature_wcount('wcount', input_df)
    expcount_df = feature_wcount('expcount', input_df)
    #dbgcount_df = feature_wcount('dbgcount', input_df)
    #expcount_df = feature_wcount('expcount', input_df)
    tmp = pd.concat([wcount_df, expcount_df], axis=1, join_axes=[wcount_df.index])
    spe_df = fetch_product_specified(input_df)
    define_fc_df = pd.concat([tmp, spe_df], axis=1, join_axes=[tmp.index])
    return define_fc_df
