#!/usr/bin/env python
# encoding: utf-8
"""
@version: 0.1
@author: whitney
@file: wechat.py
@time: 2017/7/19 下午10:00
依赖wechatpy实现微信公众号开发
todo:
1. 签名校验
2. accesstoken,和js-sdk用的ticket处理

"""
import functools
import logging

from wechatpy import WeChatClient
from wechatpy.oauth import WeChatOAuth
from config import WECHAT_APPID, WECHAT_SECRET, WECHAT_OAUTH_URL, WECHAT_IGNORE
from tornado.gen import coroutine, Return

wechat_oauth_client = WeChatOAuth(WECHAT_APPID, WECHAT_SECRET, WECHAT_OAUTH_URL, scope='snsapi_userinfo')

wechat_client = WeChatClient(WECHAT_APPID, WECHAT_SECRET)


def refresh_sdtoken():
    """定时任务，更新微信的access_token"""
    res = wechat_client.fetch_access_token()
    print res


def wx_auth(method):
    """装饰器，在微信登录的回调handler中使用"""
    @functools.wraps(method)
    @coroutine
    def warpper(self, *args, **kwargs):
        code = self.get_argument('code', None)
        if code:
            if WECHAT_IGNORE:
                user_info = {"province": "四川", "openid": "onsVNw7iwW9stXNYW0QbGaAXxwEg",
                             "unionid":"onsVNw7iwW9stXNYW0QbGaAXxwEg",
                             "headimgurl": "http://wx.qlogo.cn/mmopen/ajNVdqHZLLB8ibNHDiaoO9wicacjDmuaiaVasiasOlia0Wia\
                                           ntvbTVdP74miarTs9BRxWWt9SMICiaCI9TeNnv6I6Z2Qplg/0",
                             "language": "zh_CN",
                             "city": "成都", "country": "中国", "sex": 1, "privilege": [], "nickname": "Whitney"}

                self.wechat_info = user_info
            else:
                try:
                    # 根据code获取access_token
                    res = wechat_oauth_client.fetch_access_token(code)
                    print '[wechat fetch_access_token]%s' % res
                    user_info = wechat_oauth_client.get_user_info()

                except Exception as e:
                    print e.errmsg, e.errcode
                    # 这里需要处理请求里包含的 code 无效的情况
                    self.write_json(e.errcode, e.errmsg)
                    return
                else:
                    self.wechat_info = user_info

        rv = yield method(self, *args, **kwargs)
        raise Return(rv)

    return warpper