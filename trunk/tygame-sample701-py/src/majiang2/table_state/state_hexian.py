#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/24

from majiang2.table_state.state import MTableState


class MTableStateHeXian(MTableState):
    """安徽马鞍山市和县麻将的状态
    """

    def __init__(self):
        super(MTableStateHeXian, self).__init__()
        # 出牌
        self.setState(MTableState.TABLE_STATE_DROP)
        # 碰
        self.setState(MTableState.TABLE_STATE_PENG)
        # 杠
        self.setState(MTableState.TABLE_STATE_GANG)
        # 听
        self.setState(MTableState.TABLE_STATE_TING)
        # 抢杠和
        self.setState(MTableState.TABLE_STATE_QIANGGANG)
        # 定缺
        self.setState(MTableState.TABLE_STATE_ABSENCE)
        # 和
        self.setState(MTableState.TABLE_STATE_HU)
        # 和牌后游戏结束
        self.setState(MTableState.TABLE_STATE_GAME_OVER)
