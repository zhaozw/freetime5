# -*- coding: utf-8 -*-
'''
Created on 2018年2月1日

@author: lixi
'''
from freetime5.twisted import ftcore
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import typlugin, tyglobal, tyrpcconn
from unblock.plugins.srvtable._private import _svrtable_handler
from unblock.plugins.srvtable._private import _checker
from tuyoo5.core import tychecker


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

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
            if table._timer == None:
                table._timer = MiniMatchProcess(7, mi.userId, userId_b, mi.roomId, mi.tableId)
            table._timer.stop()
            table._timer.start()
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
                    mo.setResult('result', 'ok')
                    mo.setResult('gameResult', msg.getParamStr('gameResult'))
                    if _DEBUG:
                        debug("OUT endCLientGame  @@@ table_info = ", msg)
                    tyrpcconn.sendToUser(userid, mo)
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
                mo.setCmd('table/quit_game')
                mo.setResult('winnerId', winnerId)
                mo.setResult('loserId', loserId)
                mo.setResult('result', 'win')
                if _DEBUG:
                    debug("OUT quitCLientGame  @@@ winnerId = ", winnerId)
                tyrpcconn.sendToUser(winnerId, mo)

                mo = MsgPack()
                mo.setCmd('table/quit_game')
                mo.setResult('winnerId', winnerId)
                mo.setResult('loserId', loserId)
                mo.setResult('result', 'lose')
                if _DEBUG:
                    debug("OUT quitCLientGame  @@@ loserId = ", loserId)
                tyrpcconn.sendToUser(loserId, mo)
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
        self._timer = None

    def start(self):
        self._timer = ftcore.runOnceDelay(self._interval, self._onTimeout)

    def stop(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _onTimeout(self, lostUserId):
        if _DEBUG:
            debug("In MiniMatchProcess @@@@ onTimeOut, lostUserId = ", lostUserId)

        room = tyglobal.rooms()[self._roomId]
        if room.maptable.has_key(self.tableId):
            room.maptable.pop(self.tableId)

        if lostUserId == self.userId_a:
            self.winnerId = self.userId_b

            mo = MsgPack()
            mo.setCmd('game_finish_result')
            mo.setResult('result', 'other player lost internet')
            mo.setResult('winnerId', self.winnerId)
            if _DEBUG:
                debug("OUT game_finish_result  @@@ winnerId = ", self.winnerId)
            tyrpcconn.sendToUser(self.winnerId, mo)
        else:
            self.winnerId = self.userId_a

            mo = MsgPack()
            mo.setCmd('game_finish_result')
            mo.setResult('result', 'other player lost internet')
            mo.setResult('winnerId', self.winnerId)
            if _DEBUG:
                debug("OUT game_finish_result  @@@ self.winnerId = ", self.winnerId)
            tyrpcconn.sendToUser(self.winnerId, mo)
