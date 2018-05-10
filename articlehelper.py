from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import xml.sax.saxutils as saxutils
import os
import re
import langid
import io, zipfile
import logging

# I know this code is dirty :(

class RePostprocessor():
    def __init__(self, re_str='<.+?>'):
        self.re_compiled = re.compile(re_str)

    def process(self, text):
        return self.re_compiled.sub('', text)
        
class ArticleHandler(ContentHandler):
    def __init__(self, init_langid = True, line_postprocessor = None):
        ContentHandler.__init__( self)
        self.currentTag = None
        self.series = []
        self.item = None
        if init_langid:
            langid.set_languages(langs = ['en', 'ru', 'uk'])
        if line_postprocessor == None:
            self.line_postprocessor = RePostprocessor().process
        else:
            self.line_postprocessor = line_postprocessor

    def start_item(self):
        self.item = {}
        self.series.append(self.item)

    def clear_item(self):
        self.series.pop()
    
    def set_arrayfield(self, tag, content):
        s = content.strip()
        if s:
            try:
                if tag not in self.item:
                    self.item[tag] = []
                self.item[tag].append(s)
            except:
                logging.exception('Problem with tag {} and content\n{}'.format(tag, s))

    def set_field(self, tag, content):
        s = content.strip()
        if s:
            if tag not in self.item:
                self.item[tag] = s

    def startElement(self, name, attrs):
        if name != 'doc' and self.currentTag != 'body':
            if self.currentTag == None:
                self.currentTag = name 


    def endElement(self,name):
        if name == self.currentTag:
            self.currentTag = None  

    def characters(self, content):                     
        if self.currentTag:
            if self.currentTag in ['tags', 'body']:
                self.set_arrayfield(self.currentTag, content)
            else:
                self.set_field(self.currentTag, content)

    @staticmethod
    def _read_file(h, saxparser, lines, filename = '', lang = None):
        try:
            saxparser.reset()
            h.start_item()
            saxparser.feed('<doc>')
            for line in lines:
                if line.startswith('<body>'):
                    saxparser.feed('<body>')
                if  h.currentTag == 'body':
                    h.set_arrayfield('body', h.line_postprocessor(line))
                else:
                    saxparser.feed(line)
            saxparser.feed('</body>')
            saxparser.feed('</doc>')
            s = '\n'.join(h.item['body'])
            h.set_field('text', s.strip())
            if lang == None:
                lang = langid.classify(s)
                h.set_field('language', lang[0])
            elif type(lang) is str:
                h.set_field('language', lang)
            else:
                raise ValueError('lang must be str or None')
            h.set_field('filename', filename)
            saxparser.close() 
        except:
            logging.exception('Can\'t read file {}'.format(filename))
            h.clear_item()
    
    @staticmethod
    def _make_articlehandler(lang = None, line_postprocessor = None):
        return ArticleHandler(init_langid = lang==None, line_postprocessor = line_postprocessor)
    
    @staticmethod          
    def read_file(filename, lang = None, line_postprocessor = None):
        h = ArticleHandler._make_articlehandler(lang, line_postprocessor = line_postprocessor)
        saxparser = make_parser()
        saxparser.setContentHandler(h)    
        with open(filename, 'r', encoding='utf-8') as f:
            ArticleHandler._read_file(h, saxparser, f.readlines(), filename, lang = lang)  
        return h.series  


    @staticmethod
    def read_directory(root, pattern = '.txt', lang = None, line_postprocessor = None):
        h = ArticleHandler._make_articlehandler(lang, line_postprocessor = line_postprocessor)
        saxparser = make_parser()
        saxparser.setContentHandler(h)
        for path, dirs, files in os.walk(root):
            for file_ in files:
                if file_.endswith(pattern):
                    # print(file_)
                    with open(os.path.join(path, file_), 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        ArticleHandler._read_file(h, saxparser, lines, filename = file_, lang = lang)
        return h.series 

    @staticmethod
    def read_zip(zipfilename, pattern = '.txt', lang = None, line_postprocessor = None):
        h = ArticleHandler._make_articlehandler(lang, line_postprocessor = line_postprocessor)
        saxparser = make_parser()
        saxparser.setContentHandler(h)
        with zipfile.ZipFile(zipfilename) as myzip: 
            for file_ in myzip.namelist():
                if file_.endswith(pattern):
                    # print(file_)
                    with myzip.open(file_, 'r') as f:
                        lines = io.TextIOWrapper(f, encoding='utf-8').readlines()
                        ArticleHandler._read_file(h, saxparser, lines, filename = file_, lang = lang)
        return h.series 

    @staticmethod
    def read_zip_list(zipfilename, filelist, lang = None, line_postprocessor = None):
        '''
        zipfilename: zip file to read
        filelist: a) the name of file where the list of files is stored b) the list of filess to load
        lang: a) None to detect language with langid b) str value (for example 'uk') to asign to 'language' field of the article
        body_postprocessor: method that converts a str value to other str, could be used to clean 'body' data
        '''
        h = ArticleHandler._make_articlehandler(lang, line_postprocessor = line_postprocessor)
        saxparser = make_parser()
        saxparser.setContentHandler(h)
        filelist_ = None
        if type(filelist) is str:
            with open(filelist, 'r', encoding='utf-8') as f:
                filelist_ = f.readlines()
        else: filelist_ = filelist
        with zipfile.ZipFile(zipfilename) as myzip: 
            for file_ in filelist_:
                filename = file_.strip()
                try:
                    with myzip.open(filename, 'r') as f:
                        lines = io.TextIOWrapper(f, encoding='utf-8').readlines()
                        ArticleHandler._read_file(h, saxparser, lines, filename = filename, lang = lang)
                except:
                    logging.exception('Can\'t read file {}'.format(filename))
        return h.series 



def check_paragraph_has_letters(p):
    for x in p:
        if x.isalpha():
            return True
    return False

def map_category_default(doc):
    return doc['autocategory']


def map_category_4(cat):
    categories = ['news', 'blog', 'columns']
    other_category = 'article'
    return cat if cat in categories else other_category

def map_category(cat, categories, other_category):
    '''
    cat - category to map
    categories - list of allowed categories, if cat does not belong to this list, other_category will be assigned
    '''
    # categories = ['news', 'blog', 'columns']
    # other_category = 'article'
    return cat if cat in categories else other_category

def map_rename_category(cat, categories, other_category):
    '''
    cat - category to map
    categories - list of allowed categories, if cat does not belong to this list, other_category will be assigned
    rename_categories - dict to rename categories
    '''
    return categories[cat] if cat in categories else other_category

def map_category_4_doc(doc):
    return map_category_4(doc['autocategory'])
    # categories = ['news', 'blog', 'columns']
    # other_category = 'article'
    # cat = doc['autocategory']
    # return cat if cat in categories else other_category

def map_category_ukrpravda(doc):
    url = doc['url']
    cat = doc['autocategory']
    other_category = 'other'
    if cat != 'blog':
        if url.startswith('https://www.pravda.com.ua') or url.startswith('http://vybory.pravda.com.ua'):
            cat = map_category(cat, ['news', 'columns', 'articles'], other_category)
        elif url.startswith('https://www.eurointegration.com.ua'):
            cat = map_rename_category(cat, {'news':'news', 'experts':'columns', 'interview':'articles', 'articles':'articles'}, 
                other_category)
        elif url.startswith('https://www.epravda.com.ua'):
            cat = map_rename_category(cat, {'news':'news', 'columns':'columns', 'publications':'articles'}, 
                other_category)
        elif url.startswith('http://life.pravda.com.ua'):
            cat = map_category(cat, ['columns'], 'articles')
        else:
            cat = other_category
    return cat
    
def map_category_bruk(doc):
    # return map_rename_category(doc['id'], {'A':'press', 'C':'prof_science', 'D':'prof_science', 'F':'prof_science', 'G':'prof_science', 'H':'prof_science', 'I':'fiction'}, 'other')
    return map_rename_category(doc['id'], {'A':'press', 'C':'prof_science', 'F':'prof_science', 'G':'prof_science', 'H':'prof_science', 'I':'fiction'}, 'other')
    

def map_paragraphs(articles, map_category = map_category_default, check_paragraph = check_paragraph_has_letters):
    '''
    Converts an array of articles to paragraphs array
    '''
    paragraphs = []
    for doc in articles:
        filename  = ''
        try:
            filename = doc['filename']
        except:
            logging.exception('Can\'t get the filename of the article')
        try:
            category = map_category(doc)
            for p in doc['body']:
                if check_paragraph(p):
                    d = {   'category': category,
                            'doc': doc,
                            'text': p }
                    paragraphs.append(d)
        except:
            logging.exception('Error with ' + filename)
    return paragraphs
