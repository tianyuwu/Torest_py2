#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: user.py
@time: 2017/9/16 上午11:13
"""
import json

from tornado.gen import coroutine
from tornado.web import asynchronous

from ext.validator import validate
from forms.test_form import TestForm
from handlers import BaseHandler
from mixins import CacheMixin


class IndexHandler(BaseHandler):

    def get(self):
        """JSON数据返回测试"""
        data = {"title":'hello', "content":"world"}
        self.write_json(100, data)

class GetParamHandler(BaseHandler):
    def post(self):
        """get_param可以获取content-type为：application/json格式的提交数据"""
        params = self.get_param('name')
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
        # 查询多条
        # data = yield self.select('users', condition='id>100')
        # 查询单条
        # data = yield self.find('users', condition='id=100')
        data = {
            'uuid': '1111111',
            'tag': '测试',
            'tag_type': 'company',
            'priority': '0'
        }
        condition = {
            'uuid': '1111111'
        }
        # 插入语句
        # save_data = yield self.insert_one('option_tag', data)
        # 更新语句
        # save_data = yield self.update('option_tag', data, condition)

        self.write_json(100, data)

class CacheHandler(CacheMixin, BaseHandler):

    def get(self):
        print 'refresh'
        self.write_json(100, 2222)


class FormsHandler(BaseHandler):
    @validate(TestForm)
    def post(self):
        print self.form_data['msg']
        self.write_json(100, self.form_data)
