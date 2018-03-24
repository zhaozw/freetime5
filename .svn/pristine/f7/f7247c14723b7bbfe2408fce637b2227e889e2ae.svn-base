# coding:utf-8
from majiang2.poker2.entity import hallrpcutil
from tuyoo5.game import tygameitem
from freetime5.twisted.ftlock import lockargname


class MajiangItem(object):
    """道具
    """
#     @classmethod
#     def encodeItemAction(cls, gameId, userBag, item, action, timestamp):
#         ret = {
#             'action': action.name,
#             'name': action.displayName,
#         }
#         inputParams = action.getInputParams(gameId, userBag, item, timestamp)
#         if inputParams:
#             ret['params'] = inputParams
#         return ret
#
#     @classmethod
#     def encodeItemActionList(cls, gameId, userBag, item, timestamp):
#         ret = []
#         actions = userBag.getExecutableActions(item, timestamp)
#         for action in actions:
#             ret.append(cls.encodeItemAction(gameId, userBag, item, action, timestamp))
#         return ret
#
#     @classmethod
#     def encodeUserItem(cls, gameId, userBag, item, timestamp):
#         ret = {
#             'id': item.itemId,
#             'kindId': item.kindId,
#             'name': item.itemKind.displayName,
#             'units': item.itemKind.units.displayName,
#             'desc': item.itemKind.desc,
#             'pic': item.itemKind.pic,
#             'count': max(1, item.remaining),
#             'actions': cls.encodeItemActionList(gameId, userBag, item, timestamp)
#         }
#         if item.expiresTime >= 0:
#             ret['expires'] = item.expiresTime
#         return ret
#
#     @classmethod
#     def encodeUserItemList(cls, gameId, userBag, timestamp):
#         ret = []
#         itemList = userBag.getAllItem()
#         for item in itemList:
#             if item.itemKind.visibleInBag and item.visibleInBag(timestamp):
#                 ret.append(cls.encodeUserItem(gameId, userBag, item, timestamp))
#         return ret

    @classmethod
    def getUserItemCountByKindId(cls, userId, kindId):
        assetKindId = tygameitem.itemIdToAssetId(kindId)
        return hallrpcutil.getAssets(userId, assetKindId)

    @classmethod
    def consumeItemByKindId(cls, userId, gameId, kindId, count, eventId, roomId=0):
        """道具消费
        """
        assetKindId = tygameitem.itemIdToAssetId(kindId)
        _kindId, consumeCount, _final = hallrpcutil.consumeAsset(userId,
                                                                 gameId,
                                                                 assetKindId,
                                                                 count,
                                                                 eventId,
                                                                 roomId)
        return consumeCount == count

    @classmethod
    def addUserItemByKindId(cls, userId, gameId, kindId, count, eventId, roomId=0):
        assetKindId = tygameitem.itemIdToAssetId(kindId)
        _kindId, addCount, _final = hallrpcutil.addAsset(userId,
                                                         gameId,
                                                         assetKindId,
                                                         count,
                                                         eventId,
                                                         roomId)
        return addCount == count
