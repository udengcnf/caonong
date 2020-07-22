# -*- coding: utf-8 -*-
import sys
import json
import logging
from highcloud.items import CnnSocialContent,CnnSocialUser
from highcloud.scrapy_redis.spiders import RedisSpider


class CnnSubordinateSpider(RedisSpider):
    name = 'CnnSubordinateSpider'
    allowed_domains = ['edition.cnn.com']
    main_name = 'CnnMainSpider'

    custom_settings = {
        'ROBOTSTXT_OBEY' : False,
        'SCHEDULER' : "highcloud.scrapy_redis.scheduler.Scheduler",
        'DUPEFILTER_CLASS' : "highcloud.scrapy_redis.dupefilter.RFPDupeFilter",

        'SCHEDULER_PERSIST':True,
        'SCHEDULER_QUEUE_CLASS':'highcloud.scrapy_redis.queue.FifoQueue',
        # 'SCHEDULER_IDLE_BEFORE_CLOSE' : 5,

        # 'ITEM_PIPELINES' : {
        #       'highcloud.scrapy_redis.pipelines.RedisPipeline': 300,
        #  },
    }


    def __init__(self, task_id='task_id', *args, **kwargs):
        super(CnnSubordinateSpider, self).__init__(*args, **kwargs)

        self.task_id=task_id
        self.redis_key=self.main_name+':'+task_id+':start_urls'


    def getUserName(self,name):
        if name:
            hasBy=name.lower().find('by ')
            if hasBy>-1:
                name = name[hasBy+3:]
            if ',' in name:
                name=name[0:name.index(',')]
            return name
        else:
            return ''

    def parse(self, response):
        try:
            search_json = json.loads(response.text)
            if 'result' in search_json and search_json['result']:
                result = search_json['result']
                for data in result:
                    content_item = CnnSocialContent()
                    user_item = CnnSocialUser()
                    content_item['id'] = data.get('_id', '')
                    content_item['user'] = data.get('byLine', '')
                    content_item['url'] = data.get('url', '')
                    content_item['created_at'] = data.get('firstPublishDate', '')
                    content_item['text'] = data.get('body', '')
                    content_item['image'] = data.get('thumbnail', '')

                    if content_item['user']:
                        user_item['id'] = user_item['name'] = self.getUserName(content_item['user'])
                        yield user_item
                    yield content_item
            else:
                logging.error(' ===== cnn_spider.Spider.parse no data ===== ')
        except :
            logging.error('cnn_spider.Spider.parse Exception has occur %s' % str(sys.exc_info()[1]))
