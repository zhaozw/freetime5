# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.ting import MTing
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
from majiang2.ting_rule.ting_rule import MTingRule


class MTingSichuanRule(MTingRule):
    """
    听牌规则
    血流/血战的听牌规则
    正常听
    不能包含缺牌
    """
    def __init__(self):
        super(MTingSichuanRule, self).__init__()
        
    def canTing(self, tiles, leftTiles, tile, magicTiles=[], winSeatId=0):
        """子类必须实现
        参数：
        1）tiles 该玩家的手牌
        返回值：
        是否可以听牌，听牌详情
        """
        # 血流 血战听牌 需要没有缺牌
        tileArr = MTile.changeTilesToValueArr(MHand.copyAllTilesToList(tiles))
        # 获取当前座位号定缺的花色
        colorAbsence = self.tableTileMgr.absenceColors[winSeatId]
        # 获取手牌中定缺花色牌的数量，大于1，不用判断听 缺牌为1张的时候，打出去缺牌，有可能会听牌
        colorAbsenceNum = MTile.getTileCountByColor(tileArr, colorAbsence)
        # ftlog.debug('MTingRuleSiChuan.canTing colorAbsenceNum:', colorAbsenceNum, 'tiles:', tiles, 'tile:', tile, 'colorAbsence:', colorAbsence)
        if colorAbsenceNum > 1:
            return False, []
        resultFlag, result = MTing.canTing(self.tilePatternChecker, self.tableTileMgr, tiles, leftTiles, self.winRuleMgr, tile, magicTiles, winSeatId)
        # 如果听牌中有定的缺色，需要把其余的听口去掉
        ftlog.debug('MTingRuleSiChuan.canTing result:', result)
        if resultFlag and colorAbsenceNum == 1:
            filterResult = []
            for tingNodes in result:
                if MTile.getColor(tingNodes['dropTile']) == colorAbsence:
                    filterResult.append(tingNodes)
            ftlog.debug('MTingRuleSiChuan.canTing filterResult:', filterResult)
            return len(filterResult) > 0, filterResult   
        else:
            return resultFlag, result 
    
    def canTingBeforeAddTile(self, tiles, leftTiles, magicTiles=[], winSeatId=0):
        """子类必须实现
        参数：
        返回值：
        发牌后查看是否可以听牌，isHu已经判断是否定缺等胡牌条件，这里就不再判断了
        """
        return MTing.canTingBeforeAddTile(self.tilePatternChecker, self.tableTileMgr, tiles, leftTiles, self.winRuleMgr, magicTiles, winSeatId, winSeatId)
    
    def canTingAfterPeng(self, tiles):
        """"碰之后是否可以马上听牌"""
        return True
