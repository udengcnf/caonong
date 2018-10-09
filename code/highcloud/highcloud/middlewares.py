# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
from scrapy import signals
from utils.user_agents import agents, chrome_agents
from settings import IPPOOL
# from cookies.twitter_cookies import cookie

class UserAgentMiddleware(object):
    '''
        更换User-Agent
    '''
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers['User-Agent'] = agent

class UserAgentChromeMiddleware(object):
    '''
        更换User-Agent
    '''
    def process_request(self, request, spider):
        agent = random.choice(chrome_agents)
        request.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'

# class CookiesMiddleware(object):
#     '''
#         更换Cookie
#     '''
#     def process_request(self, request, spider):
#         request.cookies = cookie

# class ProxyMiddleware(object):
#
#     def __init__(self, ip=''):
#         self.ip = ip
#     def process_request(self, request, spider):
#         # Set the location of the proxy
#         proxy = random.choice(IPPOOL)
#         request.meta['proxy'] = proxy
#         print '---------------------- ', proxy

class HighcloudSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
