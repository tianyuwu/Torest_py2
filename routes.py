#!/usr/bin/env python
# encoding: utf-8

from handlers import user, DefaultHandler, common

handlers = [
    (r"/", user.IndexHandler),
    (r"/testparam", user.GetParamHandler),
    (r"/testquery", user.QueryHandler),
    (r"/testdao", user.DAOHandler),
    (r"/testcache", user.CacheHandler),
    (r"/testforms", user.FormsHandler),
    (r"/upload", common.UploadFileHandler),
    (r".*", DefaultHandler)
]