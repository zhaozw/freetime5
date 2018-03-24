# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''

from freetime5.util import ftlog, fttime
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.plugins.hallitem._private import _checker
from hall5.plugins.hallitem._private._actions import _action
from hall5.plugins.hallitem._private.itemhelper import ItemHelper
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpcconn


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginItemCmds(object):

    def __init__(self):
        self.checkerCmd = hallchecker.CHECK_BASE.clone()
        self.checkerCmd.addCheckFun(_checker.check_kindGameId)
        self.checkerCmd.addCheckFun(_checker.check_itemId)

        self.checkerAct = hallchecker.CHECK_BASE.clone()
        self.checkerAct.addCheckFun(_checker.check_action)
        self.checkerAct.addCheckFun(_checker.check_params)
        self.checkerAct.addCheckFun(_checker.check_itemId)

    @typlugin.markPluginEntry(cmd='item5/list', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doItemList(self, msg):
        mi = self.checkerCmd.check(msg)
        if mi.error:
            ftlog.warn('doItemList', msg, mi.error)
            return 0
        mo = ItemHelper.makeItemListResponse(mi.gameId, mi.clientId, mi.userId, mi.kindGameId)
        tyrpcconn.sendToUser(mi.userId, mo)

    @typlugin.markPluginEntry(cmd='item5/info', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doItemDetailInfo(self, msg):
        mi = self.checkerCmd.check(msg)
        if mi.error:
            ftlog.warn('doItemDetailInfo', msg, mi.error)
            return 0
        mo = ItemHelper.getItemDetailInfo(mi.gameId, mi.clientId, mi.userId, mi.itemId)
        tyrpcconn.sendToUser(mi.userId, mo)

    @typlugin.markPluginEntry(cmd='item5/*', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doItemActionCmd(self, msg):
        mo = MsgPack()
        mo.setCmd('item5')
        mi = self.checkerAct.check(msg)
        if _DEBUG:
            debug('doItemActionCmd mi=', mi)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            timestamp = fttime.getCurrentTimestamp()
            result = _action.doActionByItemId(mi.userId, mi.gameId, mi.itemId, mi.action, timestamp, mi.params, mi.clientId)
            if result.code != 0:
                mo.setError(result.code, result.message)
            mo.updateResult(result.toDict(_action._makeTodoTaskShowInfo))
        mo.setResult('userId', mi.userId)
        mo.setResult('gameId', mi.gameId)
        mo.setResult('action', mi.action)
        mo.setResult('itemId', mi.itemId)
        if _DEBUG:
            debug('doItemActionCmd mi=', mi, 'result=', result)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1
