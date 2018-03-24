# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''

from datetime import datetime

from freetime5.util import ftlog, fttime
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.plugins.hallitem._private import _checker
from hall5.plugins.hallitem._private.itemhelper import ItemHelper
from tuyoo5.core import tychecker
from tuyoo5.core import typlugin, tyglobal
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.core.typlugin import hallRpcOne, hallRpcRandom
from tuyoo5.game import tysessiondata
from tuyoo5.game import tygameitem
from tuyoo5.plugins.item import itemsys


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginItemHttp(object):

    def __init__(self):
        self.checkHttpGdss = tychecker.Checkers(
            hallchecker.check__gdssSingCode,
        )
        self.checkHttpUser = tychecker.Checkers(
            tychecker.check_userId,
            hallchecker.check__gdssSingCode,
            hallchecker.check__checkUserData
        )
        self.checkHttpActAdd = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_kindId,
            _checker.check_intEventParam,
            _checker.check_count,
            hallchecker.check__gdssSingCode,
            hallchecker.check__checkUserData,
        )
        self.checkHttpActConsume = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_kindId,
            _checker.check_intEventParam,
            _checker.check_count,
            hallchecker.check__gdssSingCode,
            hallchecker.check__checkUserData,
        )
        self.checkHttpActRemove = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_itemId,
            _checker.check_intEventParam,
            hallchecker.check__gdssSingCode,
            hallchecker.check__checkUserData,
        )
        self.checkHttpDoAction = tychecker.Checkers(
            tychecker.check_userId,
            tychecker.check_gameId,
            _checker.check_itemId,
            _checker.check_action,
            hallchecker.check__gdssSingCode,
            hallchecker.check__checkUserData,
        )
        self.checkHttpSetExpires = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_itemId,
            _checker.check_expires,
            hallchecker.check__gdssSingCode,
            hallchecker.check__checkUserData,
        )
        self.checkHttpSetCreateTime = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_itemId,
            _checker.check_createTime,
            hallchecker.check__gdssSingCode,
            hallchecker.check__checkUserData,
        )

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _gdssListItem(self):
        itemKindList = itemsys.itemSystem.getAllItemKind()
        items = []
        for itemKind in itemKindList:
            items.append({
                'kindId': itemKind.kindId,
                'displayName': itemKind.displayName,
                'masks': 0
            })
        return items

    def _encodeItem(self, userBag, item, timestamp):
        clientId = tysessiondata.getClientId(userBag.userId)
        ret = {
            'itemId': item.itemId,
            'kindId': item.kindId,
            'displayName': item.itemKind.displayName,
            'pic': item.itemKind.pic,
            'count': max(1, item.balance(timestamp)),
            'units': item.itemKind.units.displayName,
            'actions': ItemHelper.encodeItemActionList(HALL_GAMEID, clientId, userBag, item, timestamp),
            'visible': True if item.itemKind.visibleInBag and item.visibleInBag(timestamp) else False
        }
        if item.createTime > 0:
            ret['createTime'] = datetime.fromtimestamp(item.createTime).strftime('%Y-%m-%d %H:%M:%S')
        else:
            ret['createTime'] = ''
        if item.itemKind.units.isTiming and item.expiresTime > 0:
            ret['expires'] = datetime.fromtimestamp(item.expiresTime).strftime('%Y-%m-%d %H:%M:%S')
        else:
            ret['expires'] = ''
        extDatas = {}
        extNames = item.itemKind.newItemData()._getFieldNames()
        if extNames:
            for n in extNames:
                extDatas[n] = getattr(item, n, None)
        ret['extDatas'] = extDatas
        return ret

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _gdssListUserItem(self, userId):
        userBag = itemsys.itemSystem.loadUserAssets(userId).getUserBag()
        items = []
        timestamp = fttime.getCurrentTimestamp()
        for item in userBag.getAllItem():
            items.append(self._encodeItem(userBag, item, timestamp))
        return items

    @typlugin.markPluginEntry(httppath='_gdss/item/list')
    def doGdssListItem(self, request):
        mo = MsgPack()
        mi = self.checkHttpGdss.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            mo.setResult('items', hallRpcRandom.hallitem._gdssListItem().getResult())
        return mo

    @typlugin.markPluginEntry(httppath='_gdss/user/item/list')
    def doGdssListUserItem(self, request):
        mo = MsgPack()
        mi = self.checkHttpUser.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            result = hallRpcOne.hallitem._gdssListUserItem(mi.userId).getResult()
            mo.setResult('items', result)
        return mo

    @typlugin.markPluginEntry(httppath='_gdss/user/item/add')
    def doGdssAddUserItem(self, request):
        mo = MsgPack()
        mi = self.checkHttpActAdd.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            rfc = hallRpcOne.hallitem.addAsset(mi.userId,
                                               HALL_GAMEID,
                                               tygameitem.itemIdToAssetId(mi.kindId),
                                               mi.count,
                                               "GM_ADJUST",
                                               mi.intEventParam)
            _, addCount, _final = rfc.getResult()
            if addCount <= 0:
                ec, result = -1, '不能识别的道具类型: %s' % mi.kindId
                mo.setError(ec, result)
            else:
                mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='_gdss/user/item/remove')
    def doGdssRemoveUserItem(self, request):
        mo = MsgPack()
        mi = self.checkHttpActRemove.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            rfc = hallRpcOne.hallitem.removeUserItem(mi.userId,
                                                     HALL_GAMEID,
                                                     mi.itemId,
                                                     "GM_ADJUST",
                                                     mi.intEventParam)
            ec, result = rfc.getResult()
            if ec != 0:
                mo.setError(ec, result)
            else:
                mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='_gdss/user/item/consume')
    def doGdssConsumeUserItem(self, request):
        mo = MsgPack()
        mi = self.checkHttpActConsume.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            _, consumeCount, final = hallRpcOne.hallitem.consumeAsset(mi.userId,
                                                                      HALL_GAMEID,
                                                                      tygameitem.itemIdToAssetId(mi.kindId),
                                                                      mi.count,
                                                                      "GM_ADJUST",
                                                                      mi.intEventParam).getResult()
            if consumeCount <= 0:
                ec, result = (-1, '不能识别的道具类型: %s' % mi.kindId) if final <= 0 else (-1, '道具数量不足')
                mo.setError(ec, result)
            else:
                mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='_gdss/user/item/doaction')
    def doHttpUserItemAction(self, request):
        mo = MsgPack()
        mi = self.checkHttpDoAction.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            params = request.getDict()
            result = hallRpcOne.hallitem.doActionByItemId(mi.userId,
                                                          mi.gameId,
                                                          mi.itemId,
                                                          mi.action,
                                                          fttime.getCurrentTimestamp(),
                                                          params).getResult()
            mo.setKey('result', result)
        return mo

    @typlugin.markPluginEntry(httppath='_gdss/user/item/removeAll')
    def doHttpUserItemRemoveAll(self, request):
        mo = MsgPack()
        mi = self.checkHttpUser.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            result = hallRpcOne.hallitem.removeAllItem(mi.userId,
                                                       HALL_GAMEID,
                                                       "GM_ADJUST").getResult()
            mo.setKey('result', result)
        return mo

    @typlugin.markPluginEntry(httppath='_gdss/user/item/addAll')
    def doHttpUserItemAddAll(self, request):
        mo = MsgPack()
        mi = self.checkHttpUser.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            result = hallRpcOne.hallitem.addAllItem(mi.userId,
                                                    HALL_GAMEID,
                                                    "GM_ADJUST").getResult()
            mo.setKey('result', result)
        return mo

    @typlugin.markPluginEntry(httppath='_gdss/user/item/setExpires')
    def doHttpUserItemExpires(self, request):
        mo = MsgPack()
        mi = self.checkHttpSetExpires.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            ec, msg = hallRpcOne.hallitem.setItemExpires(mi.userId, mi.itemId, mi.expires).getResult()
            if ec:
                mo.setError(ec, msg)
            else:
                mo.setResult('ok', msg)
        return mo

    @typlugin.markPluginEntry(httppath='_gdss/user/item/setCreateTime')
    def doHttpUserItemCreateTime(self, request):
        mo = MsgPack()
        mi = self.checkHttpSetCreateTime.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            ec, msg = hallRpcOne.hallitem.setItemCreateTime(mi.userId, mi.itemId, mi.createTime).getResult()
            if ec:
                mo.setError(ec, msg)
            else:
                mo.setResult('ok', msg)
        return mo
