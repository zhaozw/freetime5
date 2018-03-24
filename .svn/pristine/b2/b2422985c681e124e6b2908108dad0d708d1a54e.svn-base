# -*- coding: utf-8 -*-
'''
Created on 2016年8月1日

@author: zqh
'''
from freetime5.util import ftlog
from hall5.entity import hallchecker
from hall5.plugins.hallui._private import _hallui
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginUi(typlugin.TYPlugin):

    @typlugin.markPluginEntry(cmd='hall_ui5', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doHallUi(self, msg):
        mi = hallchecker.CHECK_BASE.check(msg)
        if _DEBUG:
            debug('doHallUi IN->', mi)
        if not mi.error:
            return _hallui.sendHallUiGameList(mi.userId, mi.clientId, mi.apiVersion)
        if _DEBUG:
            debug('doHallUi OUT')
        return 1

    @typlugin.markPluginEntry(export=1)
    def sendHallUiGameList(self, userId, intClientId, apiVersion):
        return _hallui.sendHallUiGameList(userId, intClientId, apiVersion)
