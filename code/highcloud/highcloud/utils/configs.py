#coding:utf-8

import os
from highcloud import settings

class LoadConfig(object):

    @classmethod
    def load_config(cls):
        cfg = {}
        cfg['redis'] = {
            'host': settings.REDIS_HOST,
            'port': settings.REDIS_PORT,
            'user': settings.REDIS_USER,
            'password': settings.REDIS_PSD,
            'db':settings.REDIS_DB,
        }
        cfg['mongo'] = {
            'host': settings.MONGO_HOST,
            'port': settings.MONGO_PORT,
            'user': settings.MONGO_USER,
            'password': settings.MONGO_PSD,
            'db':settings.MONGO_DB,
        }
        return cfg

configs = LoadConfig.load_config()