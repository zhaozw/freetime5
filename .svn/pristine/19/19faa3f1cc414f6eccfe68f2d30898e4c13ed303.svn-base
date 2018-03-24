# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh

对应 GR 进程， 桌子分配、比赛调度管理进程
'''

from freetime5.util import ftlog
from majiang2.plugins.srvroom.srvroom import Mj2PluginSrvRoom
from tuyoo5.core import typlugin, tyglobal, tychecker
from xuezhan.plugins.srvroom._private import _checkers


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2XueZhanPluginSrvRoom(Mj2PluginSrvRoom):

    def __init__(self):
        super(Mj2XueZhanPluginSrvRoom, self).__init__()
        self.checkerQs = tychecker.Checkers(
            tychecker.check_userId,
            tychecker.check_gameId,
            tychecker.check_clientId,
            _checkers.check_roomId,
        )

    def destoryPlugin(self):
        super(Mj2XueZhanPluginSrvRoom, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_ROOM])
    def initPluginBefore(self):
        super(Mj2XueZhanPluginSrvRoom, self).initPluginBefore()

#     @typlugin.markPluginEntry(cmd='quick_start', srvType=tyglobal.SRV_TYPE_GAME_ROOM)
#     def doQuickStartWithRoom(self, msg):
#         if _DEBUG:
#             debug('doQuickStartWithRoom->', msg)
#         mi = self.checkerQs.check(msg)
#         if mi.error:
#             ftlog.error('doClientGameEnter the msg params error !', mi.error)
#         else:
#             pass
#         return 1

    @typlugin.markPluginEntry(cmd="room/quick_start", srvType=tyglobal.SRV_TYPE_GAME_ROOM)
    def doRoomQuickStart(self, roomId, userId):
        super(Mj2XueZhanPluginSrvRoom, self).doRoomQuickStart(roomId, userId)
        return 1

    @typlugin.markPluginEntry(cmd="room/match_state", srvType=tyglobal.SRV_TYPE_GAME_ROOM)
    def doMatchState(self, userId, gameId, roomId):
        super(Mj2XueZhanPluginSrvRoom, self).doMatchState(userId, gameId, roomId)
        return 1

    @typlugin.markPluginEntry(cmd="room/match_award_certificate", srvType=tyglobal.SRV_TYPE_GAME_ROOM)
    def doMatchAwardCertificate(self, userId, gameId, roomId, match_id):
        super(Mj2XueZhanPluginSrvRoom, self).doMatchAwardCertificate(userId, gameId, roomId, match_id)
        return 1

    @typlugin.markPluginEntry(cmd='room/majiang_m_signin_next', srvType=tyglobal.SRV_TYPE_GAME_ROOM)
    def signinNextMatch(self, gameId, userId):
        """报名下一场比赛
        """
        super(Mj2XueZhanPluginSrvRoom, self).signinNextMatch(gameId, userId)
        return 1

    @typlugin.markPluginEntry(cmd="room/create_table", srvType=tyglobal.SRV_TYPE_GAME_ROOM)
    def doCreateTable(self, userId, gameId, roomId):
        super(Mj2XueZhanPluginSrvRoom, self).doCreateTable(userId, gameId, roomId)
        return 1

    @typlugin.markPluginEntry(cmd="room/join_create_table", srvType=tyglobal.SRV_TYPE_GAME_ROOM)
    def doJoinCreateTable(self, userId, gameId, roomId):
        super(Mj2XueZhanPluginSrvRoom, self).doJoinCreateTable(userId, gameId, roomId)
        return 1
