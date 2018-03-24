# -*- coding=utf-8 -*-
'''
Created on 2018年1月31日

@author: lx
'''

# import Queue
from crosselimination.plugins.srvutil._private import _rpc_user_info
from freetime5.util import ftlog, fttime
from tuyoo5.core.typlugin import gameRpcRoomOne
from tuyoo5.core import tyglobal, tyrpcconn
from random import choice
from freetime5.util.ftmsg import MsgPack

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


# player_queue = []
#
# def doMatchVSPlayers():
#     while len(player_queue) >= 2:
#         player_A_userId = player_queue.pop(0)
#         player_B_userId = player_queue.pop(0)
#         if _DEBUG:
#             debug("doMatchVSPlayers @@@@ player_A_userId", player_A_userId, "player_B_userId", player_B_userId)
#         #随机取出roomId
#         roomid_key = choice(tyglobal.bigRoomIdsMap().keys())
#         roomid = choice(tyglobal.bigRoomIdsMap()[roomid_key])
#         #随机取出shadowRoomId
#         allrooms = tyglobal.roomIdDefineMap()
#         shadowRoomId = choice(allrooms[roomid].shadowRoomIds)
#         if _DEBUG:
#             debug("IN doMatchVSPlayers @@@ roomid = ", roomid, " shadowRoomId = ", shadowRoomId)
#
#         gameRpcRoomOne.srvtable.doCreateNewTable(shadowRoomId, player_A_userId, player_B_userId)


util_match_map = {}
match_count = 0

def saveUtilMatchInfo(userId_A, userId_B):
    global match_count
    match_count += 1
    util_match_map[match_count] = {userId_A: 0, userId_B: 0}

    mo = MsgPack()
    mo.setCmd('bind_game')
    mo.setResult('gameId', tyglobal.gameId())
    mo.setResult('match_count', match_count)

    time_seed = fttime.getCurrentTimestamp()
    mo.setResult('time_seed', time_seed)

    table_Info = {}
    for userId in [userId_A, userId_B]:
        name, purl, sex, addr, citycode = _rpc_user_info.getUserBaseInfo(userId)
        table_Info[userId] = (name, purl, sex, addr, citycode)

    mo.setResult('table_info', table_Info)

    tyrpcconn.sendToUser(userId_A, mo)
    tyrpcconn.sendToUser(userId_B, mo)


def updateUtilMatchStatus(match_count, userId):
    if util_match_map.has_key(match_count):
        util_match_map[match_count][userId] = 1
        start = 1
        userId_b = 0
        for uid, status in util_match_map[match_count].items():
            if _DEBUG:
                debug("IN updateUtilMatchStatus @@@ in LOOP:  userId = ", userId, " status = ", status)
            if status == 0:
                start = 0
                break
            if uid != userId:
                userId_b = uid
                if _DEBUG:
                    debug("IN updateUtilMatchStatus @@@ userId_b = ", userId_b)

        if start == 1:
            #随机取出roomId
            roomid_key = choice(tyglobal.bigRoomIdsMap().keys())
            roomid = choice(tyglobal.bigRoomIdsMap()[roomid_key])
            #随机取出shadowRoomId
            allrooms = tyglobal.roomIdDefineMap()
            shadowRoomId = choice(allrooms[roomid].shadowRoomIds)
            if _DEBUG:
                debug("IN updateUtilMatchStatus @@@ roomid = ", roomid, " shadowRoomId = ", shadowRoomId,
                      "userId_a =", userId, "userId_b =", userId_b)

            gameRpcRoomOne.srvtable.doCreateNewTable(shadowRoomId, userId, userId_b)

