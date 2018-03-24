# -*- coding=utf-8 -*-
"""
@file  : test
@date  : 2016-11-10
@author: GongXiaobo
"""

from hall5.plugins.halltest._private.test_exchange import HallPluginTestExchange
from hall5.plugins.halltest._private.test_gamedata import HallPluginTestGameData
from hall5.plugins.halltest._private.test_happybag import HallPluginTestHappyBag
from hall5.plugins.halltest._private.test_store import HallPluginTestStore
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


class HallPluginTest(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginTest, self).__init__()
        self.testStore = HallPluginTestStore()
        self.testExchange = HallPluginTestExchange()
        self.happybag = HallPluginTestHappyBag()
        self.testgamedata = HallPluginTestGameData()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_HTTP])
    def initPluginBefore(self):
        pass

    @typlugin.markPluginEntry(httppath='_test/exchange5')
    def doExchangeTest(self, request):
        return self.testExchange.doExchangeTest(request)

    @typlugin.markPluginEntry(httppath='_test/store')
    def doStoreTest(self, request):
        return self.testStore.doStoreTest(request)

    @typlugin.markPluginEntry(httppath='_test/happybag')
    def doHappyBagTest(self, request):
        return self.happybag.doHappyBagTest(request)

    @typlugin.markPluginEntry(httppath='_test/gamedata')
    def doGameDataTest(self, request):
        return self.testgamedata.doGameDataTest(request)
