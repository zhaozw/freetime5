# -*- coding: utf-8 -*-
"""
大厅的基础业务数据
"""


from freetime5.util import ftlog
from freetime5.util import ftstr
from tuyoo5.core.tydao import DataAttrObjList
from tuyoo5.core.tydao import DataSchemaHashSameKeys


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class DaoMjCreatTable(DataSchemaHashSameKeys):

    DBNAME = 'mix'
    MAINKEY = 'dummy-DaoMjCreatTable'
    SUBVALDEF = DataAttrObjList('dummy-DaoMjCreatTable', [], 512)

    _LUA_ADD_CREATE_TABLE_NO_SCRIPT_NAME = """
    local createTableKey = tostring(KEYS[1])
    local createTableNo = tostring(KEYS[2])
    local serverId = tostring(KEYS[3])
    local tableNoMapKey = tostring(KEYS[4])
    local tableId = tonumber(KEYS[5])
    local tableNoMapValue = tostring(KEYS[6])
    local createParamsKey = tostring(KEYS[7])
    local createParamsContent = tostring(KEYS[8])
    
    local allNos = redis.call("HVALS", createTableKey)
    if #allNos > 0 then
        for k,v in pairs(allNos) do
            local noArr = cjson.decode(v)
            for no_k,no_v in pairs(noArr) do
                if no_v == createTableNo then
                    return false
                end
            end
        end
    end
    local serverIdAllNoStr = redis.call('HGET',createTableKey,serverId)
    local noArr = {}
    if serverIdAllNoStr then
        noArr = cjson.decode(serverIdAllNoStr)
    end
    noArr[#noArr+1] = createTableNo
    local a = redis.call('HSET', createTableKey, serverId, cjson.encode(noArr))
    local b = redis.call('HSET', tableNoMapKey, createTableNo, tableNoMapValue)
    local c = redis.call('HSET', createParamsKey, createTableNo, createParamsContent)
    return a+b+c
    """
    _LUA_REMOVE_CREATE_TABLE_SCRIPT_NAME = """
    local createTableKey = tostring(KEYS[1])
    local createTableNo = tostring(KEYS[2])
    local serverId = tostring(KEYS[3])
    local tableNoMapKey = tostring(KEYS[4])
    local createParamsKey = tostring(KEYS[5])
    local serverIdNos = redis.call("HGET", createTableKey, serverId)
    
    if serverIdNos then
        local serverIdNoArr = cjson.decode(serverIdNos)
        if #serverIdNoArr > 0 then
            for no_k,no_v in pairs(serverIdNoArr) do
                if no_v == createTableNo then
                    table.remove(serverIdNoArr, no_k)
                    redis.call('HSET', createTableKey, serverId, cjson.encode(serverIdNoArr))
                    redis.call('HDEL', tableNoMapKey, createTableNo)
                    redis.call('HDEL', createParamsKey, createTableNo)
                    break
                end
            end
        end
    end
    return true
    """
    _LUA_CLEAR_CREATE_TABLE_SCRIPT_NAME = """
    local createTableKey = tostring(KEYS[1])
    local serverId = tostring(KEYS[2])
    local tableNoMapKey = tostring(KEYS[3])
    local createParamsKey = tostring(KEYS[4])
    local serverIdNos = redis.call("HGET", createTableKey, serverId)
    
    if serverIdNos then
        local serverIdNoArr = cjson.decode(serverIdNos)
        if #serverIdNoArr > 0 then
            for no_k,no_v in pairs(serverIdNoArr) do
                redis.call('HDEL', tableNoMapKey, no_v)
                redis.call('HDEL', createParamsKey, no_v)
            end
        end
    end
    redis.call('HDEL', createTableKey, serverId)
    return true
    """

    @classmethod
    def _getCreateTableNoKey(cls):
        """返回存储所有serverId:[no1,no2...]映射的redis key
        """
        return "dbmj:create_table"

    @classmethod
    def _getTableNoMapTableIdKey(cls):
        """返回存储所有tableNo:tableId映射的redis key
        """
        return "dbmj:create_table_no:hash"

    @classmethod
    def _getTableNoParamsKey(cls):
        """返回存储所有tableNo:tableId映射的redis key
        """
        return "dbmj:create_table_no:params"

    @classmethod
    def clearCreateTableData(cls, serverId):
        """清除重启进程对应的创建牌桌数据 只在GT服调用
        """
        ftlog.info("CreateTableData.clearCreateTableData serverId:", serverId)
        keyList = [cls._getCreateTableNoKey(),
                   serverId,
                   cls._getTableNoMapTableIdKey(),
                   cls._getTableNoParamsKey()
                   ]
        return cls.EVALSHA(0, cls._LUA_CLEAR_CREATE_TABLE_SCRIPT_NAME, keyList)

    @classmethod
    def addCreateTableNo(cls, tableId, roomId, serverId, tableNoKey, initParams):
        """添加自建桌验证码数据 只在GT服调用
        """
        tableNoMapValue = ftstr.dumps([tableId, roomId])
        initString = ftstr.dumps(initParams)
        if _DEBUG:
            debug('CreateTableData.addCreateTableNo tableId:', tableId,
                  ' roomId:', roomId, ' serverId:', serverId,
                  ' tableNoKey:', tableNoMapValue, ' initParams:', initString)
        keyList = [cls._getCreateTableNoKey(),
                   tableNoKey,
                   serverId,
                   cls._getTableNoMapTableIdKey(),
                   tableId,
                   tableNoMapValue,
                   cls._getTableNoParamsKey(),
                   initString]
        result = cls.EVALSHA(0, cls._LUA_ADD_CREATE_TABLE_NO_SCRIPT_NAME, keyList)

        ftlog.info("CreateTableData.addCreateTableNo serverId:", serverId,
                   " tableNoKey:", tableNoKey, " result:", result)
        return result

    @classmethod
    def removeCreateTableNo(cls, serverId, tableNoKey):
        """删除redis中自建桌验证码数据 只在GT服调用
        """
        keyList = [cls._getCreateTableNoKey(),
                   tableNoKey,
                   serverId,
                   cls._getTableNoMapTableIdKey(),
                   cls._getTableNoParamsKey()]
        result = cls.EVALSHA(0, cls._LUA_REMOVE_CREATE_TABLE_SCRIPT_NAME, keyList)

        ftlog.info('CreateTableData.removeCreateTableNo <<< serverId=', serverId,
                   'tableNoKey', tableNoKey, 'result=', result)
        return result

    @classmethod
    def getMainKey(cls, _cIndex, _mainKeyExt=None):
        return _mainKeyExt

    @classmethod
    def getAllCreateTableNoList(cls):
        """获取所有的自建桌验证码列表
        """
        datas = cls.HVALS(0, mainKeyExt=cls._getCreateTableNoKey())
        retArr = []
        if isinstance(datas, list):
            for tableNoList in datas:
                if tableNoList:
                    retArr.extend(tableNoList)
        return retArr

    @classmethod
    def getTableIdByCreateTableNo(cls, createTableNo):
        """通过自建桌验证码查找返回tableId
        """
        tableIdRoomIdList = cls.HGET(0, createTableNo, mainKeyExt=cls._getTableNoMapTableIdKey())
        if tableIdRoomIdList and len(tableIdRoomIdList) == 2:
            return tableIdRoomIdList[0], tableIdRoomIdList[1]
        return 0, 0

    @classmethod
    def getTableParamsByCreateTableNo(cls, createTableNo):
        """通过自建桌号查找返回建桌参数
        """
        tableIdRoomIdList = cls.HGET(0, createTableNo, mainKeyExt=cls._getTableNoParamsKey())
        if tableIdRoomIdList and isinstance(tableIdRoomIdList, list):
            return tableIdRoomIdList
        return None

    @classmethod
    def getAllCreatedTableIdList(cls):
        """返回所有已创建的tableId列表
        """
        datas = cls.HVALS(0, mainKeyExt=cls._getTableNoMapTableIdKey())
        retArr = []
        if isinstance(datas, list):
            for tableIdRoomIdList in datas:
                if len(tableIdRoomIdList) == 2:
                    retArr.append(tableIdRoomIdList[0])
        return retArr
