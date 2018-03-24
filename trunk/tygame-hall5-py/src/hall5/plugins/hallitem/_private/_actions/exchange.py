# -*- coding=utf-8 -*-
"""
@file  : itemaction
@date  : 2016-09-22
@author: GongXiaobo
"""

from freetime5.util import ftlog, fttime
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallconf
from hall5.plugins.hallitem._private._actions import _action
from hall5.plugins.hallitem._private._items.exchange import TYExchangeItem
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.plugins.item import items
from tuyoo5.plugins.item.itemexceptions import TYItemConfException


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class TYItemActionExchangeResult(items.TYItemActionResult):
    def __init__(self, action, item, message, exchangeId):
        super(TYItemActionExchangeResult, self).__init__(action, item, 0, message)
        self.exchangeId = exchangeId


class TYItemActionExchange(_action.HallItemAction):

    TYPE_ID = 'common.exchange'
    SINGLE_MODE_NAME_TYPE_LIST = []

    def __init__(self):
        super(TYItemActionExchange, self).__init__()
        self.auditParams = None

    def _decodeFromDictImpl(self, d):
        self.auditParams = d.get('auditParams', {})
        if not isinstance(self.auditParams, dict):
            raise TYItemConfException(d, 'TYItemActionExchange.auditParams must be dict')

    def isWechatRedPack(self):
        return self.auditParams.get("type") == 5

    def isJdActualProduct(self):
        return self.auditParams.get("type") == 6

    def getInputParams(self, gameId, userBag, item, timestamp):
        # 目前配置系统设计有问题,不能灵活配置InputParams的类型
        # 被迫在此黑掉配置……
        if self.isWechatRedPack():  # 微信红包,不让前端弹框输入手机号
            return {}
        if self.isJdActualProduct():  # 京东实物兑换,需要输入详细地址信息
            return {'type': 'jdActualProduct'}
        return super(TYItemActionExchange, self).getInputParams(gameId, userBag, item, timestamp)

    def checkParams(self, gameId, userId, timestamp, params):
        ftlog.info('exchange.checkParams->', params)
        if self.isWechatRedPack():  # 微信红包,无需手机号
            return items.ACT_RESULT_OK
        useBindPhone = params.get('bindPhone', 0)
        if not useBindPhone:
            # 如果没有bindPhone，则需要检查phoneNumber
            phoneNumber = params.get('phoneNumber')
            if not phoneNumber:
                return items.TYItemActionResult(None, None, -10, '请输入手机号码', None)
        return items.ACT_RESULT_OK

    def getParamNameTypeList(self):
        return self.SINGLE_MODE_NAME_TYPE_LIST

    def canDo(self, gameId, clientId, userBag, item, timestamp):
        return not item.isDied(timestamp) and item.state == TYExchangeItem.STATE_NORMAL

    def doAction(self, gameId, clientId, userAssets, item, timestamp, params):
        assert (isinstance(item, TYExchangeItem))
        if item.isDied(timestamp):
            if item.itemKind.units.isTiming():
                return items.TYItemActionResult(None, None, -30, '道具已经过期', None)
            else:
                return items.TYItemActionResult(None, None, -31, '道具数量不足', None)

        if item.state != TYExchangeItem.STATE_NORMAL:
            return items.TYItemActionResult(None, None, -32, '道具审核中', None)

        wechat_red_pack = self.isWechatRedPack()  # 微信红包，无需手机号、地址
        msg = MsgPack()
        msg.setKey('apiVersion', 5.0)
        msg.setCmdAction('exchange5', 'exchange')
        msg.updateParam(self.auditParams)
        msg.setParam('phone', str(params.get('phoneNumber') if not wechat_red_pack else '11111111111'))
        msg.setParam('uName', params.get('uName', ''))
        msg.setParam('bindPhone', params.get('bindPhone', ''))
        msg.setParam('phoneNumber', params.get('phoneNumber', ''))
        msg.setParam('uAddres', params.get('uAddres', ''))
        msg.setParam('gameId', gameId)
        msg.setParam('itemId', item.itemId)
        msg.setParam('userId', userAssets.userId)
        msg.setParam('extabName', '_item_')
        msg.setParam('clientId', clientId)
        msg.setParam('wxappid', hallconf.getWeiXinAppId(userAssets.userId, clientId))
        msg.setParam('proviceId', params.get('proviceId', ''))
        msg.setParam('cityId', params.get('cityId', ''))
        msg.setParam('countyId', params.get('countyId', ''))
        msg.setParam('townId', params.get('townId', ''))
        msg.setParam('proviceName', params.get('proviceName', ''))
        msg.setParam('cityName', params.get('cityName', ''))
        msg.setParam('countyName', params.get('countyName', ''))
        msg.setParam('townName', params.get('townName', ''))

        ftlog.info('TYItemActionExchange->doAction', msg)
        exchangeId, errMsg = pluginCross.hallexchange.doExchangeRequest(userAssets.userId, msg)
        if not exchangeId or errMsg:
            return items.TYItemActionResult(None, None, -33, errMsg, None)

        # 兑换开始，成功，转换道具状态
        item.state = TYExchangeItem.STATE_AUDIT
        item.original = 0
        userAssets.getUserBag().updateItem(item, timestamp)

        replaceParams = {'item': item.itemKind.displayName}
        _mail, message, _changed = _action._handleMailAndMessageAndChanged(gameId,
                                                                           userAssets,
                                                                           self,
                                                                           None,
                                                                           replaceParams)
        # TGHall.getEventBus().publishEventent(TYItemExchangeEvent(gameId, userAssets.userId, item))
        return TYItemActionExchangeResult(self, item, message, exchangeId)

    @staticmethod
    def doActionGdssCallBack(userId, record, result):
        if _DEBUG:
            debug('doActionGdssCallBack->', userId, record, result, record.params)

        from tuyoo5.plugins.item import itemsys
        userAssets = itemsys.itemSystem.loadUserAssets(userId)
        if not userAssets:
            return -1, 'ExchangeItem userAssets error, userId=%s' % (userId)
        userBag = userAssets.getUserBag()
        if not userBag:
            return -2,  'ExchangeItem userBag error, userId=%s' % (userId)
        item = userBag.findItem(int(record.params['itemId']))
        if not item:
            return -3, 'ExchangeItem userItem error, userId=%s' % (userId)

        timestamp = fttime.getCurrentTimestamp()
        if item.state == TYExchangeItem.STATE_AUDIT:
            if result == 1:  # 审核被拒绝，无需返还奖券
                userBag.removeItem(HALL_GAMEID, item, timestamp, 'EXCHANGE5_REDUCE_ITEM', item.kindId)
            elif result == 2:  # 审核被拒绝，需要返还奖券
                item.state = TYExchangeItem.STATE_NORMAL
                userBag.updateItem(item, timestamp)
            elif result == 3:  # 审核通过，等待发货
                item.state = TYExchangeItem.STATE_SHIPPING
                userBag.updateItem(item, timestamp)
            else:
                return -4, 'ExchangeItem.state ErrorAudit state=%s result=%s' % (item.state, result)
        elif item.state == TYExchangeItem.STATE_SHIPPING:
            if result == 0:  # 发货成功
                userBag.removeItem(HALL_GAMEID, item, timestamp, 'EXCHANGE5_REDUCE_ITEM', item.kindId)
            elif result == 4:   # 发货失败，无需返回奖券
                userBag.removeItem(HALL_GAMEID, item, timestamp, 'EXCHANGE5_REDUCE_ITEM', item.kindId)
            elif result == 5:  # 发货失败，需要返回奖券
                item.state = TYExchangeItem.STATE_NORMAL
                userBag.updateItem(item, timestamp)
            else:
                return -5, 'ExchangeItem.state ErrorAccept state=%s result=%s' % (item.state, result)
        else:
            return -6, 'ExchangeItem.state Error state=%s result=%s' % (item.state, result)
        return 0, 'ok'
