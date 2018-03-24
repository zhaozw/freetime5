# -*- coding=utf-8 -*-
"""
@file  : itemaction
@date  : 2016-09-22
@author: GongXiaobo
"""

from datetime import datetime

from freetime5.util import ftlog
from hall5.plugins.hallitem._private._actions import _action
from hall5.plugins.hallitem._private._items.submember import TYMemberCardItem
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tycontent
from tuyoo5.plugins.item import assetutils, items
from tuyoo5.plugins.item.itemexceptions import TYItemConfException


class TYItemActionCheckinResult(items.TYItemActionResult):
    def __init__(self, action, item, message, gotAssetList):
        super(TYItemActionCheckinResult, self).__init__(action, item, 0, message)
        self.gotAssetList = gotAssetList


class TYItemActionCheckin(_action.HallItemAction):
    TYPE_ID = 'common.checkin'

    def __init__(self):
        super(TYItemActionCheckin, self).__init__()
        self.content = None

    def _decodeFromDictImpl(self, d):
        content = d.get('content')
        if not content:
            raise TYItemConfException(d, 'TYItemActionCheckin.content must be set')
        self.content = tycontent.decodeFromDict(content)

    def canDo(self, gameId, clientId, userBag, item, timestamp):
        return False

    def doAction(self, gameId, clientId, userAssets, item, timestamp, params):
        assert (isinstance(item, TYMemberCardItem))
        if item.isExpires(timestamp):
            return items.TYItemActionResult(None, None, -30, '道具已经过期', None)

        if not item.canCheckin(timestamp):
            return items.TYItemActionResult(None, None, -31, '道具已经签到过', None)

        # 保存item
        item.checkinTime = timestamp
        userBag = userAssets.getUserBag()
        userBag.updateItem(item, timestamp)

        # 发放开出的奖品
        # 检查是否是订阅会员
        ct = datetime.fromtimestamp(timestamp)
        eventId = 'ITEM_USE' if pluginCross.hallsubmember.isSubExpires(userAssets.userId, ct) else 'ITEM_SUB_MEMBER_CHECKIN'
        assetItemList = userAssets.sendContentItemList(gameId,
                                                       self.content.getItems(),
                                                       1,
                                                       True,
                                                       timestamp,
                                                       eventId,
                                                       item.kindId)
        gotContent = assetutils.buildContentsString(assetItemList)
        replaceParams = {'gotContent': gotContent}
        _mail, message, _changed = _action._handleMailAndMessageAndChanged(gameId,
                                                                           userAssets,
                                                                           self,
                                                                           assetItemList,
                                                                           replaceParams)

        ftlog.info('TYItemActionCheckin._doActionImpl gameId=', gameId,
                   'userId=', userAssets.userId,
                   'itemId=', item.itemId,
                   'itemKindId=', item.kindId,
                   'gotContent=', gotContent,
                   'mail=', _mail,
                   'message=', message,
                   'changed=', _changed)
        # TGHall.getEventBus().publishEvent(TYCheckinItemEvent(gameId, userBag.userId, item, assetItemList))
        return TYItemActionCheckinResult(self, item, message, assetItemList)
