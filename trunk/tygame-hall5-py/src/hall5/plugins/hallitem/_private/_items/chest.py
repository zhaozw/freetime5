# -*- coding=utf-8 -*-
'''
Created on 2017年7月13日

@author: zqh
'''
from tuyoo5.plugins.item import items


class TYChestItemKind(items.TYItemKind):
    TYPE_ID = 'common.chest'

    def __init__(self):
        super(TYChestItemKind, self).__init__()

    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYChestItem(self, itemId)
        item.createTime = timestamp
        return item

    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYChestItem(self, itemId)

    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYChestItemData()


class TYChestItem(items.TYItem):
    '''
    捕鱼定时宝箱类道具，到时后可以打开获得东西
    '''

    def __init__(self, itemKind, itemId):
        super(TYChestItem, self).__init__(itemKind, itemId)
        assert (isinstance(itemKind, TYChestItemKind))
        self.chestId = 0
        self.order = 0
        self.beginTime = 0
        self.totalTime = 0
        self.state = 0

    def _decodeFromItemData(self, itemData):
        self.chestId = itemData.chestId
        self.order = itemData.order
        self.beginTime = itemData.beginTime
        self.totalTime = itemData.totalTime
        self.state = itemData.state

    def _encodeToItemData(self, itemData):
        itemData.chestId = self.chestId
        itemData.order = self.order
        itemData.beginTime = self.beginTime
        itemData.totalTime = self.totalTime
        itemData.state = self.state


@items.initTYItemDataStruct
class TYChestItemData(items.TYItemData):

    def __init__(self):
        super(TYChestItemData, self).__init__()
        self.remaining = 1
        self.chestId = 0
        self.order = 0
        self.beginTime = 0
        self.totalTime = 0
        self.state = 0

    @classmethod
    def _getStructFormat(cls):
        return 'HBIIB'

    @classmethod
    def _getFieldNames(cls):
        return ['chestId', 'order', 'beginTime', 'totalTime', 'state']
