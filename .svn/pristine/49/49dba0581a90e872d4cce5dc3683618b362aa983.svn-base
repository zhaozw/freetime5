# -*- coding: utf-8 -*-
'''
Created on 2016年5月1日

@author: zqh
'''

from freetime5.twisted import ftcore
from freetime5.util import ftlog
from hall5.plugins.halldatanotify import _datanotify
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginDataNotify(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginDataNotify, self).__init__()
        self._flushTimer = None

    @typlugin.markPluginEntry(initAfterConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPlugin(self):
        self._flushTimer = ftcore.runLoopSync(0.5, _datanotify._flushDataChangeNotify)

    def destoryPlugin(self):
        if self._flushTimer:
            self._flushTimer.cancel()
            self._flushTimer = None

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL, export=1)
    def sendDataChangeNotify(self, userId, gameId, changedList):
        """
        通知客户端某一个数据需要进行重新下载更新
        @param userId: 用户ID
        @param gameId: 游戏ID
        @param changedList: 变化的数据模块名称或名称列表
        """
        if changedList:
            _datanotify._sendDataChangeNotify(userId, gameId, changedList)
        return 1
