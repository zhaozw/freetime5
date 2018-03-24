# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh
对应 GI 进程 主要为机器人或自动AI的处理，
目前majiang2的机器人为桌内机器人，此服务基本为空

'''

from freetime5.util import ftlog
from majiang2.plugins.srvrobot.srvrobot import Mj2PluginRobot
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2XueZhanPluginRobot(Mj2PluginRobot):

    def __init__(self):
        super(Mj2XueZhanPluginRobot, self).__init__()

    def destoryPlugin(self):
        super(Mj2XueZhanPluginRobot, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_ROBOT])
    def initPluginBefore(self):
        super(Mj2XueZhanPluginRobot, self).initPluginBefore()
