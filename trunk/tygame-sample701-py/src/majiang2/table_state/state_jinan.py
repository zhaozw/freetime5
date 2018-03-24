# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.table_state.state import MTableState

class MTableStateJinan(MTableState):
    
    def __init__(self):
        super(MTableStateJinan, self).__init__()
        # 卡五星玩法
        self.setState(MTableState.TABLE_STATE_DROP)
        # 吃
        self.setState(MTableState.TABLE_STATE_CHI)
        # 碰
        self.setState(MTableState.TABLE_STATE_PENG)
        # 杠
        self.setState(MTableState.TABLE_STATE_GANG)
        # 听
        #self.setState(MTableState.TABLE_STATE_TING)
        # 抢杠和
        self.setState(MTableState.TABLE_STATE_QIANGGANG)
        # 补花
        self.setState(MTableState.TABLE_STATE_BUFLOWER)
        # 飘
        self.setState(MTableState.TABLE_STATE_PIAO)
        # 和
        self.setState(MTableState.TABLE_STATE_HU)
        # 和牌后游戏结束
        self.setState(MTableState.TABLE_STATE_GAME_OVER)
    
    def getStandUpSchedule(self, state = MTableState.TABLE_STATE_NONE):
        """获取每一小局的发牌流程
        先加漂，再发牌
        """
        if state == MTableState.TABLE_STATE_NONE:

            return MTableState.TABLE_STATE_SAIZI

        elif state == MTableState.TABLE_STATE_SAIZI:

            if self.states & MTableState.TABLE_STATE_PIAO:
                return MTableState.TABLE_STATE_PIAO

            return MTableState.TABLE_STATE_NEXT
        elif state == MTableState.TABLE_STATE_PIAO:

            return MTableState.TABLE_STATE_NEXT

        return MTableState.TABLE_STATE_NEXT