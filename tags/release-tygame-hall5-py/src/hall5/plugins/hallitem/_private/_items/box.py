# -*- coding=utf-8 -*-
'''
Created on 2017年7月13日

@author: zqh
'''
from tuyoo5.plugins.item import items


class TYBoxItemKind(items.TYItemKind):

    TYPE_ID = 'common.box'

    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYBoxItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        return item

    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYBoxItem(self, itemId)

    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYBoxItemData()


class TYBoxItem(items.TYItem):
    '''
    宝箱类道具，可以打开获得东西
    '''

    def __init__(self, itemKind, itemId):
        super(TYBoxItem, self).__init__(itemKind, itemId)
        assert (isinstance(itemKind, TYBoxItemKind))
        self.openTimes = 0

    def _decodeFromItemData(self, itemData):
        self.openTimes = itemData.openTimes

    def _encodeToItemData(self, itemData):
        itemData.openTimes = self.openTimes


@items.initTYItemDataStruct
class TYBoxItemData(items.TYItemData):
    def __init__(self):
        super(TYBoxItemData, self).__init__()
        self.openTimes = 0

    @classmethod
    def _getStructFormat(cls):
        return 'i'

    @classmethod
    def _getFieldNames(cls):
        return ['openTimes']
