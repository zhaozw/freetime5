# -*- coding=utf-8 -*-
'''
Created on 2017年7月13日

@author: zqh
'''
from tuyoo5.plugins.item import items


class TYSimpleItemKind(items.TYItemKind):

    TYPE_ID = 'common.simple'

    def newItemData(self):
        return TYSimpleItemData()

    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYSimpleItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        return item

    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYSimpleItem(self, itemId)


class TYSimpleItem(items.TYItem):
    '''
    简单道具，不能使用，只能消耗
    '''

    def __init__(self, itemKind, itemId):
        super(TYSimpleItem, self).__init__(itemKind, itemId)
        assert (isinstance(itemKind, TYSimpleItemKind))

@items.initTYItemDataStruct
class TYSimpleItemData(items.TYItemData):
    def __init__(self):
        super(TYSimpleItemData, self).__init__()
