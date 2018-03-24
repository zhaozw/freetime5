# -*- coding=utf-8 -*-
'''
Created on 2017年7月13日

@author: zqh
'''
from freetime5.util import fttime, ftlog
from tuyoo5.core import tyconfig
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tysessiondata
from tuyoo5.plugins.item import items
from tuyoo5.plugins.item.itemexceptions import TYItemConfException


class TYMemberCardItemKind(items.TYItemKind):
    TYPE_ID = 'common.memberCard'

    def __init__(self):
        super(TYMemberCardItemKind, self).__init__()
        self.checkinWhenAdded = None
        self.autoCheckinLimitVersion = -1

    def needAutoCheckin(self, userId):
        try:
            if self.autoCheckinLimitVersion != -1:
                clientId = tysessiondata.getClientId(userId)
                _, clientVer, _ = tyconfig.parseClientId(clientId)
                if clientVer >= self.autoCheckinLimitVersion:
                    return False
        except:
            ftlog.error('TYMemberCardItemKind.needAutoCheckin userId=', userId)
        return True

    def getCheckinContent(self):
        try:
            checkinAction = self.findActionByName('checkin')
            if checkinAction:
                return checkinAction.content
        except:
            ftlog.error()
        return None

    def _decodeFromDictImpl(self, d):
        checkinAction = self.findActionByName('checkin')
        if not checkinAction:
            raise TYItemConfException(d, 'TYMemberCardItemKind.actions.checkin must be set')
        self.checkinWhenAdded = d.get('checkinWhenAdded', 0)
        if self.checkinWhenAdded not in (0, 1):
            raise TYItemConfException(d, 'TYMemberCardItemKind.checkinWhenAdded must be int in (0,1)')

        self.autoCheckinLimitVersion = d.get('autoCheckinLimitVersion', -1)
        if not isinstance(self.autoCheckinLimitVersion, (int, float)):
            raise TYItemConfException(d, 'TYMemberCardItemKind.autoCheckinLimitVersion must be int or float')

    def newItem(self, itemId, timestamp):
        '''
        产生一个新的本种类的道具，id=itemId
        @param itemId: 道具ID
        @return: Item的子类
        '''
        item = TYMemberCardItem(self, itemId)
        item.createTime = timestamp
        item.checkinTime = 0
        item.expiresTime = 0
        return item

    def newItemForDecode(self, itemId):
        '''
        产生一个本种类的道具，用于反序列化
        '''
        return TYMemberCardItem(self, itemId)

    def newItemData(self):
        '''
        产生一个ItemData
        '''
        return TYMemberCardItemData()

    def processWhenUserLogin(self, item, userAssets, clientId, gameId, isDayFirst, timestamp):
        if self.needAutoCheckin(userAssets.userId) and item.canCheckin(timestamp):
            checkinAction = self.findActionByName('checkin')
            checkinAction.doAction(gameId, clientId, userAssets, item, timestamp, {})

    def processWhenAdded(self, item, userAssets, gameId, timestamp):
        if item.checkinTime == 0:
            if self.checkinWhenAdded and self.needAutoCheckin(userAssets.userId):
                # 从无到有需要checkin
                checkinAction = self.findActionByName('checkin')
                checkinAction.doAction(gameId, tysessiondata.getClientId(userAssets.userId), userAssets, item, timestamp, {})
            else:
                item.checkinTime = timestamp
            pluginCross.halldatanotify.sendDataChangeNotify(userAssets.userId, gameId, ['decoration'])


class TYMemberCardItem(items.TYItem):
    def __init__(self, itemKind, itemId):
        super(TYMemberCardItem, self).__init__(itemKind, itemId)
        assert (isinstance(itemKind, TYMemberCardItemKind))
        self.checkinTime = 0

    def canCheckin(self, timestamp):
        if self.isDied(timestamp):
            return False
        return fttime.getDayStartTimestamp(timestamp) > fttime.getDayStartTimestamp(self.checkinTime)

    def _decodeFromItemData(self, itemData):
        self.checkinTime = itemData.checkinTime

    def _encodeToItemData(self, itemData):
        itemData.checkinTime = self.checkinTime


@items.initTYItemDataStruct
class TYMemberCardItemData(items.TYItemData):
    def __init__(self):
        super(TYMemberCardItemData, self).__init__()
        self.checkinTime = 0

    @classmethod
    def _getStructFormat(cls):
        return 'i'

    @classmethod
    def _getFieldNames(cls):
        return ['checkinTime']
