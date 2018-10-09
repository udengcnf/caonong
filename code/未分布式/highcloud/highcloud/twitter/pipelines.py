# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
import logging
from highcloud.utils.utils_redis import RedisUtils
from items import TwitterSocialUser, TwitterSocialTrans, TwitterSocialContent, TwitterSocialComment


class HighcloudPipeline(object):
    def process_item(self, item, spider):
        print 'HighcloudPipeline ', dict(item)
        return item

class TwitterPipeline(object):

    def process_item(self, item, spider):
        '''
            根据item类型做入库处理
        '''

        try:
            if isinstance(item, TwitterSocialUser):
                RedisUtils.item_insert(item)
                logging.info('TwitterPipeline.process_item TwitterSocialUser [%s] has insert into redis' % dict(item))
            elif isinstance(item, TwitterSocialContent):
                RedisUtils.item_insert(item)
                logging.info('TwitterPipeline.process_item TwitterSocialContent [%s] has insert into redis' % dict(item))
        except Exception as e:
            logging.error('TwitterPipeline.process_item Exception has occur %s' % str(sys.exc_info()[1]))
        finally:
            return item
