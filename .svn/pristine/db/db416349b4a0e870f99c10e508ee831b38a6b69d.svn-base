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
from majiang2.tile.tile import MTile
from majiang2.table_tile.table_tile import MTableTile

class MTableTileJinan(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileJinan, self).__init__(playerCount, playMode, runMode)
        self.setQiangGangRule(0b010)
        # 过胡胡牌数组
        self.__pass_hu = [[] for _ in range(0, playerCount)]

    def reset(self):
        super(MTableTileJinan, self).reset()
        self.__pass_hu = [[] for _ in xrange(self.playCount)]

    def addPassHuBySeatId(self, seatId, tile):
        if tile in self.__pass_hu[seatId]:
            return
        else:
            self.__pass_hu[seatId].append(tile)

    def clearPassHuBySeatId(self, seatId):
        self.__pass_hu[seatId] = []

    def isPassHuTileBySeatId(self, seatId, tile):
        if tile in self.__pass_hu[seatId]:
            return True
        return False

    @property
    def passHu(self):
        return self.__pass_hu

    def setPassHu(self,passhu):
        self.__pass_hu = passhu

    def getCheckFlowCount(self):
        """
        获取用于流局判定的剩余牌数,用于某些提前判定流局的
        """
        tileCount = len(self.tiles)
        return tileCount

    def getFlowCount(self):
        """
        获取用于流局判定的剩余牌数 7组牌,用于某些提前判定流局的
        """
        return 0

    def isFlower(self, tile):
        """判断tile是否花牌"""
        return MTile.isFlower(tile)
    
    def getTingLiangMode(self):
        '''听牌时显示听口的牌'''
        return MTableTile.MODE_LIANG_TING
