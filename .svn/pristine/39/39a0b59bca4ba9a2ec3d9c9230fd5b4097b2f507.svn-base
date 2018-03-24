# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh
'''
from freetime5.util import ftlog
from majiang2.entity import majiang_conf
from tuyoo5.core import typlugin, tyglobal
from tuyoo5.plugins.weakdata.weakdata import TyPluginWeakData


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2PluginWeakData(TyPluginWeakData):

    def __init__(self):
        super(Mj2PluginWeakData, self).__init__()

    def destoryPlugin(self):
        super(Mj2PluginWeakData, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=tyglobal.SRV_TYPE_GAME_ALL)
    def initPluginBefore(self):
        super(Mj2PluginWeakData, self).initPluginBefore()

    def _getDBKey(self, roomId):
        '''
        获取DB键值
        '''
        return 'treasurebox_' + str(roomId)

    @typlugin.markPluginEntry(export=1)
    def getTbData(self, userId, gameId, roomId):
        '''
        获取循环任务进度
        '''
        data = self.getDayData(userId, self._getDBKey(roomId))
        if not majiang_conf.ROOMID in data:
            data[majiang_conf.ROOMID] = 0
        if not majiang_conf.PLAYTIMES in data:
            data[majiang_conf.PLAYTIMES] = 0
        if not majiang_conf.LASTTIME in data:
            data[majiang_conf.LASTTIME] = 0
        ftlog.debug('LoopActiveTask._getTbData userId:', userId, ' gameId:', gameId, ' roomId:', roomId, ' data:', data)
        return data

    @typlugin.markPluginEntry(export=1)
    def setTbData(self, userId, gameId, roomId, data):
        '''
        保存循环任务进度
        '''
        rData = self.setDayData(userId, self._getDBKey(roomId), data)
        ftlog.debug('LoopActiveTask._setTbData userId:', userId, ' gameId:', gameId, ' roomId:', roomId, ' data:', data, ' rData:', rData)
        return rData
