# -*- coding=utf-8 -*-
"""
Created on 2017年10月23日10:31:44

@author: yzx
"""
from freetime5.util import ftlog
from hall5.entity import hallchecker
from hall5.plugins.hallmatch._private import _match
from hall5.plugins.hallmatch._private import _dao
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin



_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginMatch(typlugin.TYPlugin):
    """
    获取用户的比赛历时记录及报名信息.
    """
    def __init__(self):
        super(HallPluginMatch, self).__init__()
        self.checkBase = hallchecker.CHECK_BASE.clone()

    def destoryPlugin(self):
        _dao.DaoMatchHistory.finalize()
        _dao.DaoMatchSignin.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        _dao.DaoMatchHistory.initialize()
        _dao.DaoMatchSignin.initialize()

    @typlugin.markPluginEntry(cmd='match_data5', act='list', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doMatchData(self, msg):
        """
        客户端查询比赛历史数据,对应我的比赛
        """
        if _DEBUG:
            debug('HallPluginMatch.doMatchData->', msg)
        mi = self.checkBase.check(msg)
        if mi.error:
            return 0
        _match._sendMatchDataResponse(mi.userId, mi.gameId, mi.clientId, mi.apiVersion)
        return 1
