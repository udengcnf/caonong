#coding:utf-8

import re
import sys
import time
import scrapy
import logging
import random
from bs4 import BeautifulSoup
from scrapy.http import Request
from highcloud.cookies.twitter_cookies import cookie
from highcloud.utils.utils_redis import RedisUtils
from highcloud.items import TwitterSocialUser

class Spider(scrapy.Spider):
    name = 'TwitterMainSpider'
    allowed_domains = ['www.twitter.com']
    start_urls = [
            'https://www.twitter.com',
    ]
    status_count = 0

    def __init__(self, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)
        ## 获取命令行参数
        self.task_id = kwargs.get('task_id', 'task_id')
        self.twitter_id = kwargs.get('twitter_id',  'KwokMiles')
        self.redis_key = '%s:%s:start_urls' % (self.name, self.task_id)
        self.user_site = 'https://twitter.com' + '/' + self.twitter_id
        self.http_site = 'https://twitter.com'
        self.mobile_site = 'https://mobile.twitter.com'

    def start_requests(self):
        yield Request(self.user_site, callback = self.parse_contents)

    def parse_contents(self, response):
        print '---------------------------------------------------  parse_contents'
        try:
            soup = BeautifulSoup(response.text)
            try:
                contents = soup.find(class_='timeline').contents
                ## 获取每条推文的链接地址
                for content in contents:
                    href = None
                    try:
                        if content.attrs['class'] == ['tweet','']:
                            href = self.http_site + content.attrs['href'].split('?p=v')[0]
                            RedisUtils.redis_key_push(self.redis_key, href)
                            logging.info('redis_key: %s has push url: %s' % (self.redis_key, href))
                    except:
                        pass

                    if href:
                        self.status_count += 1
                        logging.info('=============  %s: %s [%s]' % (self.twitter_id, self.status_count, href))
                        # if self.status_count >= 100:
                        #     print '-----------------------------   return ',
                        #     self.status_count = 0
                        #     return

                time.sleep(5)
                try:
                    next_page = self.mobile_site + soup.find(class_='w-button-more').a.attrs['href']
                    if next_page:
                        yield Request(next_page, callback=self.parse_contents, dont_filter=True)
                except:
                    logging.info('=============  [%s] get tweet finished  ===============' % self.user_site)
            except:
                logging.warning('[%s] no content' % self.user_site)

        except:
            logging.error('twitter_main_spider.Spider.parse_contents Exception has occur %s' % str(sys.exc_info()[1]))
        finally:
            pass
