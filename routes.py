#!/usr/bin/env python
# encoding: utf-8

from handlers import user, DefaultHandler

handlers = [
    (r"/", user.IndexHandler),
    (r".*", DefaultHandler)
]