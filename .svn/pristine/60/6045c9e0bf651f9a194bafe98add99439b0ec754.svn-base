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


class MJixiOneResult(MOneResult):
    # 特殊番型
    WUDUIHU = 'wuDuiHu'  # 三人麻将中 起手手牌无对子 直接胡 输家给赢家10分 庄家不翻倍 没有其它叠加
    TIANHU = 'tianHu'
    # 基本番型
    ZIMO = 'ziMo'
    GANGKAI = 'gangKai'
    QIANGGANG = 'qiangGang'
    JIAHU = 'jiaHu'
    DANDIAO = 'danDiao'
    QINGYISE_1 = 'qingYiSe1'  # 当出现三番番型和五番番型时 清一色算1番(叠加) 避免太大
    # 二番番型
    MOBAO = 'moBao'
    BAOBIAN = 'baoBian'  # 通宝 胡的是宝牌的时候 听牌之后直接胡 如果胡的是对倒 两头 飘 七对 就算宝边也叫通宝
    # 三番番型
    QIXIAODUI = 'qiXiaoDui'  # 七小对不算单吊 与单吊平级 二番
    PIAOHU = 'piaoHu'  # 飘胡 对对胡 都是碰
    QINGYISE = 'qingYiSe'  # 和的不是七小对 飘 特大夹 宝中宝的时候算三番 否则算一番
    TEDAJIA = 'teDaJia'
    # 五番番型
    BAOZHONGBAOJIA = 'baoZhongBaoJia'  # 和通宝一样的规则 是夹或者单吊时
    # 预留 先不做
    BIANJIASHUANG = 'bianJiaShuang'
    # 输家番型
    DIANPAO = 'dianPao'
    DIANPAOBAOZHUANG = 'dianPaoBaoZhuang'
    # 闭门可配置 默认不算番
    BIMEN = 'biMen'
    
    # 最大分数限制
    MAX_SCORE_LIMIT = 128
        
    def __init__(self, tilePatternChecker, playerCount):
        super(MJixiOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = {
            self.WUDUIHU: {"name":"无对胡 ", "index": 0},
            self.TIANHU: {"name":"天胡 ", "index": 6},
            self.ZIMO: {"name":"自摸 ", "index": 1},
            self.GANGKAI: {"name":"杠上开花 ", "index":1},
            self.QIANGGANG: {"name":"抢杠胡 ", "index":1},
            self.JIAHU: {"name": "夹胡 ", "index": 1},
            self.DANDIAO: {"name": "单吊 ", "index": 1},
            self.QINGYISE_1: {"name": "清一色 ", "index": 1},
            self.MOBAO: {"name": "摸宝 ", "index": 2},
            self.BAOBIAN: {"name": "通宝 ", "index": 2},
            self.QIXIAODUI: {"name": "七对 ", "index": 3},
            self.PIAOHU: {"name": "飘 ", "index": 3},
            self.QINGYISE: {"name": "清一色 ", "index": 2},
            self.TEDAJIA: {"name": "特大夹 ", "index": 3},
            self.BAOZHONGBAOJIA: {"name": "宝中宝 ", "index": 5},
            # 输家番型 
            self.DIANPAO: {"name": "点炮 ", "index": 1},  # winMode展示
            self.DIANPAOBAOZHUANG: {"name": "包庄 ", "index": 1},  # winMode展示
            self.BIMEN: {"name": "闭门 ", "index": 1},
        }
        
    @property
    def fanXing(self):
        return self.__fan_xing
        
    def isWinTile(self):
        """获胜牌在winNodes中"""
        ftlog.debug('MJixiOneResult.isWinTile winTile:', self.winTile
            , ' winNodes:', self.winNodes)
        
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                return True
        
        return False
    
    def isMagicTile(self):
        """是不是宝牌"""
        magics = self.tableTileMgr.getMagicTiles(True)
        ftlog.debug('MJixiOneResult.isMagicTile winTile:', self.winTile
            , ' magicTiles:', magics)
        
        return self.winTile in magics
            
    
    def isDanDiao(self):
        
        ftlog.debug('MJixiOneResult.isDanDiao self.winNodes:', self.winNodes)
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MJixiOneResult.isDanDiao winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) != 2:
                        continue
                    
                    if (self.winTile in p) and p[0] == p[1]:
                        ftlog.debug('MJixiOneResult.isDanDiao self.winTile:', self.winTile, 'p:', p)
                        return True
        
        # 宝牌情况时判断单吊
        if self.isMagicTile():
            for wn in self.winNodes:
                winTile = wn['winTile']
                patterns = wn['pattern'] 
                ftlog.debug('MJixiOneResult.isDanDiao winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) != 2:
                        continue
                    
                    if (winTile in p) and p[0] == p[1]:
                        ftlog.debug('MJixiOneResult.isDanDiao isMagicTile winTile:', winTile, 'p:', p)
                        return True
                    
        return False 
    
    
    # 没有吃 没有碰 没有杠
    def isQiDui(self, isMagic):
        ftlog.debug('jixi_one_result.isQiDui winSeatId:', self.winSeatId
                    , ' tiles:', self.playerAllTiles[self.winSeatId])
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        if len(handTile) % 2 > 0:
            handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])
        ftlog.debug('jixi_one_result.isQiDui adjust tiles:', handTile)
        
        if isMagic:    
            magics = self.tableTileMgr.getMagicTiles(True)
            qiduiResult, _ = MWin.isQiDui(handTile, magics)
        else:
            qiduiResult, _ = MWin.isQiDui(handTile)
        return qiduiResult
    
    # 胡牌的番型 手牌 没有吃 没有粘 至少有一个刻
    def isPiao(self):
        playerChiTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_CHI]
        if len(playerChiTiles) > 0:
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
    
    def isQingYiSe(self):
        if self.colorState[self.winSeatId] == 1:
            return True
        
        if self.isMagicTile():
            tileArr = MTile.changeTilesToValueArr(MHand.copyAllTilesToListButHu(self.playerAllTiles[self.winSeatId]))
            tempCountColor = MTile.getColorCount(tileArr)
            if tempCountColor == 1:
                return True
            
        return False
    
    def isJia(self):
        """是否夹牌"""
        ftlog.debug('MJixiOneResult.isJia')
        
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MJixiOneResult.isJia winTile:', self.winTile, ' winPatterns:', patterns)
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
    
    # 胡牌是别人的碰牌或者自己的碰牌以及手牌中的刻牌且手牌中的刻牌不能作为他用(34445)
    def isTeDaJia(self, isJia, isBian):
            
        ftlog.debug('MJixiOneResult.isTeDaJia isJia:', isJia, 'isBian:', isBian)
        
        # 不是夹也不是37边，肯定不算特大夹    
        if not isJia:
            bianMulti = self.tableConfig.get(MTDefine.BIAN_MULTI, 0)
            if not (isBian and self.isSanQi() and bianMulti):
                return False
        
        realWinTile = self.winTile
        if self.isMagicTile():  # (摸宝)胡牌的情况
            for wn in self.winNodes:
                realWinTile = wn['winTile']
                break

        ftlog.debug('MJixiOneResult.isTeDaJia self.winTile:', self.winTile, 'realWinTile:', realWinTile)
                                 
        # 他人的碰牌
        isInOtherPeng = False
        for seatId in range(self.playerCount):
            if seatId != self.winSeatId:
                playerPengTiles = self.playerAllTiles[seatId][MHand.TYPE_PENG]
                for pattern in playerPengTiles:
                    if pattern[0] == realWinTile:
                        isInOtherPeng = True
                        break;
        
        isInSelfKe = False
        playerPengTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_PENG]
        for pattern in playerPengTiles:
            if pattern[0] == realWinTile:
                isInSelfKe = True
                break
            
        # 自己的手牌
        if not isInSelfKe:
            playerHandTiles = self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND]
            winTileInHandCount = 0
            for tile in playerHandTiles:
                if tile == realWinTile:
                    winTileInHandCount = winTileInHandCount + 1
                    if winTileInHandCount == 3:
                        isInSelfKe = True
                        break
            
        if not (isInSelfKe or isInOtherPeng):
            ftlog.debug('MJixiOneResult.isTaDaJia winTile:', realWinTile, 'isInSelfKe:', isInSelfKe, 'isInOtherPeng:', isInOtherPeng)
            return False
        
        return True
    
    def isSanQi(self, winTile=None):
        
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MJixiOneResult.isBian winTile:', self.winTile, ' winPatterns:', patterns)
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
                ftlog.debug('MJixiOneResult.isBian winTile:', self.winTile, ' winPatterns:', patterns)
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
        
    def calcWin(self):
        """
        鸡西算番规则：
        """
        scoreBase = self.tableConfig.get(MTDefine.WIN_BASE, 1)
        ftlog.debug('MJixiOneResult.calcWin scoreBase:', scoreBase)
        self.results['type'] = MOneResult.KEY_TYPE_NAME_HU
        
        name = ''
        index = 0
        score = [0 for _ in range(self.playerCount)]
        fanPattern = [[] for _ in range(self.playerCount)]
        winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
        # 在和牌时统计自摸，点炮，最大番数
        resultStat = [[] for _ in range(self.playerCount)]
        isBaoPei = False  # 是否包赔,如果是包赔 那么兑奖也要包赔
        
        resultStat[self.winSeatId].append({MOneResult.STAT_WIN:1})
        # 正常和牌
        if not self.wuDuiHu:
            isZiMo = (self.lastSeatId == self.winSeatId)
            if isZiMo:
                resultStat[self.winSeatId].append({MOneResult.STAT_ZIMO:1})
            isJia = self.isJia()
            isBian = self.isBian()
            isDanDiao = self.isDanDiao()            
            isMagic = self.isMagicTile()
            isQiDui = self.isQiDui(isMagic)
            isPiao = self.isPiao()
            isQingYiSe = self.isQingYiSe()
            isTeDaJia = self.isTeDaJia(isJia, isBian)
            isSanQi = self.isSanQi()
            ftlog.debug('MJixiOneResult.calcWin isJia:', isJia
                    , ' isBian:', isBian
                    , ' isDanDiao', isDanDiao
                    , ' isQiDui:', isQiDui
                    , ' isPiao:', isPiao
                    , ' isQingYiSe:', isQingYiSe
                    , ' isSanQi:', isSanQi
                    )
            
            self.clearWinFanPattern()
            
            
            # 高级番型处理(清一色 通宝 宝中宝)
            isBaoZhongBao = False
            isTongBao = False
            if self.magicAfertTing:  # 听牌之后是宝牌 直接和牌
                # 宝中宝 宝夹
                bianMulti = self.tableConfig.get(MTDefine.BIAN_MULTI, 0)
                if (isBian and isSanQi and bianMulti and len(self.winNodes) == 1):
                    isBaoZhongBao = True

                elif isJia:
                    # 如果是摸的宝是winNodes里面的夹，就是宝中宝，否则是宝边
                    magicTileInJia = False
                    for wn in self.winNodes:
                        patterns = wn['pattern'] 
                        for p in patterns:
                            if len(p) == 2:
                                continue          
                            if p[0] == p[1]:
                                continue
                            
                            if (self.winTile in p) and (p.index(self.winTile)) == 1:
                                magicTileInJia = True
                                
                    if magicTileInJia:
                        isBaoZhongBao = True
                    else:
                        isTongBao = True
                        
                elif isDanDiao:
                    # 如果是摸的宝是winNodes里面的对子，就是宝中宝，否则是宝边
                    magicTileInPair = False
                    for wn in self.winNodes:
                        patterns = wn['pattern'] 
                        for p in patterns:
                            if len(p) != 2:
                                continue
                    
                            if p[0] == p[1] and (self.winTile in p):
                                magicTileInPair = True
                                
                    if magicTileInPair:
                        isBaoZhongBao = True
                    else:
                        isTongBao = True
                    
                # 通宝 宝边
                else: 
                    ftlog.debug('MJixiOneResult.calcWin  isTongBao = True:')
                    isTongBao = True
             
            if isBaoZhongBao:
                nameBaoZhongBao = self.fanXing[self.BAOZHONGBAOJIA]['name']
                indexBaoZhongBao = self.fanXing[self.BAOZHONGBAOJIA]['index']
                self.addWinFanPattern(nameBaoZhongBao, indexBaoZhongBao)
                index += self.fanXing[self.BAOZHONGBAOJIA]['index']
                ftlog.debug('MJixiOneResult.calcWin MagicAfertTing name:', nameBaoZhongBao, ' index:', indexBaoZhongBao)
            elif isTongBao:
                nameTongBao = self.fanXing[self.BAOBIAN]['name']
                indexTongBao = self.fanXing[self.BAOBIAN]['index']
                self.addWinFanPattern(nameTongBao, indexTongBao)
                index += self.fanXing[self.BAOBIAN]['index']
                # 计算基本番型
                name, tempindex = self.calcBaseFan(isTeDaJia, False, False, False, isQiDui, isPiao)
                index += tempindex
                ftlog.debug('MJixiOneResult.calcWin BaseFan name:', name, ' index:', index)
            elif isZiMo:  # 自摸番型处理(自摸 摸宝[2番] 杠开 )
                if isMagic:
                    index += self.fanXing[self.MOBAO]['index']
                    self.addWinFanPattern(self.fanXing[self.MOBAO]['name'], self.fanXing[self.MOBAO]['index'])
                    resultStat[self.winSeatId].append({MOneResult.STAT_MOBAO:1})
                else:
                    index += self.fanXing[self.ZIMO]['index']
                
                # 计算基本番型
                name, tempindex = self.calcBaseFan(isTeDaJia, isJia, isBian, isDanDiao, isQiDui, isPiao)
                index += tempindex
                ftlog.debug('MJixiOneResult.calcWin ZiMoFan index:', index)
            elif isZiMo == False:  # 点炮胡             
                # 计算基本番型
                name, tempindex = self.calcBaseFan(isTeDaJia, isJia, isBian, isDanDiao, isQiDui, isPiao)
                index += tempindex
                ftlog.debug('MJixiOneResult.calcWin 点炮胡 index:', index)
                    
            if isQingYiSe:
                if isTeDaJia or isQiDui or isPiao or isBaoZhongBao:
                    nameQingYiSe = self.fanXing[self.QINGYISE_1]['name']
                    indexQingYiSe = self.fanXing[self.QINGYISE_1]['index']
                    self.addWinFanPattern(nameQingYiSe, indexQingYiSe)
                    index += self.fanXing[self.QINGYISE_1]['index']
                else:
                    nameQingYiSe = self.fanXing[self.QINGYISE]['name']
                    indexQingYiSe = self.fanXing[self.QINGYISE]['index']
                    self.addWinFanPattern(nameQingYiSe, indexQingYiSe)
                    index += self.fanXing[self.QINGYISE]['index']
                ftlog.debug('MJixiOneResult.calcWin QingYiSeFan name:', nameQingYiSe, ' index:', indexQingYiSe)
                
            if self.bankerSeatId == self.winSeatId:
                index += 1
                ftlog.debug('MJixiOneResult.calcWin name:', name, ' index:', index, ' type:', type
                        , ' bankerSeatId:', self.bankerSeatId
                        , ' winSeatId:', self.winSeatId)
                
            scoreIndex = self.tableConfig.get(MTDefine.FAN_LIST, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            ftlog.debug('MJixiOneResult.calcWin scoreIndex:', scoreIndex)
            
            biMenFanConfig = self.tableConfig.get(MTDefine.BI_MEN_FAN, 0)
            # 当前局番型处理
            # 输赢模式 输家番型统计
            for seatId in range(self.playerCount):
                if seatId == self.winSeatId:
                    winModeValue = MOneResult.WIN_MODE_PINGHU
                    # 自摸
                    if self.lastSeatId == self.winSeatId:
                        winModeValue = MOneResult.WIN_MODE_ZIMO
                    if isMagic and (not self.magicAfertTing):
                        winModeValue = MOneResult.WIN_MODE_mobao
                    if isBaoZhongBao:
                        winModeValue = MOneResult.WIN_MODE_baozhongbao
                    if self.magicAfertTing:
                        if self.tableConfig.get(MTDefine.DUI_BAO, 0) == 1:
                            winModeValue = MOneResult.WIN_MODE_LOUHU
                    if self.gangKai:
                        winModeValue = MOneResult.WIN_MODE_GANGKAI
                        self.addWinFanPattern(self.fanXing[self.GANGKAI]['name'], self.fanXing[self.GANGKAI]['index'])
                    if self.qiangGang:
                        winModeValue = MOneResult.WIN_MODE_QIANGGANGHU
                        self.addWinFanPattern(self.fanXing[self.QIANGGANG]['name'], self.fanXing[self.QIANGGANG]['index'])
                    if self.daFeng:
                        winModeValue = MOneResult.WIN_MODE_guadafeng
                        


                    winMode[seatId] = winModeValue
                    fanPattern[self.winSeatId] = self.winFanPattern
                elif seatId == self.lastSeatId:
                    winModeValue = MOneResult.WIN_MODE_DIANPAO
                    winMode[seatId] = winModeValue
                    resultStat[seatId].append({MOneResult.STAT_DIANPAO:1})
                    fanPattern[seatId] = []
                    # 点炮包庄
                    if self.tingState[seatId] == 0:
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
            
            if not self.tianHu:    
                score = [index for _ in range(self.playerCount)]
                if self.lastSeatId != self.winSeatId:
                    if self.tingState[self.lastSeatId]:
                        ftlog.debug('MJixiOneResult.calcWin dianpao index is zero becouse is Ting')
                    else:
                        # 改成点炮都不翻倍
                        # score[self.lastSeatId] += 1
                        ftlog.debug('MJixiOneResult.calcWin dianpao score:', score)
                    
                if self.bankerSeatId != self.winSeatId:
                    score[self.bankerSeatId] += 1
                    ftlog.debug('MJixiOneResult.calcWin zhuangjia double score:', score
                        , ' bankerSeatId:', self.bankerSeatId
                        , ' winSeatId:', self.winSeatId)
                    
                for seatId in range(len(self.menState)):
                    if biMenFanConfig and self.menState[seatId] == 1 and seatId != self.winSeatId:
                        score[seatId] += 1
                        ftlog.debug('MJixiOneResult.calcWin menqing double score:', score
                                   , ' menState:', self.menState)
                    
                winScore = 0
                for seatId in range(len(score)):
                    if seatId != self.winSeatId:
                        newIndex = score[seatId]
                        score[seatId] = -scoreIndex[newIndex]
                        winScore += scoreIndex[newIndex]
                score[self.winSeatId] = winScore
                ftlog.debug('MJixiOneResult.calcWin score before baopei:', score)
                
                if self.lastSeatId != self.winSeatId:
                    if self.tingState[self.lastSeatId] == 0:
                        isBaoPei = True
                        # 包赔
                        for seatId in range(len(score)):
                            if seatId != self.winSeatId and seatId != self.lastSeatId:
                                s = score[seatId]
                                score[seatId] = 0
                                score[self.lastSeatId] += s
                        ftlog.debug('MJixiOneResult.calcWin dianpaobaozhuang score:', score
                            , ' lastSeatId:', self.lastSeatId
                            , ' winSeatId:', self.winSeatId
                            , ' tingState:', self.tingState)
            else:
                index = self.fanXing[self.TIANHU]['index']
                score = [index for _ in range(self.playerCount)]
                scoreIndex = self.tableConfig.get(MTDefine.FAN_LIST, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                ftlog.debug('MJixiOneResult.calcWin scoreIndex:', scoreIndex)
                winScore = 0
                for seatId in range(len(score)):
                    if seatId != self.winSeatId:
                        newIndex = score[seatId]
                        score[seatId] = -scoreIndex[newIndex]
                        winScore += scoreIndex[newIndex]
                score[self.winSeatId] = winScore
                # fanPattern = [[] for _ in range(self.playerCount)]
                winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
                winMode[self.winSeatId] = MOneResult.WIN_MODE_TIANHU
                resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN:index})
        else:
            name = self.fanXing[self.WUDUIHU]['name']
            index = self.fanXing[self.WUDUIHU]['index']
            self.addWinFanPattern(name, index)
            fanPattern[self.winSeatId] = self.winFanPattern
            score = [10 for _ in range(self.playerCount)]
            winScore = 0
            for seatId in range(len(score)):
                if seatId != self.winSeatId:
                    loseScore = score[seatId]
                    score[seatId] = -loseScore
                    winScore += loseScore
            score[self.winSeatId] = winScore
            # fanPattern = [[] for _ in range(self.playerCount)]
            winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
            winMode[self.winSeatId] = MOneResult.WIN_MODE_WUDUIHU
                
        # 最高128分封顶
        for seatId in range(len(score)):
            if seatId != self.winSeatId:
                if abs(score[seatId]) > self.MAX_SCORE_LIMIT:
                    ftlog.debug('MJixiOneResult.calcWin limit max score :', score[seatId]
                    , ' seatId:', seatId)
                    score[self.winSeatId] = score[self.winSeatId] - (abs(score[seatId]) - self.MAX_SCORE_LIMIT)
                    score[seatId] = -self.MAX_SCORE_LIMIT
                    
        # 兑奖
        awardInfos = []
        awardScores = [0 for _ in range(self.playerCount)]
        awardTiles = self.awardTiles
        if len(awardTiles) == 0:
            ftlog.debug('MJixiOneResult.calcWin award tile is zero')
        else:
            awardScore = 0
            for awardTile in awardTiles:
                tileValue = MTile.getValue(awardTile)
                realScore = 0
                if tileValue == 1 or awardTile == MTile.TILE_HONG_ZHONG:
                    realScore = 10
                    awardScore += realScore
                else:
                    realScore = tileValue
                    awardScore += realScore
                awardInfo = {'awardTile':awardTile, 'awardScore':realScore}
                awardInfos.append(awardInfo)
            
            for seatId in range(len(score)):
                if seatId != self.winSeatId:
                    if isBaoPei:  # 兑奖包赔处理
                        score[self.lastSeatId] -= awardScore
                        awardScores[self.lastSeatId] -= awardScore
                    else:
                        score[seatId] -= awardScore
                        awardScores[seatId] = -awardScore
                    score[self.winSeatId] += awardScore
                    awardScores[self.winSeatId] += awardScore
                    
        # 单局最佳统计(分数)
        resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN:score[self.winSeatId]})
        
        self.results[self.KEY_TYPE] = '和牌'
        self.results[self.KEY_NAME] = name
        ftlog.debug('MJixiOneResult.calcWin result score:', score)
        self.results[self.KEY_SCORE] = score
        ftlog.debug('MJixiOneResult.calcWin result winMode:', winMode)
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        ftlog.debug('MJixiOneResult.calcWin result fanPattern:', fanPattern)
        self.results[self.KEY_FAN_PATTERN] = fanPattern
        self.results[self.KEY_AWARD_INFO] = awardInfos
        self.results[self.KEY_AWARD_SCORE] = awardScores
        
    def calcBaseFan(self, isTeDaJia, isJia, isBian, isDanDiao, isQiDui, isPiao):
        name = ''
        index = 0
            
        if isTeDaJia:
            name = self.fanXing[self.TEDAJIA]['name']
            index = self.fanXing[self.TEDAJIA]['index']
            self.addWinFanPattern(name, index)
            return name, index
                
        if isPiao:
            name = self.fanXing[self.PIAOHU]['name']
            index = self.fanXing[self.PIAOHU]['index']
            self.addWinFanPattern(name, index)
            return name, index
        
        if isQiDui:
            name = self.fanXing[self.QIXIAODUI]['name']
            index = self.fanXing[self.QIXIAODUI]['index']
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
        bianMulti = self.tableConfig.get(MTDefine.BIAN_MULTI, 0)
        if isBian and self.isSanQi() and bianMulti:
            name = self.fanXing[self.JIAHU]['name']
            index = self.fanXing[self.JIAHU]['index']
            self.addWinFanPattern(name, index)
            return name, index
            
        ftlog.debug('name: ', name, ' index: ', index)
        return name, index    
        
    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
        ftlog.debug('jixi_one_result.calcScore...')
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
        ftlog.debug('jixi_one_result resultName:', self.results[self.KEY_NAME]
                    , ' scores:', self.results[self.KEY_SCORE]
                    , ' stat:', self.results[self.KEY_STAT])    
            
                 
    def calcGang(self):
        """计算杠的输赢"""
        ftlog.debug('jixi_one_result.calcGang...')
        # 明杠暗杠统计
        resultStat = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_GANG
        base = self.tableConfig.get(MTDefine.GANG_BASE, 0)
        if self.style == MPlayerTileGang.AN_GANG:
            self.results[self.KEY_NAME] = "暗杠"
            base *= 2
            resultStat[self.winSeatId].append({MOneResult.STAT_ANGANG:1})
        else:
            self.results[self.KEY_NAME] = "明杠"
            resultStat[self.winSeatId].append({MOneResult.STAT_MINGGANG:1})
        resultStat[self.winSeatId].append({MOneResult.STAT_GANG:1})
         
        scores = [-base for _ in range(self.playerCount)]
        scores[self.winSeatId] = (self.playerCount - 1) * base
        
        ftlog.debug('MOneResult.calcGang gangType:', self.results[self.KEY_NAME], ' scores', scores)
        self.results[self.KEY_SCORE] = scores
        self.results[self.KEY_STAT] = resultStat      
        
        
if __name__ == "__main__":
    result = MJixiOneResult()
    result.setTableConfig({})
    result.calcDianPaoFan(True, False, True, False)
