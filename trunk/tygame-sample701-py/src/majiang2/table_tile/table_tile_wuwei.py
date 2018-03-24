# -*- coding=utf-8
'''
Created on 2016年12月02日
牌桌麻将牌的管理器
包括：
1）发牌
2）牌桌上的出牌
3）宝牌

发牌说明：
发牌涉及到好牌点
@author: luoxf
'''
from majiang2.table_tile.table_tile import MTableTile

class MTableTileWuWei(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileWuWei, self).__init__(playerCount, playMode, runMode)
        self.setQiangGangRule(0b010)  # 回头杠才能抢杠胡
        
    def canGangAfterPeng(self):
        """碰牌后，可以马上选择杠牌"""
        return True
    
    def getCheckFlowCount(self):
        """
        获取用于流局判定的剩余牌数,用于某些提前判定流局的,最后四张，只摸不打
        """
        tileCount = len(self.tiles)
        return tileCount

    def selectGangAfterTing(self):
        """听牌之后杠是否需要选择"""
        return True

    def getTingGangMode(self):
        """听暗杠"""
        return MTableTile.AFTER_TING_HU_NO_CHANGE_TING | MTableTile.AFTER_TING_HU_WITHOUT_MINGGANG