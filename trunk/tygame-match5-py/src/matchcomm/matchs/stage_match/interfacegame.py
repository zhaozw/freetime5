# -*- coding:utf-8 -*-
"""
Created on 2016年1月20日

@author: zhaojiangang
"""
from datetime import datetime
import time

from freetime5.util import ftlog
from freetime5.util import fttime
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tyrpcconn
from tuyoo5.core import tyconst
from tuyoo5.core.typlugin import hallRpcOne


from matchcomm.matchs.const import MatchFinishReason,StageType
from matchcomm.matchs.const import MatchWaitReason
from matchcomm.matchs.interface import MatchTableController, MatchPlayerNotifier, \
    MatchRankRewardsIF, MatchRecordDaoRedis
from matchcomm.matchs.report import PokerMatchReport
from matchcomm.matchs.stage_match.conf import StageMatchRulesConfASS, StageMatchRulesConfDieout
from matchcomm.matchs.stage_match.match import MatchInst
from matchcomm.matchs.utils import getRiseWaitTime, MatchBIUtils
from matchcomm.servers.table.rpc import stage_match_table_remote



def _getStageType(group):
    return StageType.ASS if isinstance(group.stageConf.rulesConf, StageMatchRulesConfASS) else StageType.DIEOUT


def _getMatchGroupStepInfos(group, table):
    infoscores = []
    inforanks = []
    cardCount = 0
    for seat in table.seats:
        if seat.player:
            infoscores.append(seat.player.score)
            inforanks.append(seat.player.rank)
            cardCount += seat.player.cardCount
        else:
            infoscores.append(0)
            inforanks.append(0)
    cardCount = cardCount / len(table.seats)
    step = u'当前第%d阶段,第%d副' % (group.stageIndex + 1, cardCount)
    upcount = group.stageConf.riseUserCount

    matchRules = group.matchRules
    assLoseScore = matchRules.baseScore
    if StageType.ASS == _getStageType(group):
        mtype = u'ASS打立出局'
        bscore = u'底分:%d,低于%d将被淘汰' % (matchRules.baseScore, matchRules.loseScore)
        outline = ['淘汰分:', str(matchRules.loseScore)]
        incrnote = u'底分增加到%d低于%d将被淘汰' % (matchRules.baseScore, matchRules.loseScore)
        assLoseScore = group.matchRules.loseScore
    else:  #
        mtype = u'定局淘汰'
        bscore = u'底分:%d,%d人晋级' % (matchRules.baseScore, upcount)
        outline = ['局数:', str(cardCount) + '/' + str(group.stageConf.cardCount)]
        incrnote = u'底分增加到%d' % (matchRules.baseScore)

    isStartStep = (cardCount == 1 and group.stageIndex == 0)
    isFinalStep = (cardCount == 1 and (group.stageIndex + 1 >= len(group.matchConf.stages)))

    mInfos = {'scores': infoscores,  # 座位排序
              'rank': inforanks,  # 名次
              'all': len(group.rankList),  # 总人数
              'info': [outline,
                       ["晋级人数:", str(upcount)]
                       ],
              'basescore': matchRules.baseScore,
              'asslosechip': assLoseScore,
              }
    return mtype, step, bscore, isStartStep, isFinalStep, incrnote, mInfos


def _buildTableClearMessage(table):
    msg = MsgPack()
    msg.setCmd('table_manage')
    msg.setParam('action', 'm_table_clear')
    msg.setParam('gameId', table.gameId)
    msg.setParam('roomId', table.roomId)
    msg.setParam('tableId', table.tableId)
    msg.setParam('ccrc', table.ccrc)
    if table.group:
        msg.setParam('matchId', table.group.area.matchId)
    if ftlog.is_debug():
        ftlog.debug('_buildTableClearMessage',
                    'msg=', msg)
    return msg


def _buildTableStartMessage(table):
    msg = MsgPack()
    msg.setCmd('table_manage')
    msg.setParam('action', 'm_table_start')
    msg.setParam('gameId', table.gameId)
    msg.setParam('roomId', table.roomId)
    msg.setParam('tableId', table.tableId)
    msg.setParam('ccrc', table.ccrc)
    if table.group:
        msg.setParam('matchId', table.group.area.matchId)
        msg.setParam('groupId', table.group.groupId)
        msg.setParam('stageType', _getStageType(table.group))
        msg.setParam('stageName', table.group.stageConf.name)

        startTimeStr = datetime.fromtimestamp(table.group.startTime).strftime('%Y-%m-%d %H:%M')
        mtype, step, bscore, isStartStep, isFinalStep, incrnote, mInfos = _getMatchGroupStepInfos(table.group, table)
        notes = {'basescore': bscore, 'type': mtype, 'step': step,
                 'isStartStep': isStartStep, 'isFinalStep': isFinalStep,
                 'startTime': startTimeStr, 'incrnote': incrnote}
        msg.setParam('baseScore', bscore)

        ranktops = [[player.userId, player.userName, player.score, player.signinTime] for player in
                    table.group.rankList]
        msg.setParam('ranks', ranktops)

        seats = []
        totalCardCount = 0
        for seat in table.seats:
            if seat.player:
                totalCardCount += max(0, seat.player.cardCount - 1)
                seats.append({
                    'userId': seat.player.userId,
                    'cardCount': seat.player.cardCount,
                    'rank': seat.player.rank,
                    'chiprank': seat.player.rank,
                    'userName': seat.player.userName,
                    'score': seat.player.score,
                    'isQuit': seat.player.isQuit,
                    'championLimitFlag': False,
                    'firstCallFalg': 0
                })
            else:
                seats.append({
                    'userId': 0,
                    'cardCount': 0,
                    'rank': 0,
                    'chiprank': 0,
                    'userName': '',
                    'score': 0,
                    'isQuit': False,
                    'championLimitFlag': False,
                    'firstCallFalg': 0
                })

        msg.setParam('seats', seats)
        step = {
            'name': table.group.groupName if table.group.isGrouping else table.group.stageConf.name,
            'type': _getStageType(table.group),
            'playerCount': table.group.startPlayerCount,
            'riseCount': min(table.group.stageConf.riseUserCount, table.group.startPlayerCount),
            'cardCount': table.group.stageConf.cardCount,
            'callType': table.group.stageConf.getParam('call.type', 'random'),
            'stageIndex': table.group.stageIndex
        }
        msg.setParam('extend', {"mnotes": notes, "mInfos": mInfos, "step": step})

    if ftlog.is_debug():
        ftlog.debug('_buildTableInfoMessage',
                    'msg=', msg)
    return msg


def getMatchName(room, player):
    if player.group.isGrouping:
        return '%s%s' % (room.conf.name, player.group.groupName)
    return room.conf.name


def buildLoserInfo(room, player):
    info = None
    if isinstance(player.group.matchRules, StageMatchRulesConfASS):
        checkScore = player.group.matchRules.loseScore
        if player.score < checkScore:
            info = u'由于积分低于' + str(checkScore) + u',您已经被淘汰出局.请再接再厉,争取取得更好名次!'
    if info is None:
        info = u'比赛：%s\n名次：第%d名\n胜败乃兵家常事 大侠请重新来过！' % (getMatchName(room, player), player.rank)
    return info


def buildWinInfo(room, player, rankRewards):
    if rankRewards:
        return u'比赛：%s\n名次：第%d名\n奖励：%s\n奖励已发放，请您查收。' % (getMatchName(room, player), player.rank, rankRewards.desc)
    return u'比赛：%s\n名次：第%d名\n' % (getMatchName(room, player), player.rank)


def _buildWaitInfoMsg(player):
    conf = {}
    if player.waitReason == MatchWaitReason.WAIT_BYE:
        # 轮空提示
        return conf.get('byeMsg', u'轮空等待')
    elif player.waitReason == MatchWaitReason.WAIT_RISE:
        # 晋级等待
        if player.rank < player.group.stageConf.riseUserCount:
            return conf.get('maybeRiseMsg', u'您非常有可能晋级，请耐心等待')
        else:
            return conf.get('riseMsg', u'请耐心等待其他玩家')
    return conf.get('waitMsg', u'请耐心等待其他玩家')


def _getMatchProgress(player):
    return player.group.calcTotalRemTimes(fttime.getCurrentTimestamp())


def _getMatchCurTimeLeft(inst):
    timestamp = fttime.getCurrentTimestamp()
    if (inst
        and inst.matchConf.startConf.isTimingType()
        and inst.state < inst.ST_START
        and inst.startTime > timestamp):
        return inst.startTime - timestamp
    return 0


def _convertState(state):
    if (state >= MatchInst.ST_IDLE
        and state < MatchInst.ST_START):
        return 0
    if (state >= MatchInst.ST_START
        and state < MatchInst.ST_FINAL):
        return 10
    return 20




class PokerMatchTableController(MatchTableController):
    def startTable(self, table):
        """
        让player在具体的游戏中坐到seat上
        """
        try:
            ftlog.info('PokerMatchTableController.startTable',
                       'groupId=', table.group.groupId,
                       'tableId=', table.tableId,
                       'ccrc=', table.ccrc,
                       'roomId=', table.roomId,
                       'userIds=', table.getUserIdList())

            # 统计阶段的局数
            sequence = int(table.group.instId.split('.')[1])
            groupNum = table.group.groupId.split('.')[-1]
            userIds = table.getUserIdList()
            PokerMatchReport.reportMatchEvent("MATCH_START_TABLE", userIds[0] if userIds else 0,table.group.area.gameId,
                                              table.group.matchId,
                                           table.tableId, sequence, 0,
                                           [table.group.stageIndex, groupNum, table.group.startPlayerCount,
                                            table.group.stageConf.cardCount])

            # 发送tableStart
            message = _buildTableStartMessage(table)
            tableInfo = message.getKey('params')
            stage_match_table_remote.doStartTable(table.roomId, table.tableId, tableInfo)
        except:
            ftlog.error('PokerMatchTableController.startTable',
                        'groupId=', table.group.groupId,
                        'tableId=', table.tableId,
                        'roomId=', table.roomId,
                        'userIds=', table.getUserIdList())

    def clearTable(self, table):
        """
        清理桌子
        """
        try:
            ftlog.info('PokerMatchTableController.clearTable',
                       'groupId=', table.group.groupId,
                       'tableId=', table.tableId,
                       'roomId=', table.roomId,
                       'userIds=', table.getUserIdList())
            message = _buildTableClearMessage(table)
            tableInfo = message.getKey('params')
            stage_match_table_remote.doClearTable(table.roomId, table.tableId, tableInfo)
        except:
            ftlog.error('PokerMatchTableController.clearTable',
                        'groupId=', table.group.groupId,
                        'tableId=', table.tableId,
                        'roomId=', table.roomId,
                        'userIds=', table.getUserIdList())

    def playerGiveUp(self, roomId, tableId, userId):
        """
        玩家放弃比赛
        """
        try:
            ftlog.info('PokerMatchTableController.playerGiveUp',
                       'userId=', userId)
            stage_match_table_remote.doGiveUp(roomId, tableId, userId)
        except:
            ftlog.error('PokerMatchTableController.playerGiveUp',
                        'userId=', userId)

def convertReason(reason):
    if reason == MatchFinishReason.FINISH:
        return 2
    if reason == MatchFinishReason.USER_NOT_ENOUGH:
        return 3
    if reason == MatchFinishReason.RESOURCE_NOT_ENOUGH:
        return 4
    return 7


class PokerMatchPlayerNotifier(MatchPlayerNotifier):
    def __init__(self, room):
        self.room = room

    #     FINISH = 0
    #     USER_WIN = 1
    #     USER_LOSER = 2
    #     USER_NOT_ENOUGH = 3
    #     RESOURCE_NOT_ENOUGH = 4
    #     USER_LEAVE = 5
    #     OVERTIME = 7

    def notifyMatchSignsUpdate(self, userId):
        """
        通知用户已报名列表有更新
        """
        try:
            ftlog.info('PokerMatchPlayerNotifier.notifyMatchSignsUpdate',
                       'userId=', userId)
            mo = MsgPack()
            mo.setCmd('match')
            mo.setResult('action', 'signs')
            mo.setResult('gameId', self.room.gameId)
            mo.setResult('userId', userId)
            roomList = self.room.matchArea.signinRecordDao.loadUserAll(userId, self.room.gameId)
            mo.setResult('rooms', roomList)
            tyrpcconn.sendToUser(mo, userId)
        except:
            ftlog.error('PokerMatchPlayerNotifier.notifyMatchSignsUpdate',
                        'userId=', userId)

    def notifyMatchCancelled(self, signer, reason):
        """
        通知用户比赛由于reason取消了
        """
        try:
            ftlog.info('PokerMatchPlayerNotifier.notifyMatchCancelled',
                       'userId=', signer.userId,
                       'reason=', reason)
            userId = signer.userId
            # TODO 确认用户已经上线
            player = self.room.matchArea.findPlayer(userId)
            if player and player.isQuit:
                return

            self.notifyMatchSignsUpdate(userId)

            msg = MsgPack()
            msg.setCmd('match')
            msg.setResult('action', 'cancel')
            msg.setResult('gameId', self.room.gameId)
            msg.setResult('roomId', self.room.bigRoomId)
            msg.setResult('reason', reason)
            msg.setResult('info', MatchFinishReason.toString(reason))
            tyrpcconn.sendToUser(msg, userId)

        except:
            ftlog.error('PokerMatchPlayerNotifier.notifyMatchCancelled',
                        'userId=', signer.userId,
                        'instId=', signer.instId,
                        'reason=', reason)

    def notifyMatchStart(self, instId, signers):
        """
        通知用户比赛开始
        """
        try:
            ftlog.info('PokerMatchPlayerNotifier.notifyMatchStart',
                       'instId=', instId,
                       'userCount=', len(signers))
            mstart = MsgPack()
            mstart.setCmd('match')
            mstart.setResult('action', 'start')
            mstart.setResult('gameId', self.room.gameId)
            mstart.setResult('roomId', self.room.bigRoomId)

            if signers and len(signers) > 0:
                userIds = []  # 已经报名的用户列表
                newUserIds = []  # 已经报名且进入比赛的用户列表
                for signer in signers:
                    uId = signer.userId
                    userIds.append(uId)
                    player = self.room.matchArea.findPlayer(uId)
                    if player and player.isQuit:
                        continue
                    newUserIds.append(uId)
                tyrpcconn.sendToUserList(newUserIds, mstart)
                sequence = int(instId.split('.')[1])
                datas = {'userIds': userIds, 'gameId': self.room.gameId, 'roomId': self.room.roomId, 'sequence':
                    sequence, 'index': 0}
                # FTTimer(2, self.notifyMatchStartDelayReport_, datas)

                ftlog.info('PokerMatchPlayerNotifier.notifyMatchStart begin send bi report async'
                           'instId=', instId,
                           'userCount=', len(signers))
        except:
            ftlog.error('PokerMatchPlayerNotifier.notifyMatchStart'
                        'instId=', instId,
                        'userCount=', len(signers))

    def notifyMatchWait(self, player, reason):
        """
        通知用户等待
        """
        try:
            ftlog.debug('PokerMatchPlayerNotifier.notifyMatchWait userId=', player.userId,
                        'clientId=', player.clientId,
                        'isQuit=', player.isQuit,
                        'reason=', reason,
                        'groupId=', player.group.groupId)
            if player.isQuit:
                return
            self._notifyMatchWait(player, reason)
        except:
            ftlog.error('PokerMatchPlayerNotifier.notifyMatchWait',
                        'userId=', player.userId,
                        'groupId=', player.group.groupId,
                        'clientId=', player.clientId)

    def notifyMatchOver(self, player, reason, rankRewards):
        """
        通知用户比赛结束了
        """
        try:
            ftlog.debug('PokerMatchPlayerNotifier.notifyMatchOver userId=', player.userId,
                        'clientId=', player.clientId,
                        'groupId=', player.group.groupId,
                        'isQuit=', player.isQuit,
                        'reason=', reason,
                        'rankRewards=', rankRewards)
            rank = player.lastRank if player.isQuit else player.rank
            if reason == MatchFinishReason.FINISH:
                try:
                    if rankRewards:
                        for reward in rankRewards.rewards:
                            chipType = MatchBIUtils.getBiChipType(reward['itemId'])
                            if chipType:
                                kindId = 0
                                if chipType == tyconst.CHIP_TYPE_ITEM:
                                    kindId = reward['itemId'].strip('item:')
                                    PokerMatchReport.reportMatchEvent('MATCH_FINISH', player.userId,
                                                                      self.room.gameId, self.room.matchArea.matchId,
                                                          0, 0, 0, [chipType, reward['count'], kindId, player.rank, 0])
                    else:
                        PokerMatchReport.reportMatchEvent('MATCH_FINISH', player.userId, self.room.gameId,
                                                          self.room.matchArea.matchId, 0, 0, 0, [0,0, 0, player.rank, 0])

                except:
                    ftlog.error('PokerMatchPlayerNotifier.notifyMatchOver',
                                'userId=', player.userId,
                                'groupId=', player.group.groupId,
                                'reason=', reason,
                                'rankRewards=', rankRewards)


                try:

                    event = {'gameId': self.room.gameId,
                             'userId': player.userId,
                             'matchId': self.room.matchArea.matchId,
                             'rank': rank,
                             'isGroup': 1 if player.group.isGrouping else 0}
                    # 更新最佳战绩
                    MatchRecordDaoRedis.updateAndSaveRecord(event)
                    rewardDesc = ""
                    if rankRewards:
                        rewardDesc = MatchBIUtils.buildRewardsDesc(rankRewards)
                    event2 ={
                        'gameId': self.room.gameId,
                        'userId': player.userId,
                        'matchId': self.room.matchArea.matchId,
                        'rank': rank,
                        'desc':rewardDesc
                    }
                    # 比赛记录保存
                    MatchRecordDaoRedis.addHistory(event2)
                except:
                    ftlog.error('PokerMatchPlayerNotifier.notifyMatchOver',
                                'gameId=', self.room.gameId,
                                'userId=', player.userId,
                                'reason=', reason,
                                'matchId=', self.room.matchArea.matchId,
                                'rank=', player.rank)

            msg = MsgPack()
            msg.setCmd('match')
            msg.setResult('action', 'over')
            msg.setResult('gameId', self.room.gameId)
            msg.setResult('roomId', self.room.bigRoomId)
            msg.setResult('userId', player.userId)
            # 增加报名时候的费用选项用于再来一局(TODO 定时赛再来一局是伪需求，因为开始时间间隔大)
            msg.setResult('feeIndex', player.feeIndex)
            msg.setResult('reason', 1 if rankRewards else 2)
            msg.setResult('rank', rank)

            if rankRewards:
                msg.setResult('info', buildWinInfo(self.room, player, rankRewards))
                msg.setResult('reward', MatchBIUtils.buildRewards(rankRewards.rewards))
                rewardDesc = MatchBIUtils.buildRewardsDesc(rankRewards)
                if rewardDesc:
                    msg.setResult('rewardDesc', rewardDesc)
            else:
                msg.setResult('info', buildLoserInfo(self.room, player))

            msg.setResult('mcount',
                          player.group.startPlayerCount if player.group.isGrouping else player.group.totalPlayerCount)

            msg.setResult('date', str(datetime.now().date().today()))
            msg.setResult('time', time.strftime('%H:%M', time.localtime(time.time())))
            msg.setResult('mname', getMatchName(self.room, player))

            record = MatchRecordDaoRedis.loadRecord(self.room.gameId, player.userId, self.room.bigRoomId)
            if record:
                msg.setResult('mrecord', {'bestRank': record.bestRank,
                                          'bestRankDate': record.bestRankDate,
                                          'isGroup': record.isGroup,
                                          'crownCount': record.crownCount,
                                          'playCount': record.playCount})
            else:
                msg.setResult('mrecord', {'bestRank': player.rank,
                                          'bestRankDate': fttime.fromtimestamp(time.time()),
                                          'isGroup': 1 if player.group.isGrouping else 0,
                                          'crownCount': 1 if player.rank == 1 else 0,
                                          'playCount': 1})

            # rankRewardsList = self.room.roomConf.get('matchConf', {}).get('rank.rewards', [])
            # rankRewardsList = self.room.conf.rankRewardsList
            # bigImg = rankRewardsList[0].get('bigImg', '') if rankRewardsList else ''
            # if bigImg:
            #     msg.setResult('bigImg', bigImg)

            if not player.isQuit:
                tyrpcconn.sendToUser(msg, player.userId)

            # if player.rank == 1 and self.room.roomConf.get('championLed') and not player.isQuit:
            #     # TODO 冠军发送Led通知所有其他玩家
            #     pass

            if reason in (
                    MatchFinishReason.USER_NOT_ENOUGH, MatchFinishReason.RESOURCE_NOT_ENOUGH) and not player.isQuit:
                self.notifyMatchSignsUpdate(player.userId)

            sequence = int(player.group.instId.split('.')[1])
            PokerMatchReport.reportMatchEvent("MATCH_FINISH", player.userId,self.room.gameId, player.group.matchId, 0, sequence, 0)
        except:
            ftlog.error('PokerMatchPlayerNotifier.notifyMatchOver',
                        'userId=', player.userId,
                        'groupId=', player.group.groupId,
                        'reason=', reason,
                        'rankRewards=', rankRewards)

    def _notifyMatchUpdate(self, userId):
        mp = MsgPack()
        mp.setCmd('match')
        mp.setResult('action', 'update')
        mp.setResult('gameId', self.room.gameId)
        mp.setResult('matchId', self.room.bigRoomId)
        mp.setResult('roomId', self.room.bigRoomId)
        player = self.room.matchArea.findPlayer(userId)
        if player:
            if player and player.isQuit:
                return
            self._buildMatchStatasByPlayer(player, mp)


        else:
            signer = self.room.matchArea.findSigner(userId)
            inst = signer.inst if signer else self.room.matchArea.curInst
            self._buildMatchStatasByInst(inst, mp)

        playerCount = self.room.matchArea.getTotalPlayerCount()
        mp.setResult('onlinePlayerCount', playerCount)
        signerCount = self.room.matchArea.getTotalSignerCount()
        mp.setResult('signinPlayerCount', signerCount)

        tyrpcconn.sendToUser(mp, userId)

    def _buildMatchStatasByPlayer(self, player, mp):
        mp.setResult('state', 20)
        mp.setResult('inst', player.instId)
        mp.setResult('curPlayer', player.group.playerCount)
        mp.setResult('curTimeLeft', 0)
        mp.setResult('startTime', '')

        tcount = player.group.calcTotalUncompleteTableCount()
        if (tcount > 1
            and player.group.stageConf.rulesConf.TYPE_ID == StageMatchRulesConfDieout.TYPE_ID
            and player.cardCount < player.group.stageConf.cardCount):
            # 定局需要减掉本桌
            tcount -= 1
            if ftlog.is_debug():
                ftlog.debug('PokerMatchPlayerNotifier.getMatchStatesByPlayer roomId=', self.room.bigRoomId,
                            'instId=', player.instId,
                            'userId=', player.userId,
                            'tcount=', tcount)

        progress = _getMatchProgress(player)
        allcount = player.group.playerCount
        # 可能未配桌，没有table
        # 定局积分默认tableRank为999
        wait_time = getRiseWaitTime(player.group.matchConf.startConf.tableAvgTimes,tcount)
        waitInfo = {
            'uncompleted': tcount,  # 还有几桌未完成
            'tableRank': '%d' % 0 if player.tableRank == 999 else player.tableRank,  # 本桌排名
            'rank': '%d/%d' % (player.rank, allcount),  # 总排名
            'wait_time': '%d' % wait_time,  # 剩余晋级时间
            'chip': player.score  # 当前积分
        }
        waitInfo['info'] = _buildWaitInfoMsg(player)
        mp.setResult('waitInfo', waitInfo)
        mp.setResult('progress', progress)
        return mp

    def _buildMatchStatasByInst(self, inst, mp):
        mp.setResult('state', _convertState(inst.state) if inst else 0)
        mp.setResult('inst', inst.instId if inst else str(self.room.roomId))
        mp.setResult('curPlayer', inst.getTotalSignerCount() if inst else 0)
        mp.setResult('curTimeLeft', _getMatchCurTimeLeft(inst))
        mp.setResult('startTime', inst.startTimeStr if inst else '')
        return mp

    def notifyMatchUpdate(self, userId):
        """
        通知比赛更新.
        比赛前，报名人数更新
        比赛中，参数人数更新
        """
        try:
            if ftlog.is_debug():
                ftlog.debug('PokerMatchPlayerNotifier.notifyMatchUpdate',
                            'userId=', userId)
            self._notifyMatchUpdate(userId)
        except:

            ftlog.error('PokerMatchPlayerNotifier.notifyMatchUpdate',
                        'userId=', userId)

    def _notifyMatchRank(self, player):
        msg = MsgPack()
        msg.setCmd('match')
        msg.setResult('action', 'rank')
        msg.setResult('gameId', self.room.gameId)
        msg.setResult('roomId', self.room.bigRoomId)
        ranktops = []
        # 首位添加自己的排名信息
        ranktops.append({'userId': player.userId,
                         'name': player.userName,
                         'score': player.score,
                         'rank': player.rank})
        # 添加TOP10信息
        for i, p in enumerate(player.group.rankList[0:10]):
            ranktops.append({'userId': p.userId, 'name': p.userName, 'score': p.score, 'rank': i + 1})
        # TODO 自己在Top10中需要处理
        msg.setResult('mranks', ranktops)
        tyrpcconn.sendToUser(msg, player.userId)

    def notifyMatchRank(self, player):
        """
        通知比赛排行榜
        """
        try:
            if ftlog.is_debug():
                ftlog.debug('PokerMatchPlayerNotifier.notifyMatchRank',
                            'userId=', player.userId,
                            'isQuit=', player.isQuit,
                            'groupId=', player.group.groupId,
                            'clientId=', player.clientId)
            if player.isQuit:
                return
            self._notifyMatchRank(player)
        except:
            ftlog.error('PokerMatchPlayerNotifier.notifyMatchRank',
                        'userId=', player.userId,
                        'groupId=', player.group.groupId,
                        'clientId=', player.clientId)

    def _notifyMatchWait(self, player, riseWait=0):
        msg = MsgPack()
        msg.setCmd('match')
        msg.setResult('action', 'wait')
        msg.setResult('gameId', self.room.gameId)
        msg.setResult('roomId', self.room.bigRoomId)
        msg.setResult('tableId', player.group.matchConf.tableId)
        msg.setResult('riseWait', riseWait)
        msg.setResult('cardCount', player.cardCount)
        msg.setResult('loseScore', player.group.matchRules.loseScore if player.group.stageConf.rulesConf.TYPE_ID ==
                                                   StageMatchRulesConfASS.TYPE_ID else 0)
        msg.setResult('mname', getMatchName(self.room, player))
        steps = []
        for i, stageConf in enumerate(player.group.matchConf.stages):
            isCurrent = True if i == player.group.stageIndex else False
            if stageConf.userCountPerGroup != 0:
                des = '每组%s人晋级' % (stageConf.riseUserCount)
            else:
                des = '%s人晋级' % (stageConf.riseUserCount)
            stepInfo = {'des': des}
            if isCurrent:
                stepInfo['isCurrent'] = 1
            stepInfo['name'] = stageConf.name
            steps.append(stepInfo)

        msg.setResult('steps', steps)
        ftlog.info('PokerMatchPlayerNotifier._notifyMatchWait',
                    'msg=', msg.pack())
        tyrpcconn.sendToUser(msg, player.userId)

    def _notifyStageStart(self, player):
        mo = MsgPack()
        mo.setCmd('match')
        mo.setResult('action', 'rise')
        mo.setResult('gameId', self.room.gameId)
        mo.setResult('roomId', self.room.bigRoomId)
        mo.setResult('stageIndex', player.group.stageIndex)
        tyrpcconn.sendToUser(mo, player.userId)

    def notifyStageStart(self, player):
        """
        通知用户进入下一阶段(晋级).
        """
        try:
            ftlog.info('PokerMatchPlayerNotifier.notifyStageStart',
                        'userId=', player.userId,
                        'isQuit=', player.isQuit,
                        'stageIndex=', player.group.stageIndex,
                        'startStageIndex=', player.group.startStageIndex,
                        'groupId=', player.group.groupId)
            if player.isQuit:
                return
            # 晋级
            self._notifyStageStart(player)
            # 晋级后配合客户端展示，发送wait协议告知阶段信息
            self._notifyMatchWait(player, MatchWaitReason.WAIT_FIRST)
        except:
            ftlog.error('PokerMatchPlayerNotifier.notifyStageStart',
                        'userId=', player.userId,
                        'clientId=', player.clientId,
                        'groupId=', player.group.groupId)

    def notifyMatchStartDelayReport_(self):
        # argl = FTTasklet.getCurrentFTTasklet().run_argl
        # datas = argl[0]
        # userIds = datas['userIds']
        # roomId = datas['roomId']
        # gameId = datas['gameId']
        # sequence = datas['sequence']
        # index = datas['index']
        # ftlog.info('PokerMatchPlayerNotifier.notifyMatchStartDelayReport_',
        #            'index=', index,
        #            'total=', len(userIds))
        # nindex = self.notifyMatchStartDelayReport(userIds, gameId,roomId, sequence, index)
        # if nindex < 0:
        #     ftlog.info('PokerMatchPlayerNotifier.notifyMatchStartDelayReport_ end')
        # else:
        #     datas['index'] = nindex
        #     FTTimer(0.1, self.notifyMatchStartDelayReport_, datas)
        pass

    def notifyMatchStartDelayReport(self, userIds, gameId, roomId, sequence, index):
        ulen = len(userIds)
        blockc = 0
        while index < ulen:
            userId = userIds[index]
            PokerMatchReport.reportMatchEvent('MATCH_START', userId, gameId, roomId, 0, sequence, 0)
            index += 1
            blockc += 1
            if blockc > 10:
                return index
        return -1


class MatchRankRewardsIFStage(MatchRankRewardsIF):
    def getRankRewards(self, player):
        """
        获取奖励配置
        """
        rankRewardsList = player.group.stageConf.rankRewardsList if player.group.isGrouping else player.group.matchConf.rankRewardsList
        rank = player.lastRank if player.isQuit else player.rank
        if ftlog.is_debug():
            ftlog.debug('MatchRankRewardsIFStage.getRankRewards',
                        'userId=', player.userId,
                        'rank=', rank,
                        'rankRewardsList=', rankRewardsList,
                        'stageConf.rankRewards=', player.group.stageConf.rankRewardsList)
        if rankRewardsList:
            for rankRewards in rankRewardsList:
                if ((rankRewards.rankRange[0] == -1 or rank >= rankRewards.rankRange[0])
                    and (rankRewards.rankRange[1] == -1 or rank <= rankRewards.rankRange[1])):
                    return rankRewards
        return None

    def sendRankRewards(self, player, rankRewards):
        """
        发放比赛奖励
        """
        try:
            hallRpcOne.hallitem.addAssets(player.group.gameId, player.userId, rankRewards.rewards,
                                  'MATCH_REWARD', player.group.roomId)

            ftlog.info('MatchRankRewardsIFStage.sendRankRewards',
                       'groupId=', player.group.groupId if player.group else None,
                       'score=', player.score,
                       'rank=', player.rank,
                       'rankRewards=', rankRewards.rewards)

            if rankRewards.message:
                # pkmessage.sendPrivate(player.group.gameId, player.userId, 0, rankRewards.message)
                hallRpcOne.halldatanotify.sendDataChangeNotify(player.group.gameId, player.userId, 'message')
        except:
            ftlog.error('MatchRankRewardsIFStage.sendRankRewards',
                        'groupId=', player.group.groupId if player.group else None,
                        'score=', player.score,
                        'rank=', player.rank,
                        'rankRewards=', rankRewards.rewards)
