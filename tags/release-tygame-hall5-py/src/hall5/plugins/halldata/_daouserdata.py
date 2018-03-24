# -*- coding: utf-8 -*-
'''
Created on 2015-5-12
@author: zqh
'''
from freetime5.util import ftlog
from freetime5.util.ftmark import noException
from tuyoo5.core import tyconfig
from tuyoo5.core import tygame
from tuyoo5.core import typlugin
from tuyoo5.core.tyconst import CHIP_TYPE_CHIP
from tuyoo5.core.tyconst import CHIP_TYPE_COUPON
from tuyoo5.core.tyconst import CHIP_TYPE_DIAMOND
from tuyoo5.core.tyconst import CHIP_TYPE_TABLE_CHIP
from tuyoo5.core.tyconst import EVENT_NAME_SYSTEM_REPAIR
from tuyoo5.core.tydao import DataAttrIntAtomic
from tuyoo5.core.tydao import DataSchemaHashAttrs
from tuyoo5.core.tydao import DataSchemaHashSameKeys
from tuyoo5.core.tyrpchall import ChipNotEnoughOpMode
from tuyoo5.core.tyrpchall import UserKeys
from tuyoo5.game import tybireport
from tuyoo5.game import tysessiondata


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class DaoUserData(DataSchemaHashAttrs):

    DBNAME = 'user'
    MAINKEY = 'user:%s'

    ATTS = UserKeys


class DaoTableChip(DataSchemaHashSameKeys):
    DBNAME = 'user'
    MAINKEY = 'tablechip:%s'
    SUBVALDEF = DataAttrIntAtomic('tablechip', 0)


def getUserChipAll(uid):
    '''
    取得用户的所有金币, 包含被带入tablechip的金币
    '''
    allchip = DaoUserData.HGET(uid, UserKeys.ATT_CHIP)
    tchips = DaoTableChip.HVALS(uid)
    if tchips:
        for x in tchips:
            allchip += x
    return allchip


def getUserChip(uid):
    '''
    取得用户的所有金币, 包含被带入tablechip的金币
    '''
    return DaoUserData.HGET(uid, UserKeys.ATT_CHIP)


def getTableChip(uid, _gameid, tableId):
    '''
    取得用户的table_chip
    返回:
        否则返回对应桌子上的tablechip值 int类型
    '''
    return DaoTableChip.HGET(uid, tableId)


def getTableChipSum(uid):
    '''
    取得用户的table_chip
    返回:
        所有的tablechip的合计 int类型
    '''
    vals = DaoTableChip.HVALS(uid)
    return sum(vals)


def getTableChipDict(uid):
    '''
    取得用户的table_chip
    返回:
        所有的tablechip的所有数据 dict类型
    '''
    return DaoTableChip.HGETALL(uid)


def delTableChips(uid, tableIdList):
    '''
    取得用户的table_chip
    返回:
        所有的tablechip
    '''
    return DaoTableChip.HDEL(uid, tableIdList)


def moveAllChipToTableChip(uid, gameid, eventId, intEventParam, clientId, tableId,
                           extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    转移用户所有的chip至tablechip
    参考: set_tablechip_to_range
    '''
    return _setTableChipToRange(uid, gameid, -1, -1, eventId, intEventParam, clientId, tableId,
                                extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)


def moveAllTableChipToChip(uid, gameid, eventId, intEventParam, clientId, tableId,
                           extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    转移用户所有的tablechip至chip
    参考: set_tablechip_to_range
    '''
    return _setTableChipToRange(uid, gameid, 0, 0, eventId, intEventParam, clientId, tableId,
                                extentId=extentId,roomId=roomId, roundId=roundId, param01=param01, param02=param02)


def setTableChipToN(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                    extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    设置用户的tablechip至传入的值
    参考: set_tablechip_to_range
    '''
    return _setTableChipToRange(uid, gameid, tablechip, tablechip, eventId, intEventParam, clientId, tableId,
                                extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)


def setTableChipToBigThanN(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                           extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    设置用户的tablechip大于等于传入的值
    参考: set_tablechip_to_range
    '''
    return _setTableChipToRange(uid, gameid, tablechip, -1, eventId, intEventParam, clientId, tableId,
                                extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)


def setTableChipToNIfLittleThan(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                                extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    如果用户的tablechip小于传入的值, 至那么设置tablechip至传入的值
    参考: set_tablechip_to_range
    '''
    return _setTableChipToRange(uid, gameid, tablechip, -2, eventId, intEventParam, clientId, tableId,
                                extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)


def setTablechipNearToNIfLittleThan(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                                    extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    tablechip 小于 n 时, 让 tablechip 尽量接近 n
    参考: set_tablechip_to_range
    '''
    return _setTableChipToRange(uid, gameid, -2, tablechip, eventId, intEventParam, clientId, tableId,
                                extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)


def setTableChipToRange(uid, gameid, _min, _max, eventId, intEventParam, clientId, tableId,
                        extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    chip与tablechip转换
    使得tablechip在 [_min, _max] 范围内尽量大。
    _min, _max 正常取值范围：>= 0
    特殊取值，代表redis中的当前值：
        -1: chip+tablechip
        -2: tablechip
        -3: chip
    否则设置gamedata中的tablechip
    返回: (table_chip_final, user_chip_final, delta_chip)
        table_chip_final 最终的tablechip数量
        user_chip_final 最终的userchip数量
        delta_chip 操作变化的数量
    '''
    return _setTableChipToRange(uid, gameid, _min, _max, eventId, intEventParam, clientId, tableId,
                                extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)


def _setTableChipToRange(uid, gameid, _min, _max, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    assert (isinstance(_min, int) and (_min >= 0 or _min in (-1, -2, -3)) and
            isinstance(_max, int) and (_max >= 0 or _max in (-1, -2, -3)))

    numberClientId = tyconfig.clientIdToNumber(tysessiondata.getClientId(uid))
    appId = tysessiondata.getGameId(uid)

    otherAttName = str(tableId)
    otherKey = DaoTableChip.MAINKEY % (uid)
    tdelta, tfinal, tfixed, delta, final, fixed = DaoUserData.MOVE_OTHER_INT_TO_RANGE(
        uid, _min, _max, UserKeys.ATT_CHIP,
        otherKey, otherAttName)

    if _DEBUG:
        debug('UserChip->_setTableChipToRange', uid, gameid, _min, _max,
              eventId, intEventParam, clientId, tableId, otherKey,
              roomId, roundId, param01, param02,
              'result->', tdelta, tfinal, tfixed, delta, final, fixed)

    args = {}
    args['clientId'] = clientId
    args['appId'] = appId
    args['_min'] = _min
    args['_max'] = _max

    if tfixed != 0:
        tybireport.reportBiChip(uid, tfixed, tfixed, 0, EVENT_NAME_SYSTEM_REPAIR,
                                numberClientId, gameid, appId, intEventParam,
                                CHIP_TYPE_TABLE_CHIP, extentId=extentId, roomId=roomId, tableId=tableId,
                                roundId=roundId, param01=param01, param02=param02,
                                argdict=args)
    if fixed != 0:
        tybireport.reportBiChip(uid, fixed, fixed, 0, EVENT_NAME_SYSTEM_REPAIR,
                                numberClientId, gameid, appId, intEventParam,
                                CHIP_TYPE_CHIP, extentId=extentId, roomId=roomId, tableId=tableId,
                                roundId=roundId, param01=param01, param02=param02,
                                argdict=args)
    if tdelta != 0:
        tybireport.reportBiChip(uid, tdelta, tdelta, tfinal, eventId,
                                numberClientId, gameid, appId, intEventParam,
                                CHIP_TYPE_TABLE_CHIP, extentId=extentId, roomId=roomId, tableId=tableId,
                                roundId=roundId, param01=param01, param02=param02,
                                argdict=args)
    if delta != 0:
        tybireport.reportBiChip(uid, delta, delta, final, eventId,
                                numberClientId, gameid, appId, intEventParam,
                                CHIP_TYPE_CHIP, extentId=extentId, roomId=roomId, tableId=tableId,
                                roundId=roundId, param01=param01, param02=param02,
                                argdict=args)
        typlugin.asyncTrigerEvent(tygame.ChipChangedEvent(uid, gameid, delta, final))

    return tfinal, final, delta


def incrTableChip(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, _clientId, tableId,
                  extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    对用户的tablechip进行INCR操作
    否则设置gamedata中的tablechip
    参考: incr_chip
    '''
    lowLimit, highLimit = -1, -1
    attName = str(tableId)
    trueDelta, finalCount, fixed = DaoTableChip.HINCRBY_LIMIT(uid, attName, deltaCount, lowLimit, highLimit,
                                                              chipNotEnoughOpMode)
    _chipReport(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam,
                CHIP_TYPE_TABLE_CHIP, trueDelta, finalCount, fixed,
                extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId,
                param01=param01, param02=param02)
    return trueDelta, finalCount


def incrTableChipLimit(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam,
                       _clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    对用户的tablechip进行INCR操作
    否则设置gamedata中的tablechip
    参考: incr_chip_limit
    '''
    attName = str(tableId)
    trueDelta, finalCount, fixed = DaoTableChip.HINCRBY_LIMIT(uid, attName, deltaCount, lowLimit, highLimit,
                                                              chipNotEnoughOpMode)
    _chipReport(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam,
                CHIP_TYPE_TABLE_CHIP, trueDelta, finalCount, fixed,
                extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId,
                param01=param01, param02=param02)
    return trueDelta, finalCount


def incrChipLimit(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam, _clientId,
                  extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    '''
    对用户的金币进行INCR操作
    @param uid: userId
    @param gameid: 游戏ID
    @param deltaCount: 变化的值可以是负数
    @param lowLimit 用户最低金币数，-1表示没有最低限制
    @param highLimit 用户最高金币数，-1表示没有最高限制
    @param mode: 当INCR动作会变成负数时的处理模式, 0表示不进行操作; 1会给金币清零
    @param eventId: 触发INCR的事件ID
    @param argdict: 需要根据事件传入intEventParam
    @return (trueDelta, final) trueDelta表示实际变化的值, final表示变化后的最终数量

    地主收房间服务费示例
    地主每玩完一局需要收服务费, 对用户金币没有上下限，如果用户的金币不够服务费就收取用户所有金币, 所以mode=ChipNotEnoughOpMode.CLEAR_ZERO
    用户10001当前金币为100, 在地主601房间(服务费为500)玩了一局, 收服务费代码为
    trueDelta, final = UserProps.incr_chip_limit(10001, 6, -500, -1, -1,
                                                            ChipNotEnoughOpMode.CLEAR_ZERO,
                                                            BIEvent.ROOM_GAME_FEE, roomId=601)
    此时trueDelta=-100, final=0

    地主收报名费示例
    用户10001当前金币为100, 报名610房间的比赛(需要报名费1000金币), 对用户金币没有上下限, 报名费不足则不处理，所以mode=ChipNotEnoughOpMode.NOOP
    trueDelta, final = UserProps.incr_chip_limit(10001, 6, -1000, -1, -1,
                                                            ChipNotEnoughOpMode.NOOP,
                                                            BIEvent.MATCH_SIGNIN_FEE, roomId=610)
    if trueDelta == -1000:
        # 收取报名费成功进行报名操作
        pass
    else:
        # 报名费不足，给客户端返回错误
        pass

    有上下限的示例
    在地主601房间最低准入为1000金币，扔鸡蛋价格为10金币，用户10001的当前金币为1000, 此时的delta为10下限为1010, 没有上限
    trueDelta, final = UserProps.incr_chip_limit(10001, 6, -10, 1010, -1,
                                                            ChipNotEnoughOpMode.NOOP,
                                                            BIEvent.EMOTICON_EGG_CONSUME, roomId=610)
    if trueDelta == -10:
        # 收取扔鸡蛋金币成功
        pass
    else:
        # 扔鸡蛋金币不足，给客户端返回错误
        pass
    '''
    trueDelta, finalCount, fixed = DaoUserData.HINCRBY_LIMIT(uid, UserKeys.ATT_CHIP, deltaCount, lowLimit,
                                                             highLimit, chipNotEnoughOpMode)
    _chipReport(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam,
                CHIP_TYPE_CHIP, trueDelta, finalCount, fixed,
                extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId,
                param01=param01, param02=param02)

    if trueDelta != 0:
        typlugin.asyncTrigerEvent(tygame.ChipChangedEvent(uid, gameid, trueDelta, finalCount))

    return trueDelta, finalCount


@noException()
def _chipReport(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam, chipType,
                trueDelta, finalCount, fixed, extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    clientId = tysessiondata.getClientId(uid)
    numberClientId = tyconfig.clientIdToNumber(clientId)
    appId = tysessiondata.getGameId(uid)

    args = {}
    args['clientId'] = clientId
    args['appId'] = appId
    args['deltaCount'] = deltaCount
    args['lowLimit'] = lowLimit
    args['highLimit'] = highLimit
    args['chipType'] = chipType
    args['mode'] = chipNotEnoughOpMode

    if fixed != 0:
        tybireport.reportBiChip(uid, fixed, fixed, 0, EVENT_NAME_SYSTEM_REPAIR,
                                numberClientId, gameid, appId, intEventParam, chipType,
                                extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId,
                                param01=param01, param02=param02, argdict=args)
    if trueDelta != 0 or deltaCount == 0:
        tybireport.reportBiChip(uid, deltaCount, trueDelta, finalCount, eventId,
                                numberClientId, gameid, appId, intEventParam, chipType,
                                extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId,
                                param01=param01, param02=param02, argdict=args)


def incrChip(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam,
             extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    '''
    对用户的金币进行INCR操作
    @param uid: userId
    @param gameid: 游戏ID
    @param deltaCount: 变化的值可以是负数
    @param chipNotEnoughOpMode: 当INCR动作会变成负数时的处理模式, 0表示不进行操作; 1会给金币清零
    @param eventId: 触发INCR的事件ID
    @param argdict: 需要根据事件传入intEventParam
    @return (trueDelta, final) trueDelta表示实际变化的值, final表示变化后的最终数量
    参考incr_chip_limit的调用，此方法相当于用lowLimit, highLimit都是-1去调用incr_chip_limit
    '''
    lowLimit, highLimit = -1, -1
    trueDelta, finalCount, fixed = DaoUserData.HINCRBY_LIMIT(uid, UserKeys.ATT_CHIP, deltaCount, lowLimit,
                                                             highLimit, chipNotEnoughOpMode)
    _chipReport(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam,
                CHIP_TYPE_CHIP, trueDelta, finalCount, fixed,
                extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId,
                param01=param01, param02=param02)

    if trueDelta != 0:
        typlugin.asyncTrigerEvent(tygame.ChipChangedEvent(uid, gameid, trueDelta, finalCount))

    return trueDelta, finalCount


def incrCoupon(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam,
               extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    '''
    对用户的兑换券进行INCR操作
    参考: incr_chip
    '''
    lowLimit, highLimit = -1, -1
    trueDelta, finalCount, fixed = DaoUserData.HINCRBY_LIMIT(uid, UserKeys.ATT_COUPON, deltaCount,
                                                             lowLimit, highLimit, chipNotEnoughOpMode)
    _chipReport(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam,
                CHIP_TYPE_COUPON, trueDelta, finalCount, fixed,
                extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId,
                param01=param01, param02=param02)
    if trueDelta != 0:
        typlugin.asyncTrigerEvent(tygame.CouponChangedEvent(uid, gameid, trueDelta, finalCount))
    return trueDelta, finalCount


def incrExp(userId, detalExp):
    '''
    调整用户的经验值
    '''
    _, finalCount, _ = DaoUserData.HINCRBY_LIMIT(userId, UserKeys.ATT_EXP, detalExp, 0, -1,
                                                 ChipNotEnoughOpMode.CLEAR_ZERO)
    return finalCount


def incrCharm(userId, detalCharm):
    '''
    调整用户的魅力值
    '''
    _, finalCount, _ = DaoUserData.HINCRBY_LIMIT(userId, UserKeys.ATT_CHARM, detalCharm, 0, -1,
                                                 ChipNotEnoughOpMode.CLEAR_ZERO)
    return finalCount


def incrDiamond(userId, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId,
                extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    if not clientId:
        clientId = tysessiondata.getClientId(userId)
    lowLimit, highLimit = -1, -1
    trueDelta, finalCount, fixed = DaoUserData.HINCRBY_LIMIT(userId, UserKeys.ATT_DIAMOND, deltaCount,
                                                             lowLimit, highLimit, chipNotEnoughOpMode)
    _chipReport(userId, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam,
                CHIP_TYPE_DIAMOND, trueDelta, finalCount, fixed,
                extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId,
                param01=param01, param02=param02)
    return trueDelta, finalCount
