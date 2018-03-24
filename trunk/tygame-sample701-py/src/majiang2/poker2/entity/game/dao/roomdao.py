# -*- coding: utf-8 -*-
"""
大厅的基础业务数据
"""


from freetime5.util import ftlog
from tuyoo5.core.tydao import DataSchemaZset


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class DaoTableScore(DataSchemaZset):

    DBNAME = 'table'
    MAINKEY = 'dummy'

    _LUA_GET_BEST_TABLE_ID = '''
        local datas = redis.call("ZRANGE", KEYS[1], -1, -1, "WITHSCORES")
        if datas ~= nil then
            redis.call("ZREM", KEYS[1], datas[1])
            return datas
        end
        return {0, 0}
    '''

    _LUA_UPDATE_TABLE_SCORE = '''
        local tableKey = KEYS[1]
        local tableId = KEYS[2]
        local tableScore = KEYS[3]
        local force = KEYS[4]

        local function ty_tonumber(val)
            val = tonumber(val)
            if val == nil then
                return 0
            end
            return val
        end

        if force then
            return redis.call("ZADD", tableKey, tableScore, tableId)
        else
            local oldScore = redis.call("ZSCORE", tableKey, tableId)
            oldScore = ty_tonumber(oldScore)
            if oldScore <= 0 then
                return redis.call("ZADD", tableKey, tableScore, tableId)
            else
                return oldScore
            end
        end
    '''

    @classmethod
    def getMainKey(cls, cIndex, _mainKeyExt=None):
        return "ts:" + str(_mainKeyExt)

    @classmethod
    def clearTableScore(cls, roomId):
        return cls.DEL(roomId,  roomId)

    @classmethod
    def removeTableScore(cls, roomId, tableId):
        return cls.ZREM(roomId, tableId, roomId)

    @classmethod
    def getBestTableId(cls,   roomId):
        keyList = [
            cls.getMainKey(None, roomId)
        ]
        result = cls.EVALSHA(roomId, cls._LUA_GET_BEST_TABLE_ID, keyList)
        return result

    @classmethod
    def updateTableScore(cls, roomId, tableId, tableScore, force):
        keyList = [
            cls.getMainKey(None, roomId),
            tableId,
            tableScore,
            1 if force else 0,
        ]
        result = cls.EVALSHA(roomId, cls._LUA_UPDATE_TABLE_SCORE, keyList)
        return result
