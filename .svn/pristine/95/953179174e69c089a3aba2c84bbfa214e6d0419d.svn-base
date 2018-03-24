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
import copy
from majiang2.table.table_config_define import MTDefine

class MWinRuleBaicheng(MWinRule):
    """
    鸡西玩法的和牌规则
    1）没听牌 不和
    2）和牌不可以过
    3）和牌完全从听中去和牌番型
    """
    def __init__(self):
        super(MWinRuleBaicheng, self).__init__()
    
    
    def hasKe(self,handtiles):    
        tilesArr = MTile.changeTilesToValueArr(handtiles)
        for tile in handtiles:
            if tilesArr[tile]>=3:
                return True
        return False
    
    def SatisyYaoJiu(self,tiles):
        #有幺九
        if len(tiles[MHand.TYPE_MAO])==0:
            allTiles = MHand.copyAllTilesToList(tiles)
            tilesArr = MTile.changeTilesToValueArr(allTiles)
            #中发白做将
            if tilesArr[MTile.TILE_HONG_ZHONG] < 2 and tilesArr[MTile.TILE_FA_CAI] < 2 and tilesArr[MTile.TILE_BAI_BAN] < 2:
                #中发白
                if not (tilesArr[MTile.TILE_HONG_ZHONG]>0 and tilesArr[MTile.TILE_FA_CAI]>0 and tilesArr[MTile.TILE_BAI_BAN]>0):
                    yaojiucount = MTile.getYaoJiuCount(tilesArr)
                    if yaojiucount==0:
                        return False

        return True

    def SatisyKe(self,tiles):
        #有刻
        if len(tiles[MHand.TYPE_MAO])==0:
            if len(tiles[MHand.TYPE_PENG])==0:
                ming,an = MTile.calcGangCount(tiles[MHand.TYPE_GANG])
                if (ming + an) ==0:
                    allTiles = MHand.copyAllTilesToList(tiles)
                    tilesArr = MTile.changeTilesToValueArr(allTiles)
                    #中发白做将
                    if tilesArr[MTile.TILE_HONG_ZHONG] < 2 and tilesArr[MTile.TILE_FA_CAI] < 2 and tilesArr[MTile.TILE_BAI_BAN] < 2:
                        #中发白
                        if not (tilesArr[MTile.TILE_HONG_ZHONG]>0 and tilesArr[MTile.TILE_FA_CAI]>0 and tilesArr[MTile.TILE_BAI_BAN]>0):
                            if not self.hasKe(tiles[MHand.TYPE_HAND]):
                                return False

        return True
    
    def SatisyKe2(self,tiles):
        #有刻
        if len(tiles[MHand.TYPE_MAO])>0 or len(tiles[MHand.TYPE_PENG])>0:
            return True
        
        ming,an = MTile.calcGangCount(tiles[MHand.TYPE_GANG])
        if (ming + an) >0:
            return True
        
        allTiles = MHand.copyAllTilesToList(tiles)
        tilesArr = MTile.changeTilesToValueArr(allTiles)
        #中发白做将
        if tilesArr[MTile.TILE_HONG_ZHONG] >= 2 or tilesArr[MTile.TILE_FA_CAI] >= 2 or tilesArr[MTile.TILE_BAI_BAN] >= 2:
            return True
        
        #中发白
        if (tilesArr[MTile.TILE_HONG_ZHONG]>0 and tilesArr[MTile.TILE_FA_CAI]>0 and tilesArr[MTile.TILE_BAI_BAN]>0):
            return True

        return False


    def isHu(self, tiles, tile, isTing, getTileType, magicTiles = [], tingNodes = [], winSeatId = 0):
          
        '''
        三色全，玩家手中必须同时具有万饼条三种花色的牌
        有幺九（喜杠、幺九杠、中发白作将或刻时可免幺九）
        有刻（任意杠、中发白作将或刻时可免刻）
        '''
        
        ftlog.debug('MWinRuleBaicheng.isHu TIAN_HU:', self.tableConfig.get(MTDefine.TIAN_HU, 0), ' len(self.tableTileMgr.addTiles[winSeatId]):', len(self.tableTileMgr.addTiles[winSeatId]), ' winSeatId:', winSeatId)
        if getTileType == MWinRule.WIN_BY_MYSELF:
            if 0==self.tableConfig.get(MTDefine.TIAN_HU, 0):
                if len(self.tableTileMgr.addTiles[winSeatId]) == 1:
                    return False, []

        #tile已经加入到tiles
        ftlog.debug('MWinRuleBaicheng.isHu tiles:', tiles
            , ' magicTiles:', magicTiles
            , ' tile:', tile)

        # 三色全
        allTiles = MHand.copyAllTilesToList(tiles)
        #避免摸宝时候检查三色全问题，所以剔除最后一张
        allTiles.remove(tile)
        tilesArr = MTile.changeTilesToValueArr(allTiles)
        wanCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_WAN)
        tongCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_TONG)
        tiaoCount = MTile.getTileCountByColor(tilesArr, MTile.TILE_TIAO)
        if wanCount==0 or tongCount==0 or tiaoCount==0:
            return False, []


        #摸到宝牌
        if getTileType == MWinRule.WIN_BY_MYSELF:
            if (tile in magicTiles):
                canHuWithMagic = False
                for tileTry in range(MTile.TILE_MAX_VALUE):
                    handTile = copy.deepcopy(tiles[MHand.TYPE_HAND])
                    handTile.remove(tile)
                    handTile.append(tileTry)
                    ishu, pattern = MWin.isHu(handTile,[],True)
                    ftlog.debug('MWinRuleBaicheng.isHu handTile:', handTile,'tile',tile,'ishu',ishu,'pattern',pattern)
                    if ishu:
                        #摸宝的情况下，判断胡牌pattern里面是否有幺九，是否有刻
                        #把pattern胡牌加入到手牌，然后判断
                        allTilesMagicHu = copy.deepcopy(tiles)
                        allTilesMagicHu[MHand.TYPE_HAND] = []
                        for p in pattern:
                            allTilesMagicHu[MHand.TYPE_HAND].extend(p)

                        ftlog.debug('MWinRuleBaicheng.isHu allTilesMagicHu:', allTilesMagicHu)
                        #有幺九
                        if not self.SatisyYaoJiu(allTilesMagicHu):
                            continue
                        #有刻
                        if not self.SatisyKe(allTilesMagicHu):
                            continue
                        #可以胡，说明是摸宝胡牌
                        ftlog.debug('MWinRuleBaicheng.isHu canHuWithMagic:yes')
                        canHuWithMagic = True
                        return True,[]

                if not canHuWithMagic:
                    return False, []

        #有幺九
        if not self.SatisyYaoJiu(tiles):
            return False,[]
        
        result, pattern = MWin.isHu(tiles[MHand.TYPE_HAND],[],True)
        if not result:
            return False, []
        else:
            keAlreadyhas = self.SatisyKe2(tiles)
            if keAlreadyhas:
                return True, pattern
            else:
                #检查胡牌番型pattern，要有刻
                for p in pattern:
                    if len(p)==3 and p[0]==p[1]==p[2]:
                        return True,pattern
            
        return False,[]
        
        
    def canWinAfterChiPengGang(self, tiles):
        """
        吃完之后是否能和牌
        
        baicheng麻将无此限制
        """
        return True
    
if __name__ == "__main__":
    tiles = [[1,2,3,4,5,6,7,8,9,11,11], [[12,13,14]], [], [], [], []]
    rule = MWinRuleBaicheng()
    ftlog.debug(rule.isHu(tiles, 2, True, [3]))