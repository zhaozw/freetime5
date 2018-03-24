# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.player.hand.hand import MHand
from majiang2.ai.peng import MPeng
import copy
from majiang2.peng_rule.peng_rule import MPengRule
from majiang2.tile.tile import MTile

class MPengRuleSiChuan(MPengRule):
    """碰牌判断"""
    
    def __init__(self):
        super(MPengRuleSiChuan, self).__init__()
        
    def hasPeng(self, tiles, tile, extendInfo = {}):
        """是否有碰牌解
        
        参数说明；
        tiles - 玩家的所有牌，包括手牌，吃牌，碰牌，杠牌，胡牌
        tile - 待碰的牌
        """
        absenceColor = extendInfo.get('absenceColor', -1)
        if MTile.getColor(tile) == absenceColor:
            return []
        
        tilesForPeng = copy.deepcopy(tiles[MHand.TYPE_HAND])
        tilesForPeng = MTile.filterTilesWithOutColor(tilesForPeng, absenceColor)  
            
        pengSolutions = []
        if MPeng.hasPeng(tilesForPeng, tile):
            pengSolutions.append([tile, tile, tile])
        
        return pengSolutions    
        
if __name__ == "__main__":
    pass
