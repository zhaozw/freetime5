# -*- coding=utf-8 -*-
'''
Created on 2015年9月30日
麻将好友桌的牌桌，负责好友桌号的管理和好友桌赛制的调度。
@author: 赵良
'''
from majiang2.table.majiang_table_observer import MajiangTableObserver
from majiang2.table_statistic.statistic import MTableStatistic
from tuyoo5.core.typlugin import gameRpcUtilOne


class XueZhanTableObserver(MajiangTableObserver):
    def __init__(self, gameId, roomId, tableId):
        super(XueZhanTableObserver, self).__init__(gameId, roomId, tableId)
        
    def onBeginGame(self, players, banker):
        """游戏开始"""
        for userId in players:
            if userId < 10000:
                continue
            
            gameRpcUtilOne.srvutil.gamePlay(userId, self.gameId, self.roomId, self.tableId, banker)

    def onWinLoose(self):
        """结果"""
        pass
    
    def onGameEvent(self, event, players, roundId):
        # 统计
        self.tableStatistic.reportEvent(event
                , players
                , self.gameId
                , self.roomId
                , self.tableId
                , roundId)
     
    def upDateUserLoopTask(self, players, seatIds=[]):
        '''
        循环周期任务
        '''
        for player in players:
            if (not player) or player.isRobot():
                continue
            
            # 指定要更新的seatId
            if seatIds and player.curSeatId not in seatIds:
                continue
            
            gameRpcUtilOne.srvutil.tableLoopTask(player.userId, self.gameId, self.bigRoomId, self.tableId)

    def upDateUserWinTimesTask(self, players, winStateList, seatIds=[]):
        '''
        循环胜局任务
        '''
        for player in players:
            if (not player) or  player.isRobot():
                continue
            
            if seatIds and player.curSeatId not in seatIds:
                continue
            
            gameRpcUtilOne.srvutil.tableWinTimes(player.userId, self.gameId, self.bigRoomId, winStateList[player.curSeatId])
                  
    def upDateUserWinStreaks(self, players, winStateList, tableConfig, winNumList, userTileInfo, seatIds=[]):
        '''
        连胜任务更新
        '''
        for player in players:
            if (not player) or player.isRobot():
                continue
            
            if seatIds and player.curSeatId not in seatIds:
                continue
            
            tableConfigAll = {
                'roomConfig':tableConfig,
                'winNumList':winNumList[player.curSeatId],
                'userTileInfo':userTileInfo[player.curSeatId]
                }
            gameRpcUtilOne.srvutil.tableWinStreaks(player.userId, self.gameId, self.bigRoomId, winStateList[player.curSeatId], tableConfigAll)
