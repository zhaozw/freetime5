# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.table_state.state import MTableState
from freetime5.util import ftlog

class MTableStateYantai(MTableState):
    
    def __init__(self):
        super(MTableStateYantai, self).__init__()
        # 卡五星玩法
        self.setState(MTableState.TABLE_STATE_DROP)
        # 吃
#         self.setState(MTableState.TABLE_STATE_CHI)
        # 碰
        self.setState(MTableState.TABLE_STATE_PENG)
        # 杠
        self.setState(MTableState.TABLE_STATE_GANG)
        # 听，在配置中添加删除
#         self.setState(MTableState.TABLE_STATE_TING)
        # 抢杠和
        self.setState(MTableState.TABLE_STATE_QIANGGANG)
        # 飘，在配置中添加删除
        #self.setState(MTableState.TABLE_STATE_PIAO)
        # 加倍，在配置中添加删除
        #self.setState(MTableState.TABLE_STATE_DOUBLE)
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
            ftlog.debug('MTableStateYantai.getStandUpSchedule state:', state)
            if self.states & MTableState.TABLE_STATE_PIAO:
                ftlog.debug('MTableStateYantai.getStandUpSchedule return state:', MTableState.TABLE_STATE_PIAO)
                return MTableState.TABLE_STATE_PIAO
            
            if self.states & MTableState.TABLE_STATE_DOUBLE:
                ftlog.debug('MTableStateYantai.getStandUpSchedule return state:', MTableState.TABLE_STATE_DOUBLE)
                return MTableState.TABLE_STATE_DOUBLE
            
            ftlog.debug('MTableStateYantai.getStandUpSchedule return 1 state:', MTableState.TABLE_STATE_NEXT)
            return MTableState.TABLE_STATE_NEXT
        elif state == MTableState.TABLE_STATE_PIAO:
            if self.states & MTableState.TABLE_STATE_DOUBLE:
                ftlog.debug('MTableStateYantai.getStandUpSchedule return state:', MTableState.TABLE_STATE_DOUBLE)
                return MTableState.TABLE_STATE_DOUBLE
            ftlog.debug('MTableStateYantai.getStandUpSchedule return 2 state:', MTableState.TABLE_STATE_NEXT)
            return MTableState.TABLE_STATE_NEXT
        elif state == MTableState.TABLE_STATE_DOUBLE:
            ftlog.debug('MTableStateYantai.getStandUpSchedule return state:', MTableState.TABLE_STATE_NEXT)
            return MTableState.TABLE_STATE_NEXT
        
        ftlog.debug('MTableStateYantai.getStandUpSchedule return 3 state:', MTableState.TABLE_STATE_NEXT)
        return MTableState.TABLE_STATE_NEXT