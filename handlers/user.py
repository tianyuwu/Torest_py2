#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: user.py
@time: 2017/9/16 上午11:13
"""
import json
from collections import OrderedDict
from datetime import datetime

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
        # conditions = OrderedDict()
        # conditions['gender'] = 2
        data = yield self.db.select('users', fields="nick_name, gender",condition="gender=%s", params=[2])
        # data = {
        #     'content': 'akdhk',
        #     'creation_time': datetime.now(),
        #     'status': 'normal'
        # }
        # condition = {
        #     'uuid': '1111111'
        # }
        # 插入语句
        # save_data = yield self.db.insert('signature', data)
        # 更新语句
        # save_data = yield self.db.update('signature', data, condition=dict(id=3))

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
