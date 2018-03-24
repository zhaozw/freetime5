# -*- coding=utf-8
'''
Created on 2016年12月02日
牌桌血战麻将牌的管理器
包括：
1）发牌
2）牌桌上的出牌
3）定缺的花色

发牌说明：
发牌涉及到好牌点
@author: dongwei
'''
from majiang2.table_tile.table_tile import MTableTile
from majiang2.table.table_config_define import MTDefine
from majiang2.table_state.state import MTableState
from freetime5.util import ftlog
from majiang2.tile.tile import MTile

class MTableTileJiPingHu(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileJiPingHu, self).__init__(playerCount, playMode, runMode)
        self.setQiangGangRule(self.QIANG_GANG_RULE_HUI_TOU)
        # 赖子
        self.__magic_factors = None
        self.__magic_tile = None
        # 过胡胡牌数组
        self.__pass_hu = [[] for _ in range(0, playerCount)]
        
    def reset(self):
        super(MTableTileJiPingHu, self).reset()
        self.__pass_hu = [[] for _ in xrange(self.playCount)]
        self.__magic_tile = None

    def getAllTilesForTing(self):
        if self.tableConfig.get(MTDefine.REMOVE_FENG_ARROW_TILES,0):
            return MTile.TilesForTingNoFeng
        else:
            return MTile.TilesForTing

    def shuffle(self, goodPointCount, handTileCount):
        """
        洗牌器
        添加特殊逻辑，确定马牌
        
        1)牌池的最后一张是癞子皮，根据癞子皮确定癞子
        2)继续弹出几张作为马牌
        """
        super(MTableTileJiPingHu, self).shuffle(goodPointCount, handTileCount)

        if len(self.tiles) > 0:
            if self.tableConfig.get(MTDefine.LAIZI, 0):
                self.__magic_factors = self.tiles.pop(-1)
                self.__magic_tile = self.getMagicTilesByFactors()

        ftlog.debug("neal MWinRUleJiPingHu.shuffler magic_tile: ", self.__magic_tile, " magic_factors: ", self.__magic_factors)

        maimaconfig = self.tableConfig.get(MTDefine.MAIMA, MTDefine.MAIMA_ALL)
        maimaCount = self.tableConfig.get(MTDefine.MAIMA_COUNT, 0)
        ftlog.debug('MWinRuleJiPingHu.shuffle before addHorseTiles:', self.tiles)
        if maimaconfig == MTDefine.MAIMA_ALL:
            for _ in range(0,self.playCount):
                for _ in range(0, maimaCount):
                    horsetile = self.tiles.pop(-1)
                    self.addHorseTiles(horsetile)
        elif maimaconfig == MTDefine.MAIMA_ZIMO:
            for _ in range(0, maimaCount):
                horsetile = self.tiles.pop(-1)
                self.addHorseTiles(horsetile)

        ftlog.debug('MWinRuleJiPingHu.shuffle __magic_tile:', self.__magic_tile
            , ' horsetile:', self.horseTiles
            , ' tilesLen:', len(self.tiles)
            , ' tiles:', self.tiles
        )


    def canUseMagicTile(self, state):
        """牌桌状态state，是否可使用癞子牌"""
        if state & MTableState.TABLE_STATE_HU:
            return True

        return False

    def getMagicTiles(self, isTing=False):
        """获取宝牌，采用数组，有的游戏有多个宝牌"""
        if self.__magic_tile:
            return [self.__magic_tile]

        return []

    def getMagicFactors(self, isTing=False):
        """获取赖子皮"""
        if self.__magic_factors:
            return [self.__magic_factors]

        return []

    def getMagicTilesByFactors(self, isTing=False):
        """获取赖子皮获取赖子，采用数组，有的游戏有多个赖子"""
        if not self.__magic_factors :
            return []

        if self.__magic_factors == MTile.TILE_BAI_BAN:
            return MTile.TILE_DONG_FENG
        elif self.__magic_factors % 10 == 9:
            return self.__magic_factors - 8
        else:
            return self.__magic_factors + 1


    def addMagicTile(self, tile):
        self.__magic_tile = tile

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
        获取用于流局判定的剩余牌数,用于某些提前判定流局的,例如云南曲靖,如需要由子类覆盖
        """
        tileCount = len(self.tiles)
        return tileCount

    def getFlowCount(self):
        """
        获取用于流局判定的剩余牌数,用于某些提前判定流局的
        """
        return 0
    
    def isHaveTing(self):
        '''
        是否有听牌的动作
        '''
        return False
    
    def canGangAfterPeng(self):
        """一般麻将默认不允许碰后马上杠牌"""
        return True
    
    def canDuoHu(self):
        """是否允许一炮多响"""
        return True

    def canGangThisTile(self, tile):
        """能否杠这张牌"""
        return tile != self.__magic_tile