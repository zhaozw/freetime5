# -*- coding=utf-8 -*-
"""
@date  : 2016-09-30
@author: GongXiaobo
"""
from freetime5.util import ftlog, fttime, ftstr
from tuyoo5.core import typlugin, tyglobal
from tuyoo5.core.tyconfig import TYBizConfException
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import UserKeys
from tuyoo5.plugins.condition.condition import TYItemActionCondition


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallItemActionConditionGotSecondDaysLater(TYItemActionCondition):
    """
    获取该道具达到多少天
    """
    TYPE_ID = 'ITEM.GOT.SECOND_DAYS_LATER'

    def __init__(self, start=1, end=None):
        super(HallItemActionConditionGotSecondDaysLater, self).__init__()
        assert (start is not None and start >= 0)
        assert (end is None or end >= start)
        self._start = start
        self._end = end

    def _conform(self, gameId, userId, clientId, item, timestamp, params):
        nowTimestamp = fttime.getDayStartTimestamp(timestamp)
        gotTimestamp = fttime.getDayStartTimestamp(item.createTime)
        gotDays = (nowTimestamp - gotTimestamp) / 86400
        return gotDays >= self._start if not self._end else \
            self._start <= gotDays <= self._end


class HallItemActionConditionBindPhoneCheck(TYItemActionCondition):
    """
    检查是否留过手机号
    """
    TYPE_ID = 'BINDPHONE.CHECK.IF_NEED_BIND_PHONE'

    def _conform(self, gameId, userId, clientId, item, timestamp, params):
        bindPhone = params.get('bindPhone', 0)
        if bindPhone:
            bindMobile = pluginCross.halldata.getUserDataList(userId, UserKeys.ATT_BIND_MOBILE)
            if not bindMobile:
                return False
            else:
                params['phoneNumber'] = str(bindMobile)
                return True
        return True


class HallItemActionConditionBindWeixin(TYItemActionCondition):
    TYPE_ID = 'item.action.cond.bind.weixin'

    def _conform(self, gameId, userId, clientId, item, timestamp, params):
        wxOpenId = pluginCross.halldata.getUserDataList(userId, UserKeys.ATT_WX_OPENID)
        return False if not wxOpenId else True


class TYItemActionConditionTimeRange(TYItemActionCondition):
    '''
    某个时间段内
    '''
    TYPE_ID = 'item.action.cond.timeRange'

    def __init__(self):
        super(TYItemActionConditionTimeRange, self).__init__()
        self.startTime = -1
        self.stopTime = -1

    def _conform(self, gameId, userId, clientId, item, timestamp, params):
        ret = ((self.startTime < 0 or timestamp >= self.startTime)
               and (self.stopTime < 0 or timestamp < self.stopTime))
        if _DEBUG:
            debug('TYItemActionConditionTimeRange._conform',
                  'gameId=', gameId,
                  'userId=', userId,
                  'itemId=', item.itemId,
                  'itemKindId=', item.kindId,
                  'timestamp=', timestamp,
                  'startTime=', self.startTime,
                  'stopTime=', self.stopTime,
                  'ret=', ret)
        return ret

    def decodeFromDict(self, d):
        super(TYItemActionConditionTimeRange, self).decodeFromDict(d)
        startTime = self.params.get('startTime')
        if startTime is not None:
            try:
                self.startTime = fttime.timestrToTimestamp(startTime, '%Y-%m-%d %H:%M:%S')
            except:
                raise TYBizConfException(startTime, 'TYItemActionConditionTimeRange.params.startTime must be timestr')
        stopTime = self.params.get('stopTime')
        if stopTime is not None:
            try:
                self.stopTime = fttime.timestrToTimestamp(stopTime, '%Y-%m-%d %H:%M:%S')
            except:
                raise TYBizConfException(stopTime, 'TYItemActionConditionTimeRange.params.stopTime must be timestr')
        return self


def _getSubGameDataVal(gameId, userId, attrName):
    rpcproxy = typlugin.getRpcProxy(gameId,
                                    typlugin.RPC_CALL_SAFE,
                                    typlugin.RPC_TARGET_MOD_ONE)
    rfc = rpcproxy.gamemgr.getGameData(userId,
                                       gameId,
                                       attrName)
    if not rfc:
        ftlog.warn('ERROR, the target game service not found !')
        return None

    elif rfc.getException():
        ftlog.warn('ERROR, the target game service got exception !', str(rfc.getException()))
        return None
    return rfc.getResult()


class TYItemActionConditionCanOpenFlag(TYItemActionCondition):
    """
    此处需要插件重新实现,第1、插件禁止操作9999的gamedata，第2、大厅本身无此逻辑
    """
    TYPE_ID = 'item.action.cond.canOpenFlag'

    def _conform(self, gameId, userId, clientId, item, timestamp, params):

        flagName = 'item.open.flag:%s' % (item.kindId)
        if gameId == tyglobal.gameId():
            value = pluginCross.halldata.getHallDataList(userId, flagName)
        else:
            value = _getSubGameDataVal(gameId, userId, flagName)

        if ftstr.parseInts(value) == 1:
            return True
        return False

    def decodeFromDict(self, d):
        super(TYItemActionConditionCanOpenFlag, self).decodeFromDict(d)
        self.gameId = self.params.get('gameId', tyglobal.gameId())
        if not isinstance(self.gameId, int) or self.gameId <= 0:
            raise TYBizConfException(self.params, 'TYItemActionConditionCanOpenFlag.params.gameId must = 0')
        return self
