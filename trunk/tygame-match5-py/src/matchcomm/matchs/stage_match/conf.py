# -*- coding:utf-8 -*-
"""
Created on 2017年8月18日

@author: zhaojiangang
"""
import time
from sre_compile import isstring

from datetime import datetime

from freetime5.util import fttime
from freetime5.util.ftcron import FTCron
from tuyoo5.core.tyconfig import TYBizConfException, TYConfable, TYConfableRegister
from matchcomm.matchs.const import MatchStartType, MatchFeeType
from matchcomm.matchs.interface import MatchRankRewards, MatchFee
from matchcomm.matchs.utils import MatchBaseScoreGrowFactoryRegister, \
    MatchLoseScoreRegister, MatchPlayerScoreCalcFactoryRegister

class StageConf(object):
    def __init__(self):
        # 该阶段名称
        self.name = None
        # 最多打几副牌
        self.cardCount = None
        # 晋级人数
        self.riseUserCount = None
        # 底分
        self.baseScore = None
        # 积分算法
        self.scoreCalcFac = None
        # 每组最大人数, 0表示不分组
        self.userCountPerGroup = None
        # 赛制配置
        self.rulesConf = None
        # 阶段索引
        self.stageIndex = None
        # 奖励
        self.rankRewardsList = None
        # 延迟进入比赛时间=0表示不支持延时进入
        self.delayEntryTimes = None
        # 附加的参数
        self.params = {}

    def getParam(self, key, defVal=None):
        return self.params.get(key, defVal)

    def decodeFromDict(self, d):
        self.name = d.get('name')
        if not isstring(self.name):
            raise TYBizConfException(d, 'StageConf.name must be not empty string')

        self.cardCount = d.get('card.count')
        if not isinstance(self.cardCount, int) or self.cardCount <= 0:
            raise TYBizConfException(d, 'StageConf.card.count must be int > 0')

        self.riseUserCount = d.get('rise.user.count')
        if not isinstance(self.riseUserCount, int) or self.riseUserCount <= 0:
            raise TYBizConfException(d, 'StageConf.rise.user.count must be int > 0')

        self.baseScore = d.get('score.base')
        if not isinstance(self.baseScore, int):
            raise TYBizConfException(d, 'StageConf.chip.base must be int > 0')

        # decodeFromDict 不是类方法了
        self.scoreCalcFac = MatchPlayerScoreCalcFactoryRegister().decodeFromDict(d.get('score.calc'))

        self.userCountPerGroup = d.get('grouping.user.count', 0)
        if not isinstance(self.userCountPerGroup, int) or self.userCountPerGroup < 0:
            raise TYBizConfException(d, 'StageConf.grouping.user.count must be int >= 0')

        self.rankRewardsList = []
        rankRewardsList = d.get('rank.rewards', [])
        if not isinstance(rankRewardsList, list):
            raise TYBizConfException(d, 'StageConf.rank.rewards must be list')
        for rankRewards in rankRewardsList:
            self.rankRewardsList.append(MatchRankRewards().decodeFromDict(rankRewards))

        self.delayEntryTimes = d.get('delayEntryTimes', 0)
        if not isinstance(self.delayEntryTimes, (int, float)) or self.delayEntryTimes < 0:
            raise TYBizConfException(d, 'StageConf.delayEntryTimes must be (int, float) >= 0')

        self.params = d.get('params', {})
        if not isinstance(self.params, dict):
            raise TYBizConfException(d, 'StageConf.params must be dict')

        # 赛制配置
        self.rulesConf = StageMatchRulesConfRegister().decodeFromDict(d.get('rules'))

        return self


class MatchStartConf(TYConfable):
    """
    比赛开始配置
    """

    def __init__(self):
        self.conf = None

        # 通用配置
        self.type = None
        self.feeType = None
        self.maxPlayTime = None
        self.tableTimes = None
        # 平均一桌时间
        self.tableAvgTimes = None

        # 人满开赛的配置
        self.userCount = None

        # 定时赛配置
        self.userMinCount = None
        self.userMaxCount = None
        self.signinMaxCount = None
        self.userMaxCountPerMatch = None
        self.userNextGroup = None
        self.signinTimes = None
        self.prepareTimes = None
        self.signinTimesStr = None
        self.times = None
        self._cron = None

        # 开赛速度
        self.selectFirstStage = None

    def isTimingType(self):
        return self.type == MatchStartType.TIMING

    def isUserCountType(self):
        return self.type == MatchStartType.USER_COUNT

    def calcNextStartTime(self, timestamp=None):
        timestamp = timestamp or fttime.getCurrentTimestamp()
        ntime = datetime.fromtimestamp(int(timestamp))
        nexttime = None
        if self._cron:
            nexttime = self._cron.getNextTime(ntime)
        if nexttime is not None:
            return int(time.mktime(nexttime.timetuple()))
        return None

    def getTodayNextLater(self):
        if self._cron:
            return self._cron.getTodayNextLater()
        return -1

    def calcSigninTime(self, startTime):
        assert (self.isTimingType())
        if self.signinTimes:
            return startTime - self.signinTimes
        return None

    def calcPrepareTime(self, startTime):
        assert (self.isTimingType())
        if self.prepareTimes:
            return startTime - self.prepareTimes
        return startTime - 5

    def buildSigninTimeStr(self):
        if not self.isTimingType():
            return u''
        if self.signinTimesStr:
            return self.signinTimesStr
        ts = int(self.signinTimes)
        thours = int(ts / 3600)
        ts = ts - thours * 3600
        tminutes = int(ts / 60)
        ts = ts - tminutes * 60
        tseconds = int(ts % 60)
        tstr = u''
        if thours > 0:
            tstr = tstr + unicode(thours) + u'小时'
        if tminutes > 0:
            tstr = tstr + unicode(tminutes) + u'分钟'
        if tseconds > 0:
            tstr = tstr + unicode(tseconds) + u'秒'
        return u'请在比赛开始前%s，报名参加此比赛' % (tstr)

    def decodeFromDict(self, d):
        self.type = d.get('type')
        if not MatchStartType.isValid(self.type):
            raise TYBizConfException(d, 'MatchStartConf.type must in %s' % (MatchStartType.VALID_TYPES))

        self.feeType = d.get('fee.type')
        if not MatchFeeType.isValid(self.feeType):
            raise TYBizConfException(d, 'MatchStartConf.fee.type must in %s' % (MatchFeeType.VALID_TYPES))

        self.maxPlayTime = d.get('maxplaytime')
        if not isinstance(self.maxPlayTime, int) or self.maxPlayTime <= 0:
            raise TYBizConfException(d, 'MatchStartConf.maxplaytime must int > 0')

        self.tableTimes = d.get('table.times', 400)
        if not isinstance(self.tableTimes, int) or self.tableTimes <= 0:
            raise TYBizConfException(d, 'MatchStartConf.table.times must int > 0')

        self.tableAvgTimes = d.get('table.avg.times', 400)
        if not isinstance(self.tableAvgTimes, int) or self.tableAvgTimes <= 0:
            raise TYBizConfException(d, 'MatchStartConf.table.avg.times must int > 0')

        if self.isUserCountType():
            # 人满开赛的配置
            self.userCount = d.get('user.size', None)
            if not isinstance(self.userCount, int) or self.userCount <= 0:
                raise TYBizConfException(d, 'MatchStartConf.user.size must int > 0')
        else:
            self.userMinCount = d.get('user.minsize')
            if not isinstance(self.userMinCount, int) or self.userMinCount <= 0:
                raise TYBizConfException('MatchStartConf.user.minsize must be int > 0')

            self.userMaxCount = d.get('user.maxsize')
            if not isinstance(self.userMaxCount, int) or self.userMaxCount <= 0:
                raise TYBizConfException('MatchStartConf.user.maxsize must be int > 0')

            self.signinMaxCount = d.get('signin.maxsize', self.userMaxCount)
            if not isinstance(self.signinMaxCount, int) or self.signinMaxCount <= 0:
                raise TYBizConfException('MatchStartConf.signin.maxsize must be int > 0')

            self.userMaxCountPerMatch = self.userMaxCount
            self.signinMaxCountPerMatch = self.signinMaxCount

            self.signinTimes = d.get('signin.times')
            if not isinstance(self.signinTimes, int) or self.signinTimes < 0:
                raise TYBizConfException('MatchStartConf.signin.times must be int >= 0')

            self.signinTimesStr = d.get('signinTimesStr', '')
            if not isstring(self.signinTimesStr):
                raise TYBizConfException('MatchStartConf.signinTimesStr must be string')

            self.prepareTimes = d.get('prepare.times', 5)
            if not isinstance(self.prepareTimes, int) or self.prepareTimes < 0:
                raise TYBizConfException('MatchStartConf.prepare.times must be int >= 0')

            self.userNextGroup = d.get('user.next.group')
            if not isinstance(self.userNextGroup, (int, float)):
                raise TYBizConfException('MatchStartConf.user.next.group must be float')

            self.selectFirstStage = d.get('selectFirstStage', 0)
            if self.selectFirstStage not in (0, 1):
                raise TYBizConfException('MatchStartConf.selectFirstStage must in (0, 1)')

            self._cron = FTCron(d.get('times'))
        return self


class StageMatchConf(object):
    """
    通用比赛配置解析.

    """
    def __init__(self, gameId, matchId):
        # 游戏ID
        self.gameId = gameId
        # 赛事ID
        self.matchId = matchId
        # 比赛名称
        self.name = None
        self.desc = None
        self.tableId = None
        self.seatId = None
        # 桌子座位数
        self.tableSeatCount = None
        # 开始配置
        self.startConf = None
        # 所有阶段
        self.stages = []
        # 报名费配置
        self.fees = None
        # 奖励配置
        self.rankRewardsList = None
        # 提示信息配置
        self.tipsConf = None
        self.recordId = None

    def decodeFromDict(self, d):
        self.name = d.get('name')
        if not isstring(self.name):
            raise TYBizConfException(d, 'StageMatchConf.name must be not empty string')
        self.desc = d.get('desc')
        # TODO 德州9人桌不满
        self.tableSeatCount = d.get('table.seat.count')
        if not isinstance(self.tableSeatCount, int) or self.tableSeatCount <= 0:
            raise TYBizConfException(d, 'StageMatchConf.table.seat.count must be int > 0')

        self.startConf = MatchStartConf().decodeFromDict(d.get('start'))

        self.stages = []
        for i, stageConfD in enumerate(d.get('stages')):
            stageConf = StageConf().decodeFromDict(stageConfD)
            stageConf.stageIndex = i
            self.stages.append(stageConf)

        self.fees = []
        fees = d.get('fees', [])
        for fee in fees:
            matchFee = MatchFee().decodeFromDict(fee)
            if matchFee.fee and matchFee.fee.count > 0:
                self.fees.append(matchFee)

        self.rankRewardsList = []
        rankRewardsList = d.get('rank.rewards', [])
        if not isinstance(rankRewardsList, list):
            raise TYBizConfException(d, 'StageMatchConf.rank.rewards must be list')
        for rankRewards in rankRewardsList:
            self.rankRewardsList.append(MatchRankRewards().decodeFromDict(rankRewards))

        self.tipsConf = d.get('tips', {})
        if not isinstance(self.tipsConf, dict):
            raise TYBizConfException(d, 'StageMatchConf.tips must be dict')

        self.recordId = self.matchId
        return self


class StageMatchRulesConf(TYConfable):
    def supportDelayEntry(self):
        return False


class StageMatchRulesConfASS(StageMatchRulesConf):
    TYPE_ID = 'ass'

    def __init__(self):
        super(StageMatchRulesConfASS, self).__init__()
        # 截止人数
        self.riseUserRefer = None
        # 积分增长时间，0表示不增长
        self.baseScoreGrowTimes = None
        # 积分增长器
        self.baseScoreGrowFactory = None
        # 淘汰分计算器
        self.loseScoreCalc = None

    def supportDelayEntry(self):
        return True

    def decodeFromDict(self, d):
        self.riseUserRefer = d.get('rise.user.refer')

        if not isinstance(self.riseUserRefer, int) or self.riseUserRefer <= 0:
            raise TYBizConfException(d, 'StageMatchRulesConfASS.rise.user.refer must be int > 0')

        self.baseScoreGrowTimes = d.get('score.base.grow.times')

        if not isinstance(self.baseScoreGrowTimes, int):
            raise TYBizConfException(d, 'StageMatchRulesConfASS.score.base.grow.times must be int >= 0')

        self.baseScoreGrowFactory = MatchBaseScoreGrowFactoryRegister().decodeFromDict(d.get('score.base.grow'))
        self.loseScoreCalc = MatchLoseScoreRegister().decodeFromDict(d.get('score.lose'))


class StageMatchRulesConfDieout(StageMatchRulesConf):
    TYPE_ID = 'dieout'

    def __init__(self):
        super(StageMatchRulesConfDieout, self).__init__()

    def decodeFromDict(self, d):
        return self


class StageMatchRulesConfRegister(TYConfableRegister):
    _typeid_clz_map = {
        StageMatchRulesConfASS.TYPE_ID: StageMatchRulesConfASS,
        StageMatchRulesConfDieout.TYPE_ID: StageMatchRulesConfDieout
    }

    def __init__(self):
        super(StageMatchRulesConfRegister, self).__init__()
        self._typeid_clz_map = StageMatchRulesConfRegister._typeid_clz_map