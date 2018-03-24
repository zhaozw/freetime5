#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/4/26

from majiang2.gang_rule.gang_rule import MGangRule
from majiang2.tile.tile import MTile
from majiang2.player.hand.hand import MHand
from freetime5.util import ftlog
import copy

class MGangRuleSiChuan(MGangRule):
    """血战麻将碰规则
    """

    def __init__(self):
        super(MGangRuleSiChuan, self).__init__()

    def hasGang(self, tiles, curTile, state, extendInfo={}):
        """判断杠牌"""

        # 血战麻将必有定缺，如果定缺为-1，表明为初始化，则不判断是否有杠
        absenceColor = extendInfo.get('absenceColor', -1)
        seatId = extendInfo.get('seatId', -1)
        
        if absenceColor == -1:
            ftlog.debug('MGangRuleSiChuan.hasGang: absenceColor:', absenceColor, 'tiles:', tiles, 'curTile:', curTile, 'seatId:', seatId)
            return []
        
        tilesForGang = copy.deepcopy(tiles)
        tilesForGang[MHand.TYPE_HAND] = MTile.filterTilesWithOutColor(tilesForGang[MHand.TYPE_HAND], absenceColor)  
        ftlog.debug('MGangRuleSiChuan.hasGang tileForGang:', tilesForGang)

        return super(MGangRuleSiChuan, self).hasGang(tilesForGang, curTile, state, extendInfo)

