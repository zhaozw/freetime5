# -*- coding:utf-8 -*-
"""
Created on 2017年10月27日17:25:40

@author: yzx

GR2GT RPC调用 运行于GT

doStartTable GR调用GT，启动桌子
doClearTable GR调用GT，清理桌子


"""

from freetime5.util import ftlog
from tuyoo5.core import tyglobal



# @rpccore.markRpcCall(groupName='roomId', lockName='', syncCall=0)
def doStartTable(roomId, tableId, info):
    room = tyglobal.rooms()[roomId]

    if room:
        table = room.maptable.get(tableId)
        if table:
            table.startMatchTable(info)
        else:
            ftlog.warn("stage_match_table_remote startTable not find table", tableId)
    else:
        ftlog.warn("stage_match_table_remote startTable not find room", roomId)
    return 0


# @rpccore.markRpcCall(groupName='roomId', lockName='', syncCall=0)
def doClearTable(roomId, tableId, info):
    room = tyglobal.rooms()[roomId]
    if room:
        table = room.maptable.get(tableId)
        if table:
            table.clearMatchTable(info)
        else:
            ftlog.warn("stage_match_table_remote clearTable not find table", tableId)
    else:
        ftlog.warn("stage_match_table_remote clearTable not find room", roomId)
    return 0


# @rpccore.markRpcCall(groupName='roomId', lockName='', syncCall=0)
def doGiveUp(roomId, tableId, userId):
    room = tyglobal.rooms()[roomId]
    if room:
        table = room.maptable.get(tableId)
        if table:
            table.giveUp(userId)
        else:
            ftlog.warn("stage_match_table_remote doGiveUp not find table", tableId)
    else:
        ftlog.warn("stage_match_table_remote doGiveUp not find room", roomId)
    return 0