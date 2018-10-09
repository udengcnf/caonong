#coding:utf-8

class LoadConfig(object):

    @classmethod
    def load_config(cls):
        cfg = {}
        cfg['redis'] = {
            'host': '52.229.163.208',
            'port': '6379',
            'user': 'appadmin',
            'password': '@#se123dsa%',
            'db': '0',
        }

        cfg['mongo'] = {
            'host': '52.184.38.232',
            'port': 27017,
            'user': 'admin',
            'password': 'highcloud',
            'db': 'admin',
        }
        return cfg

configs = LoadConfig.load_config()