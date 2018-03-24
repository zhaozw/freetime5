# -*- coding=utf-8 -*-
"""
@file  : itemdao
@date  : 2016-09-23
@author: GongXiaobo
"""

from freetime5.util import ftlog
from freetime5.util.ftcache import lfu_cache
from hall5.entity import hallchecker
from tuyoo5.core import tydao
from tuyoo5.core import tyglobal
from tuyoo5.plugins.item.items import TYItemData


class DaoUserItem(tydao.DataSchemaHashSameKeys):
    DBNAME = 'user'
    MAINKEY = 'item2:{}:%s'.format(tyglobal.gameId())
    SUBVALDEF = tydao.DataAttrBinary('item', '', 64)  # 实际目前长度只有30左右
    MAX_DATA_LENGTH = 0  # 这个不好办了,道具会越来越多,最多会存多少种道具？


class DaoMixGlobalId(tydao.DataSchemaHashAttrs):
    DBNAME = 'mix'
    MAINKEY = 'globalid'  # 也就是说这个表只有1行

    # 物品自增ID
    ATT_ITEM_ID = tydao.DataAttrIntAtomic('itemId', 0)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY


class DaoMixExCodeHash(tydao.DataSchemaHashSameKeys):
    MAINKEY = 'DaoMixExCodeHash'
    DBNAME = 'mix'
    SUBVALDEF = tydao.DataAttrObjDict('userId:x', {}, 512)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return 'item:' + str(mainKeyExt) + 'Map'


class DaoMixExCodeList(tydao.DataSchemaList):
    MAINKEY = 'DaoMixExCodeList'
    DBNAME = 'mix'

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return mainKeyExt

    @classmethod
    def getFreeExCode(cls, userId, kindId, phoneNumber, timestamp):
        itemList = 'item:' + str(kindId) + 'AllList'
        itemFinishList = 'item:' + str(kindId) + 'FinishList'
        exCode = cls.RPOPLPUSH(0, itemFinishList, itemList)
        if exCode:
            exCode = str(exCode)
            paramsTemp = {
                'userId': userId,
                'phoneNumber': phoneNumber,
                'time': timestamp,
                'exCode': exCode
            }
            DaoMixExCodeHash.HSET(0, 'userId:%d' % userId,  paramsTemp, kindId)
        return exCode


def initialize():
    DaoUserItem.initialize()
    DaoMixGlobalId.initialize()
    DaoMixExCodeList.initialize()
    DaoMixExCodeHash.initialize()


def finalize():
    DaoUserItem.finalize()
    DaoMixGlobalId.finalize()
    DaoMixExCodeList.finalize()
    DaoMixExCodeHash.finalize()


class TYItemDao(object):
    """
    启用缓存机制，避免大量无谓的消息通讯、binary解析，代价是内存消耗增长
    启用条件：数据同步应该是唯一且单向的(
        同一userid只能缓存在同一进程上;
        此进程负责拉取、保存,禁止其他方式操作redis物品数据)
    """

    def __init__(self, itemSystem):
        self._itemSystem = itemSystem

    def clearCacheByUserId(self, userId):
        self.loadAll.clear_keys([userId])

    @lfu_cache(maxsize=1024, cache_key_args_index=1)
    def loadAll(self, userId):
        """
        加载用户所有的道具
        """
        if not hallchecker.isCurrentUserHallUt(userId):  # 物品数据保护
            raise Exception('item access forbidden!!')
        datas = DaoUserItem.HGETALL(userId)
        itemdict = {}
        for itemId, itemDataBytes in datas.iteritems():
            item = self._decodeItem(userId, itemId, itemDataBytes)
            if item:
                itemdict[itemId] = item
        return itemdict

    def saveItem(self, userId, item):
        """
        保存用户道具
        """
        if not hallchecker.isCurrentUserHallUt(userId):  # 物品数据保护
            raise Exception('item access forbidden!!')
        itemDataBytes = TYItemData.encodeToBytes(item.encodeToItemData())
        DaoUserItem.HSET(userId, item.itemId, itemDataBytes)

    def removeItem(self, userId, itemId):
        """
        删除用户道具
        """
        if not hallchecker.isCurrentUserHallUt(userId):  # 物品数据保护
            raise Exception('item access forbidden!!')
        # 确保移除cache
        self.loadAll(userId).pop(itemId, None)
        DaoUserItem.HDEL(userId, itemId)

    def nextItemId(self):
        """
        获取一个全局唯一的道具Id
        """
        return DaoMixGlobalId.HINCRBY(0, DaoMixGlobalId.ATT_ITEM_ID, 1)

    def _decodeItem(self, userId, itemId, itemDataBytes):
        kindId = 0
        try:
            kindId = TYItemData.decodeKindId(itemDataBytes)
            itemKind = self._itemSystem.findItemKind(kindId)
            if itemKind:
                itemData = itemKind.newItemData()
                TYItemData.decodeFromBytes(itemData, itemDataBytes)
                item = itemKind.newItemForDecode(itemId)
                item.decodeFromItemData(itemData)
                return item
            else:
                ftlog.warn('TYItemDao._decodeItem kindId NOT FOUND ! userId=', userId,
                           'itemId=', itemId,
                           'kindId=', kindId,
                           'data=[', itemDataBytes, ']')
        except:
            ftlog.error('TYItemDao._decodeItem userId=', userId,
                        'itemId=', itemId,
                        'kindId=', kindId,
                        'data=', itemDataBytes)
        return None
