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



class MWinRulePanjin(MWinRule):
    """
    鸡西玩法的和牌规则
    1）没听牌 不和
    2）和牌不可以过
    3）和牌完全从听中去和牌番型
    """
    def __init__(self):
        super(MWinRulePanjin, self).__init__()
    
    
    def SatisyYaoJiu(self,tiles):
        #有幺九
        allTiles = MHand.copyAllTilesToList(tiles)
        tilesArr = MTile.changeTilesToValueArr(allTiles)
        if self.tableConfig.get(MTDefine.HUI_PAI, 0):
            magics = self.tableTileMgr.getMagicTiles(True)
            tilesArr[magics[0]] = 0

        yaojiucount = MTile.getYaoJiuCount(tilesArr)
        if yaojiucount>0:
            return True
        else:
            for feng in range(MTile.TILE_DONG_FENG,MTile.TILE_BAI_BAN+1):
                if tilesArr[feng]>=1:
                    return True
                    
        return False

    def SatisyKe2(self,tiles):
        #有刻
        if len(tiles[MHand.TYPE_PENG])>0:
            return True
        
        ming,an = MTile.calcGangCount(tiles[MHand.TYPE_GANG])
        if (ming + an) >0:
            return True
        
        return False
    
    def isHu(self, tiles, tile, isTing, getTileType, magicTiles = [], tingNodes = [], winSeatId = 0):
          
        #tile已经加入到tiles
        ftlog.debug('MWinRulePanjin.isHu tiles:', tiles
            , ' magicTiles:', magicTiles
            , ' tile:', tile)

        if self.tableTileMgr.isPassHuTileBySeatId(winSeatId, tile):
            return False, []
        
        #是否允许闭门胡
        if not self.tableConfig.get(MTDefine.BI_MEN_FAN, 0):
            if len(tiles[MHand.TYPE_HAND]) == 14:
                return False, [] 
            
        
        # 三色全
        allTiles = MHand.copyAllTilesToList(tiles)
        #避免摸宝时候检查三色全问题，所以剔除最后一张
        allTiles.remove(tile)
        #会牌剔除
        if self.tableConfig.get(MTDefine.HUI_PAI, 0):
            magics = self.tableTileMgr.getMagicTiles(True)
            while magics[0] in allTiles:
                allTiles.remove(magics[0])
            
        tilesArr = MTile.changeTilesToValueArr(allTiles)
        wanCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_WAN)
        tongCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_TONG)
        tiaoCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_TIAO)
        if wanCount==0 or tongCount==0 or tiaoCount==0:
            return False, []

        #有幺九
        if not self.SatisyYaoJiu(tiles):
            return False,[]
        
        result, pattern = MWin.isHu(tiles[MHand.TYPE_HAND],magicTiles,True)
        ftlog.debug('MWinRulePanjin.isHu tiles:', result, ' pattern:', pattern)
        if not result:
            return False, []
        else:
            keAlreadyhas = self.SatisyKe2(tiles)
            if keAlreadyhas:
                return True, pattern
            else:
                #检查胡牌番型pattern，要有刻
                for p in pattern:
                    if len(p)==3 and (p[0]==p[2] or p[1]==p[2] or p[0]==p[1]):
                        return True,pattern
                    elif len(p)==2:
                        if (p[0] in range(MTile.TILE_DONG_FENG,MTile.TILE_BAI_BAN+1)) \
                            or (p[1] in range(MTile.TILE_DONG_FENG,MTile.TILE_BAI_BAN+1)):
                            return True,pattern
                        if self.tableConfig.get(MTDefine.HUI_PAI, 0):
                            if (p[0]==p[1]==magicTiles[0]):
                                return True,pattern
                    
        return False,[]
    
    def isPassHu(self):
        """是否有过胡规则"""
        return True
        
    def canWinAfterChiPengGang(self, tiles):
        """吃完之后是否能和牌"""
        
        handTiles = tiles[MHand.TYPE_HAND]
        count = len(handTiles) - 2
        #飘可以手把一
        if count == 3:
            if len(tiles[MHand.TYPE_CHI])==0:
                return True
            else:
                return False
        if count < 4:
            return False
        
        return True
    
    
if __name__ == "__main__":
    tiles = [[1,2,3,4,5,6,7,8,9,11,11], [[12,13,14]], [], [], [], []]
    rule = MWinRulePanjin()
    ftlog.debug(rule.isHu(tiles, 2, True, [3]))