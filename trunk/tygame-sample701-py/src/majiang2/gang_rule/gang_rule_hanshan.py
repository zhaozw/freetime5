#! -*- coding:utf-8 -*-
# Author:   luoxf
# Created:  2017/3/9

from majiang2.gang_rule.gang_rule import MGangRule

class MGangRuleHanShan(MGangRule):
    """含山麻将杠规则 配子不能碰
    """

    def __init__(self):
        super(MGangRuleHanShan, self).__init__()

    def hasGang(self, tiles, curTile, state, extendInfo={}):
        """判断杠牌"""
        magics = self.tableTileMgr.getMagicTiles()
        if curTile in magics:
            return []
        gangs = super(MGangRuleHanShan, self).hasGang(tiles, curTile, state, extendInfo)
        tempGangs = []
        for gang in gangs:
            if gang["tile"] not in magics:
                tempGangs.append(gang)
        return tempGangs

