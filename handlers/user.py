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
    @asynchronous
    @coroutine
    def get(self):
        self.write_json(100,'hahaha')