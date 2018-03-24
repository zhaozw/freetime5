# -*- coding:utf-8 -*-
"""
Created on 2017年8月14日

@author: zhaojiangang
"""

import time
from datetime import datetime

import matchcomm.matchs.dao as basedao
from freetime5.twisted import ftcore
from freetime5.twisted.ftlock import locked
from freetime5.util import ftlog
from freetime5.util import ftstr
from freetime5.util import fttime
from matchcomm.matchs.const import MatchFinishReason, MatchPlayerState
from matchcomm.matchs.exceptions import UserAlreadyInMatchException, \
    MatchSigninNotStartException, MatchSigninStoppedException, \
    MatchSigninFullException, BadMatchStateException, MatchStoppedException, MatchSigninException
from matchcomm.matchs.interface import MatchSigninRecord
from matchcomm.matchs.models import MatchPlayerData, MatchRiser, MatchSigner, StageMatchPlayer
from matchcomm.matchs.models import MatchRoomInfo
from matchcomm.matchs.report import PokerMatchReport
from matchcomm.matchs.stage_match.match_rules import StageMatchRulesFactory
from matchcomm.matchs.stage_match.match_status import StageMatchStatus
from matchcomm.matchs.utils import MatchProcesser, MatchGroupUtils, Logger, lockUserForMatch, unlockUserForMatch, \
    isRobot, checkUserLockForMatch
from matchcomm.util.keylock import KeyLock
from tuyoo5.game.tycontent import TYContentItem


class MatchInst(object):
    ST_IDLE = 0
    ST_LOAD = 1
    ST_SIGNIN = 2
    ST_PREPARE = 3
    ST_STARTING = 4
    ST_START = 5
    ST_FINAL = 6

    def __init__(self, area, instId, startTime, needLoad):
        # 赛区
        self.area = area
        # 比赛实例ID
        self.instId = instId
        # 开始时间
        self.startTime = startTime
        self.signinTimeStr = ''
        self.startTimeStr = ''
        if self.startTime:
            self.signinTimeStr = self.matchConf.startConf.buildSigninTimeStr()
            self.startTimeStr = datetime.fromtimestamp(startTime).strftime('%Y-%m-%d %H:%M')
        # 所有报名的玩家
        self._signerMap = {}
        # 状态
        self._state = self.ST_IDLE
        # 是否需要加载
        self._needLoad = needLoad
        # 玩家锁
        self._userLock = KeyLock()

        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('instId', self.instId)

    @property
    def gameId(self):
        return self.area.gameId

    @property
    def matchId(self):
        return self.area.matchId

    @property
    def roomId(self):
        return self.area.roomId

    @property
    def state(self):
        return self._state

    @property
    def matchConf(self):
        return self.area.matchConf

    @property
    def signerMap(self):
        return self._signerMap

    @property
    def signerCount(self):
        return len(self._signerMap)

    def findSigner(self, userId):
        return self._signerMap.get(userId)

    def getTotalSignerCount(self):
        if self.state < MatchInst.ST_START:
            return self.area.calcTotalSignerCount(self)
        return 0

    def buildStatus(self):
        return MatchInstStatus(self.instId, self._state, self.signerCount)

    @locked
    def load(self):
        if self._state == self.ST_IDLE:
            self._doLoad()
        else:
            self._logger.error('MatchInst.load fail',
                               'state=', self._state,
                               'err=', 'BadState')
            raise BadMatchStateException()

    @locked
    def final(self):
        if self._state < self.ST_FINAL:
            self._doFinal()
        else:
            self._logger.error('MatchInst.final fail',
                               'state=', self._state,
                               'err=', 'BadState')
            raise BadMatchStateException()

    @locked
    def cancel(self, reason):
        if self._state < self.ST_FINAL:
            self._doCancel(reason)
        else:
            self._logger.error('MatchInst.cancel fail',
                               'state=', self._state,
                               'err=', 'BadState')
            raise BadMatchStateException()

    @locked
    def cancelSigners(self, reason, userIds):
        if self._state < self.ST_FINAL:
            for userId in userIds:
                signer = self._signerMap.get(userId)
                if signer:
                    self._cancelSigner(signer, reason)
        else:
            self._logger.error('MatchInst.cancelSigners fail',
                               'reason=', reason,
                               'userCount=', len(userIds),
                               'state=', self._state,
                               'err=', 'BadState')
            raise BadMatchStateException()

    @locked
    def moveTo(self, toInstId, userIds):
        if self._state == self.ST_START:
            # TODO
            self._doMoveTo(toInstId, userIds)
        else:
            self._logger.error('MatchInst.moveTo fail',
                               'state=', self._state,
                               'toInstId=', toInstId,
                               'userIds=', userIds,
                               'err=', 'BadState')
            raise BadMatchStateException()

    @locked
    def startSignin(self):
        if self._state < self.ST_SIGNIN:
            self._doStartSignin()
        else:
            self._logger.error('MatchInst.startSignin fail',
                               'state=', self._state,
                               'err=', 'BadState')
            raise BadMatchStateException()

    @locked
    def prepare(self):
        if self._state < self.ST_PREPARE:
            self._doPrepare()
        else:
            self._logger.error('MatchInst.prepare fail',
                               'state=', self._state,
                               'err=', 'BadState')
            raise BadMatchStateException()

    @locked
    def start(self):
        if self._state < self.ST_STARTING:
            self._doStart()
        else:
            self._logger.error('MatchInst.start fail',
                               'state=', self._state,
                               'err=', 'BadState')
            raise BadMatchStateException()

    def enter(self, userId):
        with self._userLock.lock(userId):
            signer = self.findSigner(userId)
            if signer:
                self._enterNoLock(signer)

    def leave(self, userId):
        with self._userLock.lock(userId):
            signer = self.findSigner(userId)
            if signer:
                self._leaveNoLock(signer)

    def signin(self, userId, feeIndex, signinParams={}):
        """
        玩家报名
        """
        with self._userLock.lock(userId):
            return self._signinNoLock(userId, feeIndex, signinParams)

    def signout(self, userId):
        """
        玩家退赛
        """
        with self._userLock.lock(userId):
            signer = self.findSigner(userId)
            if signer:
                self._signoutNoLock(signer)
            else:
                self._logger.error('MatchInst.signout fail',
                                   'state=', self._state,
                                   'userId=', userId,
                                   'err=', 'not find signer')
                raise MatchSigninException(-1,u"玩家未报名")
            return signer

    def _enterNoLock(self, signer):
        if self._state in (self.ST_SIGNIN, self.ST_PREPARE):
            signer.isEnter = True
            self._fillSigner(signer)

            # bireport.matchUserEnter(self.gameId, self.roomId,
            #                         self.matchId, self.area.matchName,
            #                         instId=self.instId,
            #                         userId=signer.userId,
            #                         clientId=signer.clientId)

            self._logger.hinfo('MatchInst.enter ok',
                               'state=', self._state,
                               'userId=', signer.userId,
                               'clientId=', signer.clientId,
                               'signerCount=', self.signerCount)

    def _leaveNoLock(self, signer):
        if self._state in (self.ST_SIGNIN, self._state == self.ST_PREPARE):
            signer.isEnter = False
            signer.isLocked = False

            # bireport.matchUserLeave(self.gameId, self.roomId,
            #                         self.matchId, self.area.matchName,
            #                         instId=self.instId,
            #                         userId=signer.userId)

            ftlog.hinfo('MatchInst.leave ok',
                        'state=', self._state,
                        'userId=', signer.userId,
                        'clientId=', signer.clientId,
                        'signerCount=', self.signerCount)

    def _signinNoLock(self, userId, feeIndex, signinParams):
        self._ensureCanSignin(userId)

        signer = MatchSigner(userId, self.instId)
        signer.signinParams = signinParams
        signer.signinTime = time.time()
        signer.inst = self

        self._fillSigner(signer)

        # 收取报名费
        self._collectFee(signer, feeIndex)

        self._ensureCanSignin(userId)

        self._addSigner(signer)

        # bireport.matchUserSignin(self.gameId, self.roomId,
        #                          self.matchId, self.area.matchName,
        #                          instId=self.instId,
        #                          userId=userId,
        #                          clientId=signer.clientId)

        PokerMatchReport.reportMatchEvent('MATCH_SIGN_UP', userId,
                                          self.gameId,
                                          self.area.roomId,0,0,0)

        self._logger.hinfo('MatchInst.signin ok',
                           'state=', self._state,
                           'userId=', userId,
                           'clientId=', signer.clientId,
                           'signerCount=', self.signerCount,
                           'fee=', signer.fee.toDict() if signer.fee else None)

        return signer

    def _signoutNoLock(self, signer):
        """
        玩家退赛
        """
        # 退费
        self._unlockSigner(signer)
        self._returnFee(signer)
        self._removeSigner(signer)

        # bireport.matchUserSignout(self.gameId, self.area.roomId,
        #                           self.matchId, self.area.matchName,
        #                           instId=self.instId,
        #                           userId=signer.userId)

        PokerMatchReport.reportMatchEvent('MATCH_SIGN_OUT', signer.userId,
                                          self.gameId,
                                          self.area.roomId,0,0,0)

        self._logger.hinfo('MatchInst.signout ok',
                           'state=', self._state,
                           'userId=', signer.userId,
                           'signerCount=', self.signerCount,
                           'fee=', signer.fee.toDict() if signer.fee else None)

    def _doLoad(self):
        assert (self._state == self.ST_IDLE)

        self._logger.hinfo('MatchInst._doLoad ...',
                           'state=', self._state)

        self._state = self.ST_LOAD
        if self._needLoad:
            records = self.area.signinRecordDao.loadAll(self.gameId, self.matchId, self.instId, self.roomId)
            for record in records:
                signer = MatchSigner(record.userId, self.instId)
                signer.inst = self
                signer.signinTime = record.signinTime
                signer.signinParams = record.signinParams if record.signinParams is not None else {}
                if record.fee:
                    signer.fee = TYContentItem.decodeFromDict(record.fee)
                self._signerMap[signer.userId] = signer
                self._fillSigner(signer)

        self._logger.hinfo('MatchInst._doLoad ok',
                           'state=', self._state,
                           'signerCount=', self.signerCount)

    def _doFinal(self):
        assert (self._state < self.ST_FINAL)
        self._logger.info('MatchInst._doFinal ...',
                          'state=', self._state)

        self._state = self.ST_FINAL

        self._logger.info('MatchInst._doFinal ok',
                          'state=', self._state)

    # def _doMoveTo(self, toInstId, userIds):
    #     assert (self._state == MatchInst.ST_START)
    #     self._logger.info('MatchInst._doMoveTo ...',
    #                       'state=', self._state,
    #                       'toInstId=', toInstId,
    #                       'userIds=', userIds)
    #
    #     for userId in userIds:
    #         self.area.signIF.moveTo(userId, self.matchId, self.roomId, self.instId, toInstId)
    #     self._logger.info('MatchInst._doMoveTo ok',
    #                       'state=', self._state,
    #                       'toInstId=', toInstId,
    #                       'userIds=', userIds)

    def _doCancel(self, reason):
        assert (self._state < self.ST_FINAL)
        self._logger.info('MatchInst._doCancel ...',
                          'state=', self._state,
                          'reason=', reason)
        self._state = self.ST_FINAL

        for signer in self._signerMap.values()[:]:
            self._cancelSigner(signer, reason)

        self._logger.info('MatchInst._doCancel ok',
                          'state=', self._state,
                          'reason=', reason)

    def _doStartSignin(self):
        assert (self._state < self.ST_SIGNIN)

        self._logger.info('MatchInst._doStartSignin ...',
                          'state=', self._state)

        self._state = self.ST_SIGNIN

        self._logger.info('MatchInst._doStartSignin ok',
                          'state=', self._state)

    def _doPrepare(self):
        assert (self._state < self.ST_PREPARE)

        self._logger.info('MatchInst._doPrepare ...',
                          'state=', self._state,
                          'signerCount=', self.signerCount)

        startTime = time.time()
        self._state = self.ST_PREPARE

        nolocks = self._prelockSigners()
        self._kickoutSigners(nolocks)

        self._logger.info('MatchInst._doPrepare ok',
                          'state=', self._state,
                          'signerCount=', self.signerCount,
                          'usedTime=', time.time() - startTime)

    def _doStart(self):
        assert (self._state < self.ST_STARTING)
        self._logger.hinfo('MatchInst._doStart ...',
                           'state=', self._state,
                           'signerCount=', self.signerCount)

        self._state = self.ST_STARTING
        startTime = time.time()
        totalSignerCount = self.signerCount
        nolocks = self._lockSigners()
        self._kickoutSigners(nolocks)

        toKickSigners = []

        if self.matchConf.startConf.isTimingType():
            # 删除不能处理的（达到最大人数）玩家
            signers = sorted(self._signerMap.values(), key=lambda x: x.signinTime)
            toKickSigners = signers[self.matchConf.startConf.userMaxCountPerMatch:]
            for signer in toKickSigners:
                self._unlockSigner(signer)
                self._returnFee(signer)
                self._removeSigner(signer)
                self.area.playerNotifier.notifyMatchCancelled(signer, MatchFinishReason.RESOURCE_NOT_ENOUGH)



        # bireport.matchLockUser(self.area.gameId, self.area.roomId,
        #                        self.matchId, self.area.matchName,
        #                        instId=self.instId,
        #                        signinUserCount=totalSignerCount,
        #                        lockedUserCount=self.signerCount,
        #                        lockedUserIds=self._signerMap.keys())

        self._logger.hinfo('MatchInst._doStart lockOk',
                           'state=', self._state,
                           'signerCount=', self.signerCount,
                           'kickCount=', len(toKickSigners),
                           'usedTime=', time.time() - startTime)

        # TODO 跨进程时判断
        if self.matchConf.startConf.isTimingType() and totalSignerCount >= self.matchConf.startConf.userMinCount:
            self.area.playerNotifier.notifyMatchStart(self.instId, self._signerMap.values())

        self.area.signinRecordDao.removeAll(self.gameId, self.matchId, self.instId, self.roomId)
        self.area.onInstStarted(self)
        self._state = self.ST_START

        self._logger.hinfo('MatchInst._doStart ok',
                           'state=', self._state,
                           'signerCount=', self.signerCount,
                           'usedTime=', time.time() - startTime)


    def _kickoutSigners(self, signers):
        for signer in signers:
            del self._signerMap[signer.userId]

        # FTLoopTimer(0, 0, self._doKickoutSigners, signers).start()
        ftcore.runOnce(self._doKickoutSigners, signers)

    def _doKickoutSigners(self, signers):
        for signer in signers:
            self._kickoutSigner(signer)

    def _kickoutSigner(self, signer):
        try:
            self._unlockSigner(signer)
            self._returnFee(signer)
            self.area.playerNotifier.notifyMatchCancelled(signer, MatchFinishReason.NO_ENTER)
            # bireport.matchUserKickout(self.area.gameId, self.area.roomId,
            #                           self.matchId, self.area.matchName,
            #                           instId=self.instId,
            #                           userId=signer.userId,
            #                           kickoutReason='noenter')

            self._logger.info('MatchInst._kickoutSigner ok',
                              'userId=', signer.userId,
                              'kickoutReason=', 'noenter')
        except:
            self._logger.error('MatchInst._kickoutSigner fail',
                               'userId=', signer.userId)

    def _cancelSigner(self, signer, reason):
        try:
            self._unlockSigner(signer)
            self._returnFee(signer)
            self._removeSigner(signer)
            self.area.playerNotifier.notifyMatchCancelled(signer, reason)

            self._logger.info('MatchInst._cancelSigner ok',
                              'userId=', signer.userId,
                              'reason=', reason)
        except:
            self._logger.error('MatchInst._cancelSigner ERROR', signer.userId)

    def _prelockSigners(self):
        """
        先剔除未enter的玩家.
        """
        nolocks = []
        for signer in self._signerMap.values():
            if not isRobot(signer.userId) and not signer.isEnter:
                nolocks.append(signer)
        return nolocks

    def _lockSigners(self):
        """
        再剔除loc不为空的玩家.
        """
        nolocks = []
        for signer in self._signerMap.values():
            if not isRobot(signer.userId) and not self._lockSigner(signer):
                nolocks.append(signer)
        return nolocks

    def _lockSigner(self, signer):
        if checkUserLockForMatch(signer.userId) :
            signer.isLocked = True
            # 添加自己的锁定，防止其他游戏抢占
            lockUserForMatch(signer.userId, self.roomId)
        return signer.isLocked

    def _unlockSigner(self, signer):
        self.area.matchPlayerIF.removePlayer(self.matchId, self.instId, signer.userId)

    def _collectFee(self, signer, feeIndex):
        fee = self.area.matchSigninFeeIF.collectSigninFee(self, signer.userId, feeIndex, signer.signinParams)
        if fee:
            signer.fee = fee
            signer.feeIndex = feeIndex

    def _returnFee(self, signer):
        if signer.fee:
            self.area.matchSigninFeeIF.returnSigninFee(self, signer.userId, signer.fee)

    def _removeSigner(self, signer):
        del self._signerMap[signer.userId]
        self.area.matchPlayerIF.removePlayer(self.matchId, self.instId, signer.userId)
        self.area.signinRecordDao.remove(self.gameId, self.matchId, self.instId, self.roomId, signer.userId)

    def _addSigner(self, signer):
        self._signerMap[signer.userId] = signer

        record = MatchSigninRecord(signer.userId)
        record.signinTime = signer.signinTime
        if signer.fee:
            record.fee = {'itemId': signer.fee.assetKindId, 'count': signer.fee.count}
        self.area.matchPlayerIF.savePlayer(self.matchId, signer.userId, self.instId, self.roomId,
                                           MatchPlayerState.SIGNIN)
        self.area.signinRecordDao.save(self.gameId, self.matchId, self.instId, self.roomId, record)

    def _checkSigninCondition(self, userId):
        """
        检查玩家
        """
        pass

    def _ensureCanSignin(self, userId):
        # 报名还未开始
        if self._state < self.ST_SIGNIN:
            raise MatchSigninNotStartException()

        # 报名已经截止
        if self._state >= self.ST_PREPARE:
            raise MatchSigninStoppedException()

        signer = self.findSigner(userId)
        if signer:
            raise UserAlreadyInMatchException()

        # 检查报名人数是否已满
        if (self.matchConf.startConf.isTimingType()
            and self.signerCount >= self.matchConf.startConf.signinMaxCountPerMatch):
            raise MatchSigninFullException()

        self._checkSigninCondition(userId)

    def _fillSigner(self, signer):
        # count = hallRpcOne.hallitem.getAssets(userId, assetKindId).getResult()
        # userName, clientId = userdata.getAttrs(signer.userId, ['name', 'sessionClientId'])
        userName,clientId = "","" 
        signer.userName = ftstr.ensureString(userName)
        signer.clientId = ftstr.ensureString(clientId)


class MatchInstStub(object):
    def __init__(self, areaStub, instId, startTime, needLoad):
        # 赛区
        self.areaStub = areaStub
        # 实例ID
        self.instId = instId
        # 启动时间
        self.startTime = startTime
        # 是否需要加载
        self.needLoad = needLoad
        # 状态
        self._state = MatchInst.ST_IDLE
        # 所有报名
        self._signerMap = {}
        # 完成原因
        self._finishReason = MatchFinishReason.FINISH
        # 日志
        self._logger = Logger()
        self._logger.add('matchId', self.areaStub.matchId)
        self._logger.add('roomId', self.areaStub.roomId)
        self._logger.add('instId', instId)

    @property
    def roomId(self):
        return self.areaStub.roomId

    @property
    def matchId(self):
        return self.areaStub.matchId

    @property
    def master(self):
        return self.areaStub.master

    @property
    def state(self):
        return self._state

    @property
    def signerMap(self):
        return self._signerMap

    @property
    def signerCount(self):
        return len(self._signerMap)

    @property
    def finishReason(self):
        return self._finishReason

    def startSignin(self):
        """
        开始报名
        """
        self._logger.info('MatchInstStub.startSignin ...',
                          'state=', self._state)
        self._state = MatchInst.ST_SIGNIN
        try:
            self._doStartSignin()
            self._logger.info('MatchInstStub.startSignin ok',
                              'state=', self._state)
        except:
            self._logger.error('MatchInstStub.startSignin fail',
                               'state=', self._state)

    def prepare(self):
        """
        开始准备开赛
        """
        self._logger.info('MatchInstStub.prepare ...',
                          'state=', self._state)
        self._state = MatchInst.ST_PREPARE
        try:
            self._doPrepare()
            self._logger.info('MatchInstStub.prepare ok',
                              'state=', self._state)
        except:
            self._logger.info('MatchInstStub.prepare fail',
                              'state=', self._state)

    def cancel(self, reason):
        """
        取消比赛
        """
        assert (reason != MatchFinishReason.FINISH)
        self._logger.info('MatchInstStub.cancel ...',
                          'state=', self._state,
                          'reason=', reason)
        self._state = MatchInst.ST_FINAL
        self._finishReason = reason
        self._signerMap = {}
        try:
            self._doCancel()
            self._logger.info('MatchInstStub.cancel ok',
                              'state=', self._state,
                              'reason=', reason)
        except:
            self._logger.error('MatchInstStub.cancel fail',
                               'state=', self._state,
                               'reason=', reason)

    def cancelSigners(self, reason, signers):
        """
        取消比赛
        """
        assert (reason != MatchFinishReason.FINISH)
        self._logger.info('MatchInstStub.cancelSigners ...',
                          'state=', self._state,
                          'reason=', reason,
                          'signerCount=', len(signers))
        userIds = []
        for signer in signers:
            s = self._signerMap.get(signer.userId)
            if s:
                userIds.append(signer.userId)
        try:
            self._doCancelSigners(reason, userIds)
            self._logger.info('MatchInstStub.cancelSigners ok',
                              'state=', self._state,
                              'reason=', reason,
                              'signerCount=', len(signers))
        except:
            self._logger.info('MatchInstStub.cancelSigners fail',
                              'state=', self._state,
                              'reason=', reason,
                              'signerCount=', len(signers))

    def moveTo(self, toInstId, signers):
        self._logger.info('MatchInstStub.moveTo ...',
                          'state=', self._state,
                          'toInstId=', toInstId,
                          'signersCount=', len(signers))
        userIds = []
        for signer in signers:
            s = self._signerMap.get(signer.userId)
            if s:
                # TODO moveTo 待实现
                self._signerMap[signer.userId]
                userIds.append(signer.userId)
        self._doMoveTo(toInstId, userIds)
        self._logger.info('MatchInstStub.moveTo ok',
                          'state=', self._state,
                          'toInstId=', toInstId,
                          'signersCount=', len(signers))

    def start(self):
        """
        开始比赛
        """
        self._logger.info('MatchInstStub.start ...',
                          'state=', self._state)
        self._state = MatchInst.ST_STARTING
        try:
            self._doStart()
            self._logger.info('MatchInstStub.start ok',
                              'state=', self._state)
        except:
            self._logger.error('MatchInstStub.start fail',
                               'state=', self._state)

    def onSignin(self, signers):
        """
        主对象汇报报名列表
        """
        if (self._state >= MatchInst.ST_SIGNIN
            and self._state < MatchInst.ST_START):
            self._logger.info('MatchInstStub.onSignin ...',
                              'state=', self._state,
                              'signerCount=', len(signers))
            if self._logger.isDebug():
                self._logger.debug('MatchInstStub.onSignin ...',
                                   'state=', self._state,
                                   'signers=', [s.userId for s in signers])
            for signer in signers:
                # TODO 玩家是否上线
                self._signerMap[signer.userId] = signer
            self._logger.info('MatchInstStub.onSignin ok',
                              'state=', self._state,
                              'signerCount=', len(signers))
        else:
            self._logger.error('MatchInstStub.onSignin fail',
                               'state=', self._state,
                               'err=', 'BadState')

    def onStart(self):
        """
        赛区中的实例启动完成
        """
        if self._state == MatchInst.ST_STARTING:
            self._state = MatchInst.ST_START
            self._logger.info('MatchInstStub.onStart ok',
                              'state=', self._state)
        else:
            self._logger.error('MatchInstStub.onStart fail',
                               'state=', self._state,
                               'err=', 'BadState')

    def _doCancelSigners(self, reason, userIds):
        raise NotImplementedError

    def _doMoveTo(self, toInstId, userIds):
        raise NotImplementedError

    def _doStartSignin(self):
        raise NotImplementedError

    def _doPrepare(self):
        raise NotImplementedError

    def _doCancel(self):
        raise NotImplementedError

    def _doStart(self):
        raise NotImplementedError


class MatchInstStubLocal(MatchInstStub):
    def __init__(self, areaStub, instId, startTime, needLoad, inst):
        super(MatchInstStubLocal, self).__init__(areaStub, instId, startTime, needLoad)
        self.inst = inst

    def _doCancelSigners(self, reason, userIds):
        try:
            self.inst.cancelSigners(reason, userIds)
        except:
            self._logger.error('MatchInstStubLocal._doMoveTo fail',
                               'reason=', reason,
                               'userIds=', userIds)

    def _doMoveTo(self, toInstId, userIds):
        try:
            self.inst.moveTo(toInstId, userIds)
        except:
            self._logger.error('MatchInstStubLocal._doMoveTo fail',
                               'toInstId=', toInstId,
                               'userIds=', userIds)

    def _doStartSignin(self):
        try:
            self.inst.startSignin()
        except:
            self._logger.error('MatchInstStubLocal._doStartSignin fail')

    def _doPrepare(self):
        try:
            self.inst.prepare()
        except:
            self._logger.error('MatchInstStubLocal._doPrepare fail')

    def _doCancel(self):
        try:
            self.inst.cancel(self._finishReason)
        except:
            self._logger.error('MatchInstStubLocal._doCancel fail')

    def _doStart(self):
        try:
            self.inst.start()
        except:
            self._logger.error('MatchInstStubLocal._doStart fail')


class MatchGroup(object):
    ST_INIT = 0
    ST_STARTING = 1
    ST_START = 2
    ST_FINISHING = 3
    ST_FINISH = 4
    ST_FINAL = 5

    def __init__(self, area, instId, matchingId, groupId,
                 groupName, isGrouping, stageIndex, totalPlayerCount, startStageIndex):
        # 所在赛区
        self.area = area
        # 比赛实例ID
        self.instId = instId
        # 比赛ID
        self.matchingId = matchingId
        # 分组ID
        self.groupId = groupId
        # 分组名称
        self.groupName = groupName
        # 是否分组赛
        self.isGrouping = isGrouping
        # 阶段index
        self.stageIndex = stageIndex
        # 比赛开始阶段
        self.startStageIndex = startStageIndex
        # 比赛结束阶段
        self.endStageIndex = len(area.matchConf.stages)-1
        # 阶段配置
        self.stageConf = area.matchConf.stages[stageIndex]
        # 总人数
        self.totalPlayerCount = totalPlayerCount
        # 本组开始时的人数
        self._startPlayerCount = 0
        # 开始时间
        self._startTime = None
        # 最后活跃时间
        self._lastActiveTime = None
        # 当前分组所有玩家
        self._playerMap = {}
        # 所有桌子
        self._allTableMap = {}
        self._idleTableList = []
        # 心跳
        self._heartbeat = MatchProcesser(1, self._doHeartbeat)
        # 赛制
        self._matchRules = StageMatchRulesFactory.newMatchRules(self)
        # 状态
        self._state = self.ST_INIT
        # 结束原因
        self._finishReason = MatchFinishReason.FINISH
        # 晋级玩家列表
        self._riseList = []
        # 日志
        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('instId', self.instId)
        self._logger.add('matchingId', self.matchingId)
        self._logger.add('groupId', self.groupId)
        self._logger.add('stageIndex', self.stageIndex)
        self._logger.add('startStageIndex', self.startStageIndex)

    @property
    def gameId(self):
        return self.area.gameId

    @property
    def matchId(self):
        return self.area.matchId

    @property
    def roomId(self):
        return self.area.roomId

    @property
    def matchConf(self):
        return self.area.matchConf

    @property
    def playerCount(self):
        return len(self._playerMap)

    @property
    def finishReason(self):
        return self._finishReason

    @property
    def rankList(self):
        return self._matchRules.getRankList()

    @property
    def riseList(self):
        return self._riseList

    @property
    def state(self):
        return self._state

    @property
    def startTime(self):
        return self._startTime

    @property
    def lastActiveTime(self):
        return self._lastActiveTime

    @property
    def startPlayerCount(self):
        return self._startPlayerCount

    @property
    def matchRules(self):
        return self._matchRules

    def addPlayer(self, playerData):
        player = self._matchRules.newPlayer(playerData)
        assert (isinstance(player, StageMatchPlayer))
        player.userName = playerData.userName
        player.signinTime = playerData.signinTime
        player.feeIndex = playerData.feeIndex
        player.clientId = playerData.clientId
        player.score = playerData.score
        player.rank = playerData.rank
        player.tableRank = playerData.tableRank
        # 缺少人手，已经退出的玩家持续晋级
        player.isQuit = playerData.isQuit if hasattr(playerData, 'isQuit') else False
        player.group = self
        player.instId = self.instId
        # 添加断线重连标示位
        if not player.isQuit:
            lockUserForMatch(player.userId, self.roomId)
        self._playerMap[player.userId] = player


    def removePlayer(self,player):
        assert (isinstance(player, StageMatchPlayer))
        # 移除断线重连标示位
        unlockUserForMatch(player.userId, self.roomId)
        self._playerMap.pop(player.userId)


    def findPlayer(self, userId):
        return self._playerMap.get(userId)

    def calcUncompleteTableCount(self):
        return self._matchRules.getUncompleteTableCount()

    def calcTotalUncompleteTableCount(self):
        return self.area.calcTotalUncompleteTableCount(self)

    def calcRemTimes(self, timestamp=None):
        # TODO
        return 0

    def calcTotalRemTimes(self, timestamp):
        return self.area.calcTotalRemTimes(self)

    def buildStatus(self):
        return MatchGroupStatus(self.groupId, self.matchingId, self._state,
                                self.calcUncompleteTableCount(),
                                self.calcRemTimes(),
                                self._lastActiveTime,
                                self.playerCount)

    def start(self):
        self._logger.info('MatchGroup.start ...',
                          'state=', self._state)

        self._startTime = fttime.getCurrentTimestamp()
        self._lastActiveTime = self._startTime
        self._startPlayerCount = len(self._playerMap)

        self._heartbeat.start()

        self._logger.info('MatchGroup.start ok',
                          'state=', self._state)

    def kill(self, reason):
        self._logger.info('MatchGroup.kill ...',
                          'state=', self._state,
                          'reason=', reason)

        self._heartbeat.postCall(self._doFinish, reason)

        self._logger.info('MatchGroup.kill ok',
                          'state=', self._state,
                          'reason=', reason)

    def final(self):
        self._logger.info('MatchGroup.final ...',
                          'state=', self._state)

        self._heartbeat.postCall(self._doFinal)

        self._logger.info('MatchGroup.final ok',
                          'state=', self._state)

    def tableWinlose(self, tableId, ccrc, seatWinloses, isKill=False):
        self._matchRules.tableWinlose(tableId, ccrc, seatWinloses, isKill)

    def borrowTable(self):
        assert (self._idleTableList)
        table = self._idleTableList[0]
        self._idleTableList.pop(0)

        self._logger.info('MatchGroup.borrowTable',
                          'tableId=', table.tableId,
                          'idleTableCount=', len(self._idleTableList))

        return table

    def backTable(self, table):
        assert (table.idleSeatCount == table.seatCount)
        self._idleTableList.append(table)
        self._logger.info('MatchGroup.backTable',
                          'tableId=', table.tableId,
                          'idleTableCount=', len(self._idleTableList))

    def playerMatchOver(self, player, reason):
        """
        玩家在比赛中over了
        """
        self.removePlayer(player)

        # 解锁玩家
        rankRewards = None

        if reason == MatchFinishReason.FINISH or reason == MatchFinishReason.GIVE_UP:
            rankRewards = self.area.matchRankRewardsIF.getRankRewards(player)
            if rankRewards:
                self._sendRankRewards(player, rankRewards)

        self._logger.hinfo('UserMatchOver',
                           'userId=', player.userId,
                           'score=', player.score,
                           'rank=', player.rank,
                           'reason=', reason,
                           'rankRewards=', rankRewards.rewards if rankRewards else None,
                           'remUserCount=', len(self._playerMap),
                           'cardCount=', player.cardCount)

        self.area.matchPlayerIF.removePlayer(self.matchId, self.instId, player.userId)
        self.area.playerNotifier.notifyMatchOver(player, reason, rankRewards)

    def _sendRankRewards(self, player, rankRewards):
        self.area.matchRankRewardsIF.sendRankRewards(player, rankRewards)

        sequence = int(player.group.instId.split('.')[1])
        # for reward in rankRewards.rewards:
        #     chipType = MatchBIUtils.getBiChipType(reward['itemId'])
        #     if chipType:
        #         kindId = 0
        #         if chipType == tyconst.CHIP_TYPE_ITEM:
        #             kindId = reward['itemId'].strip('item:')
                # MatchBIUtils.reportGameEvent(player.group.gameId, 'MATCH_REWARD', player.userId, player.clientId,
                #                              player.group.matchId, 0, sequence, 0, 0, 0,
                #                              [chipType, reward['count'], kindId, player.rank, 0], tag='match_reward')

    def _initResources(self):
        needTableCount = self._matchRules.calcNeedTableCount()
        if self.area.tableManager.idleTableCount < needTableCount:
            # 桌子资源不足
            return False

        # 借桌子
        self._idleTableList = self.area.tableManager.borrowTables(needTableCount)
        self._allTableMap = {table.tableId: table for table in self._idleTableList}
        return True

    def _releaseResources(self):
        if len(self._idleTableList) != len(self._allTableMap):
            assert (len(self._idleTableList) == len(self._allTableMap))
        self.area.tableManager.returnTables(self._allTableMap.values())
        self._idleTableList = []
        self._allTableMap = {}

    def _doStart(self):
        assert (self._state == self.ST_INIT)

        self._logger.hinfo('MatchGroup._doStart ...',
                           'state=', self._state,
                           'userCount=', self.playerCount)

        self._state = self.ST_STARTING

        # 检查玩家数量
        if self.playerCount < self.matchConf.tableSeatCount:
            # 人数不足
            self._logger.hinfo('MatchGroup._doStart fail',
                               'state=', self._state,
                               'userCount=', self.playerCount,
                               'err=', 'NotEnoughUser')
            self._doFinish(MatchFinishReason.USER_NOT_ENOUGH)
            return

        # 初始化资源
        if not self._initResources():
            self._logger.hinfo('MatchGroup._doStart fail',
                               'state=', self._state,
                               'userCount=', self.playerCount,
                               'idleTableCount=', self.area.tableManager.idleTableCount,
                               'err=', 'NotEnoughTable')
            self._doFinish(MatchFinishReason.RESOURCE_NOT_ENOUGH)
            return

        # 初始化赛制
        self._matchRules.init()

        self._logger.hinfo('MatchGroup._doStart ok',
                           'state=', self._state,
                           'userCount=', self.playerCount)

        self._state = self.ST_START

    def _doFinish(self, reason):
        """
        结束该分组
        """
        self._logger.hinfo('MatchGroup._doFinish ...',
                           'state=', self._state,
                           'reason=', reason)

        self._state = self.ST_FINISHING
        self._finishReason = reason
        self._releaseResources()

        if reason == MatchFinishReason.FINISH:
            self._riseList = self._matchRules.getRankList()[:]
            riseUserCount = min(self.stageConf.riseUserCount, len(self._riseList))
            self._matchRules.cleanup()
            # TODO 跨进程分组排名
            if len(self._idleTableList) != len(self._allTableMap):
                self._logger.error('MatchGroup._doFinish issue',
                                   'state=', self._state,
                                   'err=', 'HaveBusyTable')

            while len(self._riseList) > riseUserCount:
                player = self._riseList.pop(-1)
                self.playerMatchOver(player, MatchFinishReason.FINISH)

            if self.stageIndex + 1 >= len(self.matchConf.stages):
                # 最后一个阶段, 给晋级的人发奖
                while self._riseList:
                    player = self._riseList.pop(-1)
                    self.playerMatchOver(player, MatchFinishReason.FINISH)
        else:
            self._riseList = []
            rankList = self._matchRules.getRankList()
            self._matchRules.cleanup()

            while rankList:
                player = rankList.pop(-1)
                self.playerMatchOver(player, reason)

        self.area.masterStub.areaGroupFinish(self.area, self)
        self._state = self.ST_FINISH

        self._logger.hinfo('MatchGroup._doFinish ok',
                           'state=', self._state,
                           'reason=', reason)

    def _doKill(self, reason):
        if self._state < MatchGroup.ST_FINISH:
            self._doFinish(reason)
            self._logger.info('MatchGroup._doKill ok',
                              'state=', self._state,
                              'reason=', reason)
        else:
            self._logger.warn('MatchGroup._doKill fail',
                              'state=', self._state,
                              'reason=', reason,
                              'err=', 'BadState')

    def _doFinal(self):
        if self._state == MatchGroup.ST_FINISH:
            self._heartbeat.stop()
            self._state = MatchGroup.ST_FINAL
            self._logger.info('MatchGroup._doFinal ok',
                              'state=', self._state)
        else:
            self._logger.warn('MatchGroup._doFinal fail',
                              'state=', self._state,
                              'err=', 'BadState')

    def _doHeartbeat(self):
        if self._logger.isDebug():
            self._logger.debug('MatchGroup._doHeartbeat',
                               'state=', self._state)

        self._lastActiveTime = fttime.getCurrentTimestamp()

        if self._state == self.ST_INIT:
            self._doStart()

        if self._state == self.ST_START:
            self._reclaimTables()
            if self._matchRules.isFinished():
                # 结束了
                self._doFinish(MatchFinishReason.FINISH)

        if self._state == self.ST_FINISH:
            self._doFinal()

        if self._state < MatchGroup.ST_FINISH:
            timestamp = fttime.getCurrentTimestamp()
            if timestamp - self._startTime > self.matchConf.startConf.maxPlayTime:
                self._doFinish(MatchFinishReason.TIMEOUT)

        return 2

    def _reclaimTables(self):
        needCount = self._matchRules.calcNeedTableCount()
        reclaimCount = len(self._allTableMap) - needCount
        if self._logger.isDebug():
            self._logger.debug('MatchGroup._reclaimTables',
                               'needCount=', needCount,
                               'reclaimCount=', reclaimCount,
                               'allCount=', len(self._allTableMap),
                               'idleCount=', len(self._idleTableList),
                               'tableManager.idleCount=', self.area.tableManager.idleTableCount)

        if reclaimCount > 0:
            count = min(reclaimCount, len(self._idleTableList))
            tables = self._idleTableList[0:count]
            self._idleTableList = self._idleTableList[count:]
            self.area.tableManager.returnTables(tables)
            for table in tables:
                del self._allTableMap[table.tableId]
            self._logger.info('MatchGroup._reclaimTables',
                              'needCount=', needCount,
                              'reclaimCount=', reclaimCount,
                              'realReclaimCount=', count,
                              'allCount=', len(self._allTableMap),
                              'idleCount=', len(self._idleTableList),
                              'tableManager.idleCount=', self.area.tableManager.idleTableCount)


class MatchGroupStub(object):
    """
    比赛分组控制对象，运行于主控进程，用与控制相应的分组
    """
    ACTIVE_TIME_COUNT = 5

    def __init__(self, areaStub, stage, groupId,
                 groupName, playerList, isGrouping,
                 totalPlayerCount, startStageIndex):
        # 赛区控制对象
        self.areaStub = areaStub
        # 当前阶段
        self.stage = stage
        # 分组ID
        self.groupId = groupId
        # 分组名称
        self.groupName = groupName
        # 是否分组
        self.isGrouping = isGrouping
        # 开赛总人数
        self.totalPlayerCount = totalPlayerCount
        self.startStageIndex = startStageIndex
        # 玩家map
        self._playerMap = {p.userId: p for p in playerList}
        # 晋级的玩家
        self._risePlayerSet = set()
        # 状态
        self._state = MatchGroup.ST_INIT
        # 完成原因
        self._finishReason = MatchFinishReason.FINISH
        # 开始时间
        self._startTime = None
        # group状态
        self._status = None
        # 最后心跳时间
        self._lastGroupHeartbeatTime = None
        # 心跳
        self._heartbeat = MatchProcesser(0, self._doHeartbeat)

        # 日志
        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('matchingId', self.matchingId)
        self._logger.add('roomId', self.roomId)
        self._logger.add('stageIndex', self.stageIndex)
        self._logger.add('groupId', self.groupId)

    @property
    def instId(self):
        return self.stage.instId

    @property
    def roomId(self):
        return self.areaStub.roomId

    @property
    def master(self):
        return self.areaStub.master

    @property
    def playerMap(self):
        return self._playerMap

    @property
    def playerCount(self):
        return len(self._playerMap)

    @property
    def matchId(self):
        return self.stage.matchId

    @property
    def matchingId(self):
        return self.stage.matchingId

    @property
    def stageIndex(self):
        return self.stage.stageIndex

    @property
    def risePlayerSet(self):
        return self._risePlayerSet

    @property
    def finishReason(self):
        return self._finishReason

    @property
    def state(self):
        return self._state

    def buildStatus(self):
        return self._status

    def start(self):
        assert (self._state == MatchGroup.ST_INIT)

        ftlog.info('MatchGroupStub.start ...',
                   'matchId=', self.matchId,
                   'matchingId=', self.matchingId,
                   'roomId=', self.roomId,
                   'stageIndex=', self.stageIndex,
                   'groupId=', self.groupId,
                   'state=', self._state)

        self._state = MatchGroup.ST_STARTING
        self._startTime = fttime.getCurrentTimestamp()
        self._lastGroupHeartbeatTime = self._startTime

        self._heartbeat.start()

        ftlog.info('MatchGroupStub.start ok',
                   'matchId=', self.matchId,
                   'matchingId=', self.matchingId,
                   'roomId=', self.roomId,
                   'stageIndex=', self.stageIndex,
                   'groupId=', self.groupId,
                   'state=', self._state)

    def kill(self, reason):
        """
        强制杀掉该分组
        """
        assert (reason != MatchFinishReason.FINISH)
        ftlog.info('MatchGroupStub.kill ...',
                   'matchId=', self.matchId,
                   'matchingId=', self.matchingId,
                   'roomId=', self.roomId,
                   'stageIndex=', self.stageIndex,
                   'groupId=', self.groupId,
                   'state=', self._state)

        self._logger.info('MatchGroupStub.kill ...',
                          'state=', self._state)
        self._heartbeat.postCall(self._doKill, reason)
        self._logger.info('MatchGroupStub.kill ok',
                          'state=', self._state)

    def final(self):
        assert(self._state < MatchGroup.ST_FINAL)
        self._logger.info('MatchGroupStub.final ...',
                          'state=', self._state)
        self._heartbeat.postCall(self._doFinal)
        self._logger.info('MatchGroupStub.final ok',
                          'state=', self._state)

    def onGroupHeartbeat(self, status):
        """
        分组心跳
        """
        self._logger.info('MatchGroupStub.onGroupHeartbeat',
                          'state=', self._state,
                          'groupTimestamp=', status.timestamp,
                          'lastActiveTime=', status.lastActiveTime)
        self._lastGroupHeartbeatTime = fttime.getCurrentTimestamp()
        self._status = status

    def onGroupRisePlayer(self, riser):
        player = self.playerMap.get(riser.userId)
        if player:
            player.score = riser.score
            player.rank = riser.rank
            self.risePlayerSet.add(player)
            ftlog.info('MatchGroupStub.onGroupRisePlayer ok',
                       'matchId=', self.matchId,
                       'instId=', self.instId,
                       'matchingId=', self.matchingId,
                       'groupId=', self.groupId,
                       'state=', self.state,
                       'userId=', riser.userId,
                       'score=', riser.score,
                       'rank=', riser.rank)
            return True
        return False

    def onGroupFinish(self, reason):
        self._heartbeat.postCall(self._doFinish, reason)

    def _doStart(self):
        self._state = MatchGroup.ST_START
        self._lastGroupHeartbeatTime = fttime.getCurrentTimestamp()
        self._doStartGroup()

        ftlog.info('MatchGroupStub._doStart ok',
                   'matchId=', self.matchId,
                   'instId=', self.instId,
                   'matchingId=', self.matchingId,
                   'groupId=', self.groupId,
                   'state=', self.state)

    def _doKill(self, reason):
        if self.state < MatchGroup.ST_FINISH:
            self._state = MatchGroup.ST_FINISH
            self._finishReason = reason

            # bireport.matchGroupFinish(self.master.gameId, self.master.roomId, self.matchId, self.master.matchName,
            #                           areaRoomId=self.roomId,
            #                           instId=self.instId,
            #                           matchingId=self.matchingId,
            #                           stageIndex=self.stageIndex,
            #                           groupId=self.groupId,
            #                           reason=reason,
            #                           isKill=True)

            sequence = int(self.instId.split('.')[1])
            groupNum = self.groupId.split('.')[-1]
            cardList = [self.stageIndex, groupNum, reason, 1]
            playerList = self.playerMap.values()
            PokerMatchReport.reportMatchEvent('MATCH_GROUP_FINISH', playerList[0].userId if playerList else 0, self.master.gameId,
                                 self.master.roomId, 0, sequence, 0, cardList)

            if self._status:
                self._status.uncompleteTableCount = 0
                self._status.remTimes = 0
                self._status.state = MatchGroup.ST_FINISH

            try:
                self._doKillGroup(reason)
                ftlog.info('MatchGroupStub._doKillGroup ok',
                           'matchId=', self.matchId,
                           'instId=', self.instId,
                           'matchingId=', self.matchingId,
                           'groupId=', self.groupId,
                           'state=', self.state,
                           'finishReason=', reason)
            except:
                ftlog.error('MatchGroupStub._doKillGroup Exception',
                            'matchId=', self.matchId,
                            'instId=', self.instId,
                            'matchingId=', self.matchingId,
                            'groupId=', self.groupId,
                            'state=', self.state,
                            'finishReason=', reason)

    def _doFinish(self, reason):
        if self.state < MatchGroup.ST_FINISH:
            self._state = MatchGroup.ST_FINISH
            self._finishReason = reason

            ftlog.info('MatchGroupStub._doFinish ok',
                       'matchId=', self.matchId,
                       'instId=', self.instId,
                       'matchingId=', self.matchingId,
                       'groupId=', self.groupId,
                       'state=', self.state,
                       'finishReason=', reason)

    def _doFinal(self):
        if self.state < MatchGroup.ST_FINAL:
            self._state = MatchGroup.ST_FINAL
            self._heartbeat.stop()
            try:
                self._doFinalGroup()
                ftlog.info('MatchGroupStub._doFinal ok',
                           'matchId=', self.matchId,
                           'instId=', self.instId,
                           'matchingId=', self.matchingId,
                           'groupId=', self.groupId,
                           'state=', self.state)
            except:
                ftlog.error('MatchGroupStub._doFinal Exception',
                            'matchId=', self.matchId,
                            'instId=', self.instId,
                            'matchingId=', self.matchingId,
                            'groupId=', self.groupId,
                            'state=', self.state)
        else:
            ftlog.warn('MatchGroupStub._doFinal BadState',
                       'matchId=', self.matchId,
                       'instId=', self.instId,
                       'matchingId=', self.matchingId,
                       'groupId=', self.groupId,
                       'state=', self.state)

    def _doHeartbeat(self):
        if self.state < MatchGroup.ST_START:
            self._doStart()

        if self.state < MatchGroup.ST_FINISHING:
            if self._isActiveTimeout():
                ftlog.info('MatchGroupStub._doHeartbeat ActiveTimeout',
                           'matchId=', self.matchId,
                           'instId=', self.instId,
                           'matchingId=', self.matchingId,
                           'groupId=', self.groupId,
                           'state=', self.state)
                try:
                    self._doKill(MatchFinishReason.TIMEOUT)
                except:
                    ftlog.error('MatchGroupStub._doHeartbeat',
                                'matchId=', self.matchId,
                                'instId=', self.instId,
                                'matchingId=', self.matchingId,
                                'groupId=', self.groupId,
                                'state=', self.state)
        return 1

    def _isActiveTimeout(self):
        delta = max(0, fttime.getCurrentTimestamp() - self._lastGroupHeartbeatTime)
        if self._status and self._status.lastActiveTime:
            delta += max(0, self._status.timestamp - self._status.lastActiveTime)
        if ftlog.is_debug():
            ftlog.debug('MatchGroupStub._isActiveTimeout',
                        'lastGroupHeartbeatTime=', self._lastGroupHeartbeatTime,
                        'lastActiveTime=', self._status.lastActiveTime if self._status else None,
                        'delta=', delta,
                        'limit=', MatchArea.HEARTBEAT_TO_MASTER_INTERVAL * self.ACTIVE_TIME_COUNT)
        return delta >= MatchArea.HEARTBEAT_TO_MASTER_INTERVAL * self.ACTIVE_TIME_COUNT

    def _doStartGroup(self):
        raise NotImplementedError

    def _doKillGroup(self, reason):
        raise NotImplementedError

    def _doFinalGroup(self):
        raise NotImplementedError


class MatchGroupStubLocal(MatchGroupStub):
    """
    比赛分组控制对象，运行于主控进程
    """

    def __init__(self, areaStub, stage, groupId,
                 groupName, playerList, isGrouping, totalPlayerCount, area, startStageIndex):
        super(MatchGroupStubLocal, self).__init__(areaStub, stage, groupId,
                                                  groupName, playerList, isGrouping,
                                                  totalPlayerCount, startStageIndex)
        self.area = area

    def _doStartGroup(self):
        ftlog.info('MatchGroupStubLocal._doStartGroup',
                   'matchId=', self.matchId,
                   'instId=', self.instId,
                   'matchingId=', self.matchingId,
                   'stageIndex=', self.stageIndex,
                   'isGrouping=', self.isGrouping,
                   'groupId=', self.groupId,
                   'groupName=', self.groupName)
        group = self.area.createGroup(self.instId, self.matchingId, self.groupId,
                                      self.groupName, self.stageIndex, self.isGrouping,
                                      self.totalPlayerCount, self.startStageIndex)

        for player in self.playerMap.values():
            group.addPlayer(player)

        group.start()

    def _doKillGroup(self, reason):
        group = self.area.findGroup(self.groupId)
        if group:
            group.kill(self.finishReason)

    def _doFinalGroup(self):
        group = self.area.findGroup(self.groupId)
        if group:
            group.final()


class MatchStage(object):
    ST_INIT = 0
    ST_START = 1
    ST_FINISH = 2
    ST_FINAL = 3

    def __init__(self, matching, stageConf):
        self.matching = matching
        self.stageConf = stageConf
        # 该阶段所有分组存根对象
        self._groupStubMap = {}
        self._state = self.ST_INIT

        # 日志
        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('instId', self.instId)
        self._logger.add('matchingId', self.matchingId)
        self._logger.add('stageIndex', self.stageIndex)

    @property
    def master(self):
        return self.matching.master

    @property
    def matchId(self):
        return self.matching.matchId

    @property
    def instId(self):
        return self.matching.instId

    @property
    def matchingId(self):
        return self.matching.matchingId

    @property
    def matchConf(self):
        return self.matching.matchConf

    @property
    def stageIndex(self):
        return self.stageConf.stageIndex

    @property
    def state(self):
        return self._state

    def findGroupStub(self, groupId):
        return self._groupStubMap.get(groupId)

    def getAllRisePlayerList(self):
        playerMap = {}
        for groupStub in self._groupStubMap.values():
            for player in groupStub.risePlayerSet:
                playerMap[player.userId] = player
        return playerMap.values()

    def startStage(self, playerList, startStageIndex=0):
        """
        开始该阶段
        """
        assert (self._state == self.ST_INIT)

        self._logger.info('MatchStage.start ...',
                          'state=', self._state,
                          'playerCount=', len(playerList))

        self._state = self.ST_START

        isGrouping, groupPlayersList = self._grouppingPlayers(playerList)
        groupInfos = []
        for i, groupPlayers in enumerate(groupPlayersList):
            groupId = '%s.%s.%s' % (self.matchingId, self.stageIndex, i + 1)
            groupName = MatchGroupUtils.generateGroupName(len(groupPlayersList), i)
            groupInfos.append((groupId, groupName, groupPlayers))

        groupStubs = self.master.createGroupStubs(self, groupInfos, isGrouping, startStageIndex)
        self._groupStubMap = {g.groupId: g for g in groupStubs}

        # bireport.matchStageStart(self.master.gameId, self.master.roomId,
        #                          self.matchId, self.master.matchName,
        #                          instId=self.instId,
        #                          matchingId=self.matchingId,
        #                          stageIndex=self.stageIndex,
        #                          isGrouping=isGrouping,
        #                          userCount=len(playerList),
        #                          groupCount=len(self._groupStubMap),
        #                          groupInfos=[(g.groupId, g.groupName, g.roomId, len(g.playerMap)) for g in groupStubs])

        sequence = int(self.instId.split('.')[1])
        cardList = [self.stageIndex, len(playerList), len(self._groupStubMap), 1 if isGrouping else 0]
        PokerMatchReport.reportMatchEvent('MATCH_STAGE_START', playerList[0].userId if playerList else 0, self.master.gameId,
                             self.master.roomId, 0, sequence, 0, cardList)


        for groupStub in self._groupStubMap.values():
            # 启动分组
            groupStub.start()
            # bireport.matchGroupStart(self.master.gameId, self.master.roomId,
            #                          self.matchId, self.master.matchName,
            #                          areaRoomId=groupStub.roomId,
            #                          instId=self.instId,
            #                          matchingId=self.matchingId,
            #                          stageIndex=self.stageIndex,
            #                          isGrouping=isGrouping,
            #                          groupId=groupStub.groupId,
            #                          userCount=len(groupStub.playerMap),
            #                          userIds=groupStub.playerMap.keys(),
            #                          startStageIndex=0)
            # TODO startStageIndex=self.matching.startStageIndex
            groupNum = groupStub.groupId.split('.')[-1]
            cardList = [self.stageIndex, len(groupStub.playerMap), groupNum, 1 if isGrouping else 0]
            PokerMatchReport.reportMatchEvent('MATCH_GROUP_START', playerList[0].userId if playerList else 0, self.master.gameId,
                                 groupStub.roomId, 0, sequence, 0, cardList)

        self._logger.info('MatchStage.start ok',
                          'state=', self._state,
                          'playerCount=', len(playerList),
                          'groupCount=', len(self._groupStubMap),
                          'groupInfos=', [(g.groupId, g.groupName, g.roomId, len(g.playerMap)) for g in groupStubs])

    def final(self):
        assert (self._state == self.ST_FINISH)
        self._state = self.ST_FINAL

        self._logger.info('MatchStage.final ...',
                          'state=', self._state)

        for groupStub in self._groupStubMap.values():
            groupStub.final()

        # bireport.matchStageFinish(self.master.gameId, self.master.roomId,
        #                           self.matchId, self.master.matchName,
        #                           instId=self.instId,
        #                           matchingId=self.matchingId,
        #                           stageIndex=self.stageIndex)
        sequence = int(self.instId.split('.')[1])
        cardList = [self.stageIndex]
        playerList = self.getAllRisePlayerList()
        PokerMatchReport.reportMatchEvent('MATCH_STAGE_FINISH', playerList[0].userId if playerList else 0, self.master.gameId,
                                          groupStub.roomId, 0, sequence, 0, cardList)

        # TODO 事件在那里处理
        # TYGame(self.master.gameId).getEventBus().publishEvent(
        #     MatchingStageFinishEvent(self.master.gameId, self.matchId, self.instId, self.matchingId, self.stageIndex))

        self._logger.info('MatchStage.final ok',
                          'state=', self._state)

    def processStage(self):
        if self._logger.isDebug():
            self._logger.debug('MatchStage._processStage',
                               'state=', self._state)

        if self._state == self.ST_START:
            if self._isAllGroupStubFinish():
                self._state = self.ST_FINISH

    def _grouppingPlayers(self, playerList):
        if self.stageConf.userCountPerGroup:
            ret = MatchGroupUtils.groupByMaxCountPerGroup(playerList,self.stageConf.userCountPerGroup,
                                                     self.matchConf.tableSeatCount)
            return True, ret
        return False, [playerList]

    def _isAllGroupStubFinish(self):
        if self._logger.isDebug():
            self._logger.debug('MatchStage._processStage',
                               'state=', self._state,
                               'groupStubs=', [(g.groupId, g.groupName, g.state) for g in self._groupStubMap.values()])

        for groupStub in self._groupStubMap.values():
            if groupStub.state < MatchGroup.ST_FINISH:
                return False
        return True


class Matching(object):
    ST_IDLE = 0
    ST_START = 1
    ST_FINISH = 2

    def __init__(self, master, instId, matchingId):
        self.master = master
        self.instId = instId
        self.matchingId = matchingId
        self._stages = self._createStages(self.master.matchConf.stages)
        self._startStageIndex = 0
        self._curStage = None
        self._state = self.ST_IDLE
        self._startPlayerCount = 0
        self._heartbeat = MatchProcesser(0, self._doHeartbeat)
        # 日志
        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('instId', self.instId)
        self._logger.add('matchingId', self.matchingId)

    @property
    def matchId(self):
        return self.master.matchId

    @property
    def startPlayerCount(self):
        return self._startPlayerCount

    @property
    def state(self):
        return self._state

    def findGroupStub(self, groupId):
        if self._curStage:
            return self._curStage.findGroupStub(groupId)
        return None

    def start(self, signers):
        assert (self._state == self.ST_IDLE)
        self._state = self.ST_START
        self._curStage = self._selectFirstStage(len(signers))

        self._logger.info('Matching.start ...',
                          'state=', self._state,
                          'userCount=', len(signers),
                          'firstStageIndex=', self._curStage.stageIndex)

        # TYGame(self.master.gameId).getEventBus().publishEvent(
        #     MatchingStartEvent(self.master.gameId, self.matchId, self.instId, self.matchingId))
        # bireport.matchStart(self.master.gameId, self.master.roomId,
        #                     self.matchId, self.master.matchName,
        #                     instId=self.instId,
        #                     matchingId=self.matchingId,
        #                     userCount=len(signers))


        playerList = self._signerToPlayer(signers)
        self._startPlayerCount = len(playerList)
        self._curStage.startStage(playerList,self._startStageIndex)
        self._heartbeat.start()

        self._logger.info('Matching.start ok',
                          'state=', self._state,
                          'userCount=', len(signers),
                          'firstStageIndex=', self._curStage.stageIndex)

    def _createStages(self, stageConfs):
        ret = []
        for stageConf in stageConfs:
            stage = MatchStage(self, stageConf)
            ret.append(stage)
        return ret

    def _selectFirstStage(self, signerCount):
        firstStage = self._stages[0]
        if not self.master.matchConf.startConf.selectFirstStage :
            # 从最接近的开赛人数阶段开始比赛
            for stage in self._stages:
                # 还是大于吧，等于就直接晋级下一次比赛
                if signerCount > stage.stageConf.riseUserCount:
                    firstStage = stage
                    break
        self._startStageIndex = firstStage.stageIndex
        return firstStage


    def _signerToPlayer(self, signers):
        ret = []
        for signer in signers:
            player = MatchPlayerData(signer.userId)
            player.userName = signer.userName
            player.signinTime = signer.signinTime
            player.clientId = signer.clientId
            player.feeIndex = signer.feeIndex
            ret.append(player)
        return ret

    def _getNextStage(self, stage):
        nextStageIndex = stage.stageIndex + 1
        if nextStageIndex < len(self._stages):
            return self._stages[nextStageIndex]
        return None

    def _startNextStage(self):
        playerList = self._curStage.getAllRisePlayerList()
        nextStage = self._getNextStage(self._curStage)

        self._logger.info('Matching._startNextStage',
                          'state=', self._state,
                          'stageIndex=', self._curStage.stageIndex,
                          'nextStageIndex=', nextStage.stageIndex if nextStage else None,
                          'nextStageState=', nextStage.state if nextStage else None,
                          'playerCount=', len(playerList))

        self._curStage.final()

        if nextStage:
            self._curStage = nextStage
            self._curStage.startStage(playerList,self._startStageIndex)
        else:
            self._doFinish()

    def _doFinish(self):
        self._logger.info('Matching._doFinish ...',
                          'state=', self._state)

        self._state = self.ST_FINISH
        self._heartbeat.stop()

        # bireport.matchFinish(self.master.gameId, self.master.roomId,
        #                      self.matchId, self.master.matchName,
        #                      instId=self.instId,
        #                      matchingId=self.matchingId)
        # TYGame(self.master.gameId).getEventBus().publishEvent(
        #     MatchingFinishEvent(self.master.gameId, self.matchId, self.instId, self.matchingId))

        self._logger.info('Matching._doFinish ok',
                          'state=', self._state)

    def _doHeartbeat(self):
        if self._logger.isDebug():
            self._logger.debug('Matching._doHeartbeat',
                               'state=', self._state,
                               'stageIndex=', self._curStage.stageIndex if self._curStage else None)

        if self._curStage:
            self._curStage.processStage()
            if self._curStage.state == MatchStage.ST_FINISH:
                self._startNextStage()

        return 2


class MatchArea(object):
    """
    比赛分区,分布式.

    报名、分组
    """

    ST_IDLE = 0
    ST_START = 1

    HEARTBEAT_TO_MASTER_INTERVAL = 5

    def __init__(self, room, matchId, conf, masterStub):
        self.room = room
        self.matchId = matchId
        self.matchConf = conf
        self.masterStub = masterStub
        self._curInst = None
        self._state = self.ST_IDLE
        self._lastHeartbeatToMasterTime = None

        # 所有比赛实例
        self._instMap = {}
        # map<groupId, MatchGroup>
        self._groupMap = {}
        # 心跳
        self._heartbeat = MatchProcesser(0, self._doHeartbeat)

        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('roomId', self.room.roomId)

        self.tableManager = None
        self.tableController = None

        self.matchSigninFeeIF = None
        self.matchRankRewardsIF = None
        self.matchPlayerIF = None

        self.signinRecordDao = None

    @property
    def roomId(self):
        return self.room.roomId

    @property
    def gameId(self):
        return self.room.gameId

    @property
    def matchName(self):
        return self.room.roomConf.get('name')

    @property
    def curInst(self):
        return self._curInst

    def findInst(self, instId):
        return self._instMap.get(instId)

    def findSigner(self, userId):
        if self._curInst:
            return self._curInst.findSigner(userId)
        return None

    def findPlayer(self, userId):
        for group in self._groupMap.values():
            player = group.findPlayer(userId)
            if player:
                return player
        return None

    def findGroup(self, groupId):
        return self._groupMap.get(groupId)

    def start(self):
        assert (self._state == MatchArea.ST_IDLE)
        self._logger.info('MatchArea.start ...',
                          'state=', self._state)
        self._state = MatchArea.ST_START
        self._heartbeat.start()
        self._logger.info('MatchArea.start ok',
                          'state=', self._state)

    @classmethod
    def parseStageId(cls, matchingId, groupId):
        try:
            return groupId[0:groupId.rfind('.')]
        except:
            return matchingId

    def calcTotalUncompleteTableCount(self, group):
        count = 0
        for areaStatus in self.masterStub.masterStatus.areaStatusMap.values():
            for groupStatus in areaStatus.groupStatusMap.values():
                if groupStatus.groupId == group.groupId:
                    count += group.calcUncompleteTableCount()
                elif groupStatus.matchingId == group.matchingId:
                    if self.parseStageId(group.matchingId, groupStatus.groupId) == self.parseStageId(group.matchingId,
                                                                                                     group.groupId):
                        count += groupStatus.uncompleteTableCount
        return count

    def calcTotalRemTimes(self, group):
        remTimes = 0
        for areaStatus in self.masterStub.masterStatus.areaStatusMap.values():
            for groupStatus in areaStatus.groupStatusMap.values():
                if groupStatus.matchingId == group.matchingId and groupStatus.remTimes > remTimes:
                    remTimes = groupStatus.remTimes
        return remTimes

    def calcTotalSignerCount(self, inst):
        """
        计算当前分区所有的报名人数.
        """
        count = 0
        for areaStatus in self.masterStub.masterStatus.areaStatusMap.values():
            if areaStatus.instStatus and inst.instId == areaStatus.instStatus.instId:
                count += areaStatus.instStatus.signerCount
        return max(count, inst.signerCount)

    def getTotalSignerCount(self):
        """
        计算比赛所有的报名人数.
        """
        count = 0
        for areaStatus in self.masterStub.masterStatus.areaStatusMap.values():
            if areaStatus.instStatus:
                count += areaStatus.instStatus.signerCount
        return count

    def getTotalPlayerCount(self):
        """
        计算比赛所有的游戏人数.
        """
        count = 0
        for areaStatus in self.masterStub.masterStatus.areaStatusMap.values():
            for groupStatus in areaStatus.groupStatusMap.values():
                count += groupStatus.playerCount
        return count

    def buildStatus(self):
        ret = MatchAreaStatus()
        ret.timestamp = fttime.getCurrentTimestamp()
        if self.curInst:
            ret.instStatus = self.curInst.buildStatus()
        for group in self._groupMap.values():
            status = group.buildStatus()
            status.timestamp = ret.timestamp
            ret.groupStatusMap[group.groupId] = status
        return ret

    def signin(self, userId, feeIndex, signinParams):
        """
        玩家报名
        """
        if not self._curInst:
            raise MatchStoppedException()

        if self.findPlayer(userId):
            raise UserAlreadyInMatchException()

        return self._curInst.signin(userId, feeIndex, signinParams)

    def signout(self, userId):
        """
        玩家退赛，转到主赛区处理
        """
        if not self._curInst:
            raise MatchStoppedException()

        return self._curInst.signout(userId)

    def enter(self, userId):
        """
        进入报名页
        """
        if self._curInst:
            self._curInst.enter(userId)

    def leave(self, userId):
        """
        离开报名页
        """
        if self._curInst:
            self._curInst.leave(userId)

    def tableWinlose(self, groupId, tableId, ccrc, seatWinloses):
        group = self.findGroup(groupId)
        if not group:
            self._logger.warn('MatchArea.tableWinlose',
                              'groupId=', groupId,
                              'tableId=', tableId,
                              'ccrc=', ccrc,
                              'seatWinloses=', seatWinloses,
                              'err=', 'NotFoundGroup')
            return

        group.tableWinlose(tableId, ccrc, seatWinloses)

    def createInst(self, instId, startTime, needLoad):
        self._logger.info('MatchArea.createInst ...',
                          'state=', self._state,
                          'instId=', instId,
                          'startTime=', startTime,
                          'needLoad=', needLoad,
                          'curInstId=', self._curInst.instId if self._curInst else None)

        inst = self.findInst(instId)
        if inst:
            self._logger.error('MatchArea.createInst fail',
                               'state=', self._state,
                               'instId=', instId,
                               'startTime=', startTime,
                               'needLoad=', needLoad,
                               'err=', 'AlreadyCreate')
            return None

        inst = MatchInst(self, instId, startTime, needLoad)
        inst.load()
        self._instMap[instId] = inst
        self._curInst = inst
        self._logger.info('MatchArea.createInst ok',
                          'state=', self._state,
                          'startTime=', startTime,
                          'needLoad=', needLoad,
                          'instId=', instId)
        return self._curInst

    def cancelInst(self, instId, reason):
        self._logger.info('MatchArea.cancelInst ...',
                          'state=', self._state,
                          'instId=', instId,
                          'reason=', reason)
        inst = self.findInst(instId)
        if inst:
            inst.cancel(reason)
        self._logger.info('MatchArea.cancelInst ok',
                          'state=', self._state,
                          'instId=', instId,
                          'reason=', reason)

    def createGroup(self, instId, matchingId, groupId,
                    groupName, stageIndex, isGrouping,
                    totalPlayerCount, startStageIndex):

        group = self.findGroup(groupId)
        if group:
            self._logger.error('MatchArea.createGroup fail',
                               'state=', self._state,
                               'instId=', instId,
                               'matchingId=', matchingId,
                               'groupId=', groupId,
                               'groupName=', groupName,
                               'stageIndex=', stageIndex,
                               'isGrouping=', isGrouping,
                               'totalPlayerCount=', totalPlayerCount,
                               'startStageIndex=', startStageIndex,
                               'err=', 'GroupExists')
            raise BadMatchStateException()

        group = MatchGroup(self, instId, matchingId, groupId,
                           groupName, isGrouping, stageIndex,
                           totalPlayerCount, startStageIndex)

        self._groupMap[groupId] = group

        self._logger.info('MatchArea.createGroup ok',
                          'instId=', instId,
                          'matchingId=', matchingId,
                          'groupId=', groupId,
                          'groupName=', groupName,
                          'stageIndex=', stageIndex,
                          'isGrouping=', isGrouping,
                          'totalPlayerCount=', totalPlayerCount)

        return group

    def onInstStarted(self, inst):
        self._logger.info('MatchArea.onInstStarted ...',
                          'state=', self._state,
                          'instId=', inst.instId,
                          'signerCount=', inst.signerCount)
        try:
            self.masterStub.areaInstStarted(self, inst)
            self._logger.info('MatchArea.onInstStarted ok',
                              'instId=', inst.instId,
                              'signerCount=', inst.signerCount)
        except:
            self._logger.error('MatchArea.onInstStarted fail',
                               'instId=', inst.instId,
                               'signerCount=', inst.signerCount)

    def onGroupFinish(self, group):
        self._logger.info('MatchArea.onGroupFinish',
                          'state=', self._state,
                          'groupId=', group.groupId,
                          'reason=', group.finishReason,
                          'riseUserIds=', [p.userId for p in group.rankList])
        try:
            self.masterStub.areaGroupFinish(self, group)
        except:
            self._logger.error('MatchArea.onGroupFinish fail',
                               'state=', self._state,
                               'groupId=', group.groupId,
                               'reason=', group.finishReason)

    def _processGroups(self):
        groups = self._groupMap.values()[:]
        for group in groups:
            if group.state == MatchGroup.ST_FINAL:
                del self._groupMap[group.groupId]
                self._logger.info('MatchArea._processGroups removeGroup',
                                  'state=', self._state,
                                  'groupId=', group.groupId)

    def _processInsts(self):
        insts = self._instMap.values()[:]
        for inst in insts:
            if inst.state == MatchInst.ST_FINAL:
                self._logger.info('MatchArea._processInsts removeInst',
                                  'state=', self._state,
                                  'instId=', inst.instId,
                                  'curInst=', self._curInst.instId if self._curInst else None)

                del self._instMap[inst.instId]
                if inst == self._curInst:
                    self._curInst = None

    def _doHeartbeat(self):
        timestamp = fttime.getCurrentTimestamp()
        if self._logger.isDebug():
            self._logger.debug('MatchArea._doHeartbeat',
                               'state=', self._state,
                               'curInst=', self._curInst.instId if self._curInst else None,
                               'timestamp=', timestamp,
                               'lastHeartbeatToMasterTime=', self._lastHeartbeatToMasterTime)

        heartbeatInterval = 1 if self.matchConf.startConf.isUserCountType else MatchArea.HEARTBEAT_TO_MASTER_INTERVAL
        if not self._lastHeartbeatToMasterTime or timestamp - self._lastHeartbeatToMasterTime > heartbeatInterval:
            self._lastHeartbeatToMasterTime = timestamp
            try:
                self.masterStub.areaHeartbeat(self)
            except:
                self._logger.error('MatchArea._doHeartbeat',
                                   'state=', self._state)
        self._processGroups()
        return 1


class MatchAreaStub(object):
    """
    赛区控制器，运行在主控进程
    """
    ST_OFFLINE = 0
    ST_ONLINE = 1
    ST_TIMEOUT = 2

    HEARTBEAT_TIMEOUT_TIMES = 3

    def __init__(self, master, roomId):
        self.master = master
        self.roomId = roomId
        # 状态
        self.areaStatus = None
        # 分组控制器
        self._groupStubMap = {}
        # 当前比赛实例控制器
        self._curInstStub = None
        # 最后心跳时间
        self._lastHeartbeatTime = None
        # 启动时间
        self._startTime = None
        # 在线状态
        self._onlineState = self.ST_OFFLINE
        # 心跳
        self._heartbeat = MatchProcesser(0, self._doHeartbeat)
        # 日志
        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('roomId', self.roomId)

    @property
    def matchId(self):
        return self.master.matchId

    @property
    def matchConf(self):
        return self.master.matchConf

    @property
    def curInstStub(self):
        return self._curInstStub

    @property
    def groupStubMap(self):
        return self._groupStubMap

    def findGroupStub(self, groupId):
        return self._groupStubMap.get(groupId)

    def findInstStub(self, instId):
        if self._curInstStub and self._curInstStub.instId == instId:
            return self._curInstStub
        return None

    def isOnline(self):
        """
        是否上线了
        """
        # TODO 上线后又掉线
        return self._lastHeartbeatTime is not None

    def buildStatus(self):
        ret = MatchAreaStatus()
        if self.areaStatus:
            ret.instStatus = self.areaStatus.instStatus
            ret.timestamp = self.areaStatus.timestamp
        for groupStub in self._groupStubMap.values():
            groupStatus = groupStub.buildStatus()
            if groupStatus:
                ret.groupStatusMap[groupStub.groupId] = groupStatus
        return ret

    def start(self):
        self._logger.info('MatchAreaStub.start ...')
        self._heartbeat.start()
        self._logger.info('MatchAreaStub.start ok')

    def createInst(self, instId, startTime, needLoad):
        """
        让分赛区创建比赛实例
        """
        self._logger.info('MatchAreaStub.createInst ...',
                          'instId=', instId,
                          'startTime=', startTime,
                          'needLoad=', needLoad)

        self._curInstStub = self._createInstStubImpl(instId, startTime, needLoad)

        self._logger.info('MatchAreaStub.createInst ok',
                          'instId=', instId,
                          'startTime=', startTime,
                          'needLoad=', needLoad)

    def createGroup(self, stage, groupId, groupName,
                    playerList, isGrouping, totalPlayerCount, startStageIndex):
        """
        创建分组
        """
        self._logger.info('MatchAreaStub.createGroup ...',
                          'instId=', stage.instId,
                          'matchingId=', stage.matchingId,
                          'groupId=', groupId,
                          'groupName=', groupName,
                          'playerCount=', len(playerList),
                          'isGrouping=', isGrouping,
                          'totalPlayerCount=', totalPlayerCount)

        groupStub = self._createGroupStubImpl(stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, startStageIndex)
        self._groupStubMap[groupStub.groupId] = groupStub

        self._logger.info('MatchAreaStub.createGroup ok',
                          'instId=', stage.instId,
                          'matchingId=', stage.matchingId,
                          'groupId=', groupId,
                          'groupName=', groupName,
                          'playerCount=', len(playerList),
                          'isGrouping=', isGrouping,
                          'totalPlayerCount=', totalPlayerCount)

        return groupStub

    def cancelInst(self, instId, reason):
        """
        分赛区取消比赛实例
        """
        raise NotImplementedError

    def masterHeartbeat(self, master):
        """
        向分赛区发送，主赛区心跳
        """
        raise NotImplementedError

    def onAreaHeartbeat(self, areaStatus):
        """
        area心跳回调
        """
        assert (isinstance(areaStatus, MatchAreaStatus))
        if self._logger.isDebug():
            self._logger.debug('MatchAreaStub.onAreaHeartbeat',
                               'curInstId=', self._curInstStub.instId if self._curInstStub else None,
                               'groupIds=', self._groupStubMap.keys())

        self._lastHeartbeatTime = fttime.getCurrentTimestamp()
        self.areaStatus = areaStatus
        # 把心跳分发给各个groupStub
        for groupStatus in self.areaStatus.groupStatusMap.values():
            groupStub = self.findGroupStub(groupStatus.groupId)
            if groupStub:
                groupStub.onGroupHeartbeat(groupStatus)

    def _doHeartbeat(self):
        if self._logger.isDebug():
            self._logger.debug('MatchAreaStub._doHeartbeat',
                               'curInstId=', self._curInstStub.instId if self._curInstStub else None,
                               'groupIds=', self._groupStubMap.keys())

        self._processGroupStubs()

        return 1

    def _processGroupStubs(self):
        groupStubs = list(self._groupStubMap.values())
        for groupStub in groupStubs:
            if groupStub.state == MatchGroup.ST_FINAL:
                del self._groupStubMap[groupStub.groupId]
                self._logger.info('MatchAreaStub._processGroupStubs removeGroupStub',
                                  'groupId=', groupStub.groupId)

    def _createInstStubImpl(self, instId, startTime, needLoad):
        raise NotImplementedError

    def _createGroupStubImpl(self, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount):
        raise NotImplementedError


class MatchAreaStubLocal(MatchAreaStub):
    def __init__(self, master, area):
        super(MatchAreaStubLocal, self).__init__(master, area.roomId)
        self.area = area

    def masterHeartbeat(self, master):
        """
        向分赛区发送，主赛区心跳
        """
        self.area.masterStub.onMasterHeartbeat(master.buildStatus())

    def cancelInst(self, instId, reason):
        """
        分赛区取消比赛实例
        """
        self.area.cancelInst(instId, reason)

    def _createInstStubImpl(self, instId, startTime, needLoad):
        try:
            inst = self.area.createInst(instId, startTime, needLoad)
        except:
            self._logger.error('MatchAreaStubLocal._createInstStubImpl',
                               'instId=', instId,
                               'startTime=', startTime,
                               'needLoad=', needLoad)
        return MatchInstStubLocal(self, instId, startTime, needLoad, inst)

    def _createGroupStubImpl(self, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, startStageIndex):
        return MatchGroupStubLocal(self, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount,
                                   self.area, startStageIndex)


class MatchMasterStub(object):
    """
    主赛区控制器，运行在分赛区
    """

    def __init__(self, roomId):
        self.masterStatus = MatchMasterStatus()
        self.roomId = roomId

        self._logger = Logger()
        self._logger.add('roomId', roomId)

    def areaHeartbeat(self, area):
        """
        赛区心跳
        """
        raise NotImplementedError

    def areaGroupFinish(self, area, group):
        """
        赛区某一分组完成了，向主赛区汇报
        """
        raise NotImplementedError

    def areaInstStarted(self, area, inst):
        """
        赛区中的实例开始了，向主赛区汇报参与比赛的玩家
        """
        raise NotImplementedError

    def onMasterHeartbeat(self, masterStatus):
        """
        主控进程心跳
        """
        assert (isinstance(masterStatus, MatchMasterStatus))
        self.masterStatus = masterStatus


class MatchMasterStubLocal(MatchMasterStub):
    def __init__(self, master):
        super(MatchMasterStubLocal, self).__init__(master.roomId)
        self.master = master

    def areaHeartbeat(self, area):
        """
        赛区心跳
        """
        self._logger.info('MatchMasterStubLocal.areaHeartbeat'
                          'area=', area.roomId)
        areaStub = self.master.findAreaStub(area.roomId)
        areaStub.onAreaHeartbeat(area.buildStatus())

    def areaGroupFinish(self, area, group):
        """
        赛区某一分组完成了，向主赛区汇报
        """
        self._logger.info('MatchMasterStubLocal.areaGroupFinish ...',
                          'area=', area.roomId,
                          'groupId=', group.groupId,
                          'finishReason=', group.finishReason)

        groupStub = self.master.findGroupStub(group.matchingId, group.groupId)
        if groupStub:
            if group.finishReason == MatchFinishReason.FINISH:
                for player in group.riseList:
                    riser = MatchRiser(player.userId, player.score, player.rank, player.tableRank)
                    groupStub.onGroupRisePlayer(riser)
            groupStub.onGroupFinish(group.finishReason)

            self._logger.info('MatchMasterStubLocal.areaGroupFinish ok',
                              'area=', area.roomId,
                              'groupId=', group.groupId,
                              'finishReason=', group.finishReason)
        else:
            self._logger.info('MatchMasterStubLocal.areaGroupFinish fail',
                              'area=', area.roomId,
                              'groupId=', group.groupId,
                              'finishReason=', group.finishReason,
                              'err=', 'NotFoundGroupStub')

    def areaInstStarted(self, area, inst):
        """
        赛区中的实例开始了，向主赛区汇报参与比赛的玩家
        """
        self._logger.info('MatchMasterStubLocal.areaInstStarted'
                          'area=', area.roomId,
                          'instId=', inst.instId)

        instStub = self.master.findInstStub(area.roomId, inst.instId)
        instStub.onSignin(inst.signerMap.values())
        instStub.onStart()

    # def onMasterHeartbeat(self, masterStatus):
    #     """
    #     主控进程心跳
    #     """
    #     pass


class MatchInstStatus(object):
    def __init__(self, instId, state, signerCount):
        self.instId = instId
        self.state = state
        self.signerCount = signerCount

    def toDict(self):
        d = {}
        d['iid'] = self.instId
        d['st'] = self.state
        d['sc'] = self.signerCount
        return d

    @classmethod
    def fromDict(cls, d):
        return MatchInstStatus(d['iid'], d['st'], d['sc'])


class MatchGroupStatus(object):
    def __init__(self, groupId, matchingId, state,
                 uncompleteTableCount, remTimes, lastActiveTime, playerCount):
        # 分组ID
        self.groupId = groupId
        # 比赛ID
        self.matchingId = matchingId
        # 状态
        self.state = state
        # 剩余几桌没完成
        self.uncompleteTableCount = uncompleteTableCount
        # 剩余时间
        self.remTimes = remTimes
        # 最后活跃时间
        self.lastActiveTime = lastActiveTime
        # 时间戳
        self.timestamp = None
        # 当前分组的人数
        self.playerCount = playerCount

    def toDict(self):
        d = {}
        d['gid'] = self.groupId
        d['mid'] = self.matchingId
        d['st'] = self.state
        d['utc'] = self.uncompleteTableCount
        d['rt'] = self.remTimes
        d['lat'] = self.lastActiveTime
        d['pc'] = self.playerCount
        return d

    @classmethod
    def fromDict(cls, d):
        return MatchGroupStatus(d['gid'], d['mid'], d['st'], d['utc'], d['rt'], d['lat'], d['pc'])


class MatchAreaStatus(object):
    def __init__(self):
        # 比赛实例状态
        self.instStatus = None
        # key=roomId, value=MatchAreaStatus
        self.groupStatusMap = {}
        # 分赛区时间戳
        self.timestamp = None

    def toDict(self):
        d = {}
        if self.instStatus:
            d['inst'] = self.instStatus.toDict()
        groups = []
        for groupStatus in self.groupStatusMap.values():
            groups.append(groupStatus.toDict())
        d['groups'] = groups
        d['ts'] = self.timestamp
        return d

    @classmethod
    def fromDict(cls, d):
        ret = MatchAreaStatus()
        instD = d.get('inst')
        if instD:
            ret.instStatus = MatchInstStatus.fromDict(instD)
        ret.timestamp = d['ts']
        for groupD in d.get('groups', []):
            groupStatus = MatchGroupStatus.fromDict(groupD)
            groupStatus.timestamp = ret.timestamp
            ret.groupStatusMap[groupStatus.groupId] = groupStatus
        return ret


class MatchMasterStatus(object):
    def __init__(self):
        # key=roomId, value=MatchAreaStatus
        self.areaStatusMap = {}

    def toDict(self):
        d = {}
        areaStatusMap = {}
        for roomId, areaStatus in self.areaStatusMap.iteritems():
            areaStatusMap[roomId] = areaStatus.toDict()
        d['asm'] = areaStatusMap
        return d

    @classmethod
    def fromDict(cls, d):
        ret = MatchMasterStatus()
        areaStatusMap = d['asm']
        for roomId, areaStatusD in areaStatusMap.iteritems():
            ret.areaStatusMap[roomId] = MatchAreaStatus.fromDict(areaStatusD)
        return ret


class MatchInstCtrl(object):
    STARTING_TIMEOUT = 90

    def __init__(self, master, status, needLoad):
        self.master = master
        self.status = status
        self.needLoad = needLoad
        self.prepareTime = None
        self.signinTime = None
        self.instId = status.instId

        if status.startTime:
            self.prepareTime = master.matchConf.startConf.calcPrepareTime(status.startTime)
            self.signinTime = master.matchConf.startConf.calcSigninTime(status.startTime)

        self._state = MatchInst.ST_IDLE
        self._startingTime = None
        self._heartbeat = MatchProcesser(0, self._doHeartbeat)

        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('instId', self.instId)
        self._logger.add('startTime', self.startTime)
        self._logger.add('signinTime', self.signinTime)

    @property
    def matchId(self):
        return self.master.matchId

    @property
    def state(self):
        return self._state

    @property
    def matchConf(self):
        return self.master.matchConf

    @property
    def startTime(self):
        return self.status.startTime

    def start(self):
        assert (self._state == MatchInst.ST_IDLE)
        self._logger.info('MatchInstCtrl.Start ...',
                          'state=', self._state)

        self._heartbeat.start()

        self._logger.info('MatchInstCtrl.Start ok',
                          'state=', self._state)

    def _doLoad(self):
        assert (self._state == MatchInst.ST_IDLE)

        self._logger.info('MatchInstCtrl._doLoad ...',
                          'state=', self._state)

        self._state = MatchInst.ST_LOAD

        for areaStub in self.master.areaStubList[::-1]:
            areaStub.createInst(self.instId, self.startTime, self.needLoad)

        self._logger.info('MatchInstCtrl._doLoad ok',
                          'state=', self._state)

    def _cancel(self, reason):
        self._logger.info('MatchInstCtrl._cancel ...',
                          'state=', self._state)

        for areaStub in self.master.areaStubList[::-1]:
            if areaStub.curInstStub:
                areaStub.curInstStub.cancel(reason)

        # TYGame(self.master.gameId).getEventBus().publishEvent(MatchCancelEvent(self.master.gameId, self.instId, reason))

        self._logger.info('MatchInstCtrl._cancel ok',
                          'state=', self._state)

    def _moveToNext(self, nextInstId, signers):
        assert (len(self.master.areaStubList) == 1)

        self._logger.info('MatchInstCtrl._moveToNext ...',
                          'state=', self._state,
                          'nextInstId=', nextInstId,
                          'signerCount=', len(signers))

        areaStub = self.master.areaStubList[0]
        areaStub.curInstStub.moveTo(nextInstId, signers)

        self._logger.info('MatchInstCtrl._moveToNext ok',
                          'state=', self._state,
                          'nextInstId=', nextInstId,
                          'signerCount=', len(signers))

    def _cancelSigners(self, reason, signers):
        self._logger.info('MatchInstCtrl._cancelSigners ...',
                          'state=', self._state,
                          'reason=', reason,
                          'signerCount=', len(signers))

        assert (len(self.master.areaStubList) == 1)

        areaStub = self.master.areaStubList[0]
        areaStub.curInstStub.cancelSigners(reason, signers)

        self._logger.info('MatchInstCtrl._cancelSigners ok',
                          'state=', self._state,
                          'reason=', reason,
                          'signerCount=', len(signers))

    def _doStartSignin(self):
        assert (self._state == MatchInst.ST_LOAD)
        self._state = MatchInst.ST_SIGNIN

        self._logger.info('MatchInstCtrl._doStartSignin ...',
                          'state=', self._state)

        for areaStub in self.master.areaStubList[::-1]:
            if areaStub.curInstStub:
                areaStub.curInstStub.startSignin()

        # TYGame(self.master.gameId).getEventBus().publishEvent(MatchStartSigninEvent(self.master.gameId, self.instId))

        self._logger.info('MatchInstCtrl._doStartSignin ok',
                          'state=', self._state)

    def _doPrepare(self):
        assert (self._state == MatchInst.ST_SIGNIN)

        self._logger.info('MatchInstCtrl._doPrepare ...',
                          'state=', self._state)

        self._state = MatchInst.ST_PREPARE

        for areaStub in self.master.areaStubList[::-1]:
            if areaStub.curInstStub:
                areaStub.curInstStub.prepare()

        self._logger.info('MatchInstCtrl._doPrepare ok',
                          'state=', self._state)

    def _doStart(self):
        assert (self._state in (MatchInst.ST_SIGNIN, MatchInst.ST_PREPARE))
        self._logger.info('MatchInstCtrl._doStart ...',
                          'state=', self._state)

        self._state = MatchInst.ST_STARTING
        self._startingTime = fttime.getCurrentTimestamp()

        for areaStub in self.master.areaStubList[::-1]:
            if areaStub.curInstStub:
                areaStub.curInstStub.start()

        self._logger.info('MatchInstCtrl._doStart ok',
                          'state=', self._state)

    def _doFinal(self):
        assert (self._state == MatchInst.ST_START)
        self._logger.info('MatchInstCtrl._doFinal ...',
                          'state=', self._state)

        self._state = MatchInst.ST_FINAL
        self._heartbeat.stop()

        self._logger.info('MatchInstCtrl._doFinal ok',
                          'state=', self._state)

    def _isAllStarted(self):
        for areaStub in self.master.areaStubList:
            if areaStub.curInstStub and areaStub.curInstStub.state != MatchInst.ST_START:
                return False
        return True

    def _isStartingTimeout(self):
        if self._state == MatchInst.ST_STARTING:
            ts = fttime.getCurrentTimestamp()
            return (ts - self._startingTime) >= MatchInstCtrl.STARTING_TIMEOUT
        return False

    def _cancelNotStartInst(self):
        for areaStub in self.master.areaStubList:
            if areaStub.curInstStub and areaStub.curInstStub.state != MatchInst.ST_START:
                areaStub.curInstStub.cancel(MatchFinishReason.TIMEOUT)

    def _calcTotalSignerCount(self):
        count = 0
        for areaStub in self.master.areaStubList:
            if areaStub.areaStatus and areaStub.areaStatus.instStatus:
                if areaStub.areaStatus.instStatus.instId == self.instId:
                    count += areaStub.areaStatus.instStatus.signerCount
        if ftlog.is_debug():
            ftlog.debug('MatchInstCtrl._calcTotalSignerCount',
                        'instId=', self.instId,
                        'startTime=', self.startTime,
                        'signinTime=', self.signinTime,
                        'state=', self._state,
                        'count=', count)
        return count

    def _collectSignerMap(self):
        signerMap = {}
        for areaStub in self.master.areaStubList:
            if areaStub.curInstStub:
                signerMap.update(areaStub.curInstStub.signerMap)
        return signerMap

    def _doHeartbeat(self):
        timestamp = fttime.getCurrentTimestamp()

        if ftlog.is_debug():
            ftlog.debug('MatchInstCtrl._doHeartbeat',
                        'matchId=', self.matchId,
                        'instId=', self.instId,
                        'startTime=', self.startTime,
                        'signinTime=', self.signinTime,
                        'state=', self._state,
                        'timestamp=', timestamp)

        if self._state == MatchInst.ST_IDLE:
            self._doLoad()

        if self._state == MatchInst.ST_LOAD:
            if (not self.signinTime
                or fttime.getCurrentTimestamp() >= self.signinTime):
                self._doStartSignin()

        if self._state == MatchInst.ST_SIGNIN:
            # 定时赛才有准备时间
            if (self.prepareTime
                and timestamp >= self.prepareTime):
                self._doPrepare()

        if self._state in (MatchInst.ST_SIGNIN, MatchInst.ST_PREPARE):
            if self.startTime:
                if timestamp >= self.startTime:
                    self._doStart()
            else:
                totalSignerCount = self._calcTotalSignerCount()
                if ftlog.is_debug():
                    ftlog.debug('MatchInstCtrl._doHeartbeat',
                                'matchId=', self.matchId,
                                'instId=', self.instId,
                                'startTime=', self.startTime,
                                'signinTime=', self.signinTime,
                                'state=', self._state,
                                'timestamp=', timestamp,
                                'totalSignerCount=', totalSignerCount,
                                'startUserCount=', self.matchConf.startConf.userCount)

                if totalSignerCount >= self.matchConf.startConf.userCount:
                    self._doStart()

        if self._state == MatchInst.ST_STARTING:
            if self._isAllStarted() or self._isStartingTimeout():
                self._cancelNotStartInst()
                self._state = MatchInst.ST_START
                signerMap = self._collectSignerMap()
                if self.startTime:
                    if ftlog.is_debug():
                        ftlog.debug('MatchInstCtrl._doHeartbeat',
                                    'matchId=', self.matchId,
                                    'instId=', self.instId,
                                    'startTime=', self.startTime,
                                    'signinTime=', self.signinTime,
                                    'state=', self._state,
                                    'timestamp=', timestamp,
                                    'signerMapCount=', len(signerMap),
                                    'userMinCount=', self.matchConf.startConf.userMinCount)
                    if len(signerMap) < self.matchConf.startConf.userMinCount:
                        self._cancel(MatchFinishReason.USER_NOT_ENOUGH)
                        signerMap = None
                    self._doFinal()
                    if signerMap:
                        # 定时赛通知玩家比赛开始
                        self.master._startMatching(self.instId, 1, signerMap.values())
                    self.master._setupNextInst(self, None)
                else:
                    signers = sorted(signerMap.values(), key=lambda s: s.signinTime)
                    num = 1
                    while len(signers) >= self.matchConf.startConf.userCount:
                        currentSigners = signers[0:self.matchConf.startConf.userCount]
                        self.master._startMatching(self.instId, num, currentSigners)
                        signers = signers[self.matchConf.startConf.userCount:]
                        num += 1
                    self.master._setupNextInst(self, signers)
                    self._doFinal()

        return 1


class MatchMaster(object):
    """MatchMaster 比赛主控对象.
    赛区控制器、开赛点、比赛进程、分组控制器


    :param room: 房间对象
    :param matchId: 比赛ID
    :param matchConf: 比赛配置

    """
    # TODO 开赛后复活、追加报名
    ST_IDLE = 0
    ST_START = 1
    ST_ALL_AREA_ONLINE = 2
    ST_LOAD = 3

    HEARTBEAT_TO_AREA_INTERVAL = 5

    def __init__(self, room, matchId, matchConf):
        self.room = room
        self.matchId = matchId
        self.matchConf = matchConf
        self._state = self.ST_IDLE
        self._areaStubList = []
        self._areaStubMap = {}
        # 所有比赛 map<matchingId, Matching>
        self._matchingMap = {}
        self._instCtrl = None
        # 最后到所有area心跳时间
        self._lastHeartbeatToAreaTime = None

        self._heartbeat = MatchProcesser(0, self._doHeartbeat)

        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('roomId', self.roomId)

        # 赛事状态dao
        self.matchStatusDao = None

    @property
    def gameId(self):
        return self.room.gameId

    @property
    def roomId(self):
        return self.room.roomId

    @property
    def areaStubList(self):
        return self._areaStubList

    @property
    def areaCount(self):
        return len(self._areaStubList)

    @property
    def matchName(self):
        return self.room.conf.name

    @property
    def signinCount(self):
        return self._instCtrl._calcTotalSignerCount() if self._instCtrl else 0

    @property
    def playerCount(self):
        return self._calcMatchingPlayerCount()

    def addAreaStub(self, areaStub):
        assert (self._state == self.ST_IDLE)
        assert (isinstance(areaStub, MatchAreaStub))
        assert (not self.findAreaStub(areaStub.roomId))
        self._areaStubMap[areaStub.roomId] = areaStub
        self._areaStubList.append(areaStub)

    def findAreaStub(self, roomId):
        return self._areaStubMap.get(roomId)

    def findMatching(self, matchingId):
        return self._matchingMap.get(matchingId)

    def findGroupStub(self, matchingId, groupId):
        matching = self.findMatching(matchingId)
        if matching:
            return matching.findGroupStub(groupId)
        return None

    def findInstStub(self, roomId, instId):
        areaStub = self.findAreaStub(roomId)
        if areaStub:
            return areaStub.findInstStub(instId)
        return None

    def buildStatus(self):
        ret = MatchMasterStatus()
        for areaStub in self._areaStubMap.values():
            ret.areaStatusMap[areaStub.roomId] = areaStub.buildStatus()
        return ret

    def start(self):
        assert (self._state == MatchMaster.ST_IDLE)

        ftlog.info('MatchMaster.start ...',
                   'matchId=', self.matchId,
                   'state=', self._state)

        self._state = MatchMaster.ST_START
        self._heartbeat.start()

        for areaStub in self._areaStubList:
            areaStub.start()

        ftlog.info('MatchMaster.start ok',
                   'matchId=', self.matchId,
                   'state=', self._state)

    def createGroupStubs(self, stage, groupInfos, isGrouping, startStageIndex):
        groupStubs = []
        for i, (groupId, groupName, players) in enumerate(groupInfos):
            index = i % len(self._areaStubList)
            groupStub = self._areaStubList[index].createGroup(stage, groupId, groupName,
                                                              players, isGrouping,
                                                              stage.matching.startPlayerCount, startStageIndex)
            groupStubs.append(groupStub)
        return groupStubs

    def _startMatching(self, instId, num, signers):
        matchingId = '%s.%s' % (instId, num)
        matching = Matching(self, instId, matchingId)
        self._matchingMap[matchingId] = matching

        ftlog.info('MatchMaster._startMatching ...',
                   'matchId=', self.matchId,
                   'instId=', instId,
                   'matchingId=', matchingId,
                   'userCount=', len(signers))

        matching.start(signers)

        ftlog.info('MatchMaster._startMatching ok',
                   'matchId=', self.matchId,
                   'instId=', instId,
                   'matchingId=', matchingId,
                   'userCount=', len(signers))

    def _processMatching(self):
        if self._matchingMap:
            matchingList = list(self._matchingMap.values())
            for matching in matchingList:
                if matching.state == Matching.ST_FINISH:
                    del self._matchingMap[matching.matchingId]
                    ftlog.info('MatchMaster._processMatching matchingFinished',
                               'matchId=', self.matchId,
                               'matchingId=', matching.matchingId)

    def _heartbeatToAllArea(self):
        for areaStub in self._areaStubList:
            try:
                areaStub.masterHeartbeat(self)
            except:
                ftlog.error('MatchMaster._heartbeatToAllArea',
                            'matchId=', self.matchId,
                            'roomId=', areaStub.roomId)

        ftlog.info('MatchMaster._heartbeatToAllArea',
                   'matchId=', self.matchId,
                   'areaCount=', self.areaCount)

    def _isAllAreaOnline(self):
        for areaStub in self._areaStubList:
            if not areaStub.isOnline():
                return False
        return True

    def _calcMatchingPlayerCount(self):
        # TODO 同时进行2个比赛
        ret = 0
        for areaStub in self._areaStubMap.values():
            for groupStub in areaStub.groupStubMap.values():
                ret += groupStub.playerCount
        return ret

    def _doHeartbeat(self):
        timestamp = fttime.getCurrentTimestamp()

        if ftlog.is_debug():
            ftlog.debug('MatchMaster._doHeartbeat',
                        'matchId=', self.matchId,
                        'timestamp=', timestamp,
                        'areaCount=', self.areaCount,
                        'matchingCount=', len(self._matchingMap))
        if self._state == MatchMaster.ST_START:
            if self._isAllAreaOnline():
                self._state = MatchMaster.ST_ALL_AREA_ONLINE
                self._logger.info('MatchMaster._doHeartbeat allAreaOnline',
                                  'areaCount=', self.areaCount)

        if self._state == MatchMaster.ST_ALL_AREA_ONLINE:
            self._doLoad()

        if self._state == MatchMaster.ST_LOAD:
            self._processMatching()

        if self._state >= MatchMaster.ST_ALL_AREA_ONLINE:
            if (not self._lastHeartbeatToAreaTime
                or timestamp - self._lastHeartbeatToAreaTime > MatchMaster.HEARTBEAT_TO_AREA_INTERVAL):
                self._lastHeartbeatToAreaTime = timestamp
                self._heartbeatToAllArea()
                roomInfo = self._buildRoomInfo()
                if self._logger.isDebug():
                    self._logger.debug('MatchMaster._doHeartbeat',
                                       'roomInfo=', roomInfo.__dict__)
                basedao.saveRoomInfo(self.gameId, roomInfo)
        return 1

    def _buildRoomInfo(self):
        roomInfo = MatchRoomInfo()
        roomInfo.roomId = self.room.bigRoomId
        roomInfo.playerCount = self._calcMatchingPlayerCount()
        roomInfo.signinCount = self._instCtrl._calcTotalSignerCount() if self._instCtrl else 0
        roomInfo.startType = self.matchConf.startConf.type
        roomInfo.instId = self._instCtrl.instId if self._instCtrl else None
        # TODO 报名费
        roomInfo.fees = []
        if self._instCtrl and self.matchConf.startConf.isTimingType():
            roomInfo.startTime = self._instCtrl.startTime
            roomInfo.signinTime = self._instCtrl.signinTime
        return roomInfo

    def _doLoad(self):
        assert (self._state == MatchMaster.ST_ALL_AREA_ONLINE)
        self._state = MatchMaster.ST_LOAD

        self._logger.info('MatchMaster._doLoad ...',
                          'state=', self._state)

        timestamp = fttime.getCurrentTimestamp()
        startTime = self.matchConf.startConf.calcNextStartTime(timestamp)
        status = self.matchStatusDao.load(self.gameId, self.matchId)
        needLoad = False

        if status:
            # 如果没有下一场了，或者当前场已经过期
            if startTime is None or startTime != status.startTime:
                # TODO 清理matchStatusDao数据
                self._cancelInst(status.instId, MatchFinishReason.TIMEOUT)
                status.seq += 1
            else:
                needLoad = True
            status.startTime = startTime
        else:
            status = StageMatchStatus(self.matchId, 1, startTime)

        self.matchStatusDao.save(self.gameId, status)

        basedao.removeRoomInfo(self.gameId, self.roomId)

        if status.startTime or self.matchConf.startConf.isUserCountType():
            self._instCtrl = MatchInstCtrl(self, status, needLoad)
            self._instCtrl.start()
            roomInfoInst = self._buildRoomInfo()
            basedao.saveRoomInfo(self.gameId, roomInfoInst)

        self._logger.info('MatchMaster._doLoad ok',
                          'state=', self._state,
                          'instId=', self._instCtrl.instId if self._instCtrl else None)

    def _cancelInst(self, instId, reason):
        for areaStub in self._areaStubList[::-1]:
            try:
                areaStub.cancelInst(instId, reason)
            except:
                self._logger.error('MatchMaster._cancelInst',
                                   'roomId=', areaStub.roomId)

        self._logger.info('MatchMaster._cancelInst ok',
                          'instId=', instId,
                          'reason=', reason)

    def _setupNextInst(self, instCtrl, signers):
        timestamp = fttime.getCurrentTimestamp()
        startTime = self.matchConf.startConf.calcNextStartTime(timestamp + 1)
        if startTime or self.matchConf.startConf.isUserCountType():
            needLoad = False
            status = StageMatchStatus(self.matchId, instCtrl.status.seq + 1, startTime)
            if signers:
                needLoad = True
                instCtrl._moveToNext(status.instId, signers)
            self.matchStatusDao.save(self.gameId, status)
            self._instCtrl = MatchInstCtrl(self, status, needLoad)
            self._instCtrl.start()
        else:
            self._instCtrl = None
            if signers:
                instCtrl._cancelSigners(MatchFinishReason.USER_NOT_ENOUGH, signers)
            basedao.removeRoomInfo(self.gameId, self.roomId)
        self._logger.hinfo('MatchMaster._setupNextInst ok',
                           'instId=', instCtrl.instId,
                           'timestamp=', timestamp,
                           'nextInstId=', self._instCtrl.instId if self._instCtrl else None,
                           'startTime=', self._instCtrl.startTime if self._instCtrl else None,
                           'signinTime=', self._instCtrl.signinTime if self._instCtrl else None,
                           'signers=', [s.userId for s in signers] if signers else None)
        return self._instCtrl



if __name__ == '__main__':
    gs = MatchGroupStatus('groupId', 'matchingId', 'state', 'uncompleteTableCount', 'remTimes', 'lastActiveTime',
                          'playerCount')
    d = gs.toDict()
    decodedGS = MatchGroupStatus.fromDict(d)
