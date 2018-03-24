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
from majiang2.table_schedule.schedule_round_count import MTableScheduleRoundCount
from majiang2.table_schedule.schedule_circle_count import MTableScheduleCircleCount
from majiang2.table_schedule.schedule_score import MTableScheduleScore
from majiang2.table_schedule.schedule_random import MTableScheduleRandom
from majiang2.table.friend_table_define import MFTDefine

class MTableScheduleFactory(object):
    
    def __init__(self):
        super(MTableScheduleFactory, self).__init__()
        
    @classmethod
    def getTableSchedule(cls, _type):
        if _type == MFTDefine.CARD_COUNT_ROUND:
            return MTableScheduleRoundCount()
        elif _type == MFTDefine.CARD_COUNT_CIRCLE:
            return MTableScheduleCircleCount()
        elif _type == MFTDefine.CARD_COUNT_BASE:
            return MTableScheduleScore()
        
        return MTableScheduleRandom()