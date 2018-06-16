import numpy as np
import logging
import string
from collections import Counter
from vectors import Vectors, plot_document_clusters
from analyzers import PosFreqWordsAnalyzer
import tokenize_uk
import pymorphy2
from sklearn.cluster import KMeans

class Ngram():
    def __init__(self, ngram_lemmas, ngram_form=None, ngram_pos=None):
        self.ngram_lemmas = ngram_lemmas
        self.ngram_form = ngram_form
        self.ngram_pos = ngram_pos
        self.vector = None
        
    def __eq__(self, other):
        if not isinstance(other, Ngram):
            return False
        if len(self.ngram_lemmas) != len(other.ngram_lemmas):
            return False
        for i in range(len(self.ngram_lemmas)):
            if self.ngram_lemmas[i] != other.ngram_lemmas[i]:
                return False
        return True
    
    def lemma_str(self):
        return ' '.join(self.ngram_lemmas)

    def __hash__(self):
        return hash(self.lemma_str())
    
    def __str__(self):
        return self.lemma_str() if self.ngram_form is None else self.ngram_form
    
    def __repr__(self):
        return "({}, '{}', {})".format(self.ngram_lemmas, self.ngram_form, self.ngram_pos)


def kmeans(similarity, cluster_count):
    if cluster_count > 1:
        # kmeans
        X =  similarity.reshape(-1, 1)
        kmeans = KMeans(n_clusters=cluster_count, random_state=0).fit(X)
        t, u = zip(*sorted(list(enumerate(kmeans.cluster_centers_)), key=lambda x: x[1]))
        cluster_map = dict(zip(t, range(len(t))))
        cluster_index = list(map(lambda x: cluster_map[x], kmeans.labels_))
    else:
        cluster_index = np.zeros(len(similarity))
    return cluster_index


class NgramProcessor():
    def __init__(self, wordvectors, morph, freq_words = None, pos_allowed = None, ngramsize = 3, 
                 topic_suffix = '_topic', include_punctuation = False, analyze_pos = False, filter_frequent = True, ner = None):
        self.wordvectors = wordvectors
        self.morph = morph
        self.analyzer = PosFreqWordsAnalyzer(morph, freq_words)
        self.ngramsize = ngramsize
        self.pos_allowed = pos_allowed
        self.include_punctuation = include_punctuation
        self.analyze_pos = analyze_pos
        self.filter_frequent = filter_frequent
        self.topic_suffix = topic_suffix
        self.save_stop_words(freq_words)
        self.save_ner(ner)
        
    def save_ner(self, ner):
        if ner is None:
            self.ner = set()
            self.ner_lemmas = set()
        else:
            self.ner = set(ner)
            self.ner_lemmas = set([self.parse(x)[1] for x in ner])
            
    def is_named_entity(self, token, lemma):
        return token[0].isupper() and (token in self.ner or lemma in self.ner_lemmas)
        
    def save_stop_words(self, stop_words):
        if stop_words is None:
            self.stop_words = set()
            self.stop_lemmas = set()
        else:
            self.stop_words = set(stop_words)
            self.stop_lemmas = set([self.parse(x)[1] for x in stop_words])
        
    def tokenize(self, text):
        doc = tokenize_uk.tokenize_text(text)
        tokens = []
        for paragraph in doc:
            tokens.extend(['<p>']*(self.ngramsize-1))
            for sentence in paragraph:
                tokens.extend(sentence)
            tokens.extend(['</p>']*(self.ngramsize-1))
        return tokens
    
    def parse(self, token):
        p = self.analyzer.parse(token)
        form = p.normal_form 
        pos = 'PROPN' if self.is_named_entity(token, form) else p.tag.POS
        if token in self.wordvectors.vectors.vocab:
            form = token # not lemmatize word if there is a wordvector for it
        return (pos, form)
    
    def tokens2vectors(self, tokens, start = 0, end = None, filterpos = False, addzeros = False, filter_stopwords = True):
        if end is None:
            end = len(tokens)
        vv = []
        for i in range(start, end):
            pos, w = self.parse(tokens[i])
            if filterpos and not pos in self.pos_allowed:
                continue
            if filter_stopwords and (tokens[i] in self.stop_words or w in self.stop_lemmas):
                continue
            if w.isalpha() or addzeros:
                v = self.wordvectors.get_vector_case(w)
                vv.append(v)
        return vv

    
    def find_ngram(self, tokens, start, end=None):
        if end is None:
            end = len(tokens)        
        n = 0
        i = start
        ngram = None
        ngram_form = None
        ngram_pos = None
        next_start = None
        while i < end and n < self.ngramsize:
            if tokens[i].isalpha() or tokens[i] in ['<p>', '</p>'] or (self.include_punctuation and tokens[i][0] in string.punctuation):
                if ngram is None:
                    ngram = []
                    ngram_form = []
                    if self.analyze_pos:
                        ngram_pos = []
                elif next_start is None:
                    next_start = i
                pos, w = self.parse(tokens[i])
                ngram.append(w)
                ngram_form.append(tokens[i])
                if self.analyze_pos:
                    if pos is None:
                        if self.include_punctuation and tokens[i][0] in string.punctuation:
                            pos = tokens[i]
                        else: pos = 'X'
                    ngram_pos.append(str(pos))
                n +=1
            i +=1
        result = None if ngram is None else Ngram(ngram, ' '.join(ngram_form), ngram_pos) 
        return result, next_start
    
    def get_ngrams(self, tokens, start=0):
        i = start
        n = len(tokens)
        ngrams = []
        while i is not None and i <= n-self.ngramsize:
            ngram, i = self.find_ngram(tokens, i)
            if ngram is not None:
                for lemma in ngram.ngram_lemmas:
                    if lemma.isalpha():
                        ngrams.append(ngram)
                        break
        return ngrams

    def fit(self, X, y=None):
        self.fit_transform(X, y)
        return self
    
    def fit_transform(self, docs, y=None):
        '''
        y is a document label(category)
        If X is a list of strings - return ngrams, nothing to collect
        If X is a list of dicts (articles with 'category', 'text' and 'body') then collect stylistic ngrams
        '''
        self.ngrams_ = []
        self.labels_ = []
        for i, doc in enumerate(docs):
            y_label = None if y is None else y[i]
            doc_vect = None
            doc_vect_list = None
            freq = None
            if type(doc) is str:
                tokens = self.tokenize(doc)        
            else: # should be dict! with article structure
                tokens = None
                doc_start = ''
                if 'tags' in doc:
                    doc_start = "{} {}".format(doc_start, ' '.join(doc['tags']))
                if 'title' in doc:
                    doc_start = "{} {}".format(doc_start, doc['title'])
                if 'body' in doc:
                    doc_start = "{} {}".format(doc_start, doc['body'][0])
                    if len(doc['body']) > 5 and len(doc_start) < 50:
                        doc_start = "{} {}".format(doc_start, doc['body'][1])
                if 'text' in doc:
                    tokens = self.tokenize(doc['text'])
                    if self.filter_frequent:
                        freq = self.find_frequent(tokens) # looking for frequent non-stop words
                if doc_start:
                    doc_vect_list = self.tokens2vectors(self.tokenize(doc_start))
                    if freq is not None:
                        doc_vect_list.extend([self.wordvectors.get_vector_case(x) for x in freq])
                    if len(doc_vect_list) > 0:
                        doc_vect = np.mean(doc_vect_list, axis=0)
                if y_label is None and 'category' in doc:
                    y_label = doc['category']
            ngrams = self.get_ngrams(tokens)
            if not y_label is None:
                labels = [y_label]*len(ngrams)
            if not doc_vect is None:
                # checking stylistic ngrams
                # TODO: make vectors only once
                n_cluster_min = 2
                n_cluster_max = 5
                n_clusters = max(n_cluster_min, min(n_cluster_min + int(np.log(len(doc['text'])) - np.log(2000)), n_cluster_max))
                cluster_index = self.cluster_ngrams(ngrams, doc_vect_list = doc_vect_list, doc_vect = doc_vect, n_clusters = n_clusters)
                # vectors
                for j, cluster in enumerate(cluster_index):
                    if cluster==0:
                        if self.analyze_pos and y_label is not None and ('X' in ngrams[j].ngram_pos or 'PROPN' in ngrams[j].ngram_pos):
                            labels[j] = y_label + self.topic_suffix
                        pass
                    else:
                        if y_label is not None:
                            labels[j] = y_label + self.topic_suffix
            self.ngrams_.extend(ngrams)
            if not y_label is None:
                self.labels_.extend(labels)
        return self.ngrams_
    
    def transform(self, X):
        return self.fit_transform(X)
    
    def find_frequent(self, tokens, filterpos = True, filter_stopwords = True, topn=30, min_freq = 3):
        lemmas = Counter()
        for t in tokens:
            pos, w = self.parse(t)
            if filterpos and not pos in self.pos_allowed:
                continue
            if filter_stopwords and (t in self.stop_words or w in self.stop_lemmas):
                continue
            if w.isalpha():
                lemmas[w] += 1
        return [x[0] for x in lemmas.most_common() if x[1] >= min_freq]
    
    def cluster_ngrams(self, ngrams, doc_vect_list=None, doc_vect=None, n_clusters = 2):
        similarity = np.zeros(len(ngrams))
        doc = [doc_vect] + doc_vect_list
        for i, ng in enumerate(ngrams):
            v = np.mean([self.wordvectors.get_vector_case(x) for x in ng.ngram_lemmas if x.isalpha()], axis = 0)
            similarity[i] = max([self.wordvectors.cosine_distance(x, v) for x in doc])
        cluster_index = kmeans(similarity, n_clusters)
        return cluster_index

  
        