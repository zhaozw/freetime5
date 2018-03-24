# -*- coding=utf-8
'''
Created on 2016年9月23日

本桌的输赢结果
1）陌生人桌，打完后直接散桌，有一个round_results
2）自建桌，SNG，打几把，有几个round_results
@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.play_mode import MPlayMode
from majiang2.table.friend_table_define import MFTDefine
from majiang2.win_loose_result.one_result import MOneResult


class MTableResultsStat(object):
    
    def __init__(self):
        super(MTableResultsStat, self).__init__()

    def getCreateExtendBudgets(self, tableResults, playerCount, playMode, score):
        '''
        自建桌大结算
        '''
        createExtendBudgets = [{} for _ in range(playerCount)]
        # roundResult 列表
        ftlog.debug('MajiangTableLogic.getCreateExtendBudgets roundResult count', len(tableResults))
        allResults = []
        for roundResult in tableResults:
            ftlog.debug('MajiangTableLogic.getCreateExtendBudgets roundResult ...')
            for oneResult in roundResult.roundResults:
                allResults.append(oneResult)
                ftlog.debug('MajiangTableLogic.getCreateExtendBudgets oneResult ...')

        ziMoMaxValue = 0
        ziMoMaxSeatId = -1
        dianPaoMaxValue = 0
        dianPaoMaxSeatId = -1
        for seatId in range(playerCount):
            extendBudget = {}
            extendBudget["sid"] = seatId
            winValue = 0
            ziMoValue = 0
            moBaoValue = 0
            dianPaoValue = 0
            gangValue = 0
            mingGangValue = 0
            anGangValue = 0
            danJuZuiJiaValue = 0
            bankerValue = 0
            jiaopaiValue = 0
            moziValue = 0  # 摸子分
            pingnaValue = 0  # 平拿分
            qingnaValue = 0  # 清拿分
            guaFengValue = 0  # 刮风分
            xiaYuValue = 0  # 下雨分s
            # statistics
            statisticInfo = []
            # 晃晃喜相逢的次数
            xiXiangFengValue = 0
            # one result
            for oneResult in allResults:
                ftlog.debug('MajiangTableLogic.getCreateExtendBudgets seatId:', seatId)
                # statScore = oneResult.results[MOneResult.KEY_SCORE]
                # totalDeltaScore += statScore[seatId]
                stats = [[] for _ in range(playerCount)]
                playerStats = []
                if MOneResult.KEY_STAT in oneResult.results:
                    stats = oneResult.results[MOneResult.KEY_STAT]
                    playerStats = stats[seatId]
                for stat in playerStats:
                    if MOneResult.STAT_WIN in stat:
                        winValue += stat[MOneResult.STAT_WIN]

                    if MOneResult.STAT_ZIMO in stat:
                        ziMoValue += stat[MOneResult.STAT_ZIMO]

                    if MOneResult.STAT_MOBAO in stat:
                        moBaoValue += stat[MOneResult.STAT_MOBAO]

                    if MOneResult.STAT_DIANPAO in stat:
                        dianPaoValue += stat[MOneResult.STAT_DIANPAO]

                    if playMode == MPlayMode.HAERBIN \
                        or playMode == MPlayMode.JIXI \
                        or playMode == MPlayMode.MUDANJIANG \
                        or playMode == MPlayMode.DANDONG \
                        or playMode == MPlayMode.BAICHENG \
                        or playMode == MPlayMode.PANJIN :
                        if MOneResult.STAT_MINGGANG in stat:
                            mingGangValue += stat[MOneResult.STAT_MINGGANG]

                        if MOneResult.STAT_ANGANG in stat:
                            anGangValue += stat[MOneResult.STAT_ANGANG]

                        if MOneResult.STAT_GANG in stat:
                            gangValue += stat[MOneResult.STAT_GANG]

                    if MOneResult.STAT_BANKER in stat:
                        bankerValue += stat[MOneResult.STAT_BANKER]

                    if MOneResult.STAT_JIAOPAI in stat:
                        jiaopaiValue += stat[MOneResult.STAT_JIAOPAI]

                    if MOneResult.STAT_PINGNA in stat:
                        pingnaValue += stat[MOneResult.STAT_PINGNA]

                    if MOneResult.STAT_QINGNA in stat:
                        qingnaValue += stat[MOneResult.STAT_QINGNA]

                    if MOneResult.STAT_MOZI in stat:
                        moziValue += stat[MOneResult.STAT_MOZI]

                    if "xiXiangFeng" in stat:
                        xiXiangFengValue += stat["xiXiangFeng"]

                    # 血流/血战麻将 大结算 统计刮风下雨
                    if playMode == MPlayMode.XUEZHANDAODI \
                        or playMode == MPlayMode.XUELIUCHENGHE:
                        if MOneResult.STAT_MINGGANG in stat:
                            guaFengValue += stat[MOneResult.STAT_MINGGANG]

                        if MOneResult.STAT_ANGANG in stat:
                            xiaYuValue += stat[MOneResult.STAT_ANGANG]

                        if MOneResult.STAT_GANG in stat:
                            xiaYuValue += stat[MOneResult.STAT_XUGAANG]

            # 单局最佳表示每局的分数变化，应该从RoundResult中获取，先获取第一个值
            danJuZuiJiaValue = tableResults[-1].scoreChange[seatId] if tableResults else 0
            for roundResult in tableResults:
                if danJuZuiJiaValue < roundResult.scoreChange[seatId]:
                    danJuZuiJiaValue = roundResult.scoreChange[seatId]
            ftlog.debug('MTableLogic.createExtendBudgets seatId:', seatId, 'danJuZuiJiaValue:', danJuZuiJiaValue)

            oneResultForName = MOneResult(self.tilePatternChecker, self.playerCount)
            if playMode == MPlayMode.HAERBIN or playMode == MPlayMode.JIXI or playMode == MPlayMode.MUDANJIANG \
                or playMode == MPlayMode.BAICHENG or playMode == MPlayMode.PANJIN or playMode == MPlayMode.DANDONG:
                statisticInfo.append({"desc":oneResultForName.statType[MOneResult.STAT_WIN]["name"], "value":winValue})
                ftlog.debug('MTableLogic.createExtendBudgets seatId', seatId, ' winValue:', winValue)
                statisticInfo.append({"desc":oneResultForName.statType[MOneResult.STAT_MOBAO]["name"], "value":moBaoValue})
                ftlog.debug('MTableLogic.createExtendBudgets seatId', seatId, ' moBaoValue:', moBaoValue)

            statisticInfo.append({"desc":oneResultForName.statType[MOneResult.STAT_ZIMO]["name"], "value":ziMoValue})
            ftlog.debug('MTableLogic.createExtendBudgets seatId', seatId, ' ziMoValue:', ziMoValue)

            # 哈尔滨统计明杠暗杠
            if playMode == MPlayMode.HAERBIN or playMode == MPlayMode.JIXI or playMode == MPlayMode.MUDANJIANG \
                or playMode == MPlayMode.BAICHENG or playMode == MPlayMode.PANJIN or playMode == MPlayMode.DANDONG:
                statisticInfo.append({"desc":oneResultForName.statType[MOneResult.STAT_GANG]["name"], "value":gangValue})
                ftlog.debug('MTableLogic.createExtendBudgets seatId', seatId, ' gangValue:', gangValue)

            statisticInfo.append({"desc":oneResultForName.statType[MOneResult.STAT_DIANPAO]["name"], "value":dianPaoValue})
            ftlog.debug('MTableLogic.createExtendBudgets seatId', seatId, ' dianPaoValue:', dianPaoValue)

            if playMode == MPlayMode.HUAINING:
                statisticInfo = [
                    {"desc": "胡牌次数", "value": winValue},
                    {"desc": "自摸次数", "value": ziMoValue},
                    {"desc": "点炮次数", "value": dianPaoValue}]

            # 血流麻将统计刮风下雨 及明杠 蓄杠 暗杠
            if playMode == MPlayMode.XUEZHANDAODI \
                    or playMode == MPlayMode.XUELIUCHENGHE:
                statisticInfo.append({"desc": "刮风", "value": guaFengValue})
                statisticInfo.append({"desc": "下雨", "value": xiaYuValue})
                ftlog.debug('MTableLogic.createExtendBudgets seatId', seatId
                                , ' guaFengValue:', guaFengValue
                                , 'xiaYuValue: ', xiaYuValue)

            statisticInfo.append({"desc":"单局最佳", "value":danJuZuiJiaValue})
            # extendBudget["total_delta_score"] = totalDeltaScore
            if self.tableResult.score and (len(self.tableResult.score) > seatId):
                extendBudget["total_delta_score"] = self.tableResult.score[seatId]
            else:
                extendBudget["total_delta_score"] = 0
            extendBudget["statistics"] = statisticInfo
            # dianpao_most zimo_most
            extendBudget["head_mark"] = ""

            createExtendBudgets[seatId] = extendBudget
            if ziMoValue > ziMoMaxValue:
                ziMoMaxValue = ziMoValue
                ziMoMaxSeatId = seatId
            if dianPaoValue > dianPaoMaxValue:
                dianPaoMaxValue = dianPaoValue
                dianPaoMaxSeatId = seatId

        if ziMoMaxSeatId >= 0:
            createExtendBudgets[ziMoMaxSeatId]["head_mark"] = "zimo_most"
            ftlog.debug('MTableLogic.createExtendBudgets zimo_most seat:', ziMoMaxSeatId)
        if dianPaoMaxSeatId >= 0:
            createExtendBudgets[dianPaoMaxSeatId]["head_mark"] = "dianpao_most"
            ftlog.debug('MTableLogic.createExtendBudgets dianpao_most seat:', dianPaoMaxSeatId)

        # 返回玩家每局的分数 (江西，安徽麻将需求）
        if self.tableConfig.get(MFTDefine.BUDGET_INCLUDE_ROUND_SCORE, 0):
            roundNum = len(tableResults)
            for seatId in xrange(self.playerCount):
                createExtendBudgets[seatId]['delta_scores'] = [0] * roundNum
                for i, roundResult in enumerate(tableResults):
                    createExtendBudgets[seatId]['delta_scores'][i] = roundResult.score[seatId]
        return createExtendBudgets