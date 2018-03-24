# -*- coding=utf-8 -*-
"""
Created on 2017年10月31日11:44:07

@author: yzx
"""
import re
from freetime5.util import ftlog
from hall5.entity import hallchecker
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from hall5.plugins.hallgamemanager._private import _gamemanager
from hall5.plugins.hallgamemanager._private import _dao


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


def check_gameIds(msg, result, name):
    """
    校验添加和删除协议上传递的gameIds参数,需为数组.
    """
    val = msg.getParam(name, [])
    if len(val) <= 0 or not isinstance(val, list):
        return None, 'the param %s error' % (name,)
    for item in val:
        # 校验一下node的id长度，和配置系统一起定长到50,超长即返回;正则规则校验
        if not isinstance(item,(str, unicode)) or len(item) > 50 or not re.match(r'^[A-Za-z]+(\:\d+){2}', item):
            return None, 'the param %s illegal ,value %s' % (name,val)
    return val, None


class HallPluginGameManager(typlugin.TYPlugin):
    """
    新版gamelist功能，支持运营、推荐及地方配置，支持用户自定义.
    """
    def __init__(self):
        super(HallPluginGameManager, self).__init__()
        self.checkBase = hallchecker.CHECK_BASE.clone()
        self.checker = hallchecker.CHECK_BASE.clone()
        self.checker.addCheckFun(check_gameIds)

    def destoryPlugin(self):
        _dao.DaoGameList5Set.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        _dao.DaoGameList5Set.initialize()

    @typlugin.markPluginEntry(export=1)
    def sendAllHallGameManager(self, userId, intClientId, apiVersion):
        """
        在hall5.binduser后主动推送到客户端
        """
        if _DEBUG:
            debug('sendAllHallGamemanager IN->', userId, intClientId, apiVersion)
        return _gamemanager.allHallGameManager(userId, intClientId, apiVersion)

    @typlugin.markPluginEntry(cmd='hall_gamelist5', act="all", srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doAllHallGameManager(self, msg):
        """
        测试用.
        """
        mi = self.checkBase.check(msg)
        if _DEBUG:
            debug('doAllHallGamemanager IN->', mi)
        if mi.error:
            ftlog.warn('doAllHallGamemanager', msg, mi.error)
            return 0
        _gamemanager.allHallGameManager(mi.userId, mi.clientId, mi.apiVersion)
        return 1

    @typlugin.markPluginEntry(cmd='hall_gamelist5', act="get", srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doGetHallGameManager(self, msg):
        """
        获取待添加游戏插件列表
        """
        mi = self.checkBase.check(msg)
        if _DEBUG:
            debug('doGetHallGamemanager IN->', mi)
        if mi.error:
            ftlog.warn('doGetHallGamemanager', msg, mi.error)
            return 0
        _gamemanager.getHallGameManager(mi.userId, mi.clientId, mi.apiVersion)
        return 1

    @typlugin.markPluginEntry(cmd='hall_gamelist5', act="add", srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doAddHallGameManager(self, msg):
        mi = self.checker.check(msg)
        if _DEBUG:
            debug('doAddHallGamemanager IN->', mi)
        if mi.error:
            ftlog.warn('doAddHallGameManager', msg, mi.error)
            return 0
        _gamemanager.addHallGameManager(mi.userId, mi.clientId, mi.apiVersion, mi.gameIds)
        return 1

    @typlugin.markPluginEntry(cmd='hall_gamelist5', act="del", srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doDelHallGameManager(self, msg):
        mi = self.checker.check(msg)
        if _DEBUG:
            debug('doDelHallGamemanager IN->', mi)
        if mi.error:
            ftlog.warn('doDelHallGameManager', msg, mi.error)
            return 0
        _gamemanager.delHallGameManager(mi.userId, mi.clientId, mi.apiVersion, mi.gameIds)
        return 1
