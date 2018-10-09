#coding:utf-8

#任务结果实体类
class TaskResult():
    def __init__(self):
        #标识ID
        self.id = {}
        #任务ID
        self.task_id = {}
        #搜索类型(0/单词搜索, 1/分类搜索)
        self.search_type = {}
        #搜索内容(0/单词内容, 1/分类ID)
        self.search_content = {}
        #搜索结果(单词搜索/内容ID列表, 分类搜索/结果词字典(key:词ID, value:内容ID列表)
        self.search_result = {}
        #最后更新时间
        self.update_time = {}
        #任务描述
        self.description = {}

    def to_dict(self):
        return self.__dict__