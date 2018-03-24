# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.ai.ting import MTing
from majiang2.ting_rule.ting_rule import MTingRule
from freetime5.util import ftlog
from majiang2.win_rule.win_rule_baicheng import MWinRuleBaicheng

class MTingBaichengRule(MTingRule):
    """胡牌规则
    """
    def __init__(self):
        super(MTingBaichengRule, self).__init__()
    
    def canTing(self, tiles, leftTiles, tile, magicTiles = [], winSeatId = 0):
        """子类必须实现
        参数：
        1）tiles 该玩家的手牌
        
        返回值：
        是否可以听牌，听牌详情
        """
        return MTing.canTing(self.tilePatternChecker, self.tableTileMgr, tiles, leftTiles, self.winRuleMgr, tile, magicTiles, winSeatId)
    
    def canTingAfterPeng(self, tiles):
        """"碰之后是否可以马上听牌"""
        # 和抢听是矛盾的，非抢听情况下，卡五星玩家正常碰牌后，应马上弹出听牌按钮
        return True
    
if __name__ == "__main__":
    tiles = [[14, 15, 24, 25], [], [[1,1,1],[12,12,12],[11,11,11]], [], [], [1]]
    leftTiles = [25, 28, 11, 26, 29, 12, 24, 23, 35, 27, 15, 35, 17, 35, 16, 28, 25, 14, 14, 11, 16, 14, 27, 16, 28, 26, 18, 15, 25, 14, 29, 13, 25, 22, 18]
    rule = MTingBaichengRule()
    rule.setWinRuleMgr(MWinRuleBaicheng())
    ftlog.debug(rule.canTing(tiles, leftTiles, 16, []))
