#coding:utf-8

#搜索任务实体类
class TaskInfo():
    def __init__(self):
        #标识ID
        self.id = {}
        #创建时间
        self.created_at = {}
        #开始时间
        self.start_time = {}
        #结束时间
        self.end_time = {}
        #刷新时间
        self.refresh_time = {}
        #用户ID
        self.user_id = {}
        #内容数量(主爬虫content数)
        self.content_count = {}
        #主爬虫ip列表
        self.master_ip = {}
        #从爬虫ip列表
        self.slave_ip = {}
        #主爬虫job_id列表
        self.master_job = {}
        #从爬虫job_id列表
        self.slave_job = {}
        #来源ID(列表)
        self.source_id = {}
        #任务状态(0/已创建, 1/正在执行, 2/已停止, 3/已完成, 4/执行失败, 5/已删除)
        self.task_status = {}
        #搜索类型(0/单词搜索, 1/分类搜索)
        self.search_type = {}
        #搜索内容(0/单词内容, 1/分类ID)
        self.search_content = {}
        #是否删除
        self.deleted = {}
        #任务描述
        self.description = {}

    def to_dict(self):
        return self.__dict__