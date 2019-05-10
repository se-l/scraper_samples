# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
# <image_id> is the SHA1 hash of the image url

import scrapy


class SampleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()
