#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/10

from majiang2.chi_rule.chi_rule import MChiRule
from majiang2.tile import tile_const_huaining as tile_const

class MChiRuleHuaiNing(MChiRule):
    """怀宁麻将碰规则
    """

    def __init__(self):
        super(MChiRuleHuaiNing, self).__init__()

    def hasChi(self, tiles, tile, extendInfo = {}):
        """判断吃牌"""

        # 花牌不能吃
        if tile in tile_const.FLOWERS:
            return []

        return super(MChiRuleHuaiNing, self).hasChi(tiles, tile)
