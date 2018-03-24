# -*- coding=utf-8 -*-
'''
Created on 2016年12月6日

@author: zqh
'''
from freetime5.util import ftlog
from tuyoo5.core import typlugin
from tuyoo5.core import tyglobal
from tuyoo5.plugins.productselector.productselector import TyPluginProductSelector


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2PluginProductSelector(TyPluginProductSelector):

    def __init__(self):
        super(Mj2PluginProductSelector, self).__init__()

    def destoryPlugin(self):
        '''
        当插件被动态卸载时，执行此方法，进行清理工作
        '''
        super(Mj2PluginProductSelector, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=tyglobal.SRV_TYPE_GAME_ALL)
    def initPluginBefore(self):
        super(Mj2PluginProductSelector, self).initPluginBefore()
