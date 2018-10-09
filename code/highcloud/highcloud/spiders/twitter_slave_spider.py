#coding:utf-8

import re
import sys
import time
import scrapy
import logging
import random
from bs4 import BeautifulSoup
from scrapy.http import Request
from highcloud.utils.commons import Utils
from highcloud.utils.utils_redis import RedisUtils
from highcloud.scrapy_redis.spiders import RedisSpider
from highcloud.items import TwitterSocialUser, TwitterSocialContent, TwitterSocialComment, TwitterSocialTrans

class Spider(RedisSpider):
    name = 'TwitterSlaveSpider'
    allowed_domains = ['twitter.com']

    custom_settings = {
        'SCHEDULER':"highcloud.scrapy_redis.scheduler.Scheduler",
        'DUPEFILTER_CLASS':"highcloud.scrapy_redis.dupefilter.RFPDupeFilter",

        'SCHEDULER_PERSIST':True,
        'SCHEDULER_QUEUE_CLASS':'highcloud.scrapy_redis.queue.FifoQueue',

        'DOWNLOADER_MIDDLEWARES':{
            "highcloud.middlewares.UserAgentChromeMiddleware": 401,
            # 'highcloud.middlewares.ProxyMiddleware': 125,
        },
    }

    def __init__(self, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)
        ## 获取命令行参数
        self.task_id = kwargs.get('task_id', 'task_id')
        self.redis_key = 'TwitterMasterSpider:%s:start_urls' % self.task_id

    def parse(self, response):
        print '---------------------------------------------------twitter  parse_contents'
        try:
            soup = BeautifulSoup(response.text)

            ts_content = TwitterSocialContent()
            ts_content['id'] = response.url.split('twitter.com/')[-1] ## 内容ID
            ts_content['user'] = response.url.split('/')[-3] ## 用户ID
            ts_content['created_at'] = soup.find(class_='client-and-actions').text.strip() ## 发布时间
            text = soup.find(class_='js-tweet-text-container').p.text.strip() ## 正文内容
            ts_content['text'] = text.split('pic.twitter.com')[0]

            ts_content['url'] = response.url ## 链接地址
            try:
                image_list = []
                image_contents = soup.find(class_='permalink-inner permalink-tweet-container').find(class_='AdaptiveMediaOuterContainer').find_all(class_='AdaptiveMedia-photoContainer js-adaptive-photo ')
                for image in image_contents:
                    try:
                        image_list.append(image.attrs['data-image-url'])
                    except:
                        pass
            except:
                pass
            finally:
                ts_content['image'] = image_list ## 图片地址列表


            t_id = response.url.split('/')[-1]
            ## 评论数
            replay = soup.find(id='profile-tweet-action-reply-count-aria-' + t_id).text.split()[0]
            ts_content['comments_count'] = '0' if replay == 'replies' else replay
            ## 转发数
            retweet = soup.find(id='profile-tweet-action-retweet-count-aria-' + t_id).text.split()[0]
            ts_content['reposts_count'] = '0' if retweet == 'retweets' else retweet
            ## 点赞数
            like = soup.find(id='profile-tweet-action-favorite-count-aria-' + t_id).text.split()[0]
            ts_content['like_count'] = '0' if like == 'likes' else like
            yield ts_content
            time.sleep(2)
            yield Request(url = response.url.split('/status')[0], callback=self.parse_users, dont_filter=True)
        except Exception as e:
            logging.error('twitter_spider.Spider.parse_contents Exception has occur %s' % str(sys.exc_info()[1]))
        finally:
            pass

    def parse_users(self, response):
        print '---------------------------------------------------twitter  parse_users'
        try:
            soup = BeautifulSoup(response.text)
            ts_user = TwitterSocialUser()

            ts_user['url'] = response.url
            ts_user['id'] = response.url.split('/')[-1]
            ts_user['name'] = response.url.split('/')[-1]
            ts_user['nick'] = soup.find(class_='ProfileHeaderCard-nameLink u-textInheritColor js-nav').text.strip()
            ts_user['image'] = soup.find(class_='ProfileAvatar-image ').attrs['src']
            ts_user['province'] = soup.find(class_='ProfileHeaderCard-locationText u-dir').text.strip()
            ts_user['description'] = soup.find(class_='ProfileHeaderCard-bio u-dir').text.strip()
            try:
                ts_user['personal_site'] = soup.find(class_='ProfileHeaderCard-urlText u-dir').text.strip()
            except:pass
            ts_user['status'] = soup.find(class_='ProfileNav-item ProfileNav-item--tweets is-active').text.split()[-1]
            ts_user['following'] = soup.find(class_='ProfileNav-item ProfileNav-item--following').text.split()[-1]
            ts_user['followers'] = soup.find(class_='ProfileNav-item ProfileNav-item--followers').text.split()[-1]
            ts_user['favourites'] = soup.find(class_='ProfileNav-item ProfileNav-item--favorites').text.split()[-1]
            ts_user['create_at'] = soup.find(class_='ProfileHeaderCard-joinDateText js-tooltip u-dir').text.strip()

            yield ts_user
            time.sleep(2)

        except Exception as e:
            logging.error('twitter_spider.Spider.parse_contents Exception has occur %s' % str(sys.exc_info()[1]))
        finally:
            pass