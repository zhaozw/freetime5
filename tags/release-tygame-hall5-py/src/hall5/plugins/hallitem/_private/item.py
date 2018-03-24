# -*- coding=utf-8 -*-
"""
@file  : item
@date  : 2016-09-28
@author: GongXiaobo
"""

from freetime5.util import ftlog
from freetime5.util import fttime
from hall5.plugins.hallitem._private.itemdao import TYItemDao
from tuyoo5.game import tybireport
from tuyoo5.game import tycontent
from tuyoo5.plugins.item.itemexceptions import TYAssetNotEnoughException
from tuyoo5.plugins.item.itemexceptions import TYDuplicateItemIdException
from tuyoo5.plugins.item.itemexceptions import TYUnknownAssetKindException
from tuyoo5.plugins.item.itemsys import TYItemSystem
from tuyoo5.core.typlugin import pluginSafeCross


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class TYUserBag(object):

    def __init__(self, userId, dao, assets):
        self._userId = userId
        self._dao = dao
        # map<itemId, item>
        self._itemIdMap = {}
        # map<kindId, map<itemId, item>>
        self._kindIdMap = {}
        self._assets = assets
        self._loaded = False
        self._isSendToUser = True

    def load(self):
        if not self._loaded:
            self._loaded = True
            self._itemIdMap = self._dao.loadAll(self.userId)
            for item in self._itemIdMap.itervalues():
                idMap = self._kindIdMap.get(item.kindId)
                if not idMap:
                    idMap = {}
                    self._kindIdMap[item.kindId] = idMap
                idMap[item.itemId] = item
        return self

    @property
    def userId(self):
        return self._userId

    @property
    def userAssets(self):
        return self._assets

    def _onCountChanged(self):
        pass
        # event = ItemCountChangeEvent(self._userId)
        # pkeventbus.globalEventBus.publishEvent(event)

    def findItem(self, itemId):
        '''
        在背包中根据itemId查找道具
        @param itemId: 要查找的道具ID
        @return: item or None
        '''
        return self._itemIdMap.get(itemId)

    def getAllItem(self):
        '''
        获取所有item
        @return: list<Item>
        '''
        return self._itemIdMap.values()

    def getItemByKind(self, itemKind):
        '''
        获取某个类型的一个道具
        '''
        return self.getItemByKindId(itemKind.kindId)

    def getItemByKindId(self, itemKindId):
        '''
        获取某个类型的一个道具
        '''
        idMap = self._kindIdMap.get(itemKindId)
        return idMap.values()[0] if idMap else None

    def getAllKindItem(self, itemKind):
        '''
        获取所有item
        @return: list<Item>
        '''
        return self.getAllKindItemByKindId(itemKind.kindId)

    def getAllKindItemByKindId(self, kindId):
        '''
        获取所有item
        @return: list<Item>
        '''
        idMap = self._kindIdMap.get(kindId)
        return idMap.values() if idMap else []

    def getAllTypeItem(self, itemType):
        '''
        获取所有item类类型为itemType的道具
        @return: list<Item>
        '''
        ret = []
        for item in self._itemIdMap.values():
            if type(item) == itemType:
                ret.append(item)
        return ret

    def addItem(self, gameId, item, timestamp, eventId, intEventParam):
        '''
        添加一个道具到背包
        '''
        self._addItem(item)
        balance = item.balance(timestamp)
#         if item.itemKind.visibleInBag:
#             pluginCross.hallmoduletip.sendModuleTipNotify(self.userId, gameId, 'bag', 1)
        tybireport.itemUpdate(gameId, self.userId, item.kindId,
                              balance, balance, eventId, intEventParam)
        self._onCountChanged()

    def addItemUnits(self, gameId, item, count, timestamp, eventId, intEventParam):
        '''
        给某个道具添加count个单位
        '''
        found = self.findItem(item.itemId)
        if found != item:
            ftlog.error('TYUserBagImpl.updateItem userId=', self.userId,
                        'item=', item,
                        'found=', found)
            raise ValueError()
        item.addUnits(count, timestamp)
        self._updateItem(item, timestamp)
#         if item.itemKind.visibleInBag:
#             pluginCross.hallmoduletip.sendModuleTipNotify(self.userId, gameId, 'bag', 1)
        tybireport.itemUpdate(gameId, self.userId, item.kindId,
                              count, self.calcTotalUnitsCount(item.itemKind, timestamp),
                              eventId, intEventParam)
        self._onCountChanged()
        return item

    def addItemUnitsByKind(self, gameId, itemKind, count, timestamp, fromUserId, eventId, intEventParam, param01='', param02=''):
        '''
        添加count个单位的道具
        '''
        assert (count > 0)
        items = []
#         is_new = True
        sameKindItemList = self.getAllKindItem(itemKind)
        if not itemKind.singleMode:
            for _ in xrange(count):
                item = itemKind.newItem(self._dao.nextItemId(), timestamp)
                item.fromUserId = fromUserId
                item.addUnits(1, timestamp)
                self._addItem(item)
                items.append(item)
        else:
            if sameKindItemList:
                item = sameKindItemList[0]
                item.fromUserId = fromUserId
                item.addUnits(count, timestamp)
                self._updateItem(item, timestamp)
                items.append(item)
#                 is_new = False
            else:
                item = itemKind.newItem(self._dao.nextItemId(), timestamp)
                item.fromUserId = fromUserId
                item.addUnits(count, timestamp)
                self._addItem(item)
                items.append(item)
#         if is_new and items and items[0].itemKind.visibleInBag:
#             pluginCross.hallmoduletip.sendModuleTipNotify(self.userId, gameId, 'bag', 1)
        tybireport.itemUpdate(gameId, self.userId, itemKind.kindId,
                              count, self.calcTotalUnitsCount(itemKind, timestamp),
                              eventId, intEventParam, param01=param01, param02=param02)
        if self._isSendToUser:
            self._onCountChanged()
        return items

    def removeItem(self, gameId, item, timestamp, eventId, intEventParam):
        '''
        在背包中根据itemId删除道具，返回删除的道具
        @return: item or None
        '''
        found = self.findItem(item.itemId)
        if found != item:
            ftlog.error('TYUserBagImpl.removeItem userId=', self.userId,
                        'item=', item,
                        'found=', found)
            raise ValueError()
        balance = item.balance(timestamp)
        self._removeItem(item)
        if balance > 0:
            tybireport.itemUpdate(gameId, self.userId, item.kindId,
                                  -balance, self.calcTotalUnitsCount(item.itemKind, timestamp),
                                  eventId, intEventParam)
        self._onCountChanged()
        return item

    def calcTotalUnitsCount(self, itemKind, timestamp=None):
        '''
        计算所有itemKind种类的道具的数量
        @param itemKind: 那种类型
        @return: 剩余多少个单位
        '''
        timestamp = timestamp if timestamp is not None else fttime.getCurrentTimestamp()
        return self._calcTotalUnitsCount(self.getAllKindItem(itemKind), timestamp)

    def _calcTotalUnitsCount(self, sameKindItemList, timestamp):
        total = 0
        for item in sameKindItemList:
            total += item.balance(timestamp)
        return total

    def consumeItemUnits(self, gameId, item, unitsCount, timestamp, eventId, intEventParam):
        '''
        消耗item unitsCount个单位
        @param item: 那个道具
        @param unitsCount: 多少个单位
        @return: consumeCount
        '''
        assert (item.itemKind.singleMode)
        if unitsCount > 0:
            balance = item.balance(timestamp)
            if balance >= unitsCount:
                item.consume(unitsCount, timestamp)
                self.updateItem(item, timestamp)
                tybireport.itemUpdate(gameId, self.userId, item.kindId,
                                      -unitsCount, self.calcTotalUnitsCount(item.itemKind, timestamp),
                                      eventId, intEventParam)
                self._onCountChanged()
                return unitsCount
        return 0

    def consumeUnitsCountByKind(self, gameId, itemKind, unitsCount, timestamp, eventId, intEventParam):
        '''
        消耗道具种类为itemKind的unitsCount个单位的道具
        @param itemKind: 那种类型
        @param unitsCount: 多少个单位
        @return: consumeCount
        '''
        if unitsCount <= 0:
            return 0

        if not itemKind.singleMode:
            sameKindItemList = self.getAllKindItem(itemKind)
            if len(sameKindItemList) < unitsCount:
                return 0
            for i in xrange(unitsCount):
                item = sameKindItemList[i]
                self._removeItem(item)
            tybireport.itemUpdate(gameId, self.userId, itemKind.kindId,
                                  -unitsCount, len(sameKindItemList) - unitsCount,
                                  eventId, intEventParam)
        else:
            item = self.getItemByKind(itemKind)
            if item is None:
                return 0
            balance = item.balance(timestamp)
            if balance < unitsCount:
                return 0
            item.consume(unitsCount, timestamp)
            self._updateItem(item, timestamp)
            tybireport.itemUpdate(gameId, self.userId, item.kindId,
                                  -unitsCount, balance - unitsCount,
                                  eventId, intEventParam)
        self._onCountChanged()
        return unitsCount

    def forceConsumeUnitsCountByKind(self, gameId, itemKind, unitsCount, timestamp, eventId, intEventParam):
        '''
        强制消耗道具种类为itemKind的unitsCount个单位的道具，如果不够则消耗所有的
        @param itemKind: 那种类型
        @param unitsCount: 多少个单位
        @return: consumeCount
        '''
        if unitsCount <= 0:
            return 0

        if not itemKind.singleMode:
            sameKindItemList = self.getAllKindItem(itemKind)
            consumeCount = min(sameKindItemList, unitsCount)
            for i in xrange(consumeCount):
                item = sameKindItemList[i]
                self._removeItem(item)
            tybireport.itemUpdate(gameId, self.userId, itemKind.kindId,
                                  -consumeCount, len(sameKindItemList) - consumeCount,
                                  eventId, intEventParam)
        else:
            item = self.getItemByKind(itemKind)
            if item:
                balance = item.balance(timestamp)
                consumeCount = min(balance, unitsCount)
                item.consume(consumeCount, timestamp)
                self._updateItem(item, timestamp)
                tybireport.itemUpdate(gameId, self.userId, item.kindId,
                                      -consumeCount, balance - consumeCount,
                                      eventId, intEventParam)
        self._onCountChanged()
        return unitsCount

    def updateItem(self, item, timestamp=None):
        '''
        保存道具
        @param item: 要保存的道具
        '''
        found = self.findItem(item.itemId)
        if found != item:
            ftlog.error('TYUserBagImpl.updateItem userId=', self.userId,
                        'item=', item,
                        'found=', found)
            raise ValueError()
        timestamp = timestamp or fttime.getCurrentTimestamp()
        self._updateItem(item, timestamp)
        return item

    def processWhenUserLogin(self, gameId, clientId, isDayFirst, timestamp=None):
        '''
        当用户登录时调用该方法，处理对用户登录感兴趣的道具
        @param gameId: 哪个游戏驱动
        @param isDayFirst: 是否是
        '''
        items = list(self._itemIdMap.values())
        timestamp = timestamp if timestamp is not None else fttime.getCurrentTimestamp()
        for item in items:
            if item.needRemoveFromBag(timestamp):
                self._removeItem(item)
            else:
                item.itemKind.processWhenUserLogin(item, self._assets, clientId,
                                                   gameId, isDayFirst, timestamp)

    def getExecutableActions(self, gameId, clientId, item, timestamp):
        '''
        获取item支持的动作列表
        @return: list<TYItemAction>
        '''
        ret = []
        for action in item.itemKind.actionList:
            if action.canDo(gameId, clientId, self, item, timestamp):
                ret.append(action)
        return ret

    def _findActionByName(self, actions, actionName):
        if actions:
            for action in actions:
                if action.name == actionName:
                    return action
        return None

    def _addItem(self, item):
        if item.itemId in self._itemIdMap:
            raise TYDuplicateItemIdException(item.itemId)
        self._addItemToMap(item)
        self._dao.saveItem(self.userId, item)
        self._updateRedPointInfo(0, item)

    def _removeItem(self, item):
        self._removeItemFromMap(item)
        self._dao.removeItem(self.userId, item.itemId)
        self._updateRedPointInfo(1, item)

    def _updateItem(self, item, timestamp):
        if item.needRemoveFromBag(timestamp):
            self._removeItem(item)
            self._updateRedPointInfo(1, item)
        else:
            self._dao.saveItem(self.userId, item)
            self._updateRedPointInfo(0, item)
        return item

    def _addItemToMap(self, item):
        self._itemIdMap[item.itemId] = item
        idMap = self._kindIdMap.get(item.kindId)
        if not idMap:
            idMap = {}
            self._kindIdMap[item.kindId] = idMap
        idMap[item.itemId] = item

    def _removeItemFromMap(self, item):
        del self._itemIdMap[item.itemId]
        idMap = self._kindIdMap.get(item.kindId)
        del idMap[item.itemId]
        if not idMap:
            del self._kindIdMap[item.kindId]


    def _updateRedPointInfo(self, isRemove, item):
        if isRemove :
            # 删除小红点提示信息
            pluginSafeCross.hallredpoint.removeItemIds(self.userId, 'item5', [item.itemId])
        else:
            # 更改至未读
            pluginSafeCross.hallredpoint.setItemUnRead(self.userId, 'item5', [item.itemId])
                
        
class TYUserAssets(object):

    def __init__(self, userId, itemSystem, itemDao):
        self._userId = userId
        self._itemSystem = itemSystem
        self._itemDao = itemDao
        self._userBag = None

    @property
    def userId(self):
        return self._userId

    def getUserBag(self):
        if not self._userBag:
            userBag = TYUserBag(self.userId, self._itemDao, self).load()
            if not self._userBag:
                self._userBag = userBag
        return self._userBag

    def balance(self, assetKindId, timestamp):
        '''
        获取assetKindId的余额
        '''
        assetKind = self._itemSystem.findAssetKind(assetKindId)
        if not assetKind:
            raise TYUnknownAssetKindException(assetKindId)
        return assetKind.balance(self, timestamp)

    def addAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam, param01='', param02=''):
        '''
        增加Asset
        @param gameId: 哪个游戏驱动的
        @param assetKindId: asset种类ID
        @param count: 个数
        @param timestamp: 时间戳
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: (AssetKind, count, final)
        '''
        assetKind = self._itemSystem.findAssetKind(assetKindId)
        if not assetKind:
            raise TYUnknownAssetKindException(assetKindId)
        final = assetKind.add(gameId, self, assetKind.kindId, count, timestamp, eventId, intEventParam, param01=param01, param02=param02)
        return assetKind, count, final

    def consumeAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam):
        '''
        消耗Asset
        @param gameId: 哪个游戏驱动的
        @param assetKindId: asset种类ID
        @param count: 个数
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: (TYAssetKind, consumeCount, final)
        '''
        assetKind = self._itemSystem.findAssetKind(assetKindId)
        if not assetKind:
            raise TYUnknownAssetKindException(assetKindId)
        consumeCount, final = assetKind.consume(gameId, self, assetKindId, count,
                                                timestamp, eventId, intEventParam)
        return assetKind, consumeCount, final

    def forceConsumeAsset(self, gameId, assetKindId, count, timestamp, eventId, intEventParam):
        '''
        消耗Asset
        @param gameId: 哪个游戏驱动的
        @param assetKindId: asset种类
        @param count: 个数
        @param timestamp: 时间戳
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: (TYAssetKind, consumeCount, final)
        '''
        assetKind = self._itemSystem.findAssetKind(assetKindId)
        if not assetKind:
            raise TYUnknownAssetKindException(assetKindId)
        consumeCount, final = assetKind.forceConsume(gameId, self, assetKindId, count,
                                                     timestamp, eventId, intEventParam)
        return assetKind, consumeCount, final

    def _backConsumed(self, gameId, assetList, eventId, intEventParam):
        for assetKind, count, _final in assetList:
            assetKind.add(gameId, self, assetKind.kindId, count, eventId, intEventParam)

    def consumeContentItemList(self, gameId, contentItemList, ignoreUnknown, timestamp, eventId, intEventParam):
        '''
        消耗contentItemList
        @param gameId: 哪个游戏驱动的
        @param contentItemList: 要消耗的内容
        @param ignoreUnknown: 是否忽略不认识的item, 如果不忽略则会抛出异常
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: list<(TYAssetKind, consumeCount, final)>
        '''
        ret = []
        assetKindCountTupleList = []
        for contentItem in contentItemList:
            if contentItem.count <= 0:
                continue
            assetKind = self._itemSystem.findAssetKind(contentItem.assetKindId)
            if not assetKind:
                if ignoreUnknown:
                    continue
                raise TYUnknownAssetKindException(contentItem.assetKindId)
            balance = assetKind.balance(self, timestamp)
            if balance < contentItem.count:
                raise TYAssetNotEnoughException(assetKind, contentItem.count, balance)
            assetKindCountTupleList.append((assetKind, contentItem.count))

        for assetKind, count in assetKindCountTupleList:
            consumeCount, final = assetKind.consume(gameId, self, assetKind.kindId, count, timestamp, eventId,
                                                    intEventParam)
            if consumeCount >= count:
                ret.append((assetKind, consumeCount, final))
            else:
                self._backConsumed(gameId, ret, eventId, intEventParam)
                raise TYAssetNotEnoughException(assetKind, consumeCount, final)
        return ret

    def sendContentItemList(self, gameId, contentItemList, count, ignoreUnknown, timestamp, eventId, intEventParam, param01='', param02=''):
        '''
        给用户发货
        @param gameId: 哪个游戏驱动的
        @param contentItemList: 要发货的内容
        @param ignoreUnknown: 是否忽略不认识的item, 如果不忽略则会抛出异常
        @param eventId: 哪个事件触发的
        @param intEventParam: eventId相关的参数
        @return: list<(TYAssetKind, consumeCount, final)>
        '''
        assert (count >= 1)
        ret = []
        contentItemList = tycontent.mergeContentItemList(contentItemList)
        assetKindCountTuple = []
        for contentItem in contentItemList:
            assetKind = self._itemSystem.findAssetKind(contentItem.assetKindId)
            if not assetKind and not ignoreUnknown:
                raise TYUnknownAssetKindException(contentItem.assetKindId)
            if not assetKind:
                ftlog.error('TYUserAssetsImpl.sendContentItemList unknow kindId gameId=', gameId,
                            'userId=', self.userId,
                            'assetKindId=', contentItem.assetKindId,
                            'count=', count)
            if assetKind and contentItem.count > 0:
                assetKindCountTuple.append((assetKind, contentItem.count * count))
        i = 0
        try:
            for assetKind, count in assetKindCountTuple:
                i += 1
                self.getUserBag()._isSendToUser = (i == len(assetKindCountTuple))
                final = assetKind.add(gameId, self, assetKind.kindId, count, timestamp, eventId, intEventParam, param01=param01, param02=param02)
                ret.append((assetKind, count, final))
        finally:
            self.getUserBag()._isSendToUser = True
        return ret


class HallItemSystem(TYItemSystem):

    def __init__(self):
        super(HallItemSystem, self).__init__()
        self._itemDao = TYItemDao(self)

    def clearCacheByUserId(self, userId):
        self._itemDao.clearCacheByUserId(userId)

    @property
    def itemDao(self):
        return self._itemDao

    def _makeItemAsset(self, itemKind):
        from hall5.plugins.hallitem._private.assetkind import HallAssetKindItem
        return HallAssetKindItem(itemKind)

    def loadUserAssets(self, userId):
        '''
        加载用户背包
        @return: UserAssets
        '''
        return TYUserAssets(userId, self, self._itemDao)

    def newItemFromItemData(self, itemData):
        itemKind = self.findItemKind(itemData.itemKindId)
        if itemKind:
            itemId = self._itemDao.nextItemId()
            item = itemKind.newItemForDecode(itemId)
            item.decodeFromItemData(itemData)
            return item
