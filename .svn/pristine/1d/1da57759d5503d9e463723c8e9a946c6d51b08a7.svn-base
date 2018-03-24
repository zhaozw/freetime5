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
from freetime5.util import ftlog
from majiang2 import player
from majiang2.table_tile.table_tile import MTableTile
from majiang2.tile.tile import MTile

class MTableTileSiChuan(MTableTile):

    def __init__(self, playerCount, playMode, runMode):
        super(MTableTileSiChuan, self).__init__(playerCount, playMode, runMode)
        self.setQiangGangRule(self.QIANG_GANG_RULE_HUI_TOU)  
        # 过胡胡牌数组
        self.__pass_hu = [[] for _ in range(0, playerCount)]
        # 呼叫转移的actionId 退税时使用
        self.__callTransferId = []
        
    def reset(self):
        super(MTableTileSiChuan, self).reset()
        self.__pass_hu = [[] for _ in xrange(self.playCount)]
        self.__callTransferId = []

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
    def callTransferId(self):
        return self.__callTransferId
    
    def setCallTransferId(self, actionId):
        self.__callTransferId.append(actionId)
    
    @property
    def passHu(self):
        return self.__pass_hu

    def setPassHu(self, passhu):
        self.__pass_hu = passhu
        
    def getCheckFlowCount(self):
        """
        获取用于流局判定的剩余牌数,用于某些提前判定流局的,例如云南曲靖,如需要由子类覆盖
        
        杠牌数量摸2有余，11
        杠牌数量摸2无余，12
        """
        tileCount = len(self.tiles)
        return tileCount

    def isHaveTing(self):
        '''
        是否有听牌的动作
        '''
        return False
    
    # 判断是否定缺结束，定缺结束，花色值不应该为-1
    @property
    def isAbsenceFinish(self):
        for color in self.absenceColors:
            if color == -1:
                ftlog.debug('MTableTileSiChuan.isAbsenceFinish False')
                return False
        ftlog.debug('MTableTileSiChuan.isAbsenceFinish True')
        return True
    
    # 血战 人数<4 去掉万牌
    @property
    def isRemoveWanTile(self):
        if self.playCount < 3:
            return True
        return False
    
    def canGangAfterPeng(self):
        """一般麻将默认不允许碰后马上杠牌"""
        return True
    
    def canDuoHu(self):
        """是否允许一炮多响"""
        return True
    
    def getTingGangMode(self):
        """听牌、和牌后 杠不可以影响已有听牌的结果"""
        return MTableTile.AFTER_TING_HU_NO_CHANGE_TING | MTableTile.AFTER_TING_HU_WITHOUT_MINGGANG
    
    def sortHandTileColor(self, players, isAbsence=True):
        '''
        玩家手牌花色排序计算，保存到__hand_tile_sort，相应玩法各自实现
        定缺的颜色不用判断，在最右边，只需要判断没有定缺的
        定缺结束后，额外处理定缺的花色排序 初始化手牌 则不用
        '''
        TILE_COLORS = [MTile.TILE_WAN, MTile.TILE_TONG, MTile.TILE_TIAO]
        colorList = [[] for _ in range(self.playCount)]
        for cp in players:
            if not cp:
                continue
            handTiles = cp.copyHandTiles()
            colorLenList = []
            for color in TILE_COLORS:
                if isAbsence and color == self.absenceColors[cp.curSeatId]:
                    pass
                else:
                    colorTiles = MTile.filterTiles(handTiles, color)
                    colorLenList.append({'color':color, 'len':len(colorTiles)})
            # 根据len来进行排序
            colorLenList.sort(key=lambda colorLen:colorLen['len'], reverse=True)
            for cpColor in colorLenList:
                colorList[cp.curSeatId].append(cpColor['color'])
            # 加上定缺的花色
            if isAbsence:
                colorList[cp.curSeatId].append(self.absenceColors[cp.curSeatId])
        ftlog.debug('MTableTileSiChuan.sortHandTileColor cpColorList:', colorList)
        self.setHandTileColorSort(colorList)
