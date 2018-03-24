# -*- coding:utf-8 -*-
"""
Created on 2017年9月11日

@author: zhaojiangang
"""

from freetime5.util import ftlog
from freetime5.util import fttime
from freetime5.util.ftmsg import MsgPack
from matchcomm.matchs.const import MatchType
from matchcomm.matchs.interface import MatchSigninRecordDaoRedis, \
    MatchSigninFeeIFDefaut, MatchPlayerIFDefault, MatchRankRewardsIF, MatchTableController, MatchPlayerNotifier, \
    MatchRecordDaoRedis
from matchcomm.matchs.models import MatchTableManager
from matchcomm.matchs.report import PokerMatchReport
from matchcomm.matchs.stage_match.conf import StageMatchConf, StageMatchRulesConfASS
from matchcomm.matchs.stage_match.match import MatchMaster, MatchArea, \
    MatchMasterStubLocal, MatchAreaStubLocal
from matchcomm.matchs.stage_match.match_status import StageMatchStatusDaoRedis
from matchcomm.matchs.utils import unlockUserForMatch
from matchcomm.servers.room.rpc.stage_match_room_remote import MatchAreaStubRemote, \
    MatchMasterStubRemote
from tuyoo5.core import tyglobal
from tuyoo5.core import tyrpcconn
from tuyoo5.core.tyconfig import TYBizException
from tuyoo5.core.tygame import TYRoom


def _buildMatchDesc(matchConfig):
    """
    构建比赛简介.

    """
    matchDesc = {}
    matchDesc["type"] = MatchType.STAGE_MATCH  # 比赛类型
    matchDesc["name"] = matchConfig.name  # 比赛名称
    matchDesc["desc"] = matchConfig.desc  # 比赛名称
    # 比赛类型 matchConf.start.type
    # 人满  USER_COUNT = 1
    # 定时  TIMING = 2
    matchDesc["startType"] = matchConfig.startConf.type
    if matchDesc["startType"] == 1:
        matchDesc["condition"] = matchConfig.startConf.userCount  # 最少开赛人数
    else:
        matchDesc["condition"] = fttime.timeStampToStr(matchConfig.startConf.calcNextStartTime())  # 最近的开赛时间
    matchDesc["ranks"] = [{"start": rank.rankRange[0], "end": rank.rankRange[1], "desc": rank.desc} for rank in
                          matchConfig.rankRewardsList]
    matchDesc["fees"] = [fee.desc for fee in matchConfig.fees]
    # hall5用于推荐充值
    matchDesc["feesDetail"] = [fee.fee.toDict() for fee in matchConfig.fees]
    matchDesc["stages"] = [
        {"name": stage.name, "riseUserCount": stage.riseUserCount, "totalUserCount": stage.userCountPerGroup,
         "cardCount": stage.cardCount, "baseScore": stage.baseScore, "type": stage.rulesConf.TYPE_ID,
         "riseUserRefer": stage.rulesConf.riseUserRefer if stage.rulesConf.TYPE_ID == StageMatchRulesConfASS.TYPE_ID
         else 0} for stage in matchConfig.stages]
    matchDesc["tips"] = matchConfig.tipsConf
    return matchDesc


class StageMatchRoomMixin():
    matchArea = None
    matchMaster = None
    masterRoomId = None
    isMaster = False
    bigmatchId = None
    conf = None
    interfaceFactory = None

    tableController = None
    playerNotifier = None
    matchSigninFeeIF = None
    matchRankRewardsIF = None
    matchPlayerIF = None
    signinRecordDao = None

    def getMasterRoomId(self):
        if self.conf.startConf.isUserCountType():
            return self.roomId
        ctrlRoomIdList = sorted(tyglobal.bigRoomIdsMap().get(self.bigRoomId, []))
        return ctrlRoomIdList[0]

    def initStageMatch(self):
        ftlog.info('StageMatchRoomMixin.initStageMatch ...',
                   'bigRoomId=', self.bigRoomId,
                   'matchId=', self.matchId,
                   'roomId=', self.roomId)
        conf = StageMatchConf(self.gameId, self.matchId)
        conf.decodeFromDict(self.matchConf)
        conf.tableId = self.roomId * 10000  # 用来表示玩家在房间队列的特殊tableId
        conf.seatId = 1

        self.conf = conf
        self.bigmatchId = self.bigRoomId
        self.masterRoomId = self.getMasterRoomId()

        self.isMaster = self.roomId == self.masterRoomId

        tableManager = MatchTableManager(self.gameId, conf.tableSeatCount)
        shadowRoomIds = self.shadowRoomIds

        ftlog.info('StageMatchRoomMixin.initStageMatch',
                   'roomId=', self.roomId,
                   'shadowRoomIds=', list(shadowRoomIds))

        for tableRoomId in shadowRoomIds:
            count = self.tableCount
            baseId = tableRoomId * 10000
            ftlog.info('StageMatchRoomMixin.initStageMatch addTables',
                       'roomId=', self.roomId,
                       'tableRoomId=', tableRoomId,
                       'tableCount=', count,
                       'baseId=', baseId)

            tableManager.addTables(tableRoomId, baseId, count)
        tableManager.shuffleIdleTable()
        area, master = self.buildStageMatch()

        if tyglobal.mode() == tyglobal.RUN_MODE_ONLINE:
            # TODO 线上模式检测，上线前需谨慎检查
            playerCapacity = int(tableManager.allTableCount * tableManager.tableSeatCount * 0.9)
            if playerCapacity <= conf.startConf.userMaxCountPerMatch:
                ftlog.error('StageMatchRoomMixin.initStageMatch',
                            'allTableCount=', tableManager.allTableCount,
                            'tableSeatCount=', tableManager.tableSeatCount,
                            'playerCapacity=', playerCapacity,
                            'userMaxCount=', conf.startConf.userMaxCount,
                            'confUserMaxCountPerMatch=', conf.startConf.userMaxCountPerMatch,
                            'err=', 'NotEnoughTable')
            assert (playerCapacity > conf.startConf.userMaxCountPerMatch)

        area.tableManager = tableManager
        self.matchArea = area
        self.matchMaster = master
        if master:
            master.start()
        area.start()

    def buildStageMatch(self):
        ctrlRoomIdList = tyglobal.bigRoomIdsMap().get(self.bigRoomId, [])
        if self.conf.startConf.isUserCountType():
            self.conf.startConf.userMaxCountPerMatch = self.conf.startConf.userMaxCount
            self.conf.startConf.signinMaxCount = self.conf.startConf.signinMaxCount
        else:
            self.conf.startConf.userMaxCountPerMatch = int(
                self.conf.startConf.userMaxCount / max(len(ctrlRoomIdList), 1))
            self.conf.startConf.signinMaxCountPerMatch = int(
                self.conf.startConf.signinMaxCount / max(len(ctrlRoomIdList), 1))

        master = None
        if self.isMaster:
            master, area = self.buildMasterAndArea()
        else:
            area = self.buildAreaOnly()

        ftlog.info('StageMatchRoomMixin.buildMatch roomId=', self.roomId,
                   'ctrlRoomIdList=', ctrlRoomIdList,
                   'ctrlRoomCount=', len(ctrlRoomIdList),
                   'userMaxCount=', self.conf.startConf.userMaxCount,
                   'signinMaxCount=', self.conf.startConf.signinMaxCount)
        if master:
            master.matchStatusDao = StageMatchStatusDaoRedis()

        # 默认空实现，会被PokerMatchTableController覆盖
        area.tableController = self.tableController or MatchTableController()
        # 默认空实现，会被PokerMatchPlayerNotifier覆盖
        area.playerNotifier = self.playerNotifier or MatchPlayerNotifier()
        # 默认空实现，会被MatchRankRewardsIFStage覆盖
        area.matchRankRewardsIF = self.matchRankRewardsIF or MatchRankRewardsIF()
        area.matchPlayerIF = self.matchPlayerIF or MatchPlayerIFDefault()
        area.matchSigninFeeIF = self.matchSigninFeeIF or MatchSigninFeeIFDefaut()
        area.signinRecordDao = self.signinRecordDao or MatchSigninRecordDaoRedis()

        return area, master

    def buildMasterAndArea(self):
        ftlog.info('StageMatchRoomMixin.buildMaster'
                   'roomId=', self.roomId,
                   'masterRoomId=', self.masterRoomId,
                   'isMaster=', self.isMaster,
                   'bigmatchId=', self.bigmatchId)
        master = MatchMaster(self, self.bigmatchId, self.conf)
        area = MatchArea(self, self.bigmatchId, self.conf, MatchMasterStubLocal(master))
        master.addAreaStub(MatchAreaStubLocal(master, area))
        if not self.conf.startConf.isUserCountType():
            ctrlRoomIdList = tyglobal.bigRoomIdsMap().get(self.bigRoomId, [])
            for ctrlRoomId in ctrlRoomIdList:
                if ctrlRoomId != area.roomId:
                    master.addAreaStub(MatchAreaStubRemote(master, ctrlRoomId))
        return master, area

    def buildAreaOnly(self):
        ftlog.info('StageMatchRoomMixin.buildArea roomId=', self.roomId,
                   'masterCtrlRoomId=', self.masterRoomId)
        return MatchArea(self, self.bigmatchId, self.conf, MatchMasterStubRemote(self.masterRoomId))

    def _do_match__signin(self, msg):
        """
        比赛报名协议监听器.

        调用赛区进行报名，成功返回roomId,userId；失败返回ec信息

        :param msg: tcp消息
        """
        userId = msg.getParam('userId')
        feeIndex = msg.getParam('fee', 0)
        signinParams = msg.getParam('signinParams', {})
        ftlog.info('StageMatchRoomMixin._do_match__signin roomId=', self.roomId,
                   'userId=', userId)

        # if not signinParams and tyglobal.enableTestHtml():
        #     signinParams = gamedata.getGameAttrJson(userId, self.gameId, 'test.signinParams')

        resp = MsgPack()
        resp.setCmd('match')
        resp.setResult('action', 'signin')
        resp.setResult('roomId', self.bigRoomId)
        resp.setResult('userId', userId)
        resp.setResult('gameId', self.gameId)
        try:
            self.matchArea.signin(userId, feeIndex, signinParams)
            resp.setResult('ok', 1)
            PokerMatchReport.reportMatchEvent('MATCH_SIGN_UP', userId, self.gameId, self.matchId, 0, 0, 0)
        except TYBizException, e:
            ftlog.info('StageMatchRoomMixin._do_match__signin Exception=', e)
            resp.setResult('ok', 0)
            resp.setError(e.errorCode, e.message)

        if not resp.getErrorCode():
            self.matchArea.playerNotifier.notifyMatchSignsUpdate(userId)

        tyrpcconn.sendToUser(resp, userId)

    def doWinlose(self, msg):
        """
        旧的消息方式
        # TODO 需要切换成rpc方式
        """
        ftlog.info('StageMatchRoomMixin.doWinlose roomId=', self.roomId,
                   'msg=', msg)
        tableId = msg.getParam('tableId')
        ccrc = msg.getParam('ccrc')
        # seatWinloses = msg.getParam('seatWinloses')
        groupId = msg.getParam('groupId')
        users = msg.getParam('users')
        seatWinloses = { user.get("userId") :user.get("deltaScore")  for user in users}
        self.matchArea.tableWinlose(groupId, tableId, ccrc, seatWinloses)

    def _do_match__signout(self, msg):
        """
        比赛退赛协议监听器.
        """
        userId = msg.getParam('userId')
        ftlog.info('StageMatchRoomMixin._do_match__signout roomId=', self.roomId,
                   'userId=', userId)
        resp = MsgPack()
        resp.setCmd('match')
        resp.setResult('action', 'signout')
        resp.setResult('roomId', self.bigRoomId)
        resp.setResult('userId', userId)
        resp.setResult('gameId', self.gameId)
        try:
            self.matchArea.signout(userId)
            resp.setResult('ok', 1)
            PokerMatchReport.reportMatchEvent('MATCH_SIGN_OUT', userId, self.gameId, self.matchId, 0, 0, 0)
        except TYBizException, e:
            resp.setResult('ok', 0)
            resp.setError(e.errorCode, e.message)

        if not resp.getErrorCode():
            self.matchArea.playerNotifier.notifyMatchSignsUpdate(userId)

        tyrpcconn.sendToUser(resp, userId)

    def _do_match__winlose(self, msg):
        # TODO GT2GR待切换成RPC方式
        tableId = msg.getParam('tableId')
        ccrc = msg.getParam('ccrc')
        seatWinloses = msg.getParam('seatWinloses')
        groupId = msg.getParam('groupId')
        self.matchArea.tableWinlose(groupId, tableId, ccrc, seatWinloses)

    def _do_match__desc(self, msg):
        """
        比赛详情协议监听器.
        """
        userId = msg.getParam('userId')
        ftlog.info('StageMatchRoomMixin._do_match__desc roomId=', self.roomId,
                   'userId=', userId)
        self._sendDesc(userId)

    def doMatchDesc(self, userId):
        """
        比赛详情协议监听器.
        """
        ftlog.info('StageMatchRoomMixin._do_match__desc roomId=', self.roomId,
                   'userId=', userId)
        self._sendDesc(userId)

    def _do_match__enter(self, msg):
        """
        比赛进入协议监听器.
        进入比赛、进入阶段
        """
        userId = msg.getParam('userId')
        ftlog.info('StageMatchRoomMixin._do_match__enter roomId=', self.roomId,
                   'userId=', userId)
        resp = MsgPack()
        resp.setCmd('match')
        resp.setResult('action', 'enter')
        resp.setResult('roomId', self.bigRoomId)
        resp.setResult('gameId', self.gameId)
        resp.setResult('userId', userId)
        try:
            self.matchArea.enter(userId)
            resp.setResult('ok', 1)
        except TYBizException, e:
            resp.setResult('ok', 0)
            resp.setError(e.errorCode, e.message)

        tyrpcconn.sendToUser(resp, userId)

    def _do_match__leave(self, msg):
        """
        比赛离开协议监听器.
        离开比赛
        """
        userId = msg.getParam('userId')
        ftlog.info('StageMatchRoomMixin._do_match__leave roomId=', self.roomId,
                   'userId=', userId)
        resp = MsgPack()
        resp.setCmd('match')
        resp.setResult('action', 'leave')
        resp.setResult('roomId', self.bigRoomId)
        resp.setResult('gameId', self.gameId)
        resp.setResult('userId', userId)
        try:
            self.matchArea.leave(userId)
            resp.setResult('ok', 1)
        except TYBizException, e:
            resp.setResult('ok', 0)
            resp.setError(e.errorCode, e.message)

        tyrpcconn.sendToUser(resp, userId)

    def _do_match__update(self, msg):
        """
        比赛信息更新监听听器.
        """
        userId = msg.getParam('userId')
        ftlog.info('StageMatchRoomMixin._do_match__update roomId=', self.roomId,
                   'userId=', userId)
        self._sendMatchStatas(userId)

    def _do_match__rank(self, msg):
        """
        比赛信息更新监听听器.
        """
        userId = msg.getParam('userId')
        ftlog.info('StageMatchRoomMixin._do_match__rank roomId=', self.roomId,
                   'userId=', userId)
        self._sendMatchRanks(userId)

    def _do_match__giveup(self, msg):
        userId = msg.getParam('userId')
        ftlog.info('StageMatchRoomMixin._do_match__giveup roomId=', self.roomId,
                   'userId=', userId)
        player = self.matchArea.findPlayer(userId)
        if player and not player.isQuit:
            player.isQuit = True
            unlockUserForMatch(userId, self.roomId, self.conf.tableId)
            resp = MsgPack()
            resp.setCmd('match')
            resp.setResult('action', 'giveup')
            resp.setResult('roomId', self.bigRoomId)
            resp.setResult('gameId', self.gameId)
            resp.setResult('userId', userId)
            resp.setResult('ok', 1)
            if player.table:  # 玩家还在牌桌上
                try:
                    self.matchArea.tableController.playerGiveUp(player.table.roomId, player.table.tableId, userId)
                except TYBizException, e:
                    resp.setResult('ok', 0)
                    resp.setError(e.errorCode, e.message)
            tyrpcconn.sendToUser(resp, userId)
            return 1
        return 0

    def doMatchQuickStart(self, msg):
        ftlog.info('StageMatchRoomMixin._do_room__quick_start')
        assert (self.roomId == msg.getParam('roomId'))
        userId = msg.getParam('userId')
        tableId = msg.getParam('tableId')
        roomId = msg.getParam('roomId')
        gameId = msg.getParam('gameId')

        ftlog.info('StageMatchRoomMixin._do_room__quick_start',
                   'userId=', userId,
                   'tableId=', tableId,
                   'roomId=', roomId,
                   'gameId=', gameId,
                   'confTableId=', self.conf.tableId)
        player = self.matchArea.findPlayer(userId)
        if player is None:
            ftlog.warn('StageMatchRoomMixin._do_room__quick_start',
                       'userId=', userId,
                       'tableId=', tableId,
                       'roomId=', roomId,
                       'gameId=', gameId,
                       'err=', 'NotFoundPlayer')
            try:
                # 可能是之前在gt中的tableId
                unlockUserForMatch(userId, self.roomId, tableId)
            except:
                ftlog.error('StageMatchRoomMixin._do_room__quick_start',
                            'userId=', userId,
                            'tableId=', tableId,
                            'roomId=', roomId,
                            'gameId=', gameId)
            reason = TYRoom.ENTER_ROOM_REASON_INNER_ERROR
            info = u'在线状态错误或其他系统内部错误'
            self._sendQuickStartRes(self.gameId, userId, reason, self.bigRoomId, 0, info)
            return
        
        # 确认是在房间掉线
        if tableId == self.conf.tableId:
            # 玩家在队列里时断线重连
            reason = TYRoom.ENTER_ROOM_REASON_OK
            self._sendQuickStartRes(self.gameId, userId, reason, self.bigRoomId, self.conf.tableId)
            # 如果用户已经被分组则发送等待信息
            if player.group:
                self._sendMatchStatas(player.userId)
                self._sendMatchRanks(player.userId)
                self._sendDesc(player.userId)
                self.matchArea.playerNotifier.notifyMatchWait(player, 1)
        else:
            # 玩家在牌桌上断线重连，游戏的UT补齐下面的参数
            extParams = msg.getKey('params') # 开放给用户的扩展参数
            clientId = msg.getParam("clientId") # clientId
            shadowRoomId = msg.getParam("shadowRoomId") # GT的房间ID
            self._sendMatchStatas(player.userId)
            self._sendMatchRanks(player.userId)
            self._sendDesc(player.userId)
            # TYRoomMixin.querySitReq(userId, shadowRoomId, tableId, clientId, extParams)

    def _sendMatchRanks(self, userId):
        player = self.matchArea.findPlayer(userId)
        if player:
            self.matchArea.playerNotifier.notifyMatchRank(player)

    def _sendMatchStatas(self, userId):
        self.matchArea.playerNotifier.notifyMatchUpdate(userId)

    def _sendDesc(self, userId):
        resp = MsgPack()
        resp.setCmd('match')
        resp.setResult('action', 'desc')
        resp.setResult('roomId', self.bigRoomId)
        resp.setResult('gameId', self.gameId)
        resp.setResult('userId', userId)
        signinCount = self.matchArea.getTotalSignerCount()  # 房间实时报名人数
        resp.setResult('signinCount', signinCount)
        matchDef = _buildMatchDesc(self.conf)
        resp.updateResult(matchDef)  # 比赛配置
        record = MatchRecordDaoRedis.loadRecord(self.gameId, userId, self.bigRoomId)
        if record:
            ret = MatchRecordDaoRedis.loadHistory(self.gameId, userId, self.bigRoomId)
            # ret = [ {"time":_["time"],"desc":"第%s名,获得%s" % (_["rank"],_["desc"]),"rank":_["rank"],"info":_["desc"] }
            #         for _ in ret]
            ret = map(lambda _:{"time":_["time"],"desc":"第%s名" % (_["rank"],),"rank":_["rank"],
                                "info":_["desc"] } if _["desc"] == "" else {"time":_["time"],"desc":"第%s名,获得%s" % (_["rank"],_["desc"]),"rank":_["rank"],
                                "info":_["desc"] } , ret)
            histories = {
                "crownCount": record.crownCount,
                "playCount": record.playCount,
                "bestRank": record.bestRank,
                "bestRankDate": record.bestRankDate,
                "records": ret
            }
        else:
            histories = {
                "crownCount": 0,
                "playCount": 0,
                "bestRank": 0,
                "bestRankDate": 0,
                "records": []
            }
        resp.setResult('histories', histories)
        tyrpcconn.sendToUser(resp, userId)

    def _sendQuickStartRes(self, gameId, userId, reason, roomId=0, tableId=0, info=""):
        mp = MsgPack()
        mp.setCmd('quick_start')
        mp.setResult('info', info)
        mp.setResult('userId', userId)
        mp.setResult('gameId', gameId)
        mp.setResult('roomId', roomId)
        mp.setResult('tableId', tableId)
        mp.setResult('reason', reason)
        tyrpcconn.sendToUser(mp, userId)
