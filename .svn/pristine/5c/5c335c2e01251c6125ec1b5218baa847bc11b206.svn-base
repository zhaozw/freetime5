# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol

说明：
牌局过程控制
1.1 退出需解散/好友桌
1）按局
2）按圈
3）按积分
1.2 可随时退出/金币卓
4）默认实现
'''
from freetime5.util import ftlog

class MTableScheduleBase(object):
    def __init__(self):
        super(MTableScheduleBase, self).__init__()
        self.__total_count = 0
        self.__cur_count = 0
        
        self.__total_quan = 0
        self.__cur_quan = 0
        
        self.__players = None
        self.__type = ''
        
        self.__fangka_count = 0
        self.__banker = 0
        
    def reset(self):
        self.__total_count = 0
        self.__cur_count = 0
        self.__total_quan = 0
        self.__cur_quan = 0
        self.__players = None
        self.__type = ''
        self.__fangka_count = 0
        self.__banker = 0
        
    @property
    def banker(self):
        return self.__banker
    
    def setBanker(self, banker):
        self.__banker = banker
        
    @property
    def fangkaCount(self):
        return self.__fangka_count
    
    def setFangkaCount(self, count):
        self.__fangka_count = count
        
    def changeFangkaCount(self, delta):
        self.setFangkaCount(self.fangkaCount + delta)
        if self.fangkaCount <= 0:
            self.setFangkaCount(0)
        
    @property
    def type(self):
        return self.__type
    
    def setType(self, _type):
        self.__type = _type
        
    @property
    def totalCount(self):
        return self.__total_count
    
    def setTotalCount(self, count):
        self.__total_count = count
        
    @property
    def curCount(self):
        return self.__cur_count
    
    def setCurCount(self, count):
        self.__cur_count = count
        
    def changeCurCount(self, delta):
        ftlog.debug('MSchedule curCount:', self.curCount, 'delta:', delta)
        self.setCurCount(self.curCount + delta)
        if (self.curCount % 2 == 0) and (self.fangkaCount > 0):
            self.setFangkaCount(self.fangkaCount - 1)
        
    @property
    def totalQuan(self):
        return self.__total_quan
    
    def setTotalQuan(self, quan):
        self.__total_quan = quan
        
    @property
    def curQuan(self):
        return self.__cur_quan
    
    def setCurQuan(self, quan):
        self.__cur_quan = quan
        
    def changeCurQuan(self, delta):
        self.setCurQuan(self.curQuan + delta)
        
    @property
    def players(self):
        return self.__players
    
    def setPlayers(self, players):
        self.__players = players
        
    def setValue(self, cValue):
        pass
    
    def udpateQuan(self, oldBanker, newBanker):
        pass
        
    def isOver(self):
        return False
    
    def getCurrentProgress(self, isReconnect):
        return ''

    def sendScheduleTips(self, uids, gameId):
        pass