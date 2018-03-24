# -*- coding=utf-8 -*-
'''
Created on 2017年7月13日

@author: zqh
'''
from tuyoo5.plugins.item import items


class TYExchangeItemKind(items.TYItemKind):

    TYPE_ID = 'common.exchange'

    def newItem(self, itemId, timestamp):
        '''
        产生一个本种类的道具id=itemId的道具
        @param itemId: 道具ID
        @return: SimpleItem
        '''
        item = TYExchangeItem(self, itemId)
        item.createTime = timestamp
        item.remaining = 0
        return item

    def newItemForDecode(self, itemId):
        '''
        从itemData中解码item
        '''
        return TYExchangeItem(self, itemId)

    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYExchangeItemData()


class TYExchangeItem(items.TYItem):
    '''
    简单道具，不能使用，只能消耗
    '''
    STATE_NORMAL = 0  # 未审核
    STATE_AUDIT = 1  # 审核中
    STATE_SHIPPING = 2  # 发货中

    def __init__(self, itemKind, itemId):
        super(TYExchangeItem, self).__init__(itemKind, itemId)
        assert (isinstance(itemKind, TYExchangeItemKind))
        self.state = TYExchangeItem.STATE_NORMAL

    def visibleInBag(self, timestamp):
        # 审核中的道具不显示
        visible = items.TYItem.visibleInBag(self, timestamp)
        if visible:
            return self.state == TYExchangeItem.STATE_NORMAL
        return visible

    def _decodeFromItemData(self, itemData):
        self.state = itemData.state

    def _encodeToItemData(self, itemData):
        itemData.state = self.state


@items.initTYItemDataStruct
class TYExchangeItemData(items.TYItemData):

    def __init__(self):
        super(TYExchangeItemData, self).__init__()
        self.state = TYExchangeItem.STATE_NORMAL

    @classmethod
    def _getStructFormat(cls):
        return 'B'

    @classmethod
    def _getFieldNames(cls):
        return ['state']
