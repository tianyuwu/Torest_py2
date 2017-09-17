#!/usr/bin/env python
# encoding: utf-8
from tornado.gen import coroutine, Return


class BaseModel(object):
    """
    封装数据库的操作 get, query, execute
    """
    def _conditions(self, condition):
        """
        查询条件，支持两种方式，字典和字符串，字符串需要用到单引号
        eg： user_model.conditions("nick_name='Whitney'").find()
            or 
            user_model.conditions({"nick_name":"Whitney"}).find()
        """
        condition_sql = ''
        if hasattr(condition, "items"):
            # mapping objects
            query = condition.items()
            l = []
            # preserve old behavior
            for k, v in query:
                if v:
                    l.append(k + '=' + "'{}'".format(v))
            if len(l):
                condition_sql = "where "+' AND '.join(l)
            else:
                condition_sql = ''

        elif isinstance(condition, str) or isinstance(condition, unicode):
            condition_sql = "WHERE " + condition

        return condition_sql

    def _insert_str(self, condition):
        """
        组合插入的sql
        """
        sql_str = ''
        if hasattr(condition, "items"):
            # mapping objects
            query = condition.items()
            fields = []
            values = []
            # preserve old behavior
            for k, v in query:
                fields.append(k)
                values.append(v)

            if not len(fields):
                self.log.error('sql错误！')
            else:
                fields_str = ','.join(fields)
                values_str = "','".join(values)
                sql_str = """(%s) VALUES ('%s')""" % (fields_str, values_str)

        elif isinstance(condition, str) or isinstance(condition, unicode):
            sql_str = condition

        return sql_str


    @coroutine
    def select(self, table, fields='*', condition=None, offset=0, limit=10):
        """查询多条"""
        where_str = self._conditions(condition)
        # offlit_str = """LIMIT %s,%s; """ % (self._offset, self._limit) if self._limit else ''
        offlit_str = " OFFSET %s LIMIT %s; " % (offset, limit)
        select_str = "SELECT %s FROM %s " % (fields, table)
        res = yield self.db.query(select_str + where_str + offlit_str)
        raise Return(res)

    @coroutine
    def find(self, table, fields='*', condition=None):
        """查询单条"""
        where_str = self._conditions(condition)
        select_str = "SELECT %s FROM %s " % (fields, table)
        res = yield self.db.get(select_str+where_str)
        raise Return(res)

    @coroutine
    def count(self, table, condition=None):
        """统计条数"""
        where_str = self._conditions(condition)
        count_str = """SELECT count(1) as num FROM %s %s""" % (table, where_str)
        res = yield self.db.get(count_str)
        if res:
            rv = res['num']
        else:
            rv = 0
        raise Return(rv)

    @coroutine
    def insert_one(self, table, data_dict):
        """插入语句"""
        sql_str = """INSERT INTO %s """ % table
        insert_str = self._insert_str(data_dict)
        res = yield self.db.execute(sql_str+insert_str)
        raise Return(res)