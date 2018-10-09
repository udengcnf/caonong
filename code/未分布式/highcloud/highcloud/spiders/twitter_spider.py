#coding:utf-8

import re
import logging
import random
from bs4 import BeautifulSoup
import sys
import urllib
import scrapy
# from highcloud.items import SocialUser
# from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from base_spider import BaseSpider
from highcloud.twitter.items import TwitterSocialUser, TwitterSocialContent, TwitterSocialComment, TwitterSocialTrans
from highcloud.twitter.cookies import cookie
from selenium import webdriver
import time
import requests

class Spider(BaseSpider):
    name = 'TwitterSpider'
    allowed_domains = ['twitter.com']
    start_urls = [
            'https://mobile.twitter.com/search',
        ]

    def __init__(self, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)
        self.http_site = 'https://mobile.twitter.com'
        print args, kwargs

    def start_requests(self):
        search_url = 'https://mobile.twitter.com/search?q=' + 'ប្រទេសចិន' + '&src=typd'
        yield scrapy.http.Request(search_url,  callback=self.parse_contents)

    def parse_contents(self, response):
        print '---------------------------------------------------  parse_contents'
        try:
            soup = BeautifulSoup(response.text)
            contents = soup.find(class_='timeline').contents

            for content in contents:
                if not hasattr(content,'table'):
                    continue
                ts_content = TwitterSocialContent()
                href = content.attrs['href']
                ts_content['id'] = re.findall(re.compile(r'status/(\d+)\?'), href)[0] ## 内容ID
                ts_content['created_at'] = content.find(class_='tweet-header ').find(class_='timestamp').text.strip() ## 发布时间
                ts_content['text'] = content.find(class_='tweet-container').td.div.div.text ## 正文内容
                print dict(ts_content)
                yield ts_content
                yield Request(url = self.http_site + content.find(class_='tweet-header ').find(class_='user-info').a.attrs['href'], callback=self.parse_users, dont_filter=True)

        except Exception as e:
            logging.error('twitter_spider.Spider.parse_contents Exception has occur %s' % str(sys.exc_info()[1]))
        finally:
            pass

    def parse_users(self, response):
        print '---------------------------------------------------  parse_users'
        try:
            ts_user = TwitterSocialUser()
            soup = BeautifulSoup(response.text)

            name = soup.find(class_='profile-details').find(class_='user-info').find(class_='username').text.strip() ## 用户名
            ts_user['id'] = ts_user['name'] = name.split('\n')[-1]  ## 用户ID/暂用用户名
            ts_user['image'] = soup.find(class_='profile-details').find(class_='avatar').img.attrs['src'] ## 头像地址
            ts_user['nick'] = soup.find(class_='profile-details').find(class_='user-info').find(class_='fullname').text.strip() ## 昵称
            ts_user['url'] = self.http_site + '/' + ts_user['name']

            for us in soup.find(class_='profile-stats').find_all(class_=re.compile('^stat')):
                if re.match(re.compile(r'\s*(\d+)\s*Tweets\s*'), us.text):
                    ts_user['status'] = re.match(re.compile(r'\s*(\d+)\s*Tweets\s*'), us.text).groups()[0]
                if re.match(re.compile(r'\s*(\d+)\s*Following\s*'), us.text):
                    ts_user['following'] = re.match(re.compile(r'\s*(\d+)\s*Following\s*'), us.text).groups()[0]
                if re.match(re.compile(r'\s*(\d+)\s*Followers\s*'), us.text):
                    ts_user['followers'] = re.match(re.compile(r'\s*(\d+)\s*Followers\s*'), us.text).groups()[0]

            yield ts_user

        except Exception as e:
            logging.error('twitter_spider.Spider.parse_contents Exception has occur %s' % str(sys.exc_info()[1]))
        finally:
            pass