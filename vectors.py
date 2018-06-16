'''
Contains class Vectors that wraps gensim KeyedVectors to provide smooth search for unknown and 
'''
from gensim.models import KeyedVectors
import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from collections import Counter


class Vectors():
    def __init__(self, vectors = None):
        self.vectors = vectors
        self.unk = None

    def calculate_unknown(self, alg='zeros', mean_shuffle_size = 2000, mean_sample_size = 100):
        '''
        Calculates unknown vector value for the class
        alg: 
            must be a string value representing algorithm for unknown word vector calculation
            zeros: unk is a zero vector
            mean: unk is a vector constructed as a mean of least frequent words
        mean_shuffle_size: for alg='mean' mean_shuffle_size of the least frequent words vectors are shuffled to get mean_sample_size vectors to calculate unknown vecctor as their mean
        mean_sample_size: for alg='mean' mean_shuffle_size of the least frequent words vectors are shuffled to get mean_sample_size vectors to calculate unknown vecctor as their mean
        '''
        if alg not in ['zeros', 'mean']:
            raise ValueError("possible values for alg are 'zeros', 'mean'")
        if alg is 'zeros':
            self.unk = self.zeros()
        if alg is 'mean':
            sample = np.random.choice(list(self.vectors.vocab.keys())[0:-mean_shuffle_size], size=mean_sample_size)
            self.unk =  np.mean([self.vectors[x] for x in sample], axis=0)
        return self.unk

    def zeros(self):
        return np.zeros(self.vectors.vector_size)

    def get_unknown(self):
        if self.unk is None:
            raise ValueError('unknown vector is not set up, use calculate_unknown method')
        return self.unk

    def get_vector(self, word):
        return self.vectors[word] if word in self.vectors.vocab else self.unk

    def get_vector_case(self, word):
        if word in self.vectors.vocab:
            v = self.vectors[word]
        elif word.title() in self.vectors.vocab:
            v = self.vectors[word.title()]
        elif word.lower() in self.vectors.vocab:
            v = self.vectors[word.lower()]
        elif not word.isalpha():
            v = self.zeros()
        else:
            v = self.unk
        return v        
    
    def load(self, vectors_fname):
        self.vectors = KeyedVectors.load_word2vec_format(vectors_fname)

    def words_mean(self, tokens):
        doc = [word for word in tokens if word in self.vectors.vocab]
        if len(doc) == 0:
            return self.get_unknown()
        return np.mean(self.vectors[doc], axis=0)
    

    def cosine_distance(self, word, docvector):
        '''
        word could be a string value or numpy array
        '''
        if type(word) is str:
            return 1-spatial.distance.cosine(self.vectors[word], docvector) if word in self.vectors else 0
        else:
            return 1-spatial.distance.cosine(word, docvector)

    def filter_document(self, docvector, items, cluster_count):
        '''
        For each word or ngram in items calculates similarity to docvector as cosine_distance and, if cluster_count > 1, divides into clusters with KMeans.
        Returns two arrays: similarity, cluster_index - corresponding to items order. The 0 cluster is the cluster of the smallest similarity values.
        docvector: vector of the document
        items: list of words or word lists containing ngrams 
        cluster_count: if cluster_count is greater than 1, KMeans algorithm will be used to get divide items into cluster_count clusters according to cosine_distance to docvector
        '''
        similarity = np.zeros(len(items))
        for i, x in enumerate(items):
            if type(x) is str:
                d = self.cosine_distance(x, docvector)
            else:
                v = self.words_mean(x)
                d = self.cosine_distance(v, docvector)
            similarity[i] = d
        if cluster_count > 1:
            # kmeans
            X =  similarity.reshape(-1, 1)
            kmeans = KMeans(n_clusters=cluster_count, random_state=0).fit(X)
            t, u = zip(*sorted(list(enumerate(kmeans.cluster_centers_)), key=lambda x: x[1]))
            cluster_map = dict(zip(t, range(len(t))))
            cluster_index = list(map(lambda x: cluster_map[x], kmeans.labels_))
        else:
            cluster_index = np.zeros(len(items))
        return similarity, cluster_index



def plot_document_clusters(words, similarity, cluster_index=None, colors=None, figsize=(20,40) ):
    '''
    Plots words sorted by 'similarity' and colored by 'cluster_index' using 'colors' as mapping from cluster index.
    If 'cluster_index' or 'colors' are None, the plot will use one color for all words
    'words', 'similarity' and 'cluster_index' should be sorted before the use of this nethod 
    '''
    use_color = not cluster_index is None and not colors is None
    x = words
    y = similarity
    color_words = [colors[x] for x in cluster_index] if use_color else None
    plt.figure(figsize=figsize)
    bars = plt.barh(range(len(y)), y, align='center', color=color_words)
    plt.yticks(range(len(x)), list(x))
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=90)
    plt.show()    
