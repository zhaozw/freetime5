# -*- coding: utf-8 -*-
"""
大厅的基础业务数据
"""

import time

from freetime5.util import ftlog
from tuyoo5.core import tyglobal
from tuyoo5.core.tydao import DataAttrObjDict
from tuyoo5.core.tydao import DataAttrObjList
from tuyoo5.core.tydao import DataSchemaHashSameKeys
from tuyoo5.core.tydao import DataSchemaString


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class DaoMjTableRecordKeys(DataSchemaHashSameKeys):

    DBNAME = 'user'
    MAINKEY = 'dummy-DaoMjTableRecordKeys'
    RECORDKEY = '%s:gamedata:record:key:%s'
    SUBVALDEF = DataAttrObjList('dummy-DaoMjTableRecordKeys', [], 512)

    @classmethod
    def getMainKey(cls, cIndex, _mainKeyExt=None):
        return 'gamedata:%s:%s' % (tyglobal.gameId(), cIndex)

    @classmethod
    def getRecordKeyList(cls, userId):
        return cls.HGET(userId, cls.RECORDKEY % (tyglobal.gameId(), userId))

    @classmethod
    def setRecordKeyList(cls, userId, keyList):
        return cls.HSET(userId, cls.RECORDKEY % (tyglobal.gameId(), userId), keyList)


class DaoMjTableRecordData(DataSchemaString):

    DBNAME = 'replay'
    MAINKEY = 'dummy-DaoMjTableRecordData'
    RECORDKEY = '{}:gamedata:record:replay:%s%s'.format(tyglobal.gameId())
    SUBVALDEF = DataAttrObjDict('dummy-DaoMjTableRecordData', {}, 512)

    @classmethod
    def getMainKey(cls, cIndex, _mainKeyExt=None):
        return cIndex

    @classmethod
    def setReplayRecord(cls, userId, playerRecordInfo):
        recordContentKey = cls.RECORDKEY % (userId, int(time.time()))
        cls.SET(recordContentKey, recordContentKey, playerRecordInfo)
        return recordContentKey

    @classmethod
    def getReplayRecord(cls, recordContentKey):
        return cls.GET(recordContentKey)

    @classmethod
    def removeReplayRecord(cls, recordContentKey):
        return cls.DEL(recordContentKey)
