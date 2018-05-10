'''
Contains functions to help with classification and result interpretation
'''
import logging
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import pairwise_distances
import numpy as np


def show_top_features(vectorizer, clf, i_label, n=20, joiner = '\n'):
    '''
    Shows top n features for the category indexed as i_label
    '''
    feature_names = vectorizer.get_feature_names()
    coefs_with_fns = sorted(zip(clf.coef_[i_label], feature_names), reverse=True)
    top = coefs_with_fns[:n]
    return joiner.join(['{}: {}'.format(x[1], x[0]) for x in top])
    

def show_all_top_features(vectorizer, clf, n=20, joiner = '\n'):
    '''
    Shows top n features for all the category of classifier clf
    '''
    def print_cat(class_label, vectorizer, clf, i, n, joiner, sep =''):
        print(class_label, ':\n', show_top_features(vectorizer, clf, i, n, joiner), sep='')

    if clf.classes_.shape[0] == clf.coef_.shape[0]:
        for i, class_label in enumerate(clf.classes_):
            print_cat(class_label, vectorizer, clf, i, n, joiner)
            # print(class_label, ':\n', show_most_informative_features(vectorizer, clf, i, n, joiner), sep='')
    else:
        for i in range(clf.coef_.shape[0]):
             print_cat(i, vectorizer, clf, i, n, joiner)
            # print(i, ':\n', show_most_informative_features(vectorizer, clf, i, n, joiner), sep='')  


def print_clf_classes_distances(clf, metric = 'manhattan', num_format = '{0:.4f}'):
    '''
    Prints a table with with distances between classifier clf features for each category
    '''
    m = pairwise_distances(clf.coef_, metric = metric)
    m = m / np.max(m)
    labels = clf.classes_
    w = np.max([len(x) for x in labels])
    print(' '.join([x.ljust(w) for x in [''] + list(labels)]))
    for i in range(len(labels)):
        print(labels[i].ljust(w), ' '.join(['{0:.4f}'.format(x).ljust(w) for x in m[i] ]))


def plot_clf_classes_distances(clf, metric = 'manhattan', num_format = '{0:.4f}'):
    '''
    Shows a table with with distances between classifier clf features for each category as a heatmap using matshow
    '''
    m = pairwise_distances(clf.coef_, metric = metric)
    m = m / np.max(m)
    labels = clf.classes_
    fig, ax = plt.subplots()
    cax = ax.matshow(m, aspect="auto")
    ax.set_xticklabels([''] + list(labels))
    ax.set_yticklabels([''] + list(labels))
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=90)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            c = m[j,i]
            ax.text(i, j, num_format.format(c), va='center', ha='center')
    plt.show()