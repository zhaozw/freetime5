# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''
from freetime5.util import ftlog
from hall5.plugins.halldata import _daouserdata
from hall5.plugins.halldata._daouserdata import DaoUserData
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class _HallPluginDataUser(object):

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def getUserDataList(self, userId, keys):
        if isinstance(keys, (str, unicode)):
            ret = DaoUserData.HGET(userId, keys)
        else:
            ret = DaoUserData.HMGET(userId, keys)
        return ret

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def getUserDataDict(self, userId, keys):
        values = DaoUserData.HMGET(userId, keys)
        return dict(zip(keys, values))

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def setUserDatas(self, userId, datas):
        return DaoUserData.HMSET(userId, datas)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrDiamond(self, userId, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId,
                    extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        return _daouserdata.incrDiamond(userId, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId,
                                        extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrChip(self, userId, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam,
                 extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        return _daouserdata.incrChip(userId, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam,
                                     extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrChipLimit(self, userId, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam, clientId,
                      extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        return _daouserdata.incrChipLimit(userId, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode,
                                          eventId, intEventParam, clientId,
                                          extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrCoupon(self, userId, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam,
                   extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
        return _daouserdata.incrCoupon(userId, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam,
                                       extentId=extentId, roomId=roomId, tableId=tableId, roundId=roundId,
                                       param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrExp(self, userId, detalExp):
        return _daouserdata.incrExp(userId, detalExp)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrCharm(self, userId, detalCharm):
        return _daouserdata.incrCharm(userId, detalCharm)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def getUserChip(self, userId):
        return _daouserdata.getUserChip(userId)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def getUserChipAll(self, userId):
        return _daouserdata.getUserChipAll(userId)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def getTableChipDict(self, uid):
        '''
        获取所有的tablechip
        '''
        return _daouserdata.getTableChipDict(uid)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def getTableChip(self, uid, gameId, tableId):
        return _daouserdata.getTableChip(uid, gameId, tableId)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def delTableChips(self, uid, tableIdList):
        '''
        删除给出的tablechip
        '''
        return _daouserdata.delTableChips(uid, tableIdList)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrTableChip(self, uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId, tableId,
                      extentId=0, roomId=0, roundId=0, param01=0, param02=0):
        '''
        转移用户所有的chip至tablechip
        参考: set_tablechip_to_range
        '''
        return _daouserdata.incrTableChip(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId, tableId,
                                          extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def incrTableChipLimit(self, uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam, clientId, tableId,
                           extentId=0, roomId=0, roundId=0, param01=0, param02=0):
        '''
        转移用户所有的chip至tablechip
        参考: set_tablechip_to_range
        '''
        return _daouserdata.incrTableChipLimit(uid, gameid, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode, eventId, intEventParam, clientId, tableId,
                                               extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def moveAllChipToTableChip(self, uid, gameid, eventId, intEventParam, clientId, tableId,
                               extentId=0, roomId=0, roundId=0, param01=0, param02=0):
        '''
        转移用户所有的chip至tablechip
        参考: set_tablechip_to_range
        '''
        return _daouserdata.moveAllChipToTableChip(uid, gameid, eventId, intEventParam, clientId, tableId,
                                                   extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def moveAllTableChipToChip(self, uid, gameid, eventId, intEventParam, clientId, tableId, 
                               extentId=0, roomId=0, roundId=0, param01=0, param02=0):
        '''
        转移用户所有的tablechip至chip
        参考: set_tablechip_to_range
        '''
        return _daouserdata.moveAllTableChipToChip(uid, gameid, eventId, intEventParam, clientId, tableId,
                                                   extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def setTableChipToN(self, uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                        extentId=0, roomId=0, roundId=0, param01=0, param02=0):
        '''
        设置用户的tablechip至传入的值
        参考: set_tablechip_to_range
        '''
        return _daouserdata.setTableChipToN(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                                            extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def setTableChipToBigThanN(self, uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                               extentId=0, roomId=0, roundId=0, param01=0, param02=0):
        '''
        设置用户的tablechip大于等于传入的值
        参考: set_tablechip_to_range
        '''
        return _daouserdata.setTableChipToBigThanN(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                                                   extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def setTableChipToNIfLittleThan(self, uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                                    extentId=0, roomId=0, roundId=0, param01=0, param02=0):
        '''
        如果用户的tablechip小于传入的值, 至那么设置tablechip至传入的值
        参考: set_tablechip_to_range
        '''
        return _daouserdata.setTableChipToNIfLittleThan(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                                                        extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def setTablechipNearToNIfLittleThan(self, uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                                        extentId=0, roomId=0, roundId=0, param01=0, param02=0):
        '''
        tablechip 小于 n 时, 让 tablechip 尽量接近 n
        参考: set_tablechip_to_range
        '''
        return _daouserdata.setTablechipNearToNIfLittleThan(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId,
                                                            extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def setTableChipToRange(self, uid, gameid, _min, _max, eventId, intEventParam, clientId, tableId,
                            extentId=0, roomId=0, roundId=0, param01=0, param02=0):
        return _daouserdata.setTableChipToRange(uid, gameid, _min, _max, eventId, intEventParam, clientId, tableId,
                                                extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)
