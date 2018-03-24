#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/7

from majiang2.table_tile.table_tile import MTableTile
from majiang2.tile import tile_const_huaining as tile_const

class MTableTileHuaiNing(MTableTile):
    """怀宁麻将牌管理器
    """

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileHuaiNing, self).__init__(playerCount, playMode, runMode)
        self.setQiangGangRule(0b010)  # 回头杠才能抢杠胡

    def canDuoHu(self):
        return True

    def canGangAfterPeng(self):
        """一般麻将默认不允许碰后马上杠牌"""
        return True

    def isFlower(self, tile):
        """判断tile是否花牌"""
        return tile in tile_const.FLOWERS

    def canGangThisTile(self, tile):
        """能否杠这张牌"""
        return not self.isFlower(tile)
