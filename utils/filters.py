#!/usr/bin/env python
# encoding: utf-8
"""
实现数据的管道过滤操作
"""
import functools

from tornado.gen import coroutine, Return


def filter_db_time(value):
    return 'after filter'

def filter_gender(value):
    return '男' if value==1 else '女'
    # return {"name": text, "value": value}



filters_map = {
    "creation_time": filter_db_time,
    "gender": filter_gender
}


class Filters(object):
    def __init__(self):
        self.filters_map = filters_map


    def filter(self, data, filter_list):
        """字典数据的过滤"""
        if isinstance(filter_list, str):
            filter_list = [filter_list]

        for filter_ins in filter_list:
            if isinstance(data, dict):
                if data.get(filter_ins):
                    data["{}_text".format(filter_ins)] = self.filters_map.get(filter_ins)(data[filter_ins])
            elif isinstance(data, list):
                for row in data:
                    if row.get(filter_ins):
                        row["{}_text".format(filter_ins)] = self.filters_map.get(filter_ins)(row[filter_ins])

        return data


filter_pipe = Filters()


def filter(*filter_list):
    """
    装饰器，用于对返回的数据进行过滤
    :param filter_list:
    :return:
    """
    def decorator(method):
        @coroutine
        @functools.wraps(method)
        def wrap_execute(self, *args, **kwargs):
            data = yield method(self, *args, **kwargs)
            return_data = filter_pipe.filter(data, filter_list)
            raise Return(return_data)
        return wrap_execute
    return decorator