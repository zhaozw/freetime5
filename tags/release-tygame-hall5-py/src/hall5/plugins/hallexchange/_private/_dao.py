# -*- coding=utf-8 -*-
"""
@file  : _exchange
@date  : 2016-12-12
@author: GongXiaobo
"""

from datetime import datetime

from freetime5.twisted import ftcore
from freetime5.twisted import ftlock
from freetime5.util import ftlog, ftcache
from freetime5.util import ftstr
from freetime5.util import fttime
from tuyoo5.core import tydao
from tuyoo5.core import tyglobal
from tuyoo5.core import tyrpchall
from tuyoo5.core.typlugin import pluginCross


class DaoExchangeId(tydao.DataSchemaString):
    DBNAME = 'mix'
    MAINKEY = 'global.exchangeId'

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY


class DaoExchangeCount(tydao.DataSchemaHashSameKeys):
    DBNAME = 'mix'
    MAINKEY = 'ex5.exchange.counts'
    SUBVALDEF = tydao.DataAttrInt('count', 0)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY


class DaoExchangeRecord(tydao.DataSchemaHashSameKeys):
    DBNAME = 'user'
    MAINKEY = 'ex5:{}:%s'.format(tyglobal.gameId())
    SUBVALDEF = tydao.DataAttrObjDict('record', {}, 256)
    MAX_DATA_LENGTH = 32


class DaoExchangeLed(tydao.DataSchemaList):
    MAINKEY = 'exchange5_led'
    DBNAME = 'mix'

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return DaoExchangeLed.MAINKEY


class TYExchangeRecord(object):
    STATE_NORMAL = 0                            # 初始状态
    STATE_GDSS_AUDIT = 100                      # 中间状态: GDSS接收兑换请求成功
    STATE_GDSS_AUDIT_ERROR_FAIL = 101           # 最终状态: GDSS接收兑换请求失败
    STATE_GDSS_AUDIT_ACCEPT = 102               # 中间状态: GDSS审核通过
    STATE_GDSS_AUDIT_REJECT_FAIL = 103          # 最终状态: GDSS拒绝发货不返还道具
    STATE_GDSS_AUDIT_REJECT_RETURN_FAIL = 104   # 最终状态: GDSS拒绝发货返还道具
    STATE_GDSS_SHIPPING_SUCC_FAIL = 105         # 最终状态: GDSS发货成功
    STATE_GDSS_SHIPPING_ERR_FAIL = 106          # 最终状态: GDSS发货失败不返还道具
    STATE_GDSS_SHIPPING_ERR_FAIL_RETURN = 107   # 最终状态: GDSS发货失败返还道具
    STATE_CHIP_SHIPPING_SUCC_FAIL = 200         # 最终状态: 兑换金币成功
    STATE_CHIP_SHIPPING_ERROR = 201             # 最终状态: 兑换金币失败

    def __init__(self, exchangeId):
        self.exchangeId = exchangeId  # 途游兑换订单号
        self.extOrderId = ''  # 京东订单号
        self.extCardId = ''  # 京东卡卡号
        self.extCardPwd = ''  # 京东卡卡密
        self.createTime = None
        self.state = TYExchangeRecord.STATE_NORMAL
        self.params = None

    def toDict(self):
        data = {
            'st': self.state,
            'ct': self.createTime,
            'params': self.params,
        }
        if self.extOrderId:
            data['ext'] = self.extOrderId
        if self.extCardId:
            data['cid'] = self.extCardId
        if self.extCardPwd:
            data['cpw'] = self.extCardPwd
        return data

    def fromDict(self, d):
        self.state = d['st']
        self.createTime = d['ct']
        self.extOrderId = d.get('ext', '')
        self.extCardId = d.get('cid', '')
        self.extCardPwd = d.get('cpw', '')
        self.params = d['params']
        return self


def makeExchangeId():
    exchangeId = DaoExchangeId.INCRBY(0, 1)
    exchangeId = 'EO%s%s' % (datetime.now().strftime('%Y%m%d%H%M%S'), exchangeId)
    return exchangeId


def creatExchangeRecord(userId, params):
    exchangeId = makeExchangeId()
    record = TYExchangeRecord(exchangeId)
    record.createTime = fttime.getCurrentTimestamp()
    record.params = params
    record.state = TYExchangeRecord.STATE_NORMAL
    DaoExchangeRecord.HSET(userId, exchangeId, record.toDict())
    ftcore.runOnceDelay(0.1, _checkUserExchangeListLimit, userId, params)
    return exchangeId


@ftlock.lockargname('_checkUserExchangeListLimit', 'userId')
def _checkUserExchangeListLimit(userId, params):

    # 添加至兑换的LED列表
    pushLedItem(userId, params)

    dataLen = DaoExchangeRecord.HLEN(userId)
    if dataLen <= DaoExchangeRecord.MAX_DATA_LENGTH:
        return

    # 超过最大数量限制时，删除历史数据
    orderIds = DaoExchangeRecord.HKEYS(userId)

    # 按时间排序
    orderIds.sort(reverse=True)
    for x in xrange(DaoExchangeRecord.MAX_DATA_LENGTH, len(orderIds)):
        orderId = orderIds[x]
        order = DaoExchangeRecord.HGET(userId, orderId)
        ftlog.info('AUTO CLEANUP EXCHANGE ORDER->', userId, orderId, ftstr.dumps(order))
        DaoExchangeRecord.HDEL(userId, orderId)


def pushLedItem(userId, params):
    ct = fttime.formatTimeSecond()
    displayName = params['displayName']
    userName = pluginCross.halldata.getUserDataList(userId, tyrpchall.UserKeys.ATT_NAME)
    led = [ct, userName,  displayName]
    DaoExchangeLed.LPUSH(0, ftstr.dumps(led))  # 加入数据


def trimLedItem():
    DaoExchangeLed.LTRIM(0, 0, 9)  # 保留最近的10条


def loadLedList():
    return _loadLedList('hall5.exchange5.led')


@ftcache.lfu_alive_cache(maxsize=2, cache_key_args_index=0, alive_second=30)
def _loadLedList(cacheKey):
    datas = DaoExchangeLed.LRANGE(0, 0, 9)  # 保留最近的10条
    if datas:
        for x in xrange(len(datas)):
            d = ftstr.loads(datas[x], ignoreException=True)
            if d:
                datas[x] = d
        return datas
    else:
        return [
            [fttime.formatTimeSecond(), '榜爷', '10元话费卡'],
            [fttime.formatTimeSecond(), '虎妞', '红烧康师傅方便面']
        ]


def loadRecord(userId, exchangeId):
    data = DaoExchangeRecord.HGET(userId, exchangeId)
    if data:
        record = TYExchangeRecord(exchangeId)
        return record.fromDict(data)
    return None


def updateRecord(userId, record):
    return DaoExchangeRecord.HSET(userId, record.exchangeId, record.toDict())


def getReordKeys(userId):
    return DaoExchangeRecord.HKEYS(userId)


def incrItemExchangeCount(itemId):
    return DaoExchangeCount.HINCRBY(0, itemId, 1)


def resetItemExchangeCount(itemId, count):
    return DaoExchangeCount.HSET(0, itemId, count)


def getItemExchangeCount(itemId):
    return DaoExchangeCount.HGET(0, itemId)


def removeExchange(userId, exchangeId):
    DaoExchangeRecord.HDEL(userId, exchangeId)
