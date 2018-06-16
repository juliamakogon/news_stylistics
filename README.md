# Stylistic features and genre detection for Ukrainian
This project was completed as an assignment within "Data Science. Natural Language Processing" course in Projector, Kyiv (https://github.com/vseloved/prj-nlp)

## Data
Data used for training:
https://github.com/brown-uk/corpus BrUK, Braun corpus for Ukrainian, train/test dataset split can be found in files data/bruk_train.txt and data/bruk_test.txt

https://www.pravda.com.ua/ 3000 news, articles, columns, and blogs from @ukrpravda, train/test dataset split can be found in files data/news_train.txt and data/news_test.txt. data/www_pravda_com_ua_news_2017_10_8_7157642.txt is an example of pseudo-XML file to store downloaded news articles. 

UberText corpus http://lang.org.ua/en/corpora/ was used to get frequent words statistics: data/freq_words.txt. 
Lex2vec embeddings for lemmatized words could be achieved from lang_uk website http://lang.org.ua/en/models/#anchor4 

data/ner.txt is a vocabulary for a simple NER model used.

data/bruk_bigrams.txt and data/news_bigrams.txt contain stylistic bigrams, produced by <><><><>



