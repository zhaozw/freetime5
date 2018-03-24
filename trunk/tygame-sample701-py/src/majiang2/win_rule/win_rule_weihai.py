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

class MWinRuleWeihai(MWinRule):
    """
    威海玩法的和牌规则
    1）没听牌 不和
    2）和牌不可以过
    3）和牌完全从听中去和牌番型
    """
    def __init__(self):
        super(MWinRuleWeihai, self).__init__()
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
        # 不能和牌的情况： 放过锚手中有风牌或箭牌
        if len(tiles[MHand.TYPE_MAO]) > 0:
            if self.tableConfig[MTDefine.MAO_DAN_SETTING] & MTDefine.MAO_DAN_DNXBZFB:#乱锚时手中有风牌或箭牌
                for T in tiles[MHand.TYPE_HAND]:
                    if T >= 31:
                        return False ,[]
            else:
                has_jmao = 0 #有箭牌
                has_fmao = 0 #有风牌
                for mao in tiles[MHand.TYPE_MAO]:
                    if mao['type'] == 1:
                        has_jmao = 1
                    if mao['type'] == 2:
                        has_fmao = 1
                if has_jmao:
                    for T in tiles[MHand.TYPE_HAND]:
                        if T >= 35:
                            return False,[]
                if has_fmao:
                    for T in tiles[MHand.TYPE_HAND]:
                        if T >= 31 and T <= 34 :
                            return False,[]




        # 威海麻将允许胡七对
        resultQiDui, patternQiDui = MWin.isQiDui(tiles[MHand.TYPE_HAND])
        if resultQiDui:
            return True, patternQiDui


        ftlog.debug('MWinRuleWeihai 258jiang_config======:', self.tableConfig[MTDefine.ONLY_JIANG_258])

        # 挑出2，5，8将，看剩下的牌是否能胡牌
        if self.tableConfig[MTDefine.ONLY_JIANG_258]:
            jiangPatterns = [[MTile.TILE_TWO_WAN, MTile.TILE_TWO_WAN]
                , [MTile.TILE_FIVE_WAN, MTile.TILE_FIVE_WAN]
                , [MTile.TILE_EIGHT_WAN, MTile.TILE_EIGHT_WAN]
                , [MTile.TILE_TWO_TONG, MTile.TILE_TWO_TONG]
                , [MTile.TILE_FIVE_TONG, MTile.TILE_FIVE_TONG]
                , [MTile.TILE_EIGHT_TONG, MTile.TILE_EIGHT_TONG]
                , [MTile.TILE_TWO_TIAO, MTile.TILE_TWO_TIAO]
                , [MTile.TILE_FIVE_TIAO, MTile.TILE_FIVE_TIAO]
                , [MTile.TILE_EIGHT_TIAO, MTile.TILE_EIGHT_TIAO]
                             ]
            for jiangPat in jiangPatterns:
                result, pattern = MWin.isHuWishSpecialJiang(tiles[MHand.TYPE_HAND], jiangPat)
                ftlog.debug('MWinRuleWeihai isHuWishSpecialJiang.result======:', result, 'pattern=====', pattern)
                if result:
                    return result, pattern
            return False, []
        else:
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
    rule = MWinRuleWeihai()
    ftlog.debug(rule.isHu(tiles, 2, True, [3]))