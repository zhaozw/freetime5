#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/9

from majiang2.gang_rule.gang_rule import MGangRule
from majiang2.player.hand.hand import MHand
from freetime5.util import ftlog
from majiang2.player.player import MPlayerTileGang

class MGangRuleMudanjiang(MGangRule):
    """怀宁麻将碰规则
    """

    def __init__(self):
        super(MGangRuleMudanjiang, self).__init__()

    def hasGang(self, tiles, curTile, state, extendInfo={}):
        """判断杠牌"""
        ftlog.debug('MGangRuleMudanjiang.hasGang tiles:', tiles
                    , ' curTile:', curTile
                    , ' state:', state)
        gangs = super(MGangRuleMudanjiang, self).hasGang(tiles, curTile, state, extendInfo)
        ftlog.debug('MGangRuleMudanjiang.hasGang tiles:', tiles
                    , ' curTile:', curTile
                    , ' state:', state
                    , ' gangs:', gangs)
        
        newGangs = []
        for gang in gangs:
            if gang['style'] == MPlayerTileGang.AN_GANG:
                if (len(tiles[MHand.TYPE_HAND]) - 4) <= 2:
                    continue
            newGangs.append(gang)
            
        ftlog.debug('MGangRuleMudanjiang.hasGang afterAdjust tiles:', tiles
                    , ' curTile:', curTile
                    , ' state:', state
                    , ' newGangs:', newGangs)
        
        return newGangs
