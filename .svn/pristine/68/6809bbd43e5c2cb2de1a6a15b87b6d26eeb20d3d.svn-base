# -*- coding=utf-8
'''
Created on 2016年9月23日

一条和牌结果

@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.player.hand.hand import MHand
from majiang2.player.player import MPlayerTileGang
from majiang2.table.table_config_define import MTDefine
from majiang2.tile_pattern_checker.jipinghu_tile_pattern_checker import MJiPingHuTilePatternChecker
from majiang2.win_loose_result.one_result import MOneResult
import copy


class MJiPingHuOneResult(MOneResult):
    '''
    血战到底麻将胡牌方式说明


    特殊牌型
    0）平胡                          X1
    1）对对胡     4刻子+1将牌        X2
    2）清一色     一门花色           X4
    3) 七对                        X4
    4) 清七对     清一色+七对        X16
    5) 龙七对     手牌中有一刻       X8
    6) 清对       清一色+碰碰胡      X8
    7) 清龙七对   清一色+龙七对      X32
    8) 全幺九    所有组成的顺子、刻子、将牌都包含1或9   X4
    9) 清幺九    全幺九+清一色      X16
    10) 将对     2、5、8组成的对对胡      X8
    11) 龙将对   全是2、5、8组成的龙七对    X16
    12) 金钩钩   胡牌中只剩下一张牌（单吊）  X4
    13) 清金钩钩 清一色+金钩钩         X16
    14) 将金钩钩 碰、杠牌全部为2、5、8 + 金钩钩 X16
    15) 十八罗汉 4个杠+1将牌     X64
    16) 清十八罗汉  清一色+十八罗汉   X256
    17) 门清   胡牌时，没有碰、杠牌   X2
    18) 断幺九  胡牌时没有1和9    X2
    19) 海底捞月  最后一张牌胡   X2
    20) 海底炮 最后一张点炮，接炮人算海底炮  X2
     
    胡牌方式
    1）点炮
    1.1 普通点炮，点炮者和胡牌者结算
    1.2 一炮多响，点炮者和每一个胡牌者结算
    2）自摸
    3）抢杠胡
    抢杠胡对于胡牌的人算自摸，赢三家的钱，不同的地方在于由被抢杠的人包庄。
    4）杠牌
    4.1 杠上花
    4.2 抢杠胡
  
    5）算分
    分数 = 番型 + 杠牌
 
    '''
    # 和牌的番型
    ANGANG = 'ANGANG'
    MINGGANG = 'MINGGANG'
    XUGANG = 'XUGANG'
    GENZHUANG = 'GENZHUANG'
    TIANHU = 'TIANHU'
    DIHU = 'DIHU'
    
    # 和牌的方式
    HAIDILAOYUE = 'HAIDILAOYUE'
    HAIDIPAO = 'HAIDIPAO'
    GANGKAI = 'GANGKAI'
    GANGKAIHAIDI = 'GANGKIHAIDI'
    GANGSHANGPAO = 'GANGSHANGPAO'
    QIANGGANGHU = 'QIANGGANGHU'
    ZIMO = 'ZIMO'
    WULAIJIABEI = 'WULAIJIABEI'
    YIPAODUOXIANG = 'YIPAODUOXIANG'
    DIANPAO = 'DIANPAO'

    FENGQUAN = 'FENGQUAN'
    FENGWEI = 'FENGWEI'
    ZHONGFABAI = 'ZHONGFABAI'

    CHANGE_SCORE_GEN = 'genzhuangScore'
    CHANGE_SCORE_GANG = 'gangScore'
    CHANGE_SCORE_WIN = 'winScore'

    def __init__(self, tilePatternChecker, playerCount):
        super(MJiPingHuOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = copy.deepcopy(self.tilePatternChecker.fanXing)

        #index为倍数，不是蕃数
        self.fanXing[self.DIANPAO] = {"name":"点炮", "index":1}
        self.fanXing[self.HAIDILAOYUE] = {"name":"海底捞月", "index": 4}
        self.fanXing[self.HAIDIPAO] = {"name":"海底炮", "index": 4}
        self.fanXing[self.GANGKAIHAIDI] = {'name': '杠上开花 海底捞月', 'index': 4}
        self.fanXing[self.ANGANG] = {"name":"暗杠", "index":2}  # 暗杠
        self.fanXing[self.MINGGANG] = {"name":"明杠", "index": 1}  # 明杠
        self.fanXing[self.XUGANG] = {"name": "蓄杠", "index": 1}  # 蓄杠
        self.fanXing[self.GENZHUANG] = {"name": "跟庄", "index": 1}
        self.fanXing[self.GANGKAI] = {"name":"杠开", "index": 4}
        self.fanXing[self.GANGSHANGPAO] = {"name": "杠上炮", "index": 4}
        self.fanXing[self.QIANGGANGHU] = {"name": "抢杠胡", "index": 2}
        self.fanXing[self.TIANHU] = {"name": "天胡", "index": 64}
        self.fanXing[self.DIHU] = {"name": "地胡", "index": 64}
        self.fanXing[self.ZIMO] = {"name": "自摸", "index": 1}
        self.fanXing[self.WULAIJIABEI] = {"name": "无鬼加倍", "index": 2}
        self.fanXing[self.YIPAODUOXIANG] = {"name": "一炮多响", "index": 1}

        self.fanXing[self.FENGQUAN] = {"name": "风圈", "index": 2}
        self.fanXing[self.FENGWEI] = {"name": "风位", "index": 2}
        self.fanXing[self.ZHONGFABAI] = {"name": "三元牌", "index": 2}


        '''
        self.__fan_xing = copy.deepcopy(self.tilePatternChecker.fanXing)
        self.fanXing[self.DIANPAO] = {"name":"点炮", "index":1}
        self.fanXing[self.HAIDILAOYUE] = {"name":"海底捞月", "index": 2}
        self.fanXing[self.HAIDIPAO] = {"name":"海底炮", "index": 2}
        self.fanXing[self.ANGANG] = {"name":"暗杠", "index":1}  # 暗杠
        self.fanXing[self.MINGGANG] = {"name":"明杠", "index": 0}  # 明杠
        self.fanXing[self.XUGANG] = {"name": "蓄杠", "index": 0}  # 蓄杠
        self.fanXing[self.GENZHUANG] = {"name": "跟庄", "index": 0}
        self.fanXing[self.GANGKAI] = {"name":"杠开", "index": 2}
        self.fanXing[self.GANGSHANGPAO] = {"name": "杠上炮", "index": 2}
        self.fanXing[self.QIANGGANGHU] = {"name": "抢杠胡", "index": 1}
        self.fanXing[self.TIANHU] = {"name": "天胡", "index": 6}
        self.fanXing[self.DIHU] = {"name": "地胡", "index": 6}
        self.fanXing[self.ZIMO] = {"name": "自摸", "index": 1}
        self.fanXing[self.YIPAODUOXIANG] = {"name": "一炮多响", "index": 0}
        '''


    @property
    def fanXing(self):
        return self.__fan_xing
    
    def setfanXing(self, fanXing):
        self.__fan_xing = fanXing

    # 根据玩家位置来确定玩家之间的关系
    def getLocationInfo(self, seatId1, seatId2):
        if seatId1 == seatId2:
            return "本家"
        res = ""
        seatIdVal = seatId1 - seatId2
        if self.playerCount == 4:
            if seatIdVal == 2 or seatIdVal == -2:
                res = "对家"
            elif seatIdVal == -3 or seatIdVal == 1:
                res = "上家"
            elif seatIdVal == -1 or seatIdVal == 3:
                res = "下家" 
        elif self.playerCount == 3:
            if seatIdVal == 2 or seatIdVal == -1:
                res = "上家"
            elif seatIdVal == 1 or seatIdVal == -2:
                res = "下家"
        else:
            res = "对家"
            
        return res
    
    def isHaidilao(self, winId):
        """
        海底捞：最后一张牌自摸和牌
        """  
        if self.lastSeatId == winId:
            if self.tableTileMgr and self.tableTileMgr.getTilesLeftCount() == 0:
                ftlog.debug('MJiPingHuOneResult.isHaidilao result: True')
                return True
        
        ftlog.debug('MJiPingHuOneResult.isHaidilao result: False')
        return False

    def isHaiDiPao(self, winId):
        """
        海底炮：最后一张牌点炮
        """  
        if self.lastSeatId != winId:
            if self.tableTileMgr and self.tableTileMgr.getTilesLeftCount() == 0:
                ftlog.debug('MJiPingHuOneResult.isHaiDiPao result: True')
                return True
        
        ftlog.debug('MJiPingHuOneResult.isHaiDiPao result: False')
        return False
    
    def isYiPaoDuoXiang(self):
        '''
        一炮多响 同时有多个赢家
        '''
        ftlog.debug('MJiPingHuOneResult.isYiPaoDuoXiang winSeats:', self.winSeats)
        if len(self.winSeats) > 1:
            return True
        else:
            return False

    def isTianHu(self, allTiles, seatId, bankerId):
        ''' 天胡
        在打牌过程中，庄家第一次摸完牌就胡牌，叫天胡
        '''
        if seatId != bankerId:
            return False
        if len(allTiles[MHand.TYPE_PENG]) != 0 or len(allTiles[MHand.TYPE_GANG]) != 0:
            return False
        ftlog.debug('MJiPingHuOneResult.isTianHu addTiles: ', self.tableTileMgr.addTiles[seatId])
        # 只摸了一张牌
        if len(self.tableTileMgr.addTiles[seatId]) == 1:
            return True
        else:
            return False

    def isDiHu(self, allTiles, seatId, bankerId):
        '''地胡
        在打牌过程中，非庄家第一次摸完牌后可以下叫，第一轮摸牌后就胡牌，叫地胡
        '''
        if seatId == bankerId:
            return False
        if len(allTiles[MHand.TYPE_PENG]) != 0 or len(allTiles[MHand.TYPE_GANG]) != 0:
            return False
        ftlog.debug('MJiPingHuOneResult.isDiHU addTiles: ', self.tableTileMgr.addTiles[seatId])
        # 只摸了一张牌
        if len(self.tableTileMgr.addTiles[seatId]) == 1:
            return True
        else:
            return False

    '''
    # 计算 赢家 输家的对局流水信息 fanSymbolList:番型  scores：扣分 winSeatId:赢家ID loosSeatId：输家ID
    def processDetailResult(self, iszimo, winSeatIds, loosSeatIds, fanSymbolList, beiShu, scores, isSelfFlag=False):
        ftlog.debug('MJiPingHuOneResult.processDetailResult fanSymbol:', fanSymbolList
                    , 'scores:', scores
                    , 'winSeatIds:', winSeatIds
                    , 'loosSeatIds:', loosSeatIds
                    )


        detailDesc = [['', '', 0, ''] for _ in range(self.playerCount)]
        if iszimo:
            detailDesc[winSeatIds[0]][self.INDEX_DESCPATTERN] = "自摸三家"
            for seatId in loosSeatIds:
                detailDesc[seatId][self.INDEX_DESCPATTERN] = "被自摸"
        else:
            for seatId in winSeatIds:
                detailDesc[seatId][self.INDEX_DESCPATTERN] = "xx点炮"

            for seatId in loosSeatIds:
                detailDesc[seatId][self.INDEX_DESCPATTERN] = "点炮"

        detailDesc[winSeatId][self.INDEX_FANPATTERN] = "+" + str(beiShu * len(loosSeatIds)) + "倍"
        for seatId in loosSeatIds:
            detailDesc[seatId][self.INDEX_FANPATTERN] = "-" + str(beiShu) + "倍"
            
        # 积分变化
        detailDesc[winSeatId][self.INDEX_SCORE] = scores[winSeatId]
        for seatId in loosSeatIds:
            detailDesc[seatId][self.INDEX_SCORE] = scores[seatId]
        
        # 对家位置  
        if len(loosSeatIds) == 1:
            detailDesc[winSeatId][self.INDEX_DESCID] = self.getLocationInfo(loosSeatIds[0], winSeatId)
        elif len(loosSeatIds) == 2:
            detailDesc[winSeatId][self.INDEX_DESCID] = "两家"
        else:
            detailDesc[winSeatId][self.INDEX_DESCID] = "三家"
        for seatId in loosSeatIds:
            detailDesc[seatId][self.INDEX_DESCID] = self.getLocationInfo(winSeatId, seatId)
        
        return detailDesc
        # 计算 赢家 输家的对局流水信息 fanSymbolList:番型  scores：扣分 winSeatId:赢家ID loosSeatId：输家ID

    '''
    def processDetailResult(self, iszimo, pattern, totalWinbeis, totalScores, winSeatIds, loosSeatIds):

        detailDesc = [['', '', 0, ''] for _ in range(self.playerCount)]

        if len(pattern) != 0: #isgang:
            for seatId in winSeatIds:
                detailDesc[seatId][self.INDEX_DESCPATTERN] = self.fanXing[pattern[0]]['name']
            for seatId in loosSeatIds:
                namePattern = self.getLocationInfo(seatId, winSeatIds[0])
                detailDesc[seatId][self.INDEX_DESCPATTERN] = namePattern + self.fanXing[pattern[0]]['name']
        else:
            if iszimo:
                detailDesc[winSeatIds[0]][self.INDEX_DESCPATTERN] = "自摸三家"
                for seatId in loosSeatIds:
                    namePattern = self.getLocationInfo(seatId, winSeatIds[0])
                    detailDesc[seatId][self.INDEX_DESCPATTERN] = namePattern + "自摸"
            else:
                losenamePattern = ""
                for seatId in winSeatIds:
                    detailDesc[seatId][self.INDEX_DESCPATTERN] = self.getLocationInfo(seatId, loosSeatIds[0]) + "点炮"
                    losenamePattern += self.getLocationInfo(loosSeatIds[0], seatId)
                detailDesc[loosSeatIds[0]][self.INDEX_DESCPATTERN] = losenamePattern + "吃胡"

        for seatid in range(self.playerCount):
            if totalWinbeis[seatid]>0:
                detailDesc[seatid][self.INDEX_FANPATTERN] = "+" + str(totalWinbeis[seatid]) + "倍"
                detailDesc[seatid][self.INDEX_SCORE] = totalScores[seatid]
            elif totalWinbeis[seatid]<0:
                detailDesc[seatid][self.INDEX_FANPATTERN] = "-" + str(abs(totalWinbeis[seatid])) + "倍"
                detailDesc[seatid][self.INDEX_SCORE] = totalScores[seatid]
        
        return detailDesc


    def processGenDetailResult(self, beishu, scores, loosSeatId, winSeatids):
        ftlog.debug('MJiPingHuOneResult.processGenDetailResult scores:', scores
                    , 'loosSeatId:', loosSeatId
                    , 'winSeatids:', winSeatids
                    )

        namePattern = "跟庄"

        detailDesc = [['', '', 0, ''] for _ in range(self.playerCount)]

        detailDesc[loosSeatId][self.INDEX_DESCPATTERN] = "被" + namePattern
        for seatId in winSeatids:
            detailDesc[seatId][self.INDEX_DESCPATTERN] = namePattern

        detailDesc[loosSeatId][self.INDEX_FANPATTERN] = "-" + str(beishu * 3) + "倍"
        for seatId in winSeatids:
            detailDesc[seatId][self.INDEX_FANPATTERN] = "+" + str(beishu) + "倍"

        # 积分变化
        detailDesc[loosSeatId][self.INDEX_SCORE] = scores[loosSeatId]
        for seatId in winSeatids:
            detailDesc[seatId][self.INDEX_SCORE] = scores[seatId]

        # 对家位置
        detailDesc[loosSeatId][self.INDEX_DESCID] = "三家"

        return detailDesc

    def processHorseDetailResult(self, winSeatIds, scores):
        ftlog.debug('MJiPingHuOneResult.processHorseDetailResult winSeatIds:', winSeatIds
                    )

        detailDesc = [['', '', '', ''] for _ in range(self.playerCount)]

        for seatId in range(self.playerCount):
            if seatId in winSeatIds:
                detailDesc[seatId][self.INDEX_DESCPATTERN] = "买中马"
                detailDesc[seatId][self.INDEX_FANPATTERN] = "赢2倍"
                detailDesc[seatId][self.INDEX_SCORE] = scores[seatId]
                detailDesc[seatId][self.INDEX_DESCID] = "三家"
            else:
                detailDesc[seatId][self.INDEX_DESCPATTERN] = "没买中马"
                detailDesc[seatId][self.INDEX_FANPATTERN] = ""
                detailDesc[seatId][self.INDEX_SCORE] = scores[seatId]
                detailDesc[seatId][self.INDEX_DESCID] = "三家"

        return detailDesc


    def calcGang(self):
        """
         计算杠的输赢
         """
        resultStat = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_FAN_PATTERN] = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_GANG
        fanSymbol = ""
        # 前端需要详细的分数变化

        detailChangeScore = [{self.CHANGE_SCORE_GANG: {}} for _ in range(self.playerCount)]

        base = self.tableConfig.get(MTDefine.GANG_BASE, 1)
        ftlog.info('MJiPingHuOneResult.calcGang GANG_BASE:', base)

        if self.style == MPlayerTileGang.AN_GANG:
            fanSymbol = self.ANGANG
        else:
            if self.lastSeatId != self.winSeatId:
                fanSymbol = self.MINGGANG
            else:
                fanSymbol = self.XUGANG

        beishu = self.fanXing[fanSymbol]['index']
        base *= beishu
        scores = [0 for _ in range(self.playerCount)]
        for loose in self.looseSeats:
            scores[loose] = -base
            detailChangeScore[loose][self.CHANGE_SCORE_GANG]['state'] = 0
        detailChangeScore[self.winSeatId][self.CHANGE_SCORE_GANG]['state'] = 1
        scores[self.winSeatId] = len(self.looseSeats) * base
        # 蓄杠、暗杠都是三家扣分
        if fanSymbol == self.ANGANG or fanSymbol == self.XUGANG:
            self.results[self.KEY_NAME] = self.fanXing[fanSymbol]['name']
            self.results[self.KEY_FAN_PATTERN][self.winSeatId] = [
                [self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]
            for seatId in self.looseSeats:
                namePattern = self.getLocationInfo(seatId, self.winSeatId)
                self.results[self.KEY_FAN_PATTERN][seatId] = [
                    [namePattern + self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]

            if fanSymbol == self.ANGANG:
                resultStat[self.winSeatId].append({MOneResult.STAT_ANGANG: 1})
        else:
            # 明杠 只有放杠、明杠两家改分 刮风
            self.results[self.KEY_NAME] = self.fanXing[fanSymbol]['name']
            self.results[self.KEY_FAN_PATTERN][self.winSeatId] = [
                [self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]
            namePattern = self.getLocationInfo(self.lastSeatId, self.winSeatId)
            self.results[self.KEY_FAN_PATTERN][self.lastSeatId] = [
                [namePattern + self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]
            resultStat[self.winSeatId].append({MOneResult.STAT_MINGGANG: 1})

            beishu = 3
            scores = [3 * a for a in scores]

        key = self.CHANGE_SCORE_GANG

        detailDesc = self.processDetailResult(False,[fanSymbol], scores, scores, [self.winSeatId], self.looseSeats)

        self.results[self.KEY_SCORE] = scores
        self.results[self.KEY_SCORE_TEMP] = scores
        self.results[self.KEY_GANG_STYLE_SCORE] = base
        self.results[self.KEY_STAT] = resultStat
        self.results[self.KEY_DETAIL_DESC_LIST] = [detailDesc]
        self.results[self.KEY_DETAIL_CHANGE_SCORES] = detailChangeScore
        ftlog.debug('MJiPingHuOneResult.calcGang results:', self.results)

    def getGangIdsFromScore(self, scores):
        winerIds = []
        for seatId in range(self.playerCount):
            if scores[seatId] < 0:
                winerIds.append(seatId)
        ftlog.debug('MJiPingHuOneResult.getGangIdsFromScore winerIds:', winerIds)
        return winerIds

    def calcGenzhuang(self):
        """
         计算跟庄的输赢
         """
        resultStat = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_FAN_PATTERN] = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_GEN
        fanSymbol = ""
        detailGenZhuang = {}
        detailChangeScore = [{self.CHANGE_SCORE_GEN: {}} for _ in range(self.playerCount)]

        base = self.tableConfig.get(MTDefine.GANG_BASE, 1)
        if self.tableConfig.get(MTDefine.GENZHUANGJIABEI, MTDefine.GENZHUANGJIABEI_NO):
            base *= 2

        ftlog.info('MJiPingHuOneResult.calcGenzhuang GANG_BASE:', base)

        fanSymbol = self.GENZHUANG

        loseid = 0
        scores = [0 for _ in range(self.playerCount)]
        for loose in self.looseSeats:
            scores[loose] = -base * 3
            loseid = loose
            detailChangeScore[loose][self.CHANGE_SCORE_GEN]['state'] = 0
        for win in self.winSeats:
            scores[win] = base
            detailChangeScore[win][self.CHANGE_SCORE_GEN]['state'] = 1

        self.results[self.KEY_NAME] = self.fanXing[fanSymbol]['name']
        self.results[self.KEY_FAN_PATTERN][loseid] = [["被" + self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]
        for seatId in self.winSeats:
            self.results[self.KEY_FAN_PATTERN][seatId] = [[self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]
            resultStat[seatId].append({MOneResult.STAT_GENZHUANG: 1})


        detailDesc = self.processGenDetailResult(base, scores, loseid, self.winSeats)
        detailGenZhuang['scores'] = scores
        detailGenZhuang['loseid'] = loseid
        detailGenZhuang['winSeats'] = self.winSeats
        detailGenZhuang['actionId'] = self.actionID
        detailGenZhuang['style'] = self.style
        detailGenZhuang['fanSymbol'] = fanSymbol

        self.results[self.KEY_SCORE] = scores
        self.results[self.KEY_SCORE_TEMP] = scores
        self.results[self.KEY_GENZHUANG_SCORE] = base
        self.results[self.KEY_STAT] = resultStat
        self.results[self.KEY_DETAIL_DESC_LIST] = [detailDesc]
        self.results[self.KEY_DETAIL_GANG_LIST] = detailGenZhuang
        self.results[self.KEY_DETAIL_CHANGE_SCORES] = detailChangeScore
        ftlog.debug('MJiPingHuOneResult.calcGenzhuang results:', self.results)

    def calcWin(self, winSeatIds):
        # 在和牌时统计自摸，点炮，最大番数 初始化
        self.clearWinFanPattern()
        winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
        resultStat = [[] for _ in range(self.playerCount)]
        fanPattern = [[] for _ in range(self.playerCount)]
        fanPatterntotalbeis = [0 for _ in range(self.playerCount)]
        loserFanPattern = [[] for _ in range(self.playerCount)]
        totalScores = [0 for _ in range(self.playerCount)]
        totalWinbeis = [0 for _ in range(self.playerCount)]
        indexs = [0 for _ in range(self.playerCount)]
        dahuDetail = [{} for _ in range(self.playerCount)]
        totalDetailDesc = []
        winBase = self.tableConfig.get(MTDefine.WIN_BASE, 1)
        detailChangeScore = [{self.CHANGE_SCORE_WIN: {}} for _ in range(self.playerCount)]
        isZiMo = False
        if len(winSeatIds) == 1 and self.lastSeatId == winSeatIds[0]:
            isZiMo = True

        for winId in winSeatIds:
            ftlog.debug('calcWin begin winSeatIds:', winSeatIds,'winId:', winId,'self.looseSeats:',self.looseSeats)

            scores = [0 for _ in range(self.playerCount)]
            winBeishus = [0 for _ in range(self.playerCount)]
            winMode[winId] = MOneResult.WIN_MODE_PINGHU
            resultStat[winId].append({MOneResult.STAT_WIN:1})
            fanSymbolList = []
            winAllTiles = self.players[winId].copyTiles()
            # 将胡的那张牌加入到手牌中
            winAllTiles[MHand.TYPE_HAND].append(winAllTiles[MHand.TYPE_HU][-1])
            '''
            和牌两种方式：自摸、点炮
            自摸有一下情况：自摸、海底捞月、天胡、地胡 杠开
            点炮有一下情况：点炮、抢杠胡、海底炮、杠上炮、一炮多响
            '''
            baozhuang = False
            baozhuangid = -1
            fancount1 = 0
            if isZiMo:
                isSelfFlag = True
                resultStat[winId].append({MOneResult.STAT_ZIMO:1})
                winMode[winId] = MOneResult.WIN_MODE_ZIMO 
                
                # 天胡、地胡、海底捞、杠开都是自摸的一种
                if self.isTianHu(winAllTiles, winId, self.bankerSeatId):
                    fanSymbolList.append(self.TIANHU)
                    winMode[winId] = MOneResult.WIN_MODE_TIANHU
                elif self.isDiHu(winAllTiles, winId, self.bankerSeatId):
                    fanSymbolList.append(self.DIHU)
                    winMode[winId] = MOneResult.WIN_MODE_DIHU
                elif self.isHaidilao(winId):
                    fanSymbolList.append(self.HAIDILAOYUE)
                    winMode[winId] = MOneResult.WIN_MODE_HAIDILAOYUE

                if self.isGangShangHua(winId):
                    if self.tableConfig.get(MTDefine.GANGKAIJIABEI, MTDefine.QIANGGANGHUJIABEI_NO):
                        self.fanXing[self.GANGKAI]['index'] *= 2

                    # 杠开 有杠上花 自摸 点炮选项
                    if self.tableConfig.get(MTDefine.FANGGANGKAICHENGBAO, MTDefine.FANGGANGKAICHENGBAO_NO):
                        if self.latestOneResult \
                                and self.latestOneResult.results[self.KEY_TYPE] == self.KEY_TYPE_NAME_GANG \
                                and self.latestOneResult.lastSeatId != winId:
                            dianGangId = self.latestOneResult.lastSeatId
                            winMode[dianGangId] = MOneResult.WIN_MODE_DIANPAO

                            baozhuang = True
                            baozhuangid = dianGangId

                            ftlog.debug('MJiPingHuOneResult.isGangShangHua FANGGANGKAICHENGBAO'
                                        , 'dianGangId:', dianGangId
                                        , 'winId:', winId
                                        , self.tableConfig.get(MTDefine.FANGGANGKAICHENGBAO, MTDefine.FANGGANGKAICHENGBAO_NO)
                                        )

                    if self.isHaidilao(winId):
                        # 杠上花 海底捞 可以叠加，番型只是显示杠上花 只有在点杠花当自摸时 才有
                        ftlog.debug('MJiPingHuOneResult GangKai and HaiDiLao')
                        fanSymbolList.append(self.GANGKAIHAIDI)
                        winMode[winId] = MOneResult.WIN_MODE_GANGKAI_HAIDI
                    else:
                        fanSymbolList.append(self.GANGKAI)
                        winMode[winId] = MOneResult.WIN_MODE_GANGKAI

                if len(fanSymbolList) == 0:
                    fanSymbolList.append(self.ZIMO)     
            else:
                isSelfFlag = False
                resultStat[self.lastSeatId].append({MOneResult.STAT_DIANPAO: 1})
                baozhuang = True
                baozhuangid = self.lastSeatId

                if self.qiangGang:
                    fanSymbolList.append(self.QIANGGANGHU)
                    winMode[winId] = MOneResult.WIN_MODE_QIANGGANGHU
                    winMode[self.lastSeatId] = MOneResult.WIN_MODE_DIANPAO
                    if self.tableConfig.get(MTDefine.QIANGGANGHUJIABEI, 0):
                        self.fanXing[self.QIANGGANGHU]['index'] *= 2
                    if self.tableConfig.get(MTDefine.QIANGGANGCHENGBAO, 0):
                        baozhuang = True
                        baozhuangid = self.lastSeatId
                if self.isHaiDiPao(winId):
                    fanSymbolList.append(self.HAIDIPAO)                  
                    winMode[self.lastSeatId] = MOneResult.WIN_MODE_HAIDIPAO
                if self.isGangShangPao(winId):
                    fanSymbolList.append(self.GANGSHANGPAO)
                    winMode[self.lastSeatId] = MOneResult.WIN_MODE_GANGSHANGPAO  
                    if self.isHaiDiPao(winId):
                        # 海底炮 杠上炮 可以叠加 不显示番型
                        ftlog.debug('MSiChuan GangShangPao and HaiDiPao')
                if self.isYiPaoDuoXiang():
                    fanSymbolList.append(self.DIANPAO)
                    winMode[self.lastSeatId] = MOneResult.WIN_MODE_YIPAODUOXIANG

                if len(fanSymbolList)==0:
                    fanSymbolList.append(self.DIANPAO)
                    winMode[self.lastSeatId] = MOneResult.WIN_MODE_DIANPAO

            isBaohu = False
            self.tilePatternChecker.initChecker(winAllTiles, self.tableTileMgr)
            if self.tableConfig.get(MTDefine.LAIZI, 0):
                fanSymbol, isBaohu = self.tilePatternChecker.getWinFanWithMagic()
            else:
                fanSymbol, isBaohu = self.tilePatternChecker.getWinFanList()

            if isBaohu:
                if self.TIANHU in fanSymbolList or self.DIHU in fanSymbolList:
                    isBaohu = False

            # 爆胡（鸡胡，平胡）自摸＋1
            if self.ZIMO in fanSymbolList:
                if isBaohu:
                    self.fanXing[self.ZIMO]['index'] += 1

            # 爆胡计算风圈风位
            isFengWei = isFengQuan = isZfb = False
            if isBaohu:
                # 风位
                FengWei = [31, 32, 33, 34]
                FengWeiTile = 31 + (winId-self.bankerSeatId+self.playerCount)%self.playerCount
                ftlog.debug('mingsong FengWeiTile:',FengWeiTile,'winId:',winId,'self.bankerSeatId:',self.bankerSeatId)
                if self.tilePatternChecker.hasKeTile(FengWeiTile):
                    fanSymbolList.append(self.FENGWEI)
                    resultStat[winId].append({MOneResult.STAT_FENGWEI: 1})
                    isFengWei = True
                if self.tableType != MTDefine.TABLE_TYPE_NORMAL:
                    # 风圈
                    FengQuan = [31, 32, 33, 34]
                    FengQuanTile = FengQuan[self.quanIndex % self.playerCount]
                    if self.tilePatternChecker.hasKeTile(FengQuanTile):
                        fanSymbolList.append(self.FENGQUAN)
                        resultStat[winId].append({MOneResult.STAT_FENGQUAN: 1})
                        isFengQuan = True
                # 三元牌
                for zfb in [35, 36, 37]:
                    if self.tilePatternChecker.hasKeTile(zfb):
                        fanSymbolList.append(self.ZHONGFABAI)
                        isZfb += 1
                        resultStat[winId].append({MOneResult.STAT_SANYUANPAI: 1})
                    if isZfb == 2:
                        break

            calcBei1 = 1
            for fan in fanSymbolList:
                fancount1 = self.fanXing[fan]['index']
                calcBei1 *= fancount1
            ftlog.debug('MJiPingHuOneResult.calcWin calcBei1:', calcBei1
                        , ' fancount1:', fancount1
                        , ' fanSymbolList:', fanSymbolList
                        )

            calcBei2 = 0
            for fan in fanSymbol:
                # 一些可选番型加倍玩法
                if fan == MJiPingHuTilePatternChecker.QIDUI:
                    if self.tableConfig.get(MTDefine.QIDUIJIABEI, MTDefine.QIDUIJIABEI_YES):
                        self.fanXing[fan]['index'] *= 2
                if fan == MJiPingHuTilePatternChecker.HAOHUAQIDUI:
                    if self.tableConfig.get(MTDefine.HAOHUAQIDUI4BEI, 0):
                        self.fanXing[fan]['index'] *= 4
                fancount2 = self.fanXing[fan]['index']
                #tempbei = pow(2, fancount2)
                tempbei = fancount2
                calcBei2 += tempbei
            fanSymbolList.extend(fanSymbol)
            ftlog.debug('MJiPingHuOneResult.calcWin calcBei2:', calcBei2
                        , ' fanSymbolList:', fanSymbolList
                        )
            #计算总倍数
            if self.TIANHU in fanSymbolList or self.DIHU in fanSymbolList:
                calcBei = calcBei1 + calcBei2
            else:
                calcBei = calcBei1 * calcBei2

            #无赖加倍
            magictiles = self.tableTileMgr.getMagicTiles()
            if len(magictiles) > 0:
                if magictiles[0] not in winAllTiles[MHand.TYPE_HAND]:
                    fanSymbolList.append(self.WULAIJIABEI)
                    calcBei *= 2

            if calcBei > 8 and isBaohu:
                #爆胡封顶8倍
                calcBei = 8
                strShow = ""
                for fan in fanSymbolList:
                    strShow += self.fanXing[fan]['name']
                strShow += "(爆胡)"
                fanPattern[winId].append([strShow, str(8) + "倍"])
            else:
                for fan in fanSymbolList:
                    fanPattern[winId].append([self.fanXing[fan]['name'], str(self.fanXing[fan]['index']) + "倍"])

            resultStat[winId].append({MOneResult.STAT_ZUIDAFAN: calcBei})

            # 填充大胡信息
            if calcBei >= 8 and not isBaohu:
                patternInfo = []
                for fan in fanSymbolList:
                    if fan != MJiPingHuTilePatternChecker.JIHU and fan != MJiPingHuTilePatternChecker.PINGHU:
                        patternInfo.append(self.fanXing[fan]['name'])
                dahuDetail[winId][self.EXINFO_BIGWIN] = patternInfo
                dahuDetail[winId][self.EXINFO_WINTIMES] = calcBei
                dahuDetail[winId][self.EXINFO_JIPING_ISWIN] = 1
                ftlog.debug('MJiPingHuOneResult.dahuDetail:', dahuDetail)

            #填充番型基础倍数
            fanPatterntotalbeis[winId] = calcBei
            # 计算每家输赢倍数
            for looserId in self.looseSeats:
                winBeishus[looserId] -= calcBei
                winBeishus[winId] += calcBei
                fanPatterntotalbeis[looserId] -= calcBei

            # 包赔
            if baozhuang:
                for seatId in range(self.playerCount):
                    if seatId != baozhuangid and winBeishus[seatId]<0:
                        winBeishus[baozhuangid] += winBeishus[seatId]
                        winBeishus[seatId] = 0
            # 设置分数
            for seatId in range(self.playerCount):
                scores[seatId] = winBeishus[seatId]*winBase

            ftlog.debug('MJiPingHuOneResult.calcWin score:', scores
                        , ' winBeishus:', winBeishus
                        , ' baozhuangid:', baozhuangid
                        )

            # 有一炮多响的情况 所以totalScore计算总分
            for index in range(self.playerCount):
                totalScores[index] += scores[index]
                totalWinbeis[index] += winBeishus[index]

            ftlog.debug('calcWin end winSeatIds:', winSeatIds,
                        'winId:', winId,
                        'self.looseSeats:', self.looseSeats,
                        'self.lastSeatId:', self.lastSeatId,
                        'scores:', scores,
                        'totalScores:', totalScores,
                        'calcBei:', calcBei,
                        'winBeishus:', winBeishus,
                        'totalWinbeis:', totalWinbeis
                        )

        # 生成对局流水
        detailDesc = self.processDetailResult(isZiMo, [], totalWinbeis, totalScores, winSeatIds, self.looseSeats)
        totalDetailDesc.append(detailDesc)
        ftlog.debug('processDetailResult isZiMo: ', isZiMo,
                    " totalWinbeis: ", totalWinbeis,
                    " totalScores: ", totalScores,
                    " winSeatIds: ", winSeatIds,
                    " self.looseSeats: ", self.looseSeats,
                    " detailDesc: ", detailDesc)


        horseScore = [0 for _ in range(self.playerCount)]
        if self.tableConfig.get(MTDefine.MAIMA, 0) == MTDefine.MAIMA_ZIMO:
            horseRes, horseScore = self.calcHorseRebuild(isZiMo, calcBei, winBase, totalWinbeis, winSeatIds, totalDetailDesc)
        elif self.tableConfig.get(MTDefine.MAIMA, 0) == MTDefine.MAIMA_ALL:
            horseRes, horseScore = self.calcHorseRebuild(isZiMo, calcBei, winBase, totalWinbeis, winSeatIds, totalDetailDesc)
        for index in range(self.playerCount):
            totalScores[index] += horseScore[index]
        ftlog.debug('MJiPingHuOneResult.totalDetailDesc: ', totalDetailDesc)

        for index in range(self.playerCount):
            if totalScores[index]>0:
                detailChangeScore[winId][self.CHANGE_SCORE_WIN]['state'] = 1
            elif totalScores[index] < 0:
                detailChangeScore[looserId][self.CHANGE_SCORE_WIN]['state'] = 0

        self.setDealyTime(2)

        # 鸡平胡的结果展示，需要区分胡法， 番型， 杠， 买马， 跟庄等信息
        self.results[self.KEY_NAME] = MOneResult.KEY_TYPE_NAME_HU       
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_HU
        self.results[self.KEY_SCORE] = totalScores
        self.results[self.KEY_SCORE_TEMP] = totalScores
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        self.results[self.KEY_DETAIL_DESC_LIST] = totalDetailDesc
        self.results[self.KEY_HORSE] = horseRes
        self.results[self.KEY_HORSE_SCORES] = horseScore
        self.results[self.KEY_FAN_PATTERN] = fanPattern
        self.results[self.KEY_FAN_TOTALBEI_PATTERN] = fanPatterntotalbeis
        self.results[self.KEY_DAHU_DETAIL] = dahuDetail
        self.results[self.KEY_LOSER_FAN_PATTERN] = loserFanPattern
        self.results[self.KEY_DETAIL_CHANGE_SCORES] = detailChangeScore
        ftlog.debug('MJiPingHuOneResult.calcWin result winMode:', winMode, 'scores:', scores, 'fanPattern:', fanPattern
                    , 'horseRes:', horseRes, "dahuDetail: ", dahuDetail, "fanSymbol: ", fanSymbol)
        ftlog.debug("MJiPingHuOneResult.calcWin results: ", self.results, " fanSymbol: ", fanSymbol)

    def countWinnerDifBanker(self):
        tempBankerid = self.bankerSeatId
        ncount = 0
        while tempBankerid != self.winSeatId:
            if tempBankerid == 3:
                tempBankerid = -1
            tempBankerid += 1
            ncount += 1
        return ncount


    """
        根据庄家所在的seatid([0,1,2,3]),来确定当前tile只向哪个位置, 买马用
        banker : 0, 1, 2, 3
        tile: 1-9, 11-19, 21-29, 31-37
        ----庄家： 1，5，9， 东
            下家： 2，6，南，中
            对家： 3，7，西，发
            上家： 4，8，北，白
    """
    def getTileSeatByBanker(self, tile, banker=0):
        if tile >= 35:
            tile += 1
        return ((tile % 10) % 4 + 3 + banker) % 4


    """
        4人买马：
            因为存在一炮多响和自摸，赢家和输家都可以只有一个，也都可能其中一方有多个，买中马的规则，看当前赢家和输家对胡牌的出分数，买中赢家获得
            -->买中赢家：1、赢家买了自己： 输家人数 * 胡牌番型倍数，输家各给一份番型分数
                    2、输家买中， (输家人数 -1)* 番型， 赢家不出分数， 其他输家给一份番型分数
            -->买中输家：1、赢家买中，对玩家所有的输分进行赔付，如果赢家只有自己，则不需要赔付
                    2、输家买中，输家出一份赢家胡牌番型倍数
        自摸买马：
            自摸买马结算为，共可以买N个马（配置），公式：番型倍数*（1+买中马数）
    """

    '''
    四人 'horseResult': [ 1, [[4,1,5,0], [21,0], [18,1], [36,0]]  [256, 256, -256, -256]  ]

    自摸 'horseResult': [2, [4,0, 21,1], [256, 256, -256, -256]]
    '''

    def calcHorseRebuild(self, isZiMo, huBei, basescore, winBeishus, winSeatIds, totalDetailDesc):
        horseResult = []
        horseScores = [0 for _ in range(self.playerCount)]

        '''
        #test return
        horseResult.append(MTDefine.MAIMA_ALL)
        horseTileResult = [[1,0,2,0],[1,0,2,0],[1,0,2,0],[1,0,2,0]]
        horseResult.append(horseTileResult)
        horseResult.append(horseScores)
        return horseResult, horseScores
        '''

        ftlog.debug("MJiPingHu.calcHorseRebuild begin, basescore:", basescore
                    , "winBeishus:", winBeishus
                    , "winSeatIds", winSeatIds
                    , "totalDetailDesc：", totalDetailDesc)

        horseTiles = self.tableTileMgr.horseTiles

        ftlog.debug("MJiPingHu.calcHorseRebuild end, horseResult:", horseResult
                    , "horseScores", horseScores
                    , "totalDetailDesc：", totalDetailDesc)

        maimaType = self.tableConfig.get(MTDefine.MAIMA, 0)
        horseResult.append(maimaType)
        
        maimaCount = self.tableConfig.get(MTDefine.MAIMA_COUNT, 0)
        if maimaType == MTDefine.MAIMA_ZIMO:
            horseTileResult = []
            
            B = [[1, 11, 21, 5, 15, 25, 9, 19, 29, 31]
                 , [2, 12, 22, 6, 16, 26, 32, 35]
                 , [3, 13, 23, 7, 17, 27, 33, 36]
                 , [4, 14, 24, 8, 18, 28, 34, 37]]
            indextemp = self.countWinnerDifBanker()
            B0 = B[indextemp]

            zhongCount = 0
            for tile in horseTiles:
                horseTileResult.append(tile)
                if (tile in B0):
                    zhongCount += 1
                    horseTileResult.append(1)
                else:
                    horseTileResult.append(0)

            ftlog.debug('MJiPingHuOneResult.calcHorse before: ', indextemp
                        , 'horseTile:', horseTiles
                        , 'horseScores:', horseScores
                        )

            # maizhongNum = reduce(lambda x, y: x + y, [ 1 if (self.getTileSeatByBanker(tile, self.bankerSeatId) in winSeatIds) else 0 for tile in self.tableTileMgr.horseTiles], 0)
            horseScores = [-zhongCount * huBei * basescore for _ in range(self.playerCount)]
            horseScores[self.winSeatId] = zhongCount * huBei * basescore * 3
            ftlog.debug('MJiPingHuOneResult.calcHorse. maizhongNum:', zhongCount
                        , 'winBeishus:', winBeishus
                        , 'basescore:', basescore
                        , 'horseScores:', horseScores
                        )
            # 买马 desc
            detailDesc = [['', '', 0, '',0] for _ in range(self.playerCount)]
            if zhongCount >= 1:
                detailDesc[self.winSeatId][self.INDEX_DESCPATTERN] = "买中" + str(zhongCount) + "马"
                detailDesc[self.winSeatId][self.INDEX_FANPATTERN] = "+" + str(zhongCount * huBei * 3) + "倍"
                detailDesc[self.winSeatId][self.INDEX_SCORE] = horseScores[self.winSeatId]
                detailDesc[self.winSeatId][self.INDEX_YES] = 1

                for seat in range(self.playerCount):
                    if seat != self.winSeatId:
                        detailDesc[seat][self.INDEX_DESCPATTERN] = self.getLocationInfo(seat,self.winSeatId) + "买中" + str(zhongCount) + "马"
                        detailDesc[seat][self.INDEX_FANPATTERN] = "-" + str(abs(huBei*zhongCount)) + "倍"
                        detailDesc[seat][self.INDEX_SCORE] = -huBei * zhongCount * basescore
                        detailDesc[seat][self.INDEX_YES] = 1
            totalDetailDesc.append(detailDesc)

        elif maimaType == MTDefine.MAIMA_ALL:
            horseTileResult = [[] for _ in range(self.playerCount)]

            winSeats = []
            loseSeats = []
            # beishu 信息 [64,-64,-64,-64] 或 [64, 0, -64, 0], 如果倍数信息是0则表示不是输家
            for i, bei in enumerate(winBeishus):
                if bei > 0:
                    winSeats.append(i)
                if bei < 0:
                    loseSeats.append(i)

            # 对所有的马牌进行遍历
            for index, tile in enumerate(horseTiles):
                #买中的是哪家
                tileSeat = self.getTileSeatByBanker(tile, self.bankerSeatId)
                #这张马属于哪个玩家
                ownerSeat = index % 4

                horseTileResult[ownerSeat].append(tile)

                if tileSeat in winSeats:
                    #买中赢家（包括赢家买中自己，输家买中赢家），和赢家赢一样的倍数，输家给钱
                    horseTileResult[ownerSeat].append(1)
                    for loseSeat in loseSeats:
                        if ownerSeat != loseSeat:
                            detailDesc = [['', '', 0, '', 0] for _ in range(self.playerCount)]

                            if isZiMo:
                                beishu = abs(winBeishus[loseSeat]) #自摸取 输家输多少倍
                            else:
                                beishu = abs(winBeishus[tileSeat]) #点炮取 赢家赢多少倍

                            horseScores[loseSeat] -= beishu * basescore
                            detailDesc[loseSeat][self.INDEX_DESCPATTERN] = self.getHorseDescBySeatId(ownerSeat, tileSeat,loseSeat, True)
                            detailDesc[loseSeat][self.INDEX_FANPATTERN] = "-" + str(beishu) + "倍"
                            detailDesc[loseSeat][self.INDEX_SCORE] += -beishu * basescore
                            detailDesc[loseSeat][self.INDEX_YES] = 1

                            horseScores[ownerSeat] += beishu * basescore
                            detailDesc[ownerSeat][self.INDEX_DESCPATTERN] = self.getHorseDescBySeatId(ownerSeat, tileSeat, ownerSeat, True)
                            detailDesc[ownerSeat][self.INDEX_FANPATTERN] = "+" + str(beishu) + "倍"
                            detailDesc[ownerSeat][self.INDEX_SCORE] += beishu * basescore
                            detailDesc[ownerSeat][self.INDEX_YES] = 1

                            totalDetailDesc.append(detailDesc)
                elif tileSeat in loseSeats:
                    # 买中输家，和输家输一样的倍数，钱给赢家
                    horseTileResult[ownerSeat].append(0)

                    if ownerSeat in winSeats:#如果赢家买中输家，等于赔付给自己，所以不再计算
                        continue

                    for winSeat in winSeats:
                        #一炮多响，所以是for循环
                        detailDesc = [['', '', 0, '', 0] for _ in range(self.playerCount)]

                        if isZiMo:
                            beishu = abs(winBeishus[tileSeat])  # 自摸取 输家输多少倍
                        else:
                            beishu = abs(winBeishus[winSeat])  # 点炮取 赢家赢多少倍

                        horseScores[ownerSeat] -= beishu * basescore
                        detailDesc[ownerSeat][self.INDEX_DESCPATTERN] = self.getHorseDescBySeatId(ownerSeat, tileSeat,ownerSeat, False)
                        detailDesc[ownerSeat][self.INDEX_FANPATTERN] = "-" + str(beishu) + "倍"
                        detailDesc[ownerSeat][self.INDEX_SCORE] += -beishu * basescore
                        detailDesc[ownerSeat][self.INDEX_YES] = 1

                        horseScores[winSeat] += beishu * basescore
                        detailDesc[winSeat][self.INDEX_DESCPATTERN] = self.getHorseDescBySeatId(ownerSeat, tileSeat, winSeat, False)
                        detailDesc[winSeat][self.INDEX_FANPATTERN] = "+" + str(beishu) + "倍"
                        detailDesc[winSeat][self.INDEX_SCORE] += beishu * basescore
                        detailDesc[winSeat][self.INDEX_YES] = 1

                        totalDetailDesc.append(detailDesc)
                else:
                    horseTileResult[ownerSeat].append(0)

        horseResult.append(horseTileResult)
        horseResult.append(horseScores)

        ftlog.debug("MJiPingHu.calcHorseRebuild end, horseResult:", horseResult
                    , "horseScores", horseScores
                    , "totalDetailDesc：", totalDetailDesc)
        return horseResult, horseScores


    def getHorseDescBySeatId(self, maijiaSeat, maSeat, youSeat, win):

        maijiaLocation = self.getLocationInfo(youSeat, maijiaSeat)
        maLocation = self.getLocationInfo(youSeat, maSeat)
        if win:
            if youSeat == maijiaSeat:
                info = "本家买中马(" + maLocation + ")"
            else:
                info = "" + maijiaLocation + "买中马(" + maLocation + ")"
        else:
            if youSeat == maijiaSeat:
                info = "买输马(" + maLocation + ")"
            else:
                info = "" + maijiaLocation + "买输马(" + maLocation + ")"
        return info

    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
        self.serialize()
    
        if self.resultType == self.RESULT_GANG:
            self.calcGang()
        if self.resultType == self.RESULT_WIN:
            self.calcWin(self.winSeats)
        if self.resultType == self.RESULT_GENZHUANG:
            self.calcGenzhuang()
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

    def updateDetailChangeScore(self, detailChangeScore, key, valueList):
        '''
        用于更新详细的积分变化，变化共分为五个部分：胡牌，呼叫转移，花猪，大叫，退税
        {
            "huaZhu": {
                "state": 1,
                "score": 1
            },
            "daJiao": {
                "state": 1
                "score": 2
            },
            "tuiShui": {
                "state": 1,
                "score": 0
            }
        }
        '''
        for seatId in range(self.playerCount):
            # state 不存在，则表明不参与此事件
            if key in detailChangeScore[seatId] and 'state' not in detailChangeScore[seatId][key]:
                continue

            if key in detailChangeScore[seatId] and 'score' in detailChangeScore[seatId][key]:
                changeScore = detailChangeScore[seatId][key]['score']
            else:
                changeScore = 0
            changeScore += valueList[seatId]
            detailChangeScore[seatId][key]['score'] = changeScore

    def updateStateChangeScore(self, detailChangeScore, key, stateList):
        '''
        用户更新退税的状态，对此退税汇总，只要退过税，则为0
        '''
        for seatId in range(self.playerCount):
            if key in stateList[seatId] and 'state' in stateList[seatId][key]:
                if stateList[seatId][key]['state'] == 0:
                    detailChangeScore[seatId][key]['state'] = 0
                elif 'state' not in detailChangeScore[seatId][key]:
                    detailChangeScore[seatId][key]['state'] = stateList[seatId][key]['state']

    def setCoinScore(self, scoreList):
        '''
        将积分转换的金币保存到result
        :param scoreList:金币值列表
        '''
        ftlog.debug('MSiChuanOneResult setCoinScore before scoreList:', scoreList
                    , 'descInfo:', self.results[self.KEY_DETAIL_DESC_LIST]
                    , 'scores:', self.results[self.KEY_SCORE]
                    , 'scoreList:', scoreList)
        self.results[self.KEY_SCORE] = scoreList
        # 杠牌 胡牌 在这里更新分数详细变化
        if self.KEY_DETAIL_CHANGE_SCORES in self.results:
            ftlog.debug('MSiChuanOneResult setCoinScore before detailChangeScore:',
                        self.results[self.KEY_DETAIL_CHANGE_SCORES])
        if self.results[self.KEY_TYPE] == self.KEY_TYPE_NAME_GANG:
            detailChangeScore = self.results[self.KEY_DETAIL_CHANGE_SCORES]
            self.updateDetailChangeScore(detailChangeScore, self.CHANGE_SCORE_GANG, scoreList)
        elif self.results[self.KEY_TYPE] == self.KEY_TYPE_NAME_GEN:
            detailChangeScore = self.results[self.KEY_DETAIL_CHANGE_SCORES]
            self.updateDetailChangeScore(detailChangeScore, self.CHANGE_SCORE_GEN, scoreList)
        elif self.results[self.KEY_TYPE] == self.KEY_TYPE_NAME_HU:
            detailChangeScore = self.results[self.KEY_DETAIL_CHANGE_SCORES]
            self.updateDetailChangeScore(detailChangeScore, self.CHANGE_SCORE_WIN, scoreList)
        if self.KEY_DETAIL_CHANGE_SCORES in self.results:
            ftlog.debug('MSiChuanOneResult setCoinScore after detailChangeScore:',
                        self.results[self.KEY_DETAIL_CHANGE_SCORES])
        # 金币桌更新一下信息
        if self.tableType != MTDefine.TABLE_TYPE_NORMAL:
            return
            # 对局流水可能是多个 根据对局流水中的比例来获取金币值
        for descInfo in self.results[self.KEY_DETAIL_DESC_LIST]:
            for seatId in range(self.playerCount):
                if self.results[self.KEY_SCORE_TEMP][seatId] == 0:
                    continue
                score = descInfo[seatId][self.INDEX_SCORE]
                descInfo[seatId][self.INDEX_SCORE] = int(
                    scoreList[seatId] * (float(score) / self.results[self.KEY_SCORE_TEMP][seatId]))
        ftlog.debug('MSiChuanOneResult after setCoinScore descInfo:', self.results[self.KEY_DETAIL_DESC_LIST])
        
    def calcMa(self, scores):
        '''
        计算买马的算法
        买马规则：
        买中输家，跟输家输一样的钱；
        买中赢家，跟赢家赢一样的钱；
        
        关键是：
        从当前玩家的角度看输赢的结果
        '''
        playerCount = len(scores)
        wins = []
        looses = []
        observers = []
        scoreDetails = [[0 for _ in range(playerCount)] for _ in range(playerCount)]
        
        for seatId in range(0, playerCount):
            if scores[seatId] > 0:
                wins.append(seatId)
            elif scores[seatId] < 0:
                looses.append(seatId)
            else:
                observers.append(seatId)
                
        # 第一种情况，自摸
        if (len(wins) == 1) and (len(looses) == (playerCount - 1)):
            win = wins[0]
            scoreDetails[win] = scores
            for loose in looses:
                scoreDetails[loose][loose] = scores[loose]
                scoreDetails[loose][win] = abs(scores[loose])
        # 第二种情况，点炮
        elif (len(looses) == 1) and (len(wins) >= 1):
            loose = looses[0]
            scoreDetails[loose] = scores
            for win in wins:
                scoreDetails[win][win] = scores[win]
                scoreDetails[win][loose] = -scores[win]
                
        return wins, looses, scoreDetails
    
def testZiMoMa():
    '''
    测试自摸的买马分析
    '''
    scores = [6, -2, -2, -2]
    
    result = MJiPingHuOneResult()
    result.setTableConfig({})
    wins, looses, scoreDetails = result.calcMa(scores)
    ftlog.debug('testZiMoMa scores', scores
                , ' wins:', wins
                , ' looses:', looses
                , ' details:', scoreDetails)
    
def testDianPaoMa():
    '''
    测试点炮的买马分析
    '''
    scores = [6, -6, 0, 0]
    
    result = MJiPingHuOneResult()
    result.setTableConfig({})
    wins, looses, scoreDetails = result.calcMa(scores)
    ftlog.debug('testDianPaoMa scores:', scores
                , ' wins:', wins
                , ' looses:', looses
                , ' details:', scoreDetails)
    
def testYiPaoDuoXiang():
    '''
    测试一炮多响
    '''
    scores = [-6, 1, 2, 3]
    
    result = MJiPingHuOneResult()
    result.setTableConfig({})
    wins, looses, scoreDetails = result.calcMa(scores)
    ftlog.debug('testYiPaoDuoXiang scores:', scores
                , ' wins:', wins
                , ' looses:', looses
                , ' details:', scoreDetails)

if __name__ == "__main__":
    testZiMoMa()
    testDianPaoMa()
    testYiPaoDuoXiang()
