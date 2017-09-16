#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: validator.py
@time: 2017/7/12 下午4:56
"""
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