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

class MWinRulePingDu258(MWinRule):
    """
    鸡西玩法的和牌规则
    1）没听牌 不和
    2）和牌不可以过
    3）和牌完全从听中去和牌番型
    """
    def __init__(self):
        super(MWinRulePingDu258, self).__init__()
        self.TAG = 'MWinRulePingDu258'
    
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

        # 检查2，5，8将
        
        # 平度麻将允许胡七对
        resultQiDui, patternQiDui = MWin.isQiDui(tiles[MHand.TYPE_HAND])
        if resultQiDui:
            for pattern in patternQiDui:
                tile = pattern[0]
                if tile > MTile.TILE_NINE_TIAO:
                    continue
                
                if MTile.getValue(pattern[0]) % 3 == 2:
                    return True, patternQiDui
                
            return False, []
        
        # 挑出2，5，8将，看剩下的牌是否能胡牌
        jiangPatterns = [[MTile.TILE_TWO_WAN,MTile.TILE_TWO_WAN]
                         , [MTile.TILE_FIVE_WAN,MTile.TILE_FIVE_WAN]
                         , [MTile.TILE_EIGHT_WAN,MTile.TILE_EIGHT_WAN]
                         , [MTile.TILE_TWO_TONG,MTile.TILE_TWO_TONG]
                         , [MTile.TILE_FIVE_TONG,MTile.TILE_FIVE_TONG]
                         , [MTile.TILE_EIGHT_TONG,MTile.TILE_EIGHT_TONG]
                         , [MTile.TILE_TWO_TIAO,MTile.TILE_TWO_TIAO]
                         , [MTile.TILE_FIVE_TIAO,MTile.TILE_FIVE_TIAO]
                         , [MTile.TILE_EIGHT_TIAO, MTile.TILE_EIGHT_TIAO]
                         ]
        
        for jiangPat in jiangPatterns:
            result, pattern = MWin.isHuWishSpecialJiang(tiles[MHand.TYPE_HAND], jiangPat)
            if result:
                return result, pattern
        return False, []
    
    
    def canWinAfterChiPengGang(self, tiles):
        """
        吃完之后是否能和牌
        
        平度麻将无此限制
        """
        return True
    
if __name__ == "__main__":
    tiles = [[1,2,3,4,5,6,7,8,9,12,12], [[12,13,14]], [], [], [], []]
    rule = MWinRulePingDu258()
    ftlog.debug(rule.isHu(tiles, 2, True, [3]))