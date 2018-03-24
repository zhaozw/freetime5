# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from majiang2.win_rule.win_rule import MWinRule
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from freetime5.util import ftlog
from majiang2.tile.tile import MTile

class MWinRulePingDu(MWinRule):
    """
    鸡西玩法的和牌规则
    1）没听牌 不和
    2）和牌不可以过
    3）和牌完全从听中去和牌番型
    """
    def __init__(self):
        super(MWinRulePingDu, self).__init__()
        self.TAG = 'MWinRulePingDu'
    
    def isHu(self, tiles, tile, isTing, getTileType, magicTiles = [], tingNodes = [], winSeatId = 0):
        ftlog.debug(self.TAG, '.isHu tiles:', tiles
                    , ' tile:', tile
                    , ' isTing:', isTing
                    , ' getTileType:', getTileType
                    , ' magicTiles:', magicTiles
                    , ' tingNodes:', tingNodes
                    , ' winSeatId:', winSeatId
                    )
        # 平度麻将即可以听也可以不听，听牌后，校验tingNodes即可，无其他限制条件
        if isTing:
            #[{'winTile': 16, 'winTileCount': 0, 'pattern': [[16, 17, 18], [12, 12]]}, {'winTile': 19, 'winTileCount': 0, 'pattern': [[17, 18, 19], [12, 12]]}] 
            for tingNode in tingNodes:
                if tingNode['winTile'] == tile:
                    pattern = tingNode['pattern']
                    return True, pattern

        # 检查8张的规则
        allTiles = MHand.copyAllTilesToListButHu(tiles)
        tilesArr = MTile.changeTilesToValueArr(allTiles)
        wanCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_WAN)
        tiaoCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_TIAO)
        tongCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_TONG)
        fengCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_FENG)
        ftlog.debug('win_rule_pingdu.isHu allTiles:', allTiles
                    , ' tilesLength:', len(allTiles)
                    , ' tilesArr:', tilesArr
                    , ' wanCount:', wanCount
                    , ' tiaoCount:', tiaoCount
                    , ' tongCount:', tongCount
                    , ' fengCount:', fengCount)
        
        if (wanCount >= 8) or (tiaoCount >= 8) or (tongCount >= 8) or (fengCount >= 8):
            pass
        else:
#             ftlog.info('win_rule_pingdu.isHu ok but do not have >=8 tiles in one color, allTiles:', allTiles
#                     , ' tilesLength:', len(allTiles)
#                     , ' tilesArr:', tilesArr
#                     , ' wanCount:', wanCount
#                     , ' tiaoCount:', tiaoCount
#                     , ' tongCount:', tongCount
#                     , ' fengCount:', fengCount)
            return False, []
        
        # 平度麻将允许胡七对
        resultQiDui, patternQiDui = MWin.isQiDui(tiles[MHand.TYPE_HAND])
        if resultQiDui:
            return True, patternQiDui
        
        result, pattern = MWin.isHu(tiles[MHand.TYPE_HAND])
        return result, pattern
        
    
    def canWinAfterChiPengGang(self, tiles):
        """
        吃完之后是否能和牌
        
        平度麻将无此限制
        """
        return True
    
if __name__ == "__main__":
    tiles = [[1,2,3,4,5,6,7,8,9,11,11], [[12,13,14]], [], [], [], []]
    rule = MWinRulePingDu()
    ftlog.debug(rule.isHu(tiles, 2, True, [3]))