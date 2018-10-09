#coding:utf-8

import os
import ConfigParser

class LoadConfig(object):

    cfg_file = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'scrapy.cfg')

    @classmethod
    def load_config(cls):
        cfg = {}
        configs = ConfigParser.ConfigParser()
        with open(cls.cfg_file) as f:
            configs.readfp(f, "rb")
            cfg['settings'] = {'default': configs.get('settings', 'default')}
            cfg['deploy'] = {'project': configs.get('deploy', 'project')}

            cfg['redis'] = {
                'host': configs.get('redis', 'host'),
                'port': configs.get('redis', 'port'),
                'user': configs.get('redis', 'user'),
                'password': configs.get('redis', 'password'),
                'db': configs.get('redis', 'db'),
            }
        return cfg

configs = LoadConfig.load_config()