# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from news.items import NewsItem
import re


class UkrpravdaSpider(scrapy.Spider):
    name = 'ukrpravda'
    default_url = r'https://www.pravda.com.ua'
    #allowed_domains = ['https://www.pravda.com.ua/']
    start_urls = [r'https://www.pravda.com.ua/archives/date_08042018/']
    category_re = re.compile(r'//.+?/(.+?)/')

    @staticmethod
    def get_autocategory(url):
        cat = UkrpravdaSpider.category_re.findall(url)[0]
        return cat

    @staticmethod
    def norm_url(url):
        if not url.startswith('http'):
            return UkrpravdaSpider.default_url + url
        return url

    def parse(self, response):
        news = response.css('div.news.news_all > div.article > div.article__title a::attr(href)')
        columns = response.css('div.columns-content > div.article_column a::attr(href)')
        articles = response.css('div.articles.articles_all > div.article.article_list a::attr(href)')
        a = []
        [a.extend(x) for x in [news, columns, articles]]
        for x in a:
            url = x.extract()
            url = UkrpravdaSpider.norm_url(url)
            self.log(url)
            if url.startswith(r'https://www.eurointegration.com.ua'):
                yield scrapy.Request(url, callback=self.parse_eurointegration)
            elif url.startswith(r'http://life.pravda.com.ua'):
                yield scrapy.Request(url, callback=self.parse_life)
            else:
                yield scrapy.Request(url, callback=self.parse_news)
        # navigation
        for a in response.css('div.archive-navigation > a.button::attr(href)'):
            url = UkrpravdaSpider.norm_url(a.extract())
            yield scrapy.Request(url, callback=self.parse)


    def parse_news(self, response):
        post = response.css('div.post')
        l = ItemLoader(item=NewsItem(), response=response)
        l.add_value('url', response.url)
        cat = UkrpravdaSpider.get_autocategory(response.url)
        l.add_css('title', 'h1.post_news__title::text')
        l.add_css('date', 'div.post_news__date::text')
        l.add_css('authors', 'post_news__author::text')
        l.add_css('text', 'div.post_news__text > p')
        l.add_css('text', 'div.post__text')
        l.add_value('autocategory', cat)
        tags = []
        for t in post.css('span.post__tags__item'):
            tags.append(t.xpath('a/text()').extract())
        l.add_value('tags_array', tags)
        return l.load_item()

    def parse_eurointegration(self, response):
        l = ItemLoader(item=NewsItem(), response=response)
        l.add_value('url', response.url)
        cat = UkrpravdaSpider.get_autocategory(response.url)
        l.add_css('title', 'div.rpad > h1.title::text')
        l.add_css('date', 'div.rpad > span.dt2::text')
        l.add_css('authors', 'div.rpad > span.dt2 > b::text')
        l.add_css('text', 'div.rpad > div.text > p')
        l.add_value('autocategory', cat)
        item = l.load_item()
        # print(item)
        return item

    def parse_life(self, response):
        l = ItemLoader(item=NewsItem(), response=response)
        l.add_value('url', response.url)
        cat = UkrpravdaSpider.get_autocategory(response.url)
        l.add_css('title', 'page-heading::text')
        l.add_css('date', 'div.article-flex-wrap > div > div.statistic-bottom-block.statistic-top-block > div.data-block > span::text')
        l.add_css('authors', 'div > div.sidebar-autor-block > div > a > span.autor-name::text')
        l.add_css('authors_description', 'div > div.sidebar-autor-block > div > a > span.autor-desctiption::text')
        l.add_css('text', 'article > p')
        l.add_value('autocategory', cat)
        item = l.load_item()
        # print(item)
        return item
