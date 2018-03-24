# -*- coding=utf-8 -*-
'''
Created on 2015年5月7日

@author: zqh
'''
from freetime5.util import ftlog
from tuyoo5.core import tygame, tyglobal


class _TGHall(tygame.TYGame):

    def initGame(self):
        ftlog.info('TGHall.initGame IN')

        srvType = tyglobal.serverType()
        if srvType in (tyglobal.SRV_TYPE_HALL_SINGLETON, tyglobal.SRV_TYPE_HALL_UTIL):
            '''
            当进程为UTIL和SINGLETON时，初始化以下模块
            '''
            pass

        ftlog.info('TGHall.initGame OUT')


TGHall = _TGHall()
