# -*- coding=utf-8
'''
Created on 2016年9月23日

本副牌局的和牌结果，可能有多个
1）普通麻将一个结果
2）血战到底N-1个结果，N为牌桌人数
3）血流成河有多个结果，直到本局牌全部发完
@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.play_mode import MPlayMode
from majiang2.table.table_config_define import MTDefine
from majiang2.win_loose_result.one_result import MOneResult


class MRoundResults(object):
    
    def __init__(self):
        super(MRoundResults, self).__init__()
        self.__round_index = 0
        self.__round_results = []
        self.__fan_patterns = []
        self.__score = None
        self.__delta = None
        self.__horseScore = None
        self.__playMode = ''
        self.__playCount = 0
        # 添加积分变化的字段
        self.__score_change = []  
        
    @property
    def playerCount(self):
        return self.__playCount
    
    def setPlayerCount(self, playCount):
        self.__playCount = playCount
    
    @property
    def playMode(self):
        return self.__playMode
    
    def setPlayMode(self, playMode):
        self.__playMode = playMode
        
    @property
    def delta(self):
        return self.__delta

    @property
    def horseScore(self):
        if not self.__horseScore:
            return [0 for _ in range(self.playerCount)]
        else:
            return self.__horseScore
    
    @property
    def scoreChange(self):
        return self.__score_change
     
    @property
    def score(self):
        return self.__score

    @property
    def fanPatterns(self):
        return self.__fan_patterns

    @property
    def roundIndex(self):
        return self.__round_index
    
    def setRoundIndex(self, index):
        self.__round_index = index
        
    @property
    def roundResults(self):
        return self.__round_results
    
    # 获取积分变化总数
    def getChangeScore(self, result):
        scores = result[MOneResult.KEY_SCORE]
        if not self.scoreChange:
            self.__score_change = scores[:]
        else:
            for index in range(len(scores)):
                self.scoreChange[index] += scores[index]
        ftlog.debug('MRoundResults.getChangeScores scoreChange: ', self.scoreChange)
        
    def getDaHuResult(self, playerCount):
        '''
        要获取最佳的胡牌信息，根据番数来判断是否为最佳
        '''
        daHuDetail = [{} for _ in range(playerCount)]
        for ri in range(0, len(self.roundResults)):
            if MOneResult.KEY_DAHU_DETAIL in self.roundResults[ri].results:
                ftlog.debug('MRoundResults.getDaHuResult index:', ri, 'results:', self.roundResults[ri].results)  
                dahuResult = self.roundResults[ri].results[MOneResult.KEY_DAHU_DETAIL]
                for index in range(playerCount):
                    if self.playMode == MPlayMode.XUEZHANDAODI or self.playMode == MPlayMode.XUELIUCHENGHE:
                        if dahuResult[index].get(MOneResult.EXINFO_WINFAN, 0) < daHuDetail[index].get(MOneResult.EXINFO_WINFAN, 0):
                            pass
                        else:
                            daHuDetail[index] = dahuResult[index]
                    else:
                        daHuDetail[index] = dahuResult[index]
                    
        return daHuDetail

    def getTotalFanSummary(self):
        '''

        for ri in range(0, len(self.roundResults)):
            if MOneResult.KEY_DETAIL_DESC_LIST in self.roundResults[ri].results:
                detailResult = self.roundResults[ri].results[MOneResult.KEY_DETAIL_DESC_LIST]
                for detail in detailResult:
                    for index in range(self.playerCount):
                        if detail[index] != ['', '', '', '']:
                            ftlog.debug('[index]: ', index, 'detail[index]:', detail[index])
                            totalBei[index] += int(abs(detail[index][2]) / winbase / basechip)
        ftlog.debug('totalBei: ', totalBei)
        '''

        totalBei = [0 for _ in range(self.playerCount)]
        for result in self.roundResults:
            scoreTemp = result.results.get(MOneResult.KEY_SCORE_TEMP, [0 for _ in range(result.playerCount)])
            for index in range(len(scoreTemp)):
                totalBei[index] += scoreTemp[index]
        return totalBei

    def getRoundGenzhuangResult(self):
        score = [0 for _ in range(self.playerCount)]
        for result in self.roundResults:
            if result.resultType == MOneResult.RESULT_GENZHUANG:
                deltaScore = result.results.get(MOneResult.KEY_SCORE, [0 for _ in range(result.playerCount)])
                for index in range(len(score)):
                    score[index] += deltaScore[index]
        return score

    def getRoundGangResult(self):
        score = [0 for _ in range(self.playerCount)]
        for result in self.roundResults:
            if result.resultType == MOneResult.RESULT_GANG:
                deltaScore = result.results.get(MOneResult.KEY_SCORE, [0 for _ in range(result.playerCount)])
                for index in range(len(score)):
                    score[index] += deltaScore[index]
        return score

    def getRoundWinResult(self):
        score = [0 for _ in range(self.playerCount)]
        for result in self.roundResults:
            if result.resultType == MOneResult.RESULT_WIN:
                deltaScore = result.results.get(MOneResult.KEY_SCORE, [0 for _ in range(result.playerCount)])
                for index in range(len(score)):
                    score[index] += deltaScore[index]
        return score

    def addRoundResult(self, result):
        """添加轮次结果"""
        ftlog.debug('MRoundResults.addRoundResult : ', result.results
                , ' now roundIndex:', self.__round_index
                )
        
        if not result.isResultOK():
            return
        
        self.__round_results.append(result)
        self.__delta = result.results.get(MOneResult.KEY_SCORE, [0 for _ in range(result.playerCount)])[:]
        if result.results.has_key(MOneResult.KEY_FAN_PATTERN):
            if self.__fan_patterns == []:
                # 根据返回值的玩家人数，初始化
                self.__fan_patterns = [[] for _ in range(len(result.results[MOneResult.KEY_FAN_PATTERN]))]
            for index in range(len(result.results[MOneResult.KEY_FAN_PATTERN])):
                self.__fan_patterns[index].extend(result.results[MOneResult.KEY_FAN_PATTERN][index])
        if not self.__score:
            self.__score = self.__delta
        else:
            for index in range(len(self.__delta)):
                self.__score[index] += self.__delta[index]
                
        ftlog.debug('MRoundResults.addRoundResult type:', result.results[MOneResult.KEY_TYPE]
            , ' name:', result.results[MOneResult.KEY_NAME]
            , ' totalScore:', self.__score
            , ' deltaScore:', self.__delta
            , ' fanPatterns:', self.__fan_patterns
            )
    
    def getMergeFanPatternList(self):
        
        patternCount = 0
        eachPattern = []
        patternValue = []
        for index in range(len(self.__fan_patterns)):
            fanPatternList = []
            for fan_index in range(len(self.__fan_patterns[index])):
                eachPattern = self.__fan_patterns[index][fan_index]
                patternCount = self.__fan_patterns[index].count(eachPattern)
                if patternCount > 1:
                    patternValue = eachPattern[0] + str(patternCount)
                else:
                    patternValue = eachPattern[0]
                patternValue = [patternValue]
                    
                if patternValue not in fanPatternList:
                    fanPatternList.append(patternValue)
            self.__fan_patterns[index] = fanPatternList
        return self.__fan_patterns;

    def isYingOrShu(self, score):
        if score >= 0:
            return 1
        else:
            return 0
