#coding:utf-8

import threading
import threadpool
pool = threadpool.ThreadPool(50)

class Thread_Util(object):

    @classmethod
    def get(cls,target,args = [],deamon = True):

        td = threading.Thread(target = target,args = tuple(args))
        if deamon == True :
            #put the thread to background
            td.setDaemon(True)

        return td

    @classmethod
    def put_pool(cls,target,args = [],callback = None):
        requests = threadpool.makeRequests(target, args,callback)
        [pool.putRequest(req) for req in requests]

    @classmethod
    def get_lock(cls):
        return threading.Lock()


class Thread_Timer:

    def __init__(self,interval, func, args):
        self.timer = None
        self.interval = interval
        self.func = func
        self.args = args

    def exec_func(self):
        self.func(self.args)
        self.timer = threading.Timer(self.interval, self.exec_func)
        self.timer.start()

    def start(self):
        self.timer = threading.Timer(self.interval, self.exec_func)
        self.timer.start()

    def stop(self):
        self.timer.cancel()
