#
#
# Nokia Copyright...
############################################################

import pandas as pd
import numpy as np
import argparse
import sys
import pickle
import os
sys.path.append(os.getcwd())

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
import yaml
import cPickle as pickle
import os
from sklearn import linear_model
from features.nls.feature_extractor import extract_feature

CLASSIFER_MODEL_DICT = {
    'glc': 'model/glc_classifier.pickle',
    'lppserver': 'model/lppserver_classifier.pickle',
    'sls_server': 'model/sls_classifier.pickle',
    'spu': 'model/spu_classifier.pickle',
    'tlr': 'model/tlr_classifier.pickle',
    'libLPP.so': 'model/lpp_classifier.pickle'
}

def apply_cv_nb(input_df, label_s):
    '''
    This function will use  Naive Bayes with Count vectorizer
    '''
    from sklearn import metrics
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.feature_extraction.text import CountVectorizer
    #from sklearn.cross_validation import train_test_split

    nd_df = input_df.applymap(keepstring)
    X = nd_df
    y = label_s
    #X_train, X_test, y_train, y_test = train_test_split(X, y)

    vect = CountVectorizer()

    #X_train_dtm = vect.fit_transform(X_train)
    #X_test_dtm = vect.fit_transform(X_test)

    #nb = MultinomialNB()
    #nb.fit(X_train_dtm, y_train)
    #y_pred_class = nb.predict(X_test_dtm)
    #metrics.accuracy_score(y_test, y_pred_class)

def keep_nwords(log):
    e_sw = stopwords.words('english')
    texts = [word for word in word_tokenize(log.lower().decode('utf-8')) if word not in e_sw]
    items = texts[0:500]
    log_begin = ' '.join(map(unicode, items))
    return log_begin

def keep_impwords(log):
    e_sw = stopwords.words('english')
    texts = [word for word in word_tokenize(log.lower().decode('utf-8')) if word not in e_sw]
    texts = [impword(word) for word in texts if not hasNumbers(word)]
    items = texts[0:]
    log_imp = ''.join(map(unicode, items))
    return log_imp

def keep_alpha(log):
    e_sw = stopwords.words('english')
    # CHange the decode to latin-1 as UTF-8 is throwing exception
    texts = [word for word in word_tokenize(log.lower().decode('latin-1')) if word not in e_sw]
    texts = [word for word in texts if not hasNumbers(word)]
    items = texts[0:]
    log_imp = ' '.join(map(unicode, items))
    return log_imp

def hasNumbers(str):
    return any(c.isdigit() for c in str)

impwords = ['ProxyDiaConnection','debug']
def impword(w):
    if w in impwords:
        return w+' '
    else:
        return ''

def train_with_data(input_df, labels, proc):
    classifier = get_classifier(proc)
    if classifier is None:
        classifier = linear_model.SGDClassifier(loss='log')
        classifier.fit(input_df, labels)
    else:
        classifier.partial_fit(input_df, labels)
    pk_file = open(CLASSIFER_MODEL_DICT[proc], 'w')
    pickle.dump(classifier, pk_file)

def predict(input_df, proc):
    classifier = get_classifier(proc)
    if classifier is None:
        raise BaseException("No persistent classifier found")
    return classifier.predict(input_df), classifier.decision_function(input_df)


def mark_bug(index_dataframe, bug_dataframe, proc):

    labels = []
    for dataindex, datarow in index_dataframe.iterrows():
        bugflag = 0
        for bugindex, bugrow in bug_dataframe.iterrows():
            if (str(datarow.loc[0]) == str(bugrow.loc[0])) \
                    & (str(datarow.loc[1]) == str(bugrow.loc[1])) & (proc == str(bugrow.loc[2])):
                labels.append(1)
                bugflag = 1
                break
        if bugflag == 0:
            labels.append(0)
    return labels

def get_bug_dataframe():
    with open(r'config/bug_list.yml') as yaml_config:
         bug_list = yaml.load(yaml_config)['bug_list']
    return pd.DataFrame.from_records(bug_list, columns=['bug_id','timestamp', 'process'])

def get_index_dataframe(fc_dataframe):
    first_index = fc_dataframe.index.get_level_values(0).values
    second_index = fc_dataframe.index.get_level_values(1).values
    return pd.DataFrame.from_records(np.array([first_index, second_index])).T

def get_classifier(proc):
    if os.path.isfile(CLASSIFER_MODEL_DICT[proc]):
        with open(CLASSIFER_MODEL_DICT[proc]) as f:
            classifier = pickle.load(f)
            return classifier
    else:
        return None




if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--p_level',
        type=str,
        default='case',
        help='Predict cases bug or process bug'
    )
    parser.add_argument(
        '--date',
        type=str,
        default='all',
        help='Sub training data set'
    )
    parser.add_argument(
        '--action',
        type=str,
        default='train'
    )
    FLAGS, unparsed = parser.parse_known_args()
    #Load the configurations
    loader = ConfigLoader()
    config = loader.load_config('config/product_config.json')

    #Read the logs and convert them into dataframe
    df_creator = DFCreator()
    case_list = df_creator.get_file_list(config.get_dstdir(), FLAGS.date)
    input_df_dict = df_creator.proc2_dataframe(case_list, config.get_processnames())
    bug_dict = {}

    if input_df_dict is None:
        print 'Input dataframe from log2_df is null'
        sys.exit(-1)

    if FLAGS.p_level == 'case':

    # Replace the NaN with 'empty'
        for proc in input_df_dict.keys():
            input_df = input_df_dict[proc]
            input_df[input_df.isnull()] = 'empty'
            bug_list = []
            define_fc_df = extract_feature(input_df)
            bug_dataframe = pd.DataFrame.from_records(get_bug_dataframe().values)
        #X_train, X_test, y_train, y_test = train_test_split(define_fc_df, labels)
        #train_with_data(X_train, y_train)
            if FLAGS.action == 'train':
                labels = mark_bug(get_index_dataframe(define_fc_df), bug_dataframe, proc)
                train_with_data(define_fc_df, labels, proc)
            elif FLAGS.action == 'predict':
                y_predict, log_proba = predict(define_fc_df, proc)
                print '--------Probability estimates-------\n'
                print log_proba
                print '--------Probability estimates-------\n'
                for i in range(len(y_predict)):
                    if y_predict[i] == 1:
                        bug_list.append(define_fc_df.index.levels[0][i])
                bug_dict[proc] = bug_list
    print bug_dict

        #print expcount_df
        #print dbgcount_df
        # keep alpha create a df will contains only alphabets
        #input_df.applymap(keep_alpha)
    #elif FLAGS.p_level == 'process':
        #print len(input_df)

