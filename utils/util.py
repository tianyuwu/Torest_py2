#!/usr/bin/env python
# encoding: utf-8
import re
import string
import random
import bcrypt
import hmac
from datetime import date, datetime
import time

import os


def get_model_table(str):
    """
    获取模型类对应的表名，大驼峰字符串转换为小写加下划线格式, 如果最后一个为Model，则去掉
    eg: UserInfo => user_info
    :return: str
    """
    _word_list = re.findall(r'[A-Z][a-z]+', str)
    word_list = _word_list[:-1]
    new_str = "_".join(word_list).lower()
    return new_str


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
    生成随机字符串
    :param size:
    :param chars:
    :return:
    """
    return ''.join(random.choice(chars) for _ in range(size))



def encryp_password(password):
    """密码加密"""
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed


def verify_passwrd(password, hashed):
    """密码验证"""
    # Validating a hash (don't use ==)
    print 'password is',password
    print 'hashed is',hashed
    if (hmac.compare_digest(bcrypt.hashpw(password, hashed), hashed)):
        # Login successful
        return True
    else:
        return False

def trans_db_time(db_datetime, pattern='%Y-%m-%d %H:%M:%S'):
    """
    datetime
    :param db_datetime: 
    :param pattern: 
    :return: 
    """
    if not db_datetime:
        return '较早时间'
    return trans_db_datetime(db_datetime, pattern)

def trans_db_datetime(dbdatetime, pattern='%Y-%m-%d %H:%M:%S'):
    if isinstance(dbdatetime, datetime):
        datestr =  dbdatetime.strftime(pattern)
    else:
        datestr = dbdatetime
    return datestr


def get_datetime(timestamp=None):
    if timestamp is None:
        return time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
    else:
        return time.strftime('%Y-%m-%d %H:%M',time.localtime(timestamp))

def calculate_age(born):
    """
    根据生日计算年龄
    :param born:  出生日期
    :return: 
    """
    if isinstance(born, int):
        return born
    if not isinstance(born, date):
        born = datetime.strptime(born, "%Y-%m-%d").date()
    today = date.today()
    try:
        birthday = born.replace(year=today.year)
    except ValueError:
        # raised when birth date is February 29
        # and the current year is not a leap year
        birthday = born.replace(year=today.year, day=born.day-1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year

def calculate_born_year(age):
    """
    根据年龄计算生日
    :param age:  出生年龄
    :return: 
    """
    today = date.today()
    now_year = today.year
    return now_year-int(age)


def member_info_finished_ratio(member_info):
    """计算用户信息完成度"""
    score = 0
    for key,val in member_info.items():
        if isinstance(val, str) or isinstance(val, int):
            if val:
                # print '1:',key
                score += 3
        elif isinstance(val, list):
            # print '2:',key
            if len(val):
                score += len(val) + 3
        # else:
            # print '3:',key
    if score >= 100:
        score = 100
    return score


def generate_rand_code(length=6):
    """
    随机产生一个手机校验码字符串，6位全数字
    """
    rdcode = []
    first = True
    random.seed(str(time.time())+os.urandom(32))
    while len(rdcode) < length:
        if first is True:
            rnum = str(random.randint(0, 9))
            first = False
        else:
            rnum = random.choice(string.digits)

        rdcode.append(rnum)

    return ''.join(rdcode)


def get_time_stamp(timestr):
    """
    就是time.time()得到的时间，
    这个是从'%Y-%m-%d %H:%M:%S'格式转换为18289423.23这种格式，用于计算时间间隔
    :param timestr:
    :return:
    """
    if timestr is None:
        return 0
    return time.mktime(time.strptime(str(timestr), '%Y-%m-%d %H:%M:%S'))