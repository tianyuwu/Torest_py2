#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: local_settings.py
@time: 2017/7/12 下午9:00
"""
# mongo配置
MONGO_HOST = '127.0.0.1'
MONGO_LOG_DATABASE = 'mongo_logs'

# session配置
SESSION_SECRET = "3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc"
STOTR_OPTIONS = {
    'redis_host': '127.0.0.1',
    'redis_port': 6379,
    'redis_pass': '123kkk',
}