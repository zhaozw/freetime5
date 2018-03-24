# -*- coding: utf-8 -*-
'''
Created on 2016年11月18日

@author: zqh
'''

from freetime5.util import ftlog
from majiang2.plugins.mj2todotask._private import _mj2todotaskunit
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.plugins.todotask import _todotaskunit
from tuyoo5.plugins.todotask.todotask import TyPluginTodoTask


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2PluginTodoTask(TyPluginTodoTask):

    def __init__(self):
        super(Mj2PluginTodoTask, self).__init__()

    def destoryPlugin(self):
        super(Mj2PluginTodoTask, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=tyglobal.SRV_TYPE_GAME_ALL)
    def initPluginBefore(self):
        super(Mj2PluginTodoTask, self).initPluginBefore()

    @typlugin.markPluginEntry(confKeys=['game5:{}:todotask:tc'.format(tyglobal.gameId())],
                              srvType=tyglobal.SRV_TYPE_GAME_ALL)
    def onConfChanged(self, confKeys, changedKeys):
        super(Mj2PluginTodoTask, self).onConfChanged(confKeys, changedKeys)

    @typlugin.markPluginEntry(export=1)
    def sendQuickStartNeedCharge(self, gameId, userId, product, chooseRoomId):
        todotask = _mj2todotaskunit.TodoTaskOrderShow.makeByProduct("金币不够啦，买一个超值礼包吧！", "", product)
        todotask.addSubCmdExtText('换房间')
        todotask.setSubCmdExt(_mj2todotaskunit.TodoTaskQuickStart(gameId, chooseRoomId))
        if todotask:
            self.sendTodoTask(gameId, userId, todotask)
        return 1

    @typlugin.markPluginEntry(export=1)
    def sendTodoTaskShowInfo(self, gameId, userId, infoStr, goShelvesName=None, allow_close=False):
        '''
        发送消息提示信息框，可携带功能按钮
        '''
        t = _todotaskunit.TodoTaskShowInfo(infoStr, allow_close)
        if goShelvesName:
            t.setSubCmd(_todotaskunit.TodoTaskGotoShop(goShelvesName))
        self.sendTodoTask(gameId, userId, t)
        return 1

    def sendTodoTaskPopTipMsg(self, gameId, userId, msg, duration):
        t = _mj2todotaskunit.TodoTaskPopTip(msg)
        t.setParam('duration', duration)
        self.sendTodoTask(gameId, userId, t)
        return 1

    @typlugin.markPluginEntry(export=1)
    def sendQuickStartChangeRoom(self, gameId, userId, product, chooseRoomId):
        todotask = _mj2todotaskunit.TodoTaskOrderShow.makeByProduct("金币不够啦，买一个超值礼包吧！", "", product)
        todotask.addSubCmdExtText('换房间')
        todotask.setSubCmdExt(_mj2todotaskunit.TodoTaskQuickStart(gameId, chooseRoomId))
        if todotask:
            self.sendTodoTask(gameId, userId, todotask)
        return 1

    @typlugin.markPluginEntry(export=1)
    def sendQuickStartJumpRoom(self, gameId, userId, chooseRoomId, playMode, tipStr):
        quickStartMsg = _mj2todotaskunit.TodoTaskQuickStart(gameId, chooseRoomId)
        jump2hall = _mj2todotaskunit.TodoTaskJumpToRoomList(gameId, playMode)
        todotask = _todotaskunit.TodoTaskShowInfo(tipStr, True)
        todotask.setSubCmd(quickStartMsg)
        todotask.setSubCmdExt(jump2hall)
        todotask.setSubText("换房间")
        if todotask:
            self.sendTodoTask(gameId, userId, todotask)
        return 1
