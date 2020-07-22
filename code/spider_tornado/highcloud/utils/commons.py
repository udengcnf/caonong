#coding:utf-8

import uuid
import time
import datetime
import urllib2
import urllib
import logging
import sys
import random
from highcloud.model.spider_config import SpiderConfig
from utils_redis import RedisUtils
from utils_mongo import MongoUtils

## 通用工具类
class Utils(object):
    @classmethod
    def get_strtime(cls):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def time2stamp(cls, time_str = None):
        if time_str:
            return time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
        else:
            return time.mktime(time.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))

    @classmethod
    def twitter_time2stamp(cls, time_str = None): ## '6:17 AM - 4 Jun 2017'
        try:
            time_list = time_str.split()
            month_map = {
                'Jan': 1,
                'Feb': 2,
                'Mar': 3,
                'Apr': 4,
                'May': 5,
                'Jun': 6,
                'Jul': 7,
                'Aug': 8,
                'Sep': 9,
                'Oct':10,
                'Nov':11,
                'Dec':12,
            }
            H = int(time_list[0].split(':')[0]) # 时
            M = int(time_list[0].split(':')[1]) # 分
            S = 0 # 秒
            H = (0 if H == 12 else H) if time_list[1] == 'AM' else (H if H == 12 else H + 12) ## 转换为24小时制

            Y = time_list[5] # 年
            m = month_map[time_list[4]] # 月
            d = time_list[3] # 日

            new_time_str = '%s-%s-%s %s:%s:%s' % (Y, m, d, H, M, S)
            return cls.time2stamp(new_time_str)
        except:
            return cls.time2stamp()

    @classmethod
    def get_uuid(cls,):
        return str(uuid.uuid4())

    @classmethod
    def post(cls,url, data):
        try:
            retcode = -1
            result = {'code':retcode}
            logging.info('commons.Utils.post url:%s data:%s' % (url, data))
            f = urllib2.urlopen(url =url, data = urllib.urlencode(data))

            result['result'] = eval(f.read())
            retcode = 1
        except Exception as e:
            logging.error('commons.Utils.get exception has occur:%s' % str(sys.exc_info()[1]))
            result['error_info'] = str(sys.exc_info()[1])
        finally:
            result['code'] = retcode
            return result

    @classmethod
    def get(cls,url, data):
        try:
            f = urllib2.urlopen(url =url, data = urllib.urlencode(data))
        except Exception as e:
            logging.error('commons.Utils.get exception has occur:%s' % str(sys.exc_info()[1]))
        else:
            return f.read()

    @classmethod
    def get_spider_config(cls,):
        try:
            result = {}
            c = SpiderConfig()
            c.id = 1
            res = RedisUtils.model_query(c)
            result['interval'] = eval(res.get('interval', '300'))
            result['main_ip'] = eval(res.get('main_ip'))
            result['subordinate_ip'] = eval(res.get('subordinate_ip'))
            result['port'] = res.get('port', '6800')

        except Exception as e:
            logging.error('commons.Utils.get_spider_config exception has occur:%s' % str(sys.exc_info()[1]))
        else:
            return result

    @classmethod
    def start_spider(cls, params):
        try:
            retcode = -1
            result = {'code':retcode}

            cfg = cls.get_spider_config()
            ## redis config
            main_ip = random.choice(cfg.get('main_ip'))
            subordinate_ip = random.choice(cfg.get('subordinate_ip'))
            port = cfg.get('port')
            ## spider params
            project = params.get('project', 'default')
            spider = params.get('spider', 'TwitterMainSpider')
            search_word = params.get('search_word', '中国')
            task_id = params.get('task_id', 'task_id')

            host = main_ip if 'Main' in spider else subordinate_ip
            url = 'http://%s:%s/schedule.json' % (host, port)
            data = {
                'project':project,
                'spider':spider,
                'search_word':search_word,
                'task_id':task_id
            }

            result['result'] = cls.post(url, data)
            retcode = 1
        except Exception as e:
            result['error_info'] = str(sys.exc_info()[1])
            logging.error('commons.Utils.start_spider exception has occur:%s' % str(sys.exc_info()[1]))
        else:
            result['code'] = retcode
            logging.info('commons.Utils.start_spider params:%s result:%s' % (params, result))
            return result

    @classmethod
    def result_redis2mongo(cls, move_count=20):
        try:
            retcode = -1
            result = {'code':retcode}

            result_hash = ['TwitterSocialContent', 'TwitterSocialUser']
            for h in result_hash:
                item_list = RedisUtils.item_list(h, 1) ## [TwitterSocialContent:task_id1, TwitterSocialContent:task_id2, ...]

                for item in item_list:
                    task_list = RedisUtils.item_list(item, 2)  ## [TwitterSocialContent:task_id1:result1, TwitterSocialContent:task_id2:result2, ...]
                    insert_item_list = []
                    deleted_key = []
                    insert_table = item.replace(':', '.') ## TwitterSocialContent.task_id1
                    for task in task_list:
                        task_result = RedisUtils.item_query(task)
                        create_time = task_result.get('created_at', None)
                        task_result['time_stamp'] = cls.twitter_time2stamp(create_time) ## 创建时间戳, 方便排序查询
                        task_result['task_id'] = task
                        insert_item_list.append(task_result)
                        deleted_key.append(task)
                        if len(insert_item_list) == move_count:
                            break

                    for i in range(len(insert_item_list)):
                        ## 将结果放入mongodb(若存在则更新)
                        update_result = MongoUtils.update(table = insert_table, condition={'id':insert_item_list[i]['id']},model_dic = insert_item_list[i])
                        if update_result:
                            ## 删除redis中的结果
                            if RedisUtils.common_delete(deleted_key[i]):
                                logging.info('[%s] [%s] move redis to mongo success' % (i, deleted_key[i]))

            retcode = 0
        except:
            result['error_info'] = str(sys.exc_info()[1])
            logging.error('commons.Utils.result_redis2mongo exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            result['code'] = retcode
            return result

    @classmethod
    def target_redis2mongo(cls):
        try:
            while True:
                logging.info('=======================   start redis2mongo   =======================')
                cls.result_redis2mongo()
                ## 每隔2s做一次数据迁移
                time.sleep(2)
        except:
            logging.error('commons.Utils.target_redis2mongo exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            pass

if __name__ == '__main__':
    print '--------------------------commons'
    print Utils.time2stamp(time_str='2017-01-27 15:04:09')
    print Utils.get_spider_config()
    # print Utils.twitter_time2stamp('6:17 PM - 4 Jun 2017')
    Utils.result_redis2mongo()
    # print Utils.post('http://52.184.38.232:6800/schedule.json', {'project': 'highcloud', 'search_word': '12', 'spider': 'TwitterMainSpider', 'task_id': '0824d499-d5d6-4698-a7ca-35a524fb4c18', 'max_count': '5'})
