# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''

from freetime5.util import ftlog
from hall5.plugins.hallvip._private import _dao
from hall5.plugins.hallvip._private import _vip
from tuyoo5.core import tyconfig
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.core.tygame import ChargeNotifyEvent


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginVip(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginVip, self).__init__()
        self.vipSystem = _vip.TYVipSystem()
        self.userVipSystem = _vip.TYUserVipSystem(self.vipSystem, _dao.TYUserVipDao())

    @typlugin.markPluginEntry(confKeys=['game5:{}:vip:sc'.format(HALL_GAMEID)], srvType=[tyglobal.SRV_TYPE_HALL_UTIL])
    def onConfChanged(self, confKeys, changedKeys):
        datas = tyconfig.getGameData(confKeys[0], None, None, None)
        self.vipSystem.reloadConf(datas)

    @typlugin.markPluginEntry(event=ChargeNotifyEvent, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onCharge(self, event):
        diamonds = int(event.diamonds)
        if diamonds > 0:
            self.userVipSystem.addUserVipExp(event.gameId,
                                             event.userId,
                                             diamonds,
                                             'BUY_PRODUCT',
                                             tyconfig.productIdToNumber(event.productId))

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def getVipInfo(self, userId):
        """
        取得用户的VIP所有信息
        @param userId: 用户ID
        """
        return self.userVipSystem.getVipInfo(userId)
