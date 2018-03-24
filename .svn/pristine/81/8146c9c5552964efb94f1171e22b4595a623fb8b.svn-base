# -*- coding=utf-8 -*-
"""
@file  : itemaction
@date  : 2016-09-22
@author: GongXiaobo
"""

from hall5.plugins.hallitem._private._actions import _action
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.plugins.item import items
from tuyoo5.plugins.item.itemexceptions import TYItemConfException


class TYItemActionBuy(_action.HallItemAction):

    TYPE_ID = 'common.buyProduct'

    def __init__(self):
        super(TYItemActionBuy, self).__init__()
        self.payOrder = None
        self.doConditionList = None

    def _decodeFromDictImpl(self, d):
        self.payOrder = d.get('payOrder')
        if not self.payOrder:
            raise TYItemConfException(d, 'TYItemActionBuy.payOrder must be dict')
        self.doConditionList = d.get('doConditionList', [])

    def canDo(self, gameId, clientId, userBag, item, timestamp):
        if not self.payOrder:
            return False

        if not pluginCross.condition.checkConditions(gameId,
                                                     userBag.userId,
                                                     clientId,
                                                     self.doConditionList):
            return False
        product, _ = pluginCross.hallstore.findProductByPayOrder(gameId,
                                                                 userBag.userId,
                                                                 clientId,
                                                                 self.payOrder)
        if not product:
            return False
        return True

    def doAction(self, gameId, clientId, userAssets, item, timestamp, params):
        product, _ = pluginCross.hallstore.findProductByPayOrder(HALL_GAMEID,
                                                                 userAssets.userId,
                                                                 clientId,
                                                                 self.payOrder)
        if product:
            todotask = pluginCross.halltodotask.makeTodoTaskPayOrder(gameId,
                                                                     userAssets.userId,
                                                                     clientId,
                                                                     product)
            if todotask:
                return items.TYItemActionResult(self, item, 0, '', todotask)
        return items.TYItemActionResult(self, item, -30, 'product not found !', None)
