# -*- coding=utf-8 -*-
'''
Created on 2018年1月31日

@author: lixi
'''
from quickmaze.plugins.srvroom.normal_room import TYNormalRoom
from quickmaze.plugins.srvtable.table import TYTable
from freetime5.util import ftlog
from tuyoo5.core import tygame, tyglobal
from quickmaze.plugins.srvroom import tyRoomConst


_DEBUG = 1


if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class _CrossElimination(tygame.TYGame):

    def __init__(self):
        super(_CrossElimination, self).__init__()
        # self._eventBus = tygame.TYEventBus()

    def initGame(self):
        ftlog.info('_CrossElimination.initGame IN')
        super(_CrossElimination, self).initGame()
        ftlog.info('_CrossElimination.initGame OUT')


    def initGameBefore(self):
        ftlog.info('_CrossElimination.initGameBefore IN')
        super(_CrossElimination, self).initGameBefore()
        srvType = tyglobal.serverType()

        if srvType in (tyglobal.SRV_TYPE_GAME_ROOM, tyglobal.SRV_TYPE_GAME_TABLE):
            pass
        ftlog.info('_CrossElimination.initGameBefore OUT')

    def initGame(self):
        ftlog.info('_CrossElimination.initGame IN')
        super(_CrossElimination, self).initGame()
        srvType = tyglobal.serverType()
        if srvType in (tyglobal.SRV_TYPE_HALL_SINGLETON, tyglobal.SRV_TYPE_HALL_UTIL):
            '''
            当进程为UTIL和SINGLETON时，初始化以下模块
            '''
            pass

        ftlog.info('_CrossElimination.initGame OUT')

    def initGameAfter(self):
        ftlog.info('_CrossElimination.initGameAfter IN')
        super(_CrossElimination, self).initGameAfter()
        ftlog.info('_CrossElimination.initGameAfter OUT')

    def getRoomInstance(self, roomdefine):
        '''
        工场设计模式，根据不同的房间配置信息创建不同类型的room对象实例
        子类可更具更新的实际要求，覆盖此方法
        必须返回 TYRoom 子类实例
        '''
        if _DEBUG:
            debug('_CrossElimination.getRoomInstance->', roomdefine)
        room = TYNormalRoom(roomdefine)
        return room

    def getTableInstance(self, room, tableId):
        '''
        工场设计模式，根据不同的房间配置信息创建不同类型的table对象实例
        子类可更具更新的实际要求，覆盖此方法
        必须返回 TYTable 子类实例
        '''
        if _DEBUG:
            debug('_CrossElimination.getTableInstance->', tableId, room.roomConf)

        table = TYTable(tableId, room)
        return table

CrossElimination = _CrossElimination()
