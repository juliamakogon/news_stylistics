from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import xml.sax.saxutils as saxutils
import os
import re
import langid
import io, zipfile

# I know this code is dirty :(
class ArticleHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__( self)
        self.currentTag = None
        self.series = []
        self.item = None
        langid.set_languages(langs = ['en', 'ru', 'uk'])
        pass

    def start_item(self):
        self.item = {}
        self.series.append(self.item)
    
    def set_arrayfield(self, tag, content):
        s = content.strip()
        if s:
            if tag not in self.item:
                self.item[tag] = []
            self.item[tag].append(s)

    def set_field(self, tag, content):
        s = content.strip()
        if s:
            if tag not in self.item:
                self.item[tag] = s

    def startElement(self, name, attrs):
        if name != 'doc':
            if self.currentTag == None:
                self.currentTag = name 


    def endElement(self,name):
        if name == self.currentTag:
            self.currentTag = None  

    def characters(self, content):                     
        if self.currentTag:
            if self.currentTag in ['tags']:
                self.set_arrayfield(self.currentTag, content)
            else:
                self.set_field(self.currentTag, content)

    @staticmethod
    def _read_file(h, saxparser, lines, filename = ''):
        try:
            saxparser.reset()
            h.start_item()
            saxparser.feed('<doc>')
            for line in lines:
                if h.currentTag == 'body' and not line.startswith('</body>'):  
                    h.set_arrayfield('body', line) 
                else:
                    saxparser.feed(line)
            saxparser.feed('</doc>')
            s = '\n'.join(h.item['body'])
            h.set_field('text', s.strip())
            lang = langid.classify(s)
            h.set_field('language', lang[0])
            saxparser.close() 
        except Exception as e:
            print(filename, ':',  e) 
    
    @staticmethod          
    def read_file(filename):
        h = ArticleHandler()
        saxparser = make_parser()
        saxparser.setContentHandler(h)    
        with open(filename, 'r', encoding='utf-8') as f:
            ArticleHandler._read_file(h, saxparser, f.readlines(), filename)  
        return h.series  


    @staticmethod
    def read_directory(root, pattern = '.txt'):
        h = ArticleHandler()
        saxparser = make_parser()
        saxparser.setContentHandler(h)
        for path, dirs, files in os.walk(root):
            for file_ in files:
                if file_.endswith(pattern):
                    # print(file_)
                    with open(os.path.join(path, file_), 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        ArticleHandler._read_file(h, saxparser, lines, filename = file_)
        return h.series 

    @staticmethod
    def read_zip(zipfilename, pattern = '.txt'):
        h = ArticleHandler()
        saxparser = make_parser()
        saxparser.setContentHandler(h)
        with zipfile.ZipFile(zipfilename) as myzip: 
            for file_ in myzip.namelist():
                if file_.endswith(pattern):
                    # print(file_)
                    with myzip.open(file_, 'r') as f:
                        lines = io.TextIOWrapper(f, encoding='utf-8').readlines()
                        ArticleHandler._read_file(h, saxparser, lines, filename = file_)
        return h.series 
