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


class MPingDuOneResult(MOneResult):
    '''
    平度麻将胡牌方式说明
    
    特殊牌型
    0）普通胡
    1）七对
    2）清一色
    条件：任意花色超过8张，包括杠牌
    
    胡牌方式
    1）点炮
    1.1 普通点炮，点炮者和胡牌者结算
    ''1.2 一炮多响，点炮者和每一个胡牌者结算，一炮多响暂时不做''
    2）自摸
    3）抢杠胡。
    抢杠胡对于胡牌的人算自摸，赢三家的钱，不同的地方在于由被抢杠的人包庄。
    4）杠牌
    4.1 杠开
    4.2 抢杠胡
    4.3 杠呲
    
    5）算分
    5.1 基础分，普通胡1分
    5.2 有杠胡牌加分，每条杠加一分，杠呲不额外算分。杠分不参与明捞翻倍，单独结算。
    5.3 清一色，七对基础分2分
    5.4 明捞算分加倍，输赢都加倍。
    
    5.5 算分举例
    5.5.1 明捞普通胡，2分
    5.5.2 明捞 + 一条杠 3分 = 明捞2 + 杠1
    5.5.3 明捞 + 清一色 [清一色2 + 明捞2] = 4分
    5.5.4 明捞 + 清一色 + 一条杠 [清一色2 + 明捞2] + 杠1 = 5
    5.5.5 明捞 + 清一色 + 七对 [清一色2 + 七对2] + 明捞2 = 6
    
    '''
    
    GANGKAI = 'GANGKAI'
    QIANGGANG = 'QIANGGANG'
    QIDUI = 'QIDUI'
    QINGYISE = 'QINGYISE'
    ZHANGYISE = 'ZHANGYISE'
    MINGLAO = 'MINGLAO'
    PINGHU = 'PINGHU'
    
    def __init__(self, tilePatternChecker, playerCount):
        super(MPingDuOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = {
            self.PINGHU: {"name":"平胡", "index": 0},
            self.GANGKAI: {"name":"杠上开花 ", "index":1},
            self.QIANGGANG: {"name":"抢杠胡 ", "index":1},
            self.QIDUI: {"name": "七对", "index": 1},
            self.ZHANGYISE: {"name": "掌一色", "index": 1},
            self.QINGYISE: {"name": "清一色", "index": 1},
            self.MINGLAO: {"name": "明捞", "index": 1},
        }
        
    @property
    def fanXing(self):
        return self.__fan_xing
    
    def setFanXing(self, fanXing):
        self.__fan_xing = fanXing
        
    def isQingYiSe(self, seatId):
        return self.colorState[seatId] == 1
    
    def isZhangYiSe(self, seatId):
        tiles = MHand.copyAllTilesToList(self.playerAllTiles[self.winSeatId])
        if len(tiles) % 2 > 0:
            tiles.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])
        for tile in tiles:
            if (tile >= MTile.TILE_DONG_FENG) or (MTile.getValue(tile) % 3 != 2):
                return False
        return True
    
    def isQiDui(self, seatId):
        handTile = copy.deepcopy(self.playerAllTiles[self.winSeatId][MHand.TYPE_HAND])
        if len(handTile) % 2 > 0:
            handTile.extend(self.playerAllTiles[self.winSeatId][MHand.TYPE_HU])
        ftlog.debug('pingdu_one_result.isQiDui adjust tiles:', handTile)
        qiduiResult, _ = MWin.isQiDui(handTile)
        return qiduiResult

    def calcWin(self):
        """
        
        """
        self.clearWinFanPattern()
        self.results['type'] = MOneResult.KEY_TYPE_NAME_HU
        # 在和牌时统计自摸，点炮，最大番数
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
            for wSeat in self.winSeats:
                winMode[wSeat] = MOneResult.WIN_MODE_PINGHU
            winMode[self.winSeatId] = MOneResult.WIN_MODE_PINGHU
        
        score = [0 for _ in range(self.playerCount)]
        baseScore = 0
        if self.isQingYiSe(self.winSeatId):
            baseScore += 2
            qingyiSeFanxing = self.fanXing[self.QINGYISE]
            self.addWinFanPattern(qingyiSeFanxing['name'], qingyiSeFanxing['index'])
            
        if self.isQiDui(self.winSeatId):
            baseScore += 2
            qiduiFanxing = self.fanXing[self.QIDUI]
            self.addWinFanPattern(qiduiFanxing['name'], qiduiFanxing['index'])
            
        if self.isZhangYiSe(self.winSeatId):
            baseScore += 2
            zhangFanxing = self.fanXing[self.ZHANGYISE]
            self.addWinFanPattern(zhangFanxing['name'], zhangFanxing['index'])
            
        if 0 == baseScore:
            baseScore = 1
            
        if self.tingState[self.winSeatId]:
            if baseScore == 1:
                baseScore = 2
            else:
                baseScore += 2
            mingLaoFanxing = self.fanXing[self.MINGLAO]
            self.addWinFanPattern(mingLaoFanxing['name'], mingLaoFanxing['index'])
        
        ftlog.debug('pingdu_one_result.calcGang seatId:', self.winSeatId,
                    ' playerGangTiles:', self.playerGangTiles)    
        gangNum = len(self.playerGangTiles[self.winSeatId])
        baseScore += gangNum
        if isZiMo:
            score = [-baseScore for _ in range(self.playerCount)]
            score[self.winSeatId] = (self.playerCount - 1) * baseScore
        else:
            score[self.winSeatId] = baseScore
            score[self.lastSeatId] = -baseScore
            
        if isZiMo:
            for loose in range(self.playerCount):
                if loose == self.winSeatId:
                    continue
                piao = self.piaoProcessor.getPiaoPointsBySeats(self.winSeatId, loose)
                score[loose] -= piao
                score[self.winSeatId] += piao
        else:
            piao = self.piaoProcessor.getPiaoPointsBySeats(self.winSeatId, self.lastSeatId)
            score[self.winSeatId] += piao
            score[self.lastSeatId] -= piao
        
        # 最大番统计(改成单局最佳)
        resultStat[self.winSeatId].append({MOneResult.STAT_ZUIDAFAN:score[self.winSeatId]}) 
        
        self.results[self.KEY_TYPE] = '和牌'
        self.results[self.KEY_NAME] = fanXing['name']
        ftlog.debug('MPingDuOneResult.calcWin result score:', score)
        self.results[self.KEY_SCORE] = score
        ftlog.debug('MPingDuOneResult.calcWin result winMode:', winMode)
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        fanPattern[self.winSeatId] = self.winFanPattern
        ftlog.debug('MPingDuOneResult.calcWin result fanPattern:', fanPattern)
        self.results[self.KEY_FAN_PATTERN] = fanPattern
    
        
    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
        self.serialize()
        
        if self.resultType == self.RESULT_WIN:
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
        """
        计算杠的输赢
        
        pass
        杠的输赢在最终结算的时候算
        
        """
        pass
            
if __name__ == "__main__":
    result = MPingDuOneResult()
    result.setTableConfig({})
