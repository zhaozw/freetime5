# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.ai.ting import MTing
from majiang2.ting_rule.ting_rule import MTingRule

class MTingWuWeiRule(MTingRule):
    """
    比较特殊：只有起手听的才需要检查听牌 摸过牌不在检查
    """
    def __init__(self):
        super(MTingWuWeiRule, self).__init__()
    
    def canTing(self, tiles, leftTiles, tile, magicTiles = [], winSeatId = 0):
        """子类必须实现
        参数：
        1）tiles 该玩家的手牌
        
        返回值：
        是否可以听牌，听牌详情
        """
        return MTing.canTing(self.tilePatternChecker, self.tableTileMgr, tiles, leftTiles, self.winRuleMgr, tile, magicTiles, winSeatId)

    def canTingBeforeAddTile(self, tiles, leftTiles, magicTiles=[], winSeatId=0):
        """子类必须实现
        参数：
        1）tiles 该玩家的手牌

        返回值：
        是否可以听牌，听牌详情
        """
        return MTing.canTingBeforeAddTile(self.tilePatternChecker, self.tableTileMgr, tiles, leftTiles, self.winRuleMgr, magicTiles, winSeatId)