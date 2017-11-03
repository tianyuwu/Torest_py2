#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: validator.py
@time: 2017/7/12 下午4:56
"""
import collections
import datetime
import functools
import json

from werkzeug.datastructures import MultiDict
from wtforms import Form

class TornadoForm(Form):
    """
    `WTForms` wrapper for Tornado.
    """
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """
        Wrap the `formdata` with the `TornadoInputWrapper` and call the base
        constuctor.
        """
        self._handler = formdata
        if self._handler.request.headers.get("Content-type") == 'application/json':
            json_data = json.loads(self._handler.request.body)
            super(TornadoForm, self).__init__(MultiDict(_flatten_json(json_data)),
                                              obj=obj, prefix=prefix, **kwargs)
        else:
            super(TornadoForm, self).__init__(TornadoInputWrapper(formdata),
            obj=obj, prefix=prefix, **kwargs)

    def error_msg(self):
        """错误信息字符串，方便返回给浏览器"""
        msg = ""
        if self.errors:
            for key,val in self.errors.items():
                msg += "{0}:{1}; ".format(key, val[0])
        return msg

    # def data(self):
    #     """表单信息"""
    #     pass

    # def _get_translations(self):
    #     return TornadoLocaleWrapper(self._handler.get_user_locale())


class TornadoInputWrapper(object):
    def __init__(self, handler):
        self._handler = handler

    def __iter__(self):
        return iter(self._handler.request.arguments)

    def __len__(self):
        return len(self._handler.request.arguments)

    def __contains__(self, name):
        return name in self._handler.request.arguments

    def getlist(self, name):
        return self._handler.get_arguments(name)


class TornadoLocaleWrapper(object):

    def __init__(self, locale):
        self.locale = locale

    def gettext(self, message):
        return self.locale.translate(message)

    def ngettext(self, message, plural_message, count):
        return self.locale.translate(message, plural_message, count)



# 用于解决 WTForms 不支持 json 形式的表单值的问题
def _flatten_json(json, parent_key='', separator='-'):
    """Flattens given JSON dict to cope with WTForms dict structure.
    :param json: json to be converted into flat WTForms style dict
    :param parent_key: this argument is used internally be recursive calls
    :param separator: default separator
    Examples::
        flatten_json({'a': {'b': 'c'}})
        >>> {'a-b': 'c'}
    """
    if not isinstance(json, collections.Mapping):
        return ''

    items = []
    for key, value in json.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(_flatten_json(value, new_key, separator).items())
        elif isinstance(value, list):
            items.extend(_flatten_json_list(value, new_key, separator))
        else:
            value = _format_value(value)
            items.append((new_key, value))
    return dict(items)


def _flatten_json_list(json, parent_key='', separator='-'):
    items = []
    i = 0
    for item in json:
        new_key = parent_key + separator + str(i)
        if isinstance(item, list):
            items.extend(_flatten_json_list(item, new_key, separator))
        elif isinstance(item, dict):
            items.extend(_flatten_json(item, new_key, separator).items())
        else:
            item = _format_value(item)
            items.append((new_key, item))
        i += 1
    return items


def _format_value(value):
    """wtforms 有些 field 只能处理字符串格式的值，无法处理 python/json 类型的值
    此函数把这些无法被处理的值转换成每种字段对应的字符串形式"""
    if value is None:
        return ''
    if isinstance(value, datetime.datetime):
        return value.isoformat().split(".").pop(0)
    if isinstance(value, int) or isinstance(value, float):
        # 若不把数字类型转换为 str ，InputValidator() 会把 0 值视为未赋值，导致验证失败
        return str(value)
    return value


def validate(form_class):
    """
    装饰器，用于验证提交的参数
    :param form_class:
    :return:
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def inner(self, *args, **kwargs):
            form = form_class(self)
            if not form.validate():
                self.write_json(101, form.errors)
                return

            self.form_data = form.data
            return view_func(self, *args, **kwargs)

        return inner

    return decorator