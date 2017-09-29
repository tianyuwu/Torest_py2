#!/usr/bin/env python
# encoding: utf-8
import logging
import os
import time

import sys
import subprocess

import signal
import tornado.web
import tornado.options
import tornado.httpserver
import tornado.ioloop
from log4mongo.handlers import MongoHandler
from tornado.gen import coroutine
from tornado.log import access_log, app_log, gen_log, LogFormatter
from tornado.options import define, options
import config
# pg连接
from ext.postgredb import PostgresDB
# session库
from ext import redis_session
from routes import handlers

define("port", default=8899, help="run on the given port", type=int)


class Application(tornado.web.Application):

    def __init__(self, ioloop):
        settings = dict(
            debug=config.DEBUG,
            allow_remote_access=True,
            cookie_secret=config.COOKIE_SECRET,
            # xsrf_cookies=True,
            # static_url_prefix="",  # static路径的前缀配置，在生产环境可以配置cdn
            # ui_modules=UIModules,
            # ui_methods=UIMethods
        )
        super(Application, self).__init__(handlers=handlers, **settings)


        dsn = 'dbname=%s user=%s password=%s host=%s port=%s' %\
              (config.DB_NAME, config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_PORT)
        self.db = PostgresDB(dsn, ioloop)
        # mongodb
        # mongo_client = motor.motor_tornado.MotorClient('mongo', 27017)
        # self.db = mongo_client.blog

        self.session_manager = redis_session.SessionManager(config.SESSION_SECRET, config.STOTR_OPTIONS)

        # mongo_logger
        self.log = logging.getLogger('mongo_logger')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # 生产环境中将所有日志添加到mongo_logs库
        if config.DEBUG:
            mon = MongoHandler(host=config.MONGO_HOST, database_name='mongo_logs')
            mon.setLevel(logging.INFO)
            self.log.addHandler(mon)
            access_log.addHandler(mon)
            app_log.addHandler(mon)
            gen_log.addHandler(mon)

        # 当前应用日志打印到标准输出
        self.log.addHandler(ch)
        # 创建表
        self.maybe_create_tables()


    @coroutine
    def maybe_create_tables(self):
        try:
            yield self.db.dbpool.execute("SELECT COUNT(*) from users;")
        except:
            with open('schema.sql') as f:
                sqlstr = f.read()
            yield self.db.dbpool.execute(sqlstr)


    def log_request(self, handler):
        """Writes a completed HTTP request to the logs.

        By default writes to the python root logger.  To change
        this behavior either subclass Application and override this method,
        or pass a function in the application settings dictionary as
        ``log_function``.
        """
        if "log_function" in self.settings:
            self.settings["log_function"](handler)
            return
        if handler.get_status() < 400:
            log_method = tornado.log.access_log.info
        elif handler.get_status() < 500:
            log_method = tornado.log.access_log.warning
        else:
            log_method = tornado.log.access_log.error
        request_time = 1000.0 * handler.request.request_time()
        log_method("%d %s %s %.2fms", handler.get_status(),
                   handler._request_summary(), handler.request.arguments, request_time)



class LogFormatter(LogFormatter):
    """修改默认输出日志格式"""
    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class App:
    def __init__(self):
        self.http_server = None
        self.mainApp = None
        self.io_loop = tornado.ioloop.IOLoop.instance()
        self.deadline = None

    def __del__(self):
        pass


    def sig_handler(self, sig, frame):
        logging.info('Caught signal: %s'%sig)
        tornado.ioloop.IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        logging.info('Stopping http server')

        if self.http_server is not None:
            self.http_server.stop()  # 不接收新的 HTTP 请求

        logging.info('Will shutdown in %s seconds ...'% 1)
        # self.io_loop = tornado.ioloop.IOLoop.instance()

        self.deadline = time.time() + 1
        self.stop_loop()

    def stop_loop(self):
        now = time.time()
        if now < self.deadline and (self.io_loop._callbacks or self.io_loop._timeouts):
            self.io_loop.add_timeout(now + 1, self.stop_loop)
        else:
            print 'Server Shutdown!'
            self.io_loop.stop()  # 处理完现有的 callback 和 timeout 后，可以跳出 io_loop.start() 里的循环

    def init(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGQUIT, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTSTP, self.sig_handler)
        return True



    def main_loop(self):
        options.parse_command_line()
        # 日志格式设置
        [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]
        # if options.debug == 'debug':
        #     import pdb
        #     pdb.set_trace()  #引入相关的pdb模块进行断点调试
        logging.info('Init Server...')
        self.mainApp = Application(self.io_loop)
        self.http_server = tornado.httpserver.HTTPServer(self.mainApp, xheaders=True)
        self.http_server.listen(options.port)

        logging.info('Server Running in port %s...'% options.port)
        self.io_loop.start()


if __name__ == "__main__":
    app = App()
    if app.init():
        app.main_loop()