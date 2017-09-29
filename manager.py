#!/usr/bin/env python
# encoding: utf-8
"""
https://github.com/yetone/script-manager
@test_manager.command
def hello(a, b, c=False, name='yetone'):
    print('test.hello: <a: {}, b: {}, c: {}> by {}'.format(a, b, c, name))
"""
import momoko
import tornado.ioloop
from script_manager import Manager
from tornado.gen import coroutine

import config
from ext.postgredb import PostgresDB

manager = Manager(description='The example manager')



@manager.command
def hello():
    print 'heelo is done'

def add_user(a, b):
    io_loop = tornado.ioloop.IOLoop.instance()
    dsn = 'dbname=%s user=%s password=%s host=%s port=%s' %\
              (config.DB_NAME, config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_PORT)
    db = PostgresDB(dsn, io_loop)
    io_loop.start()
    res = yield db.dbpool.execute("SELECT COUNT(*) from users;")
    print res


if __name__ == '__main__':
    manager.run()