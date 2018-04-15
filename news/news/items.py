# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    authors = scrapy.Field()
    authors_description = scrapy.Field()
    autocategory = scrapy.Field()
    text = scrapy.Field()
    tags_array = scrapy.Field()
    pass
