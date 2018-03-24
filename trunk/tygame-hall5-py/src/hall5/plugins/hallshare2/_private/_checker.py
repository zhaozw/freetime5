# -*- coding: utf-8 -*-
'''
Created on 2017年12月25日

@author: lixi
'''

def check_pointId(msg, result, name):
    pointId = msg.getParamInt(name, -1)
    if pointId <= 0:
        return None, 'the param %s is error' % (name)
    return pointId, None

def check_urlParams(msg, result, name):
    val = msg.getParam(name, {})
    if not isinstance(val, dict):
        return None, 'the %s must be dict or None' % (name)
    return val, None

def check_shareId(msg, result, name):
    shareId = msg.getParamInt(name, -1)
    if shareId <= 0:
        return None, 'the param %s is error' % (name)
    return shareId, None