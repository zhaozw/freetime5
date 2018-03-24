# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''
from freetime5.util import ftlog, fttime
from majiang2.entity import majiang_conf
from majiang2.plugins.mj2dao._private._creattable import DaoMjCreatTable
from majiang2.plugins.mj2dao._private._daoattrs import MajangKeys
from majiang2.plugins.mj2dao._private._daogamedata import DaoMjGameData
from majiang2.plugins.mj2dao._private._mix import DaoMjMixRoundId
from majiang2.plugins.mj2dao._private._mix import DaoMjMixPutCard
from majiang2.plugins.mj2dao._private._tablerecord import DaoMjTableRecordData
from majiang2.plugins.mj2dao._private._tablerecord import DaoMjTableRecordKeys
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2PluginData(typlugin.TYPlugin):

    def destoryPlugin(self):
        '''
        当插件被动态卸载时，执行此方法，进行清理工作
        '''
        DaoMjTableRecordKeys.finalize()
        DaoMjTableRecordData.finalize()
        DaoMjCreatTable.finalize()
        DaoMjMixRoundId.finalize()
        DaoMjMixPutCard.finalize()
        DaoMjGameData.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=tyglobal.SRV_TYPE_GAME_ALL)
    def initPluginBefore(self):
        DaoMjTableRecordKeys.initialize()
        DaoMjTableRecordData.initialize()
        DaoMjCreatTable.initialize()
        DaoMjMixRoundId.initialize()
        DaoMjMixPutCard.initialize()
        DaoMjGameData.initialize()

    @typlugin.markPluginEntry(export=1)
    def getRecordKeyList(self, userId):
        return DaoMjTableRecordKeys.getRecordKeyList(userId)

    @typlugin.markPluginEntry(export=1)
    def setRecordKeyList(self, userId, keyList):
        return DaoMjTableRecordKeys.setRecordKeyList(userId, keyList)

    @typlugin.markPluginEntry(export=1)
    def setReplayRecord(self, userId, playerRecordInfo):
        return DaoMjTableRecordData.setReplayRecord(userId, playerRecordInfo)

    @typlugin.markPluginEntry(export=1)
    def getReplayRecord(self, recordContentKey):
        return DaoMjTableRecordData.getReplayRecord(recordContentKey)

    @typlugin.markPluginEntry(export=1)
    def removeReplayRecord(self, recordContentKey):
        return DaoMjTableRecordData.removeReplayRecord(recordContentKey)

    @typlugin.markPluginEntry(export=1)
    def clearCreateTableData(self, serverId):
        return DaoMjCreatTable.clearCreateTableData(serverId)

    @typlugin.markPluginEntry(export=1)
    def addCreateTableNo(self, tableId, roomId, serverId, tableNoKey, initParams):
        return DaoMjCreatTable.addCreateTableNo(tableId, roomId, serverId, tableNoKey, initParams)

    @typlugin.markPluginEntry(export=1)
    def removeCreateTableNo(self, serverId, tableNoKey):
        return DaoMjCreatTable.removeCreateTableNo(serverId, tableNoKey)

    @typlugin.markPluginEntry(export=1)
    def getAllCreateTableNoList(self):
        return DaoMjCreatTable.getAllCreateTableNoList()

    @typlugin.markPluginEntry(export=1)
    def getTableIdByCreateTableNo(self, createTableNo):
        return DaoMjCreatTable.getTableIdByCreateTableNo(createTableNo)

    @typlugin.markPluginEntry(export=1)
    def getTableParamsByCreateTableNo(self, createTableNo):
        return DaoMjCreatTable.getTableParamsByCreateTableNo(createTableNo)

    @typlugin.markPluginEntry(export=1)
    def getAllCreatedTableIdList(self):
        return DaoMjCreatTable.getAllCreatedTableIdList()

    @typlugin.markPluginEntry(export=1)
    def getHistoryWinStreak(self, userId):
        return DaoMjGameData.HGET(userId, MajangKeys.ATT_HISTORY_WIN_STREAK)

    @typlugin.markPluginEntry(export=1)
    def setHistoryWinStreak(self, userId, historyWinStreak):
        return DaoMjGameData.HSET(userId, MajangKeys.ATT_HISTORY_WIN_STREAK, historyWinStreak)

    @typlugin.markPluginEntry(export=1)
    def getHasGetCoupon(self, userId):
        return DaoMjGameData.HGET(userId, MajangKeys.ATT_HAS_GET_COUPON)

    @typlugin.markPluginEntry(export=1)
    def setHasGetCoupon(self, userId, hasGetCoupon):
        return DaoMjGameData.HSET(userId, MajangKeys.ATT_HAS_GET_COUPON, hasGetCoupon)

    @typlugin.markPluginEntry(export=1)
    def getQuickStartCoinTimeStamp(self, userId):
        return DaoMjGameData.HGET(userId, MajangKeys.ATT_QUICK_START_COIN_TIMESTAMP)

    @typlugin.markPluginEntry(export=1)
    def setQuickStartCoinTimeStamp(self, userId, quickStartCoinTimeStamp):
        return DaoMjGameData.HSET(userId, MajangKeys.ATT_QUICK_START_COIN_TIMESTAMP, quickStartCoinTimeStamp)

    @typlugin.markPluginEntry(export=1)
    def getQuickStartLastInfo(self, userId):
        return DaoMjGameData.HMGET(userId, [
            MajangKeys.ATT_LAST_TABLE_COIN,
            MajangKeys.ATT_LAST_ROOM_ID,
            MajangKeys.ATT_LAST_LEAVE_TIME])

    @typlugin.markPluginEntry(export=1)
    def setQuickStartLastInfo(self, userId, lastTableCoin, lastRoomId, lastLeaveTime):
        return DaoMjGameData.HMSET(userId, {
            MajangKeys.ATT_LAST_TABLE_COIN: lastTableCoin,
            MajangKeys.ATT_LAST_ROOM_ID: lastRoomId,
            MajangKeys.ATT_LAST_LEAVE_TIME: lastLeaveTime
        })

    @typlugin.markPluginEntry(export=1)
    def incrPlayGameCount(self, userId):
        return DaoMjGameData.HINCRBY(userId, MajangKeys.ATT_PLAY_GAME_COUNT, 1)

    @typlugin.markPluginEntry(export=1)
    def incrMajiang2RoundId(self):
        return DaoMjMixRoundId.incrMajiang2RoundId()

    @typlugin.markPluginEntry(export=1)
    def getPutCard(self, playMode):
        return DaoMjMixPutCard.getPutCard(playMode)

    @typlugin.markPluginEntry(export=1)
    def setPutCard(self, playMode, cards):
        return DaoMjMixPutCard.setPutCard(playMode, cards)

    @typlugin.markPluginEntry(export=1)
    def delPutCard(self, playMode):
        return DaoMjMixPutCard.delPutCard(playMode)

    @typlugin.markPluginEntry(export=1)
    def getGameInfo(self, userId, clientId, gameId):
        """ 获取玩家的游戏数据
        """
        values = DaoMjGameData.HMGET(userId, DaoMjGameData.ATTS_ALL_LIST)
        gdata = dict(zip(DaoMjGameData.ATTS_ALL_LIST, values))
        return gdata

    @typlugin.markPluginEntry(export=1)
    def createGameData(self, userId, clientId, gameId):
        """ 创建玩家的游戏数据
        """
        _isCreate = DaoMjGameData.checkAndInit(userId)
        return _isCreate

    @typlugin.markPluginEntry(export=1)
    def loginGame(self, userId, gameId, clientId, iscreate, isdayfirst):
        """ 用户登录一个游戏, 游戏自己做一些其他的业务或数据处理
        """
        if isdayfirst:
            DaoMjGameData.HSET(userId, MajangKeys.ATT_DAY_PLAY_GAME_COUNT, 0)
        DaoMjGameData.HSET(userId, MajangKeys.ATT_AUTHOR_TIME, fttime.formatTimeMs())
        return DaoMjGameData.HINCRBY(userId, MajangKeys.ATT_LOGIN_SUM, 1)

    @typlugin.markPluginEntry(export=1)
    def getDaShiFen(self, userId, clientId, gameId):
        """ 获取玩家大师分信息
        """
        master_point = DaoMjGameData.HGET(userId, MajangKeys.ATT_MASTER_POINT)
        master_point_level = 0
        config = majiang_conf.get_medal_ui_config(gameId)
        title_pic, level_pic = '', ''
        if config:
            title_pic = config['title']
            level_pic = config['level'] % master_point_level

        return {
            'name':             '麻将',
            'skillscore':       master_point,
            'level':            master_point_level,
            'pic':              level_pic,
            'title':            title_pic,
            'des':              '麻将房间中每次胜利都可获得雀神分，高倍数、高级房间、会员获得的更快！',
            'score':            master_point,
            'grade':            1,
            'premaxscore':      0,
            'curmaxscore':      0,
        }
