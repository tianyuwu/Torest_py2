#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: common.py
@time: 2017/7/22 下午3:26
"""
import logging
import os
from tornado.gen import coroutine
from tornado.web import asynchronous

from ext.qiniu_uploader import get_file_extension, get_file_md5, upload_from_path, bucket_url
from handlers import BaseHandler


class UploadFileHandler(BaseHandler):

    def get(self):
        html_str = """<form action="/upload" method="post" enctype="multipart/form-data">
                        <input type="file" name="file">
                        <button type="submit">上传</button>
                    </form>"""
        self.write(html_str)

    @asynchronous
    @coroutine
    def post(self):
        """先写入文件，再上传到七牛"""
        upload_file = self.request.files.get('file', "")
        if not upload_file:
            logging.error("file error")
            self.write_json(203, 'file error')
            return

        upload_file = upload_file[0]
        file_name = upload_file.get('filename', '').encode("utf-8")
        file_ext = get_file_extension(file_name)
        if not file_ext:
            logging.error("file ext error")
            self.write_json(204, "file ext error")
            return

        file_path = None
        file_md5 = None

        file_buffer = upload_file.get("body")
        if file_buffer:
            file_path = "/tmp/" + file_name
            with open(file_path, "wb") as f:
                f.write(file_buffer)

            if os.path.exists(file_path):
                file_md5 = get_file_md5(file_path) + "." + file_ext

                file_path = file_path

        if not file_path or not file_md5:
            logging.error("file error")
            self.write_json(205, "file error")
            return

        ret, info = upload_from_path(file_md5, file_path)
        logging.info(info)
        logging.info(ret)

        if not ret:
            self.write_json(206, "upload qiniu error!")
            return
        #
        data = {
            "url": bucket_url.get("huimouke") + file_md5
        }
        self.write_json(100, data)