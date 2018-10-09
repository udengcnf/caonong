#coding:utf-8

#信息来源实体类
class SearchSource():
    def __init__(self):
        #标识ID
        self.id = {}
        #来源
        self.source = {}
        #来源类型
        self.source_type = {}
        #是否支持(1/支持, 0/不支持)
        self.enable = {}
        #描述
        self.description = {}

    def to_dict(self):
        return self.__dict__