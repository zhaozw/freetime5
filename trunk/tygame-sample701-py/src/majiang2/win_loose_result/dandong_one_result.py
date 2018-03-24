# -*- coding=utf-8
'''
Created on 2016年9月23日

一条和牌结果

@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from majiang2.player.player import MPlayerTileGang
from majiang2.table.table_config_define import MTDefine
from majiang2.tile.tile import MTile
from majiang2.win_loose_result.one_result import MOneResult
import copy


class MDandongOneResult(MOneResult):
    
    TIANHU = 'tianHu'
    ZIMO = 'ziMo'
    QIANGGANG = 'QIANGGANG'
    PINGHU = 'PINGHU'
    PIAO = 'piaoHu'
    JIAHU = 'jiaHu'
    MENQING = 'MENQING'
    TING = 'ting'
    # 输家番型
    DIANPAO = 'dianPao'
    DIANPAOBAOZHUANG = 'dianPaoBaoZhuang'
    BIMEN = 'biMen'
    
    
    def __init__(self, tilePatternChecker, playerCount):
        super(MDandongOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = {
            self.TIANHU: {"name":"天胡 ", "index": 0},
            self.ZIMO: {"name":"自摸 ", "index": 1},
            self.MENQING: {"name": "门清 ", "index": 1},
            self.TING: {"name": "报听 ", "index": 1},
            self.PINGHU: {"name":"平胡", "index": 0},
            self.QIANGGANG: {"name":"抢杠胡 ", "index":0},
            self.PIAO: {"name": "飘 ", "index": 2},
            self.JIAHU: {"name": "单张 ", "index": 1},
            # 输家番型 
            self.DIANPAO: {"name": "点炮 ", "index": 1},  # winMode展示
            self.DIANPAOBAOZHUANG: {"name": "包庄 ", "index": 1},  # winMode展示
            self.BIMEN: {"name": "闭门 ", "index": 1},
        }
        
    @property
    def fanXing(self):
        return self.__fan_xing
    
    # 胡牌的番型 手牌 没有吃 没有粘 至少有一个刻
    def isPiao(self):
        playerChiTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_CHI]
        if len(playerChiTiles) > 0:
            return False
        
        playerHandTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND]
        newPlayerHandTiles = MTile.cloneTiles(playerHandTiles)
        newPlayerHandTiles.append(self.winTile)
        
        newPlayerHandTilesArr = MTile.changeTilesToValueArr(newPlayerHandTiles)
        twoCount = 0
        for playerHandTileCount in newPlayerHandTilesArr:
            if playerHandTileCount == 1:
                return False
            elif playerHandTileCount == 2:
                twoCount += 1
            elif playerHandTileCount == 4:
                twoCount += 2
                
        if twoCount > 1:
            return False
        
        return True
    
    def isTianHu(self):
        if self.actionID <= 1:
            return True
        return False
    
    def isDandiao(self):
        if len(self.winNodes) == 1:
            return True
        else:
            return False
        
    def SatisyYaoJiu(self, tiles, addtile=-1):
        # 有幺九
        allTiles = MHand.copyAllTilesToListButHu(tiles)
        if addtile != -1:
            allTiles.append(addtile)
        tilesArr = MTile.changeTilesToValueArr(allTiles)
        
        yaojiucount = MTile.getYaoJiuCount(tilesArr)
        if yaojiucount > 0:
            return True
        else:
            for feng in range(MTile.TILE_DONG_FENG, MTile.TILE_BAI_BAN + 1):
                if tilesArr[feng] >= 1:
                    return True
                    
        return False
    
    def calcWin(self):
    
        ftlog.debug('MDandongOneResult.calcWin self.playerAllTiles[self.winSeatId]', self.playerAllTiles[self.winSeatId])
    
        resultwin = []
        if not self.tingState[self.winSeatId]:
            for tileTry in range(MTile.TILE_MAX_VALUE): 
                if self.SatisyYaoJiu(self.playerAllTiles[self.winSeatId], tileTry):
                    handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
                    handTile.append(tileTry)
                    ishu, pattern = MWin.isHu(handTile, [], True)
                    if ishu:
                        winNode = {}
                        winNode['winTile'] = tileTry
                        winNode['winTileCount'] = 2
                        for p in pattern:
                            p.sort()
                        winNode['pattern'] = pattern
                        resultwin.append(winNode)
                        
            ftlog.debug('MPanjinOneResult.calcWin MWin.isHu(handTile) resultwin', resultwin)
            self.setWinNodes(resultwin)
            
        
        self.results['type'] = MOneResult.KEY_TYPE_NAME_HU
        
        name = ''
        index = 0
        fanPattern = [[] for _ in range(self.playerCount)]
        winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
        # 在和牌时统计自摸，点炮，最大番数
        resultStat = [[] for _ in range(self.playerCount)]
        
        resultStat[self.winSeatId].append({MOneResult.STAT_WIN:1})
        # 正常和牌
        isZiMo = (self.lastSeatId == self.winSeatId)
        if isZiMo:
            resultStat[self.winSeatId].append({MOneResult.STAT_ZIMO:1})
        
        isTianhu = False
        if self.tableConfig.get(MTDefine.TIAN_HU, 0):
            isTianhu = self.isTianHu()
            
        isPiao = self.isPiao()
        isDandiao = self.isDandiao()
        ftlog.debug('MDandongOneResult.calcWin:'
                , ' isTianhu:', isTianhu
                , ' isPiao:', isPiao
                , ' isDandiao:', isDandiao
                )
        
        self.clearWinFanPattern()
        
        
        if isZiMo:
            index += self.fanXing[self.ZIMO]['index']
        
        if self.tableConfig.get(MTDefine.DAN_DIAO_JIA, 0):
            if isDandiao:
                namejia = self.fanXing[self.JIAHU]['name']
                indexjia = self.fanXing[self.JIAHU]['index']
                self.addWinFanPattern(namejia, indexjia)
                index += self.fanXing[self.JIAHU]['index']
       
        if isPiao:
            namepiaohu = self.fanXing[self.PIAO]['name']
            indexpiaohu = self.fanXing[self.PIAO]['index']
            self.addWinFanPattern(namepiaohu, indexpiaohu)
            index += self.fanXing[self.PIAO]['index']
            
        # 赢家门清永远x2
        if self.menState[self.winSeatId] == 1:
            namemenqing = self.fanXing[self.MENQING]['name']
            indexmenqing = self.fanXing[self.MENQING]['index']
            self.addWinFanPattern(namemenqing, indexmenqing)
            index += self.fanXing[self.MENQING]['index']
            
        if self.tingState[self.winSeatId]:
            nameting = self.fanXing[self.TING]['name']
            indexting = self.fanXing[self.TING]['index']
            self.addWinFanPattern(nameting, indexting)
            index += self.fanXing[self.TING]['index']
            
        # 庄家赢x2
        if self.bankerSeatId == self.winSeatId:
            index += 1
            
        # 当前局番型处理
        # 输赢模式 输家番型统计
        biMenFanConfig = self.tableConfig.get(MTDefine.BI_MEN_FAN, 0)
        
        for seatId in range(self.playerCount):
            if seatId == self.winSeatId:
                winModeValue = MOneResult.WIN_MODE_PINGHU
                # 自摸
                if self.lastSeatId == self.winSeatId:
                    winModeValue = MOneResult.WIN_MODE_ZIMO
                    
                winMode[seatId] = winModeValue
                fanPattern[self.winSeatId] = self.winFanPattern
            elif seatId == self.lastSeatId:
                winModeValue = MOneResult.WIN_MODE_DIANPAO
                winMode[seatId] = winModeValue
                resultStat[seatId].append({MOneResult.STAT_DIANPAO:1})
                fanPattern[seatId] = []
                # 点炮包庄
                if self.tableConfig.get(MTDefine.BAOZHUANG_BAOGANG, 0):
                    winModeValue = MOneResult.WIN_MODE_DIANPAO_BAOZHUANG
                    winMode[seatId] = winModeValue
                # 闭门
                if self.menState[seatId] == 1 and biMenFanConfig:
                    looseFanName = self.fanXing[self.BIMEN]['name']
                    looseFanIndex = self.fanXing[self.BIMEN]['index']
                    fanPattern[seatId].append([looseFanName.strip(), str(looseFanIndex) + "番"])
                
            else:
                fanPattern[seatId] = []
                # 闭门
                if self.menState[seatId] == 1 and biMenFanConfig:
                    looseFanName = self.fanXing[self.BIMEN]['name']
                    looseFanIndex = self.fanXing[self.BIMEN]['index']
                    fanPattern[seatId].append([looseFanName.strip(), str(looseFanIndex) + "番"])
        
        score = [index for _ in range(self.playerCount)]
        
        # 庄家输x2 
        if self.bankerSeatId != self.winSeatId:
            score[self.bankerSeatId] += 1
        # 点炮x2
        if self.lastSeatId != self.winSeatId:
            score[self.lastSeatId] += 1

        # 如果选择背靠背 输家闭门x2
        for seatId in range(len(self.menState)):
            if biMenFanConfig and self.menState[seatId] == 1 and seatId != self.winSeatId:
                score[seatId] += 1
                
        scoreIndex = self.tableConfig.get(MTDefine.FAN_LIST, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        ftlog.debug('MDandongOneResult.calcWin scoreIndex:', scoreIndex)   
        winScore = 0
        for seatId in range(len(score)):
            if seatId != self.winSeatId:
                newIndex = score[seatId]
                score[seatId] = -scoreIndex[newIndex]
                winScore += abs(score[seatId])
        score[self.winSeatId] = winScore
        ftlog.debug('MDandongOneResult.calcWin score before baopei:', score)
                
        # 加入底分的概念*2或者*5
        scoreBase = self.tableConfig.get(MTDefine.WIN_BASE, 1)
        ftlog.debug('MMudanjiangOneResult.calcWin scoreBase:', scoreBase)
        for seatId in range(len(score)):
            score[seatId] *= scoreBase
                            
        # 包庄
        if self.lastSeatId != self.winSeatId:
            if self.tableConfig.get(MTDefine.BAOZHUANG_BAOGANG, 0):
                # 包赔
                for seatId in range(len(score)):
                    if seatId != self.winSeatId and seatId != self.lastSeatId:
                        s = score[seatId]
                        score[seatId] = 0
                        score[self.lastSeatId] += s
                ftlog.debug('MDandongOneResult.calcWin dianpaobaozhuang score:', score
                    , ' lastSeatId:', self.lastSeatId
                    , ' winSeatId:', self.winSeatId)
              
        # 单局最佳统计(分数)
        resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN:score[self.winSeatId]})
        
        self.results[self.KEY_TYPE] = '和牌'
        self.results[self.KEY_NAME] = name
        ftlog.debug('MDandongOneResult.calcWin result score:', score)
        self.results[self.KEY_SCORE] = score
        ftlog.debug('MDandongOneResult.calcWin result winMode:', winMode)
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        ftlog.debug('MDandongOneResult.calcWin result fanPattern:', fanPattern)
        self.results[self.KEY_FAN_PATTERN] = fanPattern
    
        
    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
        self.serialize()
        
        if self.resultType == self.RESULT_WIN:
            self.calcWin()
        elif self.resultType == self.RESULT_GANG:
            self.calcGang()
        elif self.resultType == self.RESULT_FLOW:
            self.results[self.KEY_TYPE] = ''
            self.results[self.KEY_NAME] = '流局'
            score = [0 for _ in range(self.playerCount)]
            self.results[self.KEY_SCORE] = score
            winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
            self.results[self.KEY_WIN_MODE] = winMode
            resultStat = [[] for _ in range(self.playerCount)]
            self.results[self.KEY_STAT] = resultStat
            fanPattern = [[] for _ in range(self.playerCount)]
            self.results[self.KEY_FAN_PATTERN] = fanPattern
     
     
    def calcGang(self):
        """计算杠的输赢"""
        ftlog.debug('MDandongOneResult.calcGang...')
        # 明杠暗杠统计
        resultStat = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_GANG
        base = self.tableConfig.get(MTDefine.WIN_BASE, 0)
        if self.style == MPlayerTileGang.AN_GANG:
            self.results[self.KEY_NAME] = "暗杠"
            if self.winTile in range(MTile.TILE_HONG_ZHONG, MTile.TILE_BAI_BAN + 1):
                self.results[self.KEY_NAME] = "彩杠"
                resultStat[self.winSeatId].append({MOneResult.STAT_CaiGANG:1})
                if self.tableConfig.get(MTDefine.JUE_HU, 0):
                    base *= 8
                else:
                    base *= 4
            else:
                base *= 4
                resultStat[self.winSeatId].append({MOneResult.STAT_ANGANG:1})
        else:
            self.results[self.KEY_NAME] = "明杠"
            if self.winTile in range(MTile.TILE_HONG_ZHONG, MTile.TILE_BAI_BAN + 1):
                self.results[self.KEY_NAME] = "彩杠"
                resultStat[self.winSeatId].append({MOneResult.STAT_CaiGANG:1})
                if self.tableConfig.get(MTDefine.JUE_HU, 0):
                    base *= 4
                else:
                    base *= 2
            else:
                base *= 2
                resultStat[self.winSeatId].append({MOneResult.STAT_ANGANG:1})
        resultStat[self.winSeatId].append({MOneResult.STAT_GANG:1})
         
        scores = [-base for _ in range(self.playerCount)]
        scores[self.winSeatId] = (self.playerCount - 1) * base
        
        ftlog.debug('MOneResult.calcGang gangType:', self.results[self.KEY_NAME], ' scores', scores)
        self.results[self.KEY_SCORE] = scores
        self.results[self.KEY_STAT] = resultStat 
          
            
if __name__ == "__main__":
    result = MDandongOneResult()
    result.setTableConfig({})
