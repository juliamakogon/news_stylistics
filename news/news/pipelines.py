# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from bs4 import BeautifulSoup
import os
import re

def get_value(item, key):
    s = ''
    if key in item:
        s = item[key][0]
    return s

def convert_to_xml(item):
    s = ''
    s = s + '<url>' + get_value(item, 'url') + '</url>\n'
    s = s + '<title>' + get_value(item, 'title') + '</title>\n'
    s = s + '<date>' + get_value(item, 'date') + '</date>\n'
    s = s + '<authors>' + get_value(item, 'authors') + '</authors>\n'
    s = s + '<authors_description>' + get_value(item, 'authors_description') + '</authors_description>\n'
    s = s + '<autocategory>' + get_value(item, 'autocategory') + '</autocategory>\n'
    t = ''
    if 'tags_array' in item:
        for tt in item['tags_array']:
            t = t + '<tag>' + tt[0] + '</tag> '
    s = s + '<tags>' + t + '</tags>\n'
    if 'text' in item:    
        s = s + '<body>\n' + item['text'] + '\n</body>\n'
    #s = '<page>\n' + s + '</page>'
    return s

def remove_punctuation(s):
    return re.sub(r'\W', '_', s)

def check_path(url, category, create_dir = False):
    sitedir = remove_punctuation(re.findall(r'//(.+?)/', url)[0])
    directory = os.path.join(sitedir, category)
    fname = remove_punctuation(re.findall(r'//(.+)/', url)[0])+'.txt'
    fullname = os.path.join(directory, fname)
    if create_dir:
        if not os.path.exists(sitedir):
            os.makedirs(sitedir)
        if not os.path.exists(directory):
            os.makedirs(directory)
    return fullname


class NewsPipeline(object):
    def open_spider(self, spider):
        self.file = open(spider.name + '_list.csv', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        cat = get_value(item, 'autocategory')
        if not cat or not 'text' in item:
            spider.log('Warning: nothing to save from '+get_value(item, 'url'))
            return item
        # convert to clean text saving paragraphs
        s = ' '.join(item['text'])
        s = s.replace('<br><br>', '</p><p>')
        bs = BeautifulSoup(s)
        text = ''
        joiner = ''
        for x in bs.find_all('p'):
            text = joiner.join([text, x.text])
            joiner = '\n'
        item['text'] = text
        #save to list
        line = '\t'.join([cat, get_value(item, 'url'), get_value(item, 'title'), '']) + '\n'
        self.file.write(line)
        #save to xml
        fname = check_path(get_value(item, 'url'), cat, True)
        with open(fname, 'w', encoding='utf-8') as f:
            s = convert_to_xml(item)
            f.write(s)
        return item
