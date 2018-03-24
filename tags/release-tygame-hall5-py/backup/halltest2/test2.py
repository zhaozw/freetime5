# -*- coding=utf-8 -*-
"""
@file  : test
@date  : 2016-11-10
@author: GongXiaobo
"""

from freetime5.util import ftlog
from tuyoo5.core import tygame
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.plugins.globalevent.globalevent import TyPluginGlobalEvent


class HallPluginTest2(TyPluginGlobalEvent):

    def __init__(self):
        super(HallPluginTest2, self).__init__()

    @typlugin.markPluginEntry(initBeforeConfig=['*'])
    def initPluginBefore(self):
        self.initPub()
        self.initSub()

    @typlugin.markPluginEntry(event=tygame.GlobalChargeEvent, srvType=tyglobal.SRV_TYPE_HALL_HTTP)
    def onGlobalChargeEvent1(self, event):
        ftlog.info('event1->', event, event._encodeToJsonDict())

    @typlugin.markPluginEntry(event=tygame.GlobalChargeEvent, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onGlobalChargeEvent(self, event):
        ftlog.info('event2->', event, event._encodeToJsonDict())
