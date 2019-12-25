# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapperItem(scrapy.Item):
    link = scrapy.Field()
    address = scrapy.Field()
    description = scrapy.Field()
    image_url = scrapy.Field()
    owner_name = scrapy.Field()
    owner_contact = scrapy.Field()
    active_search = scrapy.Field()
    pass
