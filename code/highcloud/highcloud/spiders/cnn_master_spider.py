# -*- coding: utf-8 -*-
import scrapy,json
import sys
import logging
from highcloud.utils.utils_redis import RedisUtils

class CnnMasterSpider(scrapy.Spider):
    name = 'CnnMasterSpider'
    allowed_domains = ['edition.cnn.com']
    size='1'
    status_count = 0

    def __init__(self, search_word='China', *args, **kwargs):
        # print 'kkkkkkkkkk===',search_word

        super(CnnMasterSpider, self).__init__(*args, **kwargs)

        # self.search_word = kwargs.get('search_word',  'លោកអូបាម៉ា') ## 'លោកអូបាម៉ា'
        self.task_id = kwargs.get('task_id',  'task_id')
        self.max_count = int(kwargs.get('max_count', '5'))

        self.redis_key = self.name+':'+self.task_id+ ':start_urls'
        self.start_urls = ['https://search.api.cnn.io/content?q='+ search_word +'&size='+self.size+'&from=0']
        print 'starturl:',self.start_urls
        self.next_url = 'https://search.api.cnn.io/content?q='+ search_word +'&size='+self.size+'&from={0}'

    def parse(self, response):
        try:
            search_json = json.loads(response.text)
            if 'result' in search_json and search_json['result']:
                RedisUtils.redis_key_push(self.redis_key, response.url)
                self.status_count+=1
                logging.info('redis_key: %s has push url: %s' % (self.redis_key, response.url) )
            else:
                return

            if self.status_count >= self.max_count:
                print '-----------------------------   return ',
                self.status_count = 0
                return

            next_index = search_json['meta']['end']
            print 'next page',self.next_url.format(next_index)
            if next_index:
                yield scrapy.Request(self.next_url.format(next_index) , callback=self.parse, dont_filter=True)

        except Exception as e:
            print 'exception:',e
            logging.error('cnn_master Exception has occur %s' % str(sys.exc_info()[1]))
        finally:
            pass