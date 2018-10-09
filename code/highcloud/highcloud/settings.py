# -*- coding: utf-8 -*-

import os
import logging

BOT_NAME = 'highcloud'
SPIDER_MODULES = ['highcloud.spiders']
NEWSPIDER_MODULE = 'highcloud.spiders'
BASE_DIR = os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))

IPPOOL = [
    '35.226.239.0:80',
    '172.247.251.24:80'
]

# SCHEDULER = "highcloud.scrapy_redis.scheduler.Scheduler"
# DUPEFILTER_CLASS = "highcloud.scrapy_redis.dupefilter.RFPDupeFilter"

ITEM_PIPELINES = {
   'highcloud.pipelines.HighcloudPipeline': 300,
   #  'highcloud.scrapy_redis.pipelines.RedisPipeline': 300,
}
DOWNLOADER_MIDDLEWARES = {
    "highcloud.middlewares.UserAgentMiddleware": 401,

    # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    # 'highcloud.middlewares.ProxyMiddleware': 125,
}

# SCHEDULER_PERSIST = True
# SCHEDULER_QUEUE_CLASS = 'highcloud.scrapy_redis.queue.FifoQueue'

REDIS_URL = None
REDIS_USER = 'appadmin'
REDIS_HOST = '52.229.163.208'
REDIS_PSD = '@#se123dsa%'
REDIS_PORT = 6379
REDIS_DB = 0

MONGO_USER = 'admin'
MONGO_HOST = '52.184.38.232'
MONGO_PSD = 'highcloud'
MONGO_PORT = 27017
MONGO_DB = 'admin'


logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt = '%b %d %Y %H:%M:%S',
                    filename = 'social_listen.log', ##os.path.join(os.path.dirname(os.getcwd()), 'social_task.log'),
                    filemode = 'w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
