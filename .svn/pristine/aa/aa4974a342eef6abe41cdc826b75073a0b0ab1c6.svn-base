#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/4/26

from majiang2.gang_rule.gang_rule import MGangRule
from majiang2.tile.tile import MTile

class MGangRuleHeXian(MGangRule):
    """和县麻将碰规则
    """

    def __init__(self):
        super(MGangRuleHeXian, self).__init__()

    def hasGang(self, tiles, curTile, state, extendInfo={}):
        """判断杠牌"""

        # 缺门的牌不能杠
        absenceColor = extendInfo.get('absenceColor', -1)
        if MTile.getColor(curTile) == absenceColor:
            return []

        return super(MGangRuleHeXian, self).hasGang(tiles, curTile, state, extendInfo)

