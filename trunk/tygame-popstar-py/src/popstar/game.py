# -*- coding=utf-8 -*-
'''
Created on 2018年1月3日

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


class _PopStar(tygame.TYGame):

    def __init__(self):
        super(_PopStar, self).__init__()
        # self._eventBus = tygame.TYEventBus()

    def initGame(self):
        ftlog.info('_SingleGameSrv.initGame IN')
        super(_PopStar, self).initGame()
        ftlog.info('_SingleGameSrv.initGame OUT')

PopStar = _PopStar()
