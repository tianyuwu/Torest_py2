#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: user.py
@time: 2017/9/16 上午11:13
"""
from tornado.gen import coroutine
from tornado.web import asynchronous

from handlers import BaseHandler


class IndexHandler(BaseHandler):

    def get(self):
        """JSON数据返回测试"""
        data = {"name":'111', "value":"333"}
        self.write_json(100, data)

class GetParamHandler(BaseHandler):
    def post(self):
        """获取content-type为：application/json格式的提交数据"""
        params = self.request.body
        self.write_json(100, params)

class QueryHandler(BaseHandler):
    @asynchronous
    @coroutine
    def get(self):
        """数据查询测试"""
        sqlstr = """select * from users limit 2"""
        data = yield self.db.query(sqlstr)
        self.write_json(100,data)

class DAOHandler(BaseHandler):
    @asynchronous
    @coroutine
    def get(self):
        """测试引入查询函数"""
        data = yield self.select('users', condition='id>100')
        # data = yield self.find('users', condition='id=100')
        self.write_json(100, data)


