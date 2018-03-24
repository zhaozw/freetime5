# -*- coding:utf-8 -*-
"""
Created on 2017年10月17日19:49:31

@author: yzx
"""
from freetime5.util import ftlog
from majiang2.poker2.entity.game.rooms.normal_room import TYNormalRoom
from matchcomm.matchs import dao
from matchcomm.matchs.stage_match.interfacegame import PokerMatchPlayerNotifier, PokerMatchTableController, \
    MatchRankRewardsIFStage
from matchcomm.matchs.stage_match.room import StageMatchRoomMixin
from tuyoo5.core import tyglobal


class PokerCtrlStageMatchRoom(TYNormalRoom, StageMatchRoomMixin):
    """通用的比赛房间控制器，运行于GR进程.

    继承自TYRoom，创建玩家的通知器，比赛游戏桌控制器，初始化通用比赛。

    """

    def __init__(self, roomDefine):
        super(PokerCtrlStageMatchRoom, self).__init__(roomDefine)
        serverType = tyglobal.serverType()
        # GR才进行加载
        if serverType == tyglobal.SRV_TYPE_GAME_ROOM:
            ftlog.info('PokerCtrlStageMatchRoom.init ...',
                       'bigRoomId=', roomDefine.bigRoomId,
                       'gameId=', roomDefine.gameId,
                       'roomId=', roomDefine.roomId)
            self.shadowRoomIds = roomDefine.shadowRoomIds
            self.tableCount = roomDefine.tableCount
            self.playerNotifier = PokerMatchPlayerNotifier(self)
            self.tableController = PokerMatchTableController()
            self.matchRankRewardsIF = MatchRankRewardsIFStage()
            self.initDao()
            self.initStageMatch()
            ftlog.info('PokerCtrlStageMatchRoom.init ok',
                       'bigRoomId=', roomDefine.bigRoomId,
                       'gameId=', roomDefine.gameId,
                       'roomId=', roomDefine.roomId)
        else:
            #TODO GT 中需要使用roomConf
            ftlog.info('PokerCtrlStageMatchRoom.init ...',
                       'bigRoomId=', roomDefine.bigRoomId,
                       'gameId=', roomDefine.gameId,
                       'roomId=', roomDefine.roomId)
            self.shadowRoomIds = roomDefine.shadowRoomIds
            self.tableCount = roomDefine.tableCount

    def initDao(self):
        dao.DaoRoomInfo.initialize()
        dao.DaoMatchStatus.initialize()
        dao.DaoMatchSigninRecord.initialize()
        dao.DaoUserSigninRecord.initialize()
        dao.DaoMatchPlayerInfo.initialize()
        dao.DaoUserMatchHistory.initialize()

    def doQuickStart(self, msg):
        """
        覆盖TYRoom.doQuickStart方法
        """
        StageMatchRoomMixin.doMatchQuickStart(self,msg)
