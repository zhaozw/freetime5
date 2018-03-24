# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.table_state.state import MTableState

class MTableStateBaicheng(MTableState):
    
    def __init__(self):
        super(MTableStateBaicheng, self).__init__()
        # 鸡西玩法
        self.setState(MTableState.TABLE_STATE_DROP)
        # 吃
        self.setState(MTableState.TABLE_STATE_CHI)
        # 碰
        self.setState(MTableState.TABLE_STATE_PENG)
        # 杠
        self.setState(MTableState.TABLE_STATE_GANG)
        # 抢杠和(只有特大夹可以抢杠和)
        self.setState(MTableState.TABLE_STATE_QIANGGANG)
        #下锚
        self.setState(MTableState.TABLE_STATE_FANGMAO)
        #抢锚碰
        self.setState(MTableState.TABLE_STATE_QIANG_EXMAO)
        self.setState(MTableState.TABLE_STATE_QIANG_EXMAO_HU)
        # 和
        self.setState(MTableState.TABLE_STATE_HU)
        # 和牌后游戏结束
        self.setState(MTableState.TABLE_STATE_GAME_OVER)
        
    def getTimeOutByState(self, state):
        """超时设置"""
        return 12