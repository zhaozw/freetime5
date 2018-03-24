# -*- coding=utf-8 -*-
'''
Created on 2017年11月8日

@author: zqh
'''
from tuyoo5.core import tyglobal, tyconfig


def check_playMode1(msg, _result, _name):
    val = msg.getParamStr('play_mode', None)
    if not val:
        return None, 'the param play_mode = %s error !' % (val)
    return val, None


def check_playMode2(msg, _result, _name):
    val = msg.getParamStr('play_mode', None)
    return val, None


def check_roomId0(msg, _result, _name):
    val = msg.getParamInt('roomId', 0)
    val = 0 if val < 0 else val
    return val, None


def check_roomId(msg, _result, name):
    val = msg.getParamInt(name, 0)
    if not val:
        return None, 'the param %s = %s error !' % (name, val)
    room = tyglobal.rooms().get(val)
    if not room:
        return None, 'the param %s = %s room instance not found error !' % (name, val)
    return val, None


def check_tableId0(msg, _result, _name):
    val = msg.getParamInt('tableId', 0)
    val = 0 if val < 0 else val
    return val, None


def check_tableId(msg, _result, name):
    tableId = msg.getParamInt(name, 0)
    if not tableId:
        return None, 'the param %s = %s error !' % (name, tableId)
    roomId = tyconfig.getTableRoomId(tableId)
    room = tyglobal.rooms().get(roomId)
    if not room:
        return None, 'the param %s = %s tableid\'s room instance not found error !' % (name, tableId)
    if not room.maptable.get(tableId):
        return None, 'the param %s = %s (%s) table instance not found error !' % (name, tableId, roomId)
    return tableId, None


def check_seatId0(msg, _result, _name):
    val = msg.getParamInt('seatId', 0)
    val = 0 if val < 0 else val
    return val, None


def check_seatIdObserver(msg, _result, _name):
    val = msg.getParamInt('seatId', -1)
    val = 0 if val < 0 else val
    return val, None


def check_action(msg, _result, _name):
    val = msg.getParamStr(_name)
    return val, None
