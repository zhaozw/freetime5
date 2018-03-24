# -*- coding: utf-8 -*-
"""
大厅的基础业务数据
"""

from freetime5.util import ftlog
from freetime5.util import fttime
from majiang2.plugins.mj2dao._private._daoattrs import MajangKeys
from tuyoo5.core import tyglobal
from tuyoo5.core.tydao import DataSchemaHashAttrs


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class DaoMjGameData(DataSchemaHashAttrs):
    DBNAME = 'user'
    MAINKEY = 'gamedata:%s:%s' % (tyglobal.gameId(), '%s')
    ATTS = MajangKeys

    @classmethod
    def getMainKey(cls, cIndex, _mainKeyExt=None):
        return cls.MAINKEY % (cIndex)

    @classmethod
    def checkAndInit(cls, userId):
        '''
        若数据字段小于3项，认为没有数据或丢失，重新建立数据
        '''
        if cls.HLEN(userId) < 4:
            attDataDict = {}
            ct = fttime.formatTimeMs()
            attDataDict[MajangKeys.ATT_CREATE_TIME] = ct
            attDataDict[MajangKeys.ATT_AUTHOR_TIME] = ct
            attDataDict[MajangKeys.ATT_OFFLINE_TIME] = ct
            attDataDict[MajangKeys.ATT_ALIVE_TIME] = ct
            attDataDict[MajangKeys.ATT_DATA_VERSION] = 5.1
            cls.HMSET(userId, attDataDict)
            return True
        return False
