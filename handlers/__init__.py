#!/usr/bin/env python
# encoding: utf-8
import json

import datetime
from tornado.web import RequestHandler
from ext import redis_session
from models import BaseModel


class ComplexEncoder(json.JSONEncoder):
    """处理json化时时间格式的问题"""
    def default(self, obj):
        if obj is None:
            return ''
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

class BaseHandler(RequestHandler, BaseModel):
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        # 依赖request_handler中的cookie相关方法
        self.session = redis_session.Session(self.application.session_manager, self)

    def get_current_user(self):
        return self.session.get("user_name")

    @property
    def log(self):
        return self.application.log

    @property
    def db(self):
        return self.application.db

    def write_json(self, code, data=None):
        """返回json数据时用，默认正常时状态为100"""
        ejson = {'code': code}
        if code != 100:
            if data:
                ejson['msg'] = data
                self.log.warning("[API error]code => {1},msg => {2}".format(self.request.uri, code, data))
        else:
            ejson['data'] = data
        jsonstr = json.dumps(ejson, cls=ComplexEncoder)
        self.write(jsonstr)
        self.finish()




# 缺省接口
class DefaultHandler(BaseHandler):
    def get(self):
        self.write_error(404)

    def post(self):
        self.write_error(404)