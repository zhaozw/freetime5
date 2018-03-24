# -*- coding:utf-8 -*-
"""
Created on 2016年1月15日

@author: zhaojiangang
"""
import time

from freetime5.twisted import ftcore
from freetime5.util import ftlog
from freetime5.util.ftexception import FTMsgPackException



from matchcomm.matchs.const import MatchFinishReason
from matchcomm.matchs.models import MatchPlayerData
from matchcomm.matchs.stage_match.match import MatchRiser, MatchSigner, \
    MatchAreaStatus, MatchMasterStatus, MatchMasterStub, MatchInstStub, \
    MatchGroupStub, MatchAreaStub


from tuyoo5.core import tyglobal, tyconfig


def getMaster(roomId):
    room = tyglobal.rooms()[roomId]
    if room and hasattr(room, 'matchMaster'):
        return room.matchMaster
    return None


def getMatchArea(roomId):
    room = tyglobal.rooms()[roomId]
    if room and hasattr(room, 'match'):
        return room.match
    return None


def findAreaStub(roomId, areaRoomId):
    matchMaster = getMaster(roomId)
    if matchMaster:
        return matchMaster, matchMaster.findAreaStub(areaRoomId)
    return matchMaster, None


def findInstStub(roomId, areaRoomId, instId):
    matchMaster, areaStub = findAreaStub(roomId, areaRoomId)
    if areaStub and areaStub.curInstStub and areaStub.curInstStub.instId == instId:
        return matchMaster, areaStub.curInstStub
    return matchMaster, None


def findGroupStub(roomId, groupId):
    matchMaster = getMaster(roomId)
    if matchMaster:
        return matchMaster, matchMaster.findGroupStub(groupId)
    return matchMaster, None


def findGroup(roomId, groupId):
    area = getMatchArea(roomId)
    if area:
        return area, area.findGroup(groupId)
    return area, None


def decodeRiserFromDict(d):
    return MatchRiser(d[0], d[1], d[2], d[3])


def decodeRiserList(riserDictList):
    ret = []
    for d in riserDictList:
        ret.append(decodeRiserFromDict(d))
    return ret


def encodePlayerForRiserDict(player):
    return [player.userId, player.score, player.rank, player.tableRank]


def clientIdToNumber(clientId):
    cid = 0
    try:
        cid = tyconfig.clientIdToNumber(clientId)
    except:
        pass
    if cid == 0:
        ftlog.warn('stage_match_remote.clientIdToNumber failed:', clientId)
    return cid


def numberToClientId(numberId):
    cid = ''
    try:
        cid = tyconfig.numberToClientId(numberId)
    except:
        pass
    if not cid:
        ftlog.warn('stage_match_remote.numberToClientId failed:', numberId)
    return cid


def cutUserName(userName):
    try:
        if isinstance(userName, str):
            userName = unicode(userName)
        if isinstance(userName, unicode):
            return userName[0:20]
    except:
        pass
    return ''


def encodePlayerListForRiser(playerList, start, end):
    ret = []
    for i in xrange(start, end):
        ret.append(encodePlayerForRiserDict(playerList[i]))
    return ret


def encodeSignerToDict(signer):
    return [signer.userId, signer.signinTime, clientIdToNumber(signer.clientId), cutUserName(signer.userName)]


def encodeSignerList(signerList, start, end):
    ret = []
    for i in xrange(start, end):
        ret.append(encodeSignerToDict(signerList[i]))
    return ret


def decodeSignerFromDict(instId, d):
    signer = MatchSigner(d[0], instId)
    signer.signinTime = d[1]
    signer.clientId = numberToClientId(d[2])
    signer.userName = d[3]
    return signer


def decodeSignerList(instId, signerList):
    ret = []
    for d in signerList:
        ret.append(decodeSignerFromDict(instId, d))
    return ret


def encodePlayerForAddGroup(player):
    return [player.userId, cutUserName(player.userName), player.score,
            player.signinTime, player.rank, player.tableRank, clientIdToNumber(player.clientId)]


def decodePlayerFromDict(d):
    p = MatchPlayerData(d[0])
    p.userName = d[1]
    p.score = d[2]
    p.signinTime = d[3]
    p.rank = d[4]
    p.tableRank = d[5]
    p.clientId = numberToClientId(d[6])
    return p


def encodePlayerListForAddGroup(playerList, start, end):
    ret = []
    for i in xrange(start, end):
        ret.append(encodePlayerForAddGroup(playerList[i]))
    return ret


def decodePlayerList(playerDictList):
    ret = []
    for d in playerDictList:
        ret.append(decodePlayerFromDict(d))
    return ret


def areaHeartbeat(serverId, roomId, areaRoomId, areaStatusDict):
    _matchMaster, areaStub = findAreaStub(roomId, areaRoomId)
    if areaStub:
        areaStub.onAreaHeartbeat(MatchAreaStatus.fromDict(areaStatusDict))


def areaGroupRise(serverId, roomId, areaRoomId, groupId, riserDictList):
    _master, groupStub = findGroupStub(roomId, groupId)
    if groupStub:
        risers = decodeRiserList(riserDictList)
        for riser in risers:
            groupStub.onGroupRisePlayer(riser)


def areaGroupFinish(serverId, roomId, areaRoomId, groupId, finishReason):
    _master, groupStub = findGroupStub(roomId, groupId)
    if groupStub:
        groupStub.onGroupFinish(finishReason)


def areaReportSigners(serverId, roomId, areaRoomId, instId, signerList):
    _match, instStub = findInstStub(roomId, areaRoomId, instId)
    if instStub:
        signerList = decodeSignerList(instId, signerList)
        instStub.onSignin(signerList)


def areaStartOK(serverId, roomId, areaRoomId, instId):
    _match, instStub = findInstStub(roomId, areaRoomId, instId)
    if instStub:
        instStub.onStart()


def instStartSignin(serverId, roomId, masterRoomId, instId):
    area = getMatchArea(roomId)
    if not area:
        ftlog.error('stage_match_remote.instStartSignin serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'err=', 'NotFoundMatch')
        return
    if not area.curInst or area.curInst.instId != instId:
        ftlog.error('stage_match_remote.instStartSignin serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'curInstId=', area.curInst.instId if area.curInst else None,
                    'err=', 'DiffInstId')
        return
    area.curInst.startSignin()


def instPrepare(serverId, roomId, masterRoomId, instId):
    area = getMatchArea(roomId)
    if not area:
        ftlog.error('stage_match_remote.instPrepare serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'err=', 'NotFoundMatch')
        return
    if not area.curInst or area.curInst.instId != instId:
        ftlog.error('stage_match_remote.instPrepare serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'curInstId=', area.curInst.instId if area.curInst else None,
                    'err=', 'DiffInstId')
        return
    area.curInst.prepare()


def instCancel(serverId, roomId, masterRoomId, instId, reason):
    area = getMatchArea(roomId)
    if not area:
        ftlog.error('stage_match_remote.instCancel serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'reason=', reason,
                    'err=', 'NotFoundMatch')
        return
    if not area.curInst or area.curInst.instId != instId:
        ftlog.error('stage_match_remote.instPrepare serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'reason=', reason,
                    'curInstId=', area.curInst.instId if area.curInst else None,
                    'err=', 'DiffInstId')
        return
    area.curInst.cancel(reason)


def instStart(serverId, roomId, masterRoomId, instId):
    area = getMatchArea(roomId)
    if not area:
        ftlog.error('stage_match_remote.instStart serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'err=', 'NotFoundMatch')
        return
    if not area.curInst or area.curInst.instId != instId:
        ftlog.error('stage_match_remote.instStart serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'curInstId=', area.curInst.instId if area.curInst else None,
                    'err=', 'DiffInstId')
        return
    area.curInst.start()


def masterHeartbeat(serverId, roomId, masterRoomId, statusDict):
    area = getMatchArea(roomId)
    if not area:
        ftlog.error('stage_match_remote.masterHeartbeat serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'statusDict=', statusDict,
                    'err=', 'NotFoundMatch')
        return
    area.masterStub.onMasterHeartbeat(MatchMasterStatus.fromDict(statusDict))


def createInst(serverId, roomId, masterRoomId, instId, startTime, needLoad):
    area = getMatchArea(roomId)
    if not area:
        ftlog.error('stage_match_remote.createInst serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'err=', 'NotFoundMatch')
        return
    area.createInst(instId, startTime, needLoad)


def cancelInst(serverId, roomId, masterRoomId, instId, reason):
    area = getMatchArea(roomId)
    if not area:
        ftlog.error('stage_match_remote.cancelInst serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'reason=', reason,
                    'err=', 'NotMatchArea')
        return
    area.cancelInst(instId, reason)


def createGroup(serverId, roomId, masterRoomId, instId,
                matchingId, groupId, groupName, stageIndex, isGrouping, totalPlayerCount, startStageIndex):
    area = getMatchArea(roomId)
    if not area:
        ftlog.error('stage_match_remote.createGroup serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'instId=', instId,
                    'matchingId=', matchingId,
                    'groupId=', groupId,
                    'stageIndex=', stageIndex,
                    'isGrouping=', isGrouping,
                    'totalPlayerCount=', totalPlayerCount,
                    'err=', 'NotMatchArea')
        return

    area.createGroup(instId, matchingId, groupId, groupName, stageIndex, isGrouping, totalPlayerCount, startStageIndex)


def addPlayerToGroup(serverId, roomId, masterRoomId, groupId, playerList):
    startTime = time.time()
    _area, group = findGroup(roomId, groupId)
    if not group:
        ftlog.error('stage_match_remote.addPlayerToGroup serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'groupId=', groupId,
                    'playerCount=', len(playerList),
                    'err=', 'NotFoundGroup')
        return
    playerList = decodePlayerList(playerList)
    for player in playerList:
        group.addPlayer(player)
    if ftlog.is_debug():
        ftlog.info('stage_match_remote.addPlayerToGroup serverId=', serverId,
                   'roomId=', roomId,
                   'masterRoomId=', masterRoomId,
                   'groupId=', groupId,
                   'userIds=', [p.userId for p in playerList])
    ftlog.info('group_match_remote.addPlayerToGroup OK serverId=', serverId,
               'roomId=', roomId,
               'masterRoomId=', masterRoomId,
               'groupId=', groupId,
               'playerCount=', len(playerList),
               'usedTime=', time.time() - startTime)


def startGroup(serverId, roomId, masterRoomId, groupId):
    _area, group = findGroup(roomId, groupId)
    if not group:
        ftlog.error('stage_match_remote.startGroup serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'groupId=', groupId,
                    'err=', 'NotFoundGroup')
        return
    group.start()


def killGroup(serverId, roomId, masterRoomId, groupId, reason):
    _area, group = findGroup(roomId, groupId)
    if not group:
        ftlog.error('stage_match_remote.killGroup serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'groupId=', groupId,
                    'reason=', reason,
                    'err=', 'NotFoundGroup')
        return
    group.kill(reason)
    ftlog.info('stage_match_remote.killGroup serverId=', serverId,
               'roomId=', roomId,
               'masterRoomId=', masterRoomId,
               'groupId=', groupId,
               'reason=', reason)


def finalGroup(serverId, roomId, masterRoomId, groupId):
    _area, group = findGroup(roomId, groupId)
    if not group:
        ftlog.error('stage_match_remote.finalGroup serverId=', serverId,
                    'roomId=', roomId,
                    'masterRoomId=', masterRoomId,
                    'groupId=', groupId,
                    'err=', 'NotFoundGroup')
        return
    group.final()
    ftlog.info('stage_match_remote.finalGroup serverId=', serverId,
               'roomId=', roomId,
               'masterRoomId=', masterRoomId,
               'groupId=', groupId)

def doWinlose(roomId, tableId, info):
    ftlog.info('stage_match_remote.doWinlose roomId=', roomId,
               'msg=', info)
    _area = getMatchArea(roomId)
    if not _area:
        ftlog.error('stage_match_remote.doWinlose ',
                    'roomId=', roomId,
                    'err=', 'NotFoundArea')
        return

    groupId = info.get('groupId')
    ccrc = info.get('ccrc')
    seatWinloses = info.get('seatWinloses')
    # TODO find groupId by tableId
    _area.tableWinlose(groupId, tableId, ccrc, seatWinloses)


class MatchMasterStubRemote(MatchMasterStub):
    """
    赛事在赛区控制对象，运行于赛区中
    """
    RISER_COUNT_PER_TIME = 1000
    REPORT_SIGNER_COUNT_PER_TIME = 300

    def __init__(self, roomId):
        super(MatchMasterStubRemote, self).__init__(roomId)
        # self.serverId = rpccore.getRpcDstRoomServerId(self.roomId, 0)
        self._logger.add('serverId', self.serverId)

    def areaHeartbeat(self, area):
        """
        area心跳，运行
        """
        if self._logger.isDebug():
            self._logger.debug('MatchMasterStubRemote.areaHeartbeat',
                               'area=', area.roomId)

        status = area.buildStatus()
        areaHeartbeat(self.serverId, self.roomId, area.roomId, status.toDict())

    def _risePlayers(self, area, group, encodedRiserList, start):
        count = MatchMasterStubRemote.RISER_COUNT_PER_TIME
        while count > 0:
            try:
                rlist = encodedRiserList[start:start + count]
                areaGroupRise(self.serverId, self.roomId, area.roomId, group.groupId, rlist)
                return len(rlist)
            except FTMsgPackException:
                # 每次减少1/3
                newCount = max(1, count - count / 3)
                self._logger.warn('MatchMasterStubRemote._risePlayers msgTooLong',
                                  'area=', area.roomId,
                                  'groupId=', group.groupId,
                                  'count=', count,
                                  'newCount=', newCount)
                if newCount <= 1:
                    self._logger.error('MatchMasterStubRemote._risePlayers msgTooLong1',
                                       'area=', area.roomId,
                                       'groupId=', group.groupId,
                                       'count=', count,
                                       'newCount=', newCount)
                    return 1
                count = newCount
            except:
                self._logger.warn('MatchMasterStubRemote._risePlayers exception',
                                  'area=', area.roomId,
                                  'groupId=', group.groupId,
                                  'count=', count)
                return count

    def areaGroupFinish(self, area, group):
        """
        向主赛区汇报
        """
        if self._logger.isDebug():
            self._logger.debug('MatchMasterStubRemote.areaGroupFinish',
                               'finishReason=', group.finishReason,
                               'rankList=', [p.userId for p in group.rankList])

        self._logger.info('MatchMasterStubRemote.areaGroupFinish',
                          'finishReason=', group.finishReason,
                          'riseCount=', len(group.rankList))

        startTime = time.time()
        if group.finishReason == MatchFinishReason.FINISH:
            index = 0
            encodedRiserList = encodePlayerListForRiser(group.rankList, 0, len(group.rankList))
            while index < len(encodedRiserList):
                startTime = time.time()
                count = self._risePlayers(area, group, encodedRiserList, index)
                self._logger.info('MatchMasterStubRemote.areaGroupFinish reportRiser',
                                  'finishReason=', group.finishReason,
                                  'riseCount=', len(group.rankList),
                                  'index=', index,
                                  'count=', count,
                                  'usedTime=', time.time() - startTime)
                index += max(1, count)

        areaGroupFinish(self.serverId, self.roomId,
                        area.roomId, group.groupId, group.finishReason)

        self._logger.info('MatchMasterStubRemote.areaGroupFinish',
                          'finishReason=', group.finishReason,
                          'riseCount=', len(group.rankList),
                          'usedTime=', time.time() - startTime)

    def _reportSigners(self, area, inst, encodedSignerList, start):
        count = MatchMasterStubRemote.REPORT_SIGNER_COUNT_PER_TIME
        while count > 0:
            try:
                rlist = encodedSignerList[start:start + count]
                areaReportSigners(self.serverId, self.roomId, area.roomId, inst.instId, rlist)
                return len(rlist)
            except FTMsgPackException:
                # 每次减少1/3
                newCount = max(1, count - count / 3)
                self._logger.warn('MatchMasterStubRemote.reportSigners msgTooLong',
                                  'instId=', inst.instId,
                                  'area=', area.roomId,
                                  'count=', count,
                                  'newCount=', newCount)
                if newCount <= 1:
                    self._logger.error('MatchMasterStubRemote.reportSigners msgTooLong1',
                                       'instId=', inst.instId,
                                       'area=', area.roomId,
                                       'count=', count,
                                       'newCount=', newCount)
                    return 1
                count = newCount
            except:
                self._logger.error('MatchMasterStubRemote.reportSigners exception',
                                   'instId=', inst.instId,
                                   'area=', area.roomId,
                                   'count=', count)
                return count

    def areaInstStarted(self, area, inst):
        """
        向主赛区汇报比赛实例启动成功，汇报报名用户列表
        """
        signerList = inst.signerMap.values()
        if self._logger.isDebug():
            self._logger.debug('MatchMasterStubRemote.areaInstStarted',
                               'instId=', inst.instId,
                               'signerUserIds=', [s.userId for s in signerList])
        self._logger.info('MatchMasterStubRemote.slaverInstStarted',
                          'instId=', inst.instId,
                          'signerCount=', len(signerList))
        startTime = time.time()
        index = 0
        encodedSignerList = encodeSignerList(signerList, 0, len(signerList))
        while index < len(encodedSignerList):
            startTime = time.time()
            count = self._reportSigners(area, inst, encodedSignerList, index)
            self._logger.info('MatchMasterStubRemote.slaverInstStarted reportSigner',
                              'instId=', inst.instId,
                              'signerCount=', len(encodedSignerList),
                              'index=', index,
                              'count=', count,
                              'usedTime=', time.time() - startTime)
            index += max(1, count)
        areaStartOK(self.serverId, self.roomId, area.roomId, inst.instId)
        self._logger.info('MatchMasterStubRemote.slaverInstStarted OK',
                          'instId=', inst.instId,
                          'signerCount=', len(encodedSignerList),
                          'usedTime=', time.time() - startTime)


class MatchInstStubRemote(MatchInstStub):
    def __init__(self, areaStub, instId, startTime, needLoad):
        super(MatchInstStubRemote, self).__init__(areaStub, instId, startTime, needLoad)

    @property
    def serverId(self):
        return self.areaStub.serverId

    def _doStartSignin(self):
        instStartSignin(self.serverId, self.roomId,
                        self.master.roomId, self.instId)

    def _doPrepare(self):
        instPrepare(self.serverId, self.roomId,
                    self.master.roomId, self.instId)

    def _doCancel(self):
        instCancel(self.serverId, self.roomId,
                   self.master.roomId, self.instId, self.finishReason)

    def _doStart(self):
        instStart(self.serverId, self.roomId,
                  self.master.roomId, self.instId)


class MatchGroupStubRemote(MatchGroupStub):
    """
    比赛分组存根对象，运行于主控进程
    """
    ADD_PLAYER_COUNT_PER_TIME = 300

    def __init__(self, areaStub, stage, groupId,
                 groupName, playerList, isGrouping, totalPlayerCount, startStageIndex):
        super(MatchGroupStubRemote, self).__init__(areaStub, stage, groupId,
                                                   groupName, playerList, isGrouping, totalPlayerCount, startStageIndex)
        self._logger.add('serverId', self.serverId)

    @property
    def serverId(self):
        return self.areaStub.serverId

    def _addPlayersToGroup(self, encodedPlayerList, start):
        assert (start < len(encodedPlayerList))
        count = MatchGroupStubRemote.ADD_PLAYER_COUNT_PER_TIME
        while count > 0:
            try:
                plist = encodedPlayerList[start:start + count]
                addPlayerToGroup(self.serverId, self.roomId, self.master.roomId, self.groupId, plist)
                return len(plist)
            except FTMsgPackException:
                # 每次减少1/3
                newCount = max(1, count - count / 3)
                self._logger.warn('MatchGroupStubRemote._addPlayersToGroup msgTooLong',
                                  'count=', count,
                                  'newCount=', newCount)
                if newCount <= 1:
                    self._logger.error('MatchGroupStubRemote._addPlayersToGroup msgTooLong1',
                                       'count=', count,
                                       'newCount=', newCount)
                    return 1
                count = newCount
            except:
                self._logger.warn('MatchGroupStubRemote._addPlayersToGroup exception',
                                  'count=', count)
                return count

    def _doStartGroup(self):
        if self._logger.isDebug():
            self._logger.debug('MatchGroupStubRemote._doStartGroup',
                               'userCount=', len(self._playerMap),
                               'userIds=', self._playerMap.keys())
        startTime = time.time()

        createGroup(self.serverId, self.roomId, self.master.roomId, self.instId,
                    self.matchingId, self.groupId, self.groupName, self.stageIndex,
                    self.isGrouping, self.totalPlayerCount, self.startStageIndex)

        self._logger.info('MatchGroupStubRemote._doStartGroup createGroup OK',
                          'userCount=', len(self._playerMap),
                          'usedTime=', time.time() - startTime)
        index = 0
        playerList = self._playerMap.values()
        encodedPlayerList = encodePlayerListForAddGroup(playerList, 0, len(playerList))
        while index < len(encodedPlayerList):
            subStartTime = time.time()
            count = self._addPlayersToGroup(encodedPlayerList, index)
            self._logger.info('MatchGroupStubRemote._doStartGroup addPlayerToGroup OK',
                              'userCount=', len(self._playerMap),
                              'index=', index,
                              'count=', count,
                              'usedTime=', time.time() - subStartTime)
            index += max(1, count)

        startGroup(self.serverId, self.roomId, self.master.roomId, self.groupId)
        self._logger.info('MatchGroupStubRemote._doStartGroup OK',
                          'userCount=', len(self._playerMap),
                          'usedTime=', time.time() - startTime)

    def _doKillGroup(self):
        if self._logger.isDebug():
            self._logger.debug('MatchGroupStubRemote._doKillGroup',
                               'reason=', self.finishReason)
        killGroup(self.serverId, self.roomId, self.master.roomId, self.groupId, self.finishReason)

    def _doFinalGroup(self):
        if self._logger.isDebug():
            self._logger.debug('MatchGroupRemoteImpl.finalRemoteGroup',
                               'groupId=', self.groupId)
        finalGroup(self.serverId, self.roomId, self.master.roomId, self.groupId)


class MatchAreaStubRemote(MatchAreaStub):
    def __init__(self, master, roomId):
        super(MatchAreaStubRemote, self).__init__(master, roomId)
        # self.serverId = rpccore.getRpcDstRoomServerId(self.roomId, 0)


    def masterHeartbeat(self, master):
        if self._logger.isDebug():
            self._logger.debug('MatchAreaStubRemote.masterHeartbeat',
                               'roomId=', self.roomId,
                               'masterRoomId=', self.master.roomId)
        status = master.buildStatus()
        masterHeartbeat(self.serverId, self.roomId, self.master.roomId, status.toDict())

    def cancelInst(self, instId, reason):
        """
        分赛区取消比赛实例
        """
        cancelInst(self.serverId, self.roomId, self.master.roomId, instId, reason)

    def _createInstStubImpl(self, instId, startTime, needLoad):
        for _ in xrange(10):
            try:
                createInst(self.serverId, self.roomId, self.master.roomId, instId, startTime, needLoad)
                self._logger.info('MatchAreaStubRemote._createInstStubImpl ok',
                                  'instId=', instId,
                                  'startTime=', startTime,
                                  'needLoad=', needLoad)
                break
            except:
                self._logger.error('MatchAreaStubRemote._createInstStubImpl',
                                   'instId=', instId,
                                   'startTime=', startTime,
                                   'needLoad=', needLoad)
                ftcore.sleep(1)

        return MatchInstStubRemote(self, instId, startTime, needLoad)

    def _createGroupStubImpl(self, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, startStageIndex):
        return MatchGroupStubRemote(self, stage, groupId, groupName, playerList, isGrouping, totalPlayerCount, startStageIndex)
