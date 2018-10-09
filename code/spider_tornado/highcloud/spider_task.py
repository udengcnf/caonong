#coding:utf-8

import sys
import time
import logging
import threading
import Queue
from highcloud.settings import configs
from utils.utils_thread import Thread_Util, Thread_Timer
from utils.utils_redis import RedisUtils
from utils.commons import Utils
from model.search_class import SearchClass
from model.search_source import SearchSource
from model.task_info import TaskInfo
from model.task_result import TaskResult
from utils.spiders import Spiders


class SpiderTask(object):

    actions_map = {
        'StartTask':'start_task',
        'RestartTask':'start_task',
        'StopTask':'stop_task'
    }
    spider_settings = Utils.get_spider_config()
    thread_lock = threading.Lock()
    thread_queue = Queue.Queue()

    @classmethod
    def push_task(cls, task):
        try:
            retcode = -1
            result = {'code':retcode}
            ## queue中只会有一个字典
            with cls.thread_lock:
                if cls.thread_queue.empty():
                    res = {}
                else:
                    ## 更新queue中的字典
                    res = cls.thread_queue.get()
                res[task['task_id']] = task
                cls.thread_queue.put(res)

            retcode = 1
        except Exception as e:
            result = {'code':-1, 'error_info':str(sys.exc_info()[1])}
            logging.error('SpiderTask.push_task exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            return result

    @classmethod
    def get_task(cls, task):
        try:
            retcode = -1
            result = {'code':retcode}

            res = {}
            ## queue中只会有一个字典
            with cls.thread_lock:
                if not cls.thread_queue.empty():
                    ret = cls.thread_queue.get()
                    if task['task_id'] in ret.keys():
                        ## 更新queue中的字典
                        res[task['task_id']] = ret[task['task_id']]
                    cls.thread_queue.put(ret if ret else {})

            retcode = 1
        except Exception as e:
            result = {'code':-1, 'error_info':str(sys.exc_info()[1])}
            logging.error('SpiderTask.get_task exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            result['result'] = res
            print '5---------', result
            return result

    @classmethod
    def parse_params(cls, action, params):
        def dispose_params(action, params):
            retcode = -1
            result = {'code':retcode}
            try:
                logging.info('SpiderTask.parse_params.dispose_params action:%s, params:%s' % (action, params))
                if action == 'StartTask':
                    start_time = params['start_time'] ## 任务开始时间
                    end_time = params['end_time'] ## 任务结束时间
                    refresh_time = params.get('refresh_time', 60)  ## 页面刷新时间(单位s)
                    user_id = params['user_id']  ## 创建用户ID
                    content_count = params.get('content_count',50) ## 爬取内容数量
                    source_id = params['source_id'] ## 信息来源ID列表
                    search_type = params['search_type'] ## 搜索类型(0/单词搜索, 1/分类搜索)
                    search_content = params['search_content'] ## 搜索内容(0/单词内容, 1/分类ID)
                    description = params.get('description','') ## 任务描述

                    ## 判断日期是否正确
                    start_stamp = Utils.time2stamp(start_time)
                    end_stamp = Utils.time2stamp(end_time)
                    now_time = Utils.get_strtime()
                    now_stamp = Utils.time2stamp(now_time)
                    if start_stamp >= end_stamp or now_stamp > end_stamp:
                        logging.error('SpiderTask.parse_params.dispose_params StartTask time set error ! start_time:%s, end_time:%s, now_time:%s' % (start_time, end_time, now_time))
                        result['error_info'] = 'time set error ! start_time:%s, end_time:%s, now_time:%s' % (start_time, end_time, now_time)
                        return

                    ## 判断搜索源
                    available_source = []
                    for source in source_id:
                        s = SearchSource()
                        s.id = source
                        res = RedisUtils.model_query(s)
                        if res['enable'] == '1':
                            available_source.append(source)
                    if len(available_source) == 0:
                        logging.error('SpiderTask.parse_params.dispose_params StartTask source_list:%s all disabled' % source_id)
                        result['error_info'] = 'source_list:%s all disabled' % source_id
                        return

                    ## 判断搜索类型
                    if search_type == 0: ## 单词搜索
                        pass
                    else:
                        logging.error('SpiderTask.parse_params.dispose_params StartTask search_type:%s not support' % search_type)
                        result['error_info'] = 'search_type:%s not support' % search_type
                        return

                    ## 存储任务信息
                    search_taskinfo = TaskInfo()
                    search_taskinfo.id = Utils.get_uuid()
                    search_taskinfo.created_at = Utils.get_strtime()
                    search_taskinfo.start_time = start_time
                    search_taskinfo.end_time = end_time
                    search_taskinfo.refresh_time = refresh_time
                    search_taskinfo.user_id = user_id
                    search_taskinfo.source_id = available_source
                    search_taskinfo.task_status = 0
                    search_taskinfo.master_ip = []
                    search_taskinfo.slave_ip = []
                    search_taskinfo.master_job = []
                    search_taskinfo.slave_job = []
                    search_taskinfo.search_type = search_type
                    search_taskinfo.search_content = search_content
                    search_taskinfo.content_count = content_count
                    search_taskinfo.deleted = 0
                    search_taskinfo.description = description
                    ## 任务信息入库
                    if not RedisUtils.model_insert(search_taskinfo):
                        result['error_info'] = 'RedisUtils.model_insert %s failed' % search_taskinfo
                        return
                    result['task_id'] = search_taskinfo.id

                elif action == 'RestartTask':
                    ## 查询任务信息
                    search_taskinfo = TaskInfo()
                    search_taskinfo.id = params.get('task_id')
                    task_search_ret = RedisUtils.model_query(search_taskinfo)
                    print 'RestartTask ====================  ', task_search_ret

                    if task_search_ret == {}:
                        logging.error('SpiderTask.parse_params.dispose_params RestartTask task_id:%s not exist !' % params.get('task_id'))
                        result['error_info'] = 'SpiderTask.parse_params.dispose_params RestartTask task_id:%s not exist !' % params.get('task_id')
                        return

                    ## 检查任务信息
                    start_time = task_search_ret.get('start_time')
                    end_time = task_search_ret.get('end_time')
                    task_status = eval(task_search_ret.get('task_status'))
                    source_id = eval(task_search_ret.get('source_id'))
                    search_type = eval(task_search_ret.get('search_type'))

                    ## 判断任务是否正在执行
                    if task_status == 1:
                        logging.error('SpiderTask.parse_params.dispose_params RestartTask task_id:%s is runing !' % params.get('task_id'))
                        result['error_info'] = 'SpiderTask.parse_params.dispose_params RestartTask task_id:%s is runing !' % params.get('task_id')
                        return
                    ## 判断任务是否正在停止
                    elif task_status == 4:
                        logging.error('SpiderTask.parse_params.dispose_params RestartTask task_id:%s is stoping !' % params.get('task_id'))
                        result['error_info'] = 'SpiderTask.parse_params.dispose_params RestartTask task_id:%s is stoping !' % params.get('task_id')
                        return

                    ## 判断日期是否正确
                    start_stamp = Utils.time2stamp(start_time)
                    end_stamp = Utils.time2stamp(end_time)
                    now_time = Utils.get_strtime()
                    now_stamp = Utils.time2stamp(now_time)
                    if start_stamp >= end_stamp or now_stamp > end_stamp:
                        logging.error('SpiderTask.parse_params.dispose_params RestartTask time set error ! start_time:%s, end_time:%s, now_time:%s' % (start_time, end_time, now_time))
                        result['error_info'] = 'time set error ! start_time:%s, end_time:%s, now_time:%s' % (start_time, end_time, now_time)
                        return

                    ## 判断搜索源
                    available_source = []
                    for source in source_id:
                        s = SearchSource()
                        s.id = source
                        res = RedisUtils.model_query(s)
                        if res['enable'] == '1':
                            available_source.append(source)
                    if len(available_source) == 0:
                        logging.error('SpiderTask.parse_params.dispose_params RestartTask source_list:%s all disabled' % source_id)
                        result['error_info'] = 'source_list:%s all disabled' % source_id
                        return

                    ## 判断搜索类型
                    if search_type == 0:
                        pass
                    else:
                        logging.error('SpiderTask.parse_params.dispose_params RestartTask search_type:%s not support' % search_type)
                        result['error_info'] = 'search_type:%s not support' % search_type
                        return

                    ## 更新任务信息并入库
                    if not RedisUtils.model_update(search_taskinfo, {'task_status':0, 'deleted':0}):
                        result['error_info'] = 'RedisUtils.model_update %s failed' % search_taskinfo.to_dict()
                        return
                    result['task_id'] = search_taskinfo.id

                elif action == 'StopTask':
                    ## 查询任务信息
                    search_taskinfo = TaskInfo()
                    search_taskinfo.id = params.get('task_id')
                    task_search_ret = RedisUtils.model_query(search_taskinfo)
                    print 'StopTask ====================  ', task_search_ret

                    if task_search_ret == {}:
                        logging.error('SpiderTask.parse_params.dispose_params StopTask task_id:%s not exist !' % params.get('task_id'))
                        result['error_info'] = 'SpiderTask.parse_params.dispose_params StopTask task_id:%s not exist !' % params.get('task_id')
                        return

                    task_status = eval(task_search_ret.get('task_status'))
                    if task_status == 2: ## 任务为已停止状态
                        result['error_info'] = 'task:%s has stopped' % search_taskinfo.id
                        logging.error('SpiderTask.parse_params.dispose_params task:%s has stopped' % search_taskinfo.id)
                        return
                    elif task_status == 3: ## 任务为已完成状态
                        result['error_info'] = 'task:%s has finished' % search_taskinfo.id
                        logging.error('SpiderTask.parse_params.dispose_params task:%s has finished' % search_taskinfo.id)
                        return
                    elif task_status == 4: ## 任务为正在停止状态
                        result['error_info'] = 'task:%s is stopping' % search_taskinfo.id
                        logging.error('SpiderTask.parse_params.dispose_params task:%s is stopping' % search_taskinfo.id)
                        return

                    ## 更新任务信息并入库
                    if not RedisUtils.model_update(search_taskinfo, {'task_status':4}): ## 任务置为正在停止状态
                        result['error_info'] = 'RedisUtils.model_update %s failed' % search_taskinfo.to_dict()
                        return
                    result['task_id'] = search_taskinfo.id
                    logging.info('SpiderTask.parse_params.dispose_params task:%s is stopping' % search_taskinfo.id)

                retcode = 1
            except Exception as e:
                result['error_info'] = str(sys.exc_info()[1])
                logging.error('SpiderTask.parse_params.dispose_params exception has occur:%s' % str(sys.exc_info()[1]))
            finally:
                result['code'] = retcode
                logging.info('SpiderTask.parse_params.dispose_params action:%s params:%s result:%s' % (action, params, result))
                return result

        try:
            result = {'code':1}
            if action not in cls.actions_map.keys():
                result['error_info'] = 'action %s is error' % action
            else:
                ## 检查参数
                dispose_ret = dispose_params(action, params)
                if dispose_ret['code'] == 1:
                    ## 反射调用类方法
                    invoke_func = getattr(cls, cls.actions_map[action])
                    exec_ret = invoke_func(dispose_ret)
                    result.update(exec_ret)
                else:
                    result.update(dispose_ret)

        except Exception as e:
            result = {'code':-1, 'error_info':str(sys.exc_info()[1])}
            logging.error('SpiderTask.parse_params exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            return result

    @classmethod
    def run_spider(cls, task_info):
        retcode = -1
        result = {'code':retcode}
        try:
            update_time = cls.spider_settings['interval'] ## 爬虫运行时间间隔
            stop_check = 5 ## 检测停止时间
            search_taskinfo = TaskInfo()
            search_taskinfo.id = task_info.get('task_id')
            result['task_id'] = task_info.get('task_id')
            logging.info('SpiderTask.start_task run_spider task:%s  runing success' % search_taskinfo.id)
            while True:
                print ' ===========================  I am a runing spider ===========================  ', search_taskinfo.id
                task_search_ret = RedisUtils.model_query(search_taskinfo)
                source_id = eval(task_search_ret.get('source_id'))
                slave_job = eval(task_search_ret.get('slave_job'))

                ## 查询可用网站名称如Sina、Twitter
                search_sites = []
                for s in source_id:
                    site = SearchSource()
                    site.id = s
                    site_res = RedisUtils.model_query(site)
                    search_sites.append(site_res['source'])

                if len(search_sites) == 0:
                    logging.error('SpiderTask.start_task run_spider task:%s no available sites' % search_taskinfo.id)
                    result['error_info'] = 'SpiderTask.start_task run_spider task:%s no available sites' % search_taskinfo.id
                    return

                master_data = {
                    'task_id':search_taskinfo.id, ## 任务id
                    'sites': search_sites, ## 可用网站列表
                    'listen_id': task_search_ret.get('listen_id'), ## 监听用户的ID
                    'search_word': task_search_ret.get('search_content'), ## 搜索的关键词
                    'max_count':task_search_ret.get('content_count', 50), ## 主爬虫content数
                }
                ## 启动主爬虫
                master_ret = Spiders.start_master_spider(master_data)
                if master_ret['code'] == -1:
                    logging.error('SpiderTask.start_task run_spider task:%s start master spider failed %s' % (search_taskinfo.id, master_ret['error_info']))
                    result['error_info'] = 'SpiderTask.start_task run_spider task:%s start master spider failed %s' % (search_taskinfo.id, master_ret['error_info'])
                    return
                logging.info('SpiderTask.start_task run_spider task:%s start master spider success' % (search_taskinfo.id))

                slave_data = {
                    'task_id':search_taskinfo.id, ## 任务id
                    'sites': search_sites, ## 可用网站列表
                }
                ## 启动从爬虫(最多启动4个从爬虫)
                if len(slave_job) < 4:
                    for i in range(3):
                        slave_ret = Spiders.start_slave_spider(slave_data)
                        if slave_ret['code'] == -1:
                            logging.error('SpiderTask.start_task run_spider task:%s start slave spider failed %s' % (search_taskinfo.id, slave_ret['error_info']))
                            result['error_info'] = 'SpiderTask.start_task run_spider task:%s start slave spider failed %s' % (search_taskinfo.id, slave_ret['error_info'])
                            return
                        logging.info('SpiderTask.start_task run_spider task:%s start slave spider [%s] success' % (search_taskinfo.id, i))

                ## 检测停止
                for i in range(update_time/stop_check):
                    task_search_ret = RedisUtils.model_query(search_taskinfo)
                    task_status = eval(task_search_ret.get('task_status'))

                    ## 若任务状态为正在停止
                    if task_status == 4:
                        ## 停止主爬虫
                        Spiders.stop_master_spider({'task_id':search_taskinfo.id})
                        time.sleep(1)
                        ## 停止从爬虫
                        Spiders.stop_slave_spider({'task_id':search_taskinfo.id})
                        time.sleep(1)
                        ## 清空爬虫队列
                        Spiders.clean_spider_queue({'task_id':search_taskinfo.id, 'sites': search_sites})

                        ## 任务状态置为已停止
                        if not RedisUtils.model_update(search_taskinfo, {'task_status':2}):
                            result['error_info'] = 'RedisUtils.model_update %s failed  task:%s stop failed' % (search_taskinfo.to_dict(), search_taskinfo.id)
                            logging.error('RedisUtils.model_update %s failed  task:%s stop failed' % (search_taskinfo.to_dict(), search_taskinfo.id))
                        else:
                            logging.info('SpiderTask.start_task run_spider task:%s has stoped' % search_taskinfo.id)
                            return

                    ## 判断是否到任务结束时间
                    end_time = task_search_ret.get('end_time')
                    end_stamp = Utils.time2stamp(end_time)
                    now_time = Utils.get_strtime()
                    now_stamp = Utils.time2stamp(now_time)
                    ## 若到达结束时间, 则置为已完成
                    if now_stamp >= end_stamp:
                        if not RedisUtils.model_update(search_taskinfo, {'task_status':3}):
                            result['error_info'] = 'RedisUtils.model_update %s failed  task:%s finished failed' % (search_taskinfo.to_dict(), search_taskinfo.id)
                            logging.error('RedisUtils.model_update %s failed  task:%s finished failed' % (search_taskinfo.to_dict(), search_taskinfo.id))
                        else:
                            logging.info('SpiderTask.start_task run_spider task:%s has finished' % search_taskinfo.id)
                            return

                    time.sleep(stop_check) ## 检测停止时间间隔
            retcode = 1
        except Exception as e:
            result = {'code':retcode, 'error_info':str(sys.exc_info()[1])}
            logging.error('SpiderTask.start_task run_spider exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            ## 将任务放入queue中
            cls.push_task(result)
            return result

    @classmethod
    def start_task(cls, task_info):
        try:
            retcode = -1
            result = {'code':retcode}
            ## 更新任务状态为正在执行
            search_taskinfo = TaskInfo()
            search_taskinfo.id = task_info.get('task_id')
            if not RedisUtils.model_update(search_taskinfo, {'task_status':1}):
                result['error_info'] = 'RedisUtils.model_update %s failed' % search_taskinfo.to_dict()
                return

            ## 运行爬虫
            td = Thread_Util.get(cls.run_spider, [task_info])
            td.start()
            td.join(3) ## 等待爬虫进程运行3s

            ## 从queue中取出执行信息
            task_res = cls.get_task(task_info)
            if task_res['code'] == -1:
                result['error_info'] = 'get task from queue failed %s !' % task_info
                return

            ## 更新任务结果
            res = task_res['result']
            ## 任务执行成功
            if res == {}:
                result['code'] = 1
            ## 任务执行失败
            else:
                result.update(res) ## 更新返回结果
                RedisUtils.model_update(search_taskinfo, {'task_status':5}) ## 更新数据库

            result['task_id'] = task_info.get('task_id')
        except Exception as e:
            result = {'code':-1, 'error_info':str(sys.exc_info()[1])}
            logging.error('SpiderTask.start_task exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            print 'result ----------------------------------------------------------- ', result
            return result


    @classmethod
    def stop_task(cls, task_info):
        try:
            retcode = -1
            result = {'code':retcode}

            result['task_id'] = task_info.get('task_id')
            retcode = 1
        except Exception as e:
            result = {'code':-1, 'error_info':str(sys.exc_info()[1])}
            logging.error('SpiderHandler.get exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            return result
