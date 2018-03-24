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
@author: dongwei
'''
from majiang2.table_tile.table_tile import MTableTile

class MTableTileYantai(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileYantai, self).__init__(playerCount, playMode, runMode)
        
    def getCheckFlowCount(self):
        """
        获取用于流局判定的剩余牌数,用于某些提前判定流局的,例如云南曲靖,如需要由子类覆盖
        
        杠牌数量摸2有余，11
        杠牌数量摸2无余，12
        """
        tileCount = len(self.tiles)
        return tileCount
    
    def getFlowCount(self):
        return 0
    
    def getTingLiangMode(self):
        '''听牌时显示听口的牌'''
        return MTableTile.MODE_LIANG_TING