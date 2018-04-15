# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from news.items import NewsItem
import re


class UkrpravdablogsSpider(scrapy.Spider):
    name = 'ukrpravdablogs'
    allowed_domains = ['blogs.pravda.com.ua']
    start_urls = ['https://blogs.pravda.com.ua/']
    default_url = 'https://blogs.pravda.com.ua'
    

    def parse(self, response):
        blogs = response.css('div.holder1 > a::attr(href)')
        for x in blogs:
            url = UkrpravdablogsSpider.default_url + x.extract()
            yield scrapy.Request(url, callback=self.parse_blog)
        for a in response.css('div.fblock > ul.list.tl > li > a::attr(href)'):
            url = UkrpravdablogsSpider.default_url + a.extract()
            yield scrapy.Request(url, callback=self.parse)            

    def parse_blog(self, response):
        l = ItemLoader(item=NewsItem(), response=response)
        l.add_value('url', response.url)
        cat = 'blog'
        l.add_css('title', 'div.bpost > h1::text')
        l.add_css('date', 'div.bpost > span.bdate::text')
        l.add_css('authors', 'div.bpost > span.bauthor > a::text')
        l.add_css('authors_description', 'div.bpost > span.description::text')
        l.add_value('autocategory', cat)
        for bb in response.css('div.bpost > p'):
            l.add_value('text', bb.extract())
        text = ''
        b = response.css('div.bpost')
        for bb in b.xpath('child::node()'):
            s = bb.extract()
            if s.startswith('<a') or s.startswith('<br') or  not s.startswith('<'):
                text = text + s 
        l.add_value('text', '<p>' + text + '</p>')
        tags = []
        for t in response.css('div.bpost > ul.list2.fr > li > a::text'):
            tags.append([t.extract()])
        l.add_value('tags_array', tags)
        item = l.load_item()
        item['text'] = item['text']
        # print(item)
        return item
