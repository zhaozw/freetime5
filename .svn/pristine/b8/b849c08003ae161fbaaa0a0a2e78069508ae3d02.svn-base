# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh
'''
from freetime5.twisted import ftcore
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from majiang2.entity.create_table_list import CreateTable
from tuyoo5.core import typlugin, tyglobal


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2PluginSrvTable(typlugin.TYPlugin):

    def __init__(self):
        super(Mj2PluginSrvTable, self).__init__()

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_TABLE])
    def initPluginBefore(self):
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def getPlayingTableList(self, roomId, msgDict):
        msg = MsgPack(msgDict)
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableCallObserve(self, roomId, msgDict, isSync):
        if not isSync:
            ftcore.runOnce(self.doTableCallObserve, roomId, msgDict, 1)
            return 1
        msg = MsgPack(msgDict)
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doSitDown(self, roomId, msgDict, isSync):
        if not isSync:
            ftcore.runOnce(self.doSitDown, roomId, msgDict, 1)
            return 1
        msg = MsgPack(msgDict)
        tableId = msg.getParamInt('tableId', 0)
        userId = msg.getParamInt('userId', 0)
        seatId = msg.getParamInt('seatId', 0)
        clientId = msg.getParamStr('clientId', '')
        room = tyglobal.rooms()[roomId]
        table = room.maptable[tableId]
        table.doSit(msg, userId, seatId, clientId)
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableManageSit(self, roomId, msgDict, isSync):
        if not isSync:
            ftcore.runOnce(self.doTableManageSit, roomId, msgDict, 1)
            return 1
        msg = MsgPack(msgDict)
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableManageStandup(self, roomId, msgDict, isSync):
        if not isSync:
            ftcore.runOnce(self.doTableManageStandup, roomId, msgDict, 1)
            return 1
        msg = MsgPack(msgDict)
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableManageLeave(self, roomId, msgDict, isSync):
        if not isSync:
            ftcore.runOnce(self.doTableManageLeave, roomId, msgDict, 1)
            return 1
        msg = MsgPack(msgDict)
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableManageGameStart(self, roomId, msgDict, isSync):
        if not isSync:
            ftcore.runOnce(self.doTableManageGameStart, roomId, msgDict, 1)
            return 1
        msg = MsgPack(msgDict)
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableManageClearPlayers(self, roomId, msgDict, isSync):
        if not isSync:
            ftcore.runOnce(self.doTableManageClearPlayers, roomId, msgDict, 1)
            return 1
        msg = MsgPack(msgDict)
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doChangeBetsConf(self, roomId, msgDict, isSync):
        if not isSync:
            ftcore.runOnce(self.doTableManageClearPlayers, roomId, msgDict, 1)
            return 1
        msg = MsgPack(msgDict)
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def doUserChangeDone(self, roomId, tableId, userId, clientId, isSync):
        if not isSync:
            ftcore.runOnce(self.doUserChangeDone, roomId, tableId, userId, clientId, 1)
            return 1
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_TABLE)
    def getTableByRoomId(self, roomId):
        """ 
        * UT调用，需要处理完之后返回消息给UT
        """
        room = tyglobal.rooms().get(roomId, None)
        if not room:
            ftlog.info('getTableByRoomId, room is null:', roomId)
            return 0
        table_list = []
        for table in room.maptable.values():
            table_list.append([table.realPlayerNum, table])
            table_list = sorted(table_list, reverse=True)
        ftlog.debug('===getTableByRoomId===table_list=', table_list)
        return CreateTable.get_create_table_from_table_list(table_list)

    def _doTableSmilies(self, userId, roomId, tableId, seatId, smilies, toseat):
        room = tyglobal.rooms()[roomId]
        table = room.maptable[tableId]
        table.doTableSmilies(userId, seatId, smilies, toseat)

    def _doRedEnvelopeStart(self, roomId, grab_times, envelope_num, interval):
        pass

    def _doRedEnvelopeLed(self, roomId, ledMsg):
        pass

    def _doTableSceneLeave(self, userId, roomId, tableId, seatId):
        """
        客户端离开牌桌场景时通知服务器 added by nick.kai.lee
        客户端离开场景时主动发消息告知服务器,服务器可以推送一些消息,比如免费金币的todotask给客户端,当客户端返回房间列表时触发
        不能复用leave消息,因为客户端结算时会leave,点击返回按钮时还会leave一次.
        """
        room = tyglobal.rooms()[roomId]
        table = room.maptable[tableId]
        table._send_win_sequence_led_message(userId)

