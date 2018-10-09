#coding:utf-8

import time
import datetime

## 通用工具类
class Utils(object):
    @classmethod
    def get_timestamp(cls):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def time2stamp(cls, time_str = get_timestamp()):
            return time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
