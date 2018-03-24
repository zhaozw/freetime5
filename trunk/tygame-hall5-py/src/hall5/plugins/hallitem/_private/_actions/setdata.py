# -*- coding=utf-8 -*-
"""
@file  : itemaction
@date  : 2016-09-22
@author: GongXiaobo
"""

from hall5.plugins.hallitem._private._actions import _action
from tuyoo5.core import typlugin
from tuyoo5.plugins.item import items


class TYItemActionSetGameData(_action.HallItemAction):

    TYPE_ID = 'common.setGameData'

    def __init__(self):
        super(TYItemActionSetGameData, self).__init__()
        self.field = None
        self.value = None
        self.gameId = None

    def _decodeFromDictImpl(self, d):
        self.field = d['args']['field']
        self.value = int(d['args']['value'])
        self.gameId = int(d['args']['gameId'])

    def canDo(self, gameId, clientId, userBag, item, timestamp):
        return not item.isDied(timestamp)

    def doAction(self, gameId, clientId, userAssets, item, timestamp, params):
        if item.isDied(timestamp):
            return items.TYItemActionResult(None, None, -30, '道具已经过期', None)
        # 消耗道具
        userBag = userAssets.getUserBag()
        count = userBag.consumeItemUnits(gameId,
                                         item,
                                         1,
                                         timestamp,
                                         'ITEM_USE',
                                         item.kindId)
        if count != 1:
            return items.TYItemActionResult(None, None, -31, '道具数量不足', None)

        return items.TYItemActionResult(None, None, 0, 'ok, not implement', None)

        rpcproxy = typlugin.getRpcProxy(self.gameId,
                                        typlugin.RPC_CALL_SAFE,
                                        typlugin.RPC_TARGET_MOD_ONE)
        rfc = rpcproxy.gamemgr.setGameData(userBag.userId,
                                           self.gameId,
                                           self.field,
                                           self.value)
        if not rfc:
            return items.TYItemActionResult(None, None, -32, '系统错误,目标游戏服务不存在', None)
        if rfc.getException():
            return items.TYItemActionResult(None, None, -33, '系统错误,目标游戏服务异常:' + str(rfc.getException()), None)
        code, info = rfc.getResult()
        return items.TYItemActionResult(None, None, code, info, None)
