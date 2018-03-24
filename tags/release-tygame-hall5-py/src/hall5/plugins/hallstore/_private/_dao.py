# -*- coding=utf-8 -*-
"""
@file  : _dao
@date  : 2016-12-02
@author: GongXiaobo
"""

from freetime5.twisted import ftcore
from freetime5.twisted import ftlock
from freetime5.util import ftlog, fttime
from freetime5.util import ftstr
from hall5.plugins.hallstore._private._store import TYChargeInfo
from hall5.plugins.hallstore._private._store import TYOrder
from tuyoo5.core import tydao
from tuyoo5.core import tyglobal


class DaoGameOrder(tydao.DataSchemaHashAttrs):
    DBNAME = 'paydata'
    MAINKEY = 'gameOrder:%s'

    _LUA_UPDATE_STATE = '''
    local key = tostring(KEYS[1])
    local state = tonumber(KEYS[2])
    local expectState = tonumber(KEYS[3])
    local oldState = tonumber(redis.call('hget', key, 'state'))
    if oldState ~= expectState then
        return {1, oldState}
    end
    redis.call('hset', key, 'state', state)
    return {0, oldState}
    '''

    ATT_ORDERID = tydao.DataAttrStr('orderId', '', 256)
    ATT_PLATFORMORDERID = tydao.DataAttrStr('platformOrderId', '', 256)
    ATT_USERID = tydao.DataAttrInt('userId', 0)
    ATT_GAMEID = tydao.DataAttrInt('gameId', 0)
    ATT_REALGAMEID = tydao.DataAttrInt('realGameId', 0)
    ATT_PRODID = tydao.DataAttrStr('prodId', '', 256)
    ATT_COUNT = tydao.DataAttrInt('count', 0)
    ATT_CREATETIME = tydao.DataAttrInt('createTime', 0)
    ATT_UPDATETIME = tydao.DataAttrInt('updateTime', 0)
    ATT_CLIENTID = tydao.DataAttrStr('clientId', '', 256)
    ATT_STATE = tydao.DataAttrInt('state', 0)
    ATT_ERRORCODE = tydao.DataAttrInt('errorCode', 0)
    ATT_CHARGEINFO = tydao.DataAttrObjDict('chargeInfo', {}, 256)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY % mainKeyExt


class DaoUserOrderList(tydao.DataSchemaHashSameKeys):
    DBNAME = 'user'
    MAINKEY = 'orders:{}:%s'.format(tyglobal.gameId())
    SUBVALDEF = tydao.DataAttrObjList('order', [], 256)  # 实际目前长度只有30左右
    MAX_DATA_LENGTH = 32


class TYOrderDao(object):

    def getUserOrderList(self, userId):
        orders = DaoUserOrderList.HGETALL(userId)
        return orders

    @ftlock.lockargname('checkUserOrderListLimit', 'userId')
    def checkUserOrderListLimit(self, userId):
        dataLen = DaoUserOrderList.HLEN(userId)
        if dataLen <= DaoUserOrderList.MAX_DATA_LENGTH:
            return

        # 超过最大数量限制时，删除历史数据
        orderIds = DaoUserOrderList.HKEYS(userId)
        historys = []
        for orderId in orderIds:
            datas = DaoUserOrderList.HGET(userId, orderId)
            datas.append(orderId)
            historys.append(datas)

        # 按时间排序, 7天以上的或已完结的记录优先删除
        historys.sort(key=lambda x: x[0], reverse=True)
        ct = fttime.getCurrentTimestamp() - 7 * 24 * 60 * 60  # 7 天前的时间点
        for x in xrange(DaoUserOrderList.MAX_DATA_LENGTH, len(historys)):
            isTimeOut = historys[x][0] <= ct
            isFinished = historys[x][5] not in (TYOrder.STATE_CREATE, TYOrder.STATE_DELIVERYING)
            if isTimeOut or isFinished:
                orderId = historys[x][-1]
                order = DaoGameOrder.HGETALL(0, orderId)
                ftlog.info('AUTO CLEANUP STORE ORDER->', userId, orderId, ftstr.dumps(order))
                DaoUserOrderList.HDEL(userId, orderId)
                DaoGameOrder.DEL(0, orderId)

    def isOrderExits(self, orderId):
        return DaoGameOrder.EXISTS(0, orderId)

    def updateUserOrder(self, isAdd, order):
        '''
        记录用户的购买记录
        '''
        if order.product.diamondExchangeRate > 0:  # 砖石换金币的商品
            priceUnit = 1  # 单位：砖石
            price = order.product.priceDiamond * order.count
        else:
            priceUnit = 2  # 单位：人民币
            price = order.product.price * order.count

        if order.errorCode:
            state = -1
        else:
            state = order.state

        datas = [order.updateTime,
                 order.productId,
                 order.product.displayName,
                 priceUnit,
                 price,
                 state]
        DaoUserOrderList.HSET(order.userId, order.orderId, datas)

        if isAdd:
            # 延迟
            ftcore.runOnceDelay(0.1, self.checkUserOrderListLimit, order.userId)

    def addOrder(self,  order):
        '''
        增加order
        '''
        datas = {DaoGameOrder.ATT_ORDERID: order.orderId,
                 DaoGameOrder.ATT_PLATFORMORDERID: order.platformOrderId,
                 DaoGameOrder.ATT_USERID: order.userId,
                 DaoGameOrder.ATT_GAMEID: order.gameId,
                 DaoGameOrder.ATT_REALGAMEID: order.realGameId,
                 DaoGameOrder.ATT_PRODID: order.productId,
                 DaoGameOrder.ATT_COUNT: order.count,
                 DaoGameOrder.ATT_CLIENTID: order.clientId,
                 DaoGameOrder.ATT_CREATETIME: order.createTime,
                 DaoGameOrder.ATT_UPDATETIME: order.updateTime,
                 DaoGameOrder.ATT_STATE: order.state,
                 DaoGameOrder.ATT_ERRORCODE: order.errorCode,
                 DaoGameOrder.ATT_CHARGEINFO: self._encodeChargeInfo(order.chargeInfo)
                 }
        DaoGameOrder.HMSET(0, datas, order.orderId)
        # 更新用户购买记录
        self.updateUserOrder(1, order)

    def loadOrder(self, orderId):
        '''
        加载order
        '''
        datas = DaoGameOrder.HGETALL(0, orderId)
        if datas:
            return TYOrder(datas[DaoGameOrder.ATT_ORDERID],
                           datas[DaoGameOrder.ATT_PLATFORMORDERID],
                           datas[DaoGameOrder.ATT_USERID],
                           datas[DaoGameOrder.ATT_GAMEID],
                           datas[DaoGameOrder.ATT_REALGAMEID],
                           datas[DaoGameOrder.ATT_PRODID],
                           datas[DaoGameOrder.ATT_COUNT],
                           datas[DaoGameOrder.ATT_CLIENTID],
                           datas[DaoGameOrder.ATT_CREATETIME],
                           datas[DaoGameOrder.ATT_UPDATETIME],
                           datas[DaoGameOrder.ATT_STATE],
                           datas[DaoGameOrder.ATT_ERRORCODE],
                           self._decodeChargeInfo(datas[DaoGameOrder.ATT_CHARGEINFO])
                           )
        return None

    def updateOrder(self, order, expectState):
        '''
        更新order
        '''
        error, oldState = DaoGameOrder.EVALSHA(0, DaoGameOrder._LUA_UPDATE_STATE,
                                               [DaoGameOrder.getMainKey(0, order.orderId), order.state, expectState])
        if error != 0:
            return error, oldState

        datas = {
            DaoGameOrder.ATT_UPDATETIME: order.updateTime,
            DaoGameOrder.ATT_ERRORCODE: order.errorCode,
            DaoGameOrder.ATT_PRODID: order.productId,
            DaoGameOrder.ATT_REALGAMEID: order.realGameId,
            DaoGameOrder.ATT_CHARGEINFO: self._encodeChargeInfo(order.chargeInfo)
        }
        DaoGameOrder.HMSET(0, datas, order.orderId)
        # 更新用户购买记录
        self.updateUserOrder(0, order)
        return error, oldState

    def removeOrder(self, userId, orderId):
        DaoGameOrder.DEL(0, orderId)
        DaoUserOrderList.HDEL(userId, orderId)

    def _encodeChargeInfo(self, chargeInfo):
        if not chargeInfo:
            return {}
        d = {
            'chargeType': chargeInfo.chargeType,
            'charges': chargeInfo.chargeMap,
            'consumes': chargeInfo.consumeMap
        }
        return d

    def _decodeChargeInfo(self, chargeInfoDict):
        chargeType = chargeInfoDict.get('chargeType', '')
        charges = chargeInfoDict.get('charges', {})
        consumes = chargeInfoDict.get('consumes', {})
        return TYChargeInfo(chargeType, charges, consumes)
