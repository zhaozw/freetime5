# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh

对应 GU 进程，游戏内部与牌桌无关的命令、RPC处理进程
'''

from freetime5.util import ftlog
from majiang2.entity import loop_active_task
from majiang2.entity import loop_win_task
from majiang2.entity import win_streak_task
from majiang2.entity.events.events import UserTablePlayEvent
from majiang2.plugins.srvutil.srvutil import Mj2PluginSrvUtil
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core.typlugin import pluginCross


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2XueZhanPluginSrvUtil(Mj2PluginSrvUtil):

    def __init__(self):
        super(Mj2XueZhanPluginSrvUtil, self).__init__()

    def destoryPlugin(self):
        super(Mj2XueZhanPluginSrvUtil, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginBefore(self):
        super(Mj2XueZhanPluginSrvUtil, self).initPluginBefore()

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def gamePlay(self, userId, gameId, roomId, tableId, banker):
        ftlog.debug('table_events_remote trigger event UserTablePlayEvent...')
        evt = UserTablePlayEvent(gameId, userId, roomId, tableId, banker)
        tyglobal.gameIns().getEventBus().publishEvent(evt)
        pluginCross.mj2dao.incrPlayGameCount(userId)
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def tableLoopTask(self, userId, gameId, bigRoomId, tableId):
        ftlog.debug('table_events_remote tableStart...')
        loop_active_task.updateTreasureBoxState(userId, gameId, bigRoomId)
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def tableWinStreaks(self, userId, gameId, bigRoomId, winState, tableConfig):
        ftlog.debug('table_events_remote tableWinStreak...', userId, gameId, bigRoomId, winState, tableConfig)
        win_streak_task.updateStateWithWinStreak(userId, gameId, bigRoomId, winState, tableConfig)
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def tableWinTimes(self, userId, gameId, bigRoomId, winState):
        ftlog.debug('table_event_remote tableWinTimes....')
        loop_win_task.updateTreasureBoxState(userId, gameId, bigRoomId, winState)
        return 1
