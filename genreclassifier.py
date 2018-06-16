import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from analyzers import PosAnalyzer, PosFreqWordsAnalyzer, Morphology, PosLexAnalyzer
from sklearn.metrics import mutual_info_score
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import mutual_info_classif
from sklearn.externals import joblib


class ClfFactoryPosLex:
    def __init__(self, analyzer = None, pwf_analyzer=PosFreqWordsAnalyzer(Morphology().getAnalyzer(), lemmatize_freq = True), 
                 lexngrams = None, ngramsize = 2):
        if analyzer is None:
            self.analyzer = PosLexAnalyzer(pwf_analyzer, lexngrams, ngramsize)
        else:
            self.analyzer = analyzer
    
    def get_analyzer(self):
        return self.analyzer.analyze
    
    def make_classifier(self):
        return MultinomialNB(alpha=0.05)
    
    def make_vectorizer(self):
        return TfidfVectorizer(tokenizer=self.get_analyzer(), ngram_range=(2, 4), min_df=10)
    
class GenreClassifier():
    def __init__(self, dataset='news'):
        '''
        dataset = {'news', 'bruk'}
        '''
        self.tfidf = None
        self.clf = None
        self.sel_perc = None       
        if dataset == 'news':
            self.load('saves\\clf_news_MNB_poslex.pkl', 'saves\\tfidf_news_MNB_poslex.pkl', 
                      'saves\\featsel_news_MNB_poslex.pkl')
        elif dataset == 'bruk':
            self.load('saves\\clf_bruk_MNB_poslex.pkl','saves\\tfidf_bruk_MNB_poslex.pkl') 
            pass
        pass
    
    def init(self):
        freq_words = pd.read_csv('data\\freq_words.txt', sep=' ', header=None, names=['word', 'freq'])['word'].values
        lexngrams = np.loadtxt('data\\news_bigrams.txt', dtype=object, encoding='utf-8')
        print('Frequent words count:', len(freq_words))
        print('Lexical ngrams count:', len(lexngrams))
        self.factory = ClfFactoryPosLex(None, PosFreqWordsAnalyzer(Morphology().getAnalyzer(), list(freq_words), lemmatize_freq=True), lexngrams)
        
    def train(self, X, y, percentile=0):
        self.tfidf = self.factory.make_vectorizer()
        self.clf = self.factory.make_classifier()
        self.sel_perc = SelectPercentile(mutual_info_classif, percentile) if percentile >= 1 else None
        vtrain = self.tfidf.fit_transform(X)        
        if self.sel_perc is not None:
            vtrain = self.sel_perc.fit_transform(vtrain, y)
        self.clf.fit(vtrain, y)
        
    def save(self, clf_name, tfidf_name, sel_perc_name=None):
        joblib.dump(self.clf, clf_name) 
        joblib.dump(self.tfidf, tfidf_name)
        if not self.sel_perc is None:
            joblib.dump(self.sel_perc, sel_perc_name)
            
    def load(self, clf_name, tfidf_name, sel_perc_name=None):
        self.clf = joblib.load(clf_name) 
        self.tfidf = joblib.load(tfidf_name)
        if not sel_perc_name is None:
            self.sel_perc = joblib.load(sel_perc_name)        
        
    
    def predict(self, raw_strings, predict_proba = False):
        vtest = self.tfidf.transform(raw_strings)
        if self.sel_perc is not None:
            vtest = self.sel_perc.transform(vtest)
        predictor = self.clf.predict_proba if predict_proba else self.clf.predict
        y_predicted = predictor(vtest.toarray())
        return y_predicted
    
