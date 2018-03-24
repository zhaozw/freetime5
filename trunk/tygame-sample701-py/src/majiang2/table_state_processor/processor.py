# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
"""
操作的基类
"""
from freetime5.util import ftlog
from majiang2.table.table_config_define import MTDefine
from majiang2.table_state.state import MTableState


class MProcessor(object):
    def __init__(self, tableConfig):
        super(MProcessor, self).__init__()
        self.__action_id = 0
        self.__playsers = []
        self.__time_out = 0
        self.__table_tile_mgr = None
        self.__auto_win = False
        self.__msg_processor = None
        self.__tableConfig = tableConfig
        self.__tableType = MTDefine.TABLE_TYPE_CREATE
        self.__gameId = 0
        self.__roomId = 0
        self.__tableId = 0
        self.__roomConfig = None
        
    @property
    def roomId(self):
        return self.__roomId
    
    def setRoomId(self, roomId):
        self.__roomId = roomId
        
    @property
    def gameId(self):
        return self.__gameId
    
    def setGameId(self, gameId):
        self.__gameId = gameId
        
    @property
    def tableId(self):
        return self.__tableId
    
    def setTableId(self, tableId):
        self.__tableId = tableId
        
    @property
    def msgProcessor(self):
        return self.__msg_processor
    
    def setMsgProcessor(self, msgProcessor):
        self.__msg_processor = msgProcessor
        
    @property
    def autoWin(self):
        return self.__auto_win
    
    def setAutoWin(self, autoWin):
        ftlog.debug('MProcessor win_automatically:', autoWin)
        self.__auto_win = autoWin
        
    @property
    def tableConfig(self):
        return self.__tableConfig
    
    def setTableConfig(self, tableConfig):
        self.__tableConfig = tableConfig
        
    @property
    def roomConfig(self):
        return self.__roomConfig
    
    def setRoomConfig(self, config):
        self.__roomConfig = config
        
    def isNeverAutoDecide(self):
        return self.tableConfig.get(MTDefine.TRUSTTEE_TIMEOUT, 1) == MTDefine.NEVER_TIMEOUT
        
    @property
    def tableType(self):
        return self.__tableType
    
    def setTableType(self, tableType):
        self.__tableType = tableType
        
    def setTableTileMgr(self, tableTileMgr):
        """设置牌局手牌管理器"""
        self.__table_tile_mgr = tableTileMgr
        
    @property
    def tableTileMgr(self):
        return self.__table_tile_mgr
        
    @property
    def actionID(self):
        """操作ID，作为当前操作有效性的标记"""
        return self.__action_id
    
    def setActionID(self, actionID):
        """设置操作ID"""
        self.__action_id = actionID
        
    @property
    def timeOut(self):
        """获取超时时间"""
        return self.__time_out
    
    def setTimeOut(self, timeOut):
        """设置超时"""
        self.__time_out = timeOut
        
    def updateTimeOut(self, deta):
        """更新超时"""
        self.__time_out += deta
        if self.__time_out < 0:
            self.__time_out = 0
        
    @property
    def players(self):
        """玩家，由牌桌同步"""
        return self.__playsers
    
    def setPlayers(self, players):
        """设置玩家"""
        self.__playsers = players
        
    def hasAutoDecideAction(self, curSeat, trustTeeSet):
        """是否有托管的行为"""
        return MTDefine.INVALID_SEAT
    
    def isUserAutoDecided(self, seatId, trustTeeSet, state=MTableState.TABLE_STATE_NEXT, response=False):
        """
        判断用户是否由系统托管
        1）用户自己为托管状态则托管
        2）用户未托管，超时，则判断超时托管配置
        2.1）超时托管，则过关
        2.2）超时不托管，则不托管
        3）好友桌不会设置用户托管状态
        """
        if state == MTableState.TABLE_STATE_NEXT:
            return False
        
        if response:
            # 如果用户已应答，则替用户做剩下的操作
            return True
        
        # 自动胡，自动处理
        if self.autoWin and (state & MTableState.TABLE_STATE_HU):
            ftlog.debug('table win_automatically, ok...')
            return True
        
        if self.players[seatId].userId < 10000:
            ftlog.debug('MProcessor.isUserAutoDecided robot:', self.players[seatId].userId)
            return True
        
        if MTDefine.TABLE_TYPE_CREATE == self.tableType:
            ftlog.debug('MProcessor.isUserAutoDecided TABLE_TYPE_CREATE')
            ftlog.debug('MProcessor.isUserAutoDecided user autoDecide, decide:', self.players[seatId].autoDecide
                        , ' isStateFixeder:', self.players[seatId].isStateFixeder())
            if self.players[seatId].autoDecide or self.players[seatId].isStateFixeder():
                if self.players[seatId].userId > 10000 and (state & MTableState.TABLE_STATE_HU):
                    ftlog.debug('MProcessor.isUserAutoDecided user win not automatically....')
                    if self.players[seatId].isWon():
                        # 如果玩家已经胡过一次，后续自动胡
                        return True
                    else:
                        return False
                elif self.players[seatId].userId > 10000 and self.players[seatId].isStateFixeder() \
                    and (state & MTableState.TABLE_STATE_GANG):
                    if self.tableTileMgr and self.tableTileMgr.selectGangAfterTing():
                        ftlog.debug('MProcessor.isUserAutoDecided user gang not automatically....')
                        return False
                ftlog.debug('MProcessor.isUserAutoDecided user ting or autoDecide, return automatically....')
                return True
        elif MTDefine.TABLE_TYPE_NORMAL == self.tableType:
            ftlog.debug('MProcessor.isUserAutoDecided TABLE_TYPE_NORMAL')
            if self.players[seatId].autoDecide or self.players[seatId].isStateFixeder():
                return True
            
        if self.players[seatId].userId < 10000:
            ftlog.debug('MProcessor.isUserAutoDecided robot:', self.players[seatId].userId)
            return True
        
        if self.players[seatId].smartOperateCount > 0:
            ftlog.debug('MProcessor.isUserAutoDecided smartOperate...')
            return True
        
        if trustTeeSet == MTDefine.NEVER_TIMEOUT:
            # 超时不托管
            return False
        
        if self.timeOut:
            # 未超时
            return False
        else:
            self.players[seatId].addTimeOutCount()
            # 若玩家没有超时过 通知用户玩家超时
            if not self.players[seatId].isHaveTimeOut():
                if self.players[seatId].timeOutCount == 1:
                    self.setTimeOut(12)
                    self.msgProcessor.table_call_notifyTimeOut(seatId, self.timeOut, self.players[seatId].timeOutCount)
                return False
        
        if (self.players[seatId].timeOutCount == 2) or (self.players[seatId].timeOutCount == 1 and self.players[seatId].isHaveTimeOut()):       
            ftlog.debug('MProcessor.isUserAutoDecided return True')
            return True
        else:
            ftlog.debug('MProcessor.isUserAutoDecided last return False')
            return False
        
