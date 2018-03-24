# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''
from freetime5.twisted import ftcore
from freetime5.util import ftlog
from freetime5.util import fttime
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core.typlugin import pluginSafeCross
from tuyoo5.plugins.item import itemsys


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class ItemHelper(object):

    @classmethod
    def encodeItemAction(cls, gameId, userBag, item, action, timestamp):
        ret = {
            'action': action.name,
            'name': action.displayName,
        }
        inputParams = action.getInputParams(gameId, userBag, item, timestamp)
        if inputParams:
            ret['params'] = inputParams
        return ret

    @classmethod
    def encodeItemActionList(cls, gameId, clientId, userBag, item, timestamp):
        ret = []
        actions = userBag.getExecutableActions(gameId, clientId, item, timestamp)
        for action in actions:
            ret.append(cls.encodeItemAction(gameId, userBag, item, action, timestamp))
        return ret

    @classmethod
    def encodeUserItem(cls, gameId, clientId, userBag, item, timestamp):
        ret = {
            'kindId': item.kindId,
            'count': max(1, item.remaining),
            'actions': cls.encodeItemActionList(gameId, clientId, userBag, item, timestamp)
        }
        if item.expiresTime >= 0:
            ret['expires'] = item.expiresTime
        return ret

    @classmethod
    def resetHallItemRed(cls, userId, kindGameId=0):
        ftcore.runOnceDelay(0.01, cls._resetHallItemRed, userId, kindGameId)

    @classmethod
    def _resetHallItemRed(cls, userId, kindGameId=0):
        timestamp = fttime.getCurrentTimestamp()
        userBag = itemsys.itemSystem.loadUserAssets(userId).getUserBag()
        itemList = userBag.getAllItem()
        itemIds = []
        for item in itemList:
            if kindGameId == 0 or item.itemKind.gameId == kindGameId:
                if item.itemKind.visibleInBag and item.visibleInBag(timestamp):
                    itemIds.append(item.itemId)
        # 刷新小红点数据
        pluginSafeCross.hallredpoint.resetItemIds(userId, 'item5', itemIds)

    @classmethod
    def makeItemListResponse(cls, gameId, clientId, userId, kindGameId):
        timestamp = fttime.getCurrentTimestamp()
        userBag = itemsys.itemSystem.loadUserAssets(userId).getUserBag()
        itemList = userBag.getAllItem()
        items = []
        for item in itemList:
            if kindGameId == 0 or item.itemKind.gameId == kindGameId:
                if item.itemKind.visibleInBag and item.visibleInBag(timestamp):
                    items.append([item.itemId, item.kindId, max(1, item.remaining), item.expiresTime])

        cls.resetHallItemRed(userId)

        mo = MsgPack()
        mo.setCmd('item5')
        mo.setResult('action', 'list')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('kindGameId', kindGameId)
        mo.setResult('items', items)
        return mo

    @classmethod
    def getItemDetailInfo(cls, gameId, clientId, userId, itemId):
        mo = MsgPack()
        mo.setCmd('item5')
        mo.setResult('action', 'info')
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)
        mo.setResult('itemId', itemId)
        try:
            userBag = itemsys.itemSystem.loadUserAssets(userId).getUserBag()
            item = userBag.findItem(itemId)
            if not item:
                mo.setError(1, '道具不存在')
            else:
                timestamp = fttime.getCurrentTimestamp()
                if item.itemKind.visibleInBag and item.visibleInBag(timestamp):
                    itemInfo = cls.encodeUserItem(gameId, clientId, userBag, item, timestamp)
                    mo.setResult('itemInfo', itemInfo)
                else:
                    mo.setError(1, '道具被隐藏')
        except:
            ftlog.error()
            mo.setError(2, '道具信息获取失败')
        return mo
