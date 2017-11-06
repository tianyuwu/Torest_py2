#!/usr/bin/env python
# encoding: utf-8
"""
参考https://github.com/vsouza/JWT-Tornado，实现了token的fresh
token校验： 装饰器 @jwt_auth()
1. access_token校验时不带参数
2. 校验fresh_token，@jwt_auth(token_type='fresh')
3. 当接口不是非必须进行校验的话，required参数设为False， @jwt_auth(required=False)
获取token中存储的信息： self.identify
生成token:  create_token(identify)
"""
import datetime
import uuid

import jwt

secret_key = "my_secret_key"
token_expire_delta = datetime.timedelta(seconds=3600)
refresh_token_expire_delta = datetime.timedelta(seconds=3600*24*30)
algorithm = 'HS256'

options = {
    'verify_signature': True,
    'verify_exp': True,
    'verify_nbf': False,
    'verify_iat': True,
    'verify_aud': False
}

def jwt_auth(token_type="access", required=True):
    def decorator(handler_class):
        ''' Handle Tornado JWT Auth '''
        def wrap_execute(handler_execute):
            def require_auth(handler, kwargs):

                auth = handler.request.headers.get('Authorization')
                if auth:
                    parts = auth.split()
                    print parts

                    if parts[0].lower() != 'bearer' or len(parts) !=2:
                        handler._transforms = []
                        handler.set_status(401)
                        handler.write("invalid header authorization")
                        handler.finish()

                    token = parts[1]
                    try:
                        data = jwt.decode(
                            token,
                            secret_key,
                            options=options
                        )
                        if data['type'] != token_type:
                            handler.set_status(401)
                            handler.write('Only {} tokens can access this endpoint'.format(token_type))
                            handler.finish()

                        handler.identify = data.get('identity','')

                    except Exception, e:
                        handler._transforms = []
                        handler.set_status(401)
                        handler.write(e.message)
                        handler.finish()
                elif required:
                    handler._transforms = []
                    handler.set_status(401)
                    handler.write("Missing authorization")
                    handler.finish()
                else:
                    handler.identify = None

                return True

            def _execute(self, transforms, *args, **kwargs):

                try:
                    require_auth(self, kwargs)
                except Exception:
                    return False

                return handler_execute(self, transforms, *args, **kwargs)

            return _execute

        handler_class._execute = wrap_execute(handler_class._execute)
        return handler_class
    return decorator


def create_token(identity, fresh=False, token_type='access'):
    now = datetime.datetime.utcnow()
    uid = str(uuid.uuid4())
    token_data = {
        'exp': now + (token_expire_delta if token_type == 'access' else refresh_token_expire_delta),
        'iat': now,
        'nbf': now,
        'jti': uid,
        'identity': identity,
        'fresh': fresh,
        'type': token_type,
    }
    encoded_token = jwt.encode(token_data, secret_key, algorithm).decode('utf-8')
    return encoded_token