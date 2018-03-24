# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
from majiang2.win_rule.win_rule import MWinRule


class MWinRuleSichuan(MWinRule):
    
    """
    开局房主庄家
    需要传入缺牌的花色
    """
    def __init__(self):
        super(MWinRuleSichuan, self).__init__()
    
    def isHu(self, tiles, tile, isTing, getTileType, magicTiles=[], tingNodes=[], winSeatId=0):
        # 检查是否过胡状态 自摸情况下不判断过胡
        if getTileType != MWinRule.WIN_BY_MYSELF and self.tableTileMgr.isPassHuTileBySeatId(winSeatId, tile):
            ftlog.debug('MWinRuleXueZhan.isHu passHu...')
            return False, []
        tileArr = MTile.changeTilesToValueArr(MHand.copyAllTilesToList(tiles))
        # 获取当前座位号定缺的花色
        colorAbsence = self.tableTileMgr.absenceColors[winSeatId]
        # 获取手牌中定缺花色牌的数量，大于0，不用判断胡
        colorAbsenceNum = MTile.getTileCountByColor(tileArr, colorAbsence)
        # ftlog.debug('MWinRuleXueZhan colorAbsenceNum:', colorAbsenceNum, 'tiles:', tiles, 'tile:', tile, 'colorAbsence:', colorAbsence)
        if colorAbsenceNum > 0:
            return False, []
        
        resultQidui, qiduiPattern = MWin.isQiDui(tiles[MHand.TYPE_HAND], [])
        if resultQidui:
            return True, qiduiPattern
        
        result, rePattern = MWin.isHu(tiles[MHand.TYPE_HAND])
        if result:
            return True, rePattern
        return False, []
    
    def getHuPattern(self, tiles, magicTiles=[]):
        return MWin.isHu(tiles[MHand.TYPE_HAND], magicTiles)
    
    def isPassHu(self):
        """是否有过胡规则"""
        return True
