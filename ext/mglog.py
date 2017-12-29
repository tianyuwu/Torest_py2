#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: mg_log.py
@time: 2017/7/10 下午8:57
@description: 基于mongodb的日志系统，扩展tornado的日志功能
使用：
1. application类中setting方法传入log_request配置
2. application类中创建单例
    self.log = MgLog(config.MONGO_HOST).logger
3. handler基类中创建一个方法
    BaseHandler():
        @property
        def log(self):
            return self.application.log
4. 业务中需要写日志的地方调用，self.log.info方法即可写入日志
"""
import logging
from logging.handlers import SMTPHandler

from log4mongo.handlers import MongoHandler
from tornado.web import access_log
import tornado.log


class LogFormatter(tornado.log.LogFormatter):
    """修改tornado默认输出日志格式"""

    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s %(filename)s:%(lineno)d %(funcName)s]%(end_color)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


levels = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL
          }


class MgLog(object):
    """创建一个新的logger方便业务逻辑调用，并创建mongodb用的handler"""

    def __init__(self, mongo_host, database_name='mongo_logs',
                 log_level='warning', send_mail=False, debug=False, mail_list=[]):
        self.logger = logging.getLogger('mongo_logger')
        self.logger.setLevel(levels.get('debug'))
        if send_mail:
            mail_handler = SMTPHandler('smtp.qq.com', '379332952@qq.com', mail_list, 'HuiMouKe Server Error',
                                   ('379332952@qq.com', 'nffzqgrokerxcaia'), ())
            mail_handler.setLevel(logging.ERROR)
            logging.root.addHandler(mail_handler)
        if not debug:
            mon = MongoHandler(host=mongo_host, database_name=database_name)
            mon.setLevel(levels.get(log_level, 'warning'))
            logging.root.addHandler(MongoHandler)

        # 给当前所有存在的handler重新设置规则
        [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]


def log_request(handler):
    """修改tornado日志消息格式"""
    if handler.get_status() < 400:
        log_method = access_log.info
    elif handler.get_status() < 500:
        log_method = access_log.warning
    else:
        log_method = access_log.error
    request_time = 1000.0 * handler.request.request_time()
    # 屏蔽掉静态文件输出
    if ('/static' not in handler.request.uri) or handler.get_status() > 304:
        if handler.request.method == "GET":
            log_method("%d %s %s %.2fms", handler.get_status(),
                       handler._request_summary(),
                       handler.current_user, request_time)
        else:
            log_method("%d %s %s %s %.2fms", handler.get_status(),
                       handler._request_summary(),
                       handler.current_user,
                       handler.request.arguments, request_time)
