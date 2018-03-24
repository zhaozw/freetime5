# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh

对应 GT 进程，实际的桌子实例房间进程
'''

from freetime5.util import ftlog
from majiang2.plugins.srvtable.srvtable import Mj2PluginSrvTable
from tuyoo5.core import tychecker
from tuyoo5.core import tygame
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from xuezhan.plugins.srvtable._private import _checkers


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2XueZhanPluginSrvTable(Mj2PluginSrvTable):

    def __init__(self):
        super(Mj2XueZhanPluginSrvTable, self).__init__()
        self.checker1 = tychecker.Checkers(
            tychecker.check_userId,
            tychecker.check_gameId,
            tychecker.check_clientId,
            _checkers.check_roomId,
        )
        self.checker2 = tychecker.Checkers(
            tychecker.check_userId,
            tychecker.check_gameId,
            tychecker.check_clientId,
            _checkers.check_roomId,
            _checkers.check_tableId,
            _checkers.check_seatId0,
        )
        self.checker3 = tychecker.Checkers(
            tychecker.check_userId,
            tychecker.check_gameId,
            tychecker.check_clientId,
            _checkers.check_roomId,
            _checkers.check_tableId,
            _checkers.check_seatIdObserver,
            _checkers.check_action,
        )

    def destoryPlugin(self):
        super(Mj2XueZhanPluginSrvTable, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_TABLE])
    def initPluginBefore(self):
        super(Mj2XueZhanPluginSrvTable, self).initPluginBefore()

    @typlugin.markPluginEntry(cmd="room/vipTableList", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def doRoomVipTableList(self, msg):
        if _DEBUG:
            debug('doRoomVipTableList->', msg)
        mi = self.checker1.check(msg)
        if mi.error:
            ftlog.error('doRoomVipTableList the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            room.doGetVipTableList(mi.userId, mi.clientId)
        return 1

# 需要转换为RPC模式
#     @typlugin.markPluginEntry(cmd="room/playingTableList", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
#     def doRoomGetPlayingTableList(self, msg):
#         ftlog.debug('msg=', msg, caller=self)
#         result = gdata.rooms()[roomId].doGetPlayingTableList()
#         if router.isQuery():
#             mo = MsgPack()
#             mo.setCmd("room")
#             mo.setResult("action", "playingTableList")
#             mo.updateResult(result)
#             router.responseQurery(mo)

#     @typlugin.markPluginEntry(cmd="room/rank_list", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
#     def doRoomRankList(self, msg):
#         ftlog.debug('msg=', msg, caller=self)
#         gdata.rooms()[roomId].doGetRankList(userId, msg)

#     @typlugin.markPluginEntry(cmd="room/change_betsConf", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
#     def doRoomChangeBetsConf(self, msg):
#         ftlog.debug('msg=', msg, caller=self)
#         betsConf = msg.getParam("betsConf")
#         gdata.rooms()[roomId].doChangeBetsConf(betsConf)

    @typlugin.markPluginEntry(cmd="table/enter", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableEnter(self, msg):
        if _DEBUG:
            debug('doTableEnter->', msg)
        mi = self.checker2.check(msg)
        if mi.error:
            ftlog.error('doTableEnter the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            table = room.maptable[mi.tableId]
            table.doEnter(msg,
                          mi.userId,
                          mi.clientId)
        return 1

    @typlugin.markPluginEntry(cmd="table/leave", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableLeave(self, msg):
        if _DEBUG:
            debug('doTableLeave->', msg)
        mi = self.checker2.check(msg)
        if mi.error:
            ftlog.error('doTableLeave the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            table = room.maptable[mi.tableId]
            table.doLeave(msg,
                          mi.userId,
                          mi.clientId)
        return 1

    @typlugin.markPluginEntry(cmd="table/sit", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableSit(self, msg):
        if _DEBUG:
            debug('doTableSit->', msg)
        mi = self.checker2.check(msg)
        if mi.error:
            ftlog.error('doTableSit the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            table = room.maptable[mi.tableId]
            table.doSit(msg,
                        mi.userId,
                        mi.seatId0,
                        mi.clientId)
        return 1

    @typlugin.markPluginEntry(cmd="table/stand_up", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableStandUp(self, msg):
        '''
        此命令一定是由客户端发送的命令, 如果是内部控制命令,那么需要进行区分命令,不能混合调用
        主要是为了避免站起的原因混乱,
        '''
        if _DEBUG:
            debug('doTableStandUp->', msg)
        mi = self.checker2.check(msg)
        if mi.error:
            ftlog.error('doTableStandUp the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            table = room.maptable[mi.tableId]
            table.doStandUp(msg,
                            mi.userId,
                            mi.roomId,
                            mi.tableId,
                            mi.seatId0,
                            tygame.TableStandUpEvent.REASON_USER_CLICK_BUTTON,
                            mi.clientId)
        return 1

    @typlugin.markPluginEntry(cmd="table_call/*", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableCall(self, msg):
        if _DEBUG:
            debug('doTableCall->', msg)
        mi = self.checker3.check(msg)
        if mi.error:
            ftlog.error('doTableCall the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            table = room.maptable[mi.tableId]
            table.doTableCall(msg, mi.userId, mi.seatIdObserver, mi.action, mi.clientId)
        return 1

    @typlugin.markPluginEntry(cmd="table_manage/*", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
    def doTableManage(self, msg):
        # TODO 转换为RPC模式
        if _DEBUG:
            debug('doTableManage->', msg)
        mi = self.checker3.check(msg)
        if mi.error:
            ftlog.error('doTableManage the msg params error !', mi.error)
        else:
            room = tyglobal.rooms()[mi.roomId]
            table = room.maptable[mi.tableId]
            table.doTableManage(msg, mi.action)
        return 1

#     @typlugin.markPluginEntry(cmd="room/detail_infos", srvType=tyglobal.SRV_TYPE_GAME_TABLE)
#     def getRoomOnlineInfoDetails(self, msg):
#         cp = gdata.curProcess.cpu_percent()
#         datas = {'cpu': cp}
#         if roomId in gdata.rooms():
#             room = gdata.rooms()[roomId]
#             ucount, pcount, users = room.getRoomOnlineInfoDetail()
#             datas[roomId] = [ucount, pcount, users]
#         else:
#             datas[roomId] = 'not on this server'
#         msg.setResult('datas', datas)
#         return msg
