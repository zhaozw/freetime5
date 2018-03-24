# -*- coding: utf-8 -*-
'''
Created on 2016年11月5日

@author: zqh
'''

from freetime5.util import ftlog
from tuyoo5.core import typlugin, tyglobal
from tuyoo5.plugins.condition.condition import TyPluginCondition


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginCondition(TyPluginCondition):

    def destoryPlugin(self):
        super(HallPluginCondition, self).destoryPlugin()
        from hall5.plugins.condition import _userconditions
        self.unRegisterConditionModule(_userconditions)
        from hall5.plugins.condition import _storeconditions
        self.unRegisterConditionModule(_storeconditions)
        from hall5.plugins.condition import _itemconditions
        self.unRegisterConditionModule(_itemconditions)

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        super(HallPluginCondition, self).initPluginBefore()
        from hall5.plugins.condition import _userconditions
        self.registerConditionModule(_userconditions, True)
        from hall5.plugins.condition import _storeconditions
        self.registerConditionModule(_storeconditions, True)
        from hall5.plugins.condition import _itemconditions
        self.registerConditionModule(_itemconditions, True)

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_SINGLETON])
    def initSingletonPluginBefore(self):
        super(HallPluginCondition, self).initPluginBefore()

    @typlugin.markPluginEntry(confKeys=['game5:{}:condition:tc'.format(tyglobal.gameId())],
                              srvType=[tyglobal.SRV_TYPE_HALL_UTIL,
                                       tyglobal.SRV_TYPE_HALL_SINGLETON])
    def onConfChanged(self, confKeys, changedKeys):
        super(HallPluginCondition, self).onConfChanged(confKeys, changedKeys)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def remoteCheckCondition(self, userId, gameId, intClientId, conditionId, kwargs):
        kwargs['__rpc'] = True  # 死循环保护
        return self.checkCondition(gameId, userId, intClientId, conditionId, **kwargs)
