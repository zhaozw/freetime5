# ! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/25

from majiang2.table_state_processor.processor import MProcessor
from majiang2.tile.tile import MTile
from freetime5.util import ftlog

class MAbsenceProcessor(MProcessor):
    """定缺处理
       在庄家14张牌，闲家13张牌时，庄家不打牌，进入定缺阶段，在所有玩家都定好缺之后，庄家才能继续打牌
    """

    SCHEDULE_ABSENCE_NONE = 0  # 默认处于非定缺阶段
    SCHEDULE_ABSENCE_BEGIN = 1  # 开始进入定缺阶段
    SCHEDULE_ABSENCE_DING = 2  # 询问玩家选择缺哪门
    SCHEDULE_ABSENCE_END = 3  # 定缺结束，区分断线重连时，需要补发给玩家定缺信息
    COLOR_ABSENCE_INIT = -1  # 初始缺哪门状态

    def __init__(self, count, playMode, tableConfig):
        super(MAbsenceProcessor, self).__init__(tableConfig)
        # 玩家数量
        self.__player_count = count
        # 玩法
        self.__player_mode = playMode
        # 调度情况
        self.__schedule = self.SCHEDULE_ABSENCE_NONE
        # 缺门情况
        self.__absenceColor = [self.COLOR_ABSENCE_INIT] * self.playerCount
        # 建议缺门
        self.__suggestColor = [self.COLOR_ABSENCE_INIT] * self.playerCount
        # 超时时间
        self.__absence_timeout = 6

    def reset(self):
        self.__schedule = self.SCHEDULE_ABSENCE_NONE
        self.__absenceColor = [self.COLOR_ABSENCE_INIT] * self.playerCount
        # 建议缺门
        self.__suggestColor = [self.COLOR_ABSENCE_INIT] * self.playerCount
        # 超时时间
        self.__absence_timeout = 6
        
    @property
    def absenceTimeOut(self):
        return self.__absence_timeout
    
    def setAbsenceTimeOut(self, timeout):
        self.__absence_timeout = timeout
    
    def updateTimeOut(self, deta):
        if self.schedule == self.SCHEDULE_ABSENCE_DING:
            self.__absence_timeout += deta
        ftlog.debug('MAbsenceProcessor  schedule:', self.schedule, ' absenceTimeOut:', self.absenceTimeOut)
    
    @property
    def suggestColor(self):    
        return self.__suggestColor
    
    def setSuggestColor(self, colors):
        self.__suggestColor = colors
    
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

    @property
    def schedule(self):
        return self.__schedule

    def setSchedule(self, schedule):
        self.__schedule = schedule

    @property
    def absenceColor(self):
        return self.__absenceColor

    def setAbsenceColor(self, value):
        self.__absenceColor = value

    def getState(self):
        return 0 if (self.schedule == self.SCHEDULE_ABSENCE_NONE or self.schedule == self.SCHEDULE_ABSENCE_END) else 1

    def beginAbsence(self):
        """
        开始定缺，前端收到这个消息之后提示让玩家选择缺哪门
        """
        ftlog.debug('MAbsenceProcessor.beginAbsence...')
        self.setSchedule(self.SCHEDULE_ABSENCE_BEGIN)
    

    def onBankerAddedFirstTile(self, actionId, pauseProcessor, isDelay=True):
        """
        庄家摸完了牌，开始询问玩家进行定缺
        """
        ftlog.debug('MAbsenceProcessor.onBankerAddedFirstTile absenceColor:', self.absenceColor
                    , ' suggestColor:', self.suggestColor)
        self.setSchedule(self.SCHEDULE_ABSENCE_DING)

        for seatId in range(self.playerCount):
            message = self.msgProcessor.table_call_ask_absence(self.players[seatId].userId
                    , seatId
                    , self.suggestColor[seatId]
                    , self.absenceTimeOut
                    , False
                    , actionId)
            if isDelay:
                pauseProcessor.addDelayTask(4, self.players[seatId].userId, message, self.msgProcessor)
            else:
                self.msgProcessor.send_message(message, self.players[seatId].userId)
        if isDelay:
            # 4s 播放动画的时间 没有换三张 
            self.setAbsenceTimeOut(self.absenceTimeOut + 4)
        else:
            # 有换三张 则需要5秒延时
            self.setAbsenceTimeOut(self.absenceTimeOut + 5)
        
        
        
    def getAutoDecideSeatsBySchedule(self):
        '''
        托管的动作
        '''
        if self.getState() == 0:
            return []
        
        autos = []
        for seatId in range(self.playerCount):
            if self.absenceColor[seatId] != self.COLOR_ABSENCE_INIT:
                continue
            
            if self.players[seatId].isRobot():
                autos.append(seatId)
                
            if (self.players[seatId].smartOperateCount > 0) and (seatId not in autos):
                autos.append(seatId)
                
            if (self.absenceTimeOut <= 0) and (seatId not in autos) and (not self.isNeverAutoDecide()):
                autos.append(seatId)
    
        if len(autos) > 0:
            ftlog.debug('MAbsenceProcessor.getAutoDecideSeatsBySchedule return autos:', autos)
            
        return autos
     
    def autoDecide(self, seatId, msgProcessor, actionId):
        """自动操作"""
        ftlog.debug('MAbsenceProcessor.autoDecide schedule:', self.schedule
                    , 'suggestColor:', self.suggestColor[seatId]
                    , ' seatId:', seatId
                    , ' acitionId:', actionId)
        
        if self.schedule == self.SCHEDULE_ABSENCE_DING:
            color = self.suggestColor[seatId]
            self.dingAbsence(seatId, color, actionId)

    def dingAbsence(self, seatId, color, actionId):
        """玩家定缺某个花色
        """
        # 玩家已经选择过了，不能再次选择
        if self.absenceColor[seatId] != self.COLOR_ABSENCE_INIT:
            ftlog.warn('MAbsenceProcessor.dingAbsence already absenced seatId:', seatId
                        , ' absenceColor:', self.absenceColor)
            return

        # 只能缺万筒条中的一个颜色
        if color not in (MTile.TILE_WAN, MTile.TILE_TONG, MTile.TILE_TIAO):
            ftlog.warn('MAbsenceProcessor.dingAbsence wrong color..')
            return

        self.absenceColor[seatId] = color
        self.msgProcessor.table_call_notify_absence(self.players[seatId].userId
                , seatId
                , self.absenceColor[seatId]
                , False
                , actionId)

    
        if self.isAllSelected():
            # 所有人都已选择定缺，结束定缺状态
            ftlog.debug('MAbsenceProcessor.dingAbsence, all absenced !!!')
            self.setSchedule(self.SCHEDULE_ABSENCE_END)
            self.setAbsenceTimeOut(0)

    def isAllSelected(self):
        """是否所有人都已定缺
        """
        for color in self.absenceColor:
            if color == self.COLOR_ABSENCE_INIT:
                return False
        return True

    def handlePlayerReconnect(self, userId, seatId):
        """处理玩家的断线重连，定缺断线重连分为庄家断线、非庄家断线
        """
        if not self.msgProcessor:
            return
        
        # 区分 定缺完成以后，玩家是否出牌，若未出牌，则msg_longnet会补发带出牌消息的absence_end，若出过牌，则只补发colors   
        latestMsg = self.msgProcessor.latestMsg[seatId]
        reConnect = True if latestMsg and latestMsg.getCmd() != 'absence_end' else False
        if self.schedule == self.SCHEDULE_ABSENCE_END and reConnect: 
            self.msgProcessor.table_call_absence_end(userId, seatId, self.absenceColor, self.players[seatId], 0, True)
