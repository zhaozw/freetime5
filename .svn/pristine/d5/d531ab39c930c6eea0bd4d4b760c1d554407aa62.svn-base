# -*- coding=utf-8
'''
Created on 2017年4月6日

@author: yawen
'''
from majiang2.table_state_processor.processor import MProcessor
from majiang2.table_state.state import MTableState
from freetime5.util import ftlog

class MFlowerProcessor(MProcessor):
    '''
    '''

    def __init__(self, count, playMode,tableConfig):
        super(MFlowerProcessor, self).__init__(tableConfig)
        # 玩家数量
        self.__player_count = count
        # 玩家的花牌
        self.__flower_tiles = [[] for _ in range(self.playerCount)]
        # 初始状态
        self.__state = MTableState.TABLE_STATE_NEXT
        # 是否继续补花
        self.__is_begin = False
        # 座位号
        self.__seatId = 0
        
    @property
    def seatId(self):
        return self.__seatId
    
    def setSeatId(self, seatId):
        self.__seatId = seatId
        
    @property
    def isBegin(self):
        return self.__is_begin
    
    def setIsBegin(self, calc):
        self.__is_begin = calc
        
    @property
    def playerCount(self):
        return self.__player_count
    
    def setPlayerCount(self, count):
        self.__player_count = count

    def reset(self):
        self.__flower_tiles = [[] for _ in range(self.playerCount)]
        self.__state = MTableState.TABLE_STATE_NEXT
        self.__calc_continue = True
        self.__is_add_tile = False
        self.__seatId = 0

    def initProcessor(self, state, flowers, isBeginGame, seatId):
        self.__state = state
        self.setFlowerTiles(flowers)
        self.setIsBegin(isBeginGame)
        self.setSeatId(seatId)
        
    def getFlower(self, curSeat):
        for index in range(self.playerCount):
            seatId = (curSeat + index) % self.playerCount
            if len(self.flowerTiles[seatId]) > 0:
                flower = self.flowerTiles[seatId].pop(0)
                return flower, seatId
        self.setState(MTableState.TABLE_STATE_NEXT)
        self.reset()
        return None, 0

    @property
    def state(self):
        return self.__state

    def setState(self, state):
        self.__state = state
        if self.state == MTableState.TABLE_STATE_NEXT:
            self.reset()

    @property
    def flowerTiles(self):
        return self.__flower_tiles

    def setFlowerTiles(self, flowers):
        self.__flower_tiles = flowers

    def getState(self):
        """获取状态  0 补花完毕
        """
        if self.state != MTableState.TABLE_STATE_NEXT:
            ftlog.info('MFlowerProcessor.getState return:', self.state)
        return self.state
    
if __name__ == "__main__":
    dp = MFlowerProcessor(4)
