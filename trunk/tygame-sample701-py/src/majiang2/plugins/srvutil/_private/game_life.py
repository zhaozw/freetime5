# -*- coding=utf-8 -*-
'''
Created on 2015年9月28日

@author: liaoxx
'''


from freetime5.twisted.ftlock import lockargname
from freetime5.util import fttime, ftlog
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tyrpcconn, tyglobal
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tybireport


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


@lockargname('game.life', 'userId')
def doGameEnter(userId, clientId):
    if _DEBUG:
        debug('doGameEnter->', userId, clientId)
    gameId = tyglobal.gameId()
    isNewUser = pluginCross.mj2dao.createGameData(userId,
                                                   clientId,
                                                   gameId)
    # 确认是否是今日第一次登录
    isdayfirst = False
    datas = pluginCross.mj2weakdata.getDay1stDatas(userId)
    if 'daylogin' not in datas:
        isdayfirst = True
        datas['daylogin'] = 1
        datas['iscreate'] = 1
    else:
        datas['daylogin'] += 1
        datas['iscreate'] = 0
    pluginCross.mj2weakdata.setDay1stDatas(userId, datas)

    # 游戏登录次数加1，每次bind_user都会加1，包括断线重连
    loginsum = pluginCross.mj2dao.loginGame(userId,
                                             gameId,
                                             clientId,
                                             isNewUser,
                                             isdayfirst)
    if _DEBUG:
        debug('doGameEnter->userId=', userId, 'isNewUser=', isNewUser,
              'loginsum=', loginsum, 'isdayfirst=', isdayfirst)

    gdata = pluginCross.mj2dao.getGameInfo(userId,
                                            clientId,
                                            tyglobal.gameId())
    mo = MsgPack()
    mo.setCmd('game_data')
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('gdata', gdata)
    tyrpcconn.sendToUser(userId, mo)

    # BI日志统计
    tybireport.userGameEnter(tyglobal.gameId(), userId, clientId)
    tybireport.reportGameEvent('BIND_GAME',
                               userId,
                               gameId,
                               0,
                               0,
                               0,
                               0,
                               0,
                               0,
                               [],
                               clientId,
                               isNewUser)
    # evt = OnLineGameChangedEvent(userId, gameId, 1, clientId)
    # TGHall.getEventBus().publishEvent(evt)


@lockargname('game.life', 'userId')
def doGameLeave(userId, clientId):
    if _DEBUG:
        debug('doGameLeave->', userId, clientId)
    mo = MsgPack()
    mo.setCmd('game')
    mo.setResult('action', 'leave')
    mo.setResult('gameId', tyglobal.gameId())
    mo.setResult('userId', userId)
    mo.setResult('ok', 1)
    tyrpcconn.sendToUser(userId, mo)
    # evt = OnLineGameChangedEvent(userId, gameId, 0, clientId)
    # TGHall.getEventBus().publishEvent(evt)


def doGameTimestemp(userId):
    if _DEBUG:
        debug('doGameTimestemp->', userId)
    mo = MsgPack()
    mo.setCmd('user')
    mo.setResult('action', 'mj_timestamp')
    mo.setResult('gameId', tyglobal.gameId())
    mo.setResult('userId', userId)
    mo.setResult('current_ts', fttime.getCurrentTimestamp())
    tyrpcconn.sendToUser(userId, mo)
