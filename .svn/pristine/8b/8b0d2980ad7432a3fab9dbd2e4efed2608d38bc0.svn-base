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
from freetime5.util import ftlog

class MTableTileChaoHu(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileChaoHu, self).__init__(playerCount, playMode, runMode)
        self.setQiangGangRule(0b010)  # 回头杠才能抢杠胡
        # 漏胡牌数组
        self.__playerCount = playerCount
        self.__pass_hu = [[] for _ in range(0, playerCount)]

    def canGangAfterPeng(self):
        """碰牌后，可以马上选择杠牌"""
        return True
