#!/usr/bin/env python
# encoding: utf-8
import json
import logging

from ext.rly_sms import REST
from utils import util


class RL_SMSService(object):
    # 主帐号
    accountSid = 'your accountSid'
    # 主帐号Token
    accountToken = 'your accountToken'
    # 应用Id
    appId = 'your appId'
    # 请求地址，格式如下，不需要写http://
    serverIP = 'app.cloopen.com'
    # 请求端口
    serverPort = '8883'
    # REST版本号
    softVersion = '2013-12-26'
    # REST
    rest = None

    def __init__(self):
        # 初始化REST SDK
        self.rest = REST(self.serverIP, self.serverPort, self.softVersion)
        self.rest.setAccount(self.accountSid, self.accountToken)
        self.rest.setAppId(self.appId)

    def send_sms(self, targettel, tplid, datas):
        """
        返回值：{"res_code":0,"identifier":"XH7334","create_at":"1429600387"}
        """
        utf8datas = []
        for data in datas:
            utf8datas.append(data.encode('utf-8'))
        result = self.rest.sendTemplateSMS(targettel, utf8datas, tplid)
        result = result['Response']
        try:
            if result['statusCode'] == '000000':
                logging.info('荣联云短信发送 %s 成功：%s' % (targettel, json.dumps(result)))
                res = {"res_code": 0}
            else:
                logging.error('Error 荣联云短信发送 %s 失败：%s' % (targettel, json.dumps(result)))
                res = {"res_code": 1, "msg": result['statusMsg']}
            return res
        except Exception, e:
            print repr(e)
            return {"res_code": 1}


sms = RL_SMSService()