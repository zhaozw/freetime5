# -*- coding:utf-8 -*-
"""
Created on 2017年8月21日

@author: zhaojiangang
"""
import json
from sre_compile import isstring

import time
from datetime import datetime

import matchcomm.matchs.dao as daobase
from freetime5.util import ftlog
from freetime5.util import ftstr
from matchcomm.matchs.exceptions import MatchSigninFeeNotEnoughException
from matchcomm.matchs.utils import datetimeToTimestamp
from tuyoo5.core.tyconfig import TYBizConfException
from tuyoo5.core.typlugin import hallRpcOne
from tuyoo5.game.tycontent import TYContentItem


class MatchFee(object):
    def __init__(self, fee=None, params=None, desc=None):
        self.fee = fee
        self.params = params
        self.desc = desc

    def getParam(self, paramName, defVal=None):
        return self.params.get(paramName, defVal)

    @property
    def failure(self):
        return self.getParam('failure', '')

    @classmethod
    def decodeFromDict(cls, d):
        assetKindId = d.get('itemId')
        if not isstring(assetKindId):
            raise TYBizConfException(d, 'MatchFee.itemId must be string')
        count = d.get('count')
        if not isinstance(count, int):
            raise TYBizConfException(d, 'MatchFee.count must be int')
        params = d.get('params', {})
        if not isinstance(params, dict):
            raise TYBizConfException(d, 'MatchFee.params must be dict')
        desc = d.get('desc', {})
        if not isstring(desc):
            raise TYBizConfException(d, 'MatchFee.desc must be string')
        return MatchFee(TYContentItem(assetKindId, count), params, desc)


class MatchSigninFeeIF(object):
    def collectSigninFee(self, matchInst, userId, feeIndex, signinParams):
        """
        获取报名费
        @return: TYContentItem/None
        """
        pass

    def returnSigninFee(self, matchInst, userId, fee):
        """
        退还报名费
        """
        pass


class MatchSigninFeeIFDefaut(MatchSigninFeeIF):
    def collectSigninFee(self, matchInst, userId, feeIndex, signinParams):
        """
        收取用户报名费
        @return: TYContentItem/None
        """
        fee = None
        if matchInst.matchConf.fees:
            if feeIndex < 0 or feeIndex >= len(matchInst.matchConf.fees):
                feeIndex = 0
            matchFee = matchInst.matchConf.fees[feeIndex]
            if matchFee.fee:
                fee = matchFee.fee
                
                itemId, _ = hallRpcOne.hallitem.consumeAssets(userId,matchInst.gameId,
                                                      [{'itemId': fee.assetKindId, 'count': fee.count}],
                                                      'MATCH_SIGNIN_FEE', matchInst.matchId)
                if itemId:
                    raise MatchSigninFeeNotEnoughException(matchFee)
        return fee

    def returnSigninFee(self, matchInst, userId, fee):
        """
        退还报名费
        """
        hallRpcOne.hallitem.addAssets(userId,
                                      matchInst.gameId,
                                      [{'itemId': fee.assetKindId, 'count': fee.count}],
                                      'MATCH_RETURN_FEE',
                                      matchInst.matchId)


class MatchRankRewards(object):
    def __init__(self):
        self.conf = None
        self.rankRange = None
        self.rewards = None
        self.desc = None
        self.message = None

    def decodeFromDict(self, d):
        self.conf = d
        self.rankRange = d.get('rankRange')
        if not isinstance(self.rankRange, list) or len(self.rankRange) != 2:
            raise TYBizConfException(d, 'MatchRankRewards.rankRange must be [rankStart, rankStop]')

        if not isinstance(self.rankRange[0], int) or not isinstance(self.rankRange[1], int):
            raise TYBizConfException(d, 'MatchRankRewards.rankRange must be [int, int]')

        if self.rankRange[0] != -1 and self.rankRange[1] < self.rankRange[0]:
            raise TYBizConfException(d, 'MatchRankRewards.rankRange.rankStop must >= rankStart')

        self.desc = d.get('desc', '')
        if not isstring(self.desc):
            raise TYBizConfException(d, 'MatchRankRewards.desc must dict')

        self.message = d.get('message', '')
        if not isstring(self.message):
            raise TYBizConfException(d, 'MatchRankRewards.message must be string')

        self.rewards = []
        for reward in d.get('rewards'):
            if not isinstance(reward, dict):
                raise TYBizConfException(reward, 'reward item must dict')
            itemId = reward.get('itemId', None)
            if not isstring(itemId) or not itemId:
                raise TYBizConfException(reward, 'reward item.name must be not empty string')
            count = reward.get('count', None)
            if not isinstance(count, (int, float)) or count < 0:
                raise TYBizConfException('reward item.count must be int or float >= 0')
            if count > 0:
                self.rewards.append(reward)

        return self


class MatchRankRewardsIF(object):
    def getRankRewards(self, player):
        """
        获取奖励配置
        """
        pass

    def sendRankRewards(self, player, rankRewards):
        """
        发放比赛奖励
        """
        pass


class MatchSigninRecord(object):
    def __init__(self, userId):
        self.userId = userId
        self.signinTime = 0
        self.signinParams = None
        self.fee = None

    def toDict(self):
        return {
            'st': self.signinTime,
            'sp': self.signinParams,
            'fee': self.fee
        }

    def fromDict(self, d):
        self.signinTime = d['st']
        self.signinParams = d['sp']
        self.fee = d['fee']
        return self


class MatchSigninRecordDao(object):
    def save(self, gameId, matchId, instId, roomId, record):
        """
        记录报名记录
        """
        pass

    def loadAll(self, gameId, matchId, instId, roomId):
        """
        加载所有报名记录
        """
        pass

    def remove(self, gameId, matchId, instId, roomId, userId):
        """
        删除报名记录
        """
        pass

    def removeAll(self, gameId, matchId, instId, roomId):
        """
        删除所有报名记录
        """
        pass

    def saveRank(self, gameId, matchId, userId, rank):
        pass

    def loadUserAll(self, gameId, userId):
        """
        加载用户所有的报名
        """
        pass


class MatchSigninRecordDaoRedis(MatchSigninRecordDao):

    # def buildKey(self, gameId, matchId, instId, roomId):
    #     return 'msignin5:%s:%s:%s:%s' % (gameId, matchId, instId, roomId)
    #
    # def buildUserKey(self, userId):
    #     return 'usersignin5:%s' % (userId,)

    def save(self, gameId, matchId, instId, roomId, record):
        """
        记录报名记录
        """
        jstr = record.toDict()
        # daobase.executeMixCmd('hset', self.buildKey(gameId, matchId, instId, roomId), record.userId, jstr)
        daobase.saveMatchSigninRecord(gameId, matchId, instId, roomId,record.userId,jstr)
        # 记录用户的比赛报名数据,用于大厅我的比赛
        daobase.saveUserSigninRecord(record.userId, "%s|%s" % (gameId, matchId))

    def loadAll(self, gameId, matchId, instId, roomId):
        """
        加载所有报名记录
        """
        ret = []
        # datas = daobase.executeMixCmd('hgetall', self.buildKey(gameId, matchId, instId, roomId))
        # TODO
        # datas = daobase.loadMatchSigninRecord(gameId, matchId, instId, roomId)
        datas = []
        if datas:
            i = 0
            while (i + 1 < len(datas)):
                try:
                    userId = int(datas[i])
                    jstr = str(datas[i + 1])
                    d = json.loads(jstr)
                    record = MatchSigninRecord(userId).fromDict(d)
                    ret.append(record)
                except:
                    ftlog.error('MatchSigninRecordDaoRedis.loadAll',
                                'gameId=', gameId,
                                'matchId=', matchId,
                                'instId=', instId,
                                'roomId=', roomId,
                                'userId=', datas[i],
                                'data=', datas[i + 1])
                i += 2
        return ret

    def remove(self, gameId, matchId, instId, roomId, userId):
        """
        删除报名记录
        """
        ftlog.info('MatchSigninRecordDaoRedis.remove gameId=', gameId,
                    'userId=', userId,
                    'matchId=', matchId,
                    'instId=', instId,
                    'roomId=', roomId)
        # daobase.executeMixCmd('hdel', self.buildKey(gameId, matchId, instId, roomId), userId)
        # 删除用户的比赛报名数据
        daobase.removeMatchSigninRecord(gameId, matchId, instId, roomId, userId)
        daobase.removeUserSigninRecord(userId, "%s|%s" % (gameId, matchId))

    def removeAll(self, gameId, matchId, instId, roomId):
        """
        删除某个比赛某赛点的所有报名记录
        """
        ftlog.info('MatchSigninRecordDaoRedis.removeAll gameId=', gameId,
                   'matchId=', matchId,
                   'instId=', instId,
                   'roomId=', roomId)
        # datas = daobase.executeMixCmd('hgetall', self.buildKey(gameId, matchId, instId, roomId))
        datas = daobase.loadMatchSigninRecord(gameId, matchId, instId, roomId)
        if datas:
            i = 0
            while (i + 1 < len(datas)):
                try:
                    userId = int(datas[i])
                    ftlog.info('MatchSigninRecordDaoRedis.removeAll gameId=', gameId,
                               'matchId=', matchId,
                               'userId=', userId,
                               'instId=', instId,
                               'roomId=', roomId)
                    # 删除用户的比赛报名数据
                    daobase.removeUserSigninRecord(userId, "%s|%s" % (gameId, matchId))
                except:
                    ftlog.error('MatchSigninRecordDaoRedis.removeAll',
                                'gameId=', gameId,
                                'matchId=', matchId,
                                'instId=', instId,
                                'roomId=', roomId,
                                'userId=', datas[i],
                                'data=', datas[i + 1])
                i += 2
        # daobase.executeMixCmd('del', self.buildKey(gameId, matchId, instId, roomId))
        daobase.removeMatchSigninRecord(gameId, matchId, instId, roomId)


    def loadUserAll(self, userId, gameId=None):
        # 用户的所有比赛报名数据
        userMatchs = daobase.loadUserSigninRecord(userId)
        if gameId :
            # 某插件的比赛报名数据
            userGameMatchs = []
            for match in userMatchs:
                if match.startswith(str(gameId) + "|"):
                    userGameMatchs.append(match.split("|")[1])
            return userGameMatchs
        else:
            userAllMatchs = [match.split("|")[1] for match in userMatchs]
            return userAllMatchs


class MatchPlayerIF(object):
    def setPlayerActive(self, matchId, userId):
        """
        指定player为活动的Player
        @return: True/False
        """
        pass

    def savePlayer(self, matchId, userId, instId, roomId, state):
        """
        更新player信息
        """
        pass

    def removePlayer(self, matchId, instId, userId):
        """
        删除player信息
        """
        pass


class MatchPlayerInfo(object):
    def __init__(self, matchId, userId, instId=None, roomId=None, state=None):
        self.matchId = matchId
        self.userId = userId
        self.instId = instId
        self.roomId = roomId
        self.state = state

    def toDict(self):
        return {
            'instId': self.instId,
            'rid': self.roomId,
            'st': self.state
        }

    def fromDict(self, d):
        self.instId = d['instId']
        self.roomId = d['rid']
        self.state = d['st']
        return self


class MatchPlayerInfoDao(object):
    @classmethod
    def buildKey(cls, userId):
        return 'minfo2:%s' % (userId)

    @classmethod
    def save(cls, info):
        jstr = ftstr.dumps(info.toDict())
        # daobase.executeUserCmd(info.userId, 'hset', cls.buildKey(info.userId), info.matchId, jstr)
        daobase.saveMatchPlayerInfo(info.userId, info.matchId, jstr)

    @classmethod
    def load(cls, userId, matchId):
        # jstr = daobase.executeUserCmd(userId, 'hget', cls.buildKey(userId), matchId)
        jstr = daobase.getMatchPlayerInfo(userId, matchId)
        if jstr:
            d = ftstr.loads(jstr)
            return MatchPlayerInfo(matchId, userId).fromDict(d)
        return None

    @classmethod
    def remove(cls, userId, matchId):
        # daobase.executeUserCmd(userId, 'hdel', cls.buildKey(userId), matchId)
        daobase.removeMatchPlayerInfo(userId, matchId)

    @classmethod
    def loadAll(cls, userId):
        ret = {}
        # datas = daobase.executeUserCmd(userId, 'hgetall', cls.buildKey(userId))
        datas = daobase.loadMatchPlayerInfo(userId)
        if datas:
            i = 0
            while i + 1 < len(datas):
                try:
                    matchId = datas[i]
                    info = MatchPlayerInfo(matchId, userId).fromDict(datas[i + 1])
                    ret[matchId] = info
                except:
                    ftlog.error('MatchPlayerInfoDao.loadAll',
                                'userId=', userId,
                                'matchId=', datas[i],
                                'data=', datas[i + 1])
                i += 2
        return ret


class MatchPlayerIFDefault(MatchPlayerIF):
    def setPlayerActive(self, matchId, userId):
        """
        指定player为活动的Player
        @return: True/False
        """
        return True

    def savePlayer(self, matchId, userId, instId, roomId, state):
        # TODO 业务含义
        """
        更新player信息
        """
        MatchPlayerInfoDao.save(MatchPlayerInfo(matchId, userId, instId, roomId, state))

    def removePlayer(self, matchId, instId, userId):
        """
        删除player信息
        """
        info = MatchPlayerInfoDao.load(userId, matchId)
        if info and info.instId == instId:
            MatchPlayerInfoDao.remove(userId, matchId)


class MatchTableController(object):
    def startTable(self, table):
        """
        开始一局游戏
        """
        pass

    def clearTable(self, table):
        """
        清理桌子
        """
        pass

    def playerGiveUp(self, roomId, tableId, userId):
        """
        放弃比赛
        """
        pass


class MatchPlayerNotifier(object):

    def notifyMatchWait(self, player, reason):
        """
        通知玩家等待
        @param reason: MatchWaitReason 为什么等待
        """
        pass

    def notifyMatchCancelled(self, signer, reason):
        """
        通知玩家比赛取消了
        """
        pass

    def notifyMatchStart(self, instId, signers):
        """
        通知玩家比赛开始了
        """
        pass

    def notifyStageStart(self, player):
        """
        通知阶段开始
        """
        pass

    def notifyStageOver(self, player):
        """
        通知阶段结束
        """
        pass

    def notifyMatchOver(self, player, reason, rankRewards):
        """
        比赛结束
        """
        pass

    def notifyMatchRank(self, player):
        """
        比赛排行榜
        """
        pass

    def notifyMatchSignsUpdate(self, userId):
        """
        用户已经报名比赛列表
        """
        pass

    def notifyMatchUpdate(self,userId):
        """
        更新比赛信息.
        """
        pass


class MatchRecordDaoRedis(object):
    # TODO 历史记录 参考poker/entity/game/rooms/quick_upgrade_match_ctrl/game_record.py:89
    class Record(object):
        def __init__(self, bestRank, bestRankDate, isGroup, crownCount, playCount):
            assert(isinstance(bestRank, (int, float)) and bestRank >= 0)
            assert(isinstance(bestRankDate, int) and bestRankDate >= 0)
            assert(isinstance(isGroup, int) and isGroup >= 0)
            assert(isinstance(crownCount, int) and crownCount >= 0)
            assert(isinstance(playCount, int) and playCount >= 0)
            self.bestRank = int(bestRank)
            self.bestRankDate = bestRankDate
            self.isGroup = isGroup
            self.crownCount = crownCount
            self.playCount = playCount

        def update(self, rank, isGroup):
            if isGroup == 0 and self.isGroup == 1:
                self.bestRank = int(rank)
                self.bestRankDate = int(datetimeToTimestamp(datetime.now()))
                self.isGroup = 0
            elif isGroup == self.isGroup:
                if self.bestRank <= 0 or rank < self.bestRank:
                    self.bestRank = int(rank)
                    self.bestRankDate = int(datetimeToTimestamp(datetime.now()))
            if rank == 1 and self.isGroup == 0:
                self.crownCount += 1
            self.playCount += 1


        @classmethod
        def fromDict(cls, d):
            bestRank = d.get('bestRank', 0)
            bestRankDate = d.get('bestRankDate', 0)
            isGroup = d.get('isGroup', 1)
            crownCount = d.get('crownCount', 0)
            playCount = d.get('playCount', 0)
            if (not isinstance(bestRank, (int, float)) or
                not isinstance(crownCount, int) or
                not isinstance(playCount, int) or
                not isinstance(bestRankDate, int) or
                not isinstance(isGroup, int)):
                return None
            return MatchRecordDaoRedis.Record(int(bestRank), bestRankDate, isGroup, crownCount, playCount)

        def toDict(self):
            return {'bestRank':int(self.bestRank), 'bestRankDate': self.bestRankDate, 'isGroup':self.isGroup, 'crownCount':self.crownCount, 'playCount':self.playCount}

    @classmethod
    def initialize(cls, eventBus):
        # eventBus.subscribe(MatchWinloseEvent, cls.onMatchWinlose)
        pass

    @classmethod
    def updateAndSaveRecord(cls, event):
        if event['userId'] < 10000: # robot
            return
        record = cls.loadRecord(event['gameId'], event['userId'], event['matchId'], event.get('mixId'))
        if record is None:
            record = MatchRecordDaoRedis.Record(0, 0, 1, 0, 0)
        record.update(event['rank'], event['isGroup'])
        cls.saveRecord(event['gameId'], event['userId'], event['matchId'], record, event.get('mixId'))

    @classmethod
    def loadRecord(cls, gameId, userId, matchId, mixId=None):
        try:
            # jstr = gamedata.getGameAttr(userId, gameId, cls.__buildField(matchId, mixId))
            # TODO histories
            # pluginCross.halldata.getUpdateToVersion511flag(userId)
            jstr =""
            if ftlog.is_debug():
                ftlog.debug('MatchRecord.loadRecord gameId=', gameId,
                                      'userId=', userId,
                                      'matchId=', matchId,
                                      'data=', jstr,
                                      caller=cls)
            if jstr:
                return MatchRecordDaoRedis.Record.fromDict(json.loads(jstr))
        except:
            ftlog.exception()
        return None

    @classmethod
    def loadHistory(cls, gameId, userId, matchId):
        try:
            # jstr = gamedata.getGameAttr(userId, gameId, cls.__buildField(matchId,"histories"))
            jstr = ""
            if ftlog.is_debug():
                ftlog.debug('MatchRecord.loadRecord gameId=', gameId,
                            'userId=', userId,
                            'matchId=', matchId,
                            'data=', jstr,
                            caller=cls)
            if jstr:
                return json.loads(jstr)
            else:
                return []
        except:
            ftlog.exception()
        return None

    @classmethod
    def saveRecord(cls, gameId, userId, matchId, record, mixId=None):
        if ftlog.is_debug():
            ftlog.debug('MatchRecord.saveRecord gameId=', gameId,
                        'userId=', userId,
                        'matchId=', matchId,
                        'record=', json.dumps(record.toDict()),
                        'mixId=', mixId)
        # gamedata.setGameAttr(userId, gameId, cls.__buildField(matchId, mixId), json.dumps(record.toDict()))


    @classmethod
    def addHistory(cls, event):
        cls._saveUserHistory(event['gameId'], event['userId'], event['matchId'])
        cls._saveUserMatchHistory(event['gameId'], event['userId'], event['matchId'], event['rank'],
                                  event['desc'])

    @classmethod
    def __buildField(cls, matchId, mixId):
        if mixId is None:
            return 'm.%s' % (matchId)
        return 'm.%s.%s' % (matchId, mixId)

    @classmethod
    def _saveUserHistory(cls, gameId, userId, matchId):
        """
        记录通用比赛的比赛记录，用于大厅我的比赛(15个比赛)
        """
        rank_key = 'mhistory5:%s' % (userId,)
        # daobase.executeUserCmd(userId, 'RPUSH', rank_key, "%s|%s" % (gameId, matchId))
        daobase.saveUserMatchHistory(userId, "%s|%s" % (gameId, matchId))

    @classmethod
    def _saveUserMatchHistory(cls,gameId, userId, matchId, rank, desc):
        """
        比赛详情上历史成绩
        """
        hisories = cls.loadHistory(gameId, userId, matchId)
        if hisories is None:
            hisories = []
        hisories.append({"rank":rank,"time":int(time.time()),"desc":desc})
        # 保留5条记录
        if len(hisories) > 10 :
            hisories=hisories[-10:]
        if ftlog.is_debug():
            ftlog.debug('MatchRecord.addHistory gameId=', gameId,
                        'userId=', userId,
                        'matchId=', matchId,
                        'rank=', rank,
                        'desc=', desc)
        # gamedata.setGameAttr(userId, gameId, cls.__buildField(matchId, "histories"), json.dumps(hisories))