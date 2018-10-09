# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
import logging
from highcloud.utils.utils_redis import RedisUtils
from items import TwitterSocialUser, TwitterSocialTrans, TwitterSocialContent, TwitterSocialComment
from items import CnnSocialUser, CnnSocialContent


class HighcloudPipeline(object):

    def process_item(self, item, spider):
        '''
            根据item类型做入库处理
        '''
        pass
        try:
            print 'HighcloudPipeline ', dict(item)
            RedisUtils.item_insert(item,spider.task_id)
            logging.info('HighcloudPipeline.process_item  [%s] has insert into redis' % dict(item))

        except Exception as e:
            logging.error('HighcloudPipeline.process_item Exception has occur %s' % str(sys.exc_info()[1]))
        finally:
            return item
