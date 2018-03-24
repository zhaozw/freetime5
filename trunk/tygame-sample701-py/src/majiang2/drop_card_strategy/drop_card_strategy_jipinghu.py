# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.drop_card_strategy.drop_card_strategy import MDropCardStrategy
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
from freetime5.util import ftlog
from majiang2.ai.tile_value import MTileValue

class MDropCardStrategyJipinghu(MDropCardStrategy):
    """胡牌规则
    """
    def __init__(self):
        super(MDropCardStrategyJipinghu, self).__init__()

    def isWin(self, allTiles, winTile, winStyle, leftTiles):
        '''
            默认能胡就胡
            allTiles - 当前玩家的所有手牌
            winTile - 胡牌
            winStyle - 是吃炮胡，抢杠胡，还是自摸胡。
                被人点炮则胡
                自摸胡时，考虑下是否更换听口，以博取更好的机会
        '''
        doQing, qingColor = self.doQingYiSe(allTiles, leftTiles)
        if doQing:
            return (MTile.getColor(winTile) == qingColor)
        return True
    
    def doQingYiSe(self, allTiles, leftTiles):
        '''
            是否做清一色
        '''
        length = 9
        if len(leftTiles) >= 50:
            length= 8
        elif len(leftTiles) >= 40:
            length = 9
        elif len(leftTiles) >= 30:
            length = 10
        elif len(leftTiles) >= 20:
            length = 11
            
        allTilesArr = MHand.copyAllTilesToList(allTiles)
        cpgTiles = MHand.copyTiles(allTiles, [MHand.TYPE_CHI, MHand.TYPE_PENG, MHand.TYPE_GANG])
        wans = MTile.filterTiles(allTilesArr, MTile.TILE_WAN)
        if len(wans) >= length:
            for tile in cpgTiles:
                if MTile.getColor(tile) != MTile.TILE_WAN:
                    return False, MTile.TILE_FENG
            return True, MTile.TILE_WAN
            
        tongs = MTile.filterTiles(allTilesArr, MTile.TILE_TONG)
        if len(tongs) >= length:
            for tile in cpgTiles:
                if MTile.getColor(tile) != MTile.TILE_TONG:
                    return False, MTile.TILE_FENG
            return True, MTile.TILE_TONG
                
        tiaos = MTile.filterTiles(allTilesArr, MTile.TILE_TIAO)
        if len(tiaos) >= length:
            for tile in cpgTiles:
                if MTile.getColor(tile) != MTile.TILE_TIAO:
                    return False, MTile.TILE_FENG
            return True, MTile.TILE_TIAO
        
        return False, MTile.TILE_FENG
    
    def getBestDropTile(self, tiles_player_hand, tiles_left, tile, isTing, magicTiles, absenceColor, tingRule = None):
        """
        手牌的价值，根据玩家自己的手牌和已经出的牌，计算手牌价值
        参数：
            tiles_player_hand - 用户的手牌
            tiles_droped - 牌桌上已经打出的牌和玩家手里已经成型的牌，这部分牌不再参与计算牌的可能性
        计算方法：
        1）没有的手牌，权值为0
        2）有的手牌，初始权值为4 * count + 1 * left
        3）左右相邻的手牌，增加权重 3 * count
        4）左右隔一张的手牌，增加权重 2 * count
        """
        ftlog.debug('MDropCardStrategyJipinghu.getBestDropTile tiles_player_hand:', tiles_player_hand
                    , ' tiles_left:', tiles_left
                    , ' tile:', tile
                    , ' isTing:', isTing
                    , ' magicTiles:', magicTiles
                    , ' absenceColor:', absenceColor
                    , ' tingRule:', tingRule
                    )
        
        if isTing:
            # 听牌后，直接打出摸到的牌
            return tile, 0
        
        doQing, qingColor = self.doQingYiSe(tiles_player_hand, tiles_left)
        tiles_value_Arr, tiles_player_Arr = MTileValue.getHandTilesValue(tiles_player_hand, tiles_left)
        # 放大癞子牌的作用
        for mTile in magicTiles:
            tiles_value_Arr[mTile] = tiles_value_Arr[mTile] * 100
            
        # 如果有一门花色大于9张牌，放大该门花色牌的价值，便于去做清一色番型
        if doQing:
            for tile in MTile.traverseTile(qingColor):
                tiles_value_Arr[tile] += 10
            
        # 减小缺牌的作用
        for tile in range(len(tiles_value_Arr)):
            if MTile.getColor(tile) == absenceColor:
                tiles_value_Arr[tile] -= 100
                continue
            
            if doQing and MTile.getColor(tile) != qingColor:
                tiles_value_Arr[tile] -= 10
                continue
                    
        # [{'dropTile': 11, 'winNodes': [{'winTile': 1, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [1, 2, 3]]}, {'winTile': 2, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [3, 4, 5], [2, 2]]}, {'winTile': 4, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [2, 3, 4]]}, {'winTile': 5, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [5, 5], [2, 3, 4]]}, {'winTile': 7, 'winTileCount': 1, 'pattern': [[6, 6], [5, 6, 7], [5, 6, 7], [2, 3, 4]]}, {'winTile': 8, 'winTileCount': 1, 'pattern': [[6, 7, 8], [6, 6, 6], [5, 5], [2, 3, 4]]}]}]
        if tingRule:
            canTing, tingResults = tingRule.canTing(tiles_player_hand, tiles_left, tile, magicTiles)
            ftlog.debug( canTing )
            ftlog.debug( tingResults )
            
            if canTing:
                totalValue = 0
                for tingResult in tingResults:
                    dropTile = tingResult['dropTile']
                    winNodes = tingResult['winNodes']
                    for winNode in winNodes:
                        totalValue += winNode['winTileCount'] * winNode['winFan']
                        
                for tingResult in tingResults:
                    dropTile = tingResult['dropTile']
                    winNodes = tingResult['winNodes']
                    dropValue = 0
                    for winNode in winNodes:
                        dropValue += winNode['winTileCount'] * winNode['winFan']        
                    tiles_value_Arr[dropTile] = (totalValue - dropValue)
                    
                    if doQing and (MTile.getColor(dropTile) == qingColor) and (tiles_value_Arr[dropTile] != -4):
                        # 优先打出非清一色颜色的上听牌
                        tiles_value_Arr[dropTile] += (totalValue / len(tingResults))
                        
                ftlog.debug('MDropCardStrategyJipinghu.getBestDropTile adjust tileValue by ting:', tiles_value_Arr
                        , ' tingResults:', tingResults
                        , ' totalValue:', totalValue)
         
        minTile = 0
        minValue = 0  
        for index in range(MTile.TILE_MAX_VALUE):
            if tiles_player_Arr[index] > 0:
                if minTile == 0:
                    minTile = index
                    minValue = tiles_value_Arr[index]
                    continue
                
                if minValue > tiles_value_Arr[index]:
                    minValue = tiles_value_Arr[index]
                    minTile = index
         
        ftlog.debug('MDropCardStrategyJipinghu.getBestDropTile minTile:', minTile
                    , ' tileValue:', tiles_value_Arr[minTile])        
        return minTile, tiles_value_Arr[minTile]
            
if __name__ == "__main__":
    allTiles = [[12, 12, 12, 13, 14, 15, 16, 17, 18, 19], [], [[11, 11, 11]], [], [], [], [22], []]
    gangTile = 12
    gangSolution = {'pattern': [12, 12, 12, 12], 'style': 1, 'tile': 12}
    tingResults = [[11, 8, 0], [13, 4, 3], [14, 4, 2], [16, 4, 2], [17, 4, 3], [19, 4, 0]]
    
    ai = MDropCardStrategyJipinghu()
    isGang = ai.isGang(allTiles, gangTile, gangSolution, tingResults, [])
    print isGang