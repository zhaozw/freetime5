#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/4/26

from majiang2.peng_rule.peng_rule import MPengRule
from majiang2.ai.peng import MPeng
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile

class MPengRuleHeXian(MPengRule):
    """和县麻将碰规则
    """

    def __init__(self):
        super(MPengRuleHeXian, self).__init__()

    def hasPeng(self, tiles, tile, extendInfo = {}):
        """是否有碰牌解

        参数说明；
        tiles - 玩家的所有牌，包括手牌，吃牌，碰牌，杠牌，胡牌
        tile - 待碰的牌
        """
        pengSolutions = []
        seatId = extendInfo.get('seatId', -1)
        if seatId == -1:
            return pengSolutions
        
        # 缺门不能碰
        absenceColor = self.tableTileMgr.absenceColors[seatId]
        if MTile.getColor(tile) == absenceColor:
            return pengSolutions

        # 手牌里加上这张牌>=3张，可以碰
        normalPeng = MPeng.hasPeng(tiles[MHand.TYPE_HAND], tile)
        if normalPeng:
            pengSolutions.append([tile, tile, tile])
        return pengSolutions