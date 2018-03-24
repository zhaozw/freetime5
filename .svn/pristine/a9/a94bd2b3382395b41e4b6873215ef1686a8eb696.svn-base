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
from majiang2.table.table_config_define import MTDefine

class MWinRuleDandong(MWinRule):
    """
    鸡西玩法的和牌规则
    1）没听牌 不和
    2）和牌不可以过
    3）和牌完全从听中去和牌番型
    """
    def __init__(self):
        super(MWinRuleDandong, self).__init__()
        self.TAG = 'MWinRuleDandong'
    
    def hasKe(self,handtiles):    
        tilesArr = MTile.changeTilesToValueArr(handtiles)
        for tile in handtiles:
            if tilesArr[tile]>=3:
                return True
        return False
    
    def SatisyYaoJiu(self,tiles):
        #有幺九
        allTiles = MHand.copyAllTilesToList(tiles)
        tilesArr = MTile.changeTilesToValueArr(allTiles)
        
        yaojiucount = MTile.getYaoJiuCount(tilesArr)
        if yaojiucount>0:
            return True
        else:
            for feng in range(MTile.TILE_DONG_FENG,MTile.TILE_BAI_BAN+1):
                if tilesArr[feng]>=1:
                    return True
                    
        return False

    def SatisyKe(self,tiles):
        #有刻
        if len(tiles[MHand.TYPE_PENG])==0:
            ming,an = MTile.calcGangCount(tiles[MHand.TYPE_GANG])
            if (ming + an) ==0:
                allTiles = MHand.copyAllTilesToList(tiles)
                tilesArr = MTile.changeTilesToValueArr(allTiles)
                #中发白做将
                if tilesArr[MTile.TILE_HONG_ZHONG] < 2 and tilesArr[MTile.TILE_FA_CAI] < 2 and tilesArr[MTile.TILE_BAI_BAN] < 2:
                    #中发白
                    if not self.hasKe(tiles[MHand.TYPE_HAND]):
                        return False

        return True
    
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

                # 三色全
        allTiles = MHand.copyAllTilesToList(tiles)
        tilesArr = MTile.changeTilesToValueArr(allTiles)
        wanCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_WAN)
        tongCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_TONG)
        tiaoCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_TIAO)
        if wanCount==0 or tongCount==0 or tiaoCount==0:
            return False, []

        #有幺九
        if not self.SatisyYaoJiu(tiles):
            return False,[]
        
        if not self.SatisyKe(tiles):
            return False,[]
        
        result, pattern = MWin.isHu(tiles[MHand.TYPE_HAND])
        ftlog.debug('MWinRulePanjin.isHu tiles:', result, ' pattern:', pattern)

        return result, pattern
        
    
    def canDirectHuAfterTing(self):
        if self.tableConfig.get(MTDefine.QIONG_HU, 0):
            return True
        else:
            return False
    
    def canWinAfterChiPengGang(self, tiles):
        """
        吃完之后是否能和牌
        
        平度麻将无此限制
        """
        return True
    
if __name__ == "__main__":
    tiles = [[1,2,3,4,5,6,7,8,9,11,11], [[12,13,14]], [], [], [], []]
    rule = MWinRuleDandong()
    ftlog.debug(rule.isHu(tiles, 2, True, [3]))