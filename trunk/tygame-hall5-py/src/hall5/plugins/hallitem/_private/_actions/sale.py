# -*- coding=utf-8 -*-
"""
@file  : itemaction
@date  : 2016-09-22
@author: GongXiaobo
"""

from hall5.plugins.hallitem._private._actions import _action
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tycontent
from tuyoo5.plugins.item import assetutils, items
from tuyoo5.plugins.item.itemexceptions import TYItemConfException


class TYItemActionSaleResult(items.TYItemActionResult):
    def __init__(self, action, item, message, gotAssetList, rewardTodotask):
        super(TYItemActionSaleResult, self).__init__(action, item, 0, message, rewardTodotask)
        self.gotAssetList = gotAssetList


class TYItemActionSale(_action.HallItemAction):

    TYPE_ID = 'common.sale'

    SINGLE_MODE_NAME_TYPE_LIST = [('count', int)]

    def __init__(self):
        super(TYItemActionSale, self).__init__()
        self.contentItem = None
        self.contentAssetKind = None

    def getParamNameTypeList(self):
        if self.itemKind.singleMode:
            return self.SINGLE_MODE_NAME_TYPE_LIST
        return None

    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        # 当配置解析工作完成后调用，用于初始化配置中一些itemKind相关的数据
        assetKind = assetKindMap.get(self.contentItem.assetKindId)
        if not assetKind:
            raise TYItemConfException(self.conf, 'TYItemActionSale.saleContent assetKindId Unknown %s' % (
                self.contentItem.assetKindId))
        self.assetKind = assetKind
        if not self.inputParams:
            self.inputParams = {
                'type': 'countSale',
                'desc': '出售可获得：'
            }
        self.inputParams['price'] = self.contentItem.count
        self.inputParams['name'] = assetKind.displayName
        self.inputParams['units'] = assetKind.units

    def _decodeFromDictImpl(self, d):
        '''
        用于子类解析自己特有的数据
        '''
        saleContent = d.get('saleContent')
        if not saleContent:
            raise TYItemConfException(d, 'TYItemActionSale.saleContent must be set')
        self.contentItem = tycontent.TYContentItem.decodeFromDict(saleContent)
        if self.contentItem.count <= 0:
            raise TYItemConfException(d, 'TYItemActionSale.saleContent.count must > 0')

    def canDo(self, gameId, clientId, userBag, item, timestamp):
        return not item.isDied(timestamp)

    def doAction(self, gameId, clientId, userAssets, item, timestamp, params):
        userBag = userAssets.getUserBag()

        if item.isDied(timestamp):
            return items.TYItemActionResult(None, None, -30, '道具已经过期', None)

        if item.itemKind.singleMode:
            unitsCount = int(params.get('count'))
            consumeCount = userBag.consumeItemUnits(gameId, item, unitsCount, timestamp,
                                                    'SALE_ITEM', item.kindId)
            if consumeCount < unitsCount:
                return items.TYItemActionResult(None, None, -31, '道具数量不足', None)

            assetItem = userAssets.addAsset(gameId, self.contentItem.assetKindId,
                                            self.contentItem.count * unitsCount, timestamp,
                                            'SALE_ITEM', item.kindId)
            saleItem = assetutils.buildItemContent((item.itemKind, unitsCount, 0))
        else:
            userBag.removeItem(gameId, item, timestamp, 'SALE_ITEM', item.kindId)
            assetItem = userAssets.addAsset(gameId, self.contentItem.assetKindId,
                                            self.contentItem.count, timestamp,
                                            'SALE_ITEM', item.kindId)
            saleItem = item.itemKind.displayName

        # 生成打开生成的列表
        rewardsList = [{'name': assetItem[0].displayName, 'pic': assetItem[0].pic, 'count': assetItem[1],
                       'kindId': assetItem[0].kindId}]
        rewardTodotask = pluginCross.halltodotask.makeTodoTaskShowRewards(rewardsList)
        
        assetList = [assetItem]
        gotContent = assetutils.buildContent(assetItem)
        replaceParams = {'saleItem': saleItem, 'gotContent': gotContent}
        _mail, message, _changed = _action._handleMailAndMessageAndChanged(gameId, userAssets, self, assetList, replaceParams)
        # TGHall.getEventBus().publishEvent(TYSaleItemEvent(gameId, userBag.userId, item, assetList))
        return TYItemActionSaleResult(self, item, message, assetList, rewardTodotask)
