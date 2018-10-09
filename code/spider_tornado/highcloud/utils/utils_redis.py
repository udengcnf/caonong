#coding:utf-8

import sys
import redis
import logging
from highcloud.settings import configs
from highcloud.model.search_class import SearchClass
from highcloud.model.search_source import SearchSource
from highcloud.model.spider_config import SpiderConfig

class RedisUtils(object):

    host = configs['redis']['host']
    port = configs['redis']['port']
    user = configs['redis']['user']
    password = configs['redis']['password']

    @classmethod
    def redis_client(cls):
        try:
            pool = redis.ConnectionPool(host = cls.host, port = cls.port, password = cls.password)
            client = redis.Redis(connection_pool = pool)
        except Exception as e:
            logging.error('RedisUtils.client Exception has occur %s' % str(sys.exc_info()[1]))
            return None
        else:
            return client

    @classmethod
    def model_query(cls, model):
        try:
            ret = {}
            cli = cls.redis_client()
            query_key = '%s:%s' % (model.__class__.__name__, model.id) ## 获取Item类名和id

            if query_key in cli.keys():
                keys = cli.hkeys(query_key)
                values = cli.hmget(query_key, keys)
                for i in range(len(keys)):
                    ret[keys[i]] = values[i]
        except Exception as e:
            logging.error('RedisUtils.query Exception has occur %s' % str(sys.exc_info()[1]))
        else:
            return ret

    @classmethod
    def model_insert(cls, model):
        try:
            cli = cls.redis_client()
            insert_key = '%s:%s' % (model.__class__.__name__, model.id)  ## 获取Item类名和id
            cli.hmset(insert_key, model.to_dict())
        except Exception as e:
            logging.error('RedisUtils.insert Exception has occur %s' % str(sys.exc_info()[1]))
            return False
        else:
            return True

    @classmethod
    def model_update(cls, model, dic):
        try:
            cli = cls.redis_client()
            update_key = '%s:%s' % (model.__class__.__name__, model.id)  ## 获取Item类名和id
            if update_key in cli.keys():
                mdic = {}
                for k in dic.keys():
                    if k in model.to_dict().keys() and k not in ['id']: ## 获取dic中非id且model中含有的字段更新到Redis中
                        mdic[k] = dic[k]

                if len(mdic) > 0:
                    cli.hmset(update_key, mdic)
                status = 1
            else:
                status = 0
                logging.error('RedisUtils.update Failde ! update_key[%s] not in Redis' % update_key)
        except Exception as e:
            logging.error('RedisUtils.update Exception has occur %s' % str(sys.exc_info()[1]))
            return False
        else:
            return True if status else False

    @classmethod
    def model_delete(cls, model):
        try:
            cli = cls.redis_client()
            delete_key = '%s:%s' % (model.__class__.__name__, model.id)  ## 获取Item类名和id
            if delete_key in cli.keys():
                cli.delete(delete_key)
        except Exception as e:
            logging.error('RedisUtils.delete Exception has occur %s' % str(sys.exc_info()[1]))
            return False
        else:
            return True

    @classmethod
    def common_delete(cls, key):
        try:
            cli = cls.redis_client()
            if key in cli.keys():
                cli.delete(key)
        except Exception as e:
            logging.error('RedisUtils.common_delete Exception has occur %s' % str(sys.exc_info()[1]))
            return False
        else:
            return True

    @classmethod
    def item_list(cls, item_name, sep_count = 1):
        try:
            ret = set()
            cli = cls.redis_client()

            for h_name in cli.keys():
                if h_name.startswith(item_name):
                    h = h_name.split(':')
                    r = h[0]
                    for i in range(1, sep_count + 1):
                        try:
                            r += ':' + h[i]
                        except:
                            print h_name
                    ret.add(r)
        except:
            logging.error('RedisUtils.item_list Exception has occur %s' % str(sys.exc_info()[1]))
        else:
            return ret

    @classmethod
    def item_query(cls, item_name):
        try:
            ret = {}
            cli = cls.redis_client()

            if item_name in cli.keys():
                keys = cli.hkeys(item_name)
                values = cli.hmget(item_name, keys)
                for i in range(len(keys)):
                    ret[keys[i]] = values[i]
        except:
            logging.error('RedisUtils.item_pop Exception has occur %s' % str(sys.exc_info()[1]))
        else:
            return ret


if __name__ == '__main__':
    print '---------------------- redis init data ---------------------------'
    # s = SearchClass()
    # s.id = 1
    # s.word_dict = {1:u'重庆', 2:u'渝'}
    # RedisUtils.model_insert(s)

    # s = SearchSource()
    # s.id = 1
    # s.source = 'Sina'
    # s.enable = 0
    # RedisUtils.model_insert(s)
    #
    # s = SearchSource()
    # s.id = 2
    # s.source = 'Twitter'
    # s.enable = 1
    # RedisUtils.model_insert(s)
    #
    # s = SearchSource()
    # s.id = 3
    # s.source = 'Cnn'
    # s.enable = 1
    # RedisUtils.model_insert(s)
    #
    # c = SpiderConfig()
    # c.id = 1
    # c.interval = 1800
    # c.port = 6800
    # c.master_ip = ['52.184.38.232']
    # c.slave_ip = ['52.184.38.232']
    # RedisUtils.model_insert(c)

    a = RedisUtils.item_list('TwitterSocialContent', 2)
    print a