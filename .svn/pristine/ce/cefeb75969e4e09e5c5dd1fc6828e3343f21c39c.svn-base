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

class MTableTileWeihai(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileWeihai, self).__init__(playerCount, playMode, runMode)
        
    def getCheckFlowCount(self):
        """
        获取用于流局判定的剩余牌数,用于某些提前判定流局的
        """
        tileCount = len(self.tiles)

        if tileCount <= self.getFlowCount():
            return 0
        return tileCount

    def getFlowCount(self):
        """
        获取用于流局判定的剩余牌数 7组牌,用于某些提前判定流局的
        """
        return 14