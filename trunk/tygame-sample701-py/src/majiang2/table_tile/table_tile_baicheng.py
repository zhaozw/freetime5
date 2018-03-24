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
import copy

class MTableTileBaicheng(MTableTile):
    
    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileBaicheng, self).__init__(playerCount, playMode, runMode)
        # 宝牌
        self.__magic_tile = None
        
    def reset(self):
        """重置"""
        super(MTableTileBaicheng, self).reset()
        self.__magic_tile = None

    def shuffle(self, goodPointCount, handTileCount):
        """
        洗牌器 
        添加特殊逻辑，宝牌
        """
        super(MTableTileBaicheng, self).shuffle(goodPointCount, handTileCount)
        if len(self.tiles) > 0:
            self.__magic_tile = self.tiles.pop(-1)
            self.addSpecialTile(self.__magic_tile)
        
            ftlog.debug( 'MTableTileBaicheng.shuffle changed tile:', self.__magic_tile )
    
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
    
    def getAbandonedMagics(self):
        """获取废弃宝牌"""
        abandons = copy.deepcopy(self.specialTiles)
        if len(abandons) == 0:
            return []
        
        abandons.pop(-1)
        return abandons
    
    def updateMagicTile(self):
        """更新宝牌"""
        if len(self.tiles) == 0:
            return None
        
        self.__magic_tile = self.tiles.pop(-1)
        self.addSpecialTile(self.__magic_tile)
        ftlog.debug( 'MTableTileBaicheng.updateMagicTile changed tile:', self.__magic_tile )
        return self.__magic_tile
    
    def getCheckFlowCount(self):
        """覆盖父类方法,荒庄牌的数量"""
        fakeRemainCount = len(self.tiles)
        if fakeRemainCount <= self.getFlowCount():
            return 0
        return fakeRemainCount
    
    def getFlowCount(self):
        return 4
    
    def canDropWhenHaidiLao(self):
        '''
        海底捞时是否可以出牌
            True 可以打出牌
            False 不可以打出牌
        '''
        return False
    
    def canGangAfterPeng(self):
        """一般麻将默认不允许碰后马上杠牌"""
        return True