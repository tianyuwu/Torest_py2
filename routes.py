#!/usr/bin/env python
# encoding: utf-8

from handlers import user, DefaultHandler

handlers = [
    (r"/", user.IndexHandler),
    (r"/testparam", user.GetParamHandler),
    (r"/testquery", user.QueryHandler),
    (r"/testdao", user.DAOHandler),
    (r".*", DefaultHandler)
]