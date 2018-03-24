# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''
from datetime import datetime, timedelta

from freetime5.util import ftlog
from freetime5.util import fttime
from hall5.plugins.halldata import _daohalldata
from hall5.plugins.halldata._daohalldata import DaoGameDataHall
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core.tyrpchall import HallKeys


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class _HallPluginDataHall(object):

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL, export=1)
    def getHallDataList(self, userId, keys):
        """
        取得用户的大厅数据内容（即游戏gamedata:9999:<userId>存储的数据内容）
        @param userId: 用户ID
        @param keys: 数据字段列表，如果为空，则获取所有信息, 请使用HallKeys中定义的KEY值
        """
        if isinstance(keys, (str, unicode)):
            ret = DaoGameDataHall.HGET(userId, keys)
        else:
            ret = DaoGameDataHall.HMGET(userId, keys)
        return ret

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrSetNameSum(self, userId, detal):
        return DaoGameDataHall.HINCRBY(userId, HallKeys.ATT_SET_NAME_SUM, detal)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def getSetNameSum(self, userId):
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_SET_NAME_SUM)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrDaShiFen(self, userId, detalDaShiFen):
        ret = _daohalldata.incrDaShiFen(userId, detalDaShiFen)
# 51自运营版本，不支持排行榜
#         pluginSafeCross.hallrank.setUserByInputType(userId, tyglobal.gameId(),
#                                                     HallRankingInputTypes.DASHIFEN_INCR, detalDaShiFen)
        return ret

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrLoginDays(self, userId, deltaCount):
        return DaoGameDataHall.HINCRBY(userId, HallKeys.ATT_LOGIN_DAYS, deltaCount)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrLoginSum(self, userId, deltaCount):
        return DaoGameDataHall.HINCRBY(userId, HallKeys.ATT_LOGIN_SUM, deltaCount)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _setDataValue(self, userId, attName, attValue):
        return DaoGameDataHall.HSET(userId, attName, attValue)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL, export=1)
    def set_monthcheckin(self, userId, d):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_MONTH_CHECKIN, d)

    @typlugin.markPluginEntry(export=1)
    def first_roulette(self, userId):
        return DaoGameDataHall.HSETNX(userId, HallKeys.ATT_FIRST_ROULETTE, 1)

    @typlugin.markPluginEntry(export=1)
    def first_gold_roulette(self, userId):
        return DaoGameDataHall.HSETNX(userId, HallKeys.ATT_FIRST_GOLD_ROULETTE, 1)

    @typlugin.markPluginEntry(export=1)
    def roulette_attend_soldier_lottery(self, userId):
        return DaoGameDataHall.HINCRBY(userId, HallKeys.ATT_CHECKIN_SOLDIERS, 1)

    @typlugin.markPluginEntry(export=1)
    def roulette_soldier_reward(self, userId):
        return DaoGameDataHall.HINCRBY(userId, HallKeys.ATT_GET_REWARD_NUM, 1)

    @typlugin.markPluginEntry(export=1)
    def getNewMsgId(self, userId):
        return DaoGameDataHall.HINCRBY(userId, HallKeys.ATT_MESSAGE_ID_MAX, 1)

    @typlugin.markPluginEntry(export=1)
    def updateReadSysMsgId(self, userId, readId):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_MESSAGE_ID_SYSTEM, readId)

    @typlugin.markPluginEntry(export=1)
    def updateReadPriMsgId(self, userId, readId):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_MESSAGE_ID_PRIVATE, readId)

    @typlugin.markPluginEntry(export=1)
    def set_submember(self, userId, d):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_SUBMEMBER, d)

    @typlugin.markPluginEntry(export=1)
    def add_share_count(self, userId, delta):
        return DaoGameDataHall.HINCRBY(userId, HallKeys.ATT_SHARE_COUNT, delta)

    @typlugin.markPluginEntry(export=1)
    def set_moduletip(self, userId, d):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_MODULE_TIP, d)

    @typlugin.markPluginEntry(export=1)
    def userAliveTime(self, userId):
        # 记录活动时间
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_ALIVE_TIME, fttime.formatTimeMs())

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrVipExp(self, userId, count):
        '''
        给用户增加count个经验值，count可以为负数
        @param userId: 哪个用户
        @param count: 数量
        @return: 变化后的值
        '''
        return DaoGameDataHall.HINCRBY(userId, HallKeys.ATT_VIP_EXP, count)

    @typlugin.markPluginEntry(export=1)
    def saveVipGiftStatus(self, userId, vipGiftStatus):
        '''
        保存用户VIP礼包状态
        @param userId: 哪个用户
        @param vipGiftStatus: 用户VIP礼包状态
        '''
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_VIP_GIFT_STATES, vipGiftStatus)

    @typlugin.markPluginEntry(export=1)
    def setLastBuy(self, userId, d):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_LAST_BUY, d)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def isFirstRecharged(self, userId):
        """
        判定该用户是否首次充值
        """
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_FIRST_RECHARGE)

    @typlugin.markPluginEntry(export=1)
    def setnxFirstRecharge(self, userId):
        return DaoGameDataHall.HSETNX(userId, HallKeys.ATT_FIRST_RECHARGE, 1)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def isGetFirstRechargeReward(self, userId):
        """
        判定该用户是否首次充值奖励
        """
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_FIRST_RECHARGE_REWARD)

    @typlugin.markPluginEntry(export=1)
    def setFirstRechargeReward(self, userId):
        return DaoGameDataHall.HSETNX(userId, HallKeys.ATT_FIRST_RECHARGE_REWARD, 1)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrPlayTime(self, userId, detalTime, gameId, roomId, tableId):
        """
        各个游戏向大厅汇报玩家的游戏时长
        """
        DaoGameDataHall.HINCRBY(userId, HallKeys.ATT_TOTAL_TIME, detalTime)
        datas = DaoGameDataHall.HGET(userId, HallKeys.ATT_TODAY_TIME)
        today = datetime.now().strftime('%Y%m%d')[-6:]
        if today in datas:
            datas[today] += detalTime
        else:
            datas[today] = detalTime
        oldday = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')[-6:]
        for k in datas.keys()[:]:
            if k < oldday:
                del datas[k]
        DaoGameDataHall.HSET(userId, HallKeys.ATT_TODAY_TIME, datas)
        return 1

    @typlugin.markPluginEntry(export=1)
    def getNewUserFlg(self, userId):
        '''
        删除新用户的标记(新用户标记，主要用与发放启动资金)
        '''
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_NEW_USER)

    @typlugin.markPluginEntry(export=1)
    def delNewUserFlg(self, userId):
        '''
        删除新用户的标记(新用户标记，主要用与发放启动资金)
        '''
        return DaoGameDataHall.HDEL(userId, HallKeys.ATT_NEW_USER)

    @typlugin.markPluginEntry(export=1)
    def getBeneFitsInfo(self, userId):
        '''
        '''
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_BENEFITS)

    @typlugin.markPluginEntry(export=1)
    def setBeneFitsInfo(self, userId, datas):
        '''
        '''
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_BENEFITS, datas)

    @typlugin.markPluginEntry(export=1)
    def getReliefShareDate(self, userId):
        '''
        '''
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_RELIEF_SHARE_DATE)

    @typlugin.markPluginEntry(export=1)
    def setReliefShareDate(self, userId, timestamp):
        '''
        '''
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_RELIEF_SHARE_DATE, timestamp)


    @typlugin.markPluginEntry(export=1)
    def isFirstGamelist5(self, userId):
        """
        判定该用户是否第一次使用gamelist5
        """
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_FIRST_GAME_LIST5)

    @typlugin.markPluginEntry(export=1)
    def changeFirstGamelist5(self, userId):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_FIRST_GAME_LIST5, 1)

    @typlugin.markPluginEntry(export=1)
    def getUpdateToVersion511flag(self, userId):
        """
        判定该用户是否升级到5.11
        """
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_UPDATE_CLIENT_VERSION_TO_511)

    @typlugin.markPluginEntry(export=1)
    def setUpdateToVersion511flag(self, userId):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_UPDATE_CLIENT_VERSION_TO_511, 1)

    @typlugin.markPluginEntry(export=1)
    def getLoginBeforeVersion511flag(self, userId):
        """
        判定该用户是否在5.11版本之前登录过
        """
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_LOGIN_BEFORE_VERSION_TO_511)

    @typlugin.markPluginEntry(export=1)
    def setLoginBeforeVersion511flag(self, userId):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_LOGIN_BEFORE_VERSION_TO_511, 1)

    @typlugin.markPluginEntry(export=1)
    def getBiggestHallVersion(self, userId):
        """
        取得用户登录过的最高客户端版本
        """
        return DaoGameDataHall.HGET(userId, HallKeys.ATT_BIGGEST_HALL5_VERSION)

    @typlugin.markPluginEntry(export=1)
    def setBiggestHallVersion(self, userId, version):
        return DaoGameDataHall.HSET(userId, HallKeys.ATT_BIGGEST_HALL5_VERSION, version)