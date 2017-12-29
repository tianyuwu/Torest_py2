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
from ext.mglog import MgLog, log_request
from ext.postgredb import PostgresDB
# session库
from ext import rdsession
from routes import handlers

define("port", default=8899, help="run on the given port", type=int)


class Application(tornado.web.Application):

    def __init__(self, ioloop):
        settings = dict(
            debug=config.DEBUG,
            allow_remote_access=True,
            cookie_secret=config.COOKIE_SECRET,
            log_function=log_request,  # 日志格式修改
            # xsrf_cookies=True,
            # static_url_prefix="",  # static路径的前缀配置，在生产环境可以配置cdn
            # ui_modules=UIModules,
            # ui_methods=UIMethods
        )
        super(Application, self).__init__(handlers=handlers, **settings)


        dsn = 'dbname=%s user=%s password=%s host=%s port=%s' %\
              (config.DB_NAME, config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_PORT)
        self.db = PostgresDB(dsn, ioloop)
        self.session_manager = rdsession.SessionManager(config.SESSION_SECRET, config.STOTR_OPTIONS)
        self.log = MgLog(config.MONGO_HOST, debug=config.DEBUG).logger

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
        # if options.debug == 'debug':
        #     import pdb
        #     pdb.set_trace()  #引入相关的pdb模块进行断点调试
        print('Init Server...')
        self.mainApp = Application(self.io_loop)
        self.http_server = tornado.httpserver.HTTPServer(self.mainApp, xheaders=True)
        self.http_server.listen(options.port)

        logging.info('Server Running in port %s...'% options.port)
        self.io_loop.start()


if __name__ == "__main__":
    app = App()
    if app.init():
        app.main_loop()