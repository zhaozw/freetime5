# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.table_state_processor.processor import MProcessor
from freetime5.util import ftlog
from majiang2.table_state.state import MTableState
import random

class MHuanSanZhangProcessor(MProcessor):
    '''
    换三张流程：
    第一阶段，询问客户换哪三张，附带推荐换的三张牌
    第二阶段，收到客户换的三张牌，随机换牌顺序，然后发送换的牌给客户
    第三阶段，结束换三张流程
    '''
    SCHEDULE_HUAN_NONE = -1
    # 换牌中
    SCHEDULE_HUAN_INIT = 1

    
    def __init__(self, count, playMode, tableConfig):
        super(MHuanSanZhangProcessor, self).__init__(tableConfig)
        # 玩家数量
        self.__player_count = count
        # 玩法
        self.__player_mode = playMode
        # 当前阶段
        self.__schedule = self.SCHEDULE_HUAN_NONE
        # 换三张等待时间
        self.__huanPai_timeOut = 12
        # 玩家换后的牌           
        self.__after_change_tiles = [[0, 0, 0] for _ in range(self.playerCount)]
        # 禁止玩家换的牌
        self.__forbid_change_tiles = [[] for _ in range(self.playerCount)]
        # 收到玩家要换的牌
        self.__get_tiles = [[0, 0, 0] for _ in range(self.playerCount)]
        # 建议玩家换的牌
        self.__suggest_tiles = [[0, 0, 0] for _ in range(self.playerCount)]
        # 随机的顺序 1:顺时针  2:逆时针  3:对换
        self.getRandType()
    
    def reset(self):
        self.__schedule = self.SCHEDULE_HUAN_NONE
        self.__huanPai_timeOut = 12
        self.__after_change_tiles = [[0, 0, 0] for _ in range(self.playerCount)]
        self.__forbid_change_tiles = [[] for _ in range(self.playerCount)]
        self.__get_tiles = [[0, 0, 0] for _ in range(self.playerCount)]
        self.__suggest_tiles = [[] for _ in range(self.playerCount)]
        self.getRandType()
        ftlog.debug('[MHuanSanZhangProcessor.reset]  schedule:', self.schedule
                    , 'changeTiles:', self.__after_change_tiles, 'noChangeTiels:', self.__forbid_change_tiles)
        
    def getRandType(self):
        if self.playerCount == 3:
            self.__rand_type = random.randint(1, 2)
        elif self.playerCount == 2:
            self.__rand_type = 3
        else:
            self.__rand_type = random.randint(1, 3)
         
    @property
    def huanSanZhangTimeOut(self):
        return self.__huanPai_timeOut
    
    def setHuanSanZhangTimeOut(self, timeOut):
        self.__huanPai_timeOut = timeOut
    
    @property
    def getTilesFromUser(self):
        return self.__get_tiles
    
    @property
    def afterChangeTiles(self):
        return self.__after_change_tiles
    
    def setAfterChangeTiles(self, changeTiles):
        self.__after_change_tiles = changeTiles
        ftlog.debug('MHuanSanZhangProcessor.afterChangeTiles:', self.afterChangeTiles)
        
    @property
    def suggestTiles(self):
        return self.__suggest_tiles
    
    def setSuggestTiles(self, tiles):
        self.__suggest_tiles = tiles

    @property
    def forbidChangeTiles(self):
        return self.__forbid_change_tiles
    
    def setForbidChangeTiles(self, forbidChangeTiles):
        self.__forbid_change_tiles = forbidChangeTiles
        ftlog.debug('MHuanSanZhangProcessor.forbidChangeTiles:', self.forbidChangeTiles)
    
    @property
    def schedule(self):
        return self.__schedule
    
    def setSchedule(self, schedule):
        self.__schedule = schedule
 
    @property
    def randType(self):
        return self.__rand_type
 
    @property
    def playerCount(self):
        return self.__player_count
    
    def setPlayerCount(self, pCount):
        self.__player_count = pCount

    @property
    def playMode(self):
        """获取本局玩法"""
        return self.__player_mode

    def setPlayMode(self, playMode):
        self.__player_mode = playMode

    def updateTimeOut(self, deta):
        if self.schedule == self.SCHEDULE_HUAN_INIT:
            if self.huanSanZhangTimeOut >= 0:
                self.__huanPai_timeOut += deta
                ftlog.debug('[MHuanSanZhangProcessor.updateTimeOut]  schedule:', self.schedule, ' huanPaiTimeOut:', self.__huanPai_timeOut)
    
    def getState(self):
        """获取状态 
        """
        if self.schedule != self.SCHEDULE_HUAN_NONE:
            return MTableState.TABLE_STATE_CHANGE_TILE
        
        return MTableState.TABLE_STATE_NEXT
    
    def getAutoDecideSeatsBySchedule(self):
        """根据座位号，获取托管的座位号列表"""
        seats = []
   
        if self.schedule == self.SCHEDULE_HUAN_INIT:
            for index in range(self.playerCount):
                if self.players[index].isRobot():
                    seats.append(index)
                    
                if (self.players[index].smartOperateCount > 0) and (index not in seats):
                    seats.append(index)
                
                if (self.huanSanZhangTimeOut <= 0) and (not self.isNeverAutoDecide()) and (index not in seats):
                    seats.append(index)
                
        if len(seats) > 0:
            ftlog.debug('[MHuanSanZhangProcessor]  schedule:', self.schedule
                    , ' afterChangeTiles:', self.afterChangeTiles
                    , ' seats:', seats)
                    
        return seats
     
    def randChangeTiles(self):
        '''
        根据randType来交换牌 1:顺时针 2:逆时针 3:对换
        '''
        ftlog.debug('MHuanSanZhangProcessor.randChangeTiles before getTilesFromUser:', self.getTilesFromUser
                    , ' suggestTiles:', self.suggestTiles
                    , ' afterChangeTiles:', self.afterChangeTiles
                    , ' randType:', self.randType)
        if self.randType == 1:
            for seatId in range(self.playerCount):
                fromSeatId = (seatId + 1) % self.playerCount
                self.afterChangeTiles[seatId] = self.getTilesFromUser[fromSeatId]
        elif self.randType == 2:
            for seatId in range(self.playerCount):
                fromSeatId = (seatId - 1) % self.playerCount
                self.afterChangeTiles[seatId] = self.getTilesFromUser[fromSeatId]
        elif self.randType == 3:
            for seatId in range(self.playerCount):
                fromSeatId = (seatId + self.playerCount / 2) % self.playerCount
                self.afterChangeTiles[seatId] = self.getTilesFromUser[fromSeatId]
        
        ftlog.debug('MHuanSanZhangProcessor.randChangeTiles getTilesFromUser:', self.getTilesFromUser
                    , ' suggestTiles:', self.suggestTiles
                    , ' afterChangeTiles:', self.afterChangeTiles)
        
    def setTilesFromUser(self, seatId, tiles, msgProcessor):
        """玩家确定换哪三张牌    
        """
        # 玩家已经选择过了，不能再次选择
        if self.getTilesFromUser[seatId] != [0, 0, 0]:
            return  

        self.getTilesFromUser[seatId] = tiles
        
        # 换牌确认成功，广播通知前端
        for _id in range(self.playerCount):
            msgProcessor.table_call_notify_huansanzhang(self.players[_id].userId, _id, seatId, tiles, self.actionID, False)
        
        if self.isAllConfirmed():
            # 玩家换牌信息保存，断线重连会用到
            for _id in range(self.playerCount):
                self.players[_id].setChangeTiles(self.getTilesFromUser[_id])
                self.players[_id].setChangeTilesModel(self.randType)
            self.setHuanSanZhangTimeOut(0)
            self.randChangeTiles()
            # 所有人都已选择 换牌结束
            self.setSchedule(self.SCHEDULE_HUAN_NONE)   
     
    def autoDecide(self, seatId, msgProcessor):
        """自动操作"""
        if self.schedule == self.SCHEDULE_HUAN_INIT and self.getTilesFromUser[seatId] == [0, 0, 0]:
            ftlog.debug('[MHuanSanZhangProcessor] afterChangeTiles:', self.afterChangeTiles, 'getTiles:', self.getTilesFromUser, 'suggestTiles:', self.suggestTiles)
            self.setTilesFromUser(seatId, self.suggestTiles[seatId], msgProcessor)
            ftlog.debug('[MHuanSanZhangProcessor] 2 afterChangeTiles:', self.afterChangeTiles, 'getTiles:', self.getTilesFromUser, 'suggestTiles:', self.suggestTiles)
        
    def beginHuanSanZhang(self, msgProcessor, actionId, pauseProcessor):
        if self.schedule != self.SCHEDULE_HUAN_INIT:
            return
     
        ftlog.debug('[MHuanSanZhangProcessor] beginHuanSanZhang changeTiles:', self.afterChangeTiles, 'forbidChangeTiles:', self.forbidChangeTiles)
        
        for seatId in range(self.playerCount):
            message = msgProcessor.table_call_ask_huansanzhang(self.players[seatId].userId
                    , seatId
                    , self.suggestTiles[seatId]
                    , self.forbidChangeTiles[seatId]
                    , self.huanSanZhangTimeOut
                    , actionId)
            
            pauseProcessor.addDelayTask(4, self.players[seatId].userId, message, msgProcessor)
        # 4 秒是播放开局动画的时间
        self.__huanPai_timeOut += 4    
        
    def initProcessor(self, actionID, seatId, state, extendInfo=None, timeOut=9):
        pass
    
    def updateProcessor(self, actionID, seatId, state, tile, pattern=None):
        pass
    
    def isAllConfirmed(self):
        """是否所有人都已选择
        """
        for tiles in self.getTilesFromUser:
            if tiles == [0, 0, 0]:
                return False
        return True

    def handlePlayerReconnect(self, seatId, msgProcessor):
        '''
        不是本人的消息 断线重连在这里补发，结束后，则不补发
        :param seatId:
        :param msgProcessor:
        '''
        ftlog.debug('[MHuanSanZhangProcessor].handlePlayerReconnect seatId:', seatId, 'State:', self.getState())
        if not self.getState():
            return 
        for _id in range(self.playerCount):
            if self.getTilesFromUser[_id] != [0, 0, 0] and _id != seatId:
                msgProcessor.table_call_notify_huansanzhang(self.players[seatId].userId
                                                            , seatId
                                                            , _id
                                                            , self.getTilesFromUser[_id]
                                                            , True)

if __name__ == "__main__":
    dp = MHuanSanZhangProcessor(4)
