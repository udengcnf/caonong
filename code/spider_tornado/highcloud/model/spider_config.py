#coding:utf-8

#爬虫配置实体类
class SpiderConfig():
    def __init__(self):
        #标识ID
        self.id = {}
        #主爬虫运行间隔/s
        self.interval = {}
        #主爬虫ip列表
        self.main_ip = {}
        #从爬虫ip列表
        self.subordinate_ip = {}
        #scrapyd端口
        self.port = {}

    def to_dict(self):
        return self.__dict__