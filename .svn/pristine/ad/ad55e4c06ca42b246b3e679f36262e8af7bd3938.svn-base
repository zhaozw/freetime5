# -*- coding=utf-8 -*-
'''
Created on 2017年7月13日

@author: zqh
'''
from sre_compile import isstring

from freetime5.twisted.ftlock import lockargname
from freetime5.util import ftlog, ftstr
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tysessiondata
from tuyoo5.plugins.condition.condition import TYItemActionCondition
from tuyoo5.plugins.item import itemsys, items, assetutils


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


@lockargname('hall5.item', 'userId')
def doActionByItemId(userId, gameId, itemId, actionName, timestamp, params, clientId=None):
    """
    GDSS接口在用
    """
    if _DEBUG:
        debug('doActionByItemId IN', userId, gameId, itemId, actionName, timestamp, params, clientId)

    try:
        userAssets = itemsys.itemSystem.loadUserAssets(userId)
        if not userAssets:
            return items.TYItemActionResult(None, None, -1, '用户ID资产错误', None)

        userBag = userAssets.getUserBag()
        if not userBag:
            return items.TYItemActionResult(None, None, -2, '用户ID背包错误', None)

        item = userBag.findItem(itemId)
        if not item:
            return items.TYItemActionResult(None, None, -3, '不能识别的道具ID', None)

        action = item.itemKind.findActionByName(actionName)
        if not action:
            return items.TYItemActionResult(None, None, -4, '不能执行该动作', None)

        clientId = clientId or tysessiondata.getClientId(userId)

        # 基本参数类型检查 10
        result = action.checkParams(gameId, userId, timestamp, params)
        if result.code != 0:
            return result

        # 前提条件检查 20
        result = action.checkCondition(gameId, clientId, userId, item, timestamp, params)
        if result.code != 0:
            return result

        # 执行动作 30
        result = action.doAction(gameId, clientId, userAssets, item, timestamp, params)
    except Exception, e:
        ftlog.error()
        result = items.TYItemActionResult(None, None, -6, '系统错误' + str(e), None)

    if _DEBUG:
        debug('doActionByItemId OUT', result)
    return result


def _buildMailAndMessageAndChanged(gameId, userAssets, action, assetList, replaceParams):
    changed = assetutils.getChangeDataNames(assetList) if assetList else set()
    mail = ftstr.replaceParams(action.mail, replaceParams)
    message = ftstr.replaceParams(action.message, replaceParams)
#     if mail:
#         pluginCross.hallmessage.sendMessageSystem(userAssets.userId, gameId, mail, None, None)
#         changed.add('message')
    changed.discard('item')
    return mail, message, changed


def _handleMailAndMessageAndChanged(gameId, userAssets, action, assetList, replaceParams, extChanged=None):
    mail, message, changed = _buildMailAndMessageAndChanged(gameId,
                                                            userAssets,
                                                            action,
                                                            assetList,
                                                            replaceParams)
    if isstring(extChanged):
        extChanged = [extChanged]
    if changed is None:
        changed = extChanged
    elif extChanged:
        changed.update(extChanged)
    pluginCross.halldatanotify.sendDataChangeNotify(userAssets.userId, gameId, changed)
    return mail, message, changed


def _makeTodoTaskShowInfo(info, goShelvesName=None, allow_close=False):
    return pluginCross.halltodotask.makeTodoTaskShowInfo(info, goShelvesName, allow_close)


def _makeTodoWithPayOrder(provider, gameId, userId, clientId):
    payOrder = provider.getParam('payOrder')
    if not payOrder:
        todotaskId = provider.getParam('todotask')
        if todotaskId:
            todotask = pluginCross.halltodotask.makeTodoTaskByConfId(todotaskId, gameId, userId, clientId)
            return items.TYItemActionResult(None, None, -20, provider.failure, todotask)
        else:
            todotask = _makeTodoTaskShowInfo(provider.failure, None, False)
            return items.TYItemActionResult(None, None, -21, provider.failure, todotask)
    else:
        product, shelves = pluginCross.store.findProductByPayOrder(gameId, userId, clientId, payOrder)
        goShelvesName = shelves.name if product and shelves else ''
        todotask = _makeTodoTaskShowInfo(provider.failure, goShelvesName, False)
        return items.TYItemActionResult(None, None, -22, provider.failure, todotask)


class HallItemAction(items.TYItemAction):

    def checkCondition(self, gameId, clientId, userId, item, timestamp, params):

        if not self.conditionList:
            return items.ACT_RESULT_OK

        for conditionId in self.conditionList:
            if not pluginCross.condition.checkCondition(gameId,
                                                        userId,
                                                        clientId,
                                                        conditionId,
                                                        item=item,
                                                        params=params):
                condition = pluginCross.condition.getConditionInstanceById(conditionId, True)
                if isinstance(condition, TYItemActionCondition):
                    return _makeTodoWithPayOrder(condition, gameId, userId, clientId)
                else:
                    return items.TYItemActionResult(None, None, -23, '条件检查失败', None)
        return items.ACT_RESULT_OK
