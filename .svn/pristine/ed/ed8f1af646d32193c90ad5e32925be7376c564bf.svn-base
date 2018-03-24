# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh
'''
from freetime5.twisted import ftcore
from freetime5.util import ftlog
from tuyoo5.core import typlugin, tyglobal


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2PluginRobot(typlugin.TYPlugin):

    def __init__(self):
        super(Mj2PluginRobot, self).__init__()

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_ROBOT])
    def initPluginBefore(self):
        pass

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROBOT)
    def doRobotCallUp(self, roomId, tableId, ucount, uids, params, isSync):
        if not isSync:
            ftcore.runOnce(self.doRobotCallUp, roomId, tableId, ucount, uids, params, 1)
            return 1
        # do sync code
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROBOT)
    def doRobotShutDown(self, roomId, msgDict, isSync):
        if not isSync:
            ftcore.runOnce(self.doRobotShutDown, roomId, msgDict, 1)
            return 1
        # do sync code
        # msg = MsgPack(msgDict)
        return 1
