# -*- coding=utf-8
'''
Created on 2016年9月23日
牌桌麻将牌的管理器
包括：
1）发牌
2）牌桌上的出牌
3）宝牌

发牌说明：
发牌涉及到好牌点
@author: zhaol
'''
from majiang2.table_tile.table_tile import MTableTile
from majiang2.table_state.state import MTableState
from freetime5.util import ftlog
from majiang2.table.table_config_define import MTDefine

class MTableTilePanjin(MTableTile):
    
    def __init__(self, playerCount, playMode, runMode):
        super(MTableTilePanjin, self).__init__(playerCount, playMode, runMode)
        # 宝牌
        self.__magic_tile = None
        
        # 过胡胡牌数组
        self.__pass_hu = [[] for _ in range(0, playerCount)]
        
    def reset(self):
        """重置"""
        super(MTableTilePanjin, self).reset()
        self.__magic_tile = None
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
        
    def shuffle(self, goodPointCount, handTileCount):
        """
        洗牌器 
        添加特殊逻辑，宝牌
        """
        super(MTableTilePanjin, self).shuffle(goodPointCount, handTileCount)
        if len(self.tiles) > 0:
            if self.tableConfig.get(MTDefine.HUI_PAI, 0)==1:
                #self.__magic_tile = random.choice(self.tiles)
                self.__magic_tile = self.tiles[-1]
                self.addSpecialTile(self.__magic_tile)

                
            ftlog.debug( 'MTableTileBaicheng.shuffle changed tile:', self.__magic_tile,'self.tableConfig.get(MTDefine.HUI_PAI, 0)',self.tableConfig.get(MTDefine.HUI_PAI, 0) )
    
    def canUseMagicTile(self, state):
        """牌桌状态state，是否可使用癞子牌"""
        if state & MTableState.TABLE_STATE_HU:
            return True
        
        return False
    
    def getMagicTiles(self, isTing = False):
        """获取宝牌，采用数组，有的游戏有多个宝牌"""
        if self.__magic_tile:
            return [self.__magic_tile]
        
        return []
    
    def getCheckFlowCount(self):
        """覆盖父类方法,荒庄牌的数量"""
        fakeRemainCount = len(self.tiles)
        if fakeRemainCount <= self.getFlowCount():
            return 0
        return fakeRemainCount
    
    def getFlowCount(self):
        return 16
    
    