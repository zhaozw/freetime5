#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/9

from majiang2.gang_rule.gang_rule import MGangRule
from majiang2.tile import tile_const_huaining as tile_const

class MGangRuleHuaiNing(MGangRule):
    """怀宁麻将碰规则
    """

    def __init__(self):
        super(MGangRuleHuaiNing, self).__init__()

    def hasGang(self, tiles, curTile, state, extendInfo= {}):
        """判断杠牌"""
        return super(MGangRuleHuaiNing, self).hasGang(tiles, curTile, state, extendInfo)


    def canGangThisTile(self, tile):
        """能否杠这张牌
           花牌不能杠
        """
        return tile not in tile_const.FLOWERS
