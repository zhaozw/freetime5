# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.ai.tile_value import MTileValue
from majiang2.tile.tile import MTile
from majiang2.drop_card_strategy.drop_card_strategy import MDropCardStrategy
from freetime5.util import ftlog

class MDropCardStrategyJiPingHuNormal(MDropCardStrategy):
    """
    
    别人出牌时，自己的应对策略
    是否胡
    是否吃
    是否碰
    是否杠
    是否抢听
    
    """
    def __init__(self):
        super(MDropCardStrategyJiPingHuNormal, self).__init__()
        
    def isChi(self, allTiles, chiTile, chiPatterns, leftTiles, tingResults, seatResponse, extend={}):
        '''
            默认能吃就吃
            allTiles - 当前玩家的所有手牌
            chiTile - 吃牌
            chiPatterns - 吃牌方案
            leftTiles - 牌池剩余牌数
            
            extend - 扩展信息，本接口不要再添加更多参数，更多参数通过extend传递
        '''
        return True
    
    def isPeng(self, allTiles, pengTile, pengPatterns, leftTiles, tingResults, seatResponse, extend={}):
        '''
            默认能碰就碰
            allTiles - 当前玩家的所有手牌
            pengTile - 碰牌
            pengPatterns - 碰牌方案
            leftTiles - 牌池剩余牌数
            
            extend - 扩展信息，本接口不要再添加更多参数，更多参数通过extend传递
        '''
        return True
    
    def isGang(self, allTiles, gangTile, gangSolution, leftTiles, tingResults, seatResponse, extend={}):
        '''
            默认能杠就杠
            allTiles - 当前玩家的所有手牌
            gangTile - 杠牌
            gangSolution - 杠牌方案
            leftTiles - 牌池剩余牌数
            seatResponse - 玩家是否选择
            
            extend - 扩展信息，本接口不要再添加更多参数，更多参数通过extend传递
        '''
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
        return True

    def isWin(self, allTiles, winTile, winStyle, leftTiles, seatResponse, extend={}):
        '''
            默认能胡就胡
            allTiles - 当前玩家的所有手牌
            winTile - 胡牌
            winStyle - 是吃炮胡，抢杠胡，还是自摸胡。
                被人点炮则胡
                自摸胡时，考虑下是否更换听口，以博取更好的机会
            leftTiles - 牌池剩余牌数
            
            extend - 扩展信息，本接口不要再添加更多参数，更多参数通过extend传递
        '''
        return True
    
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
        
        该套策略可用于推倒胡
        """
        if isTing:
            # 听牌后，直接打出摸到的牌
            ftlog.debug('alReady ting, drop tile directly:', tile)
            return tile, 0
        
        tiles_value_Arr, tiles_player_Arr = MTileValue.getHandTilesValue(tiles_player_hand, tiles_left)
        
        # 放大癞子牌的作用
        for mTile in magicTiles:
            tiles_value_Arr[mTile] = tiles_value_Arr[mTile] * 100
          
        tingRule = extend.get('tingRule', None)  
        # [{'dropTile': 11, 'winNodes': [{'winTile': 1, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [1, 2, 3]]}, {'winTile': 2, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [3, 4, 5], [2, 2]]}, {'winTile': 4, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [2, 3, 4]]}, {'winTile': 5, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [5, 5], [2, 3, 4]]}, {'winTile': 7, 'winTileCount': 1, 'pattern': [[6, 6], [5, 6, 7], [5, 6, 7], [2, 3, 4]]}, {'winTile': 8, 'winTileCount': 1, 'pattern': [[6, 7, 8], [6, 6, 6], [5, 5], [2, 3, 4]]}]}]
        if tingRule:
            canTing, tingResults = tingRule.canTing(tiles_player_hand, tiles_left, tile, magicTiles)
            ftlog.debug(canTing)
            ftlog.debug(tingResults)
            
            if canTing:
                totalValue = 0
                
                for tingResult in tingResults:
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
         
        minTile = 0
        minValue = 0  
        for index in range(MTile.TILE_MAX_VALUE):
            if tiles_player_Arr[index] > 0:
                if minTile == 0:
                    minTile = index
                    minValue = tiles_value_Arr[index]
                    continue
                
                if minValue >= tiles_value_Arr[index]:
                    # 优先打高数值的牌，风
                    minValue = tiles_value_Arr[index]
                    minTile = index
         
        ftlog.debug('MDropCardStrategy.getBestDropTile '
                    , ' tile:', tile
                    , ' magicTiles:', magicTiles
                    , ' isTing:', isTing
                    , ' tiles_player_hand:', tiles_player_hand
                    , ' tileValues:', tiles_value_Arr
                    , ' tiles_left:', tiles_left
                    , ' minTile:', minTile
                    , ' minTileValue:', minValue
                    )
        
        return minTile, tiles_value_Arr[minTile]
        
if __name__ == "__main__":
    pass
