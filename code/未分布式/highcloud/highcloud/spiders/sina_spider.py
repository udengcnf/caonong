#coding:utf-8

import re
import random
from bs4 import BeautifulSoup
import sys
import urllib
import scrapy
# from scrapy.spiders import CrawlSpider
# from scrapy.selector import Selector
# from scrapy.http import Request
from highcloud.sina.items import SinaSocialUser
from selenium import webdriver
import time
class Spider(scrapy.Spider):
    name = 'SinaSpider'
    allowed_domains = ['weibo.cn']
    start_urls = [
            'https://weibo.cn/search/?pos=search',
        ]

    def __init__(self, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)
        self.search_word = kwargs.get('search_word', '中国')
        self.search_type = kwargs.get('search_type', '0') ## 0/搜微博, 1/找人, 2/搜标签

    def start_requests(self):
        search_url = 'https://weibo.cn/search/?pos=search&keyword=' + '重庆' + '&smblog=' + '搜微博'
        print 'search_url  :', search_url
        yield scrapy.http.Request(search_url,  callback=self.parse)

    def parse(self, response):
        s = SinaSocialUser()
        yield s