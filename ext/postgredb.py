#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
实现了crud操作，并且返回内容支持两种索引方式
"""
import momoko
import os
from tornado import gen
from psycopg2.extras import RealDictCursor
from tornado.log import app_log

enable_hstore = True if os.environ.get('MOMOKO_TEST_HSTORE', False) == '1' else False


class PostgresDB(object):
    """为降低耦合，改用一个类封装以方便传入参数"""
    def __init__(self, dsn, ioloop):
        self.adb_trans = []
        self.dbpool = momoko.Pool(
            dsn=dsn,
            size=1,
            max_size=3,
            ioloop=ioloop,
            cursor_factory=RealDictCursor,
            setsession=("SET TIME ZONE PRC",),  # 时区设置 SET TIME ZONE UTC
            raise_connect_errors=False,
        )
        # this is a one way to run ioloop in sync
        future = self.dbpool.connect()
        ioloop.add_future(future, lambda f: ioloop.stop())
        ioloop.start()

        if enable_hstore:
            future = self.dbpool.register_hstore()
            # This is the other way to run ioloop in sync
            ioloop.run_sync(lambda: future)

        # 以下代码在Mac中会报错
        # if self.dbpool.server_version >= 90200:
        #     future = self.dbpool.register_json()
        #     # This is the other way to run ioloop in sync
        #     ioloop.run_sync(lambda: future)


    @gen.coroutine
    def find(self, table, fields='*', condition=None, params=None):
        """查询单条"""
        where_str, _params = self.__conditions(condition)
        if not params:
            params = _params
        select_str = "SELECT {0} FROM {1} ".format(fields, table)
        res = yield self.execute('find', select_str + where_str, *params)
        raise gen.Return(res)

    @gen.coroutine
    def select(self, table, fields='*', condition=None, offset=0, limit=10, params=None):
        """查询多条"""
        where_str, _params = self.__conditions(condition)
        if not params:
            params = _params

        select_str = "SELECT {0} FROM {1} {2} LIMIT {3} OFFSET {4}".\
            format(fields, table, where_str, limit, offset)
        res = yield self.execute('select', select_str, *params)
        raise gen.Return(res)

    @gen.coroutine
    def count(self, table, condition=None, params=None):
        """统计条数"""
        where_str, _params = self.__conditions(condition)
        if not params:
            params = _params
        count_str = "SELECT count(1) as num FROM {0} {1}".format(table, where_str)
        res = yield self.execute('find', count_str, *params)
        if res:
            rv = res['num']
        else:
            rv = 0
        raise gen.Return(rv)

    @gen.coroutine
    def insert(self, table, data_dict, return_id=False):
        """
        插入数据
        :param table: 表名
        :param data_dict: 插入的数据
        :return: True or False
        """
        sql_str = "INSERT INTO {0}".format(table)
        insert_str, params = self.__get_insert_str(data_dict)
        if not return_id:
            res = yield self.execute('exec', sql_str + insert_str, *params)
        else:
            _res = yield self.execute('find', sql_str + insert_str + " RETURNING id", *params)
            res = _res['id'] if _res else None
        raise gen.Return(res)

    @gen.coroutine
    def update(self, table, data_dict, condition, params=None):
        """
        更新数据
        :param table: 表名
        :param data_dict: 要更新的数据
        :param condition: 更新条件
        :param params: 传入的参数(list格式)，仅当字符串传入时候需要
        :return: True or False
        """
        update_str, _params = self.__get_update_str(data_dict)
        condition_str, _params1 = self.__conditions(condition)
        if not params:
            _params.extend(_params1)
            params = _params

        sql_str = "UPDATE {0} SET {1} {2}".format(table, update_str, condition_str)
        res = yield self.execute('exec', sql_str, *params)
        raise gen.Return(res)

    @gen.coroutine
    def execute(self, action, sqlstr, *parm):
        """
        发送sql语句，返回执行结果
        """
        rv = True
        try:
            cursor = yield self.dbpool.execute(sqlstr, parm)
            if not cursor:
                rv = False
            else:
                if action == 'exec':
                    rv = True
                elif action == 'find':
                    rv = cursor.fetchone()
                elif action == 'select':
                    rv = cursor.fetchall()

            app_log.info(self.__print_sql(sqlstr, parm))

        except Exception as e:
            error_msg = self.__print_sql(sqlstr, parm) + '\n' + repr(e)
            app_log.error(error_msg)
            rv = False

        finally:
            raise gen.Return(rv)

    def trans_exec(self, sqlstr, *parm):
        """
        进行事务
        :param sqlstr:
        :param parm:
        :return:
        """
        app_log.info(self.__print_sql(sqlstr, parm))
        if not self.adb_trans:
            self.adb_trans = []

        sqltask = [sqlstr, parm]
        self.adb_trans.append(sqltask)

    @gen.coroutine
    def trans_commit(self):
        """
        提交事务
        :return:
        """
        rv = True
        try:
            cursors = yield self.dbpool.transaction(self.adb_trans)
            if not cursors:
                rv = False

        except Exception as e:
            error_msg = '[sql error]' + repr(e)
            app_log.error(error_msg)
            rv = False

        finally:
            self.adb_trans = []
            raise gen.Return(rv)


    def __conditions(self, condition):
        """
        查询条件，支持两种方式，字典和字符串，字符串需要用到单引号
        eg： "nick_name='Whitney'
                or
            {"nick_name":"Whitney"}
        :return 返回sql片段和参数
        """
        condition_sql = ''
        params = ''
        if hasattr(condition, "items"):
            # mapping objects
            query = condition.items()
            l = []
            params = []
            # preserve old behavior
            for k, v in query:
                if v:
                    l.append("{}=%s".format(k))
                    params.append(v)

            if len(l):
                condition_sql = "where "+' AND '.join(l)
            else:
                condition_sql = ''

        elif isinstance(condition, str) or isinstance(condition, unicode):
            condition_sql = "WHERE " + condition

        return condition_sql, params


    def __get_insert_str(self, data_dict):
        """
        组合插入的sql
        """
        sql_str = ''
        params = []
        if hasattr(data_dict, "items"):
            # mapping objects
            query = data_dict.items()
            fields = []
            values = []
            # preserve old behavior
            for k, v in query:
                fields.append(k)
                values.append('%s')
                params.append(v)

            fields_str = ','.join(fields)
            values_str = ",".join(values)
            sql_str = "({0}) VALUES ({1})".format(fields_str, values_str)

        elif isinstance(data_dict, str) or isinstance(data_dict, unicode):
            sql_str = data_dict

        return sql_str, params

    def __get_update_str(self, data_dict):
        if hasattr(data_dict, "items"):
            l = []
            args = []
            for k, v in data_dict.items():
                l.append("{0}=%s".format(k))
                args.append(v)
            if len(l):
                sql_str = ",".join(l)
            else:
                sql_str = ''
            return sql_str, args

    def __print_sql(self, sqlstr, parm):
        """打印完整的sql语句，方便调试"""
        _parm = []
        if parm:
            for p in parm:
                _parm.append("'%s'" % p)
            outstr = sqlstr % tuple(_parm)
        else:
            outstr = sqlstr

        return 'SQL execute:\n{}'.format(outstr.decode('utf-8'))