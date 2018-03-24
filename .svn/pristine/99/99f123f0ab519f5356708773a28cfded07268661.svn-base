# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: yawen
'''
from freetime5.util import ftlog
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from majiang2.table.table_config_define import MTDefine
from majiang2.tile.tile import MTile
from majiang2.win_loose_result.one_result import MOneResult
import copy


class MJinanOneResult(MOneResult):
    '''
    济南麻将积分计算方式：
    积分合计 = （花分“抓到的花牌”+杠分“杠刻加的花分”+底分）*番数+总跑分（漂分）
    
    1）底分 根据建桌时的选项 1、 2、 5分
    2）坐庄 坐庄不翻倍
    3）胡法 自摸和点炮都不翻倍
    
    4）胡型
        4.3 海底捞 * 2 海底捞的牌，只能用来自摸，打出去不点炮
        4.4 杠呲 * 2
        4.5 花呲 * 2
        4.6 明搂 * 2 
        4.7 抢杠胡  付3家
        
    5）牌型
        5.0 大吊车 * 2 手里最后剩一张牌单叫，且叫的是2、5、8
        5.1 平胡 * 1
        5.2 碰碰胡 * 2
        5.3 七小对 * 2
        5.5 豪华七小对 * 4 五对加四张一样的
        5.7 混一色 * 4
        5.8 清一色 * 4
        6.0 全将 * 2
        6.1 十三不靠 * 2
    
    6）明杠+1 暗杠+2
    
    7）刻子 风刻 1分 风杠 2分  风暗杠 3分
    
  
    8）跑
        8.1 点炮胡：+胡家分数+放炮者分数，由放炮者承担；
        8.2 自摸胡：+胡家分数x3 +A的分数+B的分数+C的分数，即，每家除了输掉自己下的分数，还要再输掉胡家下的分数


    '''

    ZIMOHU = 'ZIMOHU'
    DIANPAOHU = 'DIANPAOHU'

    DADIAOCHE = 'DADIAOCHE'
    HAIDILAO = 'HAIDILAO'
    GANGCI = 'GANGCI'
    HUACI = 'HUACI'

    MINGGANG = 'MINGGANG'
    ANGANG = 'ANGANG'

    PINGHU = 'PINGHU'
    PENGPENGHU = 'PENGPENGHU'
    QIXIAODUI = 'QIXIAODUI'
    HHQIXIAODUI = 'HHQIXIAODUI'
    HUNYISE = 'HUNYISE'
    QINGYISE = 'QINGYISE'
    QUANJIANG = 'QUANJIANG'
    BUKAO13 = 'BUKAO13'
    MINGLOU = 'MINGLOU'
    FLOWERHU = 'FLOWERHU'
    QIANGGANG = 'QIANGGANG'



    
    def __init__(self, tilePatternChecker, playerCount):
        super(MJinanOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = {
            self.ZIMOHU: {"name":"自摸", "index": 0},
            self.DIANPAOHU: {"name":"点炮", "index":1},
            self.DADIAOCHE: {"name": "大吊车", "index": 1},
            self.HAIDILAO: {"name": "海底捞月", "index": 1},
            self.GANGCI: {"name": "杠呲", "index": 1},
            self.HUACI: {"name": "花呲", "index": 1},
            self.MINGLOU: {"name": "明搂", "index": 1},

            self.MINGGANG: {"name": "明杠", "index": 1},
            self.ANGANG: {"name": "暗杠", "index": 1},
            self.PINGHU: {"name": "平胡", "index": 1},
            self.PENGPENGHU: {"name": "碰碰胡", "index": 1},
            self.QIXIAODUI: {"name": "七小对", "index": 1},
            self.HHQIXIAODUI: {"name": "豪华七小对", "index": 1},
            self.HUNYISE: {"name": "混一色", "index": 1},
            self.QINGYISE: {"name": "清一色", "index": 1},
            self.QUANJIANG: {"name": "全将", "index": 1},
            self.BUKAO13: {"name": "十三不靠", "index": 1},
            self.FLOWERHU: {"name": "花胡", "index": 1},
            self.QIANGGANG: {"name": "抢杠", "index": 1}
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

        ftlog.debug('jinan_one_result.isQingyise handTile=', handTile)

        for tile in handTile:
            color = MTile.getColor(tile)
            colorArr[color] = 1

        colorCount = 0
        for eachColor in colorArr:
            if eachColor:
                colorCount += 1
        if colorCount == 1 and colorArr[3] == 0:
            ftlog.debug('jinan_one_result.isQingyise result: True')
            return True
        ftlog.debug('jinan_one_result.isQingyise result: False')
        return False

    def isHunyise(self):
        """
        混一色：由东南西北中发白 + 万、条、筒中的任意一种组成的胡牌
        """
        colorArr = [0, 0, 0, 0]
        handTile = MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId])  # 手牌区+吃+碰+杠+锚+胡区

        ftlog.debug('jinan_one_result.isHunyise handTile=', handTile)

        for tile in handTile:
            color = MTile.getColor(tile)
            colorArr[color] = 1

        colorCount = 0
        for eachColor in colorArr:
            if eachColor:
                colorCount += 1
        if colorCount == 2 and colorArr[3] == 1:
            ftlog.debug('jinan_one_result.isHunyise result: True')
            return True
        ftlog.debug('jinan_one_result.isHunyise result: False')
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

        ftlog.debug('jinan_one_result.isQidui result: ', result)
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
                ftlog.debug('jinan_one_result.isQiduiHao result: True')
                return True

        ftlog.debug('jinan_one_result.isQiduiHao result: False')
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

        if (len(handTile) == 2):
            if self.tableTileMgr.tableConfig.get(MTDefine.ONLY_JIANG_258, 0) == 1:
                if (huTile < MTile.TILE_DONG_FENG) and (MTile.getValue(huTile) % 3 == 2):
                    return True
                else:
                    return False
            else:
                return  True

        ftlog.debug('MYantaiOneResult.isDadiaoche result: False')
        return False

    def isQuanjiang(self):
        """
        全将：手中的牌全部是二五八，不用成牌
        """
        tiles = copy.deepcopy(self.playerAllTiles[self.winSeatId])

        result, _ = MWin.isQuanJiang(tiles)

        ftlog.debug('jinan_one_result.isQuanjiang result: ', result)
        return result

    def isFlowerHu(self):
        """
        花胡 8张花牌都摸到
        """
        tiles = copy.deepcopy(self.playerAllTiles[self.winSeatId])

        result, _ = MWin.isFlowerHu(tiles)

        ftlog.debug('jinan_one_result.isFlowerHu result: ', result)
        return result

    def is13BuKao(self):
        """
        十三不靠：不同花色的 1、4、7 +  2、5、8 + 3、6、9 + 不相同的风牌4张
        #[[1, 4, 7, 12, 15, 18, 23, 26, 29, 31, 32, 33, 36], [], [], [], [], [35], [36], []]
        """

        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])

        chiTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_CHI])
        pengTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_PENG])
        gangTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_GANG])

        if len(chiTile) > 0 or len(pengTile) > 0 or len(gangTile) > 0:
            return False

        result, _ = MWin.is13BuKao(handTile)

        ftlog.debug('jinan_one_result.is13BuKao result: ', result)
        return result

    def getFengKe(self):
        """
        获得风刻的分数：手牌区和碰牌区
        """
        score = 0
        pengTile = self.playerAllTiles[self.winSeatId][MHand.TYPE_PENG]  # 碰牌区
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        for pengPatten in pengTile:
                if MTile.getColor(pengPatten[0]) == 3:
                    score = score + 1

        tileCountArr = MTile.changeTilesToValueArr(handTile)  # 手牌区
        for tileIndex in range(0, len(tileCountArr)):
            # 刻子
            if tileCountArr[tileIndex] == 3 and MTile.getColor(tileIndex) == 3:
                score = score + 1

        ftlog.debug('jinan_one_result.getFengKe  ', score)
        return score


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
                ftlog.debug('jinan_one_result.isPengpenghu result: False')
                return False
            elif hTileArr[tileIndex] == 4:
                ftlog.debug('jinan_one_result.isPengpenghu result: False')
                return False

        if duiCount == 1 and keCount >= 0:
            ftlog.debug('jinan_one_result.isPengpenghu result: True')
            return True
        else:
            ftlog.debug('jinan_one_result.isPengpenghu result: False')
            return False



    def calcWin(self):
        """
        济南赢牌算分
        """
        # ## 清理
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
            if self.qiangGang:
                winMode[self.winSeatId] = MOneResult.WIN_MODE_QIANGGANGHU

        score = [0 for _ in range(self.playerCount)]
        # 底分 配置项的底分
        baseScore = self.tableTileMgr.tableConfig.get(MTDefine.WIN_BASE, 1)

        ftlog.debug('jinan_one_result.calcWin baseScore=====', baseScore)

        # ## 算杠分
        gangscore = 0  # 杠牌得分
        gangList = self.playerGangTiles[self.winSeatId]
        for ga in gangList:
            if MTile.getColor(ga['pattern'][0]) == 3:
                gangscore += 1

            if ga['style'] == 0:  # 暗杠
                gangscore += 2
            else:
                gangscore += 1

        baseScore = baseScore + gangscore
        ftlog.debug('jinan_one_result.calcWin baseScore=====', baseScore, ' gangscore:', gangscore)

        # ## 算风刻分
        baseScore = baseScore + self.getFengKe()
        ftlog.debug('jinan_one_result.calcWin baseScore=====', baseScore, ' getFengKe:', self.getFengKe())

        # #算花分
        huaScore = len(self.tableTileMgr.flowerTiles(self.winSeatId))
        baseScore = baseScore + huaScore
        ftlog.debug('jinan_one_result.calcWin baseScore=====', baseScore, ' huaScore:', huaScore)


        # 胡型判断
        if self.isDadiaoche():  # 大吊车
            ftlog.debug('jinan_one_result.calcWin isDadiaoche=====', self.isDadiaoche())
            fx = self.fanXing[self.DADIAOCHE]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
        if self.tableTileMgr.isHaidilao():  # 海底捞月
            ftlog.debug('jinan_one_result.calcWin isHaidilao=====', self.tableTileMgr.isHaidilao())
            fx = self.fanXing[self.HAIDILAO]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
        if self.gangKai:  # 杠呲
            ftlog.debug('jinan_one_result.calcWin isGangKai=====', self.gangKai)
            fx = self.fanXing[self.GANGCI]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
        if self.huaCi:  # 花呲
            ftlog.debug('jinan_one_result.calcWin isHuaCi=====', self.huaCi)
            fx = self.fanXing[self.HUACI]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2
        if self.tingState[self.winSeatId]:  # 明搂
            ftlog.debug('jinan_one_result.calcWin isMingLou=====', self.tingState[self.winSeatId])
            fx = self.fanXing[self.MINGLOU]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2


        ####牌型判断
        if self.isFlowerHu():  # 花胡
            fx = self.fanXing[self.FLOWERHU]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 1

        if self.isQingyise():  # 清一色
            ftlog.debug('jinan_one_result.calcWin isQingyise=====', self.isQingyise())
            fx = self.fanXing[self.QINGYISE]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 4
        elif self.isHunyise():  # 混一色
            fx = self.fanXing[self.HUNYISE]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2

        if self.isQidui():
            if self.isQiduiHao():  # 豪华七小对
                ftlog.debug('jinan_one_result.calcWin isQiduiHao=====', self.isQiduiHao())
                fx = self.fanXing[self.HHQIXIAODUI]
                self.addWinFanPattern(fx['name'], fx['index'])
                baseScore = baseScore * 4
            else:  # 七小对
                ftlog.debug('jinan_one_result.calcWin isQidui=====', self.isQidui())
                fx = self.fanXing[self.QIXIAODUI]
                self.addWinFanPattern(fx['name'], fx['index'])
                baseScore = baseScore * 2

        elif self.isPengpenghu():  # 碰碰胡
            ftlog.debug('jinan_one_result.calcWin isPengpenghu=====', self.isPengpenghu())
            fx = self.fanXing[self.PENGPENGHU]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2

        elif self.isQuanjiang():  # 全将
            ftlog.debug('jinan_one_result.calcWin isQuanjiang=====', self.isQuanjiang())
            fx = self.fanXing[self.QUANJIANG]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2

        elif self.is13BuKao():  # 十三不靠
            ftlog.debug('jinan_one_result.calcWin is13BuKao=====', self.is13BuKao())
            fx = self.fanXing[self.BUKAO13]
            self.addWinFanPattern(fx['name'], fx['index'])
            baseScore = baseScore * 2


        ftlog.debug('jinan_one_result.calcWin baseScore=====', baseScore)


        #### 胡法判断
        if isZiMo:  # 自摸
            score = [-baseScore for _ in range(self.playerCount)]
            score[self.winSeatId] = (self.playerCount - 1) * baseScore
        else:  # 点炮
            if self.qiangGang:  # 抢杠包三家
                score = [0 for _ in range(self.playerCount)]
                score[self.winSeatId] = (self.playerCount - 1) * baseScore
                score[self.lastSeatId] = -(self.playerCount - 1) * baseScore
            else:
                score[self.lastSeatId] = -baseScore
                score[self.winSeatId] = baseScore

        #### 跑分计算
        if isZiMo:  # 自摸 自己的飘 + 别人的飘 + 必票*n
            for loose in range(self.playerCount):
                if loose != self.winSeatId:
                    piao = self.piaoProcessor.getPiaoPointsBySeats(self.winSeatId, loose)  # 算飘的分
                    ftlog.debug('jinan_one_result.calcWin isZiMo.piao=====', piao)
                    score[loose] -= piao
                    score[self.winSeatId] += piao

        else:  # 点炮
            if self.qiangGang:  # 抢杠包三家
                for loose in range(self.playerCount):
                    if loose != self.winSeatId:
                        piao = self.piaoProcessor.getPiaoPointsBySeats(self.winSeatId, loose)  # 算飘的分
                        score[self.lastSeatId] -= piao
                        score[self.winSeatId] += piao
            else:
                piao = self.piaoProcessor.getPiaoPointsBySeats(self.winSeatId, self.lastSeatId)  # 算飘的分
                ftlog.debug('jinan_one_result.calcWin dianpao.piao=====', piao)
                score[self.lastSeatId] -= piao
                score[self.winSeatId] += piao

        piaoPoints = {}
        piaoPoints['points'] = [self.piaoProcessor.piaoPoints[seat] for seat in range(self.playerCount)]  # 给前端显示票分
        flowerScores = {}
        flowerScores['scores'] = [self.tableTileMgr.flowerScores(seat) for seat in range(self.playerCount)]  # 给前端显示花分

        # 最大番统计(改成单局最佳)
        resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN: score[self.winSeatId]})

        self.results[self.KEY_TYPE] = '和牌'
        self.results[self.KEY_NAME] = fanXing['name']
        self.results[self.KEY_SCORE] = score
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        fanPattern[self.winSeatId] = self.winFanPattern
        ftlog.debug('jinan_one_result.calcWin result fanPattern:', fanPattern)
        self.results[self.KEY_FAN_PATTERN] = fanPattern
        self.results[self.KEY_PIAO_POINTS] = piaoPoints
        self.results[self.KEY_FLOWER_SCORES] = flowerScores

    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
        self.serialize()

        if self.resultType == self.RESULT_WIN:
            self.calcWin()
        elif self.resultType == self.RESULT_FLOW:
            piaoPoints = {}
            piaoPoints['points'] = [self.piaoProcessor.piaoPoints[seat] for seat in range(self.playerCount)]  # 给前端显示票分
            flowerScores = {}
            flowerScores['scores'] = [self.tableTileMgr.flowerScores(seat) for seat in range(self.playerCount)]  # 给前端显示花分

            self.results[self.KEY_TYPE] = ''
            self.results[self.KEY_NAME] = '流局'
            score = [0 for _ in range(self.playerCount)]
            self.results[self.KEY_SCORE] = score
            winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
            self.results[self.KEY_WIN_MODE] = winMode
            resultStat = [[] for _ in range(self.playerCount)]
            self.results[self.KEY_STAT] = resultStat
            self.results[self.KEY_PIAO_POINTS] = piaoPoints
            self.results[self.KEY_FLOWER_SCORES] = flowerScores

     
     
    def calcGang(self):
        """计算杠的输赢"""
        pass

            
if __name__ == "__main__":
    result = MJinanOneResult()
