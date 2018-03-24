# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh
'''

from freetime5.util import ftlog
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2PluginSrvJobs(typlugin.TYPlugin):

    def __init__(self):
        super(Mj2PluginSrvJobs, self).__init__()

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_SINGLETON])
    def initPluginBefore(self):
        pass
