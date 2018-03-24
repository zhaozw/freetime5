#! -*- coding:utf-8 -*-
# Author:   luoxf
# Created:  2017/3/9

from majiang2.peng_rule.peng_rule import MPengRule
from majiang2.ai.peng import MPeng
from majiang2.player.hand.hand import MHand

class MPengRuleHanShan(MPengRule):
    """含山麻将碰规则 配子不能碰
    """

    def __init__(self):
        super(MPengRuleHanShan, self).__init__()

    def hasPeng(self, tiles, tile, extendInfo = {}):
        """是否有碰牌解

        参数说明；
        tiles - 玩家的所有牌，包括手牌，吃牌，碰牌，杠牌，胡牌
        tile - 待碰的牌
        """
        pengSolutions = []
        magics = self.tableTileMgr.getMagicTiles()
        if tile in magics:
            return pengSolutions

        # 手牌里加上这张牌>=3张，可以碰
        normalPeng = MPeng.hasPeng(tiles[MHand.TYPE_HAND], tile)
        if normalPeng:
            pengSolutions.append([tile, tile, tile])
        return pengSolutions
