# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.ai.ting import MTing
from majiang2.ting_rule.ting_rule import MTingRule
from majiang2.tile.tile import MTile
from majiang2.player.hand.hand import MHand
from freetime5.util import ftlog

class MTingJiPingHuRule(MTingRule):
    """
    听牌规则

    """
    def __init__(self):
        super(MTingJiPingHuRule, self).__init__()
        
    def canTing(self, tiles, leftTiles, tile, magicTiles = [], winSeatId = 0):
        """子类必须实现
        参数：
        1）tiles 该玩家的手牌
        返回值：
        是否可以听牌，听牌详情
        """
        tileArr = MTile.changeTilesToValueArr(MHand.copyAllTilesToList(tiles))
        resultFlag, result = MTing.canTing(self.tilePatternChecker, self.tableTileMgr, tiles, leftTiles, self.winRuleMgr, tile, magicTiles, winSeatId)
        ftlog.debug('MTingJiPingHuRule.canTing result:',resultFlag,result)
        return resultFlag, result

    def canTingBeforeAddTile(self, tiles, leftTiles, magicTiles=[], winSeatId=0):
        """子类必须实现
        参数：
        返回值：
        发牌后查看是否可以听牌，isHu已经判断是否定缺等胡牌条件，这里就不再判断了
        """
        return MTing.canTingBeforeAddTile(self.tilePatternChecker, self.tableTileMgr, tiles, leftTiles, self.winRuleMgr,
                                          magicTiles, winSeatId, winSeatId)

    def canTingAfterPeng(self, tiles):
        """"碰之后是否可以马上听牌"""
        return True