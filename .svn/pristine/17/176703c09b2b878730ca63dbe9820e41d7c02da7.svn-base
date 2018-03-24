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
from majiang2.table_schedule.schedule_base import MTableScheduleBase
class MTableScheduleCircleCount(MTableScheduleBase):
    
    def __init__(self):
        super(MTableScheduleCircleCount, self).__init__()
        
    def setValue(self, cValue):
        self.setTotalQuan(cValue)
        self.setCurQuan(0)
        
    def udpateQuan(self, oldBanker, newBanker):
        if (newBanker != oldBanker) and (newBanker == 0):
            self.changeCurQuan(1)
        
    def isOver(self):
        return (self.curQuan == self.totalQuan)
    
            
    def getBankerString(self):
        banker = self.banker
        switcher = {
        0: "东",
        1: "南",
        2: "西",
        3: "北" }
        
        return switcher.get(banker, "庄")
    
    def getCurrentProgress(self, isReconnect):
        if isReconnect:
            return ('%s/%s圈-%s 第%s局' % (self.curQuan + 1, self.totalQuan, self.getBankerString(), self.curCount))
        else:
            return ('%s/%s圈-%s 第%s局' % (self.curQuan + 1, self.totalQuan, self.getBankerString(), self.curCount + 1))
     
    def sendScheduleTips(self, uids, gameId):
        pass       