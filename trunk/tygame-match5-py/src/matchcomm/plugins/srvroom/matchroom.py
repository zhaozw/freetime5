# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh

对应 GR 进程， 桌子分配、比赛调度管理进程
'''

from freetime5.util import ftlog
from matchcomm.plugins.srvroom._private import _checkers
from tuyoo5.core import typlugin, tyglobal, tychecker


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class MatchPluginSrvRoom(typlugin.TYPlugin):

    def __init__(self):
        super(MatchPluginSrvRoom, self).__init__()
        self.checkerQs = tychecker.Checkers(
            tychecker.check_userId,
            _checkers.check_roomId
        )
        ftlog.info('MatchPluginSrvHttp init')

    def destoryPlugin(self):
        super(MatchPluginSrvRoom, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_ROOM])
    def initPluginBefore(self):
        pass


    @typlugin.markPluginEntry(cmd="match/desc", srvType=tyglobal.SRV_TYPE_GAME_ROOM)
    def doMatchDesc(self, roomId, userId):
        ftlog.debug('doMatchDesc, input: ', roomId, userId)
        roomIns = tyglobal.rooms()[roomId]
        roomIns.doMatchDesc(userId)
        return 1

