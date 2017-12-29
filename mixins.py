#!/usr/bin/env python
# encoding: utf-8
import hashlib

from ext.rdcache import cache

try:
    import cPickle as pickle
except ImportError:
    import pickle

import functools
from tornado.gen import coroutine, Return


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