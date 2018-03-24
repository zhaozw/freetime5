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


class _ChatGame(tygame.TYGame):

    def __init__(self):
        super(_ChatGame, self).__init__()

    def initGame(self):
        ftlog.info('ChatGameSrv.initGame IN')
        super(_ChatGame, self).initGame()
        ftlog.info('ChatGameSrv.initGame OUT')


ChatGame = _ChatGame()
