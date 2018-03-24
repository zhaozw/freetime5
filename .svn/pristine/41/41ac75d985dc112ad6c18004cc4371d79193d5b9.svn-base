# -*- coding=utf-8
'''
Created on 2016年9月23日

本桌的输赢结果
1）陌生人桌，打完后直接散桌，有一个round_results
2）自建桌，SNG，打几把，有几个round_results
@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.win_loose_result.one_result import MOneResult

class MTableResultsStatGuangDong(object):
    
    def __init__(self):
        super(MTableResultsStatGuangDong, self).__init__()

    def getCreateExtendBudgets(self, tableResults, playerCount, playMode, score):
        '''
        自建桌大结算
        自摸 点炮 刮风 下雨 单场最佳
        '''
        ftlog.debug('MTableResultsStatGuangDong.getCreateExtendBudgets playMode:', playMode)
        createExtendBudgets = [{} for _ in range(playerCount)]
        allResults = []
        ftlog.debug('MTableResultsStatGuangDong.getCreateExtendBudgets roundResult count', len(tableResults))
        for roundResult in tableResults:
            for oneResult in roundResult.roundResults:
                allResults.append(oneResult)

        ziMoMaxValue = 0
        ziMoMaxSeatId = -1
        dianPaoMaxValue = 0
        dianPaoMaxSeatId = -1
        for seatId in range(playerCount):
            extendBudget = {}
            extendBudget["sid"] = seatId
            winValue = 0
            ziMoValue = 0
            dianPaoValue = 0
            danJuZuiJiaValue = 0
            mingValue = 0
            anValue = 0
            # statistics
            statisticInfo = []
            # one result
            for oneResult in allResults:
                ftlog.debug('MTableResultsStatGuangDong.getCreateExtendBudgets seatId:', seatId)
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

                    if MOneResult.STAT_DIANPAO in stat:
                        dianPaoValue += stat[MOneResult.STAT_DIANPAO]

                    if MOneResult.STAT_MINGGANG in stat:
                        mingValue += stat[MOneResult.STAT_MINGGANG]

                    if MOneResult.STAT_ANGANG in stat:
                        anValue += stat[MOneResult.STAT_ANGANG]

                    if MOneResult.STAT_GANG in stat:
                        mingValue += stat[MOneResult.STAT_XUGAANG]

            # 单局最佳表示每局的分数变化，应该从RoundResult中获取，先获取第一个值
            danJuZuiJiaValue = tableResults[-1].scoreChange[seatId] if tableResults else 0
            for roundResult in tableResults:
                if danJuZuiJiaValue < roundResult.scoreChange[seatId]:
                    danJuZuiJiaValue = roundResult.scoreChange[seatId]
            ftlog.debug('MTableResultsStatGuangDong.createExtendBudgets seatId:', seatId, 'danJuZuiJiaValue:',
                        danJuZuiJiaValue)

            statisticInfo.append({"desc": "自摸", "value": ziMoValue})
            statisticInfo.append({"desc": "点炮", "value": dianPaoValue})
            statisticInfo.append({"desc": "明杠", "value": mingValue})
            statisticInfo.append({"desc": "暗杠", "value": anValue})
            statisticInfo.append({"desc": "单局最佳", "value": danJuZuiJiaValue})
            ftlog.debug('MTableResultsStatGuangDong.createExtendBudgets seatId', seatId
                        , ' ziMoValue:', ziMoValue
                        , ' dianPaoValue:', dianPaoValue
                        , 'mingValue:', mingValue
                        , 'anValue:', anValue)

            # extendBudget["total_delta_score"] = totalDeltaScore
            if score and (len(score) > seatId):
                extendBudget["total_delta_score"] = score[seatId]
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
            ftlog.debug('MTableResultsStatGuangDong.createExtendBudgets zimo_most seat:', ziMoMaxSeatId)
        if dianPaoMaxSeatId >= 0:
            createExtendBudgets[dianPaoMaxSeatId]["head_mark"] = "dianpao_most"
            ftlog.debug('MTableResultsStatGuangDong.createExtendBudgets dianpao_most seat:', dianPaoMaxSeatId)

        return createExtendBudgets