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

class MTableTileWuHu(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileWuHu, self).__init__(playerCount, playMode, runMode)
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

    def canDropWhenHaidiLao(self):
        '''
        海底捞时是否可以出牌
            True 可以打出牌
            False 不可以打出牌
        '''
        return False
