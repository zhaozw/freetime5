# -*- coding=utf-8 -*-
'''
Created on 2018年1月31日

@author: lx
'''

import Queue

from dig.plugins.srvtable._private import _rpc_user_info
from freetime5.util import ftlog, fttime, ftstr
from tuyoo5.core import tyglobal, tyrpcconn
from dig.plugins.srvtable.table import TYTable
from freetime5.util.ftmsg import MsgPack


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

tableId = 0

def createNewTable(userId_A, userId_B):
    for roomId, roomIns in tyglobal.rooms().items():
        if _DEBUG:
            debug("In createNewTable @@@@ roomId = ", roomId, " roomIns = ", roomIns, " userId_A = ",
                  userId_A, " userId_B = ", userId_B)
        global tableId
        if not roomIns.maptable:
            baseid = roomId * 10000 + 1
            tableId = baseid
        if tableId >= roomId * 10000 + 9999:
            tableId = roomId * 10000 + 1
        tableId += 1
        tblIns = TYTable(roomIns, tableId)
        roomIns.maptable[tableId] = tblIns
        table_Info = {}
        for userId in [userId_A, userId_B]:
            name, purl, sex, addr, citycode = _rpc_user_info.getUserBaseInfo(userId)
            table_Info[userId] = (name, purl, sex, addr, citycode)

        tblIns.playersInfo = table_Info

        time_seed = fttime.getCurrentTimestamp()

        mo = MsgPack()
        mo.setCmd('start_game')
        mo.setResult('gameId', tyglobal.gameId())
        mo.setResult('roomId', tblIns.roomId)
        mo.setResult('tableId', tblIns.tableId)
        mo.setResult('seatId', 1)
        mo.setResult('time_seed', time_seed)
        mo.setResult('table_info', table_Info)
        if _DEBUG:
            debug("OUT createNewTable  @@@ table_info = ", table_Info)
        tyrpcconn.sendToUser(userId_A, mo)

        mo = MsgPack()
        mo.setCmd('start_game')
        mo.setResult('gameId', tyglobal.gameId())
        mo.setResult('roomId', tblIns.roomId)
        mo.setResult('tableId', tblIns.tableId)
        mo.setResult('seatId', 2)
        mo.setResult('time_seed', time_seed)
        mo.setResult('table_info', table_Info)
        if _DEBUG:
            debug("OUT createNewTable  @@@ table_info = ", table_Info)
        tyrpcconn.sendToUser(userId_B, mo)
        break

