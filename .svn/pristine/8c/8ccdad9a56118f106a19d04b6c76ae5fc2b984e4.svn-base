# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh
'''

from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from majiang2.entity.item import MajiangItem
from majiang2.plugins.srvutil._private import game_handler, _checkers, game_ui,\
    game_life
from tuyoo5.core import typlugin, tyglobal, tychecker, tyrpcconn
from tuyoo5.core.typlugin import pluginCross


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2PluginSrvUtil(typlugin.TYPlugin):

    def __init__(self):
        typlugin.TYPlugin.__init__(self)
        self.checker = tychecker.Checkers(
            tychecker.check_userId,
            tychecker.check_gameId,
            tychecker.check_clientId,
        )

        self.checkerRoomLlist = self.checker.clone()
        self.checkerRoomLlist.addCheckFun(_checkers.check_playMode1)

        self.checkerQs = self.checker.clone()
        self.checkerQs.addCheckFun(_checkers.check_playMode2)
        self.checkerQs.addCheckFun(_checkers.check_roomId0)
        self.checkerQs.addCheckFun(_checkers.check_tableId0)

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginBefore(self):
        pass

    @typlugin.markPluginEntry(cmd='bind_game', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doClientGameEnter(self, msg):
        '''
        进入游戏
        '''
        if _DEBUG:
            debug('doClientGameEnter->', msg)
        mi = self.checker.check(msg)
        if mi.error:
            ftlog.error('doClientGameEnter the msg params error !', mi.error)
        else:
            game_life.doGameEnter(mi.userId, mi.clientId)
        return 1

    @typlugin.markPluginEntry(cmd='game/leave', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doClientGameLeave(self, msg):
        '''
        离开游戏
        '''
        if _DEBUG:
            debug('doClientGameLeave->', msg)
        mi = self.checker.check(msg)
        if mi.error:
            ftlog.error('doClientGameLeave the msg params error !', mi.error)
        else:
            game_life.doGameLeave(mi.userId, mi.clientId)
        return 1

    @typlugin.markPluginEntry(cmd='hall_info', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doClientHallInfo(self, msg):
        '''
        老版本兼容 获取大厅列表信息
        '''
        if _DEBUG:
            debug('doClientHallInfo->', msg)
        mi = self.checker.check(msg)
        if mi.error:
            ftlog.error('doClientHallInfo the msg params error !', mi.error)
        else:
            mo = MsgPack()
            mo.setCmd('hall_info')
            mo.setResult('gameId', tyglobal.gameId())
            mo.setResult('userId', mi.userId)
            mo.setResult('sessions', None)
            tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd='room_list', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doClientRoomList(self, msg):
        '''
        获取房间列表
        '''
        if _DEBUG:
            debug('doClientRoomList->', msg)
        mi = self.checkerRoomLlist.check(msg)
        if mi.error:
            ftlog.error('doClientRoomList the msg params error !', mi.error)
        else:
            game_ui.doRoomList(mi.userId, mi.gameId, mi.playMode1)
        return 1

    @typlugin.markPluginEntry(cmd='quick_start', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doClientQuickStart(self, msg):
        '''
        未指定房间的 快速开始
        '''
        if _DEBUG:
            debug('doClientQuickStart->', msg)
        mi = self.checkerQs.check(msg)
        if mi.error:
            ftlog.error('doClientQuickStart the msg params error !', mi.error)
        else:
            game_handler.doGameQuickStart(mi.userId,
                                          mi.gameId,
                                          mi.clientId,
                                          mi.roomId0,
                                          mi.tableId0,
                                          mi.playMode2,
                                          0,
                                          msg)
        return 1

    @typlugin.markPluginEntry(cmd='user/mj_timestamp', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def curTimestemp(self, msg):
        if _DEBUG:
            debug('curTimestemp->', msg)
        mi = self.checker.check(msg)
        if mi.error:
            ftlog.error('curTimestemp the msg params error !', mi.error)
        else:
            game_life.doGameTimestemp(mi.userId)
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def getItemCount(self, userId, itemId):
        """获取房卡数"""
        user_fangka_count = MajiangItem.getUserItemCountByKindId(userId, itemId)
        return user_fangka_count

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def consumeItem(self, userId, gameId, itemId, count, roomId, bigRoomId):
        """消费房卡，加锁操作"""
        user_fangka_count = MajiangItem.getUserItemCountByKindId(userId, itemId)
        if user_fangka_count >= count:
            consumeResult = MajiangItem.consumeItemByKindId(userId, gameId, itemId, count, 'MAJIANG_FANGKA_CONSUME', bigRoomId)
            return consumeResult
        return False

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def resumeItemFromRoom(self, userId, gameId, itemId, count, roomId, bigRoomId):
        """退还房卡，加锁操作"""
        MajiangItem.addUserItemByKindId(userId, gameId, itemId, count, 'MAJIANG_FANGKA_RETURN_BACK', bigRoomId)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def resumeItemFromTable(self, userId, gameId, itemId, count, roomId, tableId, bigRoomId):
        """退还房卡，加锁操作"""
        ftlog.debug('user_remote resumeItemFromTable userId:', userId, ' gameId:', gameId, ' itemId:', itemId, ' count:', count, ' roomId:', roomId, ' tableId:', tableId, ' bigRoomId:', bigRoomId
                    )

        lseatId = pluginCross.onlinedata.getOnLineLocSeatId(userId, roomId, tableId)
        ftlog.debug('user_remote resumeItemFromTable lseatId:', lseatId)

        if lseatId < 0:
            ftlog.info('user_remote resumeItemFromTable loc not match, do not resume item. userId:', userId, ' gameId:', gameId,
                       ' itemId:', itemId, ' count:', count, ' roomId:', roomId, ' tableId:', tableId, ' seatId:', lseatId)
            return

        MajiangItem.addUserItemByKindId(userId, gameId, itemId, count, 'MAJIANG_FANGKA_RETURN_BACK', bigRoomId)
