# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.tile.tile import MTile
from majiang2.player.hand.hand import MHand
from freetime5.util import ftlog

class MTileValue(object):
    """计算麻将牌的价值
    """
    
    def __init__(self):
        super(MTileValue, self).__init__()
        
    @classmethod
    def getBestChiPattern(cls, tiles, tiles_left, chiPatterns):
        """选择最佳的吃牌方案
        
        特殊说明：加上吃牌再比较
        """
        bestValue = 0
        chiChoise = []
        for chiSolution in chiPatterns:
            for tile in chiSolution:
                tiles[MHand.TYPE_HAND].remove(tile)
            left_tiles_value_arr, _ = cls.getHandTilesValue(tiles, tiles_left)
            leftValue = 0
            for itemValue in left_tiles_value_arr:
                leftValue += itemValue
            if bestValue < leftValue:
                bestValue = leftValue
                chiChoise = chiSolution
            for tile in chiSolution:
                tiles[MHand.TYPE_HAND].append(tile)
                
        ftlog.debug('best chiChoice:', chiChoise, ' value:', bestValue)
        return chiChoise, bestValue
        
    @classmethod
    def getHandTilesValue(cls, tiles_player_hand, tiles_left):
        """计算手牌价值
        
        返回值：
        1）每张牌的价值
        2）手牌花色个数的数组
        """
        tiles_player_Arr = MTile.changeTilesToValueArr(tiles_player_hand[MHand.TYPE_HAND])
#         tiles_left_Arr = MTile.changeTilesToValueArr(tiles_left)
                
        # 权值初始化    
        tiles_value_Arr = [0 for _ in range(40)]
        for index in range(MTile.TILE_MAX_VALUE):
            if tiles_player_Arr[index] == 0:
                continue
            # 风牌只考虑自己的价值
            tiles_value_Arr[index] = tiles_player_Arr[index] * 4
#              + tiles_left_Arr[index]
            # 万筒条还考虑同周围牌的关系
            if index < 30:
                if index % 10 < 9:
                    tiles_value_Arr[index] += tiles_player_Arr[index + 1] * 3
                if index % 10 < 8:
                    tiles_value_Arr[index] += tiles_player_Arr[index + 2] * 2
                if index % 10 > 1:
                    tiles_value_Arr[index] += tiles_player_Arr[index - 1] * 3
                if index % 10 > 2:
                    tiles_value_Arr[index] += tiles_player_Arr[index - 2] * 2
        
        ftlog.debug('getHandTilesValue valueArr:', tiles_value_Arr, 'playerArr:', tiles_player_Arr)            
        return tiles_value_Arr, tiles_player_Arr
        
    @classmethod
    def getBestDropTile(cls, tiles_player_hand, tiles_left, playMode, tile, isTing, magicTiles, absenceColor, tingRule = None, seatId = 0):
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
        ftlog.debug('MTileValue.getBestDropTile tiles_player_hand:', tiles_player_hand
                    , ' tiles_left:', tiles_left
                    , ' playMode:', playMode
                    , ' tile:', tile
                    , ' isTing:', isTing
                    , ' magicTiles:', magicTiles
                    , ' tingRule:', tingRule
                    , ' seatId:', seatId)
        
        if isTing:
            # 听牌后，直接打出摸到的牌
            return tile, 0
        
        tiles_value_Arr, tiles_player_Arr = cls.getHandTilesValue(tiles_player_hand, tiles_left)
        # 放大癞子牌的作用
        for mTile in magicTiles:
            tiles_value_Arr[mTile] = tiles_value_Arr[mTile] * 100
            
        # 如果有一门花色大于9张牌，放大该门花色牌的价值，便于去做清一色番型
        allTiles = MHand.copyAllTilesToList(tiles_player_hand)
        wans = MTile.filterTiles(allTiles, MTile.TILE_WAN)
        if len(wans) >= 9:
            for tile in MTile.traverseTile(MTile.TILE_WAN):
                tiles_value_Arr[tile] += 10
            
        tongs = MTile.filterTiles(allTiles, MTile.TILE_TONG)
        if len(tongs) >= 9:
            for tile in MTile.traverseTile(MTile.TILE_TONG):
                tiles_value_Arr[tile] += 10
                
        tiaos = MTile.filterTiles(allTiles, MTile.TILE_TIAO)
        if len(tiaos) >= 9:
            for tile in MTile.traverseTile(MTile.TILE_TIAO):
                tiles_value_Arr[tile] += 10
                
        fengs = MTile.filterTiles(allTiles, MTile.TILE_FENG)
        if len(fengs) >= 9:
            for tile in MTile.traverseTile(MTile.TILE_FENG):
                tiles_value_Arr[tile] += 10
                
        # 减小缺牌的作用
        for tile in range(len(tiles_value_Arr)):
            if MTile.getColor(tile) == absenceColor:
                tiles_value_Arr[tile] -= 100
                    
        # [{'dropTile': 11, 'winNodes': [{'winTile': 1, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [1, 2, 3]]}, {'winTile': 2, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [3, 4, 5], [2, 2]]}, {'winTile': 4, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [2, 3, 4]]}, {'winTile': 5, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [5, 5], [2, 3, 4]]}, {'winTile': 7, 'winTileCount': 1, 'pattern': [[6, 6], [5, 6, 7], [5, 6, 7], [2, 3, 4]]}, {'winTile': 8, 'winTileCount': 1, 'pattern': [[6, 7, 8], [6, 6, 6], [5, 5], [2, 3, 4]]}]}]
        if tingRule:
            canTing, tingResults = tingRule.canTing(tiles_player_hand, tiles_left, tile, magicTiles)
            ftlog.debug( canTing )
            ftlog.debug( tingResults )
            
            if canTing:
                for tingResult in tingResults:
                    dropTile = tingResult['dropTile']
                    winNodes = tingResult['winNodes']
                    outs = 0
                    for winNode in winNodes:
                        outs += winNode['winTileCount']
                    tiles_value_Arr[dropTile] = (0 - outs)
         
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
         
        ftlog.debug('MTileValue.getBestDropTile minTile:', minTile
                    , ' tileValue:', tiles_value_Arr[minTile])        
        return minTile, tiles_value_Arr[minTile]
    
    @classmethod
    def getGroupTilesValue(cls, tilesArr):
        """
        计算一手牌的价值
        
        每颗牌记为4分，相邻的牌记为3分，隔牌记为2分
        特殊说明：考虑剩余的牌，通常用于机器人，对机器人有偏向
        返回值：
        1）每张牌的价值
        2）手牌花色个数的数组
        """
        total = 0
        tilesArr.sort()
        lastTile = None
        for tile in tilesArr:
            total += 15
            if lastTile:
                if lastTile == tile:
                    total += 7
                elif tile - lastTile == 1:
                    total += 3
                elif tile - lastTile == 2:
                    total += 1
            lastTile = tile
                    
        return total
    
def testBestDropTile():
    tiles = [[11,11,14,14,15], [], [], [], [], []]
    tileLeft = [19, 15, 21, 14, 18, 9, 26, 22, 13, 23, 16, 5, 12, 35, 5, 5, 27, 24, 25, 29, 9, 12, 8, 9, 24, 7, 28, 24, 13, 7, 14, 25, 11]
    playMode = 'yunnan'
    tile = 21
    print MTileValue.getBestDropTile(tiles, tileLeft, playMode, tile, False, [21], MTile.TILE_WAN)
    
def testGroupValue():
    tBaozi = [11,11,11]
    print 'tBaozi value:', MTileValue.getGroupTilesValue(tBaozi)
    
    tDuiLian = [11,11,12]
    print 'tDuiLian value:', MTileValue.getGroupTilesValue(tDuiLian)
    
    tDuiGe = [11,11,13]
    print 'tDuiGe value:', MTileValue.getGroupTilesValue(tDuiGe)
    
    tDuiDan = [11,11,17]
    print 'tDuiDan value:', MTileValue.getGroupTilesValue(tDuiDan)

    tShun = [11,12,13]
    print 'tShun value:', MTileValue.getGroupTilesValue(tShun)
    
    tShunGe = [11,12,14]
    print 'tShunGe value:', MTileValue.getGroupTilesValue(tShunGe)
    
    tShunDan = [11,12,15]
    print 'tShunDan value:', MTileValue.getGroupTilesValue(tShunDan)
    
    tDan = [11,14,17]
    print 'tDan value:', MTileValue.getGroupTilesValue(tDan)
    
if __name__ == "__main__":
    #testGroupValue()
    testBestDropTile()
    