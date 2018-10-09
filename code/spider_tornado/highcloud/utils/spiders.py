#coding:utf-8

import uuid
import time
import datetime
import urllib2
import urllib
import logging
import sys
import random
from commons import Utils
from highcloud.model.spider_config import SpiderConfig
from highcloud.model.task_info import TaskInfo
from utils_redis import RedisUtils

## 爬虫相关类
class Spiders(object):

    @classmethod
    def get_spider_config(cls):
        try:
            result = {}
            c = SpiderConfig()
            c.id = 1
            res = RedisUtils.model_query(c)
            result['interval'] = eval(res.get('interval', '300'))
            result['master_ip'] = eval(res.get('master_ip'))
            result['slave_ip'] = eval(res.get('slave_ip'))
            result['port'] = res.get('port', '6800')

        except Exception as e:
            logging.error('commons.Utils.get_spider_config exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            return result

    @classmethod
    def start_master_spider(cls, params):
        try:
            retcode = -1
            result = {'code':retcode}

            cfg = cls.get_spider_config()
            ## redis config
            m_ip = random.choice(cfg.get('master_ip'))
            port = cfg.get('port')
            ## spider params
            project = params.get('project', 'highcloud')
            sites = params.get('sites', ['Twitter'])
            search_word = params.get('search_word', '中国')
            task_id = params.get('task_id', 'task_id')
            runing_task = TaskInfo()
            runing_task.id = task_id
            url = 'http://%s:%s/schedule.json' % (m_ip, port)
            data = {
                'project':project,
                'search_word':search_word,
                'task_id':task_id,
                'max_count':params.get('max_count', 50),
            }

            ## 依次启动各个网站的主爬虫
            success = False
            for site in sites:
                data['spider'] = site + 'MasterSpider'
                ## 通过scrapyd提供的接口启动spider
                ret = Utils.post(url, data)
                logging.info('commons.Utils.start_spider task:%s result:%s' % (task_id, ret))
                if ret['code'] == -1:
                    logging.error('commons.Utils.start_spider %s spider run failed' % site)
                else:
                    ## spider运行失败
                    if ret['result']['status'] != 'ok':
                        logging.error('commons.Utils.start_spider task:%s runing spider failed result:%s' % (task_id, ret['result']))
                        continue

                    ## 更新主爬虫jobid列表
                    master_job = eval(RedisUtils.model_query(runing_task).get('master_job'))
                    if master_job != [] and ret['result']['jobid'] not in master_job:
                        master_job.append(ret['result']['jobid'])
                    else:
                        master_job = [ret['result']['jobid']]

                    ## 更新主爬虫ip列表
                    master_ip = eval(RedisUtils.model_query(runing_task).get('master_ip'))
                    if master_ip != [] and m_ip not in master_ip:
                        master_ip.append(m_ip)
                    else:
                        master_ip = [m_ip]

                    ## 更新数据库
                    if not RedisUtils.model_update(runing_task, {'master_job':master_job, 'master_ip':master_ip}):
                        logging.error('commons.Utils.start_spider task:%s update master_job:%s master_ip:%s failed' % (task_id, master_job, master_ip))
                        continue

                    success = True
                    logging.info('commons.Utils.start_spider %s master spider run success' % site)

            if not success:
                retcode = -1
                logging.error('commons.Utils.start_spider all site [%s] master spider run failed' % ','.join(sites))
                result['error_info'] = 'all site %s spider master run failed' % ','.join(sites)
                return
            retcode = 1
        except Exception as e:
            result['error_info'] = str(sys.exc_info()[1])
            logging.error('commons.Utils.start_spider exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            logging.info('commons.Utils.start_spider params:%s result:%s' % (params, result))
            return result

    @classmethod
    def start_slave_spider(cls, params):
        try:
            retcode = -1
            result = {'code':retcode}

            cfg = cls.get_spider_config()
            ## redis config
            s_ip = random.choice(cfg.get('slave_ip'))
            port = cfg.get('port')
            ## spider params
            project = params.get('project', 'highcloud')
            sites = params.get('sites', ['Twitter'])
            task_id = params.get('task_id', 'task_id')
            runing_task = TaskInfo()
            runing_task.id = task_id
            url = 'http://%s:%s/schedule.json' % (s_ip, port)
            data = {
                'project':project,
                'task_id':task_id,
            }

            ## 依次启动各个网站的从爬虫
            success = False
            for site in sites:
                data['spider'] = site + 'SlaveSpider'
                ## 通过scrapyd提供的接口调用spider
                ret = Utils.post(url, data)
                logging.info('commons.Utils.start_spider task:%s result:%s' % (task_id, ret))
                if ret['code'] == -1:
                    logging.error('commons.Utils.start_spider %s spider run failed' % site)
                else:
                    ## spider运行失败
                    if ret['result']['status'] != 'ok':
                        logging.error('commons.Utils.start_spider task:%s runing spider failed result:%s' % (task_id, ret['result']))
                        continue

                    ## 更新从爬虫jobid列表
                    slave_job = eval(RedisUtils.model_query(runing_task).get('slave_job'))
                    if slave_job != [] and ret['result']['jobid'] not in slave_job:
                        slave_job.append(ret['result']['jobid'])
                    else:
                        slave_job = [ret['result']['jobid']]

                    ## 更新从爬虫ip列表
                    slave_ip = eval(RedisUtils.model_query(runing_task).get('slave_ip'))
                    if slave_ip != [] and s_ip not in slave_ip:
                        slave_ip.append(s_ip)
                    else:
                        slave_ip = [s_ip]

                    ## 更新数据库
                    if not RedisUtils.model_update(runing_task, {'slave_job':slave_job, 'slave_ip':slave_ip}):
                        logging.error('commons.Utils.start_spider task:%s update slave_job:%s  slave_ip:%s failed' % (task_id, slave_job, slave_ip))
                        continue

                    success = True
                    logging.info('commons.Utils.start_spider %s slave spider run success' % site)

            if not success:
                retcode = -1
                logging.error('commons.Utils.start_spider all site %s slave spider run failed' % ','.join(sites))
                result['error_info'] = 'all site %s slave spider run failed' % ','.join(sites)
                return
            retcode = 1
        except Exception as e:
            result['error_info'] = str(sys.exc_info()[1])
            logging.error('commons.Utils.start_spider exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            logging.info('commons.Utils.start_spider params:%s result:%s' % (params, result))
            return result

    @classmethod
    def stop_master_spider(cls, params):
        try:
            retcode = -1
            result = {'code':retcode}

            cfg = cls.get_spider_config()
            ## redis config
            port = cfg.get('port')

            ## spider params
            task_id = params.get('task_id', 'task_id')
            project = params.get('project', 'highcloud')
            runing_task = TaskInfo()
            runing_task.id = task_id
            runing_res = RedisUtils.model_query(runing_task)
            master_ip = eval(runing_res.get('master_ip'))
            master_job = eval(runing_res.get('master_job'))

            if len(master_ip) == 0 or len(master_job) == 0:
                result['error_info'] = 'master_ip:%s, master_job:%s  error!' % (master_ip, master_job)
                logging.error('commons.Utils.stop_master_spider master_ip:%s, master_job:%s  error!' % (master_ip, master_job))
                return

            success = True
            ## 停止所有的ip->job配对
            for m_ip in master_ip:
                for m_job in master_job:
                    url = 'http://%s:%s/cancel.json' % (m_ip, port)
                    data = {'project':project, 'job':m_job}

                    ## 通过scrapyd提供的接口停止spider
                    ret = Utils.post(url, data)
                    logging.info('commons.Utils.stop_master_spider task:%s, ip:%s, job:%s, result:%s' % (task_id, m_ip, m_job, ret))
                    if not ret or ret['code'] == -1:
                        logging.info('commons.Utils.stop_master_spider task:%s, ip:%s, job:%s failed' % (task_id, m_ip, m_job))
                        success = False
                        continue
                    else:
                        ## spider运行失败
                        if ret['result']['status'] != 'ok':
                            logging.error('commons.Utils.stop_master_spider task:%s runing spider failed result:%s' % (task_id, ret['result']))
                            success = False
                            continue
                        logging.info('commons.Utils.stop_master_spider task:%s, ip:%s, job:%s success' % (task_id, m_ip, m_job))

            if not success:
                retcode = -1
                result['error_info'] = 'stop_master_spider error'
                logging.error('commons.Utils.stop_master_spider %s failed' % (params))
                return

            retcode = 1
        except Exception as e:
            result['error_info'] = str(sys.exc_info()[1])
            logging.error('commons.Utils.stop_master_spider exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            logging.info('commons.Utils.stop_master_spider params:%s result:%s' % (params, result))
            return result

    @classmethod
    def stop_slave_spider(cls, params):
        try:
            retcode = -1
            result = {'code':retcode}

            cfg = cls.get_spider_config()
            ## redis config
            port = cfg.get('port')

            ## spider params
            task_id = params.get('task_id', 'task_id')
            project = params.get('project', 'highcloud')
            runing_task = TaskInfo()
            runing_task.id = task_id
            runing_res = RedisUtils.model_query(runing_task)
            slave_ip = eval(runing_res.get('slave_ip'))
            slave_job = eval(runing_res.get('slave_job'))

            if len(slave_ip) == 0 or len(slave_job) == 0:
                result['error_info'] = 'slave_ip:%s, slave_job:%s  error!' % (slave_ip, slave_job)
                logging.error('commons.Utils.stop_slave_spider slave_ip:%s, slave_job:%s  error!' % (slave_ip, slave_job))
                return

            success = True
            ## 停止所有的ip->job配对
            for s_ip in slave_ip:
                for s_job in slave_job:
                    url = 'http://%s:%s/cancel.json' % (s_ip, port)
                    data = {'project':project, 'job':s_job}

                    ## 通过scrapyd提供的接口停止spider
                    ret = Utils.post(url, data)
                    logging.info('commons.Utils.stop_slave_spider task:%s, ip:%s, job:%s, result:%s' % (task_id, s_ip, s_job, ret))
                    if ret['code'] == -1:
                        logging.info('commons.Utils.stop_slave_spider task:%s, ip:%s, job:%s failed' % (task_id, s_ip, s_job))
                        success = False
                        continue
                    else:
                        ## spider运行失败
                        if ret['result']['status'] != 'ok':
                            logging.error('commons.Utils.stop_slave_spider task:%s runing spider failed result:%s' % (task_id, ret['result']))
                            success = False
                            continue
                        logging.info('commons.Utils.stop_slave_spider task:%s, ip:%s, job:%s success' % (task_id, s_ip, s_job))

            if not success:
                retcode = -1
                result['error_info'] = 'stop_slave_spider error'
                logging.error('commons.Utils.stop_slave_spider %s failed' % (params))
                return

            retcode = 1
        except Exception as e:
            result['error_info'] = str(sys.exc_info()[1])
            logging.error('commons.Utils.stop_slave_spider exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            logging.info('commons.Utils.stop_slave_spider params:%s result:%s' % (params, result))
            return result

    @classmethod
    def clean_spider_queue(cls, params):
        try:
            retcode = -1
            result = {'code':retcode}

            task_id = params.get('task_id', 'task_id')
            sites = params.get('sites', ['Twitter'])

            for site in sites:
                delete_key = '%sMasterSpider:%s' % (site, task_id)
                if not RedisUtils.common_delete(delete_key):
                    result['error_info'] = 'clean_spider_queue task_id:%s  delete failed' % task_id
                    logging.error('commons.Utils.clean_spider_queue task_id:%s  delete failed' % task_id)

            retcode = 1
        except Exception as e:
            result['error_info'] = str(sys.exc_info()[1])
            logging.error('commons.Utils.stop_slave_spider exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            logging.info('commons.Utils.stop_slave_spider params:%s result:%s' % (params, result))
            return result

if __name__ == '__main__':
    print '--------------------------commons'
    print Utils.time2stamp(time_str='2017-10-27 15:48:29')
    print Utils.get_spider_config()
