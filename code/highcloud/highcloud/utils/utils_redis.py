#coding:utf-8

import sys
import redis
import logging
from configs import configs
from highcloud.items import TwitterSocialUser, TwitterSocialContent

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
    def item_query(cls, item, task_id = ''):
        try:
            ret = {}
            cli = cls.redis_client()
            query_key = '%s:%s:%s' % (item.__class__.__name__, task_id, item['id']) if task_id else '%s:%s' % (item.__class__.__name__, item['id'])

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
    def item_insert(cls, item, task_id = ''):
        try:
            cli = cls.redis_client()
            insert_key = '%s:%s:%s' % (item.__class__.__name__, task_id, item['id']) if task_id else '%s:%s' % (item.__class__.__name__, item['id'])
            item.fields.update( dict(item) )
            cli.hmset(insert_key, item.fields)
        except Exception as e:
            logging.error('RedisUtils.insert Exception has occur %s' % str(sys.exc_info()[1]))
            return False
        else:
            return True


    @classmethod
    def item_update(cls, item, dic, task_id = ''):
        try:
            cli = cls.redis_client()
            update_key = '%s:%s:%s' % (item.__class__.__name__, task_id, item['id']) if task_id else '%s:%s' % (item.__class__.__name__, item['id'])
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
    def item_delete(cls, item, task_id = ''):
        try:
            cli = cls.redis_client()
            delete_key = '%s:%s:%s' % (item.__class__.__name__, task_id, item['id']) if task_id else '%s:%s' % (item.__class__.__name__, item['id'])
            if delete_key in cli.keys():
                cli.delete(delete_key)
        except Exception as e:
            logging.error('RedisUtils.delete Exception has occur %s' % str(sys.exc_info()[1]))
            return False
        else:
            return True

    @classmethod
    def redis_key_push(cls, key, url):
        try:
            cli = cls.redis_client()
            cli.rpush(key, url)
        except Exception as e:
            logging.error('RedisUtils.redis_key_push Exception has occur %s' % str(sys.exc_info()[1]))
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
    def redis_key_clean(cls, key):
        try:
            cli = cls.redis_client()
            cli.delete(key)
        except Exception as e:
            logging.error('RedisUtils.redis_key_clean Exception has occur %s' % str(sys.exc_info()[1]))
            return False
        else:
            return True


if __name__ == '__main__':
    s = TwitterSocialUser()
    s1 = TwitterSocialUser()
    s2 = TwitterSocialUser()
    s['id'] = '1234567890'
    s['city'] = '123'
    RedisUtils.item_insert(s, task_id='lalala')
    # s['city'] = '234'
    # RedisUtils.item_insert(s)

    # c = TwitterSocialContent()
    # c['id'] = 2
    # # print RedisUtils.item_query(s)
    # # s1['id'] = '1780'
    # RedisUtils.item_insert(c)
    # RedisUtils.item_update(s, {'city':456})
    # print RedisUtils.item_query(s)
    # s2['id'] = '1'
    # RedisUtils.item_delete(s2)
    # RedisUtils.redis_key_push('TwitterMasterSpider:start_urls', 'a1')
    # RedisUtils.redis_key_clean('TwitterMasterSpider:dupefilter')