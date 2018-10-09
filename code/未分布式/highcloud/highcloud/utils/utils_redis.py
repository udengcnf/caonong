#coding:utf-8

import sys
import redis
import logging
from configs import configs
from highcloud.twitter.items import TwitterSocialUser

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
    def item_query(cls, item):
        try:
            ret = {}
            cli = cls.redis_client()
            query_key = '%s:%s' % (item.__class__.__name__, item['id']) ## 获取Item类名和id

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
    def item_insert(cls, item):
        try:
            cli = cls.redis_client()
            insert_key = '%s:%s' % (item.__class__.__name__, item['id'])  ## 获取Item类名和id
            item.fields.update( dict(item) )
            cli.hmset(insert_key, item.fields)
        except Exception as e:
            logging.error('RedisUtils.insert Exception has occur %s' % str(sys.exc_info()[1]))
            return False
        else:
            return True

    @classmethod
    def item_update(cls, item, dic):
        try:
            cli = cls.redis_client()
            update_key = '%s:%s' % (item.__class__.__name__, item['id'])  ## 获取Item类名和id
            if update_key in cli.keys():
                mdic = {}
                for k in dic.keys():
                    if k in item.fields.keys() and k not in ['id']: ## 获取dic中非id且item中含有的字段更新到Redis中
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
    def item_delete(cls, item):
        try:
            cli = cls.redis_client()
            delete_key = '%s:%s' % (item.__class__.__name__, item['id'])  ## 获取Item类名和id
            if delete_key in cli.keys():
                cli.delete(delete_key)
        except Exception as e:
            logging.error('RedisUtils.delete Exception has occur %s' % str(sys.exc_info()[1]))
            return False
        else:
            return True


if __name__ == '__main__':
    s = TwitterSocialUser()
    s1 = TwitterSocialUser()
    s2 = TwitterSocialUser()
    s['id'] = '1234567890'
    s['city'] = '123'
    RedisUtils.item_insert(s)
    s['city'] = '234'
    RedisUtils.item_insert(s)
    # print RedisUtils.item_query(s)
    # s1['id'] = '1780'
    # RedisUtils.item_insert(s1)
    # RedisUtils.item_update(s, {'city':456})
    # print RedisUtils.item_query(s)
    # s2['id'] = '1'
    # RedisUtils.item_delete(s2)