# -*- coding=utf-8 -*-
'''
Created on 2018年2月6日

@author: lx
'''

# import Queue
from casualmatch.plugins.srvutil._private import _rpc_user_info
from freetime5.util import ftlog
from casualmatch.plugins.srvutil._private._matchqueue import DaoCasualGameMatch
from tuyoo5.core.typlugin import getRpcProxy
from tuyoo5.core.typlugin import RPC_CALL_SAFE
from tuyoo5.core.typlugin import RPC_TARGET_MOD_ONE
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tyrpcconn

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

gameIdList = [601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612]

def doMatchLoopVS():
    doCasualMatchGameVSPlayer()
    # doCasualBigMatchVSPlayer()
    doBigMatchVSPlayer()
    doCheckTimeOut()

def doCasualMatchGameVSPlayer():
    for gameId in gameIdList:
        while DaoCasualGameMatch.getMatchGameQueueLength(gameId) >= 2:
            player_A_userId, player_B_userId = DaoCasualGameMatch.getMatchGameQueueUsers(gameId)
            if _DEBUG:
                debug("doCasualMatchGameVSPlayer @@@@ gameid = ", gameId, "player_A_userId", player_A_userId, "player_B_userId", player_B_userId)
            rpcproxy = getRpcProxy(gameId, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
            rpcproxy.srvutil.doMatchCasualGamePlayers(player_A_userId, player_B_userId)
            
            mo = MsgPack()
            mo.setCmd('match_result')
            mo.setResult('gameId', gameId)
            mo.setResult('other_userId', player_B_userId)
            mo.setResult('result', 'match success')
            tyrpcconn.sendToUser(player_A_userId, mo)

            mo = MsgPack()
            mo.setCmd('match_result')
            mo.setResult('gameId', gameId)
            mo.setResult('other_userId', player_A_userId)
            mo.setResult('result', 'match success')
            tyrpcconn.sendToUser(player_B_userId, mo)


# def doCasualBigMatchVSPlayer():
#     while DaoCasualGameMatch.getBigMatchQueueLength() >= 2:
#         player_A_userId, player_B_userId = DaoCasualGameMatch.getBigMatchQueueUsers()
#         sendBigMatchMsgToPlayers(player_A_userId, player_B_userId)

def doBigMatchVSPlayer():
    DaoCasualGameMatch.getBigMatchQueueUsersHash()


def doFriendMatch(userId_a, userId_b, gameId):
    if _DEBUG:
        debug("doFriendMatch @@@@ gameId =", gameId, " userId_a =", userId_a, " userId_b =", userId_b)
    rpcproxy = getRpcProxy(gameId, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
    rpcproxy.srvutil.doMatchCasualGamePlayers(userId_a, userId_b)

def doCheckTimeOut():
    if _DEBUG:
        debug("In doCheckMatchQueueTimeOut @@@")
    DaoCasualGameMatch.doCheckBigMatchQueueTimeOut()


# player_queue = []
#
# def doMatchVSPlayers():
#     while player_queue.qsize() >= 2:
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

