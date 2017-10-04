#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: qiniu_uploader.py
@time: 2017/7/22 下午4:48
"""
import hashlib
import os

from qiniu import Auth, put_file
from qiniu import BucketManager

access_key = 'aO-cPpe664qy_IWLOXu1yVvD6cZWQ-YHHd89bD8Q'
secret_key = 'MaS5J7jreMCslZjPoNzuD_hfYeK0UVN9619SH2OA'
bucket_name = 'huimouke'
bucket_url = {
    "huimouke": "http://opii1dlks.bkt.clouddn.com/",
}

q = Auth(access_key, secret_key)
bucket = BucketManager(q)


def get_file_extension(filename):
    """获取文件的扩展名"""
    end_index = filename.rfind(".")
    if end_index >= 0:
        return filename[end_index + 1:]
    else:
        return ''


def get_file_md5(filename):
    """大文件的MD5值"""
    if not os.path.isfile(filename):
        return None

    md5obj = hashlib.md5()
    f = file(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        md5obj.update(b)
    f.close()

    md5 = md5obj.hexdigest()
    return md5


def upload_from_path(key, localfile):
    """从本地中上传"""
    token = q.upload_token(bucket_name, key, 3600)

    ret, info = put_file(token, key, localfile)
    return ret, info


def upload_from_url(key, url):
    """从url中上传"""
    ret, info = bucket.fetch(url, bucket_name, key)
    return ret, info