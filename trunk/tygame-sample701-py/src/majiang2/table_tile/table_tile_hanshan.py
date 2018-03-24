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
from majiang2.tile.tile import MTile
from majiang2.table.table_config_define import MTDefine

class MTableTileHanShan(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileHanShan, self).__init__(playerCount, playMode, runMode)
        #self.setQiangGangRule(0b010)  # 回头杠才能抢杠胡
        self.__magic_tiles = None
        self.__magic_factors = []

    def reset(self):
        """重置"""
        super(MTableTileHanShan, self).reset()
        self.__magic_tiles = None
        self.__magic_factors = []
        
    def canGangAfterPeng(self):
        """碰牌后，可以马上选择杠牌"""
        return True

    def getCheckFlowCount(self):
        """
        获取用于流局判定的剩余牌数,用于某些提前判定流局的,最后四张，只摸不打
        """
        tileCount = len(self.tiles)
        if tileCount <= self.getFlowCount():
            return 0
        return tileCount
        
    def getFlowCount(self):
        gangCount = 0
        for player in self.players:
            gangs = player.copyGangArray()
            gangCount += len(gangs)

        if gangCount%2 == 0:
            #偶数杠 留24
            return 24
        else:
            # 奇数杠 留25
            return 25

    def shuffle(self, goodPointCount, handTileCount):
        """
        洗牌器
        添加特殊逻辑，赖子
        """
        super(MTableTileHanShan, self).shuffle(goodPointCount, handTileCount)
        if self.tableConfig.get(MTDefine.PEIZI_SETTING, 0) == MTDefine.PEIZI_TYPE1:
            self.__magic_factors.append(self.tiles.pop(-1))
            self.__magic_tiles = self.getMagicTilesByFactors()
            if len(self.__magic_tiles) == 1:
                self.addSpecialTile(self.__magic_tiles[0])

    def getMagicTilesByFactors(self, isTing=False):
        """获取赖子皮获取赖子，采用数组，有的游戏有多个赖子"""
        if len(self.__magic_factors) == 0:
            return []

        magicTiles = []
        for magicFactor in self.__magic_factors:
            if magicFactor == MTile.TILE_BAI_BAN:
                magicTiles.append(MTile.TILE_HONG_ZHONG)
            elif magicFactor == MTile.TILE_BEI_FENG:
                magicTiles.append(MTile.TILE_DONG_FENG)
            elif magicFactor % 10 == 9:
                magicTiles.append(magicFactor - 8)
            else:
                magicTiles.append(magicFactor + 1)

        return magicTiles

    def getMagicTiles(self, isTing=False):
        """获取赖子，采用数组，有的游戏有多个赖子"""
        if self.__magic_tiles:
            return self.__magic_tiles

        return []

    def getMagicFactors(self, isTing = False):
        """获取赖子皮"""
        return self.__magic_factors

    def canShowBaoAfterTing(self):
        """玩家没有听牌时，不显示宝牌"""
        return False

    def getTingGangMode(self):
        """一般麻将听牌后只能杠不影响听口的牌"""
        return MTableTile.AFTER_TING_HU_NONE