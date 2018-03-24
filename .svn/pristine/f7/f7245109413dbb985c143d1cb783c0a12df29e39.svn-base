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
from majiang2.entity import util

class MTableScheduleRoundCount(MTableScheduleBase):
    
    def __init__(self):
        super(MTableScheduleRoundCount, self).__init__()
        
    def setValue(self, cValue):
        self.setTotalCount(cValue)
        self.setCurCount(0)
        
    def isOver(self):
        return self.curCount == self.totalCount
    
    def getCurrentProgress(self, isReconnect):
        # 在所有玩家准备完以后，还会再发一遍，此处可以不用＋1
        return ('%s/%s局' % (self.curCount, self.totalCount))
    
        if isReconnect or (self.curCount+1 >= self.totalCount):
            return ('%s/%s局' % (self.curCount, self.totalCount))
        else:
            return ('%s/%s局' % (self.curCount + 1, self.totalCount))

    def sendScheduleTips(self, uids, gameId):
        if self.isOver():
            for uid in uids:
                util.sendPopTipMsg(uid, '本局结束后，将进行结算并解散房间')