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


class MMudanjiangOneResult(MOneResult):
    ZIMO = 'ziMo'
    GANGKAI = 'gangKai'
    QIANGGANG = 'qiangGang'
    HONGZHONGBAO = 'hongZhongBao'
    BAOBIAN = 'baoBian'
    GUADAFENG = 'guaDaFeng'
    BAOZHONGBAOJIA = 'baoZhongBaoJia'
    BAOZHONGBAODAFENG = 'baoZhongBaoDaFeng'
    JIAHU = 'jiaHu'
    BIANHU = 'bianZhang'
    MOBAO = 'moBao'
    BIANJIASHUANG = 'bianJiaShuang'
    DANDIAO = 'danDiao'
    DAKOU = 'daKou'
    # 输家番型
    DIANPAO = 'dianPao'
    DIANPAOBAOZHUANG = 'dianPaoBaoZhuang'
    BIMEN = 'biMen'
    BAOPAO = 'baoPao'
        
    def __init__(self, tilePatternChecker, playerCount):
        super(MMudanjiangOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = {
            self.ZIMO: {"name":"自摸 ", "index": 1},
            self.DAKOU: {"name":"大扣 ", "index":1},
            self.GANGKAI: {"name":"杠上开花 ", "index":1},
            self.QIANGGANG: {"name":"抢杠胡 ", "index":1},
            self.HONGZHONGBAO: {"name": "红中满天飞 ", "index":2},
            self.BAOBIAN: {"name": "宝边 ", "index": 3},
            self.GUADAFENG: {"name": "刮大风 ", "index": 2},
            self.BAOZHONGBAOJIA: {"name": "宝中宝 ", "index": 4},
            self.BAOZHONGBAODAFENG: {"name": "宝中宝 ", "index": 3},
            self.JIAHU: {"name": "夹胡 ", "index": 1},
            self.BIANHU: {"name": "边胡 ", "index": 1},
            self.MOBAO: {"name": "摸宝 ", "index": 2},
            self.DANDIAO: {"name": "单吊 ", "index": 1},
            # 输家番型 
            self.DIANPAO: {"name": "点炮 ", "index": 1},  # winMode展示
            self.DIANPAOBAOZHUANG: {"name": "包庄 ", "index": 1},  # winMode展示
            self.BIMEN: {"name": "闭门 ", "index": 1},
            self.BAOPAO: {"name": "宝炮 ", "index": 1},
        }
        
    @property
    def fanXing(self):
        return self.__fan_xing
        
    def isWinTile(self):
        """获胜牌在winNodes中，而且是宝牌"""
        ftlog.debug('MMudanjiangOneResult.isWinTile winTile:', self.winTile
            , ' winNodes:', self.winNodes)
        
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                return True
        
        return False
    
    def isMagicTile(self):
        """是不是宝牌"""
        if not self.magics:
            return False
        
        ftlog.debug('MMudanjiangOneResult.isMagicTile winTile:', self.winTile
            , ' magicTiles:', self.magics)
        return self.winTile in self.magics
    
    # 胡的就是宝牌
    def isHuMagicTile(self):
        magics = self.tableTileMgr.getMagicTiles(True)
        for wn in self.winNodes:
            if wn['winTile'] in magics:
                return True
        return False
        
    
    def isHongZhong(self):
        return self.winTile == MTile.TILE_HONG_ZHONG
            
    def isDaKou(self):
        return self.menState[self.winSeatId] == 1
    
    def isDaKouLoose(self, seatId):
        ftlog.debug('MMudanjiangOneResult.isDaKouLoose seatId:', seatId
                    , ' menState:', self.menState
                    , ' tingState:', self.tingState)
        return self.tingState[seatId] and self.menState[seatId]
    
    def isDanDiao(self):
        if len(self.winNodes) > 1:
            return False
        
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MMudanjiangOneResult.isDanDiao winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) != 2:
                        continue
                    
                    if (self.winTile in p) and p[0] == p[1]:
                        return True
        
        # 宝牌情况时判断单吊
        hongZongBaoConfig = self.tableConfig.get(MTDefine.HONG_ZHONG_BAO, 0)
        if self.isMagicTile() or (self.isHongZhong() and hongZongBaoConfig) or self.daFeng:
            for wn in self.winNodes:
                winTile = wn['winTile']
                patterns = wn['pattern'] 
                ftlog.debug('MMudanjiangOneResult.isDanDiao winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) != 2:
                        continue
                    
                    if (winTile in p) and p[0] == p[1]:
                        return True
                    
        return False 
    
    def isJia(self):
        """是否夹牌"""
        if len(self.winNodes) > 1:
            return False
        
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MMudanjiangOneResult.isJia winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) == 2:
                        continue
                    
                    if p[0] == p[1]:
                        continue
                    
                    if (self.winTile in p) and (p.index(self.winTile)) == 1:
                        return True
                    
        # 宝牌和红中宝刮大风的情况处理(用真实的胡牌来判断夹)
        hongZongBaoConfig = self.tableConfig.get(MTDefine.HONG_ZHONG_BAO, 0)
        ftlog.debug('MMudanjiangOneResult.isJia checkMagic, isMagicTile:', self.isMagicTile()
                    , ' isHongZhong:', self.isHongZhong()
                    , ' hongZongBaoConfig:', hongZongBaoConfig
                    , ' daFeng:', self.daFeng
                    , ' magicAfertTing:', self.magicAfertTing)
        if self.isMagicTile() or (self.isHongZhong() and hongZongBaoConfig) or self.daFeng or self.magicAfertTing:
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
    
    def isDaFeng(self, isMagic):
        """只补充判断有三种宝牌的情况"""
        if not isMagic:
            return self.daFeng
        
        if self.isHongZhong():
            return self.daFeng
        
        handTiles = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        if len(handTiles) % 3 != 2:
            handTiles.append(self.winTile)
        
        tileArr = MTile.changeTilesToValueArr(handTiles)
        if tileArr[self.winTile] == 4:
            # 测试去掉胡牌的刻子之后是否仍旧能胡牌
            for _ in range(3):
                handTiles.remove(self.winTile)
            result, _ = MWin.isHu(handTiles)
            if result:
                self.setDaFeng(True)
                
        return self.daFeng
    
    def isBian(self):
        """是否夹牌"""
        for wn in self.winNodes:
            if wn['winTile'] == self.winTile:
                patterns = wn['pattern']
                ftlog.debug('MMudanjiangOneResult.isBian winTile:', self.winTile, ' winPatterns:', patterns)
                for p in patterns:
                    if len(p) == 2:
                        continue
                    
                    if p[0] == p[1]:
                        continue
                    
                    # 三七边
                    if (self.winTile in p) \
                        and (p.index(self.winTile) == 0) \
                        and (MTile.getValue(p[1]) == 8) \
                        and (MTile.getValue(p[2]) == 9):
                        ftlog.debug('MMudanjiangOneResult.isBian winTile:', self.winTile, ' winPatterns:', patterns, ' 7 bian')
                        return True
                    if (self.winTile in p) \
                        and (p.index(self.winTile) == 2) \
                        and (MTile.getValue(p[0]) == 1) \
                        and (MTile.getValue(p[1]) == 2):
                        ftlog.debug('MMudanjiangOneResult.isBian winTile:', self.winTile, ' winPatterns:', patterns, ' 3 bian')
                        return True
        
        # 宝牌情况处理
        hongZongBaoConfig = self.tableConfig.get(MTDefine.HONG_ZHONG_BAO, 0)
        ftlog.debug('MMudanjiangOneResult.isBian checkMagic, isMagicTile:', self.isMagicTile()
                    , ' isHongZhong:', self.isHongZhong()
                    , ' hongZongBaoConfig:', hongZongBaoConfig
                    , ' daFeng:', self.daFeng
                    , ' magicAfertTing:', self.magicAfertTing)
        if self.isMagicTile() or (self.isHongZhong() and hongZongBaoConfig) or self.daFeng or self.magicAfertTing:
            for wn in self.winNodes:
                winTile = wn['winTile']
                patterns = wn['pattern']
                for p in patterns:
                    if len(p) == 2:
                        continue
                    
                    if p[0] == p[1]:
                        continue
                    
                    # 三七边
                    if (winTile in p) \
                        and (p.index(winTile) == 0) \
                        and (MTile.getValue(p[1]) == 8) \
                        and (MTile.getValue(p[2]) == 9):
                        ftlog.debug('MMudanjiangOneResult.isBian winTile:', self.winTile, ' winPatterns:', patterns, ' 7 bian')
                        return True
                    if (winTile in p) \
                        and (p.index(winTile) == 2) \
                        and (MTile.getValue(p[0]) == 1) \
                        and (MTile.getValue(p[1]) == 2):
                        ftlog.debug('MMudanjiangOneResult.isBian winTile:', self.winTile, ' winPatterns:', patterns, ' 3 bian')
                        return True
        
        return False
        
    def calcWin(self):
        """
        牡丹江算番规则：
        1）合并一番
        自摸，特殊情况下的自摸可以有杠开/红中宝两种叫法
            1.1杠开
            1.2红中宝 自己摸到红中
            1.4刮大风 上听后摸到自己的碰牌或刻牌且不是宝牌，宝牌算宝中宝
            1.5宝中宝1 3番 宝牌 夹牌
            1.6宝中宝2 3番 刮大风+宝牌
        2）自摸点炮都算
        2.1夹胡
        2.2三七边
        2.3摸宝
        1.3宝边，2番，自摸的要胡的牌刚好是宝牌
        2.4边夹双 2倍数
        大扣
        
        """
        self.results['type'] = MOneResult.KEY_TYPE_NAME_HU
        
        # 在和牌时统计自摸，点炮，最大番数
        resultStat = [[] for _ in range(self.playerCount)]
        
        isZiMo = (self.lastSeatId == self.winSeatId)
        if isZiMo:
            resultStat[self.lastSeatId].append({MOneResult.STAT_ZIMO:1})
        isLikeZiMo = False
        if (self.lastSeatId != self.winSeatId) and (self.tingState[self.lastSeatId] == 0):
            isLikeZiMo = True
            
        resultStat[self.winSeatId].append({MOneResult.STAT_WIN:1})
        isJia = self.isJia()
        isBian = self.isBian()
        isDanDiao = self.isDanDiao()
        isMagic = self.isMagicTile()
        isDaKou = self.isDaKou()
        ftlog.debug('MMudanjiangOneResult.calcWin isJia:', isJia
                , ' isBian:', isBian
                , ' isDanDiao', isDanDiao
                , ' isDafeng', self.daFeng
                , ' isDaKou', isDaKou
                , ' isMagic:', isMagic
                , ' isZiMo:', isZiMo
                , ' isLikeZiMo:', isLikeZiMo
                , ' menState:', self.menState
                , ' tingState:', self.tingState)
        
        self.clearWinFanPattern()
        # 计算基本番型(只有单吊 夹胡 三七边)
        name, index = self.calcDianPaoFan(isJia, isBian, isDanDiao)
        ftlog.info('MMudanjiangOneResult.calcWin after calcDianPaoFan name:', name, ' index:', index)
        
        # 计算自摸高级番型 都和自摸有关(不包含自摸 杠开 抢杠胡 摸宝 红中宝)
        if isZiMo or isLikeZiMo:
            name2 = ''
            index2 = 1
            if isLikeZiMo and (self.tableConfig.get(MTDefine.DUI_BAO, 0) == 0):
                # 点黑炮的时候，如果不选择对宝，只算自摸
                ftlog.info('MMudanjiangOneResult.calcWin isLikeZimo, justCalcZiMO name2:', name2, ' index2:', index2)
                name2 = self.fanXing[self.ZIMO]['name']
                index2 = self.fanXing[self.ZIMO]['index']
            else:
                name2, index2 = self.calcZiMoAdvFan((isZiMo or isLikeZiMo), isDanDiao, self.daFeng, self.baoZhongBao, isMagic, isJia, isBian)
                
            ftlog.info('MMudanjiangOneResult.calcWin after calcZiMoAdvFan name2:', name2, ' index2:', index2)
            # 只是自摸 没有高级番型
            if name2 == self.fanXing[self.ZIMO]['name']:
                # 在基础番型上增加自摸倍数
                ftlog.info('MMudanjiangOneResult.calcWin after calcZiMoAdvFan zimo name2:', name2, ' index2:', index2)
                hongZongBaoConfig = self.tableConfig.get(MTDefine.HONG_ZHONG_BAO, 0)
                if isMagic and isZiMo:
                    index += self.fanXing[self.MOBAO]['index']
                    resultStat[self.lastSeatId].append({MOneResult.STAT_MOBAO:1})
                elif self.isHongZhong() and hongZongBaoConfig and isZiMo:
                    index += self.fanXing[self.HONGZHONGBAO]['index']
                else:
                    index += index2
            # 自摸相关的特殊番型 直接覆盖基本番型
            else:
                ftlog.info('MMudanjiangOneResult.calcWin after calcZiMoAdvFan not zimo name2:', name2, ' index2:', index2)
                name = name2
                index = index2
                self.clearWinFanPattern()
                self.addWinFanPattern(name, index)  
                
        ftlog.info('MMudanjiangOneResult.calcWin after calcZimo name:', name, ' index:', index)  
        
        if name == self.fanXing[self.GUADAFENG]['name']:
            # 刮大风的情况下判断是不是夹
            if isJia or (isBian and self.tableConfig.get(MTDefine.BIAN_MULTI, 0)):
                jianame = self.fanXing[self.JIAHU]['name']
                jiaindex = self.fanXing[self.JIAHU]['index']
                self.addWinFanPattern(jianame, jiaindex)
                index += 1
                
        ftlog.info('MMudanjiangOneResult.calcWin after calcDafeng name:', name, ' index:', index) 
        
        # daKouConfig = self.tableConfig.get(MTDefine.DA_KOU, 0)
        daKouConfig = 1
        if self.isDaKou() and daKouConfig:
            dakouname = self.fanXing[self.DAKOU]['name']
            dakouindex = self.fanXing[self.DAKOU]['index']
            self.addWinFanPattern(dakouname, dakouindex)
            index += 1
               
        ftlog.info('MMudanjiangOneResult.calcWin after calcDaKou name:', name, ' index:', index)
            
        scoreBase = self.tableConfig.get(MTDefine.WIN_BASE, 1)
        ftlog.debug('MMudanjiangOneResult.calcWin scoreBase:', scoreBase)
        scoreIndex = []
        if scoreBase == 5:
            scoreIndex = [2, 5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560]
        else:
            scoreIndex = self.tableConfig.get(MTDefine.FAN_LIST, [1, 2, 4, 8, 16, 32, 64, 128, 256])
            
        ftlog.info('MMudanjiangOneResult.calcWin scoreIndex:', scoreIndex)
        
        # 当前局番型处理
        fanPattern = [[] for _ in range(self.playerCount)]
        winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
        # 输赢模式 输家番型统计
        for seatId in range(self.playerCount):
            if seatId == self.winSeatId:
                winModeValue = MOneResult.WIN_MODE_PINGHU
                # 自摸
                if self.lastSeatId == self.winSeatId:
                    winModeValue = MOneResult.WIN_MODE_ZIMO
                    
                    if self.baoZhongBao:
                        winModeValue = MOneResult.WIN_MODE_baozhongbao
                    if self.magicAfertTing:
                        if self.tableConfig.get(MTDefine.DUI_BAO, 0) == 1:
                            winModeValue = MOneResult.WIN_MODE_LOUHU
                    # 红中宝
                    hongZongBaoConfig = self.tableConfig.get(MTDefine.HONG_ZHONG_BAO, 0)
                    if self.isHongZhong() and hongZongBaoConfig and (MTile.TILE_HONG_ZHONG not in self.tableTileMgr.getMagicTiles(True)):
                        winModeValue = MOneResult.WIN_MODE_hongzhongbao
                        self.addWinFanPattern(self.fanXing[self.HONGZHONGBAO]['name'], self.fanXing[self.HONGZHONGBAO]['index'])
        
                    if isMagic and (not self.magicAfertTing):
                        winModeValue = MOneResult.WIN_MODE_mobao
                        self.addWinFanPattern(self.fanXing[self.MOBAO]['name'], self.fanXing[self.MOBAO]['index'])
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
                if self.menState[seatId] == 1:
                    looseFanName = self.fanXing[self.BIMEN]['name']
                    looseFanIndex = self.fanXing[self.BIMEN]['index']
                    fanPattern[seatId].append([looseFanName.strip(), str(looseFanIndex) + "番"])
                
            else:
                fanPattern[seatId] = []
                # 闭门
                if self.menState[seatId] == 1:
                    looseFanName = self.fanXing[self.BIMEN]['name']
                    looseFanIndex = self.fanXing[self.BIMEN]['index']
                    fanPattern[seatId].append([looseFanName.strip(), str(looseFanIndex) + "番"])

            
        score = [index for _ in range(self.playerCount)]
        
        '''
        #不听点炮*2
        if self.lastSeatId != self.winSeatId:
            if self.tingState[self.lastSeatId]:
                ftlog.debug('MHaerbinOneResult.calcWin dianpao index is zero becore tingState')
            else:
                score[self.lastSeatId] += 1
                ftlog.info('MMudanjiangOneResult.calcWin dianpao score:', score)
        '''
         
        if (self.bankerSeatId == self.winSeatId) and self.tableConfig.get(MTDefine.BANKER_DOUBLE, 1):
            for seatId in range(self.playerCount):
                if seatId == self.winSeatId:
                    continue
                
                score[seatId] += 1
                
            ftlog.info('MMudanjiangOneResult.calcWin zhuang double score:', score
                , ' bankerSeatId:', self.bankerSeatId
                , ' winSeatId:', self.winSeatId)
            
        if (self.bankerSeatId != self.winSeatId) and self.tableConfig.get(MTDefine.BANKER_DOUBLE, 1):
            score[self.bankerSeatId] += 1
        ftlog.info('MMudanjiangOneResult.calcWin zhuang loose double score:', score
                    , ' bankerSeatId:', self.bankerSeatId
                    , ' winSeatId:', self.winSeatId
                    , ' looseSeatId:', self.lastSeatId)
            
        for seatId in range(len(self.menState)):
            if (self.menState[seatId] == 1) and (seatId != self.winSeatId) and self.tableConfig.get(MTDefine.MEN_CLEAR_DOUBLE, 1):
                score[seatId] += 1
                ftlog.info('MMudanjiangOneResult.calcWin menqing double score:', score
                           , ' menState:', self.menState)
        
        # 输家只算闭门，不算大扣    
        winScore = 0
        for seatId in range(self.playerCount):
            if seatId != self.winSeatId:
                newIndex = score[seatId]
                looseScore = scoreIndex[newIndex]
#                 if self.isDaKouLoose(seatId):
#                     ftlog.info('MMudanjiangOneResult.calcWin dakouLoose double score:', looseScore
#                             , ' seatId:', seatId
#                             , ' menState:', self.menState
#                             , ' tingState:', self.tingState)
#                     looseScore = looseScore * 2
#                     # 大扣
#                     looseFanName = self.fanXing[self.DAKOU]['name']
#                     looseFanIndex = self.fanXing[self.DAKOU]['index']
#                     fanPattern[seatId].append([looseFanName.strip(), str(looseFanIndex) + "番"])
                score[seatId] = -looseScore
                winScore += looseScore
        score[self.winSeatId] = winScore
        
        # 加入底分的概念*2或者*5
        '''
        for seatId in range(len(score)):
            score[seatId] *= scoreBase
        '''
         
        ftlog.info('MMudanjiangOneResult.calcWin score before baopei:', score)
        
        if self.lastSeatId != self.winSeatId:
            if self.tingState[self.lastSeatId] == 0:
                # 包赔
                for seatId in range(len(score)):
                    if seatId != self.winSeatId and seatId != self.lastSeatId:
                        s = score[seatId]
                        score[seatId] = 0
                        score[self.lastSeatId] += s
                ftlog.info('MMudanjiangOneResult.calcWin dianpaobaozhuang score:', score
                    , ' lastSeatId:', self.lastSeatId
                    , ' winSeatId:', self.winSeatId
                    , ' tingState:', self.tingState)
                
        # 最大番统计(改成单局最佳)
        resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN:score[self.winSeatId]}) 
        
        self.results[self.KEY_TYPE] = '和牌'
        self.results[self.KEY_NAME] = name
        ftlog.debug('MMudanjiangOneResult.calcWin result score:', score)
        self.results[self.KEY_SCORE] = score
        ftlog.debug('MMudanjiangOneResult.calcWin result winMode:', winMode)
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        ftlog.debug('MMudanjiangOneResult.calcWin result fanPattern:', fanPattern)
        self.results[self.KEY_FAN_PATTERN] = fanPattern
    
    def calcZiMoAdvFan(self, isZiMo, isDanDiao, isDaFeng, isBaoZhongBao, isMagic, isJia, isBian):
        if not isZiMo:
            return '', 0
        
        bianMulti = self.tableConfig.get(MTDefine.BIAN_MULTI, 0)
        
        if self.magicAfertTing:  # 听牌之后是宝牌 直接和牌
            if (isBian and bianMulti and len(self.winNodes) == 1):
                # 宝夹
                return self.fanXing[self.BAOZHONGBAOJIA]['name'], self.fanXing[self.BAOZHONGBAOJIA]['index']
            elif isJia:
                return self.fanXing[self.BAOZHONGBAOJIA]['name'], self.fanXing[self.BAOZHONGBAOJIA]['index']
            elif isDanDiao:
                return self.fanXing[self.BAOZHONGBAOJIA]['name'], self.fanXing[self.BAOZHONGBAOJIA]['index']
            else: 
                # 宝边
                return self.fanXing[self.BAOBIAN]['name'], self.fanXing[self.BAOBIAN]['index']
        
        # 红中宝情况 如果本来胡的是宝夹
        hongZongBaoConfig = self.tableConfig.get(MTDefine.HONG_ZHONG_BAO, 0)
        if self.isHongZhong() and hongZongBaoConfig:
            if self.isHuMagicTile() and (isJia or (isBian and bianMulti)):
                return self.fanXing[self.BAOZHONGBAOJIA]['name'], self.fanXing[self.BAOZHONGBAOJIA]['index'] 
        
        # 哈尔滨宝中宝 听牌之后手里刚好有三张宝牌 直接和牌
        if isBaoZhongBao:
            return self.fanXing[self.BAOZHONGBAODAFENG]['name'], self.fanXing[self.BAOZHONGBAODAFENG]['index']
        
        if isDaFeng and isMagic:
            return self.fanXing[self.BAOZHONGBAODAFENG]['name'], self.fanXing[self.BAOZHONGBAODAFENG]['index']
        
        
        if isMagic and isBian:
            if bianMulti and self.isHuMagicTile():
                return self.fanXing[self.BAOZHONGBAOJIA]['name'], self.fanXing[self.BAOZHONGBAOJIA]['index']
            else:
                return self.fanXing[self.BAOBIAN]['name'], self.fanXing[self.BAOBIAN]['index']
        
        if isMagic and isJia and self.isHuMagicTile():
            return self.fanXing[self.BAOZHONGBAOJIA]['name'], self.fanXing[self.BAOZHONGBAOJIA]['index']
        
        if isDaFeng:
            # 大风时判断宝夹
            if self.isHuMagicTile() and (isJia or (isBian and bianMulti)):
                return self.fanXing[self.BAOZHONGBAOJIA]['name'], self.fanXing[self.BAOZHONGBAOJIA]['index']
            else:
                return self.fanXing[self.GUADAFENG]['name'], self.fanXing[self.GUADAFENG]['index']
        
        return self.fanXing[self.ZIMO]['name'], self.fanXing[self.ZIMO]['index']
    
    def calcDianPaoFan(self, isJia, isBian, isDanDiao):
        name = ''
        index = 0
        
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
        if isBian and bianMulti:
            name = self.fanXing[self.JIAHU]['name']
            index = self.fanXing[self.JIAHU]['index']
            self.addWinFanPattern(name, index)
            return name, index
            
        print 'name: ', name, ' index: ', index
        return name, index    
        
    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
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
     
     
    def calcGang(self):
        """计算杠的输赢"""
        
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
         
        if self.lastSeatId != self.winSeatId:
            scores = [0 for _ in range(self.playerCount)]
            scores[self.lastSeatId] = -base * (self.playerCount - 1)  # 点杠包3家
            scores[self.winSeatId] = base * (self.playerCount - 1)
        else:
            scores = [-base for _ in range(self.playerCount)]
            scores[self.winSeatId] = (self.playerCount - 1) * base
        
        ftlog.debug('MOneResult.calcGang gangType:', self.results[self.KEY_NAME], ' scores', scores)
        self.results[self.KEY_SCORE] = scores
        self.results[self.KEY_STAT] = resultStat      
         
            
if __name__ == "__main__":
    result = MMudanjiangOneResult()
    result.setTableConfig({})
    result.setMenState([0, 0, 0, 0])
    result.setTingState([1, 0, 0, 0])
    result.setLastSeatId(2)
    result.setWinSeatId(0)
    result.setPlayerCount(4)
    result.setWinTile(8)
    result.setMagics([23])
    result.setBankerSeatId(1)
    result.setWinNodes([{"winTile": 8, "pattern": [[7, 8, 9], [11, 11]]}])
    result.calcWin()
