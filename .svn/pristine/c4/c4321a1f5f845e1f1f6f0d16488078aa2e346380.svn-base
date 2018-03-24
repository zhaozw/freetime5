# -*- coding: utf-8 -*-
'''
Created on 2018年2月1日

@author: lixi
'''
import json

from freetime5._tyserver._plugins._rpc2 import getRpcProxy, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE
from freetime5.twisted import ftcore
from freetime5.util import ftlog, fttime
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import typlugin, tyglobal, tyrpcconn
from flipjoy.plugins.srvtable._private import _svrtable_handler
from flipjoy.plugins.srvtable._private import _checker
from tuyoo5.core import tychecker


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

def check_MsgId(msg, result, name):
    MsgId = msg.getParamStr(name, '')
    if MsgId:
        return MsgId, None
    return None, 'the param %s error' % (name)

class CrossEliminationPluginSrvTable(typlugin.TYPlugin):

    def __init__(self):
        super(CrossEliminationPluginSrvTable, self).__init__()
        self.checker1 = tychecker.Checkers(
            tychecker.check_userId,
            tychecker.check_gameId,
            tychecker.check_clientId,
            _checker.check_roomId,
            _checker.check_tableId,
        )
        self.checkStartGameInfo = self.checker1.clone()
        self.checkStartGameInfo.addCheckFun(check_MsgId)

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_TABLE])
    def initPluginBefore(self):
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def getPlayingTableList(self, roomId, msgDict):
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doCreateNewTable(self, roomId, userId_A, userId_B):
        if _DEBUG:
            debug("In doCreateNewTable @@@@@  userid_A = ", userId_A, "  userId_B = ", userId_B)
        _svrtable_handler.createNewTable(userId_A, userId_B)
        return 1

    @typlugin.markPluginEntry(cmd="table/start_game_info", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def startGameInfo(self, msg):
        if _DEBUG:
            debug("In startGameInfo @@@ msg = ", msg)
        mi = self.checkStartGameInfo.check(msg)
        if mi.error:
            ftlog.error('startGameInfo the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            table = room.maptable[mi.tableId]
            if _DEBUG:
                ftlog.debug("IN startGameInfo @@ startGameInfo =", table.playersInfo.keys(), " MsgId = ", mi.MsgId)
            table.tableMsgId = mi.MsgId
            mo = MsgPack()
            mo.setCmd('start_game_info')
            mo.setResult('result', "ok")
            tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd="table/check_existed", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def checkUserExisted(self, msg):
        if _DEBUG:
            debug("In checkUserExisted @@@ msg = ", msg)
        mi = self.checker1.check(msg)
        if mi.error:
            ftlog.error('checkUserExisted the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            if room.maptable.has_key(mi.tableId):
                mo = MsgPack()
                mo.setCmd('check_existed')
                time_seed = fttime.getCurrentTimestamp()
                mo.setResult('time_seed', time_seed)
                mo.setResult('result', "1")
                tyrpcconn.sendToUser(mi.userId, mo)
            else:
                mo = MsgPack()
                mo.setCmd('check_existed')
                time_seed = fttime.getCurrentTimestamp()
                mo.setResult('time_seed', time_seed)
                mo.setResult('result', "0")
                tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd="table/syn_info", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def synClientInfo(self, msg):
        if _DEBUG:
            debug("In synClientInfo @@@ msg = ", msg)
        mi = self.checker1.check(msg)
        if mi.error:
            ftlog.error('synClientInfo the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            table = room.maptable[mi.tableId]
            if _DEBUG:
                ftlog.debug("IN synClientInfo @@ synClientInfo =", table.playersInfo.keys())
            userId_b = 0
            for userid in table.playersInfo.keys():
                if userid != mi.userId:
                    mo = MsgPack()
                    mo.setCmd('syn_info')
                    mo.setResult('gdata', msg.getParamStr('gdata'))
                    if _DEBUG:
                        debug("OUT synClientInfo  @@@ table_info = ", msg)
                    tyrpcconn.sendToUser(userid, mo)
                    userId_b = userid
            if len(table.timerInfo) == 0:
                table.timerInfo[mi.userId] = MiniMatchProcess(7, mi.userId, userId_b, mi.roomId, mi.tableId)
                table.timerInfo[userId_b] = MiniMatchProcess(7, userId_b, mi.userId, mi.roomId, mi.tableId)
            for userid in table.timerInfo.keys():
                if _DEBUG:
                    debug("IN synClientInfo @@@ table_info = ", msg)
                if userid == mi.userId:
                    table.timerInfo[mi.userId].stop()
                    table.timerInfo[mi.userId].start(mi.userId)
        return 1

    @typlugin.markPluginEntry(cmd="table/end_game", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def endCLientGame(self, msg):
        if _DEBUG:
            debug("In synClientInfo @@@ msg = ", msg)
        mi = self.checker1.check(msg)
        if mi.error:
            ftlog.error('endCLientGame the msg params error !', mi.error)
        else:
            #todo 1: add loc 2:客户端上行的第一条end_game消息作为判断依据,对双方结算
            room = tyglobal.rooms()[mi.roomId]
            if room.maptable.has_key(mi.tableId):
                table = room.maptable.pop(mi.tableId)
                for userid in table.playersInfo.keys():
                    mo = MsgPack()
                    mo.setCmd('end_game')
                    mo.setResult('gameResult', msg.getParamStr('gameResult'))
                    if _DEBUG:
                        debug("OUT endCLientGame  @@@ table_info = ", msg)
                    tyrpcconn.sendToUser(userid, mo)

                rpcproxy = getRpcProxy(9993, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
                rpcproxy.srvgame.doReportGameResult(userid, tyglobal.gameId(), msg.getParamStr('gameResult'))
            else:
                pass
                # mo = MsgPack()
                # mo.setCmd('end_game')
                # mo.setResult('result', 'has finished')
                # mo.setResult('msg', msg)
                # if _DEBUG:
                #     debug("OUT endCLientGame  @@@ table_info = ", msg)
                # tyrpcconn.sendToUser(mi.userid, mo)
        return 1

    @typlugin.markPluginEntry(cmd="table/quit_game", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def quitCLientGame(self, msg):
        if _DEBUG:
            debug("In quitCLientGame @@@ msg = ", msg)
        mi = self.checker1.check(msg)
        if mi.error:
            ftlog.error('quitCLientGame the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            loserId = 0
            winnerId =0
            if room.maptable.has_key(mi.tableId):
                table = room.maptable.pop(mi.tableId)
                for userid in table.playersInfo.keys():
                    if userid == mi.userId:
                        loserId = userid
                    else:
                        winnerId = userid

                mo = MsgPack()
                mo.setCmd('end_game')
                msg_dict = {"winnerId":winnerId, "userId_a":loserId, "userId_b":winnerId, "table_msgId":table.tableMsgId}
                mo.setResult('gameResult', json.dumps(msg_dict, separators=(',', ':')))

                # mo.setResult('winnerId', winnerId)
                # mo.setResult('userId_a', loserId)
                # mo.setResult('userId_b', winnerId)
                # mo.setResult('table_msgId', table.tableMsgId)
                if _DEBUG:
                    debug("OUT quitCLientGame  @@@ winnerId = ", winnerId)
                tyrpcconn.sendToUser(winnerId, mo)
                tyrpcconn.sendToUser(loserId, mo)

                mo = MsgPack()
                mo.setResult('winnerId', winnerId)
                mo.setResult('userId_a', loserId)
                mo.setResult('userId_b', winnerId)
                mo.setResult('table_msgId', table.table_msgId)

                rpcproxy = getRpcProxy(9993, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
                rpcproxy.srvgame.doReportGameResult(winnerId, tyglobal.gameId(), mo.pack())
            else:
                pass
        return 1

class MiniMatchProcess(object):
    def __init__(self, interval, userId_a, userId_b, roomId, tableId):
        self._interval = interval
        self._roomId = roomId
        self._tableId = tableId
        self.userId_a = userId_a
        self.userId_b = userId_b
        self.winnerId = 0
        self.table_msgId = 0
        self._timer = None

    def start(self, lostUserId):
        self._timer = ftcore.runOnceDelay(self._interval, self._onTimeout, lostUserId)

    def stop(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _onTimeout(self, lostUserId):
        if _DEBUG:
            debug("In MiniMatchProcess @@@@ onTimeOut, lostUserId = ", lostUserId)

        room = tyglobal.rooms()[self._roomId]
        if room.maptable.has_key(self._tableId):
            table = room.maptable.pop(self._tableId)
            self.table_msgId = table.tableMsgId

        if lostUserId == self.userId_a:
            self.winnerId = self.userId_b

            mo = MsgPack()
            mo.setCmd('end_game')
            msg_dict = {"winnerId":self.winnerId, "userId_a":self.userId_a, "userId_b":self.userId_b, "table_msgId":self.table_msgId}
            mo.setResult('gameResult', json.dumps(msg_dict, separators=(',', ':')))
            # mo.setResult('winnerId', self.winnerId)
            # mo.setResult('userId_a', self.userId_a)
            # mo.setResult('userId_b', self.userId_b)
            # mo.setResult('table_msgId', self.table_msgId)

            if _DEBUG:
                debug("OUT end_game  @@@ winnerId = ", self.winnerId)
            tyrpcconn.sendToUser(self.winnerId, mo)

            mo = MsgPack()
            mo.setResult('winnerId', self.winnerId)
            mo.setResult('userId_a', self.userId_a)
            mo.setResult('userId_b', self.userId_b)
            mo.setResult('table_msgId', self.table_msgId)

            rpcproxy = getRpcProxy(9993, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
            rpcproxy.srvgame.doReportGameResult(self.winnerId, tyglobal.gameId(), mo.pack())

        else:
            self.winnerId = self.userId_a

            mo = MsgPack()
            mo.setCmd('end_game')
            msg_dict = {"winnerId":self.winnerId, "userId_a":self.userId_a, "userId_b":self.userId_b, "table_msgId":self.table_msgId}
            mo.setResult('gameResult', json.dumps(msg_dict, separators=(',', ':')))
            # mo.setResult('winnerId', self.winnerId)
            # mo.setResult('userId_a', self.userId_a)
            # mo.setResult('userId_b', self.userId_b)
            # mo.setResult('table_msgId', self.table_msgId)
            if _DEBUG:
                debug("OUT end_game  @@@ self.winnerId = ", self.winnerId)
            tyrpcconn.sendToUser(self.winnerId, mo)

            mo = MsgPack()
            mo.setResult('winnerId', self.winnerId)
            mo.setResult('userId_a', self.userId_a)
            mo.setResult('userId_b', self.userId_b)
            mo.setResult('table_msgId', self.table_msgId)

            rpcproxy = getRpcProxy(9993, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
            rpcproxy.srvgame.doReportGameResult(self.winnerId, tyglobal.gameId(), mo.pack())
