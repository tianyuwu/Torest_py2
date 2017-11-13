#!/usr/bin/env python
# encoding: utf-8
import hashlib

from ext.redis_cache import cache

try:
    import cPickle as pickle
except ImportError:
    import pickle

import functools
from tornado.gen import coroutine, Return


class DAOMixin(object):
    """
    Data Access Object as  get, query, execute ..
    """
    def _conditions(self, condition):
        """
        查询条件，支持两种方式，字典和字符串，字符串需要用到单引号
        eg： "nick_name='Whitney'
            or 
            {"nick_name":"Whitney"}
        """
        condition_sql = ''
        if hasattr(condition, "items"):
            # mapping objects
            query = condition.items()
            l = []
            # preserve old behavior
            for k, v in query:
                if v:
                    l.append("{0}='{1}'".format(k, v))
            if len(l):
                condition_sql = "where "+' AND '.join(l)
            else:
                condition_sql = ''

        elif isinstance(condition, str) or isinstance(condition, unicode):
            condition_sql = "WHERE " + condition

        return condition_sql

    def _get_insert_str(self, data_dict):
        """
        组合插入的sql
        """
        sql_str = ''
        if hasattr(data_dict, "items"):
            # mapping objects
            query = data_dict.items()
            fields = []
            values = []
            # preserve old behavior
            for k, v in query:
                if v is not None:
                    fields.append(k)
                    values.append(str(v))

            if not len(fields):
                self.log.error('sql错误！')
            else:
                fields_str = ','.join(fields)
                values_str = "','".join(values)
                sql_str = "({0}) VALUES ('{1}')".format(fields_str, values_str)

        elif isinstance(data_dict, str) or isinstance(data_dict, unicode):
            sql_str = data_dict

        return sql_str


    def _get_update_str(self, data_dict):
        sql_str = ''
        if hasattr(data_dict, "items"):
            l = []
            for k, v in data_dict.items():
                l.append("{0}='{1}'".format(k, v))
            if len(l):
                sql_str = ",".join(l)
            else:
                sql_str = ''

        return sql_str

    @coroutine
    def select(self, table, fields='*', condition=None, offset=0, limit=10):
        """查询多条"""
        where_str = self._conditions(condition)
        # offlit_str = """LIMIT %s,%s; """ % (self._offset, self._limit) if self._limit else ''
        offlit_str = " LIMIT {0} OFFSET {1}; ".format(limit, offset)
        select_str = "SELECT {0} FROM {1} ".format(fields, table)
        res = yield self.db.query(select_str + where_str + offlit_str)
        raise Return(res)

    @coroutine
    def find(self, table, fields='*', condition=None):
        """查询单条"""
        where_str = self._conditions(condition)
        select_str = "SELECT {0} FROM {1} ".format(fields, table)
        res = yield self.db.get(select_str + where_str)
        raise Return(res)

    @coroutine
    def count(self, table, condition=None):
        """统计条数"""
        where_str = self._conditions(condition)
        count_str = "SELECT count(1) as num FROM {0} {1}".format(table, where_str)
        res = yield self.db.get(count_str)
        if res:
            rv = res['num']
        else:
            rv = 0
        raise Return(rv)

    @coroutine
    def insert_one(self, table, data_dict, return_id=False):
        """
        插入数据
        :param table: 表名
        :param data_dict: 插入的数据
        :return: True or False
        """
        sql_str = "INSERT INTO {0}".format(table)
        insert_str = self._get_insert_str(data_dict)
        if not return_id:
            res = yield self.db.execute(sql_str + insert_str)
        else:
            _res = yield self.db.execute_return(sql_str + insert_str + " RETURNING id")
            res = _res.id
        raise Return(res)

    @coroutine
    def update(self, table, data_dict, condition):
        """
        更新数据
        :param table: 表名
        :param data_dict: 要更新的数据
        :param condition: 更新条件
        :return: True or False
        """
        update_str = self._get_update_str(data_dict)
        condition_str = self._conditions(condition)
        sql_str = "UPDATE {0} SET {1} {2}".format(table, update_str, condition_str)
        res = yield self.db.execute(sql_str)
        raise Return(res)



class CacheMixin(object):
    """
    缓存接口数据，handler级的缓存
    思路来源于 http://liyangliang.me/posts/2015/11/cache-response-in-tornado-and-flask/
    """
    def _generate_key(self):
        key = pickle.dumps((self.request.path, self.request.arguments))
        return self._with_prefix(hashlib.sha1(key).hexdigest())

    def _with_prefix(self, key):
        return '%s:%s' % (self.request.path.strip('/'), key)

    def write_cache(self, chunk):
        super(CacheMixin, self).write(chunk)

    def prepare(self):
        super(CacheMixin, self).prepare()
        key = self._generate_key()
        cached = cache.get(key)
        if cached is not None:
            self.log.info('Cache is HIT')
            self.write_cache(pickle.loads(cached))
            self.finish()

    def write(self, chunk):
        key = self._generate_key()
        expiration = getattr(self, 'expiration', 300)
        cache.set(key, pickle.dumps(chunk), expiration)
        super(CacheMixin, self).write(chunk)



def set_cache_timeout(expiration=300):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(handler, *args, **kwargs):
            handler.expiration = expiration
            return func(handler, *args, **kwargs)

        return wrapper

    return decorator