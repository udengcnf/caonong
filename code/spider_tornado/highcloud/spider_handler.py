#coding:utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen

import sys
import json
import logging
from spider_task import SpiderTask

class SpiderHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        try:
            action = self.get_argument('action')
            params = self.get_argument('params')

            client = tornado.httpclient.AsyncHTTPClient()
            logging.info('SpiderHandler.post has received action:%s, params:%s' % (action, params) )
            response = yield tornado.gen.Task(client.fetch, SpiderTask.parse_params(action, eval(params)))
            logging.info('SpiderHandler.post has return:%s' % response.effective_url)
            self.finish(response.effective_url)
        except Exception as e:
            logging.error('SpiderHandler.post exception has occur:%s' % str(sys.exc_info()[1]))
            self.finish({'code':-1, 'error_info':str(sys.exc_info()[1])})
        finally:
            pass
