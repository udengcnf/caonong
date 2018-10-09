# coding=utf-8

BOT_NAME = 'weibo'

SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'

'''
#把数据存到路径中的CSV文件中去
FEED_URI = u'file:///G:/MovieData/followinfo.csv'
FEED_FORMAT = 'CSV'
'''

DOWNLOADER_MIDDLEWARES = {
    "weibo.middleware.UserAgentMiddleware": 401,
    "weibo.middleware.CookiesMiddleware": 402,
}


ITEM_PIPELINES = {
    #'weather2.pipelines.Weather2Pipeline': 300,
    'weibo.pipelines.MySQLStorePipeline': 300,
}


DOWNLOAD_DELAY = 2  # 下载器间隔时间

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'doubanmovie (+http://www.yourdomain.com)'
