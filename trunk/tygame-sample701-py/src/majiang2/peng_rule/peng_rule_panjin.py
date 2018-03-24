# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.player.hand.hand import MHand
from majiang2.ai.peng import MPeng
from majiang2.peng_rule.peng_rule import MPengRule
import copy

class MPengRulePanJin(MPengRule):
    """碰牌判断"""
    
    def __init__(self):
        super(MPengRulePanJin, self).__init__()
        
    def hasPeng(self, tiles, tile, extendInfo = {}):
        """是否有碰牌解
        
        参数说明；
        tiles - 玩家的所有牌，包括手牌，吃牌，碰牌，杠牌，胡牌
        tile - 待碰的牌
        """
        
        tilesForPeng = copy.deepcopy(tiles[MHand.TYPE_HAND])
        magicTiles = self.tableTileMgr.getMagicTiles()
        for magicTile in magicTiles:
            while magicTile in tilesForPeng:
                tilesForPeng.remove(magicTile)
                
        pengSolutions = []
        normalPeng = MPeng.hasPeng(tilesForPeng, tile)
        if normalPeng:
            pengSolutions.append([tile, tile, tile])
        
        return pengSolutions    
        
if __name__ == "__main__":
    pass
