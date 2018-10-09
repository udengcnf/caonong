# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from highcloud.utils import utils_items

class HighcloudItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class TwitterSocialUser(utils_items.SocialUser):
    pass

class TwitterSocialContent(utils_items.SocialContent):
    pass

class TwitterSocialTrans(utils_items.SocialTrans):
    pass

class TwitterSocialComment(utils_items.SocialComment):
    pass