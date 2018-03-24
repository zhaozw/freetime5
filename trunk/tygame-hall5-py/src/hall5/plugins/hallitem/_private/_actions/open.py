# -*- coding=utf-8 -*-
"""
@file  : itemaction
@date  : 2016-09-22
@author: GongXiaobo
"""

from hall5.plugins.hallitem._private._actions import _action
from hall5.plugins.hallitem._private._items.box import TYBoxItem
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tycontent
from tuyoo5.game._private._tycontent import TYContentItem, TYEmptyContent
from tuyoo5.plugins.item import assetutils, items
from tuyoo5.plugins.item.itemexceptions import TYItemConfException


class TYItemActionBoxOpenResult(items.TYItemActionResult):
    def __init__(self, action, item, message, gotAssetList, todotask):
        super(TYItemActionBoxOpenResult, self).__init__(action, item, 0, message, todotask)
        self.gotAssetList = gotAssetList


class _TYItemBindings(object):

    def __init__(self, items, params):
        self.items = items
        self.params = params

    def getParam(self, paramName, defVal=None):
        return self.params.get(paramName, defVal)

    @property
    def failure(self):
        return self.getParam('failure', '')

    @classmethod
    def decodeFromDict(cls, d):
        params = d.get('params', {})
        if not isinstance(params, dict):
            raise TYItemConfException(d, 'TYItemBindings.params must be dict')
        items = TYContentItem.decodeList(d.get('items', []))
        return cls(items, params)

    # 处理items
    def consume(self, gameId, item, userAssets, timestamp, eventId, intEventParam):
        for contentItem in self.items:
            assetKind, consumeCount, final = userAssets.consumeAsset(gameId,
                                                                     contentItem.assetKindId,
                                                                     contentItem.count,
                                                                     timestamp,
                                                                     eventId,
                                                                     intEventParam)
            if consumeCount == contentItem.count:
                return True, (assetKind, consumeCount, final)
        return False, None


class TYItemActionBoxOpen(_action.HallItemAction):

    TYPE_ID = 'common.box.open'

    def __init__(self):
        super(TYItemActionBoxOpen, self).__init__()
        self.itemBindings = None
        self.contentList = None
        self.nextItemKindId = None
        self.nextItemKind = None

    def _decodeFromDictImpl(self, d):
        bindings = d.get('bindings')
        if bindings:
            self.itemBindings = _TYItemBindings.decodeFromDict(bindings)
        self.contentList = self._decodeContents(d)
        self.nextItemKindId = d.get('nextItemKindId')
        if self.nextItemKindId is not None and not isinstance(self.nextItemKindId, int):
            raise TYItemConfException(d, 'TYItemActionBoxOpen.nextItemKindId must be int')

    def _decodeContents(self, d):
        '''
        从d中解析数据
        '''
        contentList = []
        contents = d.get('contents')
        if not isinstance(contents, list) or not contents:
            raise TYItemConfException(d, 'TYItemActionBoxOpen.contents must be not empty list')
        for contentConf in contents:
            openTimes = contentConf.get('openTimes', {'start': 0, 'stop': -1})
            if not isinstance(openTimes, dict):
                raise TYItemConfException(contentConf, 'TYItemActionBoxOpen.openTimes must be dict')
            startTimes = openTimes.get('start')
            stopTimes = openTimes.get('stop')
            if (not isinstance(startTimes, int)
                    or not isinstance(stopTimes, int)):
                raise TYItemConfException(openTimes, 'TYItemActionBoxOpen.openTimes.start end must be int')
            if 0 <= stopTimes < startTimes:
                raise TYItemConfException(openTimes, 'TYItemActionBoxOpen.openTimes.stop must ge start')
            content = tycontent.decodeFromDict(contentConf)
            contentList.append((startTimes, stopTimes, content))
        return contentList

    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        if self.nextItemKindId:
            nextItemKind = itemKindMap.get(self.nextItemKindId)
            if not nextItemKind:
                raise TYItemConfException(self.conf, 'TYItemActionBoxOpen._initWhenLoad unknown nextItemKind %s' % (
                    self.nextItemKindId))
            self.nextItemKind = nextItemKind

    def canDo(self, gameId, clientId, userBag, item, timestamp):
        return not item.isDied(timestamp)

    def doAction(self, gameId, clientId, userAssets, item, timestamp, params):
        assert (isinstance(item, TYBoxItem))
        userBag = userAssets.getUserBag()

        if item.isDied(timestamp):
            return items.TYItemActionResult(None, None, -30, '道具已经过期', None)

        if self.itemBindings:
            ok, _assetTuple = self.itemBindings.consume(gameId,
                                                        item,
                                                        userAssets,
                                                        timestamp,
                                                        'ITEM_USE',
                                                        item.kindId)
            if not ok:
                return _action._makeTodoWithPayOrder(self.itemBindings,
                                                     gameId,
                                                     userAssets.userId,
                                                     clientId)
        if not item.itemKind.singleMode:
            # 互斥型道具打开时直接删除
            userBag.removeItem(gameId, item, timestamp, 'ITEM_USE', item.kindId)
        else:
            # 保存item
            item.openTimes += 1
            item.original = 0
            userBag.consumeItemUnits(gameId, item, 1, timestamp, 'ITEM_USE', item.kindId)

        sendItems = self._getContent(item).getItems()
        assetItemList = userAssets.sendContentItemList(gameId,
                                                       sendItems,
                                                       1,
                                                       True,
                                                       timestamp,
                                                       'ITEM_USE',
                                                       item.kindId)
        # 如果需要生成下一个道具
        if self.nextItemKind:
            userBag.addItemUnitsByKind(gameId,
                                       self.nextItemKind,
                                       1,
                                       timestamp,
                                       0,
                                       'ITEM_USE',
                                       item.kindId)
        # 生成打开生成的列表
        rewardsList = []
        for assetItemTuple in assetItemList:
            '''
            0 - assetItem
            1 - count
            2 - final
            '''
            assetItem = assetItemTuple[0]
            reward = {'name': assetItem.displayName, 'pic': assetItem.pic, 'count': assetItemTuple[1],
                      'kindId': assetItem.kindId}
            rewardsList.append(reward)
        rewardTodotask = pluginCross.halltodotask.makeTodoTaskShowRewards(rewardsList)

        # 提示文案
        gotContent = assetutils.buildContentsString(assetItemList)
        # 提示消息替换参数
        replaceParams = {'item': item.itemKind.displayName, 'gotContent': gotContent}
        _mail, message, _changed = _action._handleMailAndMessageAndChanged(gameId,
                                                                           userAssets,
                                                                           self,
                                                                           assetItemList,
                                                                           replaceParams)
        # TGHall.getEventBus().publishEvent(TYOpenItemEvent(gameId, userBag.userId, item, assetItemList))
        return TYItemActionBoxOpenResult(self, item, message, assetItemList, rewardTodotask)

    def _getContent(self, item):
        if self.contentList:
            openTimes = max(item.openTimes - 1, 0)
            for startTimes, stopTimes, content in self.contentList:
                if (startTimes < 0 or openTimes >= startTimes) and (stopTimes < 0 or openTimes <= stopTimes):
                    return content
        return TYEmptyContent()
