# -*- coding: utf-8 -*-
'''
Created on 2016年8月1日

@author: zqh
'''
from freetime5.util import ftlog, fttime
from freetime5.util.ftmsg import MsgPack
from hall5.plugins.hallui._private import _hallgamelist
from tuyoo5.core import tyrpcconn
from tuyoo5.core.tyconst import HALL_GAMEID


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


def sendHallUiGameList(userId, intClientId, apiVersion):
    nowdate = fttime.formatTimeSecond()
    mo = MsgPack()
    mo.setCmd('hall_ui5')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('gameId', HALL_GAMEID)
    mo.setResult('intClientId', intClientId)
    mo.setResult('userId', userId)
    mo.setResult('gamelist', _hallgamelist.getUiInfo(userId, intClientId, nowdate))
    tyrpcconn.sendToUser(userId, mo)
