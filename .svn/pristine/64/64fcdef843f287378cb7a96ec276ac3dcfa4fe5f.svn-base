# -*- coding=utf-8 -*-
"""
@file  : test
@date  : 2016-11-10
@author: GongXiaobo
"""

from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.plugins.halltest._private import _checker
from tuyoo5.core import tychecker
from tuyoo5.core.typlugin import hallRpcOne
from tuyoo5.game import tysessiondata


class HallPluginTestHappyBag(object):

    def __init__(self):
        self.checkHttpUser = tychecker.Checkers(
            tychecker.check_userId,
            hallchecker.check__checkUserData
        )
        self.checkHttpTaskAction = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_taskId,
            _checker.check_itemId,
            hallchecker.check__checkUserData
        )
        self.checkHttpTaskUpTime = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_taskId,
            _checker.check_updateTime,
            hallchecker.check__checkUserData
        )
        self.checkHttpTaskUpProgress = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_taskId,
            _checker.check_progress,
            hallchecker.check__checkUserData
        )

    def doHappyBagTest(self, request):
        action = request.getParamStr('action')
        if action == 'list':
            return self.doHappyBagList(request)
        if action == 'removeAll':
            return self.doHappyBagRemoveAll(request)
        if action == 'setfinish':
            return self.doHappyBagFinish(request)
        if action == 'getreward':
            return self.doHappyBagGetReward(request)
        if action == 'setUpdateTime':
            return self.doHappyBagSetUpdateTime(request)
        if action == 'setProgress':
            return self.doHappyBagSetProgress(request)
        return 'params action error'

    def doHappyBagList(self, request):
        mo = MsgPack()
        mi = self.checkHttpUser.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            clientId = tysessiondata.getClientId(mi.userId)
            tasks = hallRpcOne.halltaskhappybag._doHappyBagListFull(mi.userId, clientId).getResult()
            mo.setResult('tasks', tasks)
        return mo

    def doHappyBagRemoveAll(self, request):
        mo = MsgPack()
        mi = self.checkHttpUser.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            ret = hallRpcOne.halltaskhappybag._doRemoveAll(mi.userId).getResult()
            if ret == 'ok':
                mo.setResult('ok', 1)
            else:
                mo.setError(1, ret)
        return mo

    def doHappyBagFinish(self, request):
        mo = MsgPack()
        mi = self.checkHttpTaskAction.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            ret = hallRpcOne.halltaskhappybag._setProgress(mi.userId,
                                                           mi.taskId,
                                                           -1).getResult()
            if ret == 'ok':
                mo.setResult('ok', 1)
            else:
                mo.setError(1, ret)
        return mo

    def doHappyBagGetReward(self, request):
        mo = MsgPack()
        mi = self.checkHttpTaskAction.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            clientId = tysessiondata.getClientId(mi.userId)
            ret = hallRpcOne.halltaskhappybag._doGetReward(mi.userId,
                                                           mi.taskId,
                                                           mi.itemId,
                                                           clientId).getResult()
            if isinstance(ret, (list, tuple)):
                code, rewards = ret[0], ret[1]
                if code == 0:
                    mo.setResult('rwards', rewards)
                else:
                    mo.setError(1, rewards)
            else:
                mo.setError(1, ret)
        return mo

    def doHappyBagSetUpdateTime(self, request):
        mo = MsgPack()
        mi = self.checkHttpTaskUpTime.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            ret = hallRpcOne.halltaskhappybag._setUpdateTime(mi.userId,
                                                             mi.taskId,
                                                             mi.updateTime).getResult()
            if ret == 'ok':
                mo.setResult('ok', 1)
            else:
                mo.setError(1, ret)
        return mo

    def doHappyBagSetProgress(self, request):
        mo = MsgPack()
        mi = self.checkHttpTaskUpProgress.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            ret = hallRpcOne.halltaskhappybag._setProgress(mi.userId,
                                                           mi.taskId,
                                                           mi.progress).getResult()
            if ret == 'ok':
                mo.setResult('ok', 1)
            else:
                mo.setError(1, ret)
        return mo
