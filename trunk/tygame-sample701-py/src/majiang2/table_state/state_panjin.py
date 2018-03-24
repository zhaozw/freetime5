# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.table_state.state import MTableState
from freetime5.util import ftlog

class MTableStatePanjin(MTableState):
    
    def __init__(self):
        super(MTableStatePanjin, self).__init__()
        
        self.setState(MTableState.TABLE_STATE_DROP)
        # 吃
        self.setState(MTableState.TABLE_STATE_CHI)
        # 碰
        self.setState(MTableState.TABLE_STATE_PENG)
        # 杠
        self.setState(MTableState.TABLE_STATE_GANG)
        # 抢杠和(只有特大夹可以抢杠和)
        self.setState(MTableState.TABLE_STATE_QIANGGANG)
        # 和
        self.setState(MTableState.TABLE_STATE_HU)
        # 和牌后游戏结束
        self.setState(MTableState.TABLE_STATE_GAME_OVER)
        
    def getStandUpSchedule(self, state = MTableState.TABLE_STATE_NONE):
        """获取每一小局的发牌流程
        先加漂
        再加倍
        再发牌
        """
        if state == MTableState.TABLE_STATE_NONE:
            if self.states & MTableState.TABLE_STATE_DOUBLE:
                ftlog.debug('MTableStatePanjin.getStandUpSchedule return state:', MTableState.TABLE_STATE_DOUBLE)
                return MTableState.TABLE_STATE_DOUBLE
            
            ftlog.debug('MTableStatePanjin.getStandUpSchedule return 1 state:', MTableState.TABLE_STATE_NEXT)
            return MTableState.TABLE_STATE_NEXT
        elif state == MTableState.TABLE_STATE_DOUBLE:
            ftlog.debug('MTableStatePanjin.getStandUpSchedule return state:', MTableState.TABLE_STATE_NEXT)
            return MTableState.TABLE_STATE_NEXT
        
        ftlog.debug('MTableStatePanjin.getStandUpSchedule return 3 state:', MTableState.TABLE_STATE_NEXT)
        return MTableState.TABLE_STATE_NEXT