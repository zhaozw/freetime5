# -*- coding=utf-8 -*-
'''
Created on 2018年1月31日

@author: lixi
'''

from freetime5.util import ftlog
from tuyoo5.core import tygame, tyglobal



_DEBUG = 1


if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class _CasualMatch(tygame.TYGame):

    def __init__(self):
        super(_CasualMatch, self).__init__()
        # self._eventBus = tygame.TYEventBus()

    def initGame(self):
        ftlog.info('_CasualMatch.initGame IN')
        super(_CasualMatch, self).initGame()
        ftlog.info('_CrossElimination.initGame OUT')


    def initGameBefore(self):
        ftlog.info('_CasualMatch.initGameBefore IN')
        super(_CasualMatch, self).initGameBefore()
        srvType = tyglobal.serverType()

        if srvType in (tyglobal.SRV_TYPE_GAME_ROOM, tyglobal.SRV_TYPE_GAME_TABLE):
            pass
        ftlog.info('_CasualMatch.initGameBefore OUT')

    def initGame(self):
        ftlog.info('_CrossElimination.initGame IN')
        super(_CasualMatch, self).initGame()
        srvType = tyglobal.serverType()
        if srvType in (tyglobal.SRV_TYPE_HALL_SINGLETON, tyglobal.SRV_TYPE_HALL_UTIL):
            '''
            当进程为UTIL和SINGLETON时，初始化以下模块
            '''
            pass

        ftlog.info('_CrossElimination.initGame OUT')

    def initGameAfter(self):
        ftlog.info('_CrossElimination.initGameAfter IN')
        super(_CasualMatch, self).initGameAfter()
        ftlog.info('_CrossElimination.initGameAfter OUT')


CasualMatch = _CasualMatch()
