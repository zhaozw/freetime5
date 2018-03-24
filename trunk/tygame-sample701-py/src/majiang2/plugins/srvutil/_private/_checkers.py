# -*- coding=utf-8 -*-
'''
Created on 2017年11月8日

@author: zqh
'''


def check_playMode1(msg, _result, _name):
    val = msg.getParamStr('play_mode', None)
    if not val:
        return None, 'the param play_mode = %s error !' % (val)
    return val, None


def check_playMode2(msg, _result, _name):
    val = msg.getParamStr('play_mode', None)
    return val, None


def check_roomId0(msg, result, name):
    val = msg.getParamInt('roomId', 0)
    val = 0 if val < 0 else val
    return val, None


def check_tableId0(msg, result, name):
    val = msg.getParamInt('tableId', 0)
    val = 0 if val < 0 else val
    return val, None
