# -*- coding=utf-8 -*-
'''
Created on 2018年1月31日

@author: lixi
'''
from tuyoo5.core import tyglobal, tyconfig

def check_roomId(msg, _result, name):
    val = msg.getParamInt(name, 0)
    if not val:
        return None, 'the param %s = %s error !' % (name, val)
    room = tyglobal.rooms().get(val)
    if not room:
        return None, 'the param %s = %s room instance not found error !' % (name, val)
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