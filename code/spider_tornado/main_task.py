#coding:utf-8

import os
import sys
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen
from tornado.options import define, options

from highcloud.spider_handler import SpiderHandler
from highcloud.utils.utils_redis import RedisUtils
from highcloud.utils.utils_thread import Thread_Util
from highcloud.utils.commons import Utils

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt = '%b %d %Y %H:%M:%S',
                    filename = 'social_task.log', ##os.path.join(os.path.dirname(os.getcwd()), 'social_task.log'),
                    filemode = 'w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

## 数据迁移线程
def move_data_thread():
    th = Thread_Util.get(target=Utils.target_redis2mongo)
    th.start()
    logging.info('=====================  move_data_thread start success  =====================')


listen_port = 8009
if __name__ == "__main__":
    def main():
        try:
            if not RedisUtils.redis_client():
                logging.error('=====================  redis connection failed  =====================' % listen_port)
                return

            move_data_thread()
            define('port', default = listen_port, type = int)
            tornado.options.parse_command_line()
            spider_app = tornado.web.Application([
                (r'/StartTask', SpiderHandler),
                (r'/RestartTask', SpiderHandler),
                (r'/StopTask', SpiderHandler),
            ])
            http_server = tornado.httpserver.HTTPServer(spider_app)
            logging.info('=====================  spider task management startup listening %s  =====================' % listen_port)
            http_server.listen(options.port)
            tornado.ioloop.IOLoop.instance().start()
        except Exception as e:
            logging.error('main.py exception has occur:%s' % str(sys.exc_info()[1]))
        finally:
            pass

    main()