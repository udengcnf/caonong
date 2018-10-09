#coding:utf-8

#搜索分类实体类
class SearchClass():
    def __init__(self):
        #标识ID
        self.id = {}
        #搜索词字典(key:词ID, value:词)
        self.word_dict = {}
        #描述
        self.description = {}

    def to_dict(self):
        return self.__dict__