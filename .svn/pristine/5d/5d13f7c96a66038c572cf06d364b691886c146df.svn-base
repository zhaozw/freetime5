#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/24

"""和县麻将牌管理器
"""

from majiang2.table_tile.table_tile import MTableTile


class MTableTileHeXian(MTableTile):
    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileHeXian, self).__init__(playerCount, playMode, runMode)
        self.setQiangGangRule(0b010)  # 回头杠才能抢杠胡

    def canDuoHu(self):
        """不能一炮多胡"""
        return False

    def canGangAfterPeng(self):
        """一般麻将默认不允许碰后马上杠牌"""
        return True

    def selectGangAfterTing(self):
        """听牌之后杠是否需要选择"""
        return True

    def getTingGangMode(self):
        """听暗杠"""
        return MTableTile.AFTER_TING_HU_NO_CHANGE_TING | MTableTile.AFTER_TING_HU_WITHOUT_MINGGANG
