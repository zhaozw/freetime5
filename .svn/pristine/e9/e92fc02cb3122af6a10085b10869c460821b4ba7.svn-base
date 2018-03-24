# -*- coding=utf-8 -*-
"""
@file  : test
@date  : 2016-11-10
@author: GongXiaobo
"""

from datetime import datetime
import time


def check_taskId(msg, result, name):
    val = msg.getParamInt(name, 0)
    if val <= 0:
        return None, 'the param %s = %s error !' % (name, val)
    return val, None


def check_itemId(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_updateTime(msg, result, name):
    val = msg.getParamStr(name, '')
    try:
        val = int(time.mktime(datetime.strptime(val, '%Y-%m-%d %H:%M:%S').timetuple()))
    except:
        return None, 'the param %s error, must be "YYYY-MM-DD HH:MM:SS"' % (name)
    return val, None


def check_progress(msg, result, name):
    val = msg.getParamInt(name, -1)
    if val < 0:
        return None, 'the param %s error, must be integer' % (name)
    return val, None


def check_productId(msg, result, name):
    val = msg.getParamStr(name, '')
    if not val:
        return None, 'the param %s error' % (name)
    return val, None


def check_buyType(msg, result, name):
    val = msg.getParamStr(name, '')
    if not val:
        return None, 'the param %s error' % (name)
    return val, None


def check_count(msg, result, name):
    val = msg.getParamInt(name, 0)
    if val <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_unitType(msg, result, name):
    val = msg.getParamInt(name, 0)
    if val <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_price(msg, result, name):
    val = msg.getParamFloat(name, 0)
    if val <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_orderId(msg, result, name):
    val = msg.getParamStr(name, '')
    if not val:
        return None, 'the param %s error' % (name)
    return val, None


def check_prodRmd(msg, result, name):
    val = msg.getParamFloat(name, 0)
    return val, None


def check_prodDiamond(msg, result, name):
    val = msg.getParamInt(name, 0)
    return val, None


def check_exchangeId(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None
