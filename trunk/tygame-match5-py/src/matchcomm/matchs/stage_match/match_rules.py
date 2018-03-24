# -*- coding:utf-8 -*-
"""
Created on 2017年8月14日

@author: zhaojiangang
"""
import time

from freetime5.util import ftsortedlist as sortedlist
from matchcomm.matchs.const import MatchFinishReason, MatchWaitReason, \
    MatchPlayerState
from matchcomm.matchs.models import StageMatchPlayer
from matchcomm.matchs.stage_match.conf import StageMatchRulesConfASS, \
    StageMatchRulesConfDieout
from matchcomm.matchs.utils import MatchProcesser, Logger, unlockUserForMatch, lockUserForMatch
from matchcomm.util.orderdedict import LastUpdatedOrderedDict


class StageMatchRules(object):

    def __init__(self, group):
        super(StageMatchRules, self).__init__()
        self.group = group

    @property
    def area(self):
        return self.group.area

    @property
    def matchConf(self):
        return self.group.matchConf

    @property
    def stageConf(self):
        """
        本阶段配置
        """
        return self.group.stageConf

    @property
    def matchId(self):
        return self.group.matchId

    @property
    def instId(self):
        return self.group.instId

    @property
    def roomId(self):
        return self.group.roomId

    @property
    def matchingId(self):
        return self.group.matchingId

    @property
    def groupId(self):
        return self.group.groupId

    @property
    def playerCount(self):
        return len(self.group._playerMap)

    @property
    def stageIndex(self):
        return self.group.stageIndex

    @property
    def startStageIndex(self):
        return self.group.startStageIndex

    @property
    def endStageIndex(self):
        return self.group.endStageIndex

    def newPlayer(self, playerData):
        return StageMatchPlayer(playerData.userId)

    def init(self):
        """
        初始化赛制
        """
        pass

    def cleanup(self):
        """
        清理
        """
        pass

    def isFinished(self):
        """
        该赛制是否结束了
        """
        raise NotImplementedError

    def calcNeedTableCount(self):
        """
        计算该分组目前还需要多少张桌子
        """
        raise NotImplementedError

    def getUncompleteTableCount(self):
        """
        获取还有多少桌未完成
        """
        raise NotImplementedError

    def getRankList(self):
        """
        获取排行榜
        """
        raise NotImplementedError


class StageMatchNormalRules(StageMatchRules):
    def __init__(self, group):
        super(StageMatchNormalRules, self).__init__(group)
        # 排行榜
        self._rankList = []

        # 淘汰的玩家列表
        self._losePlayers = LastUpdatedOrderedDict()
        self._losePlayersProcesser = MatchProcesser(1, self._processLosePlayers)

        # 等待开局的玩家列表
        self._waitPlayers = []
        self._waitPlayersProcesser = MatchProcesser(0, self._processWaitPlayers)
        # 分好桌的玩家列表list< list<MatchPlayer> >
        self._tabledPlayers = []
        self._tabledPlayersProcesser = MatchProcesser(1, self._processTabledPlayers)
        # 刚刚结束一局的桌子
        self._winlosePlayersList = []
        self._winlosePlayersListProcesser = MatchProcesser(1, self._processWinlosePlayersList)
        # 已经完成局数的玩家
        self._finishCardCountPlayerSet = set()
        # 正在比赛的桌子
        self._busyTables = LastUpdatedOrderedDict()
        # 处理超时的桌子
        self._timeoutTableProcesser = MatchProcesser(1, self._processTimeoutTables)
        # 结束原因
        self._finishReason = MatchFinishReason.FINISH
        # 底分
        self._baseScore = group.stageConf.baseScore

        # 日志
        self._logger = Logger()
        self._logger.add('matchId', self.matchId)
        self._logger.add('instId', self.instId)
        self._logger.add('matchingId', self.matchingId)
        self._logger.add('groupId', self.groupId)
        self._logger.add('stageIndex', self.stageIndex)

    @property
    def baseScore(self):
        return self._baseScore

    def init(self):
        """
        开始该分组
        """
        # 初始化排行榜
        self._initRankList()
        # 初始化等待队列
        self._initWaitPlayers()
        # 初始化底分
        self._baseScore = self.stageConf.baseScore
        self._startProcessers()

    def cleanup(self):
        self._logger.info('StageMatchNormalRules.cleanup')

        self._stopProcessers()
        self._finishCardCountPlayerSet.clear()
        self._winlosePlayersList = []
        self._rankList = []
        self._clearBusyTables()

    def isFinished(self):
        """
        该赛制是否结束了
        """
        return len(self._finishCardCountPlayerSet) >= len(self._rankList)

    def calcNeedTableCount(self):
        """
        计算该分组目前还需要多少张桌子
        """
        return (self.playerCount + self.matchConf.tableSeatCount - 1) / self.matchConf.tableSeatCount

    def getUncompleteTableCount(self):
        """
        获取还有多少桌未完成
        """
        busyTableCount = len(self._busyTables)
        tabledCount = len(self._tabledPlayers)
        winloseTableCount = len(self._winlosePlayersList)
        return int(busyTableCount + tabledCount + winloseTableCount)

    def getRankList(self):
        """
        获取排行榜
        """
        return self._rankList

    def tableWinlose(self, tableId, ccrc, seatWinloses, isKill=False):
        """
        桌子一局结束
        """
        table = self._busyTables.get(tableId)
        if not table:
            self._logger.warn('StageMatchNormalRules.tableWinlose fail',
                              'tableId=', tableId,
                              'ccrc=', ccrc,
                              'seatWinloses=', seatWinloses,
                              'isKill=', isKill,
                              'err=', 'NotFoundTable')
            return False

        if table.ccrc != ccrc:
            self._logger.warn('StageMatchNormalRules.tableWinlose fail',
                              'tableId=', tableId,
                              'ccrc=', ccrc,
                              'seatWinloses=', seatWinloses,
                              'isKill=', isKill,
                              'err=', 'DiffCCRC')
            return False

        if len(seatWinloses.keys()) != table.seatCount:
            self._logger.warn('StageMatchNormalRules.tableWinlose fail',
                              'tableId=', tableId,
                              'ccrc=', ccrc,
                              'seatWinloses=', seatWinloses,
                              'isKill=', isKill,
                              'seatCount=', table.seatCount,
                              'seatWinloseCount=', len(seatWinloses),
                              'err=', 'DiffSeatCount')
            return False

        self._tableWinlose(table, seatWinloses, False)
        return True

    def _initRankList(self):
        # 初始化排行榜
        rankList = sorted(self.group._playerMap.values(), key=lambda p: (-p.score, p.signinTime, p.userId))
        self._initPlayerDatas(rankList)

        self._rankList = []
        for player in rankList:
            player._sortScore = self._calcPlayerSortScore(player)
            sortedlist.insert(self._rankList, player)
        self._updatePlayerRank(rankList)

    def _updatePlayerSortScore(self, player):
        """
        更新玩家积分及排名
        """
        newScore = self._calcPlayerSortScore(player)
        if newScore != player._sortScore:
            sortedlist.remove(self._rankList, player)
            player._sortScore = newScore
            sortedlist.insert(self._rankList, player)

    def _updatePlayerRank(self, rankList):
        """
        更新排行榜排名
        """
        for i, player in enumerate(rankList):
            player.rank = i + 1
            self.area.playerNotifier.notifyMatchRank(player)

    def _calcPlayerSortScore(self, player):
        """
        计算玩家排序积分
        """
        return (-player.score, player.signinTime, player.userId)

    def _initPlayerDatas(self, rankList):
        """
        初始化玩家数据
        """
        scoreCalc = self.group.stageConf.scoreCalcFac.newCalc(rankList)
        for player in rankList:
            score = scoreCalc.calc(player.score)
            if self._logger.isDebug():
                self._logger.debug('StageMatchNormalRules._initPlayerDatas',
                                   'userId=', player.userId,
                                   'calc=', scoreCalc,
                                   'oldScore=', player.score,
                                   'newScore=', score)
            player.score = score
            player.cardCount = 0
            player.tableRank = 0

    def _startProcessers(self):
        self._losePlayersProcesser.start()
        self._waitPlayersProcesser.start()
        self._tabledPlayersProcesser.start()
        self._winlosePlayersListProcesser.start()
        self._timeoutTableProcesser.start()

    def _stopProcessers(self):
        self._losePlayersProcesser.stop()
        self._waitPlayersProcesser.stop()
        self._tabledPlayersProcesser.stop()
        self._winlosePlayersListProcesser.stop()
        self._timeoutTableProcesser.stop()

    def _clearBusyTables(self):
        while self._busyTables:
            table = self._busyTables.popitem()
            self.area.tableController.clearTable(table)
            self._clearAndReleaseTable(table)
        self._busyTables.clear()

    def _processWaitPlayers(self):
        """
        处理等待队列
        """
        if self._logger.isDebug():
            self._logger.debug('StageMatchNormalRules._processWaitPlayers',
                               'waitPlayerCount=', len(self._waitPlayers),
                               'finishPlayerCount=', len(self._finishCardCountPlayerSet),
                               'allPlayerCount=', len(self._rankList))

        tableSeatCount = self.matchConf.tableSeatCount
        needProcessCount = len(self._waitPlayers) / tableSeatCount * tableSeatCount
        if needProcessCount > 0:
            processedCount = 0
            while processedCount < needProcessCount:
                players = self._waitPlayers[processedCount:processedCount + tableSeatCount]
                # 从等待队列移入到配桌队列,每次移入tableSeatCount位
                self._addTabledPlayers(players)
                processedCount += tableSeatCount
            # 轮空的人员
            self._waitPlayers = self._waitPlayers[processedCount:]
            for player in self._waitPlayers:
                self.area.playerNotifier.notifyMatchWait(player, MatchWaitReason.WAIT_BYE)
        else:
            # 剩余的人数不足一桌且已经完成指定局数直接结束
            waitCount = len(self._waitPlayers)
            if waitCount > 0 and (waitCount + len(self._finishCardCountPlayerSet) >= len(self._rankList)):
                for player in self._waitPlayers:
                    self._logger.info('StageMatchNormalRules._processWaitPlayers FinishCardCount',
                                      'waitPlayerCount=', waitCount,
                                      'finishPlayerCount=', len(self._finishCardCountPlayerSet),
                                      'allPlayerCount=', len(self._rankList),
                                      'userId=', player.userId)
                    self._playerFinishCardCount(player)
                self._waitPlayers = []
        return 2

    def _processTabledPlayers(self):
        """
        处理分好桌的玩家
        """
        if self._logger.isDebug():
            self._logger.debug('StageMatchNormalRules._processTabledPlayers',
                               'tabledCount=', len(self._tabledPlayers))

        while self._tabledPlayers:
            players = self._tabledPlayers.pop(0)
            table = self._borrowTable()
            table.playTime = time.time()
            table.ccrc += 1
            for player in players:
                player.cardCount += 1
                table.sitdown(player)
                # 移除断线重连标示位
                unlockUserForMatch(player.userId, self.group.roomId)

            # 启动桌子
            self.area.tableController.startTable(table)
        return 1

    def _processWinlosePlayersList(self):
        """
        处理一局结束的玩家
        """
        if self._logger.isDebug():
            self._logger.debug('StageMatchNormalRules._processWinlosePlayersList',
                               'winloseTableCount=', len(self._winlosePlayersList))

        while self._winlosePlayersList:
            playerList = self._winlosePlayersList.pop(0)
            # 桌子排序
            self._sortTableRank(playerList)

            for player in playerList:
                self._updatePlayerSortScore(player)

            # 更新排名
            self._updatePlayerRank(self._rankList)

            # 子类自己处理
            self._doPlayersWinlose(playerList)
        return 2

    def _processLosePlayers(self):
        """
        处理淘汰的玩家
        """
        return 1

    def _processTimeoutTables(self):
        """
        处理超时的桌子
        """
        if self._logger.isDebug():
            self._logger.debug('StageMatchNormalRules._processTimeoutTables')

        timeoutTables = []
        nowTime = time.time()
        for table in self._busyTables.values():
            if nowTime - table.playTime >= self.matchConf.startConf.tableTimes:
                timeoutTables.append(table)
            else:
                break

        for table in timeoutTables:
            if nowTime - table.playTime >= self.matchConf.startConf.tableTimes:
                self._logger.info('StageMatchNormalRules._processTimeoutTables tableTimeout',
                                  'tableId=', table.tableId,
                                  'userIds=', [seat.userId for seat in table.seats])

                seatWinloses = self._seatWinloseForTimeout(table)
                assert (len(seatWinloses.keys()) == table.seatCount)
                self._tableWinlose(table, seatWinloses, True)
        return 2

    def _tableWinlose(self, table, seatWinloses, isKill):
        """
        桌子一局结束，进行结算
        """
        # players = []
        # for i, seat in enumerate(table.seats):
        #     player = seat.player
        #     if player:
        #         players.append(player)
        #         player.score += seatWinloses[i]

        players = []
        for i, seat in enumerate(table.seats):
            player = seat.player
            if player:
                players.append(player)
                player.score += seatWinloses.get(player.userId)

        self._logger.info('StageMatchNormalRules._tableWinlose',
                          'tableId=', table.tableId,
                          'seatWinlose=', seatWinloses,
                          'users=', [(seat.userId, seat.player.score if seat.player else None) for seat in table.seats],
                          'isKill=', isKill)

        self._clearAndReleaseTable(table)
        # 从开桌列表移入结束一局的桌子
        self._winlosePlayersList.append(players)

    def _seatWinloseForTimeout(self, table):
        # seatWinloses = []
        # for _ in table.seats:
        #     seatWinloses.append(0)
        # return seatWinloses
        return {_.userId: 0 for _ in table.seats}

    def _sortTableRank(self, playerList):
        playerList.sort(key=lambda x: (-x.score, x.signinTime, x.userId))
        for i, player in enumerate(playerList):
            player.tableRank = i + 1

    def _clearAndReleaseTable(self, table):
        # 清理桌子
        self.area.tableController.clearTable(table)

        for seat in table.seats:
            if seat.player:
                # 添加断线重连标示位
                if not seat.player.isQuit:
                    lockUserForMatch(seat.player.userId, self.group.roomId)
                table.standup(seat.player)

        # 清理桌子
        self._backTable(table)

    def _addWaitPlayer(self, player):
        player.waitReason = MatchWaitReason.WAIT_TABLE
        self._waitPlayers.append(player)

    def _addTabledPlayers(self, players):
        self._tabledPlayers.append(players)

    def _initWaitPlayers(self):
        # 第一阶段需要处理在其它牌桌打牌的玩家
        for player in self._rankList:
            self.area.matchPlayerIF.savePlayer(self.matchId, player.userId, self.instId, self.roomId,
                                               MatchPlayerState.PLAYING)
            if self.stageIndex != self.startStageIndex:
                # 其它阶段晋级
                self.area.playerNotifier.notifyStageStart(player)
            else:
                # 第一阶段补充等待配桌
                self.area.playerNotifier.notifyMatchWait(player, MatchWaitReason.WAIT_FIRST)

            self._addWaitPlayer(player)

    def _doPlayersWinlose(self, playerList):
        """
        子类自己实现，处理刚刚结束一局牌的玩家列表
        """
        raise NotImplementedError

    def _borrowTable(self):
        table = self.group.borrowTable()
        self._busyTables[table.tableId] = table
        table._group = self.group
        return table

    def _backTable(self, table):
        table._group = None
        table.playTime = None
        self._busyTables.safepop(table.tableId)
        self.group.backTable(table)

    def _playerFinishCardCount(self, player):
        """
        玩家完成了当前阶段局数
        """
        player.waitReason = MatchWaitReason.WAIT_RISE
        self._finishCardCountPlayerSet.add(player)

    def _outPlayer(self, player, reason=MatchFinishReason.FINISH):
        """
        踢出player
        """
        assert (player.seat is None)

        self._logger.info('StageMatchNormalRules._outPlayer',
                          'userId=', player.userId,
                          'reason=', reason)

        # 删除已完成cardCount的用户
        self._finishCardCountPlayerSet.discard(player)
        # 删除排行榜中的用户
        sortedlist.remove(self._rankList, player)
        # 玩家完成比赛
        if player.isQuit:
            self.group.playerMatchOver(player, MatchFinishReason.GIVE_UP)
        else:
            self.group.playerMatchOver(player, reason)


class StageMatchNormalRulesASS(StageMatchNormalRules):
    def __init__(self, group):
        super(StageMatchNormalRulesASS, self).__init__(group)
        # 在其它牌桌打牌的玩家进入该队列，超时之后踢出
        self._busyTimeout = None
        self._busyPlayers = LastUpdatedOrderedDict()
        self._busyPlayersProcesser = None
        # 底分增长器
        self._baseScoreGrow = group.stageConf.rulesConf.baseScoreGrowFactory.newScoreGrow()
        # 底分增长处理器
        self._baseScoreGrowProcesser = MatchProcesser(self.stageConf.rulesConf.baseScoreGrowTimes,
                                                      self._processBaseScoreGrow)
        # 淘汰分
        self._loseScore = self.stageConf.rulesConf.loseScoreCalc.calcLoseScore(self._baseScore)

    @property
    def loseScore(self):
        return self._loseScore

    def _startProcessers(self):
        super(StageMatchNormalRulesASS, self)._startProcessers()
        if self.stageIndex == 0 and self.stageConf.delayEntryTimes > 0:
            self._busyTimeout = time.time() + self.stageConf.delayEntryTimes
            self._busyPlayersProcesser = MatchProcesser(1, self._processBusyPlayers)
            self._busyPlayersProcesser.start()
        self._baseScoreGrowProcesser.start()

    def _stopProcessers(self):
        super(StageMatchNormalRulesASS, self)._stopProcessers()
        if self._busyPlayersProcesser:
            self._busyPlayersProcesser.stop()
        self._baseScoreGrowProcesser.stop()

    def _processBaseScoreGrow(self):
        self._baseScore = self._baseScoreGrow.grow(self._baseScore)
        self._loseScore = self.stageConf.rulesConf.loseScoreCalc.calcLoseScore(self._baseScore)

    # def _initWaitPlayers(self):
    #     # 第一阶段需要处理在其它牌桌打牌的玩家
    #     # TODO 还不太理解
    #     if self.stageIndex == 0:
    #         for player in self._rankList:
    #             # 看当前玩家是否在其它牌桌，如果在则放到busy队列
    #             self.area.matchPlayerIF.savePlayer(self.matchId, player.userId, self.instId, self.roomId,
    #                                                MatchPlayerState.PLAYING)
    #             if not self.area.matchPlayerIF.setPlayerActive(self.matchId, player.userId):
    #                 self._busyPlayers[player.userId] = player
    #             else:
    #                 self.area.playerNotifier.notifyStageStart(player)
    #                 self._addWaitPlayer(player)
    #     else:
    #         super(StageMatchNormalRulesASS, self)._initWaitPlayers()

    def _processBusyPlayers(self):
        """
        处理在其它牌桌上忙着的玩家
        """
        if self._busyPlayers:
            if time.time() >= self._busyTimeout:
                while self._busyPlayers:
                    _, player = self._busyPlayers.popitem()
                    self._outPlayer(player, MatchFinishReason.TIMEOUT)
        else:
            self._busyPlayersProcesser.stop()

        return 1

    def _doPlayersWinlose(self, playerList):
        """
        子类自己实现，处理刚刚结束一局牌的玩家列表
        """
        if self._logger.isDebug():
            self._logger.debug('StageMatchNormalRulesASS._doPlayersWinlose',
                               'userIds=', [p.userId for p in playerList])

        playerList.sort(key=lambda p: p.score)

        for player in playerList:
            # 打立阶段玩家退赛直接淘汰
            if player.isQuit:
                player.lastRank = len(self._rankList)
                self._outPlayer(player, MatchFinishReason.GIVE_UP)
                self._logger.info('StageMatchNormalRulesASS player give up',
                                  'userId=', player.userId)
                continue
            if len(self._rankList) <= self.stageConf.rulesConf.riseUserRefer:
                self._playerFinishCardCount(player)
                self.area.playerNotifier.notifyMatchWait(player, MatchWaitReason.WAIT_RISE)
            else:
                if player.score <= self._loseScore:
                    self._outPlayer(player, MatchFinishReason.FINISH)
                else:
                    if player.cardCount >= self.stageConf.cardCount:
                        self._playerFinishCardCount(player)
                        # 玩家已经打完规定手数，但是还不确定是否晋级
                        self.area.playerNotifier.notifyMatchWait(player, MatchWaitReason.WAIT_RISE)
                    else:
                        # 加入等待列表，重新分桌
                        self._addWaitPlayer(player)
                        self.area.playerNotifier.notifyMatchWait(player, MatchWaitReason.WAIT_TABLE)


class StageMatchNormalRulesDieout(StageMatchNormalRules):
    def __init__(self, group):
        super(StageMatchNormalRulesDieout, self).__init__(group)

    def _initPlayerDatas(self, rankList):
        """
        初始化玩家数据
        """
        scoreCalc = self.group.stageConf.scoreCalcFac.newCalc(rankList)
        for player in rankList:
            score = scoreCalc.calc(player.score)
            if self._logger.isDebug():
                self._logger.debug('StageMatchNormalRulesDieout._initPlayerDatas',
                                   'userId=', player.userId,
                                   'calc=', scoreCalc,
                                   'oldScore=', player.score,
                                   'newScore=', score)
            player.score = score
            player.cardCount = 0
            player.tableRank = 999

    def _calcPlayerSortScore(self, player):
        """
        计算玩家排序积分.理论上定局积分需要使用本桌排名进行计算，实际上可能导致麻将游戏中积分低但是桌上排名高的问题，然后排名靠前的问题。
        """
        # return (player.tableRank, -player.score, player.signinTime, player.userId)
        return (-player.score, player.tableRank, player.signinTime, player.userId)

    def _doPlayersWinlose(self, playerList):
        """
        子类自己实现，处理刚刚结束一局牌的玩家列表
        """
        if self._logger.isDebug():
            self._logger.debug('StageMatchNormalRulesDieout._doPlayersWinlose',
                               'userIds=', [p.userId for p in playerList])

        playerList.sort(key=lambda p: p.tableRank)

        if playerList[0].cardCount >= self.stageConf.cardCount:
            for player in playerList:
                # 玩家完成了指定的牌数
                self._playerFinishCardCount(player)
                if self.stageIndex != self.endStageIndex:
                    # 玩家已经完成游戏手数，是否晋级需要等待其它桌成绩
                    self.area.playerNotifier.notifyMatchWait(player, MatchWaitReason.WAIT_RISE)
                if player.isQuit and not player.lastRank:
                    player.lastRank = len(self._rankList)
        else:
            # 继续开桌，并不进行再分桌
            self._addTabledPlayers(playerList)

            for player in playerList:
                self.area.playerNotifier.notifyMatchWait(player, MatchWaitReason.WAIT_TABLE)
                if player.isQuit and not player.lastRank:
                    player.lastRank = len(self._rankList)


class StageMatchRulesFactory(object):
    _factoryMap = {
        StageMatchRulesConfASS.TYPE_ID: StageMatchNormalRulesASS,
        StageMatchRulesConfDieout.TYPE_ID: StageMatchNormalRulesDieout
    }

    @classmethod
    def registerMatchRules(cls, typeId, fac):
        cls._factoryMap[typeId] = fac

    @classmethod
    def newMatchRules(self, group):
        fac = self._factoryMap.get(group.stageConf.rulesConf.TYPE_ID)
        return fac(group)
