# -*- coding=utf-8
'''
Created on 2016年9月23日

一条和牌结果

@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.play_mode import MPlayMode
from majiang2.player.hand.hand import MHand
from majiang2.player.player import MPlayerTileGang
from majiang2.table.friend_table_define import MFTDefine
from majiang2.table.table_config_define import MTDefine
from majiang2.tile.tile import MTile
from majiang2.win_loose_result.one_result import MOneResult
import copy


class MSiChuanOneResult(MOneResult):
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
    PINGHU = 'PINGHU'
    DUIDUIHU = 'DUIDUIHU'
    QINGYISE = 'QINGYISE'
    QIDUI = 'QIDUI'
    QINGQIDUI = 'QINGQIDUI'
    LONGQIDUI = 'LONGQIDUI'
    QINGDUI = 'QINGDUI'
    QINGLONGQIDUI = 'QINGLONGQIDUI'
    QUANYAOJIU = 'QUANYAOJIU'
    QINGYAOJIU = 'QINGYAOJIU'
    JIANGDUI = 'JIANGDUI'
    JIANGQIDUI = 'JIANGQIDUI'
    LONGJIANGDUI = 'LONGJIANGDUI'
    JINGOUDIAO = 'JINGOUDIAO'
    QINGJINGOUDIAO = 'QINGJINGOUGOU'
    JIANGJINGOUDIAO = 'JIANGJINGOUGOU'
    SHIBALUOHAN = 'SHIBALUOHAN'
    QINGSHIBALUOHAN = 'QINGSHIBALUOHAN'
    MENQING = 'MENQING'
    DUANYAOJIU = 'DUANYAOJIU'
    ANGANG = 'ANGANG'
    XUGANG = 'XUGANG'
    MINGGANG = 'MINGGANG'
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
    YIPAODUOXIANG = 'YIPAODUOXIANG'
    DIANPAO = 'DIANPAO'
    CHAHUAZHU = 'CHAHUAZHU'
    CHADAJIAO = 'CHADAJIAO'
    
    CHANGE_SCORE_WIN = 'winScore'
    CHANGE_SCORE_HUAZHU = 'huazhuScore'
    CHANGE_SCORE_DAJIAO = 'dajiaoScore'
    CHANGE_SCORE_TUISHUI = 'tuishuiScore'
    CHANGE_SCORE_GANG = 'gangScore'
    CHANGE_SCORE_CALLTRAN = 'callTranScore'
    
    def __init__(self, tilePatternChecker, playerCount):
        super(MSiChuanOneResult, self).__init__(tilePatternChecker, playerCount)
        self.__fan_xing = copy.deepcopy(self.tilePatternChecker.fanXing)
        self.fanXing[self.DIANPAO] = {"name":"点炮", "index":1}
        self.fanXing[self.HAIDILAOYUE] = {"name":"海底捞月", "index": 2}
        self.fanXing[self.HAIDIPAO] = {"name":"海底炮", "index": 2}
        self.fanXing[self.ANGANG] = {"name":"下雨", "index":1}  # 暗杠
        self.fanXing[self.XUGANG] = {"name":"刮风", "index": 0}  # 蓄杠
        self.fanXing[self.MINGGANG] = {"name":"刮风", "index": 1}  # 明杠
        self.fanXing[self.GANGKAI] = {"name":"杠上开花", "index": 2}
        self.fanXing[self.GANGSHANGPAO] = {"name": "杠上炮", "index": 2}
        self.fanXing[self.QIANGGANGHU] = {"name": "抢杠胡", "index": 1}
        self.fanXing[self.TIANHU] = {"name": "天胡", "index": 5}
        self.fanXing[self.DIHU] = {"name": "地胡", "index": 5}
        self.fanXing[self.ZIMO] = {"name": "自摸", "index": 1}
        self.fanXing[self.YIPAODUOXIANG] = {"name": "一炮多响", "index": 1}
        self.fanXing[self.CHAHUAZHU] = {"name": "查花猪", 'index': 0}
        self.fanXing[self.CHADAJIAO] = {'name':'查大叫', 'index': 0}
        self.fanXing[self.GANGKAIHAIDI] = {'name':'杠上开花 海底捞月', 'index':4}

        # 是否呼叫转移过
        self.__hasCallTransfer = False
        # 是否需要呼叫转移
        self.__needCallTransfer = False
        # 保存花猪LoserId 
        self.__huaZhuLooseIds = []
        # 保存花猪WinID
        self.__huaZhuWinIds = []
        # 保存大叫LoserId
        self.__daJiaoLooseIds = []
        # 保存大叫Win ID
        self.__daJiaoWinIds = []
        # 计算龙根 番型 龙七对 -1根 清龙七对 -1根 将七对 -1根 十八罗汉 -4根 清十八罗汉 -4根 
        self.__gen_xing = {
            self.LONGQIDUI : 1,
            self.QINGLONGQIDUI : 1,
            self.JIANGQIDUI : 1,
            self.SHIBALUOHAN : 4,
            self.QINGSHIBALUOHAN : 4
        }
    
    @property
    def huaZhuWinIds(self):
        return self.__huaZhuWinIds
    
    def setHuaZhuWinIds(self, seatIds):
        self.__huaZhuWinIds.extend(seatIds)
        
    @property
    def daJiaoWinIds(self):
        return self.__daJiaoWinIds
    
    def setDaJiaoWinIds(self, seatIds):
        self.__daJiaoWinIds.extend(seatIds)
    
    @property
    def daJiaoLooseIds(self):
        return self.__daJiaoLooseIds
    
    def setDaJiaoLooseIds(self, seatIds):
        self.__daJiaoLooseIds.extend(seatIds)
    
    @property
    def huaZhuLooseIds(self):
        return self.__huaZhuLooseIds
    
    def setHuaZhuLooseIds(self, seatIds):
        self.__huaZhuLooseIds.extend(seatIds)
    
    @property
    def needCallTransfer(self):
        return self.__needCallTransfer
    
    def setNeedCallTransfer(self):
        ftlog.debug('MSiChuanOneResult.setNeedCallTransfer True...')
        self.__needCallTransfer = True
    
    @property
    def hasCallTransfer(self):
        return self.__hasCallTransfer
    
    def setHasCallTransfer(self):
        ftlog.debug('MSiChuanOneResult.setHasCallTransfer True...')
        self.__hasCallTransfer = True
       
    @property
    def genXing(self):
        return self.__gen_xing
        
    @property
    def fanXing(self):
        return self.__fan_xing
    
    def setfanXing(self, fanXing):
        self.__fan_xing = fanXing
    
    def setHuaZhuDaJiaoIdTotal(self, huaZhuIdList, daJiaoIdList):
        for seatId in huaZhuIdList:
            if seatId not in self.huaZhuDaJiaoId:
                self.huaZhuDaJiaoId.append(seatId)
    
        for seatId in daJiaoIdList:
            if seatId not in self.huaZhuDaJiaoId:
                self.huaZhuDaJiaoId.append(seatId)
    
    # 根据玩家位置来确定玩家之间的关系
    def getLocationInfo(self, seatId1, seatId2):
        res = ""
        seatIdVal = seatId1 - seatId2
        if self.playerCount == 4:
            if seatIdVal == 2 or seatIdVal == -2:
                res = "对家"
            elif seatIdVal == 3 or seatIdVal == -1:
                res = "上家"
            elif seatIdVal == 1 or seatIdVal == -3:
                res = "下家" 
        elif self.playerCount == 3:
            if seatIdVal == 2 or seatIdVal == -1:
                res = "上家"
            elif seatIdVal == 1 or seatIdVal == -2:
                res = "下家"
        else:
            res = "对家"
            
        return res
    
    def isGameOver(self):
        if self.playMode == MPlayMode.XUEZHANDAODI:
            count = 0
            for player in self.players:
                if player.isObserver():
                    count += 1
            if count >= self.playerCount - 1:
                return True
            else:
                return False
        elif self.playMode == MPlayMode.XUELIUCHENGHE:
            if self.tableTileMgr.getTilesLeftCount() == 0:
                return True
            else:
                return False
       
    def getLongGenCount(self, allTiles):
        '''
        获取玩家手牌根的个数 杠过的牌也算
        ''' 
        count = 0
        tiles = MHand.copyAllTilesToListButHu(allTiles)
        tileArr = MTile.changeTilesToValueArr(tiles)
        for tile in tileArr:
            if tile == 4:
                count += 1
                
        return count
    
   
    def isHaidilao(self, winId):
        """
        海底捞：最后一张牌自摸和牌
        """  
        # 房间配置为0，则没有海底捞月
        if not self.tableConfig.get(MFTDefine.HAIDILAOYUE_DOUBLE, 0):
            ftlog.debug('MSiChuanOneResult.isHaidilao False because roomConfig')
            return False
        if self.lastSeatId == winId:
            if self.tableTileMgr and self.tableTileMgr.getTilesLeftCount() == 0:
                ftlog.debug('MSiChuanOneResult.isHaidilao result: True')
                return True
        
        ftlog.debug('MSiChuanOneResult.isHaidilao result: False')
        return False

    def isHaiDiPao(self, winId):
        """
        海底炮：最后一张牌点炮
        """  
        leftTilesCount = self.tableTileMgr.getTilesLeftCount() if self.tableTileMgr else 0
        ftlog.debug('MSiChuanOneResult.isHaiDiPao winId:', winId
                        , 'lastSeatId:', self.lastSeatId
                        , 'leftTilesCount:', leftTilesCount)
        if self.lastSeatId != winId:
            if self.tableTileMgr and self.tableTileMgr.getTilesLeftCount() == 0:
                ftlog.debug('MSiChuanOneResult.isHaiDiPao result: True')
                return True
        
        ftlog.debug('MSiChuanOneResult.isHaiDiPao result: False')
        return False
    
    def isYiPaoDuoXiang(self):
        '''
        一炮多响 同时有多个赢家
        '''
        ftlog.debug('MSiChuanOneResult.isYiPaoDuoXiang winSeats:', self.winSeats)
        if len(self.winSeats) > 1:
            return True
        else:
            return False

    def isTianHu(self, allTiles, seatId, bankerId):
        ''' 天胡
        在打牌过程中，庄家第一次摸完牌就胡牌，叫天胡
        '''
        # 房间配置为0，则没有天胡
        if not self.tableConfig.get(MFTDefine.TIANDIHU_DOUBLE, 0):
            ftlog.debug('MSiChuanOneResult.isTianHu False because roomConfig')
            return False
        if seatId != bankerId:
            return False
        if len(allTiles[MHand.TYPE_PENG]) != 0 or len(allTiles[MHand.TYPE_GANG]) != 0:
            return False
        ftlog.debug('MSiChuanOneResult.isTianHu addTiles: ', self.tableTileMgr.addTiles[seatId])
        # 只摸了一张牌
        if len(self.tableTileMgr.addTiles[seatId]) == 1:
            return True
        else:
            return False

    def isDiHu(self, allTiles, seatId, bankerId):
        '''地胡
        在打牌过程中，非庄家第一次摸完牌后可以下叫，第一轮摸牌后就胡牌，叫地胡
        '''
        # 房间配置为0，则没有地胡
        if not self.tableConfig.get(MFTDefine.TIANDIHU_DOUBLE, 0):
            ftlog.debug('MSiChuanOneResult.isDiHu False because roomConfig')
            return False
        
        if seatId == bankerId:
            return False
        if len(allTiles[MHand.TYPE_PENG]) != 0 or len(allTiles[MHand.TYPE_GANG]) != 0:
            return False
        ftlog.debug('MSiChuanOneResult.isDiHU addTiles: ', self.tableTileMgr.addTiles[seatId])
        # 只摸了一张牌
        if len(self.tableTileMgr.addTiles[seatId]) == 1:
            return True
        else:
            return False
              
    # 计算 赢家 输家的对局流水信息 fanSymbolList:番型  scores：扣分 winSeatId:赢家ID loosSeatId：输家ID
    def processDetailResult(self, fanSymbolList, scores, winSeatId, loosSeatId, gengNum=0, isSelfFlag=False, ziMoJiaBei=False):
        ftlog.debug('MSiChuanOneResult.processDetailResult fanSymbol:', fanSymbolList
                    , 'scores:', scores
                    , 'winSeatId:', winSeatId
                    , 'loosSeatId:', loosSeatId
                    , 'gengNum: ', gengNum)
        
        for symbol in fanSymbolList:
            ftlog.debug('MSiChuanOneResult.processDetailResult fanSymbol fanSymbol: ', self.fanXing[symbol])
         
        if len(fanSymbolList) > 1 and gengNum != 0:
            namePattern = self.fanXing[fanSymbolList[0]]["name"] + "(" + self.fanXing[fanSymbolList[1]]["name"] + "," + str(gengNum) + "根)"
            indexPattern = self.fanXing[fanSymbolList[0]]["index"] + self.fanXing[fanSymbolList[1]]["index"] + gengNum
        elif len(fanSymbolList) > 1 and gengNum == 0:
            namePattern = self.fanXing[fanSymbolList[0]]["name"] + "(" + self.fanXing[fanSymbolList[1]]["name"] + ")"
            indexPattern = self.fanXing[fanSymbolList[0]]["index"] + self.fanXing[fanSymbolList[1]]["index"]
        elif len(fanSymbolList) == 1 and gengNum != 0:
            namePattern = self.fanXing[fanSymbolList[0]]["name"] + "(" + str(gengNum) + "根)"
            indexPattern = self.fanXing[fanSymbolList[0]]["index"] + gengNum
        else: 
            namePattern = self.fanXing[fanSymbolList[0]]["name"]
            indexPattern = self.fanXing[fanSymbolList[0]]["index"]
            
        detailDesc = [['', '', 0, ''] for _ in range(self.playerCount)]
        # 抢杠胡 对局流水与自摸显示 类似 抢杠胡 被抢杠胡
        if isSelfFlag or self.qiangGang:
            detailDesc[winSeatId][self.INDEX_DESCPATTERN] = namePattern
            for seatId in loosSeatId:
                detailDesc[seatId][self.INDEX_DESCPATTERN] = "被" + namePattern
        else:
            detailDesc[winSeatId][self.INDEX_DESCPATTERN] = "被" + namePattern
            for seatId in loosSeatId:
                detailDesc[seatId][self.INDEX_DESCPATTERN] = namePattern
        
        ziMoVal = 1 if ziMoJiaBei else 0  
        detailDesc[winSeatId][self.INDEX_FANPATTERN] = str(pow(2, indexPattern) + ziMoVal) + "倍"
        for seatId in loosSeatId:
            detailDesc[seatId][self.INDEX_FANPATTERN] = str(pow(2, indexPattern) + ziMoVal) + "倍"
            
        # 积分变化
        detailDesc[winSeatId][self.INDEX_SCORE] = scores[winSeatId]
        for seatId in loosSeatId:
            detailDesc[seatId][self.INDEX_SCORE] = scores[seatId]
        
        # 对家位置  
        if len(loosSeatId) == 1:
            detailDesc[winSeatId][self.INDEX_DESCID] = self.getLocationInfo(loosSeatId[0], winSeatId)
        elif len(loosSeatId) == 2:
            detailDesc[winSeatId][self.INDEX_DESCID] = "两家"
        else:
            detailDesc[winSeatId][self.INDEX_DESCID] = "三家"
        for seatId in loosSeatId:
            detailDesc[seatId][self.INDEX_DESCID] = self.getLocationInfo(winSeatId, seatId)
        
        return detailDesc

    # 获取听牌玩家 的番型
    def getMaxFanByTing(self, winId):
        ftlog.debug('MSiChuanOneResult.getMaxFanByTing seatId:', winId, 'winNodes:', self.players[winId].winNodes)
        bestFanIndex = 0
        for winNode in self.players[winId].winNodes:
            allTiles = self.players[winId].copyTiles()
            allTiles[MHand.TYPE_HAND].append(winNode['winTile'])
            self.tilePatternChecker.initChecker(allTiles, self.tableTileMgr)
            fanSymbol = self.tilePatternChecker.getFanSymbolFromAllTiles()
            fanSymbolIndex = self.fanXing[fanSymbol]['index']
            genIndex = self.getLongGenCount(allTiles)
            totalIndex = genIndex + fanSymbolIndex
            ftlog.debug('MSichuanOneResult.getMaxFanByTing fanSymbol:', fanSymbol, 'genIndex:', genIndex)
            # 去除掉番型不叠加的根数
            if fanSymbol in self.genXing:
                totalIndex -= self.genXing[fanSymbol]
            
            if bestFanIndex < totalIndex:
                bestFanIndex = totalIndex
        # 查看是否超过封顶倍数
        maxFan = self.tableConfig.get(MTDefine.MAX_FAN, 0)
        bestFanScore = self.calcFanKmodel(totalIndex, maxFan)
        ftlog.debug('MSiChuanOneResult.getMaxFanByTing bestFanScore:', bestFanScore)
        return bestFanScore
    
    # 番数转化成倍数
    def calcFanKmodel(self, fan, maxFan):
        '''
        :param maxFlag: 是否封顶 算番型 金币场无封顶 花猪大叫有封顶
        '''
        beiVal = pow(2, fan)
        if beiVal > maxFan and maxFan > 0:
            beiVal = maxFan
        return beiVal
       
    def getBestFanSymbol(self, winResults):
        '''
        从众多番型中，获取分值最大的番型
            winResults [{}, {}] 
            return {}
        '''
        maxIndex = 0
        maxFan = {}
        for fanSymbol in winResults:
            if fanSymbol['index'] > maxIndex:
                maxInde = fanSymbol['index']
                maxFan = fanSymbol
        ftlog.debug('MSiChuanOneResult.getBestFanSymbol maxFan:', maxFan
                    , ' maxInde:', maxInde)
        return maxFan
   
    def getFanPatternListByResults(self, results):
        fanIndex = self.tableConfig.get(MTDefine.FAN_LIST, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        fanPatternList = []
        names = []
        for result in results:
            ftlog.debug('MSiChuanOneResult.getFanByResults result=', result)
            name = result['name']
            if result['index']:
                fan = [result['name'], str(fanIndex[result['index']]) + "倍"]
            else:
                fan = [result['name'], "算分"]

            if name not in names:
                # 排重
                names.append(name)
                fanPatternList.append(fan)

        ftlog.debug('MSiChuanOneResult.getFanPatternListByResults fanPatternList=', fanPatternList)
        return fanPatternList
    
    def getGangIdsFromScore(self, scores):
        winerIds = []
        for seatId in range(self.playerCount):
            if scores[seatId] < 0:
                winerIds.append(seatId)
        ftlog.debug('MSiChuanOneResult.getGangIdsFromScore winerIds:', winerIds)
        return winerIds

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
                
     
    # 获取花猪 looserId winnerId
    def getChaHuaZhuId(self):  
        looserId = []
        winnerId = []        
        for seatId in range(self.playerCount):
            # 玩家没有离开及认输
            if self.players[seatId].isIgnoreMessage():
                continue
            
            if self.players[seatId].isWon():
                winnerId.append(seatId)
                continue
            ftlog.debug('MSichuanOneResult.getChaHuaZhu allTiles:', self.playerAllTiles[seatId]
                                , 'absenceColor:', self.tableTileMgr.absenceColors
                                , 'seatId:', seatId)
            absenceTiles = MTile.filterTiles(self.playerAllTiles[seatId][MHand.TYPE_HAND], self.tableTileMgr.absenceColors[seatId])
            ftlog.debug('MSiChuanOneResult.getChaHuaZhu absenceTiles:', absenceTiles)
            if len(absenceTiles) > 0:
                looserId.append(seatId)
                continue
            winnerId.append(seatId)
        
        ftlog.debug('MSiChuanOneResult.getChaHuaZhu looserId:', looserId, 'winnerId:', winnerId)
        # 添加打印，确认花猪是否正确
        for _id in looserId:
            ftlog.debug('MSiChuanOneResult.getChaHuaZhu id:', _id \
                            , 'handTiles:', self.playerAllTiles[_id][MHand.TYPE_HAND] \
                            , 'absenceColor:', self.tableTileMgr.absenceColors[_id]) 
        return looserId, winnerId
    
    # 获取退税id
    def getTuiShuiId(self):
        # 未听牌的玩家退税
        loserId = []
        for seatId in range(self.playerCount):
            # 玩家没有离开
            if self.players[seatId].isObserver() \
                or self.players[seatId].isWon() \
                or len(self.players[seatId].winNodes) > 0:
                continue
            loserId.append(seatId)
        ftlog.debug('MSiChuanOneResult.getTuiShui id:', loserId)
        return loserId
    
    # 获取查大叫 
    def getChaDaJiaoId(self, loosHuaZhu):
        loosId = []
        winnerId = []
        for seatId in range(self.playerCount):
            ftlog.debug('MSiChuanOneResult.getChaDaJiaoId seatId:', seatId
                            , 'winNodes:', self.players[seatId].winNodes
                            , 'tiles:', self.players[seatId].copyTiles())
            # 查大叫 赢家为未胡牌且听牌的玩家
            if self.players[seatId].isWon():
                continue
            if self.players[seatId].isObserver():
                continue
            if len(self.players[seatId].winNodes) > 0:
                winnerId.append(seatId)
            elif seatId not in loosHuaZhu:
                loosId.append(seatId)
        ftlog.debug('MSiChuanOneResult.getChaDaJiao looserId:', loosId, 'winnerId:', winnerId)  
        return loosId, winnerId    

    def calcWin(self, winSeatIds):
        """
        血战麻将玩法 算分 点炮类型 + 和牌番型 + 根
        1) 流局：查花猪、查大叫、退税
        2) 赢局：查花猪 查大叫 退税
        3) 注意：玩家同时被查大叫 退税，则退税，不查大叫，查花猪了，则不查大叫了
        """
        # 在和牌时统计自摸，点炮，最大番数 初始化
        winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
        resultStat = [[] for _ in range(self.playerCount)]
        fanPattern = [[] for _ in range(self.playerCount)]
        loserFanPattern = [[] for _ in range(self.playerCount)]
        totalScores = [0 for _ in range(self.playerCount)]
        indexs = [0 for _ in range(self.playerCount)]
        dahuDetail = [{} for _ in range(self.playerCount)]
        totalDetailDesc = []
        winBase = self.tableConfig.get(MTDefine.WIN_BASE, 1)
        maxFan = self.tableConfig.get(MTDefine.MAX_FAN, 0) 
        ftlog.debug('MSiChuanOneResult latestGangSeatId:', self.latestGangSeatId
                        , 'winSeatids:', winSeatIds
                        , 'lastSeatId:', self.lastSeatId)
        # 前端需要详细的积分变化 胡牌 呼叫转移 花猪 大叫 退税
        detailChangeScore = [{self.CHANGE_SCORE_WIN:{}, self.CHANGE_SCORE_CALLTRAN:{}, self.CHANGE_SCORE_HUAZHU:{}, self.CHANGE_SCORE_DAJIAO:{}, self.CHANGE_SCORE_TUISHUI:{}} for _ in range(self.playerCount)]
        for winId in winSeatIds:
            scores = [0 for _ in range(self.playerCount)]
            winMode[winId] = MOneResult.WIN_MODE_PINGHU
            resultStat[winId].append({MOneResult.STAT_WIN:1})
            fanSymbolList = []
            winAllTiles = self.players[winId].copyTiles()
            # 是否自摸的标志
            isSelfFlag = False
            # 玩法选择 自摸加倍 自摸加底...
            playModeWanFaConfig = self.tableConfig.get(MTDefine.PLAYMODE_WANFA, MTDefine.WANFA_ZIMO_DEFAULT) 
            playModeWanFaDianGangConfig = self.tableConfig.get(MTDefine.PLAYMODE_WANFA_DIANGANGHUA, MTDefine.WANFA_ZIMO_DEFAULT)
            # 将胡的那张牌加入到手牌中
            winAllTiles[MHand.TYPE_HAND].append(winAllTiles[MHand.TYPE_HU][-1])
            ftlog.debug('MSiChuanOneResult.calcWin winAllTiles:', winAllTiles
                                , 'playModeWanFaConfig:', playModeWanFaConfig
                                , 'playModeWanFaDianGangConfig:', playModeWanFaDianGangConfig)
            '''
            和牌两种方式：自摸、点炮
            自摸有一下情况：自摸、海底捞月、天胡、地胡 杠开
            点炮有一下情况：点炮、抢杠胡、海底炮、杠上炮、一炮多响
            ''' 
            isZiMo = (self.lastSeatId == winId)
            if isZiMo:
                isSelfFlag = True
                resultStat[winId].append({MOneResult.STAT_ZIMO:1})
                # 天胡、地胡、海底捞、杠开都是自摸的一种
                if self.isTianHu(winAllTiles, winId, self.bankerSeatId):
                    fanSymbolList.append(self.TIANHU)
                    winMode[winId] = MOneResult.WIN_MODE_TIANHU
                    indexs[winId] += self.fanXing[self.TIANHU]['index'] 
                elif self.isDiHu(winAllTiles, winId, self.bankerSeatId):
                    fanSymbolList.append(self.DIHU)
                    winMode[winId] = MOneResult.WIN_MODE_DIHU
                    indexs[winId] += self.fanXing[self.DIHU]['index']
                elif self.isGangShangHua(winId) \
                    and playModeWanFaDianGangConfig == MTDefine.WANFA_DIANGANGHUA_ZIMO \
                    and self.isHaidilao(winId):
                    # 杠上花 海底捞 杠开当自摸
                    winMode[winId] = MOneResult.WIN_MODE_GANGKAI_HAIDI
                    fanSymbolList.append(self.GANGKAIHAIDI)
                    indexs[winId] += self.fanXing[self.GANGKAIHAIDI]['index']
                elif self.isGangShangHua(winId):
                    fanSymbolList.append(self.GANGKAI)   
                    indexs[winId] += self.fanXing[self.GANGKAI]['index'] 
                    winMode[winId] = MOneResult.WIN_MODE_GANGKAI
                    
                    if playModeWanFaDianGangConfig == MTDefine.WANFA_DIANGANGHUA_DIANPAO:
                        ftlog.debug('MSiChuanOneResult.calcWin latestOneResult lastSeatId:', self.latestOneResult.lastSeatId
                                        , 'key_type:', self.latestOneResult.results[self.KEY_NAME])
                        # 杠开 有杠上花 自摸 点炮选项
                        if self.latestOneResult  \
                                and self.latestOneResult.results[self.KEY_TYPE] == self.KEY_TYPE_NAME_GANG \
                                and self.latestOneResult.lastSeatId != winId:
                            self.setLooseSeats([self.latestOneResult.lastSeatId])
                            winMode[self.latestOneResult.lastSeatId] = MOneResult.WIN_MODE_DIANPAO
                elif self.isHaidilao(winId):
                    fanSymbolList.append(self.HAIDILAOYUE)
                    indexs[winId] += self.fanXing[self.HAIDILAOYUE]['index'] 
                    winMode[winId] = MOneResult.WIN_MODE_HAIDILAOYUE
                else: 
                    fanSymbolList.append(self.ZIMO)     
                    indexs[winId] += self.fanXing[self.ZIMO]['index']  
                    winMode[winId] = MOneResult.WIN_MODE_ZIMO 
            else:
                isSelfFlag = False
                resultStat[self.lastSeatId].append({MOneResult.STAT_DIANPAO: 1})
                winMode[winId] = MOneResult.WIN_MODE_PINGHU
                if self.qiangGang:
                    fanSymbolList.append(self.QIANGGANGHU)
                    winMode[winId] = MOneResult.WIN_MODE_QIANGGANGHU
                    if self.isYiPaoDuoXiang():
                        winMode[self.lastSeatId] = MOneResult.WIN_MODE_YIPAODUOXIANG
                    else:
                        winMode[self.lastSeatId] = MOneResult.WIN_MODE_DIANPAO
                    indexs[winId] += self.fanXing[self.QIANGGANGHU]['index']
                elif self.isHaiDiPao(winId):  
                    fanSymbolList.append(self.HAIDIPAO)                  
                    winMode[self.lastSeatId] = MOneResult.WIN_MODE_HAIDIPAO
                    indexs[winId] += self.fanXing[self.HAIDIPAO]['index']
                    if self.isGangShangPao(winId):
                        ftlog.debug('MSiChuanOneResult.calcWin GangShangPao and HaiDiPao')
                        indexs[winId] += self.fanXing[self.GANGSHANGPAO]['index']
                elif self.isGangShangPao(winId):
                    fanSymbolList.append(self.GANGSHANGPAO)
                    winMode[self.lastSeatId] = MOneResult.WIN_MODE_GANGSHANGPAO  
                    indexs[winId] += self.fanXing[self.GANGSHANGPAO]['index']
                    # 杠上炮 需要判断是否是呼叫转移 一炮多响没有呼叫转移
                    if self.tableConfig.get(MTDefine.CALL_TRANSFER, MTDefine.CALL_TRANSFER_NO)  \
                            and not self.isYiPaoDuoXiang():  
                        # 配置需要呼叫转移
                        self.setNeedCallTransfer()
                        ftlog.debug('MSiChuanOneResult.calcWin callTransfer True')
                        # 呼叫转移需要额外延时两秒
                        self.setDealyTime(4)
                        winMode[self.lastSeatId] = MOneResult.WIN_MODE_HUJIAOZHUANYI
                        detailChangeScore[self.lastSeatId][self.CHANGE_SCORE_CALLTRAN]['state'] = 0
                        detailChangeScore[winId][self.CHANGE_SCORE_CALLTRAN]['state'] = 1
                    
                    if self.isHaiDiPao(winId):  
                        # 海底炮 杠上炮 可以叠加 不显示番型
                        ftlog.debug('MSiChuanOneResult.calcWin GangShangPao and HaiDiPao')
                        indexs[winId] += self.fanXing[self.HAIDIPAO]['index']
                elif self.isYiPaoDuoXiang():
                    fanSymbolList.append(self.DIANPAO)
                    winMode[self.lastSeatId] = MOneResult.WIN_MODE_YIPAODUOXIANG
                    indexs[winId] += self.fanXing[self.YIPAODUOXIANG]['index']   
                else:
                    fanSymbolList.append(self.DIANPAO)
                    winMode[self.lastSeatId] = MOneResult.WIN_MODE_DIANPAO  
                    indexs[winId] += self.fanXing[self.DIANPAO]['index']
            # fanPattern[winId].append([self.fanXing[fanSymbolList[-1]]['name'], str(self.fanXing[fanSymbolList[-1]]['index']) + "倍"])   
            dahuDetail[winId][self.EXINFO_HU_ACTION] = self.fanXing[fanSymbolList[-1]]['name'] if fanSymbolList[-1] != self.DIANPAO else '胡'
            
            # 根据玩家手牌及ID来获取玩家应该胡的番型
            self.tilePatternChecker.initChecker(winAllTiles, self.tableTileMgr)
            fanSymbol = self.tilePatternChecker.getFanSymbolFromAllTiles()
            fanSymbolList.append(fanSymbol)
            fanPattern[winId].append([self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"])
            indexs[winId] += self.fanXing[fanSymbol]['index']
            
            # 计算根数，根据番型去掉不计根的番型    
            gengNum = self.getLongGenCount(winAllTiles)
            for patternName in fanSymbolList:
                if self.genXing.has_key(patternName):
                    gengNum -= self.genXing[patternName]
                
            # 番型+根
            indexs[winId] += gengNum
            
            # 获取番数对应的分值 底分 * 倍数 如果是自摸，判断加倍、加底
            calcBei = self.calcFanKmodel(indexs[winId], maxFan)
            ziMoFlag = False
            if isSelfFlag:
                if playModeWanFaConfig == MTDefine.WANFA_ZIMO_JIADI:
                    # 自摸加底
                    winBase += 1
                elif playModeWanFaConfig == MTDefine.WANFA_ZIMO_JIABEI:
                    # 自摸加倍
                    if calcBei < maxFan:
                        calcBei += 1
                    ziMoFlag = True
            
            baseScore = calcBei * winBase
            ftlog.debug('MSiChuanOneResult.calcWin fanIndex: ', indexs[winId], 'maxFan: ', maxFan, 'winBase: ', winBase)
            
            # 判断用户是否大胡 总倍数大于2倍
            if baseScore >= 4:
                dahuDetail[winId][self.EXINFO_BIGWIN] = self.fanXing[fanSymbol]['name']
                
            if self.playMode == MPlayMode.XUEZHANDAODI:
                if isSelfFlag and playModeWanFaConfig == MTDefine.WANFA_ZIMO_JIABEI:
                    dahuDetail[winId][self.EXINFO_WINTIMES] = pow(2, indexs[winId]) + 1
                else:
                    dahuDetail[winId][self.EXINFO_WINTIMES] = pow(2, indexs[winId])
            elif self.playMode == MPlayMode.XUELIUCHENGHE:
                dahuDetail[winId][self.EXINFO_WINTIMES] = len(self.players[winId].copyHuArray())
            dahuDetail[winId][self.EXINFO_WINTILE] = self.winTile
                
            # 计算番型的分数
            for looserId in self.looseSeats:
                scores[looserId] -= baseScore
                scores[winId] += baseScore
                detailChangeScore[looserId][self.CHANGE_SCORE_WIN]['state'] = 0
            detailChangeScore[winId][self.CHANGE_SCORE_WIN]['state'] = 1
            # 单局最佳 分数
            resultStat[winId].append({MOneResult.STAT_ZUIDAFAN: scores[winId]})
            dahuDetail[winId][self.EXINFO_WINFAN] = scores[winId]
            # 生成对局流水
            detailDesc = self.processDetailResult(fanSymbolList, scores, winId, self.looseSeats, gengNum, isSelfFlag, ziMoFlag) 
            ftlog.debug('MSiChuanOneResult.calcWin detailDesc: ', detailDesc)
            
            totalDetailDesc.append(detailDesc)
            for seatId in range(self.playerCount):
                totalScores[seatId] += scores[seatId]
                
        if self.isGameOver():
            if self.playMode == MPlayMode.XUEZHANDAODI:
                huaZhuLooserId, huaZhuWinnerId = [], []
                daJiaoLooserId, daJiaoWinnerId = [], []
            else:
                huaZhuLooserId, huaZhuWinnerId = self.getChaHuaZhuId()
                daJiaoLooserId, daJiaoWinnerId = self.getChaDaJiaoId(huaZhuLooserId)
            self.setHuaZhuLooseIds(huaZhuLooserId)
            self.setHuaZhuWinIds(huaZhuWinnerId)
            self.setDaJiaoLooseIds(daJiaoLooserId)
            self.setDaJiaoWinIds(daJiaoWinnerId)
            
            # 设置花猪状态
            for looseHuaZhu in huaZhuLooserId:
                detailChangeScore[looseHuaZhu][self.CHANGE_SCORE_HUAZHU]['state'] = 0
            for winHuaZhuin in huaZhuWinnerId:
                detailChangeScore[winHuaZhuin][self.CHANGE_SCORE_HUAZHU]['state'] = 1
                
            for looseDaJiao in daJiaoLooserId:
                detailChangeScore[looseDaJiao][self.CHANGE_SCORE_DAJIAO]['state'] = 0
            for winDaJiao in daJiaoWinnerId:
                detailChangeScore[winDaJiao][self.CHANGE_SCORE_DAJIAO]['state'] = 1
            
            # 设置花猪、大叫ID，轮庄使用
            self.setHuaZhuDaJiaoIdTotal(huaZhuLooserId, daJiaoLooserId)
            ftlog.debug('MSiChuanOneResult.calcWin huaZhu LooserId:', huaZhuLooserId
                                , 'winnerId:', huaZhuWinnerId
                                , 'dajiao LooserId:', daJiaoLooserId
                                , 'winnerId:', daJiaoWinnerId)
        
        self.results[self.KEY_NAME] = MOneResult.KEY_TYPE_NAME_HU       
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_HU
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_STAT] = resultStat
        self.results[self.KEY_DETAIL_DESC_LIST] = totalDetailDesc
        self.results[self.KEY_FAN_PATTERN] = fanPattern
        self.results[self.KEY_DAHU_DETAIL] = dahuDetail
        self.results[self.KEY_LOSER_FAN_PATTERN] = loserFanPattern
        self.results[self.KEY_DETAIL_CHANGE_SCORES] = detailChangeScore
        self.results[self.KEY_SCORE] = totalScores
        self.results[self.KEY_SCORE_TEMP] = totalScores
        ftlog.debug('MSiChuanOneResult.calcWin result winMode:', winMode
                   , ' fanPattern:', fanPattern
                   , ' dahuDetail:', dahuDetail
                   , ' detailDescList:', totalDetailDesc)
     
    def calcGang(self):
        """
        计算杠的输赢
        """
        resultStat = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_FAN_PATTERN] = [[] for _ in range(self.playerCount)]
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_GANG
        fanSymbol = ""
        # detailGang = {}
        # 前端需要详细的分数变化
        detailChangeScore = [{self.CHANGE_SCORE_GANG:{}} for _ in range(self.playerCount)]
        scores = [0 for _ in range(self.playerCount)]
        
        base = self.tableConfig.get(MTDefine.GANG_BASE, 1)
        ftlog.debug('MSiChuanOneResult.calcGang GANG_BASE:', base)
        
        if self.style == MPlayerTileGang.AN_GANG:
            fanSymbol = self.ANGANG 
        else:
            if self.lastSeatId != self.winSeatId:
                fanSymbol = self.MINGGANG
            else:
                fanSymbol = self.XUGANG
   
        base *= pow(2, self.fanXing[fanSymbol]['index'])
        for loose in self.looseSeats:
            scores[loose] = -base
            detailChangeScore[loose][self.CHANGE_SCORE_GANG]['state'] = 0
        detailChangeScore[self.winSeatId][self.CHANGE_SCORE_GANG]['state'] = 1
            
        scores[self.winSeatId] = len(self.looseSeats) * base
        # 蓄杠、暗杠都是三家扣分
        if fanSymbol == self.ANGANG or fanSymbol == self.XUGANG:
            self.results[self.KEY_NAME] = self.fanXing[fanSymbol]['name']
            self.results[self.KEY_FAN_PATTERN][self.winSeatId] = [[self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]
            for seatId in self.looseSeats:
                self.results[self.KEY_FAN_PATTERN][seatId] = [["被" + self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]
            
            if fanSymbol == self.ANGANG:   
                resultStat[self.winSeatId].append({MOneResult.STAT_ANGANG:1})
            else:
                resultStat[self.winSeatId].append({MOneResult.STAT_XUGAANG:1})
        else:
            # 明杠 只有放杠、明杠两家改分 刮风
            self.results[self.KEY_NAME] = self.fanXing[fanSymbol]['name'] 
            self.results[self.KEY_FAN_PATTERN][self.winSeatId] = [[self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]
            self.results[self.KEY_FAN_PATTERN][self.lastSeatId] = [["被" + self.fanXing[fanSymbol]['name'], str(self.fanXing[fanSymbol]['index']) + "倍"]]
            resultStat[self.winSeatId].append({MOneResult.STAT_MINGGANG:1})
            
        detailDesc = self.processDetailResult([fanSymbol], scores, self.winSeatId, self.looseSeats, 0, True)
        self.results[self.KEY_TYPE] = self.KEY_TYPE_NAME_GANG
        self.results[self.KEY_NAME] = self.KEY_TYPE_NAME_GANG
        self.results[self.KEY_SCORE] = scores
        self.results[self.KEY_SCORE_TEMP] = scores
        self.results[self.KEY_GANG_STYLE_SCORE] = base
        self.results[self.KEY_STAT] = resultStat
        self.results[self.KEY_DETAIL_DESC_LIST] = [detailDesc]
        self.results[self.KEY_DETAIL_CHANGE_SCORES] = detailChangeScore
        ftlog.debug('MSiChuanOneResult.calcGang results:', self.results)
    
    def calcFlow(self):
        """
        流局及牌局结束计算：
        退税 花猪 大叫
        """
        loserFanPattern = [[] for _ in range(self.playerCount)]
        scores = [0 for _ in range(self.playerCount)]
        totalDetailDesc = []
        detailChangeScore = [{self.CHANGE_SCORE_DAJIAO:{}, self.CHANGE_SCORE_HUAZHU:{}, self.CHANGE_SCORE_TUISHUI:{}} for _ in range(self.playerCount)]
        huaZhuLooserId, huaZhuWinnerId = self.getChaHuaZhuId()
        daJiaoLooserId, daJiaoWinnerId = self.getChaDaJiaoId(huaZhuLooserId)
        self.setHuaZhuLooseIds(huaZhuLooserId)
        self.setHuaZhuWinIds(huaZhuWinnerId)
        self.setDaJiaoLooseIds(daJiaoLooserId)
        self.setDaJiaoWinIds(daJiaoWinnerId)
        ftlog.debug('MSiChuanOneResult.calcFlow huaZhu LooserId:', huaZhuLooserId
                            , 'winnerId:', huaZhuWinnerId
                            , 'dajiao LooserId:', daJiaoLooserId
                            , 'winnerId:', daJiaoWinnerId)
        
        # 设置花猪、大叫ID，轮庄使用
        self.setHuaZhuDaJiaoIdTotal(huaZhuLooserId, daJiaoLooserId)
        
        # 设置花猪状态
        for looseHuaZhu in huaZhuLooserId:
            detailChangeScore[looseHuaZhu][self.CHANGE_SCORE_HUAZHU]['state'] = 0
        for winHuaZhuin in huaZhuWinnerId:
            detailChangeScore[winHuaZhuin][self.CHANGE_SCORE_HUAZHU]['state'] = 1
            
        for looseDaJiao in daJiaoLooserId:
            detailChangeScore[looseDaJiao][self.CHANGE_SCORE_DAJIAO]['state'] = 0
        for winDaJiao in daJiaoWinnerId:
            detailChangeScore[winDaJiao][self.CHANGE_SCORE_DAJIAO]['state'] = 1
               
        self.results[self.KEY_SCORE] = scores
        self.results[self.KEY_SCORE_TEMP] = scores
        self.results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_FLOW
        self.results[self.KEY_NAME] = MOneResult.KEY_TYPE_NAME_FLOW
        winMode = [MOneResult.WIN_MODE_LOSS for _ in range(self.playerCount)]
        self.results[self.KEY_WIN_MODE] = winMode
        self.results[self.KEY_LOSER_FAN_PATTERN] = loserFanPattern
        self.results[self.KEY_DETAIL_DESC_LIST] = totalDetailDesc
        self.results[self.KEY_DETAIL_CHANGE_SCORES] = detailChangeScore
  
    def calcDaJiao(self):
        '''
        大叫计算 
        赢家 输家id在OneResult计算出
        '''
        scoreList = [0 for _ in range(self.playerCount)]
        descInfo = [["", "", 0, ""] for _ in range(self.playerCount)]
        loserFanPattern = [[] for _ in range(self.playerCount)]
        ftlog.debug('MSiChuanOneResult.calcDaJiao winSeatId:', self.winSeats
                        , 'looseSeats:', self.looseSeats
                        , 'huaZhuLooserIds:', self.huaZhuLooseIds)
        for winId in self.winSeats:
            tingScore = self.getMaxFanByTing(winId)
            ftlog.debug('MSiChuanOneResult.calcDaJiao tingScore:', tingScore)
            scoreList[winId] += tingScore
            scoreList[self.looseSeats] -= tingScore
            # 赢家 对局流水
            descInfo[winId][self.INDEX_DESCPATTERN] = "查大叫"
            descInfo[winId][self.INDEX_FANPATTERN] = str(tingScore) + "倍"
            descInfo[winId][self.INDEX_SCORE] = tingScore
            descInfo[winId][self.INDEX_DESCID] = self.getLocationInfo(self.looseSeats, winId)
        # 输家对局流水
        descInfo[self.looseSeats][self.INDEX_DESCPATTERN] = '被查大叫'
        descInfo[self.looseSeats][self.INDEX_FANPATTERN] = str(tingScore) + '倍'
        descInfo[self.looseSeats][self.INDEX_SCORE] = scoreList[self.looseSeats]
        if len(self.winSeats) == 3:
            strDescId = '三家'
        elif len(self.winSeats) == 2:
            strDescId = '两家'
        else:
            strDescId = self.getLocationInfo(self.winSeats[0], self.looseSeats)
        descInfo[self.looseSeats][self.INDEX_DESCID] = strDescId
        
        loserFanPattern[self.looseSeats].append(['查大叫', str(scoreList[self.looseSeats]) + '倍'])
          
        ftlog.debug('MSiChuanOneResult.calcDaJiao descInfo:', descInfo, 'scoreList:', scoreList)
        self.results[self.KEY_SCORE] = scoreList
        self.results[self.KEY_SCORE_TEMP] = scoreList
        self.results[self.KEY_TYPE] = self.KEY_TYPE_NAME_DAJIAO
        self.results[self.KEY_NAME] = self.KEY_TYPE_NAME_DAJIAO
        self.results[self.KEY_DETAIL_DESC_LIST] = [descInfo]
        self.results[self.KEY_LOSER_FAN_PATTERN] = loserFanPattern
  
    def calcHuaZhu(self):
        '''
        花猪计算 每次只是计算一个输家 多个赢家
        需要传入winId looserId
        '''
        scoreList = [0 for _ in range(self.playerCount)]
        maxFan = self.tableConfig.get(MTDefine.MAX_FAN, 64)
        descInfo = [["", "", 0, ""] for _ in range(self.playerCount)]
        loserFanPattern = [[] for _ in range(self.playerCount)]
        
        ftlog.debug('MSiChuanOneResult.calcHuaZhu looserId:', self.looseSeats
                            , 'wins:', self.winSeats
                            , 'maxFan:', maxFan)
        maxFanScore = maxFan
        for seatId in self.winSeats:
            scoreList[seatId] += maxFanScore
            scoreList[self.looseSeats] -= maxFanScore
            descInfo[seatId][self.INDEX_DESCPATTERN] = '查花猪'
            descInfo[seatId][self.INDEX_FANPATTERN] = str(maxFanScore) + '倍'
            descInfo[seatId][self.INDEX_SCORE] = maxFanScore
            descInfo[seatId][self.INDEX_DESCID] = self.getLocationInfo(self.looseSeats, seatId)
        
        descInfo[self.looseSeats][self.INDEX_DESCPATTERN] = '被查花猪'
        descInfo[self.looseSeats][self.INDEX_FANPATTERN] = str(maxFanScore) + '倍'
        descInfo[self.looseSeats][self.INDEX_SCORE] = scoreList[self.looseSeats]
        if len(self.winSeats) == 3:
            strDescId = '三家'
        elif len(self.winSeats) == 2:
            strDescId = '两家'
        else:
            strDescId = self.getLocationInfo(self.winSeats[0], self.looseSeats)
        descInfo[self.looseSeats][self.INDEX_DESCID] = strDescId
        
        # 更新前端播放动画所需的数据
        loserFanPattern[self.looseSeats].append(["查花猪", str(maxFanScore) + '倍'])
        ftlog.debug('MSiChuanOneResult.calcHuaZhu descInfo:', descInfo, 'scoreList:', scoreList)
        self.results[self.KEY_SCORE] = scoreList
        self.results[self.KEY_SCORE_TEMP] = scoreList
        self.results[self.KEY_TYPE] = self.KEY_TYPE_NAME_HUAZHU
        self.results[self.KEY_NAME] = self.KEY_TYPE_NAME_HUAZHU
        self.results[self.KEY_DETAIL_DESC_LIST] = [descInfo]
        self.results[self.KEY_LOSER_FAN_PATTERN] = loserFanPattern
  
    def calcTuiShui(self):
        '''
        退税计算 需要传入winId looserId latestOneResult
        根据传入的OneResult来计算退税
        '''
        scoreList = [0 for _ in range(self.playerCount)]
        descInfo = [["", "", 0, ""] for _ in range(self.playerCount)]
        detailChangeScore = [{self.CHANGE_SCORE_TUISHUI:{}} for _ in range(self.playerCount)]
        loserFanPattern = [[] for _ in range(self.playerCount)]
        # 分数
        latestScores = self.latestOneResult.results[self.KEY_SCORE_TEMP]
        # 倍数
        baseGang = self.latestOneResult.results[self.KEY_GANG_STYLE_SCORE]
        # 杠WinID
        latestWinId = self.latestOneResult.winSeatId
        # 输家ID
        latestLooseIds = self.latestOneResult.looseSeats
        
        ftlog.debug('MSiChuanOneResult.calcTuiShui latestScores:', latestScores
                            , 'baseGang:', baseGang
                            , 'latestWinId:', latestWinId
                            , 'latestLooseIds:', latestLooseIds)
        
        for seatId in range(self.playerCount):
            scoreList[seatId] -= latestScores[seatId]
        
        # 退税赢家对局
        for seatId in latestLooseIds:
            descInfo[seatId][self.INDEX_DESCPATTERN] = '被退税'
            descInfo[seatId][self.INDEX_FANPATTERN] = str(baseGang) + '倍'
            descInfo[seatId][self.INDEX_SCORE] = scoreList[seatId]
            descInfo[seatId][self.INDEX_DESCID] = self.getLocationInfo(latestWinId, seatId)
            
            detailChangeScore[seatId][self.CHANGE_SCORE_TUISHUI]['state'] = 1
        # 退税输家对局
        descInfo[latestWinId][self.INDEX_DESCPATTERN] = '退税'
        descInfo[latestWinId][self.INDEX_FANPATTERN] = str(baseGang) + '倍'
        descInfo[latestWinId][self.INDEX_SCORE] = scoreList[latestWinId]
        detailChangeScore[latestWinId][self.CHANGE_SCORE_TUISHUI]['state'] = 0
        if len(latestLooseIds) == 3:
            strDescId = '三家'
        elif len(latestLooseIds) == 2:
            strDescId = '两家'
        else:
            strDescId = self.getLocationInfo(latestLooseIds[0], latestWinId)
        descInfo[latestWinId][self.INDEX_DESCID] = strDescId
        
        # 添加前端播放动画需要的数据
        loserFanPattern[latestWinId].append(['退税', str(baseGang) + "倍"])
            
        ftlog.debug('MSiChuanOneResult.calcTuishui descInfo:', descInfo, 'scoreList:', scoreList)
        self.results[self.KEY_SCORE] = scoreList
        self.results[self.KEY_SCORE_TEMP] = scoreList
        self.results[self.KEY_TYPE] = self.KEY_TYPE_NAME_TUISHUI
        self.results[self.KEY_NAME] = self.KEY_TYPE_NAME_TUISHUI
        self.results[self.KEY_DETAIL_DESC_LIST] = [descInfo]
        self.results[self.KEY_LOSER_FAN_PATTERN] = loserFanPattern
        self.results[self.KEY_DETAIL_CHANGE_SCORES] = detailChangeScore
        
  
    def calcCallTransfer(self):
        '''
        呼叫转移计算 需要传入winId looserId latestOneResult
        根据最近的OneResult来计算呼叫转移分数
        '''
        scoreList = [0 for _ in range(self.playerCount)]
        descInfo = [["", "", 0, ""] for _ in range(self.playerCount)]
        # 分数
        latestScores = self.latestOneResult.results[self.KEY_SCORE_TEMP]
        # 倍数
        baseGang = self.latestOneResult.results[self.KEY_GANG_STYLE_SCORE] if self.KEY_GANG_STYLE_SCORE in self.latestOneResult.results else 0
        winSeatId = self.winSeats[0]
        looseSeatId = self.looseSeats[0]
        ftlog.debug('MSiChuanOneResult.calcCallTransfer latestScores:', latestScores, 'baseGang:', baseGang)
        
        scoreList[winSeatId] = latestScores[looseSeatId]
        scoreList[looseSeatId] = -latestScores[looseSeatId]
        # 赢家对局
        descInfo[winSeatId][self.INDEX_DESCPATTERN] = '呼叫转移'
        descInfo[winSeatId][self.INDEX_FANPATTERN] = str(baseGang) + '倍'
        descInfo[winSeatId][self.INDEX_SCORE] = scoreList[winSeatId]
        descInfo[winSeatId][self.INDEX_DESCID] = self.getLocationInfo(looseSeatId, winSeatId)
        # 输家对局
        descInfo[looseSeatId][self.INDEX_DESCPATTERN] = '呼叫转移'
        descInfo[looseSeatId][self.INDEX_FANPATTERN] = str(baseGang) + '倍'
        descInfo[looseSeatId][self.INDEX_SCORE] = scoreList[looseSeatId]
        descInfo[looseSeatId][self.INDEX_DESCID] = self.getLocationInfo(winSeatId, looseSeatId)
        # 设置OneResult状态值，退税时，不退呼叫转移过的
        self.latestOneResult.setHasCallTransfer()
        # 整理返回值
        self.results[self.KEY_SCORE] = scoreList
        self.results[self.KEY_SCORE_TEMP] = scoreList
        self.results[self.KEY_TYPE] = self.KEY_TYPE_NAME_CALLTRAN
        self.results[self.KEY_NAME] = self.KEY_TYPE_NAME_CALLTRAN
        self.results[self.KEY_DETAIL_DESC_LIST] = [descInfo]

    def calcScore(self):
        """计算输赢数值"""
        # 序列化，以备后续的查找核实
        self.serialize()
        if self.resultType == self.RESULT_GANG:
            self.calcGang()
        elif self.resultType == self.RESULT_WIN:
            self.calcWin(self.winSeats)
        elif self.resultType == self.RESULT_FLOW:
            self.calcFlow()
        elif self.resultType == self.RESULT_CALLTRAN:
            self.calcCallTransfer()
        elif self.resultType == self.RESULT_TUISHUI:
            self.calcTuiShui()
        elif self.resultType == self.RESULT_HUAZHU:
            self.calcHuaZhu()
        elif self.resultType == self.RESULT_DAJIAO:
            self.calcDaJiao()
        else:
            ftlog.debug('MSiChuanOneResult calcScore ResultType not found...')
    
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
            ftlog.debug('MSiChuanOneResult setCoinScore before detailChangeScore:', self.results[self.KEY_DETAIL_CHANGE_SCORES])
        if self.results[self.KEY_TYPE] == self.KEY_TYPE_NAME_GANG:
            detailChangeScore = self.results[self.KEY_DETAIL_CHANGE_SCORES]
            self.updateDetailChangeScore(detailChangeScore, self.CHANGE_SCORE_GANG, scoreList)
        elif self.results[self.KEY_TYPE] == self.KEY_TYPE_NAME_HU:
            detailChangeScore = self.results[self.KEY_DETAIL_CHANGE_SCORES]
            self.updateDetailChangeScore(detailChangeScore, self.CHANGE_SCORE_WIN, scoreList)
        if self.KEY_DETAIL_CHANGE_SCORES in self.results:
            ftlog.debug('MSiChuanOneResult setCoinScore after detailChangeScore:', self.results[self.KEY_DETAIL_CHANGE_SCORES])
        # 金币桌更新一下信息
        if self.tableType != MTDefine.TABLE_TYPE_NORMAL:
            return 
        # 对局流水可能是多个 根据对局流水中的比例来获取金币值
        for descInfo in self.results[self.KEY_DETAIL_DESC_LIST]:
            for seatId in range(self.playerCount):
                if self.results[self.KEY_SCORE_TEMP][seatId] == 0:
                    continue
                score = descInfo[seatId][self.INDEX_SCORE]
                descInfo[seatId][self.INDEX_SCORE] = int(scoreList[seatId] * (float(score) / self.results[self.KEY_SCORE_TEMP][seatId]))
        ftlog.debug('MSiChuanOneResult after setCoinScore descInfo:', self.results[self.KEY_DETAIL_DESC_LIST])
    
       
    def updateInfo(self, oneResultList):
        '''
        将oneResultList中的数据合并到result中，
        1 积分 2 对局流水 3 loserFanPattern 4 详细的积分变化
        :param oneResultList: oneResult 需要合并列表
        '''
        for oneResult in oneResultList:
            # 积分更新
            for seatId in range(self.playerCount):
                self.results[MOneResult.KEY_SCORE][seatId] += oneResult.results[MOneResult.KEY_SCORE][seatId]
            # 对局流水汇总
            self.results[MOneResult.KEY_DETAIL_DESC_LIST].extend(oneResult.results[MOneResult.KEY_DETAIL_DESC_LIST])
            
            # 详细积分变化汇总 杠 胡 流 不用添加 只需要添加 呼叫  退税 花猪 大叫
            scoreList = oneResult.results[self.KEY_SCORE] 
            detailChangeScores = self.results[self.KEY_DETAIL_CHANGE_SCORES]
            resultType = oneResult.results[self.KEY_TYPE]
            if resultType == self.KEY_TYPE_NAME_CALLTRAN:
                self.updateDetailChangeScore(detailChangeScores, self.CHANGE_SCORE_CALLTRAN, scoreList)
            elif resultType == self.KEY_TYPE_NAME_TUISHUI:
                self.updateStateChangeScore(detailChangeScores, self.CHANGE_SCORE_TUISHUI, oneResult.results[self.KEY_DETAIL_CHANGE_SCORES])
                self.updateDetailChangeScore(detailChangeScores, self.CHANGE_SCORE_TUISHUI, scoreList)
            elif resultType == self.KEY_TYPE_NAME_HUAZHU:
                self.updateDetailChangeScore(detailChangeScores, self.CHANGE_SCORE_HUAZHU, scoreList)
            elif resultType == self.KEY_TYPE_NAME_DAJIAO:
                self.updateDetailChangeScore(detailChangeScores, self.CHANGE_SCORE_DAJIAO, scoreList)
            # loserFanPattern 汇总
            if self.KEY_LOSER_FAN_PATTERN in oneResult.results:
                loserFanPattern = oneResult.results[self.KEY_LOSER_FAN_PATTERN]
                for seatId in range(self.playerCount):
                    self.results[self.KEY_LOSER_FAN_PATTERN][seatId].extend(loserFanPattern[seatId])
                
        ftlog.debug('MSiChuanOneResult updateInfo score:', self.results[MOneResult.KEY_SCORE]
                        , 'descList:', self.results[MOneResult.KEY_DETAIL_DESC_LIST]
                        , 'detailChangeScore:', self.results[self.KEY_DETAIL_CHANGE_SCORES]
                        , 'loserFanPattern:', self.results[self.KEY_LOSER_FAN_PATTERN])
        
    def getExtendGameWinParams(self):
        '''
        获取结算延时的扩展参数
        '''
        return {'huaZhuDaJiaoId': self.huaZhuDaJiaoId}
     
if __name__ == "__main__":
    result = MSiChuanOneResult()
    result.setTableConfig({})
