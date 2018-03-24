#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/7

from majiang2.table_state.state import MTableState


class MTableStateHuaiNing(MTableState):
    """安徽怀宁麻将的状态
    """

    def __init__(self):
        super(MTableStateHuaiNing, self).__init__()
        # 出牌
        self.setState(MTableState.TABLE_STATE_DROP)
        # 吃
        self.setState(MTableState.TABLE_STATE_CHI)
        # 碰
        self.setState(MTableState.TABLE_STATE_PENG)
        # 杠
        self.setState(MTableState.TABLE_STATE_GANG)
        # 抢杠和
        self.setState(MTableState.TABLE_STATE_QIANGGANG)
        # 和
        self.setState(MTableState.TABLE_STATE_HU)
        # 和牌后游戏结束
        self.setState(MTableState.TABLE_STATE_GAME_OVER)
