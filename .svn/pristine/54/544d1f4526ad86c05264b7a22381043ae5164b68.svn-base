# -*- coding=utf-8
'''
Created on 2016年9月23日

一条和牌结果

@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from majiang2.table.table_config_define import MTDefine
from majiang2.tile.tile import MTile
from majiang2.win_loose_result.one_result import MOneResult
import copy


class MYantaiOneResult(MOneResult):
    '''
    烟台麻将积分计算方式：
    积分合计 = 底分 x 庄 x 胡法 x 胡型 x 牌型 + 杠 + 漂。
        如果胡牌时有多种胡型均符合，则该几种胡型相乘
    
    1）底分 1分
    2）坐庄X2 胡或者放炮都翻倍
    3）胡法 自摸和点炮都不翻倍
    4）明楼*2，明楼若没胡，点炮，输分也X2
    
    4）胡型
        4.1 夹胡/侧边 X 2
            4.1.1 夹胡，13叫2为夹胡
            4.1.2 侧边，12胡三和89胡七叫侧边
            4.1.3 夹五 X 4
        4.2 手把一 X 2。 手里最后剩一张牌单叫
        4.3 海底捞 X 2，海底捞的牌，只能用来自摸，打出去不点炮
        4.4 杠上开花 X 2
        
    5）牌型
        5.1 平胡 1
        5.2 碰碰胡 2
        5.3 七小对 2
        5.4 门清 2
        5.5 豪华七小对 4 五对加四张一样的
        5.6 七大对 10
        5.7 混一色 10
        5.8 清一色 10
        5.9 风一色 10
        6.0 十三幺 10
    
    6）明杠+1 暗杠+2
        
    8）漂
        8.1 点炮胡：+胡家漂数+放炮者漂数，由放炮者承担；
        8.2 自摸胡：+胡家漂数x3 +A的漂数+B的漂数+C的漂数，即，每家除了输掉自己下的漂数，还要再输掉胡家下的漂数

    '''

    ZIMOHU = 'ZIMOHU'
    DIANPAOHU = 'DIANPAOHU'
    MINGLOU = 'MINGLOU'

    SHOUZHUAYI = 'SHOUZHUAYI'
    HAIDILAO = 'HAIDILAO'
    GANGSHANGKAI = 'GANGSHANGKAI'
    MENQING = 'MENQING'
    DADIAOCHA = 'DADIAOCHE'

    MINGGANG = 'MINGGANG'
    ANGANG = 'ANGANG'

    PINGHU = 'PINGHU'
    PENGPENGHU = 'PENGPENGHU'
    QIXIAODUI = 'QIXIAODUI'
    HHQIXIAODUI = 'HHQIXIAODUI'
    HUNYISE = 'HUNYISE'
    QINGYISE = 'QINGYISE'
    FENGYISE = 'FENGYISE'
    SHISANYAO = 'SHISANYAO'

    def __init__(self, tilePatternChecker, playerCount):
        super(MYantaiOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = {
            self.ZIMOHU: {"name":"自摸", "index": 0},
            self.DIANPAOHU: {"name":"点炮", "index":1},
            self.SHOUZHUAYI: {"name": "手一把", "index": 1},
            self.HAIDILAO: {"name": "海底捞月", "index": 1},
            self.MENQING: {"name": "门清", "index": 1},
            self.MINGLOU: {"name": "明搂", "index": 1},
            self.DADIAOCHA: {"name": "大吊车", "index": 1},
            self.GANGSHANGKAI: {"name": "杠上开花", "index": 1},
            self.MINGGANG: {"name": "明杠", "index": 1},
            self.ANGANG: {"name": "暗杠", "index": 1},
            self.PINGHU: {"name": "平胡", "index": 1},
            self.PENGPENGHU: {"name": "碰碰胡", "index": 1},
            self.QIXIAODUI: {"name": "七小对", "index": 1},
            self.HHQIXIAODUI: {"name": "豪华七小对", "index": 1},
            self.HUNYISE: {"name": "混一色", "index": 1},
            self.QINGYISE: {"name": "清一色", "index": 1},
            self.FENGYISE: {"name": "风一色", "index": 1},
            self.SHISANYAO: {"name": "十三幺", "index": 1}
        }
        
    @property
    def fanXing(self):
        return self.__fan_xing
    
    def setFanXing(self, fanXing):
        self.__fan_xing = fanXing

    def isQingyise(self):
        """
        清一色：由同一门花色（筒子或条子）组成的和牌牌型
        """
        colorArr = [0, 0, 0, 0]
        handTile = MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId])  # 手牌区+吃+碰+杠+锚+胡区

        ftlog.debug('MYantaiOneResult.isQingyise handTile=', handTile)

        for tile in handTile:
            color = MTile.getColor(tile)
            colorArr[color] = 1

        colorCount = 0
        for eachColor in colorArr:
            if eachColor:
                colorCount += 1
        if colorCount == 1 and colorArr[3] == 0:
            ftlog.debug('MYantaiOneResult.isQingyise result: True')
            return True
        ftlog.debug('MYantaiOneResult.isQingyise result: False')
        return False
    
    def isHunyise(self):
        """
        混一色：由东南西北中发白 + 万、条、筒中的任意一种组成的胡牌
        """
        colorArr = [0, 0, 0, 0]
        handTile = MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId])  # 手牌区+吃+碰+杠+锚+胡区

        ftlog.debug('MYantaiOneResult.isHunyise handTile=', handTile)

        for tile in handTile:
            color = MTile.getColor(tile)
            colorArr[color] = 1

        colorCount = 0
        for eachColor in colorArr:
            if eachColor:
                colorCount += 1
        if colorCount == 2 and colorArr[3] == 1:
            ftlog.debug('MYantaiOneResult.isHunyise result: True')
            return True
        ftlog.debug('MYantaiOneResult.isHunyise result: False')
        return False

    def isFengyise(self):
        """
        风一色：由东南西北中发白组成的胡牌
        """
        handTile = MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId])  # 手牌区+吃+碰+杠+锚+胡区
        handArr = MTile.changeTilesToValueArr(handTile)
        colorCount = MTile.getColorCount(handArr)
        result, _ = MWin.isLuanFengyise(handTile, colorCount)
        return result

    def isQidui(self):
        """
        七对：手中有七个对子的胡牌牌型，碰出的牌不算
        """
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])

        qiduiResult, _ = MWin.isQiDui(handTile)
        ftlog.debug('MYantaiOneResult.isQidui result: ', qiduiResult)
        return qiduiResult

    def isQiduiHao (self):
        """
        豪华七对：有四个相同的牌当做两个对子使用
        """
        if not self.isQidui():
            return False
        
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])

        hTileArr = MTile.changeTilesToValueArr(handTile)  # 手牌区符合 2+ 4*n

        for tileIndex in range(len(hTileArr)):
            if hTileArr[tileIndex] == 4:
                ftlog.debug('MYantaiOneResult.isQiduiHao result: True')
                return True

        ftlog.debug('MYantaiOneResult.isQiduiHao result: False')
        return False

    def isPengpenghu (self):
        """
        碰碰胡：由四个刻子（杠）和一对组成的胡牌牌型
        """
        chiTile = self.playerAllTiles[self.winSeatId][MHand.TYPE_CHI]  # 吃牌区
        if len(chiTile) > 0:
            return False

        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])
        ftlog.debug('MYantaiOneResult.isPengpenghu handTile: ', handTile)
        
        hTileArr = MTile.changeTilesToValueArr(handTile)  # 手牌区符合 2+ 3*n
        duiCount = 0
        keCount = 0
        for tileIndex in range(0, len(hTileArr)):
            if hTileArr[tileIndex] == 0:
                continue
            # 对子
            elif hTileArr[tileIndex] == 2:
                duiCount += 1
            # 刻子
            elif hTileArr[tileIndex] == 3:
                keCount += 1
            elif hTileArr[tileIndex] == 1:
                ftlog.debug('MYantaiOneResult.isPengpenghu result: False')
                return False
            elif hTileArr[tileIndex] == 4:
                ftlog.debug('MYantaiOneResult.isPengpenghu result: False')
                return False

        if duiCount == 1 and keCount >= 0:
            ftlog.debug('MYantaiOneResult.isPengpenghu result: True')
            return True
        else:
            ftlog.debug('MYantaiOneResult.isPengpenghu result: False')
            return False
        
    def isDadiaoche(self):
        """
        大吊车：胡牌时自己手上只有一张牌，且胡的是二五八
        """
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        if len(handTile) % 3 != 2:
            handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])
        huTile = self.playerAllTiles[self.winSeatId][MHand.TYPE_HU][0]
        ftlog.debug('MYantaiOneResult.isDadiaoche handTile:', handTile
                    , ' huTile:', huTile)

        if (len(handTile) == 2) and (huTile < MTile.TILE_DONG_FENG) and (MTile.getValue(huTile) % 3 == 2):
            ftlog.debug('MYantaiOneResult.isDadiaoche result: True')
            return True

        ftlog.debug('MYantaiOneResult.isDadiaoche result: False')
        return False

    def getMaoTiles(self, seatId):

        maoNum = 0
        for mao in self.playerAllTiles[seatId][MHand.TYPE_MAO]:
            maoNum += len (mao['pattern'])

        return maoNum

    def getMaoScores(self, seatId):

        maoScore = 0
        for mao in self.playerAllTiles[seatId][MHand.TYPE_MAO]:
            if len (mao['pattern']) > 0 :  # 放锚的三张不算分
                maoScore += len (mao['pattern']) - 3

        return  maoScore

    def calcWin(self):
        """
        威海赢牌算分
        """
        self.clearWinFanPattern()
        self.tilePatternChecker.setPlayerAllTiles(self.playerAllTiles[self.winSeatId])

        # 在和牌时统计自摸，点炮状态
        resultStat = [[] for _ in range(self.playerCount)]
        winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
        fanPattern = [[] for _ in range(self.playerCount)]
        fanXing = self.fanXing[self.PINGHU]
        resultStat[self.winSeatId].append({MOneResult.STAT_WIN:1})
        isZiMo = (self.lastSeatId == self.winSeatId)
        if isZiMo:
            resultStat[self.lastSeatId].append({MOneResult.STAT_ZIMO:1})
            winMode[self.lastSeatId] = MOneResult.WIN_MODE_ZIMO
        else:
            resultStat[self.lastSeatId].append({MOneResult.STAT_DIANPAO: 1})
            winMode[self.lastSeatId] = MOneResult.WIN_MODE_DIANPAO
            winMode[self.winSeatId] = MOneResult.WIN_MODE_PINGHU


        score = [0 for _ in range(self.playerCount)]
        # 底分1分
        baseScore = 1
        ftlog.debug('MYantaiOneResult.calcWin baseScore:', baseScore)

        # 胡型判断
        if self.tableTileMgr.isHaidilao():  # 海底捞月
            fx = self.fanXing[self.HAIDILAO]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
            ftlog.debug('MYantaiOneResult.calcWin Haidilao, baseScore double:', baseScore)
        
        if self.gangKai:  # 杠上开
            fx = self.fanXing[self.GANGSHANGKAI]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
            ftlog.debug('MYantaiOneResult.calcWin gangKai, baseScore double:', baseScore)
            
        if self.menState[self.winSeatId] == 1:
            fx = self.fanXing[self.MENQING]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
            ftlog.debug('MYantaiOneResult.calcWin menQing, baseScore double:', baseScore)
            
        if self.isDadiaoche():
            fx = self.fanXing[self.DADIAOCHA]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
            ftlog.debug('MYantaiOneResult.calcWin daDiaoChe, baseScore double:', baseScore)

        # 牌型判断
        multi = 1
        if self.isQingyise():  # 清一色
            fx = self.fanXing[self.QINGYISE]
            self.addWinFanPattern(fx['name'], fx['index'])
            multi = multi * 2
            ftlog.debug('MYantaiOneResult.calcWin isQingyise, multi X 5:', multi)
            
        if self.isHunyise():  # 混一色
            fx = self.fanXing[self.HUNYISE]
            self.addWinFanPattern(fx['name'], fx['index'])
            multi = multi * 2
            ftlog.debug('MYantaiOneResult.calcWin isHunyise, multi X 5:', multi)
            
        if self.isFengyise():  # 风一色
            fx = self.fanXing[self.FENGYISE]
            self.addWinFanPattern(fx['name'], fx['index'])
            multi = multi * 2
            ftlog.debug('MYantaiOneResult.calcWin isFengyise, multi X 5:', multi)
        
        if self.isQidui():  # 七小对
            if self.isQiduiHao():  # 豪华七小对
                fx = self.fanXing[self.HHQIXIAODUI]
                self.addWinFanPattern(fx['name'], fx['index'])
                multi = multi * 4
                ftlog.debug('MYantaiOneResult.calcWin isQiduiHao, multi X 10:', multi)
            else:
                fx = self.fanXing[self.QIXIAODUI]
                self.addWinFanPattern(fx['name'], fx['index'])
                multi = multi * 2
                ftlog.debug('MYantaiOneResult.calcWin isQidui, multi X 5:', multi)

        if self.isPengpenghu():  # 碰碰胡
            fx = self.fanXing[self.PENGPENGHU]
            self.addWinFanPattern(fx['name'], fx['index'])
            multi = multi * 2
            ftlog.debug('MYantaiOneResult.calcWin isPengpenghu, multi X 5:', multi)
            
        if self.tilePatternChecker.isShisanyao():
            fx = self.fanXing[self.SHISANYAO]
            self.addWinFanPattern(fx['name'], fx['index'])
            multi = multi * 4
            ftlog.debug('MYantaiOneResult.calcWin isShisanyao, multi X 10:', multi)
            
        baseScore = multi * baseScore
        ftlog.debug('MYantaiOneResult.calcWin adjustMulti:', multi
                        , ' baseScore:', baseScore)
            
        ftlog.debug('MYantaiOneResult.calcWin tingState:', self.tingState)
        #### 胡法判断
        if isZiMo:  # 自摸
            if self.tingState[self.winSeatId]:
                baseScore = baseScore * 2
                fx = self.fanXing[self.MINGLOU]
                self.addWinFanPattern(fx['name'], fx['index'])
                ftlog.debug('MYantaiOneResult.calcWin isZiMo, winnerTing baseScore double:', baseScore
                            , ' winSeatId:', self.winSeatId
                            , ' scores:', score)
                
            # 庄家判断  赢家是庄家
            if self.bankerSeatId == self.winSeatId:
#                 baseScore = baseScore * 2
                score = [-baseScore for _ in range(self.playerCount)]
                score[self.winSeatId] = (self.playerCount - 1) * baseScore
                ftlog.debug('MYantaiOneResult.calcWin isZiMo, bankerWin baseScore double:', baseScore
                            , ' winSeatId:', self.winSeatId
                            , ' scores:', score)
            else:  # 赢家不是庄家
                for loose in range(self.playerCount):
                    if loose == self.winSeatId:
                        continue
#                     if loose == self.bankerSeatId: #庄家输双倍
#                         score[loose] = - baseScore * 2
#                     else:
                    score[loose] = -baseScore
                score[self.winSeatId] = (self.playerCount - 1) * baseScore
                ftlog.debug('MYantaiOneResult.calcWin isZiMo, notBankerWin baseScore:', baseScore
                            , ' winSeatId:', self.winSeatId
                            , ' scores:', score)
        else:  # 点炮
            # 庄家判断  赢家是庄家
            if self.bankerSeatId == self.winSeatId:
#                 baseScore = baseScore * 2
                score[self.lastSeatId] = -baseScore
                score[self.winSeatId] = baseScore
                ftlog.debug('MYantaiOneResult.calcWin dianPao, BankerWin baseScore double:', baseScore
                            , ' winSeatId:', self.winSeatId
                            , ' looseSeatId:', self.lastSeatId
                            , ' scores:', score)
            else:  # 赢家不是庄家
                if self.lastSeatId == self.bankerSeatId:  # 庄家放炮
                    score[self.lastSeatId] = -baseScore
                    score[self.winSeatId] = baseScore
                    ftlog.debug('MYantaiOneResult.calcWin dianPao, BankerLoose baseScore double:', baseScore
                            , ' winSeatId:', self.winSeatId
                            , ' looseSeatId:', self.lastSeatId
                            , ' scores:', score)
                else:
                    score[self.lastSeatId] = -baseScore
                    score[self.winSeatId] = baseScore
                    ftlog.debug('MYantaiOneResult.calcWin dianPao, NotBankerLoose baseScore:', baseScore
                            , ' winSeatId:', self.winSeatId
                            , ' looseSeatId:', self.lastSeatId
                            , ' scores:', score)
                    
        # 庄加倍
        if self.tableConfig.get(MTDefine.BANKER_DOUBLE, 0):
            if isZiMo:
                if self.winSeatId == self.bankerSeatId:
                    # 庄家自摸
                    for index in range(self.playerCount):
                        score[index] = score[index] * 2
                else:
                    adJust = abs(score[self.bankerSeatId])
                    score[self.winSeatId] += adJust
                    score[self.bankerSeatId] -= adJust
                ftlog.debug('MYantaiOneResult.calcWin bankerDouble banker:', self.bankerSeatId
                            , ' winSeat:', self.winSeatId
                            , ' ZIMO '
                            , ' newScore:', score)
            else:
                if (self.winSeatId == self.bankerSeatId) or (self.lastSeatId == self.bankerSeatId):
                    adJust = abs(score[self.lastSeatId])
                    score[self.winSeatId] += adJust
                    score[self.lastSeatId] -= adJust
                ftlog.debug('MYantaiOneResult.calcWin bankerDouble banker:', self.bankerSeatId
                            , ' winSeat:', self.winSeatId
                            , ' DIANPAO '
                            , ' newScore:', score)   
                    
        ftlog.debug('MYantaiOneResult.calcWin doublePoints:', self.doublePoints)
        if self.doublePoints[self.winSeatId] == 2:
            score[self.winSeatId] = score[self.winSeatId] * 2
            if isZiMo:
                for loose in range(self.playerCount):
                    if loose == self.winSeatId:
                        continue
                    
                    score[loose] = score[loose] * 2
            else:
                score[self.lastSeatId] = score[self.lastSeatId] * 2
        ftlog.debug('MYantaiOneResult.calcWin afterDouble banker winSeatId:', self.winSeatId
                            , ' looseSeatId:', self.lastSeatId
                            , ' scores:', score)
        
        if isZiMo:
            for loose in range(self.playerCount):
                if loose == self.winSeatId:
                    continue
                if self.doublePoints[loose] == 1:
                    continue
                
                score[self.winSeatId] += abs(score[loose])
                score[loose] = score[loose] * 2
        else:
            if self.doublePoints[self.lastSeatId] == 2:
                score[self.winSeatId] += abs(score[self.lastSeatId])
                score[self.lastSeatId] = score[self.lastSeatId] * 2

        ###### 算杠分
        gangscore = 0  # 杠牌得分
        gangList = self.playerGangTiles[self.winSeatId]
        for ga in gangList:
            if ga['style'] == 0:  # 暗杠
                gangscore += 2
            else:
                gangscore += 1
        ftlog.debug('MYantaiOneResult.calcWin gangscore:', gangscore)

        ##### 飘分、锚分计算
        if isZiMo:  # 自摸 自己的飘 + 别人的飘 + 必票*n
            for loose in range(self.playerCount):
                if loose != self.winSeatId:
                    piao = self.piaoProcessor.getPiaoPointsBySeats(self.winSeatId, loose)  # 算飘的分
                    ftlog.debug('MYantaiOneResult.calcWin piao:', piao
                                , ' between ', self.winSeatId, loose)
                    score[loose] -= piao
                    score[self.winSeatId] += piao
                    # 算杠
                    score[loose] -= gangscore
                    score[self.winSeatId] += gangscore
        else:  # 点炮
            piao = self.piaoProcessor.getPiaoPointsBySeats(self.winSeatId, self.lastSeatId)  # 算飘的分
            ftlog.debug('MYantaiOneResult.calcWin piao:', piao
                                , ' between ', self.winSeatId, self.lastSeatId)
            score[self.lastSeatId] -= piao
            score[self.winSeatId] += piao
            # 算杠
            score[self.lastSeatId] -= gangscore
            score[self.winSeatId] += gangscore
        ftlog.debug('MYantaiOneResult.calcWin afterPiaoGang winSeatId:', self.winSeatId
                            , ' looseSeatId:', self.lastSeatId
                            , ' scores:', score)

        piaoPoints = {}
        piaoPoints['points'] = [self.piaoProcessor.piaoPoints[seat] for seat in range(self.playerCount)]  # 给前端显示票分

        # 最大番统计(改成单局最佳)
        resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN: score[self.winSeatId]})
            
        self.results[self.KEY_TYPE] = '和牌'
        self.results[self.KEY_NAME] = fanXing['name']
        self.results[self.KEY_SCORE] = score
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        fanPattern[self.winSeatId] = self.winFanPattern
        ftlog.debug('MYantaiOneResult.calcWin result fanPattern:', fanPattern)
        self.results[self.KEY_FAN_PATTERN] = fanPattern
        self.results[self.KEY_PIAO_POINTS] = piaoPoints

    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
        self.serialize()

        if self.resultType == self.RESULT_WIN:
            self.calcWin()
        elif self.resultType == self.RESULT_FLOW:
            piaoPoints = {}
            piaoPoints['points'] = [self.piaoProcessor.piaoPoints[seat] for seat in range(self.playerCount)]  # 给前端显示票分

            self.results[self.KEY_TYPE] = ''
            self.results[self.KEY_NAME] = '流局'
            score = [0 for _ in range(self.playerCount)]
            self.results[self.KEY_SCORE] = score
            winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
            self.results[self.KEY_WIN_MODE] = winMode
            resultStat = [[] for _ in range(self.playerCount)]
            self.results[self.KEY_STAT] = resultStat
            self.results[self.KEY_PIAO_POINTS] = piaoPoints

     
     
    def calcGang(self):
        """计算杠的输赢"""
        pass

            
if __name__ == "__main__":
    result = MYantaiOneResult()
    result.setTableConfig({})
