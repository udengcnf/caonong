#coding:utf-8

import scrapy
from highcloud.sina.items import SinaSocialUser

class BaseSpider(scrapy.Spider):
    name = 'BaseSpider'
    allowed_domains = ['weibo.cn']
    start_urls = [
            'https://weibo.cn/search/?pos=search',
        ]

    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        ## 获取命令行参数 scrapy crawl -a search_word=chongqing
        self.search_word = kwargs.get('search_word', '中国')
        self.search_type = kwargs.get('search_type', '0') ## 0/搜微博, 1/找人, 2/搜标签

    def start_requests(self):
        search_url = 'https://weibo.cn/search/?pos=search&keyword=' + '重庆' + '&smblog=' + '搜微博'
        yield scrapy.http.Request(search_url,  callback=self.parse)

    def parse(self, response):
        s = SinaSocialUser()
        yield s