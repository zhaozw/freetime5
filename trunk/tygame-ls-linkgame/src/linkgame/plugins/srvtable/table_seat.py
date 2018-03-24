# -*- coding: utf-8 -*-
'''
Created on 2015年7月7日

@author: zqh
'''
from freetime5.util import ftstr

class TYSeat(object):
    '''
    为了兼容老版Table（seat是list类型）， TYSeat需要实现list的部分函数
    Note： 如果直接继承list的话，在redis化时，没有覆写的函数会出现致数据不一致的问题， 所以不推荐。
    注意约定: 此列表中第0个字段为当前座位的上userId,
            此列表中第1个字段为当前座位的玩家状态,
    ''' 

    INDEX_SEATE_USERID = 0  # 第0个字段固定为座位上的userId
    INDEX_SEATE_STATE = 1  # 第1个字段固定为座位的状态

    SEAT_STATE_IDEL = 0  # 座位的状态 空闲
    SEAT_STATE_WAIT = 10  # 座位的状态 玩家等待
    SEAT_STATE_READY = 20  # 座位的状态 玩家准备
    SEAT_STATE_PLAYING = 30  # 座位的状态 玩家游戏中


    def __init__(self, table):
        self.table = table
        self._list = [0, self.SEAT_STATE_IDEL]


    def __getitem__(self, index):
        return self._list[index]


    def __setitem__(self, index, value):  
        self._list[index] = value
    

    def __len__(self):
        return len(self._list)


    def __str__(self):
        return self._list.__str__()

    
    def __repr__(self):
        return self._list.__repr__()
    

    def getDatas(self):
        return self._list


    def update(self, stateList):
        '''
        将 stateList (list类型) 数据更新到TYSeat类属性
        TYSeat子类可以通过覆写此函数来扩展属性,
        此方法通常再初始化桌子状态时调用
        '''
        assert(isinstance(stateList, list))        
        self._list = ftstr.cloneData(stateList)


    def replace(self, stateList):
        self._list = stateList


    @property
    def userId(self):
        return self._list[self.INDEX_SEATE_USERID]


    @userId.setter
    def userId(self, userId):
        self._list[self.INDEX_SEATE_USERID] = userId


    @property
    def state(self):
        return self._list[self.INDEX_SEATE_STATE]


    @state.setter
    def state(self, state):
        self._list[self.INDEX_SEATE_STATE] = state


    #功能函数    
    def isEmptySeat(self):
        return self.userId == 0

    
    def isPlayingSeat(self):
        return not self.isEmptySeat() and self.state == TYSeat.SEAT_STATE_PLAYING
    
    
    def setPlayingState(self):
        self.state = TYSeat.SEAT_STATE_PLAYING
        
        
    def isWaitingSeat(self):
        return not self.isEmptySeat() and self.state == TYSeat.SEAT_STATE_WAIT
    
    
    def setWaitingState(self):
        self.state = TYSeat.SEAT_STATE_WAIT
