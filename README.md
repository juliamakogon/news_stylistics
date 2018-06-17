# Stylistic features and genre detection for Ukrainian
This project was completed as an assignment within "Data Science. Natural Language Processing" course in Projector, Kyiv (https://github.com/vseloved/prj-nlp)

Classifier achieves averaged accuracy of 70.9% / 85.22% (paragraphs/documents) for texts from BrUK corpus and 61.07% / 86.67% (paragraphs/documents) for news/articles/columns/blogs from pravda.com.ua using mixed N-gram approach. Words are treated as lemmas if they belong to the frequent words list, or are parts of stylistic bigrams. Punctuation is treated as is. POS tags are used for other words. 
To separate lexical N-grams from stylistic, we use the minimum distance from N-gram vector to vectors from document meaning cluster. Mean of Lex2Vec word embeddings is used as N-gram vector.

## Data
Data used for training:
https://github.com/brown-uk/corpus BrUK, Braun corpus for Ukrainian, train/test dataset split can be found in files data/bruk_train.txt and data/bruk_test.txt

https://www.pravda.com.ua/ 3000 news, articles, columns, and blogs from @ukrpravda, train/test dataset split can be found in files data/news_train.txt and data/news_test.txt. data/www_pravda_com_ua_news_2017_10_8_7157642.txt is an example of a pseudo-XML file to store downloaded news articles. 

UberText corpus http://lang.org.ua/en/corpora/ was used to get frequent words statistics: data/freq_words.txt. 
Lex2vec embeddings for lemmatized words could be achieved from lang_uk website http://lang.org.ua/en/models/#anchor4. 

data/ner.txt is a vocabulary for a simple NER model used.

data/bruk_bigrams.txt and data/news_bigrams.txt contain saved stylistic bigrams.

## Dependencies

## Scripts 
| File | Purpose |
| --- | --- |
| bayes_bruk.ipynb | Calculations for BrUK | 
| bayes_news.ipynb | Calculations for ukrpravda |
| demo.ipynb | Demonstration of trained genre classifiers | 







