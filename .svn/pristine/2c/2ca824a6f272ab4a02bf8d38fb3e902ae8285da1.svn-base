# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
import copy
from majiang2.chi_rule.chi_rule import MChiRule

class MChiRuleXuezhan(MChiRule):
    """胡牌规则
    """
    def __init__(self):
        super(MChiRuleXuezhan, self).__init__()
        
    def hasChi(self, tiles, tile, extendInfo = {}):
        """是否有吃牌解
        
        参数说明；
        tiles - 玩家的所有牌，包括手牌，吃牌，碰牌，杠牌，胡牌
        tile - 待吃的牌
        """
        newTiles = copy.deepcopy(tiles)
        absenseColor = extendInfo.get('absenseColor', -1)
        if MTile.getColor(tile) == absenseColor:
            return []
        
        newTiles[MHand.TYPE_HAND] = filter(lambda x:MTile.getColor(x) != absenseColor, newTiles[MHand.TYPE_HAND])
        return super(MChiRuleXuezhan, self).hasChi(newTiles, tile)
    
if __name__ == "__main__":
    pass