# -*- coding: utf-8 -*-
'''
Created on 2016年11月18日

@author: zqh
'''

from freetime5.util import ftlog
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.plugins.todotask.todotask import TyPluginTodoTask


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginTodoTask(TyPluginTodoTask):

    def __init__(self):
        super(HallPluginTodoTask, self).__init__()

    def destoryPlugin(self):
        super(HallPluginTodoTask, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL, tyglobal.SRV_TYPE_HALL_SINGLETON])
    def initPluginBefore(self):
        super(HallPluginTodoTask, self).initPluginBefore()

    @typlugin.markPluginEntry(confKeys=['game5:{}:todotask:tc'.format(tyglobal.gameId())],
                              srvType=[tyglobal.SRV_TYPE_HALL_UTIL, tyglobal.SRV_TYPE_HALL_SINGLETON])
    def onConfChanged(self, confKeys, changedKeys):
        super(HallPluginTodoTask, self).onConfChanged(confKeys, changedKeys)

    @typlugin.markPluginEntry(export=1)
    def sendTodoTaskStartChip(self, gameId, userId, startChip, totalChip, pic, tip):
        '''
        发送启动资金的弹窗
        '''
        t = self.baseUnit.TodoTaskIssueStartChip(startChip, totalChip, pic, tip)
        self.sendTodoTask(gameId, userId, t)
        return 1

    @typlugin.markPluginEntry(export=1)
    def sendNoticeLoginPopWnd(self, gameId, userId, noticeid):
        '''
        发送用户登录时的弹窗
        '''
        t = self.baseUnit.TodoTaskNoticeLoginPopWnd(noticeid)
        self.sendTodoTask(gameId, userId, t)
        return 1
