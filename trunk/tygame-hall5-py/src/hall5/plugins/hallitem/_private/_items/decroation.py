# -*- coding=utf-8 -*-
'''
Created on 2017年7月13日

@author: zqh
'''
from tuyoo5.plugins.item import items


class TYDecroationItemKind(items.TYItemKind):

    TYPE_ID = 'common.decroation'

    def newItemData(self):
        return TYDecroationItemData()

    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYDecroationItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        item.isWore = 0
        return item

    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYDecroationItem(self, itemId)


class TYDecroationItem(items.TYItem):

    def __init__(self, itemKind, itemId):
        super(TYDecroationItem, self).__init__(itemKind, itemId)
        assert (isinstance(itemKind, TYDecroationItemKind))
        self.isWore = 0


@items.initTYItemDataStruct
class TYDecroationItemData(items.TYItemData):

    def __init__(self):
        super(TYDecroationItemData, self).__init__()
        self.isWore = 0

    @classmethod
    def _getStructFormat(cls):
        return 'B'

    @classmethod
    def _getFieldNames(cls):
        return ['isWore']
