# -*- coding=utf-8
'''
Created on 2015年7月1日

@author: zhaojiangang
基于：newsvn/hall37-py/tags/tygame-hall5-release-20160913 进行移植

'''
from freetime5.util import ftlog
from hall5.plugins.hallvip._private import _entity
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import HallKeys


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class TYUserVipDao(object):

    def loadVipExp(self, userId):
        '''
        加载用户的VIP经验值
        @param userId: 哪个用户
        @return: VIP经验值
        '''
        return pluginCross.halldata.getHallDataList(userId, HallKeys.ATT_VIP_EXP)

    def incrVipExp(self, userId, count):
        '''
        给用户增加count个经验值，count可以为负数
        @param userId: 哪个用户
        @param count: 数量
        @return: 变化后的值
        '''
        return pluginCross.halldata.incrVipExp(userId, count)

    def loadVipGiftStatus(self, userId):
        '''
        加载用户VIP礼包状态
        @param userId: 哪个用户
        @return: TYUserVipGiftStatusData
        '''
        status = _entity.TYUserVipGiftStatusData()
        d = pluginCross.halldata.getHallDataList(userId, HallKeys.ATT_VIP_GIFT_STATES)
        if d:
            for level, state in d.iteritems():
                status.giftStateMap[int(level)] = state
        return status

    def saveVipGiftStatus(self, userId, vipGiftStatus):
        '''
        保存用户VIP礼包状态
        @param userId: 哪个用户
        @param vipGiftStatus: 用户VIP礼包状态
        '''
        pluginCross.halldata.saveVipGiftStatus(userId, vipGiftStatus.giftStateMap)
