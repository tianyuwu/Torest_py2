#!/usr/bin/env python
# encoding: utf-8
# wtforms文档参见http://wtforms.readthedocs.org/en/latest/

import wtforms
from wtforms import validators, Form
from wtforms.validators import ValidationError

from ext.validator import TornadoForm

class TelephoneForm(Form):
    country_code = wtforms.IntegerField('country_code', [validators.required()])
    area_code    = wtforms.IntegerField('area_code', [validators.required()])
    number       = wtforms.StringField('number')


class TestForm(TornadoForm):
    msg = wtforms.StringField('msg',  [validators.Length(min=4, max=23)])
    lst = wtforms.FieldList(wtforms.StringField('lst'))  # 数组
    dit = wtforms.FormField(TelephoneForm)  # 字典判断

    def validate_msg(self, field):
        # 自定义验证器
        if field.data != 'hello world':
             raise ValidationError(u'Must be hello world')