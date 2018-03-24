# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''
from freetime5.twisted import ftcore
from freetime5.twisted.ftlock import lockargname
from freetime5.util import ftlog, fttime
from freetime5.util import ftstr
from hall5.plugins.hallitem._private._actions import _action
from hall5.plugins.hallitem._private.item_cmds import HallPluginItemCmds
from hall5.plugins.hallitem._private.item_event import HallPluginItemEvent
from hall5.plugins.hallitem._private.item_http import HallPluginItemHttp
from hall5.plugins.hallitem._private.item_life import HallPluginItemLife
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game.tycontent import TYContentItemGenerator
from tuyoo5.plugins.item import assetutils
from tuyoo5.plugins.item import itemsys
from tuyoo5.plugins.item.itemexceptions import TYAssetNotEnoughException


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginItem(HallPluginItemLife, HallPluginItemEvent, HallPluginItemCmds, HallPluginItemHttp):

    def __init__(self):
        HallPluginItemLife.__init__(self)
        HallPluginItemEvent.__init__(self)
        HallPluginItemCmds.__init__(self)
        HallPluginItemHttp.__init__(self)

    def _decodeContentItems(self, contentItems):
        ret = []
        genList = TYContentItemGenerator.decodeList(contentItems)
        for gen in genList:
            ret.append(gen.generate())
        return ret

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL, export=1)
    def getAssets(self, userId, assetKindIds):
        """
        获取资产数量
        :param userId: 用户id
        :param assetKindIds: 财富id 或者 财富id的序列
        :return:
        """
        userAssets = itemsys.itemSystem.loadUserAssets(userId)
        timestamp = fttime.getCurrentTimestamp()
        if isinstance(assetKindIds, (str, unicode)):
            return userAssets.balance(assetKindIds, timestamp)
        elif isinstance(assetKindIds, (list, tuple, set)):
            ret = {}
            for assetKindId in assetKindIds:
                ret[assetKindId] = userAssets.balance(assetKindId, timestamp)
            return ret

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL, export=1)
    @lockargname('hall5.item', 'userId')
    def addAsset(self, userId, gameId, assetKindId, count, eventId, intEventParam, param01='', param02='', **kwargs):
        '''
        添加资产
        '''
        try:
            userAssets = itemsys.itemSystem.loadUserAssets(userId)
            assetKind, addCount, final = userAssets.addAsset(gameId, assetKindId, count,
                                                             fttime.getCurrentTimestamp(),
                                                             eventId, intEventParam,
                                                             param01=param01,
                                                             param02=param02)
            if addCount > 0 and assetKind.keyForChangeNotify:
                pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, assetKind.keyForChangeNotify)
            return assetKind.kindId, addCount, final
        except:
            ftlog.error('hallitemrpc.addAsset gameId=', gameId,
                        'userId=', userId,
                        'assetKindId=', assetKindId,
                        'count=', count,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam)
            return 0, 0, 0

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def addAssets(self, userId, gameId, contentItems, eventId, intEventParam, **kwargs):
        '''
        添加一组资产
        '''
        try:
            contentItems = self._decodeContentItems(contentItems)
            assetList = self.sendContentItemList(gameId, userId, contentItems, 1, True, fttime.getCurrentTimestamp(),
                                                 eventId, intEventParam, **kwargs)
            return [(assetKind.kindId, addCount, final) for (assetKind, addCount, final) in assetList]
        except:
            ftlog.error()

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL, export=1)
    @lockargname('hall5.item', 'userId')
    def consumeAsset(self, userId, gameId, assetKindId, count, eventId, intEventParam):
        '''
        消费一个资产
        '''
        try:
            userAssets = itemsys.itemSystem.loadUserAssets(userId)
            assetKind, consumeCount, final = userAssets.consumeAsset(gameId, assetKindId, count,
                                                                     fttime.getCurrentTimestamp(), eventId, intEventParam)
            if consumeCount > 0 and assetKind.keyForChangeNotify:
                pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, assetKind.keyForChangeNotify)
            return assetKind.kindId, consumeCount, final
        except:
            ftlog.error('hallitemrpc.consumeAsset gameId=', gameId,
                        'userId=', userId,
                        'assetKindId=', assetKindId,
                        'count=', count,
                        'eventId=', eventId,
                        'intEventParam=', intEventParam)
            return 0, 0, 0

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.item', 'userId')
    def doActionByItemId(self, userId, gameId, itemId, actionName, timestamp, params, clientId=None):
        """
        执行一个道具的动作
        """
        if _DEBUG:
            debug('doActionByItemId IN', userId, gameId, itemId, actionName, timestamp, params, clientId)
        result = _action.doActionByItemId(userId, gameId, itemId, actionName, timestamp, params, clientId)
        if _DEBUG:
            debug('doActionByItemId OUT', userId, result)
        return result.toDict(_action._makeTodoTaskShowInfo)

    @typlugin.markPluginEntry(export=1)
    def doActionGdssCallBack(self, userId, record, result):
        from hall5.plugins.hallitem._private._actions.exchange import TYItemActionExchange
        return TYItemActionExchange.doActionGdssCallBack(userId, record, result)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.item', 'userId')
    def removeUserItem(self, userId, gameId, itemId, eventId, intEventParam):
        userBag = itemsys.itemSystem.loadUserAssets(userId).getUserBag()
        item = userBag.findItem(itemId)
        if not item:
            return -1, '道具不存在: %s' % itemId
        timestamp = fttime.getCurrentTimestamp()
        userBag.removeItem(gameId, item, timestamp, eventId, intEventParam)
        pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, 'item')
        return 0, ""

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.item', 'userId')
    def removeAllItem(self, userId, gameId, eventId, intEventParam=0):
        userBag = itemsys.itemSystem.loadUserAssets(userId).getUserBag()
        timestamp = fttime.getCurrentTimestamp()
        userBag._isSendToUser = False
        try:
            for item in userBag.getAllItem():
                userBag.removeItem(gameId, item, timestamp, eventId, intEventParam)
        finally:
            userBag._isSendToUser = True
        pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, 'item')
        return True

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.item', 'userId')
    def addAllItem(self, userId, gameId, eventId, intEventParam=0):
        userBag = itemsys.itemSystem.loadUserAssets(userId).getUserBag()
        timestamp = fttime.getCurrentTimestamp()
        userBag._isSendToUser = False
        try:
            for itemKind in itemsys.itemSystem.getAllItemKind():
                userBag.addItemUnitsByKind(gameId, itemKind, 1, timestamp, 0, eventId, intEventParam)
        finally:
            userBag._isSendToUser = True
        pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, 'item')
        return True

    @typlugin.markPluginEntry(export=1)
    def sendContent(self, gameId, userId, content, count, ignoreUnknown, timestamp, eventId, intEventParam, param01='', param02=''):
        return self.sendContentItemList(gameId, userId, content.getItems(), count, ignoreUnknown, timestamp, eventId,
                                        intEventParam, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1)
    @lockargname('hall5.item', 'userId')
    def sendContentItemList(self, gameId, userId, contentItemList, count, ignoreUnknown, timestamp, eventId, intEventParam, param01='', param02=''):
        assetList = []
        if contentItemList:
            userAssets = itemsys.itemSystem.loadUserAssets(userId)
            assetList = userAssets.sendContentItemList(gameId, contentItemList, count, ignoreUnknown, timestamp, eventId, intEventParam, param01=param01, param02=param02)
            changedDataNames = assetutils.getChangeDataNames(assetList)
            pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, changedDataNames)
        return assetList

    @typlugin.markPluginEntry(export=1)
    @lockargname('hall5.item', 'userId')
    def consumeContentItemList(self, gameId, userId, contentItemList, ignoreUnknown, timestamp, eventId, intEventParam):
        try:
            userAssets = itemsys.itemSystem.loadUserAssets(userId)
            assetList = userAssets.consumeContentItemList(gameId, contentItemList, ignoreUnknown,
                                                          timestamp, eventId, intEventParam)
            pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, assetutils.getChangeDataNames(assetList))
            return None, 0
        except TYAssetNotEnoughException, e:
            return e.assetKind.kindId, e.required - e.actually

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def rankSendReward(self, userId2Data, gameId, mail, eventId, intEventParam):
        """
        排行榜发奖
        """
        if not userId2Data:
            return 0

        def _longwork():
            for userId, data in userId2Data.iteritems():
                self._rankSendReward(int(userId), gameId, data, mail, eventId, intEventParam)
        ftcore.runOnce(_longwork)
        return 1

    @lockargname('hall5.item', 'userId')
    def _rankSendReward(self, userId, gameId, data, mail, eventId, intEventParam):
        assetList = self.addAssets(userId, gameId, data.get('content'), eventId, intEventParam)
        if mail:
            params = {
                'rank': data.get('rank'),
                'rewardContent': self.buildContentsString(assetList)
            }
            mail = ftstr.replaceParams(mail, params)
            pluginCross.hallmessage.sendMessageSystem(userId, gameId, mail)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.item', 'userId')
    def setItemExpires(self, userId, itemId, expiretime):
        userAssets = itemsys.itemSystem.loadUserAssets(userId)
        userBag = userAssets.getUserBag()
        item = userBag.findItem(itemId)
        if not item:
            return -1, '找不到道具'
        if not item.itemKind.units.isTiming():
            return -2, '该道具不是时间类型的'

        item.expiresTime = expiretime
        userBag.updateItem(item)
        pluginCross.halldatanotify.sendDataChangeNotify(userId, HALL_GAMEID, 'item')
        return 0, 'ok'

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.item', 'userId')
    def setItemCreateTime(self, userId, itemId, createTime):
        userAssets = itemsys.itemSystem.loadUserAssets(userId)
        userBag = userAssets.getUserBag()
        item = userBag.findItem(itemId)
        if not item:
            return -1, '找不到道具'

        item.createTime = createTime
        userBag.updateItem(item)
        pluginCross.halldatanotify.sendDataChangeNotify(userId, HALL_GAMEID, 'item')
        return 0, 'ok'

    @typlugin.markPluginEntry(export=1)
    def buildContentsString(self, assetList, needUnits=True):
        contents = []
        for asset in assetList:
            assetKind = itemsys.itemSystem.findAssetKind(asset[0])
            if assetKind:
                contents.append(assetKind.buildContent(asset[1], needUnits))
        return ','.join(contents)
