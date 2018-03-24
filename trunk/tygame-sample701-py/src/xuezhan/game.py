# -*- coding=utf-8 -*-
'''
Created on 2015年9月25日

@author: liaoxx
'''
from freetime5.util import ftlog
from majiang2.poker2.entity.game.rooms import tyRoomConst
from majiang2.poker2.entity.game.rooms.normal_room import TYNormalRoom
from tuyoo5.core import tygame, tyglobal
from xuezhan.table.majiang_friend_table import XueZhanMajiangFriendTable
from xuezhan.table.majiang_quick_table import XueZhanMajiangQuickTable


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class _TGXueZhan(tygame.TYGame):

    def __init__(self):
        super(_TGXueZhan, self).__init__()
        self._eventBus = tygame.TYEventBus()

    def getEventBus(self):
        return self._eventBus

    def initGameBefore(self):
        ftlog.info('_TGXueZhan.initGameBefore IN')
        super(_TGXueZhan, self).initGameBefore()
        srvType = tyglobal.serverType()

        if srvType in (tyglobal.SRV_TYPE_GAME_ROOM, tyglobal.SRV_TYPE_GAME_TABLE):
            from majiang2.poker2.entity.game.dao import roomdao
            roomdao.DaoTableScore.initialize()
        ftlog.info('_TGXueZhan.initGameBefore OUT')

    def initGame(self):
        ftlog.info('_TGXueZhan.initGame IN')
        super(_TGXueZhan, self).initGame()
        srvType = tyglobal.serverType()
        if srvType in (tyglobal.SRV_TYPE_HALL_SINGLETON, tyglobal.SRV_TYPE_HALL_UTIL):
            '''
            当进程为UTIL和SINGLETON时，初始化以下模块
            '''
            pass

        ftlog.info('_TGXueZhan.initGame OUT')

    def initGameAfter(self):
        ftlog.info('_TGXueZhan.initGameAfter IN')
        super(_TGXueZhan, self).initGameAfter()
        ftlog.info('_TGXueZhan.initGameAfter OUT')

    def getRoomInstance(self, roomdefine):
        '''
        工场设计模式，根据不同的房间配置信息创建不同类型的room对象实例
        子类可更具更新的实际要求，覆盖此方法
        必须返回 TYRoom 子类实例
        '''
        if _DEBUG:
            debug('TGXueZhan.getRoomInstance->', roomdefine)
        roomTypeName = roomdefine.configure['typeName']
        if _DEBUG:
            debug("TGXueZhan.getRoomInstance |roomId, roomType:", roomdefine.roomId, roomTypeName)
        if roomTypeName == tyRoomConst.ROOM_TYPE_NAME_NORMAL:
            return TYNormalRoom(roomdefine)
        raise Exception('the room type not know [%s]!' % (roomTypeName))

    def getTableInstance(self, room, tableId):
        '''
        工场设计模式，根据不同的房间配置信息创建不同类型的table对象实例
        子类可更具更新的实际要求，覆盖此方法
        必须返回 TYTable 子类实例
        '''
        if _DEBUG:
            debug('TGXueZhan.getTableInstance->', tableId, room.roomConf)
        playMode = room.roomConf.get("playMode", "xuezhan")
        isCreateTable = room.roomConf.get("iscreate", 0)
        if _DEBUG:
            debug('TGXueZhan.getTableInstance playMode:', playMode, ' isCreateTable:', isCreateTable)
        # 根据playMode和isCreateTable决定实例化那张桌子
        if isCreateTable:
            table = XueZhanMajiangFriendTable(tableId, room)
        else:
            table = XueZhanMajiangQuickTable(tableId, room)
        return table

    def isWaitPigTable(self, userId, room, tableId):
        '''
        检查是否是杀猪状态的桌子, 缺省为非杀猪状态的桌子
        '''
        if _DEBUG:
            debug('isWaitPigTable->', userId, room, tableId)
        return 0


TGXueZhan = _TGXueZhan()
