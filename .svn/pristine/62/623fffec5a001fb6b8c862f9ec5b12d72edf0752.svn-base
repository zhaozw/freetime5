# -*- coding=utf-8 -*-
"""
@file  : _store
@date  : 2016-12-01
@author: GongXiaobo
"""
from datetime import datetime
from sre_compile import isstring

from freetime5.util import ftlog
from freetime5.util import fttime
from tuyoo5.core import tyconfig
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.plugins.store.storeimpl import TYProductBuyType
from tuyoo5.plugins.store.storeimpl import TYStoreSystem


class TYChargeInfo(object):

    def __init__(self, chargeType, chargeMap, consumeMap):
        assert (chargeType is None or isstring(chargeType))
        assert (chargeMap is None or isinstance(chargeMap, dict))
        assert (consumeMap is None or isinstance(consumeMap, dict))
        if chargeMap:
            for k, v in consumeMap.iteritems():
                assert (isstring(k))
                assert (isinstance(v, (int, float)))
        if consumeMap:
            for k, v in consumeMap.iteritems():
                assert (isstring(k))
                assert (isinstance(v, (int, float)))
        self.chargeType = chargeType or ''
        self.chargeMap = chargeMap or {}
        self.consumeMap = consumeMap or {}

    def __repr__(self):
        return str(self.toDict())

    def __str__(self):
        return str(self.toDict())

    def __unicode__(self):
        return unicode(self.toDict())

    def getCharge(self, name, defValue):
        return self.chargeMap.get(name, defValue)

    def getConsume(self, name, defValue):
        return self.consumeMap.get(name, defValue)

    def toDict(self):
        return {'chargeType': self.chargeType, 'charges': self.consumeMap, 'consumes': self.consumeMap}


class TYOrder(object):
    STATE_CREATE = 0  # 初始状态
    STATE_DELIVERYING = 1  # 充值发货中
    STATE_DELIVERY = 2  # 充值发货完毕， 最终状态
    STATE_PAY_FAIL = 3  # 充值失败， 最终状态
    STATE_PAY_CANCEL = 4  # 充值取消， 最终状态

    def __init__(self, orderId=None, platformOrderId=None, userId=None,
                 gameId=None, realGameId=None, productId=None, count=None,
                 clientId=None, createTime=None, updateTime=None,
                 state=STATE_CREATE, errorCode=None, chargeInfo=None):
        # 订单ID
        self.orderId = orderId
        # 平台订单ID
        self.platformOrderId = platformOrderId
        # 用户ID
        self.userId = userId
        # 在哪个游戏中购买的
        self.gameId = gameId
        # 在哪个插件中购买的
        self.realGameId = realGameId
        # 购买商品的ID
        self.productId = productId
        # 购买的商品
        self.product = None
        # 数量
        self.count = count
        # 创建时间
        self.createTime = createTime
        # 最后更新时间
        self.updateTime = updateTime
        # 购买时的clientId
        self.clientId = clientId
        # 订单状态
        self.state = state
        # 发货失败时的错误信息
        self.errorCode = errorCode
        # 该订单的支付信息
        self.chargeInfo = chargeInfo


class TYOrderDeliveryResult(object):

    def __init__(self, order, assetItems, contents):
        # 订单信息
        self.order = order
        # 发了什么货物
        self.assetItems = assetItems
        self.contents = contents


class HallStoreSystem(TYStoreSystem):

    def __init__(self, orderDao):
        super(HallStoreSystem, self).__init__()
        self._orderDao = orderDao

    def makeGameOrderId(self):
        return self._orderDao.makeGameOrderId()

    def isOrderExits(self, orderId):
        return self._orderDao.isOrderExits(orderId)

    def buyProduct(self, gameId, realGameId, userId, clientId, orderId, productId, count):
        product = self.findProduct(productId)
        if not product:
            return None, '没有该商品'

        timestamp = fttime.getCurrentTimestamp()
        order = TYOrder(orderId,
                        '',
                        userId,
                        gameId,
                        realGameId,
                        productId,
                        count,
                        clientId,
                        timestamp,
                        timestamp,
                        TYOrder.STATE_CREATE,
                        0,
                        None)
        order.product = product
        self._orderDao.addOrder(order)
        ftlog.info('HallStoreSystem.buyProduct gameId=', gameId,
                   'realGameId=', realGameId,
                   'userId=', userId,
                   'clientId=', clientId,
                   'orderId=', orderId,
                   'productId=', productId,
                   'count=', count)
        return order, 'ok'

    def deliveryOrder(self, userId, realGameId, orderId, productId, chargeInfo, platformOrderId):
        '''
        给订单发货
        '''
        order = self._loadOrder(orderId)
        if not order:
            ftlog.error('HallStoreSystem.deliveryOrder userId=', userId,
                        'orderId=', orderId,
                        'productId=', productId,
                        'chargeInfo=', chargeInfo,
                        'err=', 'OrderNotFound')
            return None, '没有找到该订单'

        if order.userId != userId:
            ftlog.error('HallStoreSystem.deliveryOrder userId=', userId,
                        'orderId=', orderId,
                        'productId=', productId,
                        'chargeInfo=', chargeInfo,
                        'orderUserId=', order.userId,
                        'orderProductId=', order.productId,
                        'realGameId=', order.realGameId,
                        'err=', 'DiffUser')
            return None, '订单用户不匹配'

        if order.productId != productId:
            ftlog.error('HallStoreSystem.deliveryOrder userId=', userId,
                        'orderId=', orderId,
                        'productId=', productId,
                        'chargeInfo=', chargeInfo,
                        'orderUserId=', order.userId,
                        'orderProductId=', order.productId,
                        'realGameId=', order.realGameId,
                        'err=', 'DiffProductId')
            return None, '订单商品不匹配'

        if not order.product:
            ftlog.error('HallStoreSystem.deliveryOrder userId=', userId,
                        'orderId=', orderId,
                        'productId=', productId,
                        'chargeInfo=', chargeInfo,
                        'orderUserId=', order.userId,
                        'orderProductId=', order.productId,
                        'realGameId=', order.realGameId,
                        'err=', 'ProductNotFound')
            return None, '没有找到要发货的商品'

        if order.state != TYOrder.STATE_CREATE:
            ftlog.error('HallStoreSystem.deliveryOrder userId=', userId,
                        'orderId=', orderId,
                        'productId=', productId,
                        'chargeInfo=', chargeInfo,
                        'orderUserId=', order.userId,
                        'orderProductId=', order.productId,
                        'realGameId=', order.realGameId,
                        'state=', order.state,
                        'err=', 'BadState')
            return None, '订单状态错误'

        # 校验消耗的钻石和商品钻石的价格
        if order.product.buyType in (TYProductBuyType.BUY_TYPE_CONSUME,
                                     TYProductBuyType.BUY_TYPE_DIRECT):
            priceDiamond = order.product.priceDiamond * order.count
            consumeDiamond = chargeInfo.getConsume('coin', 0)
            if consumeDiamond < priceDiamond:
                ftlog.warn('HallStoreSystem.deliveryOrder userId=', userId,
                           'orderId=', orderId,
                           'productId=', productId,
                           'chargeInfo=', chargeInfo,
                           'orderUserId=', order.userId,
                           'orderProductId=', order.productId,
                           'state=', order.state,
                           'priceDiamond=', priceDiamond,
                           'consumeDiamond=', consumeDiamond,
                           'realGameId=', order.realGameId,
                           'err=', 'LessPriceDiamond')
                # raise TYStoreException(-1, '订单价格和商品价格不一致')

        curtime = fttime.getCurrentTimestamp()
        order.updateTime = curtime
        order.chargeInfo = chargeInfo
        order.state = TYOrder.STATE_DELIVERYING
        order.realGameId = realGameId
        if platformOrderId :
            order.platformOrderId = platformOrderId
        error, _oldState = self._orderDao.updateOrder(order, TYOrder.STATE_CREATE)
        if error:
            return None, '变更订单状态错误'

        assetList = pluginCross.hallitem.sendContent(order.realGameId, userId, order.product.content,
                                                     order.count, True, curtime,
                                                     'STORE_BUY_PRODUCT', tyconfig.productIdToNumber(order.productId), 
                                                     param01=order.platformOrderId, param02=order.orderId)
        assetList = [(assetKind.kindId, addCount, final) for (assetKind, addCount, final) in assetList]

        self._finishDelivery(order, 0)

        ftlog.info('HallStoreSystem.deliveryOrder',
                   'orderId=', order.orderId,
                   'platformOrderId=', order.platformOrderId,
                   'productId=', order.productId,
                   'userId=', order.userId,
                   'gameId=', order.gameId,
                   'count=', order.count,
                   'chargeInfo=', order.chargeInfo,
                   'assetList=', assetList)
        orderDeliveryResult = TYOrderDeliveryResult(order, assetList, None)
        return orderDeliveryResult, 'ok'

    def _loadOrder(self, orderId):
        order = self._orderDao.loadOrder(orderId)
        if order:
            order.product = self.findProduct(order.productId)
        return order

    def _finishDelivery(self, order, errorCode):
        order.errorCode = errorCode
        order.state = TYOrder.STATE_DELIVERY
        order.updateTime = fttime.getCurrentTimestamp()
        error, oldState = self._orderDao.updateOrder(order, TYOrder.STATE_DELIVERYING)
        if error != 0:
            ftlog.info('HallStoreSystem._finishDelivery orderId=', order.orderId,
                       'platformOrderId=', order.platformOrderId,
                       'userId=', order.userId,
                       'gameId=', order.gameId,
                       'productId', order.productId,
                       'count=', order.count,
                       'chargeInfo=', order.chargeInfo,
                       'errorCode=', order.errorCode,
                       'oldState=', oldState)
        else:
            ftlog.info('HallStoreSystem._finishDelivery orderId=', order.orderId,
                       'platformOrderId=', order.platformOrderId,
                       'userId=', order.userId,
                       'gameId=', order.gameId,
                       'productId', order.productId,
                       'count=', order.count,
                       'chargeInfo=', order.chargeInfo,
                       'errorCode=', order.errorCode)
        return error, oldState

    def finishOrder(self, orderId, userId, finishState):
        order = self._loadOrder(orderId)
        if not order:
            ftlog.error('HallStoreSystem.finishOrder userId=', userId,
                        'orderId=', orderId,
                        'err=', 'OrderNotFound')
            return '没有找到该订单'

        if order.userId != userId:
            ftlog.error('HallStoreSystem.finishOrder userId=', userId,
                        'orderId=', orderId,
                        'productId=', order.productId,
                        'chargeInfo=', order.chargeInfo,
                        'orderUserId=', order.userId,
                        'orderProductId=', order.productId,
                        'realGameId=', order.realGameId,
                        'err=', 'DiffUser')
            return '订单用户不匹配'

        if order.state == TYOrder.STATE_DELIVERY:
            # 有可能是直购金币的单子，已经投递完毕后的，再次砖石变化通知
            ftlog.info('HallStoreSystem.finishOrder orderId=', order.orderId,
                       'platformOrderId=', order.platformOrderId,
                       'userId=', order.userId,
                       'gameId=', order.gameId,
                       'productId', order.productId,
                       'count=', order.count,
                       'chargeInfo=', order.chargeInfo,
                       'errorCode=', order.errorCode,
                       'chip product already deliver ok')
            return 'ok'

        order.state = finishState
        order.updateTime = fttime.getCurrentTimestamp()
        error, oldState = self._orderDao.updateOrder(order, TYOrder.STATE_CREATE)
        if error != 0:
            ftlog.info('HallStoreSystem.finishOrder orderId=', order.orderId,
                       'platformOrderId=', order.platformOrderId,
                       'userId=', order.userId,
                       'gameId=', order.gameId,
                       'productId', order.productId,
                       'count=', order.count,
                       'chargeInfo=', order.chargeInfo,
                       'errorCode=', order.errorCode,
                       'oldState=', oldState)
            return '变更订单状态错误'
        else:
            ftlog.info('HallStoreSystem.finishOrder orderId=', order.orderId,
                       'platformOrderId=', order.platformOrderId,
                       'userId=', order.userId,
                       'gameId=', order.gameId,
                       'productId', order.productId,
                       'count=', order.count,
                       'chargeInfo=', order.chargeInfo,
                       'errorCode=', order.errorCode)
            return 'ok'

    def getUserOrderList(self, userId):
        orders = self._orderDao.getUserOrderList(userId)
        # 转换为列表
        historys = []
        for oid, datas in orders.iteritems():
            datas.append(oid)
            historys.append(datas)
        historys.sort(key=lambda x: x[0], reverse=True)
        for h in historys:
            # 更新时间、商品ID、商品名称、价格单位、价格、状态、订单号
            # 转换时间戳值字符串
            h[0] = fttime.formatTimeSecond(datetime.fromtimestamp(h[0]))
        return historys
