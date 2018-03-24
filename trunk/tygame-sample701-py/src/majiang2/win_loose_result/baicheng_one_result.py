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


class MBaichengOneResult(MOneResult):
    # 特殊番型
    TIANHU = 'tianHu'
    BAOZHONGGANG = 'baozhonggang'
    # 基本番型
    ZIMO = 'ziMo'
    QIANGGANG = 'qiangGang'
    JIAHU = 'jiaHu'
    DANDIAO = 'danDiao'
    JIHU = 'jiHu'
    # 二番番型
    MOBAO = 'moBao'
    # 三番番型

    DANPIAO = 'danPiao'
    SHUANGPIAO = 'shuangPiao'
    JIDANPIAO = 'jiDanPiao'
    JISHUANGPIAO = 'jiShuangPiao'
    # 五番番型
    BAOZHONGBAOJIA = 'baoZhongBaoJia'  # 和通宝一样的规则 是夹或者单吊时
    # 预留 先不做
    BIANJIASHUANG = 'bianJiaShuang'
    # 输家番型
    DIANPAO = 'dianPao'
    DIANPAOBAOZHUANG = 'dianPaoBaoZhuang'
    # 闭门可配置 默认不算番
    BIMEN = 'biMen'
    MENQING = 'MENQING'
        
    def __init__(self, tilePatternChecker, playerCount):
        super(MBaichengOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = {
            self.BAOZHONGGANG: {"name":"宝中杠 ", "index": 0},
            self.TIANHU: {"name":"天胡 ", "index": 0},
            self.ZIMO: {"name":"自摸 ", "index": 1},
            self.QIANGGANG: {"name":"抢杠胡 ", "index":1},
            self.JIAHU: {"name": "夹胡 ", "index": 1},
            self.SHUANGPIAO: {"name": "双飘 ", "index": 2},
            self.DANPIAO: {"name": "单飘 ", "index": 3},
            self.JIHU: {"name": "鸡胡 ", "index": 1},
            self.JIDANPIAO: {"name": "鸡单飘 ", "index": 4},
            self.JISHUANGPIAO: {"name": "鸡双飘 ", "index": 3},
            self.DANDIAO: {"name": "单吊 ", "index": 1},
            self.MOBAO: {"name": "摸宝 ", "index": 2},
            self.BAOZHONGBAOJIA: {"name": "宝中宝 ", "index": 3},
            self.MENQING: {"name": "门清 ", "index": 1},

            # 输家番型 
            self.DIANPAO: {"name": "点炮 ", "index": 1},  # winMode展示
            self.DIANPAOBAOZHUANG: {"name": "包庄 ", "index": 1},  # winMode展示
            self.BIMEN: {"name": "闭门 ", "index": 1},
        }
        
    @property
    def fanXing(self):
        return self.__fan_xing
        
    
    def isMagicTile(self):
        """是不是宝牌"""
        magics = self.tableTileMgr.getMagicTiles(True)
        ftlog.debug('MBaichengOneResult.isMagicTile winTile:', self.winTile
            , ' magicTiles:', magics)
        
        return self.winTile in magics
            
    
    def isDanDiao(self):
        
        ftlog.debug('MBaichengOneResult.isDanDiao LIANGTOU_JIA:', self.tableConfig.get(MTDefine.LIANGTOU_JIA, 0), 'len(self.winNodes)', len(self.winNodes))
        
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MBaichengOneResult.isDanDiao winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) != 2:
                        continue
                    
                    if (self.winTile in p) and p[0] == p[1]:
                        # 如果设置两头吊算夹，肯定算单调。如果没有设置，判断手牌
                        if self.tableConfig.get(MTDefine.LIANGTOU_JIA, 0):
                            return True
                        else:
                            haveShun = False
                            for pp in patterns:
                                if len(pp) == 3 and pp[0] != pp[1]:
                                    if ((self.winTile + 1) in pp) or ((self.winTile - 1) in pp):  
                                        haveShun = True
                                        break
                                        
                            if haveShun:
                                return False
                            else:
                                return True
        
        # 宝牌情况时判断单吊
        if self.isMagicTile():
            for wn in self.winNodes:
                winTile = wn['winTile']
                patterns = wn['pattern'] 
                ftlog.debug('MBaichengOneResult.isDanDiao winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) != 2:
                        continue
                    
                    if (winTile in p) and p[0] == p[1]:
                        # 如果设置两头吊算夹，肯定算单调。如果没有设置，判断胡牌胡几口
                        if self.tableConfig.get(MTDefine.LIANGTOU_JIA, 0):
                            ftlog.debug('MBaichengOneResult.isDanDiao winTile:', winTile, 'p:', p)
                            return True
                        else:
                            haveShun = False
                            for pp in patterns:
                                if len(pp) == 3 and pp[0] != pp[1]:
                                    if ((winTile + 1) in pp) or ((winTile - 1) in pp):  
                                        haveShun = True
                                        break
                                        
                            if haveShun:
                                return False
                            else:
                                return True
                    
        return False 
    
    
    # 胡牌的番型 手牌 没有吃 没有粘 至少有一个刻
    def isPiao(self):
        # 如果有吃牌，且不是123条，返回false
        playerChiTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_CHI]
        ftlog.debug('MJixiOneResult.isPiao playerChiTiles:', playerChiTiles)
        for chipattern in playerChiTiles:
            if (21 not in chipattern) or (22 not in chipattern) or (23 not in chipattern):
                return False
        
        playerHandTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND]
        newPlayerHandTiles = MTile.cloneTiles(playerHandTiles)
        if self.isMagicTile():
            for wn in self.winNodes:
                realWinTile = wn['winTile']
                ftlog.debug('MJixiOneResult.isPiao winTile:', realWinTile)
                newPlayerHandTiles.append(realWinTile)
                break
        else:
            newPlayerHandTiles.append(self.winTile)
        
        # 排除21，22，23
        while ((21 in newPlayerHandTiles) and (22 in newPlayerHandTiles) and (23 in newPlayerHandTiles)):
            newPlayerHandTiles.remove(21)
            newPlayerHandTiles.remove(22)
            newPlayerHandTiles.remove(23)
            
        # 排除中发白
        while ((35 in newPlayerHandTiles) and (36 in newPlayerHandTiles) and (37 in newPlayerHandTiles)):
            newPlayerHandTiles.remove(35)
            newPlayerHandTiles.remove(36)
            newPlayerHandTiles.remove(37)
        
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
    
    def isBaozhongbao(self):
        
        for wn in self.winNodes:
            if wn['winTile'] != self.winTile:
                return False
                
        return True
            
    
    def isJia(self):
        """是否夹牌"""
        ftlog.debug('MBaichengOneResult.isJia')
        
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MBaichengOneResult.isJia winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) == 2:
                        continue
                    
                    if p[0] == p[1]:
                        continue
                    
                    if (self.winTile in p) and (p.index(self.winTile)) == 1:
                        return True
                    
        # 宝牌情况处理
        if self.isMagicTile():
            for wn in self.winNodes:
                winTile = wn['winTile']
                patterns = wn['pattern']
                for p in patterns:
                    if len(p) == 2:
                        continue
                    
                    if p[0] == p[1]:
                        continue
                    
                    if (winTile in p) and (p.index(winTile)) == 1:
                        return True
                
        return False

    def isZFBJia(self):
        """是否夹牌"""
        ftlog.debug('MBaichengOneResult.isZFBJia')
        
        for wn in self.winNodes:
            if wn['winTile'] == MTile.TILE_HONG_ZHONG \
                or wn['winTile'] == MTile.TILE_FA_CAI \
                or wn['winTile'] == MTile.TILE_BAI_BAN:
                patterns = wn['pattern']
                for p in patterns:
                    if (wn['winTile'] in p) and len(p) == 3:
                        if p[0] != p[1]:
                            return True

        return False
    
    def isWinnerHasBaozhonggang(self):
        magics = self.tableTileMgr.getMagicTiles(True)
        for wn in self.winNodes:
            patterns = wn['pattern']
            for p in patterns:
                if len(p) == 3 and p[0] == p[1] == p[2] == magics[0]:
                    return True

        return False
    
    def isSanQi(self, winTile=None):         
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MBaichengOneResult.isBian winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) == 2:
                        continue
                    
                    if p[0] == p[1]:
                        continue
                    
                    if (self.winTile in p) and (p.index(self.winTile) == 0) and MTile.getValue(self.winTile) == 7:
                        return True
                    
                    if (self.winTile in p) and (p.index(self.winTile) == 2) and MTile.getValue(self.winTile) == 3:
                        return True
        
        # 宝牌情况处理
        if self.isMagicTile():
            for wn in self.winNodes:
                winTile = wn['winTile']
                patterns = wn['pattern']
                for p in patterns:
                    if len(p) == 2:
                        continue
                    
                    if p[0] == p[1]:
                        continue
                    
                    if (winTile in p) and (p.index(winTile) == 0) and MTile.getValue(winTile) == 7:
                        return True
                    
                    if (winTile in p) and (p.index(winTile) == 2) and MTile.getValue(winTile) == 3:
                        return True
        
        return False
    
    # 胡的就是宝牌
    def isHuMagicTile(self):
        magics = self.tableTileMgr.getMagicTiles(True)
        for wn in self.winNodes:
            if wn['winTile'] in magics:
                return True
        return False
    
    def isBian(self):
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MBaichengOneResult.isBian winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) == 2:
                        continue
                    
                    if p[0] == p[1]:
                        continue
                    
                    if (self.winTile in p) and (p.index(self.winTile) == 0):
                        return True
                    
                    if (self.winTile in p) and (p.index(self.winTile) == 2):
                        return True
        
        # 宝牌情况处理
        if self.isMagicTile():
            for wn in self.winNodes:
                winTile = wn['winTile']
                patterns = wn['pattern']
                for p in patterns:
                    if len(p) == 2:
                        continue
                    
                    if p[0] == p[1]:
                        continue
                    
                    if (winTile in p) and (p.index(winTile) == 0):
                        return True
                    
                    if (winTile in p) and (p.index(winTile) == 2):
                        return True
        
        return False
    
    def isJiHu(self):
        # 只要牌里有幺鸡，就是鸡胡
        # tileArr = MTile.changeTilesToValueArr(MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId]))
        iszimo = self.lastSeatId == self.winSeatId
        
        tempCount = MTile.getTileCount(MTile.TILE_ONE_TIAO, MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId]))
        ftlog.debug('MBaichengOneResult.calcWin isJiHu tempCount:', tempCount)
        
        magics = self.tableTileMgr.getMagicTiles(True)
        if iszimo and (self.winTile == magics[0] == MTile.TILE_ONE_TIAO):
            isHuYaoji = False
            for wn in self.winNodes:
                if wn['winTile'] == MTile.TILE_ONE_TIAO:
                    isHuYaoji = True
            if isHuYaoji:
                return True
            else:
                if tempCount <= 1:
                    return False
                else:
                    return True
            
        else:
            # 胡牌
            if tempCount >= 1:
                return True
            else:
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
 
        isMagic = self.isMagicTile()
        
        resultwin = []
    
        ftlog.debug('MBaichengOneResult.calcWin self.playerAllTiles[self.winSeatId]', self.playerAllTiles[self.winSeatId])
    
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
                    
        ftlog.debug('MBaichengOneResult.calcWin MWin.isHu(handTile) resultwin', resultwin)
        self.setWinNodes(resultwin)
            
        self.results['type'] = MOneResult.KEY_TYPE_NAME_HU
        
        name = ''
        index = 0
        _ = [0 for _ in range(self.playerCount)]
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
        isJia = self.isJia()
        if not isJia:
            isJia = self.isZFBJia()
        isBian = self.isBian()
        isDanDiao = self.isDanDiao()            
        isPiao = self.isPiao()
        isJiHu = self.isJiHu()
        isSanQi = self.isSanQi()
        if not (isJia or isDanDiao or (isBian and isSanQi)):
            if len(self.winNodes) == 1:
                isJia = True 
        ftlog.debug('MBaichengOneResult.calcWin isJia:', isJia
                , ' isTianhu:', isTianhu
                , ' isBian:', isBian
                , ' isDanDiao', isDanDiao
                , ' isPiao:', isPiao
                , ' isJiHu:', isJiHu
                , ' isSanQi:', isSanQi
                )
        
        self.clearWinFanPattern()
        
        
        if self.isWinnerHasBaozhonggang():
            namebaozhonggang = self.fanXing[self.BAOZHONGGANG]['name']
            indexbaozhonggang = self.fanXing[self.BAOZHONGGANG]['index']
            self.addWinFanPattern(namebaozhonggang, indexbaozhonggang)
        
        if isTianhu:
            nametianhu = self.fanXing[self.TIANHU]['name']
            indextianhu = self.fanXing[self.TIANHU]['index']
            self.addWinFanPattern(nametianhu, indextianhu)
            index += self.fanXing[self.TIANHU]['index']
            ftlog.debug('MBaichengOneResult.calcWin name:', nametianhu, ' index:', indextianhu)
            
        # 高级番型处理(清一色 通宝 宝中宝)
        isBaoZhongBao = False                                    
         
        if isZiMo:  # 自摸番型处理
            if isMagic:
                if self.isBaozhongbao():
                    isBaoZhongBao = True
                    nameBaoZhongBao = self.fanXing[self.BAOZHONGBAOJIA]['name']
                    indexBaoZhongBao = self.fanXing[self.BAOZHONGBAOJIA]['index']
                    self.addWinFanPattern(nameBaoZhongBao, indexBaoZhongBao)
                    index += self.fanXing[self.BAOZHONGBAOJIA]['index']
                else:
                    index += self.fanXing[self.MOBAO]['index']
                    self.addWinFanPattern(self.fanXing[self.MOBAO]['name'], self.fanXing[self.MOBAO]['index'])
                    resultStat[self.winSeatId].append({MOneResult.STAT_MOBAO:1})
            else:
                index += self.fanXing[self.ZIMO]['index']
            
            # 计算基本番型
            name, tempindex = self.calcBaseFan(isJia, isBian, isSanQi, isDanDiao, isPiao, isJiHu, isMagic)
            index += tempindex
            ftlog.debug('MBaichengOneResult.calcWin ZiMoFan index:', index)
        else:  # 点炮胡             
            # 计算基本番型
            name, tempindex = self.calcBaseFan(isJia, isBian, isSanQi, isDanDiao, isPiao, isJiHu, isMagic)
            index += tempindex
            ftlog.debug('MBaichengOneResult.calcWin 点炮胡 index:', index)
 
       
        if isJiHu and not isPiao:
            namejihu = self.fanXing[self.JIHU]['name']
            indexjihu = self.fanXing[self.JIHU]['index']
            self.addWinFanPattern(namejihu, indexjihu)
            index += self.fanXing[self.JIHU]['index']
            
        # 赢家门清永远x2
        if self.menState[self.winSeatId] == 1:
            namemenqing = self.fanXing[self.MENQING]['name']
            indexmenqing = self.fanXing[self.MENQING]['index']
            self.addWinFanPattern(namemenqing, indexmenqing)
            index += self.fanXing[self.MENQING]['index']
            
        # 庄家赢x2
        if self.bankerSeatId == self.winSeatId:
            index += 1

        
        biMenFanConfig = self.tableConfig.get(MTDefine.BI_MEN_FAN, 0)
        # 当前局番型处理
        # 输赢模式 输家番型统计
        for seatId in range(self.playerCount):
            if seatId == self.winSeatId:
                winModeValue = MOneResult.WIN_MODE_PINGHU
                # 自摸
                if self.lastSeatId == self.winSeatId:
                    winModeValue = MOneResult.WIN_MODE_ZIMO
                if isMagic and isZiMo:
                    winModeValue = MOneResult.WIN_MODE_mobao
                if isBaoZhongBao:
                    winModeValue = MOneResult.WIN_MODE_baozhongbao
                if self.qiangGang:
                    winModeValue = MOneResult.WIN_MODE_QIANGGANGHU
                    self.addWinFanPattern(self.fanXing[self.QIANGGANG]['name'], self.fanXing[self.QIANGGANG]['index'])
                    

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
                
        for seatId in range(self.playerCount):
            ftlog.debug('MBaichengOneResult calcGangInHand seatId:', seatId, 'self.playerCount', self.playerCount)
            # 手里三张和宝牌一样算暗杠
            if seatId != self.winSeatId:
                handTile = copy.deepcopy(self.playerAllTiles[seatId][MHand.TYPE_HAND])
                handtileArr = MTile.changeTilesToValueArr(handTile)
                magicTiles = self.tableTileMgr.getMagicTiles(True)
                magictile = magicTiles[0]
                if handtileArr[magictile] == 3:
                    gangFanName = self.fanXing[self.BAOZHONGGANG]['name']
                    gangFanIndex = self.fanXing[self.BAOZHONGGANG]['index']
                    fanPattern[seatId].append([gangFanName.strip(), str(gangFanIndex) + "番"])
                    break
                    
        scoreIndex = self.tableConfig.get(MTDefine.FAN_LIST, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        oneLossLimit = self.tableConfig.get(MTDefine.MAX_LOSS_SCORE, 256)
        ftlog.debug('MBaichengOneResult.calcWin scoreIndex:', scoreIndex)   
        winScore = 0
        for seatId in range(len(score)):
            if seatId != self.winSeatId:
                newIndex = score[seatId]
                score[seatId] = (-scoreIndex[newIndex] if scoreIndex[newIndex] < oneLossLimit else -oneLossLimit)
                winScore += abs(score[seatId])
        score[self.winSeatId] = winScore
        ftlog.debug('MBaichengOneResult.calcWin score before baopei:', score)
        
        if self.lastSeatId != self.winSeatId:
            if self.tableConfig.get(MTDefine.BAOZHUANG_BAOGANG, 0):
                # 包赔
                for seatId in range(len(score)):
                    if seatId != self.winSeatId and seatId != self.lastSeatId:
                        s = score[seatId]
                        score[seatId] = 0
                        score[self.lastSeatId] += s
                ftlog.debug('MBaichengOneResult.calcWin dianpaobaozhuang score:', score
                    , ' lastSeatId:', self.lastSeatId
                    , ' winSeatId:', self.winSeatId)
              
              
        # 单局最佳统计(分数)
        resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN:score[self.winSeatId]})
        
        # 白城无漂分，根据score计算最终结果
        self.results[self.KEY_TYPE] = '和牌'
        self.results[self.KEY_NAME] = name
        ftlog.debug('MBaichengOneResult.calcWin result score:', score)
        self.results[self.KEY_SCORE] = score
        ftlog.debug('MBaichengOneResult.calcWin result winMode:', winMode)
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        ftlog.debug('MBaichengOneResult.calcWin result fanPattern:', fanPattern)
        self.results[self.KEY_FAN_PATTERN] = fanPattern
          
      
    def calcBaseFan(self, isJia, isBian, isSanqi, isDanDiao, isPiao, isJiHu, ismagic):
        name = ''
        index = 0
                       
        if isPiao:
            if isJiHu:
                
                if isJia or isDanDiao or (isBian and isSanqi) or len(self.winNodes) == 1:
                    name = self.fanXing[self.JIDANPIAO]['name']
                    index = self.fanXing[self.JIDANPIAO]['index']
                    self.addWinFanPattern(name, index)
                    return name, index 
                else:
                    name = self.fanXing[self.JISHUANGPIAO]['name']
                    index = self.fanXing[self.JISHUANGPIAO]['index']
                    self.addWinFanPattern(name, index)
                    return name, index                 
            else:
                if isJia or isDanDiao:
                    name = self.fanXing[self.DANPIAO]['name']
                    index = self.fanXing[self.DANPIAO]['index']
                    self.addWinFanPattern(name, index)
                    return name, index
                else:
                    name = self.fanXing[self.SHUANGPIAO]['name']
                    index = self.fanXing[self.SHUANGPIAO]['index']
                    self.addWinFanPattern(name, index)
                    return name, index
        
        if isDanDiao:
            name = self.fanXing[self.DANDIAO]['name']
            index = self.fanXing[self.DANDIAO]['index']
            self.addWinFanPattern(name, index)
            return name, index
        
        if isJia:
            name = self.fanXing[self.JIAHU]['name']
            index = self.fanXing[self.JIAHU]['index']
            self.addWinFanPattern(name, index)
            return name, index
        
        # 三七边算夹胡
        if isBian and isSanqi:
            name = self.fanXing[self.JIAHU]['name']
            index = self.fanXing[self.JIAHU]['index']
            self.addWinFanPattern(name, index)
            return name, index
            
        ftlog.debug('name: ', name, ' index: ', index)
        return name, index    
        
    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
        ftlog.debug('MBaichengOneResult.calcScore...')
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
            
            for seatId in range(self.playerCount):
                # 手里三张和宝牌一样算暗杠
                handTile = copy.deepcopy(self.playerAllTiles[seatId][MHand.TYPE_HAND])
                handtileArr = MTile.changeTilesToValueArr(handTile)
                magicTiles = self.tableTileMgr.getMagicTiles(True)
                magictile = magicTiles[0]
                if handtileArr[magictile] == 3:
                    gangFanName = self.fanXing[self.BAOZHONGGANG]['name']
                    gangFanIndex = self.fanXing[self.BAOZHONGGANG]['index']
                    fanPattern[seatId].append([gangFanName.strip(), str(gangFanIndex) + "番"])
                    break
                    
            self.results[self.KEY_FAN_PATTERN] = fanPattern
        ftlog.debug('MBaichengOneResult resultName:', self.results[self.KEY_NAME]
                    , ' scores:', self.results[self.KEY_SCORE]
                    , ' stat:', self.results[self.KEY_STAT])    
                 
    def calcGang(self):
        """计算杠的输赢"""
        ftlog.debug('MWinRuleBaicheng.calcGang...')
        # 明杠暗杠统计
        resultStat = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_GANG
        base = self.tableConfig.get(MTDefine.GANG_BASE, 0)
        if self.style == MPlayerTileGang.AN_GANG:
            self.results[self.KEY_NAME] = "暗杠"
            if base == 3:
                base = 5
            elif base == 5:
                base = 10
            resultStat[self.winSeatId].append({MOneResult.STAT_ANGANG:1})
        elif self.style == MPlayerTileGang.MING_GANG:
            self.results[self.KEY_NAME] = "明杠"
            resultStat[self.winSeatId].append({MOneResult.STAT_MINGGANG:1})
        elif self.style == MPlayerTileGang.ZFB_GANG:
            self.results[self.KEY_NAME] = "喜杠"
            resultStat[self.winSeatId].append({MOneResult.STAT_ZFBGANG:1})
        elif self.style == MPlayerTileGang.YAOJIU_GANG:
            self.results[self.KEY_NAME] = "幺九杠"
            resultStat[self.winSeatId].append({MOneResult.STAT_YAOJIUGANG:1})
        elif self.style == MPlayerTileGang.EXMao_GANG:
            self.results[self.KEY_NAME] = "补杠"
            resultStat[self.winSeatId].append({MOneResult.STAT_ExmaoGANG:1})
        elif self.style == MPlayerTileGang.BaoZhong_MING_GANG:
            self.results[self.KEY_NAME] = "宝中杠"
            resultStat[self.winSeatId].append({MOneResult.STAT_BaoZhongGANG:1})
        elif self.style == MPlayerTileGang.BaoZhong_AN_GANG:
            self.results[self.KEY_NAME] = "宝中杠"
            if base == 3:
                base = 5
            elif base == 5:
                base = 10
            resultStat[self.winSeatId].append({MOneResult.STAT_BaoZhongGANG:1})
                    
        resultStat[self.winSeatId].append({MOneResult.STAT_GANG:1})
         
        
        scores = [-base for _ in range(self.playerCount)]
        scores[self.winSeatId] = (self.playerCount - 1) * base
        
        # 包杠
        if self.tableConfig.get(MTDefine.BAOZHUANG_BAOGANG, 0):
            if self.lastSeatId != self.winSeatId:
                scores = [0 for _ in range(self.playerCount)]
                scores[self.lastSeatId] = -(self.playerCount - 1) * base  # 点杠包3家
                scores[self.winSeatId] = (self.playerCount - 1) * base
        
        ftlog.debug('MBaichengOneResult.calcGang gangType:', self.results[self.KEY_NAME], ' scores', scores)
        self.results[self.KEY_SCORE] = scores
        self.results[self.KEY_STAT] = resultStat      
        
        
if __name__ == "__main__":
    result = MBaichengOneResult()
    
    tiles = [[2, 2, 3, 4, 5, 6, 7, 8, 8, 13, 13], [[12, 13, 14]], [], [], [], []]
    ftlog.debug(result.SatisyYaoJiu(tiles, 4))
