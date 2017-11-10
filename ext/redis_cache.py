#!/usr/bin/env python
# coding=utf-8

"""
装饰器版的python自动缓存系统，使用redis持久化数据库,
https://github.com/ma6174/pycache
初始化时请修改配置
"""

import hashlib
import datetime   # 方便eval函数用
import redis
from functools import wraps
from tornado.gen import coroutine, Return


class Redis_Cache(object):
    def __init__(self):
        #pool设置
        rdpool = redis.ConnectionPool(host='127.0.0.1', port=6379, password='123kkk', max_connections=65535)
        self._db = redis.Redis(connection_pool=rdpool)

    def __del__(self):
        pass

    # 默认的数据保存时间长度（秒），缺省保留1天
    def set(self, key, value, expire_second=86400):
        self._db.set(key, value)
        if expire_second > 0:
            self._db.expire(key, expire_second)

    def get(self, key):
        return self._db.get(key)

    def delete(self, key):
        return self._db.delete(key)

    def hset(self, name, key, value, expire_second=86400):
        self._db.hset(name, key, value)
        if expire_second > 0:
            self._db.expire(name, expire_second)

    def hdel(self, name, key):
        self._db.hdel(name, key)

    def hget(self, name, key):
        return self._db.hget(name, key)

cache = Redis_Cache()

def _compute_key(method, args, kw):
    """序列化并求其哈希值"""
    hashfac = method.__name__
    _args = args[1:]
    hashfac += ''.join('_'+str(i)+str(v) for i, v in enumerate(_args))
    hashfac += ''.join('_'+str(k)+str(v) for (k, v) in kw.items())
    return hashlib.sha1(hashfac).hexdigest()


def memorize(duration=-1):
    """自动缓存同步版本"""
    def _memoize(method):
        @wraps(method)  # 自动复制函数信息, 能保留原有函数的名称和docstring
        def __memoize(*args, **kw):
            key = _compute_key(method, args, kw)
            # 是否已缓存？
            if cache._db.exists(key):
                try:  # 判断存在和返回之间还有一段时间，可能造成key不存在
                    return cache.Get(key)
                except:
                    pass
            # 运行函数
            result = method(*args, **kw)
            # 保存结果
            cache.Set(key, result, duration)
            return result

        return __memoize

    return _memoize


def async_memorize(duration=-1):
    """自动缓存异步版本，针对异步函数, 自动生成缓存名"""
    def _memoize(method):
        @wraps(method)  # 自动复制函数信息
        @coroutine
        def __memoize(*args, **kw):
            key = _compute_key(method, args, kw)
            # 是否已缓存？
            if cache._db.exists(key):
                try:  # 判断存在和返回之间还有一段时间，可能造成key不存在
                    print '[Cache HIT]%s ==> %s' % (method.__name__, key)
                    result = eval(cache.Get(key))
                except Exception as e:
                    print e
                    result = None
                raise Return(result)
            else:
                # 运行函数
                result = yield method(*args, **kw)
                # 保存结果
                cache.Set(key, result, duration)
                print '[Cache REFRESH %s]%s ==> %s ' % (duration, method.__name__, key)
                raise Return(result)

        return __memoize

    return _memoize


def async_cache(name, duration=-1):
    """自动缓存异步版本，针对异步函数, 自定义缓存名字以方便清除"""
    def _memoize(method):
        @wraps(method)  # 自动复制函数信息
        @coroutine
        def __memoize(*args, **kw):
            key = _compute_key(method, args, kw)
            # 是否已缓存？
            if cache._db.hexists(name, key):
                try:  # 判断存在和返回之间还有一段时间，可能造成key不存在
                    print '[Cache %s HIT]%s ==> %s' % (name, method.__name__, key)
                    result = eval(cache.hget(name, key))
                except Exception as e:
                    print '[Cache %s is ERROR]%s' % e
                    result = None
                raise Return(result)
            else:
                # 运行函数
                result = yield method(*args, **kw)
                # 保存结果
                cache.hset(name, key, result, duration)
                print '[Cache %s REFRESH %s]%s ==> %s ' % (name, duration, method.__name__, key)
                raise Return(result)

        return __memoize

    return _memoize