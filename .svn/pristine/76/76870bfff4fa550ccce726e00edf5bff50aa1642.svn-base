# -*- coding=utf-8
'''
Created on 2016年12月3日

@author: luoxf
'''
from majiang2.table_state.state import MTableState

class MTableStateWuWei(MTableState):
    
    def __init__(self):
        super(MTableStateWuWei, self).__init__()
        # 出牌
        self.setState(MTableState.TABLE_STATE_DROP)
        # 碰
        self.setState(MTableState.TABLE_STATE_PENG)
        # 杠
        self.setState(MTableState.TABLE_STATE_GANG)
        # 听
        self.setState(MTableState.TABLE_STATE_TING)
        # 抢听
        # self.setState(MTableState.TABLE_STATE_GRABTING)
        # 抢杠和
        self.setState(MTableState.TABLE_STATE_QIANGGANG)
        # 和
        self.setState(MTableState.TABLE_STATE_HU)
        # 和牌后游戏结束
        self.setState(MTableState.TABLE_STATE_GAME_OVER)
