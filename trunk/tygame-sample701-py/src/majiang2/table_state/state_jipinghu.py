# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.table_state.state import MTableState
from freetime5.util import ftlog

class MTableStateJiPingHu(MTableState):
    
    def __init__(self):
        super(MTableStateJiPingHu, self).__init__()
        self.setState(MTableState.TABLE_STATE_DROP)
        #
        self.setState(MTableState.TABLE_STATE_CHI)
        # 碰
        self.setState(MTableState.TABLE_STATE_PENG)
        # 杠
        self.setState(MTableState.TABLE_STATE_GANG)
        # 听
        self.setState(MTableState.TABLE_STATE_TING)
        #掷骰子
        self.setState(MTableState.TABLE_STATE_SAIZI)
        # 抢杠胡
        self.setState(MTableState.TABLE_STATE_QIANGGANG)
        # 和
        self.setState(MTableState.TABLE_STATE_HU)

    def getStandUpSchedule(self, state = MTableState.TABLE_STATE_NONE):
        """获取每一小局的发牌流程
        换三张 -> 定缺
        """
        ftlog.debug('MTableStateYantai.getStandUpSchedule state:', state,'states', self.states)
        if state == MTableState.TABLE_STATE_NONE:
            if self.states & MTableState.TABLE_STATE_SAIZI:
                ftlog.debug('MTableStateYantai.getStandUpSchedule return ShaiZi')
                return MTableState.TABLE_STATE_SAIZI

            ftlog.debug('MTableStateYantai.getStandUpSchedule return Next')
            return MTableState.TABLE_STATE_NEXT

        ftlog.debug('MTableStateYantai.getStandUpSchedule return Next')
        return MTableState.TABLE_STATE_NEXT