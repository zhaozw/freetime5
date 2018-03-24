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


class MPanjinOneResult(MOneResult):
    TIANHU = 'tianHu'
    ZIMO = 'ziMo'
    QIANGGANG = 'qiangGang'
    JIHU = 'jiHu'
    QIONGHU = 'qiongHu'
    JUEHU = 'jueHu'
    PIAO = 'piaoHu'
    # 输家番型
    DIANPAO = 'dianPao'
    DIANPAOBAOZHUANG = 'dianPaoBaoZhuang'
        
    def __init__(self, tilePatternChecker, playerCount):
        super(MPanjinOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = {
            self.TIANHU: {"name":"天胡 ", "index": 0},
            self.ZIMO: {"name":"自摸 ", "index": 1},
            self.QIANGGANG: {"name":"抢杠胡 ", "index":0},
            self.PIAO: {"name": "飘胡 ", "index": 1},
            self.JIHU: {"name": "鸡胡 ", "index": 1},
            self.QIONGHU: {"name": "穷胡 ", "index": 1},
            self.JUEHU: {"name": "绝胡 ", "index": 1},

            # 输家番型 
            self.DIANPAO: {"name": "点炮 ", "index": 1},  # winMode展示
            self.DIANPAOBAOZHUANG: {"name": "包庄 ", "index": 1},  # winMode展示
        }
        
    @property
    def fanXing(self):
        return self.__fan_xing
        
    
    def isMagicTile(self):
        """是不是宝牌"""
        magics = self.tableTileMgr.getMagicTiles(True)
        ftlog.debug('MPanjinOneResult.isMagicTile winTile:', self.winTile
            , ' magicTiles:', magics)
        
        return self.winTile in magics

    
    # 胡牌的番型 手牌 没有吃 没有粘 至少有一个刻
    def isPiao(self):
        playerChiTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_CHI]
        if len(playerChiTiles) > 0:
            return False
        
        playerHandTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND]
        newPlayerHandTiles = MTile.cloneTiles(playerHandTiles)
        newPlayerHandTiles.append(self.winTile)
        
        ishu, pattern = MWin.isHu(newPlayerHandTiles, self.tableTileMgr.getMagicTiles(True), True)
        ftlog.debug('MPanjinOneResult.calcWin isPiao newPlayerHandTiles:', newPlayerHandTiles
                    , 'ishu', ishu, 'pattern', pattern)
        if ishu:
            for p in pattern:
                if len(p) == 3: 
                    if (p[0] == p[2] or p[1] == p[2] or p[0] == p[1]):
                        continue
                    else:
                        ftlog.debug('MPanjinOneResult.calcWin isPiao False')
                        return False
        ftlog.debug('MPanjinOneResult.calcWin isPiao True')
        return True
    
    def isTianHu(self):
        if self.actionID <= 1:
            return True
        return False
    
    def isJiHu(self):
        # 只要牌里有幺鸡，就是鸡胡
        # tileArr = MTile.changeTilesToValueArr(MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId]))
        if self.tableConfig.get(MTDefine.HUI_PAI, 0) and self.tableConfig.get(MTDefine.JI_HU, 0):
            magics = self.tableTileMgr.getMagicTiles(True)
            if magics[0] == MTile.TILE_ONE_TIAO == self.winTile:
                playerHandTiles = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
                if MTile.TILE_ONE_TIAO in playerHandTiles:
                    return False
                else:
                    return True
                
                
        if self.tableConfig.get(MTDefine.JI_HU, 0):
            tempCount = MTile.getTileCount(MTile.TILE_ONE_TIAO, MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId]))
            ftlog.debug('MPanjinOneResult.calcWin isJiHu tempCount:', tempCount)
            # 胡牌
            if tempCount >= 1:
                return True
            else:
                return False

        return False
     
    def isQiongHu(self):
        '''穷胡 '''
        if self.tableConfig.get(MTDefine.QIONG_HU, 0) and self.tableConfig.get(MTDefine.HUI_PAI, 0):
            playerHandTiles = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
            playerHandTiles.append(self.winTile)
            magics = self.tableTileMgr.getMagicTiles(True)
            if magics[0] in playerHandTiles:
                return False
            else:
                return True

        return False
    
    def isJueHu(self):
        '''绝胡 '''
        if self.tableConfig.get(MTDefine.JUE_HU, 0):
            if self.tableConfig.get(MTDefine.HUI_PAI, 0):
                magics = self.tableTileMgr.getMagicTiles(True)
                if self.winTile == magics[0]:
                    return False
            
            ncount = 0
            ncount = self.tableTileMgr.getVisibleTilesCount(self.winTile)
            ftlog.debug('MPanjinOneResult.calcWin isJueHu1', ncount)
            playerHandTiles = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
            playerHandTiles.append(self.winTile)
            playerHandTilesArr = MTile.changeTilesToValueArr(playerHandTiles)
            ncount += playerHandTilesArr[self.winTile]
            ftlog.debug('MPanjinOneResult.calcWin isJueHu2', ncount, 'playerHandTiles:', playerHandTiles, 'playerHandTilesArr', playerHandTilesArr)
            if ncount >= 4:
                return True
            
        return False
    
    def isGangYaoji(self):
        '''杠幺鸡X4 '''
        playerGangTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_GANG]
        ftlog.debug('MPanjinOneResult.calcWin playerGangTiles', playerGangTiles)
        
        for gangObj in playerGangTiles:
            gangPattern = gangObj['pattern']
            if MTile.TILE_ONE_TIAO in gangPattern:
                return True
            
        return False
    
    def SatisyYaoJiu(self, tiles, addtile=-1):
        # 有幺九
        if len(tiles[MHand.TYPE_MAO]) == 0:
            allTiles = MHand.copyAllTilesToListButHu(tiles)
            if addtile != -1:
                allTiles.append(addtile)
            tilesArr = MTile.changeTilesToValueArr(allTiles)
            # 中发白做将
            if tilesArr[MTile.TILE_HONG_ZHONG] < 2 and tilesArr[MTile.TILE_FA_CAI] < 2 and tilesArr[MTile.TILE_BAI_BAN] < 2:
                # 中发白
                if not (tilesArr[MTile.TILE_HONG_ZHONG] > 0 and tilesArr[MTile.TILE_FA_CAI] > 0 and tilesArr[MTile.TILE_BAI_BAN] > 0):
                    yaojiucount = MTile.getYaoJiuCount(tilesArr)
                    if yaojiucount == 0:
                        return False

        return True
    
    def calcWin(self):
 
        resultwin = []
    
        ftlog.debug('MPanjinOneResult.calcWin self.playerAllTiles[self.winSeatId]', self.playerAllTiles[self.winSeatId])
    
        '''
        for tileTry in range(MTile.TILE_MAX_VALUE): 
            if self.SatisyYaoJiu(self.playerAllTiles[self.winSeatId], tileTry):
                handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
                handTile.append(tileTry)
                ishu, pattern = MWin.isHu(handTile,[],True)
                if ishu:
                    winNode = {}
                    winNode['winTile'] = tileTry
                    winNode['winTileCount'] = 2
                    for p in pattern:
                        p.sort()
                    winNode['pattern'] = pattern
                    resultwin.append(winNode)
                    
        ftlog.debug('MPanjinOneResult.calcWin MWin.isHu(handTile) resultwin',resultwin)
        self.setWinNodes(resultwin)
        '''
            
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
        isJiHu = self.isJiHu()
        isQiongHu = self.isQiongHu()
        isJueHu = self.isJueHu()
        isGangYaoji = self.isGangYaoji()
        ftlog.debug('MPanjinOneResult.calcWin:'
                , ' isTianhu:', isTianhu
                , ' isPiao:', isPiao
                , ' isJiHu:', isJiHu
                , ' isQiongHu:', isQiongHu
                , ' isJueHu:', isJueHu
                , ' isGangYaoji:', isGangYaoji
                )
        
        self.clearWinFanPattern()
        
        
        if isTianhu:
            nametianhu = self.fanXing[self.TIANHU]['name']
            indextianhu = self.fanXing[self.TIANHU]['index']
            self.addWinFanPattern(nametianhu, indextianhu)
            index += self.fanXing[self.TIANHU]['index']
            ftlog.debug('MPanjinOneResult.calcWin name:', nametianhu, ' index:', indextianhu)                                 
         
        if isZiMo:
            nameZimo = self.fanXing[self.ZIMO]['name']
            indexZimo = self.fanXing[self.ZIMO]['index']
            self.addWinFanPattern(nameZimo, indexZimo)
            index += self.fanXing[self.ZIMO]['index']
       
        if isPiao:
            namepiaohu = self.fanXing[self.PIAO]['name']
            indexpiaohu = self.fanXing[self.PIAO]['index']
            self.addWinFanPattern(namepiaohu, indexpiaohu)
            index += self.fanXing[self.PIAO]['index']
            
        if isJiHu:
            namejihu = self.fanXing[self.JIHU]['name']
            indexjihu = self.fanXing[self.JIHU]['index']
            self.addWinFanPattern(namejihu, indexjihu)
            index += self.fanXing[self.JIHU]['index']
            
        if isQiongHu:
            nameqionghu = self.fanXing[self.QIONGHU]['name']
            indexqionghu = self.fanXing[self.QIONGHU]['index']
            self.addWinFanPattern(nameqionghu, indexqionghu)
            index += self.fanXing[self.QIONGHU]['index']
            
        if isJueHu or self.qiangGang:
            namejuehu = self.fanXing[self.JUEHU]['name']
            indexjuehu = self.fanXing[self.JUEHU]['index']
            self.addWinFanPattern(namejuehu, indexjuehu)
            index += self.fanXing[self.JUEHU]['index']
            
        # 庄家赢x2
        if self.bankerSeatId == self.winSeatId:
            index += 1
        if isGangYaoji:
            index += 1
            
        # 赢家加钢
        ftlog.debug('MYantaiOneResult.calcWin doublePoints:', self.doublePoints)
        if self.doublePoints[self.winSeatId] == 2:
            index += 1
            
        # 当前局番型处理
        # 输赢模式 输家番型统计
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
                
            else:
                fanPattern[seatId] = []
        
        score = [index for _ in range(self.playerCount)]
        
        # 庄家输x2 
        if self.bankerSeatId != self.winSeatId:
            score[self.bankerSeatId] += 1
        # 点炮x2
        if self.lastSeatId != self.winSeatId:
            score[self.lastSeatId] += 1
        # 输家加钢
        for loose in range(self.playerCount):
            if loose == self.winSeatId:
                continue
            if self.doublePoints[loose] == 2:
                score[loose] += 1 

        scoreIndex = self.tableConfig.get(MTDefine.FAN_LIST, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        ftlog.debug('MPanjinOneResult.calcWin scoreIndex:', scoreIndex)   
        winScore = 0
        for seatId in range(len(score)):
            if seatId != self.winSeatId:
                newIndex = score[seatId]
                score[seatId] = -scoreIndex[newIndex]
                winScore += abs(score[seatId])
        score[self.winSeatId] = winScore
        ftlog.debug('MPanjinOneResult.calcWin score before baopei:', score)
                                    
        # 包庄
        if self.lastSeatId != self.winSeatId:
            if self.tableConfig.get(MTDefine.BAOZHUANG_BAOGANG, 0):
                # 包赔
                for seatId in range(len(score)):
                    if seatId != self.winSeatId and seatId != self.lastSeatId:
                        s = score[seatId]
                        score[seatId] = 0
                        score[self.lastSeatId] += s
                ftlog.debug('MPanjinOneResult.calcWin dianpaobaozhuang score:', score
                    , ' lastSeatId:', self.lastSeatId
                    , ' winSeatId:', self.winSeatId)
              
        # 单局最佳统计(分数)
        resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN:score[self.winSeatId]})
        
        self.results[self.KEY_TYPE] = '和牌'
        self.results[self.KEY_NAME] = name
        ftlog.debug('MPanjinOneResult.calcWin result score:', score)
        self.results[self.KEY_SCORE] = score
        ftlog.debug('MPanjinOneResult.calcWin result winMode:', winMode)
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        ftlog.debug('MPanjinOneResult.calcWin result fanPattern:', fanPattern)
        self.results[self.KEY_FAN_PATTERN] = fanPattern
          
        
    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
        ftlog.debug('MPanjinOneResult.calcScore...')
        self.serialize()
        
        if self.resultType == self.RESULT_GANG:
            self.calcGang()
        elif self.resultType == self.RESULT_WIN:
            self.calcWin()
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
        ftlog.debug('MPanjinOneResult resultName:', self.results[self.KEY_NAME]
                    , ' scores:', self.results[self.KEY_SCORE]
                    , ' stat:', self.results[self.KEY_STAT])    
                 
    def calcGang(self):
        """计算杠的输赢"""
        ftlog.debug('MPanjinOneResult.calcGang...')
        # 明杠暗杠统计
        resultStat = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_GANG
        base = self.tableConfig.get(MTDefine.GANG_BASE, 0)
        if self.style == MPlayerTileGang.AN_GANG:
            self.results[self.KEY_NAME] = "暗杠"
            base *= 2
            resultStat[self.winSeatId].append({MOneResult.STAT_ANGANG:1})
        elif self.style == MPlayerTileGang.MING_GANG:
            self.results[self.KEY_NAME] = "明杠"
            resultStat[self.winSeatId].append({MOneResult.STAT_MINGGANG:1})
                    
        resultStat[self.winSeatId].append({MOneResult.STAT_GANG:1})
        
        scores = [-base for _ in range(self.playerCount)]
        scores[self.winSeatId] = (self.playerCount - 1) * base
        
        ftlog.debug('MPanjinOneResult.calcGang gangType:', self.results[self.KEY_NAME], ' scores', scores)
        self.results[self.KEY_SCORE] = scores
        self.results[self.KEY_STAT] = resultStat      
        
        
if __name__ == "__main__":
    result = MPanjinOneResult()
    
    tiles = [[2, 2, 3, 4, 5, 6, 7, 8, 8, 13, 13], [[12, 13, 14]], [], [], [], []]
    ftlog.debug(result.SatisyYaoJiu(tiles, 4))
