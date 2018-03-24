# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''

from freetime5.twisted.ftlock import lockargname
from freetime5.util import ftlog, ftreflect
from hall5.plugins.hallitem._private import itemdao
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.plugins.item import itemsys, items
from tuyoo5.plugins.item.item import TYPluginItem
import importlib


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginItemLife(TYPluginItem):

    def _regPackages(self, basepkg, reg, isReg, clz):
        if _DEBUG:
            debug('HallPluginItemLife->_regPackages IN', basepkg, basepkg.__path__)
        pkgs = ftreflect.findSubModuleNames(basepkg)
        for pkg in pkgs:
            m = importlib.import_module(pkg)
            if _DEBUG:
                debug('HallPluginItemLife->_regPackages', m)
            if isReg:
                reg.registerModule(m, clz, True)
            else:
                reg.unRegisterModule(m, clz)

    def destoryPlugin(self):
        TYPluginItem.destoryPlugin(self)

        from hall5.plugins.hallitem._private import assetkind
        itemsys.REG_ASSET_KIND.unRegisterModule(assetkind, items.TYAssetKind)

        from hall5.plugins.hallitem._private import _actions
        self._regPackages(_actions, itemsys.REG_ITEM_ACTION, 0, items.TYItemAction)

        from hall5.plugins.hallitem._private import _items
        self._regPackages(_items, itemsys.REG_ITEM_KIND, 0, items.TYItemKind)

        itemdao.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_HTTP])
    def initHHPluginBefore(self):
        TYPluginItem.initPluginBefore(self)

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initHUPluginBefore(self):
        TYPluginItem.initPluginBefore(self)

        from hall5.plugins.hallitem._private import assetkind
        itemsys.REG_ASSET_KIND.registerModule(assetkind, items.TYAssetKind, True)

        from hall5.plugins.hallitem._private import _actions
        self._regPackages(_actions, itemsys.REG_ITEM_ACTION, 1, items.TYItemAction)

        from hall5.plugins.hallitem._private import _items
        self._regPackages(_items, itemsys.REG_ITEM_KIND, 1, items.TYItemKind)

        from hall5.plugins.hallitem._private.item import HallItemSystem
        itemsys.itemSystem = HallItemSystem()

        itemdao.initialize()

    @typlugin.markPluginEntry(confKeys=['game5:{}:item:sc'.format(HALL_GAMEID)],
                              srvType=[tyglobal.SRV_TYPE_HALL_UTIL])
    def onConfChanged(self, confKeys, changedKeys):
        TYPluginItem.onConfChanged(self, confKeys, changedKeys)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.item', 'userId')
    def cleanItemCache(self, userId):
        '''
        清理用户Item缓存,重新加载
        :param userId:
        :return:
        '''
        itemsys.itemSystem.clearCacheByUserId(userId)
        return 0, 'ok'
