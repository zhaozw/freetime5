# -*- coding=utf-8
'''
Created on 2016年9月23日

一条和牌结果

@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
from majiang2.win_loose_result.one_result import MOneResult
import copy


class MWeihaiOneResult(MOneResult):
    '''
    威海麻将积分计算方式：
    积分合计 = 底分 x 庄 x （胡法 x 胡型 x 牌型 + 杠 + 锚 + 漂）。如果胡牌时有多种胡型均符合，则该几种胡型相乘
    
    1）底分 1分
    2）坐庄X2 胡或者放炮都翻倍
    3）胡法 自摸和点炮都不翻倍
    
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
    
    7）锚
        7.1 点炮胡：+胡家门前锚数+放炮者门前锚数，由放炮者承担；
        7.2 自摸胡：+胡家门前锚数x3 +A家锚数+B家锚数+C家锚数，即，每家除了输掉自己门前的锚数，还要再输掉胡家门前的锚数
        
    8）漂
        8.1 点炮胡：+胡家漂数+放炮者漂数，由放炮者承担；
        8.2 自摸胡：+胡家漂数x3 +A的漂数+B的漂数+C的漂数，即，每家除了输掉自己下的漂数，还要再输掉胡家下的漂数


    '''

    ZIMOHU = 'ZIMOHU'
    DIANPAOHU = 'DIANPAOHU'

    JIAHU = 'JIAHU'
    JIAWU = 'JIAWU'
    CEBIAN = 'CEBIAN'
    SHOUZHUAYI = 'SHOUZHUAYI'
    HAIDILAO = 'HAIDILAO'
    GANGSHANGKAI = 'GANGSHANGKAI'

    MINGGANG = 'MINGGANG'
    ANGANG = 'ANGANG'

    PINGHU = 'PINGHU'
    PENGPENGHU = 'PENGPENGHU'
    QIXIAODUI = 'QIXIAODUI'
    MENQING = 'MENQING'
    HHQIXIAODUI = 'HHQIXIAODUI'
    QIDADUI = 'QIDADUI'
    HUNYISE = 'HUNYISE'
    QINGYISE = 'QINGYISE'
    FENGYISE = 'FENGYISE'
    SHISANYAO = 'SHISANYAO'



    
    def __init__(self, tilePatternChecker, playerCount):
        super(MWeihaiOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = {
            self.ZIMOHU: {"name":"自摸", "index": 0},
            self.DIANPAOHU: {"name":"点炮", "index":1},
            self.JIAHU: {"name":"夹胡", "index":1},
            self.JIAWU: {"name": "夹五", "index": 1},
            self.CEBIAN: {"name": "三七边", "index": 1},
            self.SHOUZHUAYI: {"name": "手一把", "index": 1},
            self.HAIDILAO: {"name": "海底捞月", "index": 1},
            self.GANGSHANGKAI: {"name": "杠上开花", "index": 1},
            self.MINGGANG: {"name": "明杠", "index": 1},
            self.ANGANG: {"name": "暗杠", "index": 1},
            self.PINGHU: {"name": "平胡", "index": 1},
            self.PENGPENGHU: {"name": "碰碰胡", "index": 1},
            self.QIXIAODUI: {"name": "七小对", "index": 1},
            self.MENQING: {"name": "门清", "index": 1},
            self.HHQIXIAODUI: {"name": "豪华七小对", "index": 1},
            self.QIDADUI: {"name": "七大对", "index": 1},
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


    def isSanQi(self):
        """是否三七边"""
        # 1，2，3 拿出来，剩下的能不能胡
        # 7，8，9 拿出来 剩下的能不能胡
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])

        if MTile.getValue(self.winTile) == 7 and self.winTile < 30 and (self.winTile + 1) in handTile and (self.winTile + 2) in handTile:
            handTile.remove(self.winTile)
            handTile.remove(self.winTile + 1)
            handTile.remove(self.winTile + 2)
            res, _ = MWin.isHu(handTile)
            ftlog.debug('weihai_one_result.isSanQi result: ', res)
            return res
        elif MTile.getValue(self.winTile) == 3 and self.winTile < 30 and (self.winTile - 1) in handTile and self.winTile - 2 in handTile:
            handTile.remove(self.winTile)
            handTile.remove(self.winTile - 1)
            handTile.remove(self.winTile - 2)
            res, _ = MWin.isHu(handTile)
            ftlog.debug('weihai_one_result.isSanQi result: ', res)
            return res
        else:
            ftlog.debug('weihai_one_result.isSanQi result: False')
            return False


    def isJia(self):
        """是否夹牌"""
        # winTile-1 winTile winTile + 1拿出来，剩下的判胡
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])

        if (self.winTile - 1) in handTile and (self.winTile + 1) in handTile:
            handTile.remove(self.winTile)
            handTile.remove(self.winTile - 1)
            handTile.remove(self.winTile + 1)

            res, _ = MWin.isHu(handTile)
            ftlog.debug('weihai_one_result.isJia result: ', res)
            return res
        else:
            ftlog.debug('weihai_one_result.isJia result:False ')
            return False


    def isJia5(self):
        """是否夹五"""
        res = self.isJia() and (MTile.getValue(self.winTile) == 5) and (self.winTile < 30)
        ftlog.debug('weihai_one_result.isJia5 result: ', res)
        return res

    def isQingyise(self):
        """
        清一色：由同一门花色（筒子或条子）组成的和牌牌型
        """
        colorArr = [0, 0, 0, 0]
        handTile = MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId])  # 手牌区+吃+碰+杠+锚+胡区

        ftlog.debug('weihai_one_result.isQingyise handTile=', handTile)

        for tile in handTile:
            color = MTile.getColor(tile)
            colorArr[color] = 1

        colorCount = 0
        for eachColor in colorArr:
            if eachColor:
                colorCount += 1
        if colorCount == 1 and colorArr[3] == 0:
            ftlog.debug('weihai_one_result.isQingyise result: True')
            return True
        ftlog.debug('weihai_one_result.isQingyise result: False')
        return False

    def isHunyise(self):
        """
        混一色：由东南西北中发白 + 万、条、筒中的任意一种组成的胡牌
        """
        colorArr = [0, 0, 0, 0]
        handTile = MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId])  # 手牌区+吃+碰+杠+锚+胡区

        ftlog.debug('weihai_one_result.isHunyise handTile=', handTile)

        for tile in handTile:
            color = MTile.getColor(tile)
            colorArr[color] = 1

        colorCount = 0
        for eachColor in colorArr:
            if eachColor:
                colorCount += 1
        if colorCount == 2 and colorArr[3] == 1:
            ftlog.debug('weihai_one_result.isHunyise result: True')
            return True
        ftlog.debug('weihai_one_result.isHunyise result: False')
        return False

    def isFengyise(self):
        """
        风一色：由东南西北中发白组成的胡牌
        """

        colorArr = [0, 0, 0, 0]
        handTile = MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId])  # 手牌区+吃+碰+杠+锚+胡区

        ftlog.debug('weihai_one_result.isFengyise handTile=', handTile)

        for tile in handTile:
            color = MTile.getColor(tile)
            colorArr[color] = 1

        colorCount = 0
        for eachColor in colorArr:
            if eachColor:
                colorCount += 1
        if colorCount == 1 and colorArr[3] == 1:
            ftlog.debug('weihai_one_result.isFengyise result: True')
            return True
        ftlog.debug('weihai_one_result.isFengyise result: False')
        return False

    def isQidui(self):
        """
        七对：手中有七个对子的胡牌牌型，碰出的牌不算
        """
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])

        result, _ = MWin.isQiDui(handTile)

        # 放锚之后不能胡七对
        maoTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_MAO])
        if len(maoTile) > 0 :
            result = False

        ftlog.debug('weihai_one_result.isQidui result: ', result)
        return result

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
                ftlog.debug('weihai_one_result.isQiduiHao result: True')
                return True

        ftlog.debug('weihai_one_result.isQiduiHao result: False')
        return False

    def isQiduiDa (self):
        """
        七大对：七对的牌面值是连续的
        """
        if not self.isQidui():
            return False
        
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])
        
        hTileArr = MTile.changeTilesToValueArr(handTile)
        shunCount = 0
        shunIndex = 0
        for tileIndex in range(len(hTileArr)):
            if hTileArr[tileIndex] > 0:
                if 0 == shunIndex:
                    shunCount += 1
                    shunIndex = tileIndex
                else:
                    if (tileIndex != (shunIndex + 1)):
                        ftlog.debug('weihai_one_result.isQiduiDa result: False')
                        return False
                    else:
                        shunCount += 1
                        shunIndex = tileIndex
        if shunCount == 7:
            ftlog.debug('weihai_one_result.isQiduiDa result: True')
            return True
        ftlog.debug('weihai_one_result.isQiduiDa result: False')
        return False

    def isShouzhuayi(self):
        """
        手抓一：胡牌时自己手上只有一张牌，和牌手牌应该是一对
        """
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])

        if len(handTile) == 2:
            ftlog.debug('weihai_one_result.isShouzhuayi result: True')
            return True

        ftlog.debug('weihai_one_result.isShozhuayi result: False')
        return False


    def isPengpenghu (self):
        """
        碰碰胡：由四个刻子（杠）和一对组成的胡牌牌型
        """
        chiTile = self.playerAllTiles[self.winSeatId][MHand.TYPE_CHI]  # 吃牌区
        if len(chiTile) > 0:
            return False

        maoTile = self.playerAllTiles[self.winSeatId][MHand.TYPE_MAO]  # 锚牌区
        if len(maoTile) > 0:
            return False

        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])
        
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
                ftlog.debug('weihai_one_result.isPengpenghu result: False')
                return False
            elif hTileArr[tileIndex] == 4:
                ftlog.debug('weihai_one_result.isPengpenghu result: False')
                return False

        if duiCount == 1 and keCount >= 0:
            ftlog.debug('weihai_one_result.isPengpenghu result: True')
            return True
        else:
            ftlog.debug('weihai_one_result.isPengpenghu result: False')
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

    def isMenQing(self):
        if self.menState[self.winSeatId] == 0:
            return False

        if self.getMaoTiles(self.winSeatId) > 0:  # 放锚了不算门清
            return False
        if self.lastSeatId != self.winSeatId:  # 点炮不算门清
            return False

        return True


    def calcWin(self):
        """
        威海赢牌算分
        """
        self.clearWinFanPattern()

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

        # 胡型判断
        if self.isSanQi():  # 侧边
            fx = self.fanXing[self.JIAHU]  # 三七边算夹
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
        
        if self.isJia():  # 夹胡
            if self.isJia5():  # 夹五
                fx = self.fanXing[self.JIAWU]
                self.addWinFanPattern(fx['name'], fx['index'])
                baseScore = baseScore * 4
            else:
                fx = self.fanXing[self.JIAHU]
                self.addWinFanPattern(fx['name'], fx['index'])
                baseScore = baseScore * 2
        
        if self.isShouzhuayi():  # 手把一
            fx = self.fanXing[self.SHOUZHUAYI]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
        
        if self.tableTileMgr.isHaidilao():  # 海底捞月
            fx = self.fanXing[self.HAIDILAO]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
        
        if self.gangKai:  # 杠上开
            fx = self.fanXing[self.GANGSHANGKAI]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2


        # 牌型判断
        if self.isQingyise():  # 清一色
            fx = self.fanXing[self.QINGYISE]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 4
        elif self.isHunyise():  # 混一色
            fx = self.fanXing[self.HUNYISE]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2

        if self.isQidui():  # 七小对
            if self.isQiduiHao():  # 豪华七小对
                fx = self.fanXing[self.HHQIXIAODUI]
                self.addWinFanPattern(fx['name'], fx['index'])
                baseScore = baseScore * 4
            else:
                fx = self.fanXing[self.QIXIAODUI]
                self.addWinFanPattern(fx['name'], fx['index'])
                baseScore = baseScore * 2

        elif self.isPengpenghu():  # 碰碰胡
            fx = self.fanXing[self.PENGPENGHU]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
            
        if self.isMenQing():  # 门清
            fx = self.fanXing[self.MENQING]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2

        ###### 算杠分
        gangscore = 0  # 杠牌得分
        gangList = self.playerGangTiles[self.winSeatId]
        for ga in gangList:
            if ga['style'] == 0:  # 暗杠
                gangscore += 2
            else:
                gangscore += 1

        ftlog.debug('weihai_one_result.calcWin baseScore=====', baseScore)

        #### 胡法判断
        if isZiMo:  # 自摸
            # 庄家判断  赢家是庄家
            if self.bankerSeatId == self.winSeatId:
                baseScore = baseScore * 2
                score = [-baseScore for _ in range(self.playerCount)]
                score[self.winSeatId] = (self.playerCount - 1) * baseScore
            else:  # 赢家不是庄家
                for loose in range(self.playerCount):
                    if loose == self.winSeatId:
                        continue
                    if loose == self.bankerSeatId:  # 庄家输双倍
                        score[loose] = -baseScore * 2
                    else:
                        score[loose] = -baseScore
                score[self.winSeatId] = self.playerCount * baseScore
        else:  # 点炮
            # 庄家判断  赢家是庄家
            if self.bankerSeatId == self.winSeatId:
                baseScore = baseScore * 2
                score[self.lastSeatId] = -baseScore
                score[self.winSeatId] = baseScore
            else:  # 赢家不是庄家
                if self.lastSeatId == self.bankerSeatId:  # 庄家放炮
                    score[self.lastSeatId] = -baseScore * 2
                    score[self.winSeatId] = baseScore * 2
                else:
                    score[self.lastSeatId] = -baseScore
                    score[self.winSeatId] = baseScore

        ftlog.debug('weihai_one_result.calcWin score_hufa=====', score  , 'banker:', self.bankerSeatId , 'winer', self.winSeatId)

        ##### 飘分、锚分计算
        if isZiMo:  # 自摸 自己的飘 + 别人的飘 + 必票*n
            for loose in range(self.playerCount):
                if loose != self.winSeatId:
                    piao = self.piaoProcessor.getPiaoPointsBySeats(self.winSeatId, loose)  # 算飘的分
                    score[loose] -= piao
                    score[self.winSeatId] += piao
                    # 算锚的分值
                    mao = self.getMaoScores(loose) + self.getMaoScores(self.winSeatId)

                    score[loose] -= mao
                    score[self.winSeatId] += mao
                    # 算杠
                    score[loose] -= gangscore
                    score[self.winSeatId] += gangscore

        else:  # 点炮
            piao = self.piaoProcessor.getPiaoPointsBySeats(self.winSeatId, self.lastSeatId)  # 算飘的分
            score[self.lastSeatId] -= piao
            score[self.winSeatId] += piao

            # 算锚的分值
            mao = self.getMaoScores(self.lastSeatId) + self.getMaoScores(self.winSeatId)
            ftlog.debug('getPiaoPointsBySeats1 mao1=====', self.getMaoScores(self.lastSeatId), 'mao2===', self.getMaoScores(self.winSeatId))
            score[self.lastSeatId] -= mao
            score[self.winSeatId] += mao
            # 算杠
            score[self.lastSeatId] -= gangscore
            score[self.winSeatId] += gangscore

        piaoPoints = {}
        piaoPoints['points'] = [self.piaoProcessor.piaoPoints[seat] for seat in range(self.playerCount)]  # 给前端显示票分
        piaoPoints['biPiao'] = self.piaoProcessor.biPiaoPoint

        # 最大番统计(改成单局最佳)
        resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN: score[self.winSeatId]})


        self.results[self.KEY_TYPE] = '和牌'
        self.results[self.KEY_NAME] = fanXing['name']
        self.results[self.KEY_SCORE] = score
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        fanPattern[self.winSeatId] = self.winFanPattern
        ftlog.debug('weihai_one_result.calcWin result fanPattern:', fanPattern)
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
            piaoPoints['biPiao'] = self.piaoProcessor.biPiaoPoint

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
    result = MWeihaiOneResult()
    result.setTableConfig({})
