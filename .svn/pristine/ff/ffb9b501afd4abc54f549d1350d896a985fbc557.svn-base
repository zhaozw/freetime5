# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.ai.tile_value import MTileValue
from majiang2.drop_card_strategy.drop_card_strategy import MDropCardStrategy
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
import copy
from freetime5.util import ftlog


class MDropCardStrategyXuezhanHigh(MDropCardStrategy):
    """胡牌规则
    """
    def __init__(self):
        super(MDropCardStrategyXuezhanHigh, self).__init__()
     
    def isChi(self, allTiles, chiTile, chiPatterns, leftTiles, tingResults, seatResponse, extend={}):
        '''
            默认能吃就吃
            allTiles - 当前玩家的所有手牌
            chiTile - 吃牌
            chiPatterns - 吃牌方案
            seatResponse - 玩家是否做出选择
            
            extend - 扩展信息，本接口不要再添加更多参数，更多参数通过extend传递
        '''
        if seatResponse:
            return True
        
        seatId = extend.get('seatId', None)
        abColors = extend.get('absenceColor', None)
        doQing, qingColor = self.doQingYiSe(allTiles, leftTiles, seatId, abColors)
        if doQing:
            return (MTile.getColor(chiTile) == qingColor)
            
        return True
    
    def isPeng(self, allTiles, pengTile, pengPatterns, leftTiles, tingResults, seatResponse, extend={}):
        '''
            默认能碰就碰
            allTiles - 当前玩家的所有手牌
            pengTile - 碰牌
            pengPatterns - 碰牌方案
            seatResponse - 玩家是否选择
            
            extend - 扩展信息，本接口不要再添加更多参数，更多参数通过extend传递
        '''
        if seatResponse:
            return True
        
        seatId = extend.get('seatId', None)
        abColors = extend.get('absenceColor', None)
        doQing, qingColor = self.doQingYiSe(allTiles, leftTiles, seatId, abColors)
        if doQing:
            return (MTile.getColor(pengTile) == qingColor)
            
        return True
    
    def isGang(self, allTiles, gangTile, gangSolution, leftTiles, tingResults, seatResponse, extend={}):
        '''
            默认能杠就杠
            allTiles - 当前玩家的所有手牌
            gangTile - 杠牌
            gangSolution - 杠牌方案
            seatResponse - 玩家是否选择
            
            extend - 扩展信息，本接口不要再添加更多参数，更多参数通过extend传递
        '''
        ftlog.debug('MDropCardStrategyXuezhan.isGang allTiles:', allTiles
                    , ' gangTile:', gangTile
                    , ' gangSolution:', gangSolution
                    , ' tingResults:', tingResults
                    , 'seatResponse:', seatResponse)
        if seatResponse:
            return True
        
        seatId = extend.get('seatId', None)
        abColors = extend.get('absenceColor', None)
        doQing, _ = self.doQingYiSe(allTiles, leftTiles, seatId, abColors)
        if doQing:
            # 清一色默认不开杠    
            return False
        else:
            # 非清一色默认开杠
            return True
    
    def isGrabTing(self):
        '''
            默认能抢听就抢听
        '''
        return True
    
    def isTing(self, allTiles, dropTile, leftTiles, seatResponse=False, extend={}):
        '''
        是否听牌
        '''
        ftlog.debug('isTing allTiles:', allTiles
                    , ' dropTile:', dropTile
                    , ' leftTiles:', leftTiles
                    , ' seatResponse:', seatResponse)
        if seatResponse:
            return True
        
        seatId = extend.get('seatId', None)
        abColors = extend.get('absenceColor', None)
        doQing, qingColor = self.doQingYiSe(allTiles, leftTiles, seatId, abColors)
        if doQing:
            handTiles = copy.deepcopy(allTiles[MHand.TYPE_HAND])
            handColors = MTile.filterTiles(handTiles, qingColor)
            if (MTile.getColor(dropTile) == qingColor) and (len(handTiles) != len(handColors)):
                ftlog.debug('handTiles:', handTiles
                            , ' handColors:', handColors
                            , ' dropTile:', dropTile
                            , ' doQingYiSe, do not drop...')
                return False
        return True

    def isWin(self, allTiles, winTile, winStyle, leftTiles, seatResponse, extend={}):
        '''
            默认能胡就胡
            allTiles - 当前玩家的所有手牌
            winTile - 胡牌
            winStyle - 是吃炮胡，抢杠胡，还是自摸胡。
                被人点炮则胡
                自摸胡时，考虑下是否更换听口，以博取更好的机会
            seatResponse - 玩家是否选择，已选择，则返回True
            
            extend - 扩展信息，本接口不要再添加更多参数，更多参数通过extend传递
        '''
        ftlog.debug('isWin allTiles:', allTiles
                    , ' winTile:', winTile
                    , ' winStyle:', winStyle
                    , ' leftTiles:', leftTiles
                    , ' seatResponse:', seatResponse)
        
        if seatResponse:
            return True
        
        seatId = extend.get('seatId', None)
        abColors = extend.get('absenceColor', None)
        doQing, qingColor = self.doQingYiSe(allTiles, leftTiles, seatId, abColors)
        if doQing:
            return self.isQingYiSe(allTiles, qingColor) and (MTile.getColor(winTile) == qingColor)
        return True
    
    def isQingYiSe(self, allTiles, qingColor):
        '''
        判断当前是否是清一色
        '''
        allTilesArr = MHand.copyAllTilesToList(allTiles)
        for tile in allTilesArr:
            if MTile.getColor(tile) != qingColor:
                return False
            
        return True
        
    
    def isSanShaQingYiSe(self, seatId, abColors):
        '''
        是否是三杀清一色
        其他三家的缺牌花色是一样的，同时我的缺牌花色与其他三家的不一样。
        
        策略：
        清一色胡其他三家的缺牌花色
        
        分析：
        可以胡所有的听牌
        '''
        playerCount = len(abColors)
        if playerCount != 4:
            return False
        
        myAb = abColors[seatId]
        otherAb = abColors[(seatId + 1) % playerCount]
        
        if myAb == otherAb:
            return False, otherAb
        
        otherAbCount = 0
        for ab in abColors:
            if ab == otherAb:
                otherAbCount += 1
        
        return (otherAbCount == 3), otherAb
    
    
    def doQingYiSe(self, allTiles, leftTiles, seatId, abColors):
        '''
            是否做清一色
        '''
        isSanSha, bestColor = self.isSanShaQingYiSe(seatId, abColors)
        if isSanSha:
            ftlog.debug('SanSha, best situation!!! doSanShaQingYiSe')
            return True, bestColor
        
        length = 9
        if len(leftTiles) >= 50:
            length = 8
        elif len(leftTiles) >= 40:
            length = 9
        elif len(leftTiles) >= 30:
            length = 10
        elif len(leftTiles) >= 20:
            length = 11
            
        allTilesArr = MHand.copyAllTilesToList(allTiles)
        cpgTiles = MHand.copyTiles(allTiles, [MHand.TYPE_CHI, MHand.TYPE_PENG, MHand.TYPE_GANG])
        wans = MTile.filterTiles(allTilesArr, MTile.TILE_WAN)
        wanLength = len(wans)
        if wanLength >= length:
            for tile in cpgTiles:
                if MTile.getColor(tile) != MTile.TILE_WAN:
                    return False, MTile.TILE_FENG
            return True, MTile.TILE_WAN
            
        tongs = MTile.filterTiles(allTilesArr, MTile.TILE_TONG)
        tongLength = len(tongs)
        if tongLength >= length:
            for tile in cpgTiles:
                if MTile.getColor(tile) != MTile.TILE_TONG:
                    return False, MTile.TILE_FENG
            return True, MTile.TILE_TONG
                
        tiaos = MTile.filterTiles(allTilesArr, MTile.TILE_TIAO)
        tiaoLength = len(tiaos)
        if tiaoLength >= length:
            for tile in cpgTiles:
                if MTile.getColor(tile) != MTile.TILE_TIAO:
                    return False, MTile.TILE_FENG
            return True, MTile.TILE_TIAO
        
        
        if wanLength >= tongLength and wanLength >= tiaoLength:
            return False, MTile.TILE_WAN
        elif tongLength >= wanLength and tongLength >= tiaoLength:
            return False, MTile.TILE_TONG
        else:
            return False, MTile.TILE_TIAO
    
    def getBestDropTile(self, tiles_player_hand, tiles_left, tile, isTing, magicTiles, extend={}):
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
        ftlog.debug('MDropCardStrategyXuezhan.getBestDropTile tiles_player_hand:', tiles_player_hand
                    , ' tiles_left:', tiles_left
                    , ' tile:', tile
                    , ' isTing:', isTing
                    , ' magicTiles:', magicTiles
                    , ' extend:', extend
                    )
        
        if isTing:
            # 听牌后，直接打出摸到的牌
            return tile, 0
        
        tiles_value_Arr, tiles_player_Arr = MTileValue.getHandTilesValue(tiles_player_hand, tiles_left)

        # 如果有缺牌，打出缺牌
        seatId = extend.get('seatId', 0)
        abColors = extend.get('absenceColor', [])
        absenceColor = MTile.TILE_FENG
        if len(abColors) > 0:
            absenceColor = abColors[seatId]
            
        abMinTile = 0
        abMinValue = 0
        for tile in MTile.traverseTile(absenceColor):
            if tiles_player_Arr[tile] > 0:
                if abMinTile == 0:
                    abMinTile = tile
                    abMinValue = tiles_value_Arr[tile]
                    continue
                
                if abMinValue > tiles_value_Arr[tile]:
                    abMinValue = tiles_value_Arr[tile]
                    abMinTile = tile
        if abMinTile:
            ftlog.debug('has Absence, drop the min absence tile:', abMinTile
                        , ' abMinValue:', abMinValue)
            return abMinTile, abMinValue
        
        seatId = extend.get('seatId', None)
        abColors = extend.get('absenceColor', None)
        doQing, qingColor = self.doQingYiSe(tiles_player_hand, tiles_left, seatId, abColors)
        # 放大癞子牌的作用
        for mTile in magicTiles:
            tiles_value_Arr[mTile] = tiles_value_Arr[mTile] * 100
            
        # 如果有一门花色大于9张牌，放大该门花色牌的价值，便于去做清一色番型
        if doQing:
            colors = [MTile.TILE_WAN, MTile.TILE_TONG, MTile.TILE_TIAO]
            colors.remove(absenceColor)
            colors.remove(qingColor)
            dMinTiles = []
            dMinValue = 0
            for tile in MTile.traverseTile(colors[0]):
                if tiles_player_Arr[tile] > 0:
                    if len(dMinTiles) == 0:
                        dMinValue = tiles_value_Arr[tile]
                        dMinTiles.append(tile)
                        continue
                    
                    if dMinValue > tiles_value_Arr[tile]:
                        dMinValue = tiles_value_Arr[tile]
                        dMinTiles = [tile]
                    elif dMinValue == tiles_value_Arr[tile]:
                        dMinTiles.append(tile)
                        
            if len(dMinTiles) > 0:
                ftlog.debug('doQingYiSe, qingColor:', qingColor
                            , ' dMinTiles:', dMinTiles
                            , ' dMinValue:', dMinValue)
                return self.chooseBestDropTile(dMinTiles, tiles_left, qingColor), dMinValue
         
        tingRule = extend.get('tingRule', None)    
        # [{'dropTile': 11, 'winNodes': [{'winTile': 1, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [1, 2, 3]]}, {'winTile': 2, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [3, 4, 5], [2, 2]]}, {'winTile': 4, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [2, 3, 4]]}, {'winTile': 5, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [5, 5], [2, 3, 4]]}, {'winTile': 7, 'winTileCount': 1, 'pattern': [[6, 6], [5, 6, 7], [5, 6, 7], [2, 3, 4]]}, {'winTile': 8, 'winTileCount': 1, 'pattern': [[6, 7, 8], [6, 6, 6], [5, 5], [2, 3, 4]]}]}]
        if tingRule:
            canTing, tingResults = tingRule.canTing(tiles_player_hand, tiles_left, tile, magicTiles)
            ftlog.debug(canTing)
            ftlog.debug(tingResults)
            
            if canTing:
                totalValue = 0
                for tingResult in tingResults:
                    # 对dropTile的价值重新考虑
                    dropTile = tingResult['dropTile']
                    tiles_value_Arr[dropTile] = 0
                    
                    winNodes = tingResult['winNodes']
                    for winNode in winNodes:
                        totalValue += winNode['winTileCount'] * winNode['winFan']
                        
                for tingResult in tingResults:
                    dropTile = tingResult['dropTile']
                    winNodes = tingResult['winNodes']
                    dropValue = 0
                    for winNode in winNodes:
                        dropValue += winNode['winTileCount'] * winNode['winFan']        
                    tiles_value_Arr[dropTile] += (-dropValue)
                    
                    if doQing and (MTile.getColor(dropTile) == qingColor):
                        # 优先打出非清一色颜色的上听牌
                        tiles_value_Arr[dropTile] += (totalValue / len(tingResults))
                        
                    ftlog.debug('MDropCardStrategyXuezhan.getBestDropTile dropTile:', dropTile
                                , ' dropTileValue:', tiles_value_Arr[dropTile])
                        
                ftlog.debug('MDropCardStrategyXuezhan.getBestDropTile adjust tileValue by ting:', tiles_value_Arr
                        , ' tingResults:', tingResults
                        , ' totalValue:', totalValue)
         
        minTiles = []
        minValue = 0  
        for index in range(MTile.TILE_MAX_VALUE):
            if tiles_player_Arr[index] > 0:
                if (len(minTiles) == 0) or (minValue > tiles_value_Arr[index]):
                    minValue = tiles_value_Arr[index]
                    minTiles = [index]
                elif minValue == tiles_value_Arr[index]:
                    minTiles.append(index)
         
        ftlog.debug('MDropCardStrategyJipinghu.getBestDropTile minTiles:', minTiles
                    , ' tileValue:', minValue)        
        return self.chooseBestDropTile(minTiles, tiles_left, qingColor), minValue
    
    def chooseBestDropTile(self, tiles, leftTiles, mostColor):
        '''
        从若干最小分值的牌中选择一个最合适的
        附加权重：
        1）自身权重
        1、9的本身附加权重为0
        2，8的附件权重为1
        3，4，5，6，7的附件权重为2
        2）剩余牌数权重
        剩余牌数的附件权重每张为1
        3）花色权重
        花色之间的比较，花色较多的一方去加权重为1，花色较少的一方附件权重为0
        '''
        if len(tiles) == 1:
            return tiles[0]
        
        tiles.sort()
        values = [0 for _ in tiles]
        
        minTile = 0
        minValue = 0
        
        for index in range(len(tiles)):
            tile = tiles[index]
            
            if (MTile.getValue(tile) == 1) or (MTile.getValue(tile) == 9):
                values[index] += 0
            elif (MTile.getValue(tile) == 2) or (MTile.getValue(tile) == 8):
                values[index] += 1
            else:
                values[index] += 2
                
            tileCount = 0
            for _t in leftTiles:
                if _t == tile:
                    tileCount += 1
            values[index] += tileCount
            
            if MTile.getColor(tile) == mostColor:
                values[index] += 1
                
            if (minTile == 0) or (minValue > values[index]):
                minTile = tile
                minValue = values[index]  
          
        ftlog.debug('chooseBestDropTile tiles:', tiles
                    , ' leftTiles:', leftTiles
                    , ' mostColor:', mostColor
                    , ' values:', values
                    , ' minTile:', minTile
                    , ' minValue:', minValue)
                
        return minTile  
            
if __name__ == "__main__":
    allTiles = [[1, 1, 1, 2, 3, 4, 4, 7, 8, 9, 21], [], [[6, 6, 6]], [], [], [], [21], []]
    tile = 11
    
    ai = MDropCardStrategyXuezhanHigh()
    minTile, minValue = ai.getBestDropTile(allTiles, [21, 21, 21, ], 11, False, [], 1, {})
    print minTile, minValue
