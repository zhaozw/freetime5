# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh

对应 GS 进程，游戏内部的单点任务处理，例如排行榜统一定时发奖等
'''

from freetime5.util import ftlog
from majiang2.plugins.srvjobs.srvjobs import Mj2PluginSrvJobs
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2XueZhanPluginSrvJobs(Mj2PluginSrvJobs):

    def __init__(self):
        super(Mj2XueZhanPluginSrvJobs, self).__init__()

    def destoryPlugin(self):
        super(Mj2XueZhanPluginSrvJobs, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_SINGLETON])
    def initPluginBefore(self):
        super(Mj2XueZhanPluginSrvJobs, self).initPluginBefore()
