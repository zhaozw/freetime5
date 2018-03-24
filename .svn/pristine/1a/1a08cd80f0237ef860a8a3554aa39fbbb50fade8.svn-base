# -*- coding: utf-8 -*-
'''
Created on 2018年1月31日

@author: lx
'''

from freetime5.twisted import ftcore
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import typlugin, tyglobal, tychecker, tyrpcconn
from boxxo.plugins.srvutil._private import _srvutil_handler

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

def check_matchId(msg, result, name):
    matchId = msg.getParamInt(name, -1)
    if matchId <= 0:
        return None, 'the param %s is error' % (name)
    return matchId, None

class CrossEliminationSrvUtil(typlugin.TYPlugin):

    def __init__(self):
        typlugin.TYPlugin.__init__(self)
        self.basechecker = tychecker.Checkers(
            tychecker.check_userId,
            tychecker.check_gameId,
            tychecker.check_clientId,
        )
        self.checkSaveMatchInfo = self.basechecker.clone()
        self.checkSaveMatchInfo.addCheckFun(check_matchId)



    def destoryPlugin(self):
        pass
        # if self._playerMatcher:
        #     self._playerMatcher.cancel()
        #     self._playerMatcher = None

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginBefore(self):
        pass
        # self._playerMatcher = ftcore.runLoopSync(0.5, _srvutil_handler.doMatchVSPlayers)


    @typlugin.markPluginEntry(cmd='bind_game', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doBindGame(self, msg):
        '''
        未指定房间的 快速开始
        '''
        if _DEBUG:
            debug('doBindGame->', msg)
        mi = self.basechecker.check(msg)
        if mi.error:
            ftlog.error('doBindGame the msg params error !', mi.error)
        else:
            mo = MsgPack()
            mo.setCmd('bind_game')
            mo.setResult('gameId', mi.gameId)
            mo.setResult('userId', mi.userId)
            mo.setResult('result', 'ok')
            tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    # @typlugin.markPluginEntry(cmd='join_queue', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    # def doQuickStart(self, msg):
    #     '''
    #     未指定房间的 快速开始
    #     '''
    #     if _DEBUG:
    #         debug('doQuickStart->', msg)
    #     mi = self.basechecker.check(msg)
    #     if mi.error:
    #         ftlog.error('doQuickStart the msg params error !', mi.error)
    #     else:
    #         if mi.userId in _srvutil_handler.player_queue:
    #             mo = MsgPack()
    #             mo.setCmd('join_queue')
    #             mo.setResult('gameId', mi.gameId)
    #             mo.setResult('userId', mi.userId)
    #             mo.setResult('result', 'already in queue')
    #             tyrpcconn.sendToUser(mi.userId, mo)
    #         else:
    #             _srvutil_handler.player_queue.append(mi.userId)
    #             mo = MsgPack()
    #             mo.setCmd('join_queue')
    #             mo.setResult('gameId', mi.gameId)
    #             mo.setResult('userId', mi.userId)
    #             mo.setResult('result', 'ok')
    #             tyrpcconn.sendToUser(mi.userId, mo)
    #     return 1


    @typlugin.markPluginEntry(cmd='game_ready', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doGameReady(self, msg):
        if _DEBUG:
            debug('doGameReady->', msg)
        mi = self.checkSaveMatchInfo.check(msg)
        if mi.error:
            ftlog.error('doGameReady the msg params error !', mi.error)
        else:
            _srvutil_handler.updateUtilMatchStatus(mi.matchId, mi.userId)
        return 1


    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def doMatchCasualGamePlayers(self, userId_A, userId_B):
        if _DEBUG:
            debug("In doMatchCasualGamePlayers @@@@@  userid_A = ", userId_A, "  userId_B = ", userId_B)
            _srvutil_handler.saveUtilMatchInfo(userId_A, userId_B)
        return 1

