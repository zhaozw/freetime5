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
import copy

class MWinRuleJinan(MWinRule):
    """
    鸡西玩法的和牌规则
    1）没听牌 不和
    2）和牌不可以过
    3）和牌完全从听中去和牌番型
    """
    def __init__(self):
        super(MWinRuleJinan, self).__init__()
        self.TAG = 'MWinRuleJinan'
    
    def isHu(self, tiles, tile, isTing, getTileType, magicTiles = [], tingNodes = [], winSeatId = 0):
        ftlog.debug(self.TAG, '.isHu tiles:', tiles
                    , ' tile:', tile
                    , ' isTing:', isTing
                    , ' getTileType:', getTileType
                    , ' magicTiles:', magicTiles
                    , ' tingNodes:', tingNodes
                    , ' winSeatId:', winSeatId
                    )

        if self.tableTileMgr.isPassHuTileBySeatId(winSeatId, tile):
            return False, []

        # 济南麻将允许胡七对
        qiduiTiles = copy.deepcopy(tiles)
        resultQiDui, patternQiDui = MWin.isQiDui(qiduiTiles[MHand.TYPE_HAND])
        if resultQiDui:
            if self.tableConfig[MTDefine.ONLY_JIANG_258]:
                for pattern in patternQiDui:
                    tile = pattern[0]
                    if tile > MTile.TILE_NINE_TIAO:
                        continue
                    
                    # 选了258将判断这里，而且不能是风牌
                    if (MTile.getValue(pattern[0]) % 3 == 2) and pattern[0] < MTile.TILE_DONG_FENG:
                        return True, patternQiDui
                return False, []
            else:
                return resultQiDui, patternQiDui
                
        # 花胡
        if getTileType == MWinRule.WIN_BY_MYSELF:
            flowerTiles = copy.deepcopy(tiles)
            resFlowerHu,patternFlowerHu = MWin.isFlowerHu(flowerTiles)
            if resFlowerHu:
                return resFlowerHu, patternFlowerHu

        # 全将
        jiangTiles = copy.deepcopy(tiles)
        resQuanj,patternQuanj = MWin.isQuanJiang(jiangTiles)
        if resQuanj:
            return resQuanj, patternQuanj

        # 十三不靠
        if not self.tableConfig[MTDefine.ONLY_JIANG_258]:
            bukaoTiles = copy.deepcopy(tiles)
            res13Bukao,pattern13Bukao = MWin.is13BuKao(bukaoTiles[MHand.TYPE_HAND])
            if res13Bukao:
                return res13Bukao,pattern13Bukao

        # 挑出2，5，8将，看剩下的牌是否能胡牌
        if self.tableConfig[MTDefine.ONLY_JIANG_258]:
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
        
            jiangTiles = copy.deepcopy(tiles)
            for jiangPat in jiangPatterns:
                result, pattern = MWin.isHuWishSpecialJiang(jiangTiles[MHand.TYPE_HAND], jiangPat)
                if result:
                    return result, pattern
        else:
            newTiles = copy.deepcopy(tiles)
            result, pattern = MWin.isHu(newTiles[MHand.TYPE_HAND])
            return result, pattern
        
        return False, []
    
    
    def canWinAfterChiPengGang(self, tiles):
        """
        吃完之后是否能和牌
        
        济南麻将无此限制
        """
        return True

    def isPassHu(self):
        """是否有过胡规则"""
        return True

if __name__ == "__main__":
    tiles = [[1,2,3,4,5,6,7,8,9,12,12], [[12,13,14]], [], [], [], []]
    rule = MWinRuleJinan()
    ftlog.debug(rule.isHu(tiles, 2, True, [3]))