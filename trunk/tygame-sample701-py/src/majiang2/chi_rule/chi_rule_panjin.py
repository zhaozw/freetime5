# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.ai.chi import MChi
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
from majiang2.chi_rule.chi_rule import MChiRule
import copy

class MChiRulePanJin(MChiRule):
    """胡牌规则
    """
    def __init__(self):
        super(MChiRulePanJin, self).__init__()
        
    def hasChi(self, tiles, tile, extendInfo = {}):
        """是否有吃牌解
        
        参数说明；
        tiles - 玩家的所有牌，包括手牌，吃牌，碰牌，杠牌，胡牌
        tile - 待吃的牌
        """
        if tile >= MTile.TILE_DONG_FENG:
            return []
        
        #是否允许会牌参与,如果不允许，删除会牌
        tilesForChi = copy.deepcopy(tiles[MHand.TYPE_HAND])
        magicTiles = self.tableTileMgr.getMagicTiles()
        for magicTile in magicTiles:
            while magicTile in tilesForChi:
                tilesForChi.remove(magicTile)
        
        chiSolutions = MChi.hasChi(tilesForChi, tile)
        return chiSolutions
    
if __name__ == "__main__":
    pass