# -*- coding=utf-8
'''
Created on 2016年9月23日

本桌的输赢结果
1）陌生人桌，打完后直接散桌，有一个round_results
2）自建桌，SNG，打几把，有几个round_results
@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.win_loose_result.table_results_stat_factory import MTableResultsStateFactory

class MTableResults(object):
    
    def __init__(self):
        super(MTableResults, self).__init__()
        self.__results = []
        self.__score = None
        self.__paoUid = -1
    
    def reset(self):
        self.__results = []
        self.__score = None
        self.__paoUid = -1
        
    @property
    def score(self):
        return self.__score
    
    @property
    def paoUid(self):
        return self.__paoUid
    
    def setPaoUid(self, paoUid):
        self.__paoUid = paoUid
    
    @property
    def results(self):
        return self.__results
    
    def addResult(self, result):
        self.__results.append(result)
        # 设置总积分
        if self.__score is None:
            lenCount = len(result.score)
            self.__score = [0 for _ in range(lenCount)]
            for index in range(lenCount):
                self.__score[index] = result.score[index]
        else:
            for index in range(len(self.__score)):
                self.__score[index] += result.score[index]
                
                
        ftlog.debug('MTableResults.addResult deltaScore:', result.score
            , ' totalScore:', self.__score)
        
    def createExtendBudgets(self, playerCount, playMode):
        '''
        获取自建桌大结算统计信息
        '''
        stater = MTableResultsStateFactory.getStat(playMode)
        return stater.getCreateExtendBudgets(self.results, playerCount, playMode, self.score)
