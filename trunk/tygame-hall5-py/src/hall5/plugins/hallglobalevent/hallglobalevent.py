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


class HallPluginGlobalEvent(TyPluginGlobalEvent):

    def __init__(self):
        super(HallPluginGlobalEvent, self).__init__()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_HTTP])
    def initPluginBeforeHt(self):
        self.initPub()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBeforeUt(self):
        self.initSub()

    @typlugin.markPluginEntry(event=tygame.GlobalChargeEvent, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onGlobalChargeEvent(self, event):
        ftlog.info('onGlobalChargeEvent->', event, event._encodeToJsonDict())
