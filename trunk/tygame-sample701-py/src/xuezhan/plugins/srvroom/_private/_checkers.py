# -*- coding=utf-8 -*-
'''
Created on 2017年11月8日

@author: zqh
'''


def check_roomId(msg, result, name):
    val = msg.getParamInt(name, 0)
    if val <= 0:
        return None, 'the param %s = %s error !' % (name, val)
    return val, None
