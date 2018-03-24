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

class MTableTileDandong(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileDandong, self).__init__(playerCount, playMode, runMode)
        
    def getCheckFlowCount(self):
        """覆盖父类方法,荒庄牌的数量"""
        fakeRemainCount = len(self.tiles)
        if fakeRemainCount <= self.getFlowCount():
            return 0
        return fakeRemainCount
    
    def getFlowCount(self):
        return 8

