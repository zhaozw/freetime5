# -*- coding=utf-8 -*-
"""
Created on 2018年02月02日10:43:20
@author: yzx
"""
from freetime5.util import ftlog
from tuyoo5.core import tygame

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class _SNSGame(tygame.TYGame):

    def __init__(self):
        super(_SNSGame, self).__init__()
        # self._eventBus = tygame.TYEventBus()

    def initGame(self):
        ftlog.info('SNSGameSrv.initGame IN')
        super(_SNSGame, self).initGame()
        ftlog.info('SNSGameSrv.initGame OUT')


SNSGame = _SNSGame()
