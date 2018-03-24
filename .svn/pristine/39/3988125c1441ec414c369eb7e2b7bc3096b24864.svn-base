# -*- coding: utf-8 -*-
'''
Created on 2017年7月19日

@author: zqh
'''
from datetime import datetime
import time


def check_itemId(msg, result, name):
    val = msg.getParamInt(name, 0)
    return val, None


def check_kindGameId(msg, result, name):
    val = msg.getParamInt(name, 0)
    return val, None


def check_action(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) <= 0:
        return None, 'the %s can not be empty' % (name)
    return val, None


def check_params(msg, result, name):
    val = msg.getParam(name, {})
    if not isinstance(val, dict):
        return None, 'the %s must be dict or None' % (name)
    return val, None


def check_count(msg, result, name):
    val = msg.getParamInt(name, 0)
    if val <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_kindId(msg, result, name):
    val = msg.getParamInt(name, 0)
    return val, None


def check_intEventParam(msg, result, name):
    val = msg.getParamInt(name, 0)
    if val < 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_createTime(msg, result, name):
    val = msg.getParamStr(name, '')
    try:
        val = int(time.mktime(datetime.strptime(val, '%Y-%m-%d %H:%M:%S').timetuple()))
    except:
        return None, 'the param %s error, nust be "YYYY-MM-DD HH:MM:SS"' % (name)
    return val, None


def check_expires(msg, result, name):
    val = msg.getParamStr(name, '')
    try:
        val = int(time.mktime(datetime.strptime(val, '%Y-%m-%d %H:%M:%S').timetuple()))
    except:
        return None, 'the param %s error, nust be "YYYY-MM-DD HH:MM:SS"' % (name)
    return val, None
