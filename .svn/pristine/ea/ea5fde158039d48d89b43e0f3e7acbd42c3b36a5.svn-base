# -*- coding:utf-8 -*-
"""
Created on 2017年8月14日

@author: zhaojiangang
"""
import functools
import math
import time

from freetime5.twisted import ftcore
from freetime5.util import ftlog
from tuyoo5.core.tyconfig import TYBizConfException,TYConfable,TYConfableRegister
from tuyoo5.core.typlugin import pluginCross


class Logger(object):
    def __init__(self, kvs=None):
        self._args = []
        if kvs:
            for k, v in kvs:
                self.add(k, v)

    def add(self, k, v):
        self._args.append('%s=' % (k))
        self._args.append(v)

    def info(self, prefix=None, *args):
        self._log(prefix, ftlog.info, *args)

    def hinfo(self, prefix=None, *args):
        self._log(prefix, ftlog.hinfo, *args)

    def debug(self, prefix=None, *args):
        self._log(prefix, ftlog.debug, *args)

    def warn(self, prefix=None, *args):
        self._log(prefix, ftlog.warn, *args)

    def error(self, prefix=None, *args):
        self._log(prefix, ftlog.error, *args)

    def isDebug(self):
        return ftlog.is_debug()

    def _log(self, prefix, func, *args):
        argl = []
        if prefix:
            argl.append(prefix)
        argl.extend(self._args)
        argl.extend(args)
        func(*argl)


class MatchProcesser(object):
    ST_IDLE = 0
    ST_START = 1
    ST_STOP = 2

    def __init__(self, interval, handler):
        """
        count=0表示无限循环
        """
        self._handler = handler
        self._interval = interval
        self._timer = None
        self._state = self.ST_IDLE
        self._postTaskList = []

    def start(self):
        assert (self._state == self.ST_IDLE)
        self._state = self.ST_START
        self._timer = ftcore.runOnceDelay(self._interval, self._onTimeout)

    def stop(self):
        if self._state == self.ST_START:
            self._state = self.ST_IDLE

        if self._timer:
            self._timer.cancel()
            self._timer = None

    def postCall(self, func, *args, **kw):
        self.postTask(functools.partial(func, *args, **kw))

    def postTask(self, task):
        if self._state != self.ST_STOP:
            self._postTaskList.append(task)

    def _onTimeout(self):
        try:
            self._processPostTaskList()
            newInterval = self._handler()
            if newInterval is not None:
                self._interval = newInterval
            self._processPostTaskList()
        except:
            self._interval = 1
            ftlog.error('MatchProcesser._onTimeout',
                        self._handler)
            raise
        finally:
            if self._state == self.ST_START:
                self._timer = ftcore.runOnceDelay(self._interval, self._onTimeout)

    def _processPostTaskList(self):
        if self._postTaskList:
            taskList = self._postTaskList
            self._postTaskList = []
            for task in taskList:
                try:
                    task()
                except:
                    ftlog.error('MatchProcesser._processPostTaskList')


class MatchPlayerScoreCalc(object):
    def calc(self, score):
        """
        根据玩家现有积分计算玩家新积分
        """
        raise NotImplementedError


class MatchPlayerScoreCalcFactory(TYConfable):
    def newCalc(self, rankList):
        """
        根据rankList创建积分计算器
        """
        raise NotImplementedError


class MatchPlayerScoreCalcSet(MatchPlayerScoreCalc):
    def __init__(self, score):
        super(MatchPlayerScoreCalcSet, self).__init__()
        self.score = score

    def calc(self, score):
        """
        根据玩家现有积分计算玩家新积分
        """
        return self.score

    def __str__(self):
        return 'scorecalc:set:%s' % (self.score)


class MatchPlayerScoreCalcFactorySet(TYConfable):
    TYPE_ID = 'set'

    def __init__(self):
        super(MatchPlayerScoreCalcFactorySet, self).__init__()
        self.score = None

    def newCalc(self, rankList):
        """
        根据rankList创建积分计算器
        """
        return MatchPlayerScoreCalcSet(self.score)

    def decodeFromDict(self, d):
        self.score = d.get('score')
        if not isinstance(self.score, int):
            raise TYBizConfException(d, 'MatchPlayerScoreCalcSet.score must be int')

        return self


class MatchPlayerScoreCalcRate(MatchPlayerScoreCalc):
    def __init__(self, rate):
        super(MatchPlayerScoreCalcRate, self).__init__()
        self.rate = rate

    def calc(self, score):
        return int(score * self.rate)

    def __str__(self):
        return 'scorecalc:rate:%s' % (self.rate)


class MatchPlayerScoreCalcFactoryRate(MatchPlayerScoreCalcFactory):
    TYPE_ID = 'rate'

    def __init__(self):
        super(MatchPlayerScoreCalcFactoryRate, self).__init__()
        self.rate = None

    def newCalc(self, rankList):
        return MatchPlayerScoreCalcRate(self.rate)

    def decodeFromDict(self, d):
        self.rate = d.get('rate')
        if (not isinstance(self.rate, (int, float))
            or self.rate < 0
            or self.rate > 1):
            raise TYBizConfException(d, 'MatchPlayerScoreCalcFactoryPercent.rate must be int or float in [0, 1]')

        return self


class MatchPlayerScoreCalcSqrt(MatchPlayerScoreCalc):
    def __init__(self, base, middle):
        super(MatchPlayerScoreCalcSqrt, self).__init__()
        self.base = base
        self.middle = max(middle, 1)
        self.rate = self.base / self.middle ** 0.5

    def calc(self, score):
        return int((score ** 0.5) * self.rate) if score >= 0 else 0

    def __str__(self):
        return 'scorecalc:sqrt:(%s,%s,%s)' % (self.base, self.middle, self.rate)


class MatchPlayerScoreCalcFactorySqrt(MatchPlayerScoreCalcFactory):
    TYPE_ID = 'sqrt'

    def __init__(self):
        super(MatchPlayerScoreCalcFactorySqrt, self).__init__()
        self.base = None

    def newCalc(self, rankList):
        middle = len(rankList) / 2
        middleScore = rankList[middle].score

        if middleScore < 0:
            totalScore = 0
            for p in rankList:
                totalScore += p.score
            middleScore = totalScore / len(rankList)

        return MatchPlayerScoreCalcSqrt(self.base, middleScore)

    def decodeFromDict(self, d):
        self.base = d.get('base')
        if not isinstance(self.base, (int, float)):
            raise TYBizConfException(d, 'MatchPlayerScoreCalcFactorySqrt.base must be int or float')

        return self


class MatchPlayerScoreCalcFactoryRegister(TYConfableRegister):
    _typeid_clz_map = {
        MatchPlayerScoreCalcFactorySet.TYPE_ID: MatchPlayerScoreCalcFactorySet,
        MatchPlayerScoreCalcFactoryRate.TYPE_ID: MatchPlayerScoreCalcFactoryRate,
        MatchPlayerScoreCalcFactorySqrt.TYPE_ID: MatchPlayerScoreCalcFactorySqrt
    }

    def __init__(self):
        super(MatchPlayerScoreCalcFactoryRegister, self).__init__()
        self._typeid_clz_map = MatchPlayerScoreCalcFactoryRegister._typeid_clz_map

class MatchBaseScoreGrow(object):
    """
    积分增长器
    """

    def grow(self, score):
        """
        @param score: 当前积分
        @return: 增长后的积分
        """
        raise NotImplementedError


class MatchBaseScoreGrowFactory(TYConfable):
    """
    积分增长器工厂
    """

    def newScoreGrow(self):
        """
        @return: MatchBaseScoreGrow
        """
        raise NotImplementedError


class MatchBaseScoreGrowRate(object):
    """
    积分增长器
    """

    def __init__(self, factory):
        super(MatchBaseScoreGrowRate, self).__init__()
        self.factory = factory

    def grow(self, score):
        return score + score * self.factory.rate


class MatchBaseScoreGrowFactoryRate(MatchBaseScoreGrowFactory):
    """
    百分比增长算法
    """
    TYPE_ID = 'rate'

    def __init__(self):
        super(MatchBaseScoreGrowFactoryRate, self).__init__()
        self.rate = None

    def newScoreGrow(self):
        return MatchBaseScoreGrowRate(self)

    def decodeFromDict(self, d):
        self.rate = d.get('rate')
        if not isinstance(self.rate, (int, float)) or self.rate <= 0:
            raise TYBizConfException(d, 'MatchBaseScoreGrowRate.rate must be int or float > 0')

        return self


class MatchBaseScoreGrowIncr(object):
    """
    积分增长器
    """

    def __init__(self, factory):
        super(MatchBaseScoreGrowIncr, self).__init__()
        self.factory = factory
        self.growCount = 0

    def grow(self, score):
        self.growCount +=1
        return score + self.factory.base + self.growCount * self.factory.incr


class MatchBaseScoreGrowFactoryIncr(MatchBaseScoreGrowFactory):
    TYPE_ID = 'incr'

    def __init__(self):
        super(MatchBaseScoreGrowFactoryIncr, self).__init__()
        self.base = None
        self.incr = None

    def newScoreGrow(self):
        return MatchBaseScoreGrowIncr(self)

    def decodeFromDict(self, d):
        self.base = d.get('base')
        if not isinstance(self.base, int):
            raise TYBizConfException('MatchScoreGrowRate.base must be int > 0')

        self.incr = d.get('incr')
        if not isinstance(self.incr, int):
            raise TYBizConfException('MatchScoreGrowRate.incr must be int > 0')

        return self


class MatchBaseScoreGrowFactoryRegister(TYConfableRegister):
    _typeid_clz_map = {
        MatchBaseScoreGrowFactoryRate.TYPE_ID: MatchBaseScoreGrowFactoryRate,
        MatchBaseScoreGrowFactoryIncr.TYPE_ID: MatchBaseScoreGrowFactoryIncr
    }

    def __init__(self):
        super(MatchBaseScoreGrowFactoryRegister, self).__init__()
        self._typeid_clz_map = MatchBaseScoreGrowFactoryRegister._typeid_clz_map

class MatchLoseScoreCalc(TYConfable):
    """
    淘汰分计算器
    """

    def calcLoseScore(self, baseScore):
        """
        根据baseScore计算淘汰分数
        """
        pass


class MatchLoseScoreCalcRate(MatchLoseScoreCalc):
    """
    按照底分比率进行计算
    """
    TYPE_ID = 'rate'

    def __init__(self):
        super(MatchLoseScoreCalcRate, self).__init__()
        self.rate = None

    def calcLoseScore(self, baseScore):
        return baseScore * self.rate

    def decodeFromDict(self, d):
        self.rate = d.get('rate')
        if not isinstance(self.rate, (int, float)) or self.rate < 0 or self.rate > 1:
            raise TYBizConfException(d, 'MatchLoseScoreRate.rate must be int in [0, 1]')

        return self

    def __str__(self):
        return 'losescore:rate:%s' % (self.rate)


class MatchLoseScoreCalcFixed(MatchLoseScoreCalc):
    """
    到达某个分数进行淘汰
    """
    TYPE_ID = 'fixed'

    def __init__(self):
        super(MatchLoseScoreCalcFixed, self).__init__()
        self.loseScore = None

    def calcLoseScore(self, baseScore):
        return self.loseScore

    def decodeFromDict(self, d):
        self.loseScore = d.get('loseScore')
        if not isinstance(self.loseScore, int):
            raise TYBizConfException(d, 'MatchLoseScoreCalcFixed.loseScore must be int')

        return self

    def __str__(self):
        return 'losescore:fixed:%s' % (self.loseScore)


class MatchLoseScoreRegister(TYConfableRegister):
    _typeid_clz_map = {
        MatchLoseScoreCalcRate.TYPE_ID: MatchLoseScoreCalcRate,
        MatchLoseScoreCalcFixed.TYPE_ID: MatchLoseScoreCalcFixed
    }

    def __init__(self):
        super(MatchLoseScoreRegister, self).__init__()
        self._typeid_clz_map = MatchLoseScoreRegister._typeid_clz_map



class MatchGroupUtils(object):
    GROUP_NAME_PREFIX = [chr(i) for i in range(ord('A'), ord('F') + 1)]

    @classmethod
    def generateGroupName(cls, groupCount, i):
        assert (0 <= i < groupCount)
        groupName = cls.GROUP_NAME_PREFIX[i % len(cls.GROUP_NAME_PREFIX)]
        number = i / len(cls.GROUP_NAME_PREFIX) + 1
        groupName += '%s' % (number)
        return groupName

    @classmethod
    def calcCountByMaxCountPerGroup(cls, playerCount, maxCountPerGroup, tableSeatCount):
        groupCount = (playerCount + maxCountPerGroup - 1) / maxCountPerGroup
        userCountPerGroup = playerCount / groupCount
        userCountPerGroup += tableSeatCount - userCountPerGroup % tableSeatCount
        return groupCount, min(userCountPerGroup, maxCountPerGroup)

    @classmethod
    def groupByMaxCountPerGroup(cls, playerList, maxCountPerGroup, tableSeatCount):
        groupCount, countPerGroup = cls.calcCountByMaxCountPerGroup(len(playerList), maxCountPerGroup, tableSeatCount)
        pos = 0
        ret = []
        for _ in xrange(groupCount):
            nextPos = pos + countPerGroup
            ret.append(playerList[pos:nextPos])
            pos = nextPos
        return ret


class MatchBIUtils(object):
    @classmethod
    def getBiChipType(cls, assetKindId):
        # if assetKindId == hallitem.ASSET_CHIP_KIND_ID:
        #     return daoconst.CHIP_TYPE_CHIP
        # elif assetKindId == hallitem.ASSET_COUPON_KIND_ID:
        #     return daoconst.CHIP_TYPE_COUPON
        # elif assetKindId.startswith('item'):
        #     return daoconst.CHIP_TYPE_ITEM
        # elif assetKindId == hallitem.ASSET_DIAMOND_KIND_ID:
        #     return daoconst.CHIP_TYPE_DIAMOND
        # else:
        #     return 0
        return 0

    @classmethod
    def buildRewards(cls,rankRewards):
        ret = []
        # for r in rankRewards:
        #     if r['count'] > 0:
        #         # name = hallconf.translateAssetKindIdToOld(r['itemId'])
        #         assetKind = hallitem.itemSystem.findAssetKind(r['itemId'])
        #         ret.append({'name': assetKind.displayName or '', 'count': r['count'], 'url': assetKind.pic if
        #         assetKind else ''})
        return ret

    @classmethod
    def buildRewardsDesc(cls,rankRewards):
        notNeedDescNames = set(['user:chip', 'user:coupon', 'ddz.exp'])
        allZero = True
        for r in rankRewards.rewards:
            if r['count'] <= 0:
                continue
            if r['itemId'] not in notNeedDescNames:
                return rankRewards.desc
        return rankRewards.desc if allZero else ""

    # @classmethod
    # def reportGameEvent(cls, gameId, eventId, userId, clientId, roomId, tableId, roundId, detalChip, state1, state2,
    #                     cardlist, tag=''):
    #     try:
    #         bireport.reportGameEvent(eventId, userId, 6, roomId, tableId, roundId, detalChip, state1, state2, cardlist,
    #                                  clientId, 0, 0)
    #         ftlog.info('MatchBIUtils.reportGameEvent',
    #                    'eventId=', eventId,
    #                    'userId=', userId,
    #                    'gameId=', gameId,
    #                    'roomId=', roomId,
    #                    'tableId=', tableId,
    #                    'roundId=', roundId,
    #                    'tag=', tag)
    #     except:
    #         ftlog.error('MatchBIUtils.reportGameEvent',
    #                     'eventId=', eventId,
    #                     'userId=', userId,
    #                     'gameId=', gameId,
    #                     'roomId=', roomId,
    #                     'tableId=', tableId,
    #                     'roundId=', roundId,
    #                     'tag=', tag)


class MsgHandler(object):
    """
    配合matchcomm/servers/room/match_handler.py:MatchTcpHandler处理比赛协议.
    """
    def handleMsg(self, msg):
        handler = self.findMsgHandler(msg)
        if handler:
            ret = handler(msg)
            return True, ret
        return False, None

    def findMsgHandler(self, msg):
        cmd = msg.getCmd()
        action = msg.getAction()
        ftlog.info('StageMatchRoomMixin.MsgHandler ...',
                   'cmd=', cmd,
                   'action=', action)
        if action:
            handlerName = '_do_%s__%s' % (cmd, action)
        else:
            handlerName = '_do_%s' % (cmd,)

        if hasattr(self, handlerName):
            return getattr(self, handlerName)

        handlerName = '_do_%s__' % (cmd,)
        if hasattr(self, handlerName):
            return getattr(self, handlerName)

        ftlog.warn('StageMatchRoomMixin.MsgHandler not find handler',
                   'cmd=', cmd,
                   'action=', action)
        return None


def datetimeToTimestamp(dt):
    '''
    datetime对象转化为时间戳
    '''
    return time.mktime(dt.timetuple())

def getRiseWaitTime(asvg,uncompleted):
    """
    计算比赛剩余晋级时间.
    TODO 瑞士移位的剩余时间计算
    :param asvg: 每桌平均开始时间，秒
    :param uncompleted: 未完成桌
    :return: 剩余大约开赛时间，秒
    """
    if uncompleted <= 0 :
        return 10
    if uncompleted == 1 :
        return asvg*0.2
    else:
        return int(math.floor(math.pow(uncompleted,1.0/8)*asvg*0.2))


def checkUserLockForMatch(userId):
    """
    检查用户断线重连标识
    """
    if not isRobot(userId):
        ret = pluginCross.onlinedata.getOnlineLocList(userId)
        return True if len(ret) == 0 else False
    return True


def lockUserForMatch(userId, roomId):
    """
    添加比赛断线重连标识
    :param userId:
    :param roomId:
    """
    if not isRobot(userId):
        queueTableId = roomId * 10000
        max_seatid = 1000
        pluginCross.onlinedata.addOnlineLoc(userId, roomId, queueTableId, max_seatid)

def unlockUserForMatch(userId, roomId, tableId=None):
    """
    移除比赛断线重连标识
    :param userId:
    :param roomId:
    :return:
    """
    if not isRobot(userId):
        if not tableId:
            tableId = roomId * 10000
        pluginCross.onlinedata.removeOnlineLoc(userId, roomId, tableId)


def isRobot(userId):
    robot_user_id_max = 10000
    if userId > 0 and userId <= robot_user_id_max :
        return True
    return False


if __name__ == '__main__':
    #     groupCount = 53
    #     for i in xrange(groupCount):
    #         print i, MatchGroupUtils.generateGroupName(groupCount, i)
    playerCount = 20
    playerList = [i for i in xrange(playerCount)]
    groups = MatchGroupUtils.groupByMaxCountPerGroup(playerList, 6, 3)
    print [len(pl) for pl in groups]
