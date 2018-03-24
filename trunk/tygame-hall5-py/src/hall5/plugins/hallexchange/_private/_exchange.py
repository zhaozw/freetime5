# -*- coding=utf-8 -*-
"""
@file  : _exchange
@date  : 2016-12-12
@author: GongXiaobo
"""

from freetime5.twisted import ftcore
from freetime5.twisted.ftlock import lockargname
from freetime5.util import ftlog
from freetime5.util import ftstr
from hall5.plugins.hallexchange._private import _conf, _counts
from hall5.plugins.hallexchange._private import _dao
from tuyoo5.core import tyglobal
from tuyoo5.core import tyrpcgdss
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import ChipNotEnoughOpMode


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass
# GDSS 兑换类型表：
# type = 0 手机充值卡 count 单位：RMB，为充值的金额
# type = 1 手工实物兑换（例如：神秘手机、老的京东卡道具）
# type = 2 比赛等线下邀请函、门票等、比赛资格手工处理（例如：TUPT决赛资格）
# type = 3 京东卡（例如：30元京东卡）count 单位：RMB，为京东卡的面值
# type = 5 微信红包（例如：1元微信红包）
# type = 6 京东实物兑换（例如：京东5KG大米）
# type = 99 奖券换金币

_ERR_MSG_ITEM_NOT_FOUND = '此商品已经下架，请选择其他商品进行兑换'
_ERR_MSG_NOT_ENOUGHT_COUPON = '奖券数量不足以兑换此商品'
_ERR_MSG_EX_CHIP_ADD = '金币兑换失败'


def check_tabName(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_pageNum(msg, result, name):
    val = msg.getParamInt(name, 0)
    return val, None


def check_proviceId(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_cityId(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_countyId(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_townId(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_proviceName(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_cityName(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_countyName(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_townName(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_exchangeId(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_result(msg, result, name):
    val = msg.getParamInt(name, -1)
    return val, None


def check_extOrderId(msg, result, name):
    val = msg.getParamStr(name, '')
    if not val:
        val = msg.getParamStr('jdOrderId', '')
    return val, None


def check_extCardId(msg, result, name):
    val = msg.getParamStr(name, '')
    if not val:
        val = msg.getParamStr('jdCardNo', '')
    return val, None


def check_extCardPwd(msg, result, name):
    val = msg.getParamStr(name, '')
    if not val:
        val = msg.getParamStr('jdCardPwd', '')
    return val, None


def check_itemId(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_extabName(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_phone(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) < 11:
        val = msg.getParamStr('bindPhone', '')
        if len(val) < 11:
            val = msg.getParamStr('phoneNumber', '')
            if len(val) < 11:
                return None, 'the param %s error' % (name)
    return val, None


def check_uName(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) <= 0:
        if not msg.getParamStr('wxappid'):  # 微信红包兑换，无需名字
            return None, 'the param %s error' % (name)
    return val, None


def check_uAddres(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_wxappid(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check__relation_(msg, result, name):
    if result.extabName == '_item_':  # 道具列表中发起的兑换操作
        from tuyoo5.plugins.item import itemsys
        userAssets = itemsys.itemSystem.loadUserAssets(result.userId)
        if not userAssets:
            return None, '用户ID资产错误'
        userBag = userAssets.getUserBag()
        if not userBag:
            return None,  '用户ID背包错误'
        item = userBag.findItem(int(result.itemId))
        if not item:
            return None,  '不能识别的道具ID'
        result._add_('displayName', item.itemKind.displayName)
        result._add_('coupon', 1)
        result._add_('count', 1 if msg.getParamInt('count', 1) <= 0 else msg.getParamInt('count', 1))
        result._add_('type', msg.getParamInt('type', -1))
        result._add_('itemKindId', item.itemKind.kindId)
        result._add_('jd_product_id', msg.getParamStr('jdProductId', ''))
    else:
        itemInfo = _conf.getItemInfo(result.extabName, result.itemId)
        if not itemInfo:
            return None, _ERR_MSG_ITEM_NOT_FOUND

        result._add_('displayName', itemInfo['title'])
        result._add_('coupon', itemInfo['price'])
        result._add_('count', itemInfo['count'])

    if not result.displayName:
        return None, 'the param displayName error'

    if result.coupon <= 0:
        return None, 'the param coupon error'

    if result.count <= 0:
        return None, 'the param count error'

    if result.extabName == '_item_':  # 道具列表中发起的兑换操作
        pass
    elif result.extabName == 'chip':  # 奖券换金币
        result._add_('type', 99)
        result._add_('itemKindId', 'chip')
        result._add_('jd_product_id', '')
    elif result.extabName == 'czcard':  # 奖券换充值卡
        result._add_('type', 0)
        result._add_('itemKindId', 'czcard')
        result._add_('jd_product_id', '')
    elif result.extabName == 'jdcard':  # 奖券换京东卡
        result._add_('type', 3)
        result._add_('itemKindId', 'jdcard')
        result._add_('jd_product_id', '')
    else:  # rice electric supplies 京东实物兑换
        result._add_('type', 6)
        result._add_('itemKindId', 'jindong')
        result._add_('jd_product_id', result.itemId.split(':')[-1])

    if result.type == 99:  # 兑换金币
        pass
    elif result.type == 0:  # 奖券换充值卡
        pass
    elif result.type == 1:  # 手工实物兑换， 
        pass
    elif result.type == 2:  # 比赛等线下邀请函、门票等
        pass
    elif result.type == 3:  # 奖券换京东卡
        pass
    elif result.type == 4:  # 未使用
        pass
    elif result.type == 5:  # 微信红包
        if len(result.wxappid) <= 0:
            return None, 'the param wxappid error'
    elif result.type == 6:  # 京东实物兑换
        if len(result.jd_product_id) <= 0:
            return None, 'the param jd_product_id error'
        if len(result.proviceId) <= 0:
            return None, 'the param proviceId error'
        if len(result.cityId) <= 0:
            return None, 'the param cityId error'
        if len(result.countyId) <= 0:
            return None, 'the param countyId error'
        if len(result.proviceName) <= 0:
            return None, 'the param proviceName error'
        if len(result.cityName) <= 0:
            return None, 'the param cityName error'
        if len(result.countyName) <= 0:
            return None, 'the param countyName error'
        # if len(result.townId) <= 0: # 可能没有4级地址
        #    return None, 'the param townId error'
        if len(result.uAddres) <= 0:
            return None, 'the param uAddres error'
    else:
        return None, 'the params type error'
    return 1, None


@lockargname('hall5.exchange', 'userId')
def doExchangeRequest(userId, mi):
    if _DEBUG:
        debug('doExchangeRequest IN userId=', userId, 'mi=', mi)

    exchangeId, errMsg = _doExchangeBegin(userId, mi)  # 开始兑换，建立单子、扣除钻石
    if exchangeId:
        if mi.extabName == '_item_':  # 道具列表兑换入口
            errMsg, state = _doExchangeRequestGdss(userId, exchangeId, mi)
        elif mi.extabName == 'chip':  # 奖券换金币
            errMsg, state = _doExchangeCoupon2Chip(userId, exchangeId, mi)
        elif mi.extabName == 'czcard':  # 奖券换充值卡
            errMsg, state = _doExchangeRequestGdss(userId, exchangeId, mi)
        elif mi.extabName == 'jdcard':  # 奖券换京东卡
            errMsg, state = _doExchangeRequestGdss(userId, exchangeId, mi)
        else:  # rice electric supplies 京东实物兑换
            errMsg, state = _doExchangeRequestGdss(userId, exchangeId, mi)
        # 提交订单状态
        _doExchangeCommit(userId, exchangeId, mi, errMsg, state)

    if _DEBUG:
        debug('doExchangeRequest OUT userId=', userId, 'exchangeId=', exchangeId, 'errMsg=', errMsg)
    return exchangeId, errMsg


def _doExchangeBegin(userId, mi):

    if mi.extabName == '_item_':  # 道具列表兑换入口, 由道具的action进行扣除或标记处理
        trueDelta, finalCount = -mi.coupon, 0
        product_id = mi.itemKindId
    else:
        product_id = _conf.PRODUCT_MAP[mi.itemId]
        trueDelta, finalCount = pluginCross.halldata.incrCoupon(userId,
                                                                mi.gameId,
                                                                -mi.coupon,
                                                                ChipNotEnoughOpMode.NOOP,
                                                                'EXCHANGE5_REDUCE_COUPON',
                                                                product_id)
    if _DEBUG:
        debug('_doExchangeBegin tabName=', mi.extabName, 'userId=', userId,
              'couponIncr=', -mi.coupon, 'couponDelta=', trueDelta,
              'couponFinal=', finalCount)

    if trueDelta != -mi.coupon:
        # 奖券扣除失败
        errMsg = _ERR_MSG_NOT_ENOUGHT_COUPON
        exchangeId = ''
    else:
        errMsg = None
        datas = {
            'userId': mi.userId,
            'gameId': mi.gameId,
            'clientId': mi.clientId,
            'extabName': mi.extabName,
            'itemId': mi.itemId,
            'itemKindId': mi.itemKindId,
            'phone': mi.phone,
            'uName': mi.uName,
            'displayName': mi.displayName,
            'coupon': mi.coupon,
            'count': mi.count,
            'type': mi.type,
            'jdProductId': mi.jd_product_id,
            'jdAddres': [mi.proviceName, mi.cityName, mi.countyName, mi.townName, mi.uAddres],
            'productId': product_id
        }
        exchangeId = _dao.creatExchangeRecord(userId, datas)

    return exchangeId, errMsg


def _doExchangeCommit(userId, exchangeId, mi, errMsg, state):
    if errMsg:
        # 有错误发生，回滚奖券数量
        if mi.extabName == '_item_':  # 道具列表兑换入口, 由道具的action进行处理回退处理
            trueDelta, finalCount = -mi.coupon, 0
        else:
            product_id = _conf.PRODUCT_MAP[mi.itemId]
            trueDelta, finalCount = pluginCross.halldata.incrCoupon(userId, mi.gameId, mi.coupon,
                                                                    ChipNotEnoughOpMode.NOOP,
                                                                    'EXCHANGE5_ROLLBACK_COUPON',
                                                                    product_id)
        if _DEBUG:
            debug('_doExchangeCommit rollback coupon userId=', userId,
                  'couponIncr=', -mi.coupon, 'ouponDelta=', trueDelta,
                  'ouponFinal=', finalCount)
    # 更新订单状态
    record = _dao.loadRecord(userId, exchangeId)
    record.state = state
    _dao.updateRecord(userId, record)

    # 记录兑换个数
    ftcore.runOnceDelay(1, _counts.incrItemExchangeCount, mi.itemId)

    if _DEBUG:
        debug('_doExchangeCommit commit coupon userId=', userId,
              'exchangeId=', exchangeId, 'state=', state)


def _doExchangeCoupon2Chip(userId, exchangeId, mi):
    # 奖券扣除成功，添加金币
    product_id = _conf.PRODUCT_MAP[mi.itemId]
    trueDelta, finalCount = pluginCross.halldata.incrChip(userId, mi.gameId, mi.count,
                                                          ChipNotEnoughOpMode.NOOP,
                                                          'EXCHANGE5_COUPON_TO_CHIP',
                                                          product_id)
    if _DEBUG:
        debug('_doExchangeCoupon2Chip userId=', userId, 'exchangeId=', exchangeId,
              'chipIncr=', mi.count, 'chipDelta=', trueDelta,
              'chipFinal=', finalCount)

    if trueDelta == mi.count:
        state = _dao.TYExchangeRecord.STATE_CHIP_SHIPPING_SUCC_FAIL
        errMsg = ''
    else:
        # 金币添加失败
        state = _dao.TYExchangeRecord.STATE_CHIP_SHIPPING_ERROR
        errMsg = _ERR_MSG_EX_CHIP_ADD

    if _DEBUG:
        debug('_doExchangeCoupon2Chip userId=', userId, 'exchangeId=', exchangeId,
              'state=', state, 'errMsg=', errMsg)
    return errMsg, state


def _doExchangeRequestGdss(userId, exchangeId, mi):
    if _DEBUG:
        debug('_doExchangeRequestGdss IN', userId, mi)

    parasDict = {}
    parasDict['callbackAudit'] = tyglobal.httpGame() + '/api/hall5/exchange/auditCallback'
    parasDict['callbackShipping'] = tyglobal.httpGame() + '/api/hall5/exchange/shippingCallback'
    parasDict['user_id'] = userId
    parasDict['exchange_id'] = exchangeId
    parasDict['prod_id'] = mi.itemId
    parasDict['prod_num'] = 1
    parasDict['prod_kind_name'] = mi.displayName
    parasDict['exchange_type'] = mi.type
    parasDict['exchange_amount'] = mi.count
    parasDict['exchange_desc'] = ''
    parasDict['user_phone'] = mi.phone
    parasDict['user_name'] = mi.uName
    parasDict['user_addres'] = mi.uAddres
    # 微信红包需要
    parasDict['wxappid'] = mi.wxappid
    # 京东实物兑换需要
    parasDict['jd_product_id'] = mi.jd_product_id
    parasDict['user_province'] = mi.proviceId
    parasDict['user_city'] = mi.cityId
    parasDict['user_district'] = mi.countyId
    parasDict['user_town'] = mi.townId

    res = tyrpcgdss.itemExchange(parasDict)
    retcode = res.get('retcode', -1)

    if retcode != 1:
        state = _dao.TYExchangeRecord.STATE_GDSS_AUDIT_ERROR_FAIL
        errMsg = '兑换请求出错(' + res.get('retmsg', '') + ')'
    else:
        state = _dao.TYExchangeRecord.STATE_GDSS_AUDIT
        errMsg = None

    if _DEBUG:
        debug('_doExchangeRequestGdss userId=', userId, 'exchangeId=', exchangeId,
              'parasDict=', ftstr.dumps(parasDict), 'response=', ftstr.dumps(res),
              'state=', state, 'errMsg=', errMsg)
    return errMsg, state


@lockargname('hall5.exchange', 'userId')
def doExchangeGdssCallBack(userId, exchangeId, result, extOrderId, extCardId, extCardPwd):
    """
    处理审核结果
    RESULT_OK = 0  # 发货成功
    RESULT_REJECT = 1  # 审核失败不返还道具
    RESULT_REJECT_RETURN = 2  # 审核失败返还道具
    RESULT_AUDITSUCC = 3  # 审核成功
    RESULT_SHIPPINGFAIL = 4  # 发货失败不返还道具
    RESULT_SHIPPINGFAIL_RETURN = 5  # 发货失败返还道具
    RESULT_UPDATE_INFO = 6  # 更新信息，例如补充extOrderId等
    """
    if _DEBUG:
        debug('doExchangeGdssCallBack IN userId=', userId, 'exchangeId=', exchangeId, 'result=', result)

    ret = 'UnKnow Error'
    state = -1
    needReturn = 0
    record = _dao.loadRecord(userId, exchangeId)
    if record:
        if _DEBUG:
            debug('doExchangeGdssCallBack IN userId=', userId, 'exchangeId=', exchangeId, 'record.state=', record.state)

        if result == 6:
            if extOrderId or extCardId or extCardPwd:  # 更新信息，例如补充extOrderId等
                if extOrderId:
                    record.extOrderId = extOrderId
                if extCardId:
                    record.extCardId = extCardId
                if extCardPwd:
                    record.extCardPwd = extCardPwd
                _dao.updateRecord(userId, record)
            if _DEBUG:
                debug('doExchangeGdssCallBack OUT userId=', userId, 'exchangeId=', exchangeId,
                      'result=', result, 'RESULT_UPDATE_INFO', extOrderId, extCardId, extCardPwd)
            return 'ok'

        if record.state == _dao.TYExchangeRecord.STATE_GDSS_AUDIT:
            if result == 1:  # 审核被拒绝，无需返还奖券
                state = _dao.TYExchangeRecord.STATE_GDSS_AUDIT_REJECT_FAIL
            elif result == 2:  # 审核被拒绝，需要返还奖券
                needReturn = 1
                state = _dao.TYExchangeRecord.STATE_GDSS_AUDIT_REJECT_RETURN_FAIL
            elif result == 3:  # 审核通过，等待发货
                state = _dao.TYExchangeRecord.STATE_GDSS_AUDIT_ACCEPT
            else:
                ret = 'ExchangeRecord.state ErrorAudit state=%s result=%s' % (record.state, result)
        elif record.state == _dao.TYExchangeRecord.STATE_GDSS_AUDIT_ACCEPT:
            if result == 0:  # 发货成功
                state = _dao.TYExchangeRecord.STATE_GDSS_SHIPPING_SUCC_FAIL
            elif result == 4:  # 发货失败，无需返回奖券
                state = _dao.TYExchangeRecord.STATE_GDSS_SHIPPING_ERR_FAIL
            elif result == 5:  # 发货失败，需要返回奖券
                needReturn = 1
                state = _dao.TYExchangeRecord.STATE_GDSS_SHIPPING_ERR_FAIL_RETURN
            else:
                ret = 'ExchangeRecord.state ErrorAccept state=%s result=%s' % (record.state, result)
        else:
            ret = 'ExchangeRecord.state Error state=%s result=%s' % (record.state, result)
    else:
        ret = 'UnKnow exchangeId'

    if record and record.params['extabName'] == '_item_':  # 道具列表兑换入口, 由道具的action进行扣除或标记处理
        needReturn = 0
        code, error = pluginCross.hallitem.doActionGdssCallBack(userId, record, result)
        if _DEBUG:
            debug('doExchangeGdssCallBack _item_ userId=', userId, 'code=', code, 'error=', error)
        if code != 0:
            return error

    if state > 0:
        ret = 'ok'
        # 设置了正常状态
        record.state = state
        if extOrderId :
            record.extOrderId = extOrderId
        if extCardId :
            record.extCardId = extCardId
        if extCardPwd :
            record.extCardPwd = extCardPwd
        _dao.updateRecord(userId, record)
        # 需要返还奖券
        if needReturn:
            gameId = record.params['gameId']
            deltaCount = record.params['coupon']

            if isinstance(record.params['itemKindId'], (int, long)):
                product_id = record.params['itemKindId']
            else:
                product_id = _conf.PRODUCT_MAP[record.params['itemId']]

            trueDelta, finalCount = pluginCross.halldata.incrCoupon(userId,
                                                                    gameId,
                                                                    deltaCount,
                                                                    ChipNotEnoughOpMode.NOOP,
                                                                    'EXCHANGE5_ROLLBACK_COUPON',
                                                                    product_id)
            if _DEBUG:
                debug('doExchangeGdssCallBack rollback coupon userId=', userId,
                      'couponIncr=', deltaCount, 'ouponDelta=', trueDelta,
                      'ouponFinal=', finalCount)
    if _DEBUG:
        debug('doExchangeGdssCallBack OUT userId=', userId, 'exchangeId=', exchangeId, 'result=', result, 'ret=', ret)

    return ret
