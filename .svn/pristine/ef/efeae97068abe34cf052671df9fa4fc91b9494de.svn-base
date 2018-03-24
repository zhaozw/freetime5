# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh
'''
from freetime5.util import ftlog
from hall5.entity.hallevent import HallUserEventLogin
from hall5.plugins.hallday1st._private import hall5_login_reward
from tuyoo5.core import typlugin, tyglobal
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.plugins.weakdata.weakdata import TyPluginWeakData


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginDay1st(TyPluginWeakData):

    def __init__(self):
        super(HallPluginDay1st, self).__init__()
        self.configLoginreward = TyCachedConfig('loginreward', tyglobal.gameId())

    def destoryPlugin(self):
        super(HallPluginDay1st, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL,
                                                tyglobal.SRV_TYPE_HALL_SINGLETON])
    def initPluginBefore(self):
        super(HallPluginDay1st, self).initPluginBefore()

    @typlugin.markPluginEntry(event=HallUserEventLogin, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onHallUserEventLogin(self, event):
        if event.isDayfirst:
            # 检测发送登录奖励
            hall5_login_reward.sendLoginReward(self, event.userId, tyglobal.gameId(), event.intClientId)

    @typlugin.markPluginEntry(export=1)
    def getHappyBagFlg(self, userId):
        datas = self.getDay1stDatas(userId)
        return datas.get('happybag', 0)

    @typlugin.markPluginEntry(export=1)
    def setHappyBagFlg(self, userId):
        return self.updateDay1stDatas(userId, 'happybag', 1)
