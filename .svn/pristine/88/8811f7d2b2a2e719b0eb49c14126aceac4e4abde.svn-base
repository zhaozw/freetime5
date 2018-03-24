# -*- coding: utf-8 -*-
'''
Created on 2018年2月6日

@author: lx
'''
from freetime5._tyserver._plugins._rpc2 import getRpcProxy, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE
from freetime5.twisted import ftcore
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import typlugin, tyglobal, tychecker, tyrpcconn
from casualmatch.plugins.srvutil._private._matchqueue import DaoCasualGameMatch
from casualmatch.plugins.srvutil._private import _rpc_user_info
from casualmatch.plugins.srvutil._private import _srvutil_handler
from casualmatch.plugins.srvutil._private import _matchqueue

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

def check_friendId(msg, result, name):
    friendId = msg.getParamInt(name, -1)
    if friendId <= 0:
        return None, 'the param %s is error' % (name)
    return friendId, None

def check_joinGameId(msg, result, name):
    joinGameId = msg.getParamInt(name, -1)
    if joinGameId <= 0:
        return None, 'the param %s is error' % (name)
    return joinGameId, None

def check_demandSex(msg, result, name):
    demandSex = msg.getParamInt(name, -1)
    if demandSex <= 0:
        return None, 'the param %s is error' % (name)
    return demandSex, None

def check_MsgId(msg, result, name):
    MsgId = msg.getParamStr(name, '')
    if MsgId:
        return MsgId, None
    return None, 'the param %s error' % (name)

class CasualMatchSrvUtil(typlugin.TYPlugin):

    def __init__(self):
        typlugin.TYPlugin.__init__(self)
        self.basechecker = tychecker.Checkers(
            tychecker.check_userId,
            tychecker.check_gameId,
            tychecker.check_clientId,
        )
        self.checkFriedMatch = self.basechecker.clone()
        self.checkFriedMatch.addCheckFun(check_friendId)
        self.checkFriedMatch.addCheckFun(check_joinGameId)
        self.checkFriedMatch.addCheckFun(check_MsgId)
        self.checkGameMatch = self.basechecker.clone()
        self.checkGameMatch.addCheckFun(check_joinGameId)
        # self.checkBigGameMatch = self.basechecker.clone()
        # self.checkBigGameMatch.addCheckFun(check_demandSex)

    def destoryPlugin(self):
        if self._playerMatcher:
            self._playerMatcher.cancel()
            self._playerMatcher = None
        _matchqueue.DaoCasualGameMatch.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginBefore(self):
        _matchqueue.DaoCasualGameMatch.initialize()
        self._playerMatcher = ftcore.runLoopSync(0.5, _srvutil_handler.doMatchLoopVS)

    @typlugin.markPluginEntry(cmd='join_match_queue', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doJoinMatchGameQueue(self, msg):
        '''
        制定游戏加入匹配队列
        '''
        if _DEBUG:
            debug('join_match_queue->', msg)
        mi = self.checkGameMatch.check(msg)
        if mi.error:
            ftlog.error('join_match_queue the msg params error !', mi.error)
            mo = MsgPack()
            mo.setCmd('join_match_queue')
            mo.setResult('gameId', mi.joinGameId)
            mo.setResult('userId', mi.userId)
            mo.setResult('result', 'msg params error')
            tyrpcconn.sendToUser(mi.userId, mo)
        else:
            sex = _rpc_user_info.getUserSexInfo(mi.userId)
            if sex == 1:
                result = DaoCasualGameMatch.joinMatchGameQueueMale(mi.userId, mi.joinGameId)
            else:
                result = DaoCasualGameMatch.joinMatchGameQueueFemale(mi.userId, mi.joinGameId)
            if result == 0:
                mo = MsgPack()
                mo.setCmd('join_match_queue')
                mo.setResult('gameId', mi.joinGameId)
                mo.setResult('userId', mi.userId)
                mo.setResult('result', 'already in queue')
                tyrpcconn.sendToUser(mi.userId, mo)
            else:
                mo = MsgPack()
                mo.setCmd('join_match_queue')
                mo.setResult('gameId', mi.joinGameId)
                mo.setResult('userId', mi.userId)
                mo.setResult('result', 'ok')
                tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd='quit_match_queue', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doQuitMatchGameQueue(self, msg):
        '''
        制定游戏退出匹配队列
        '''
        if _DEBUG:
            debug('quit_match_queue->', msg)
        mi = self.checkGameMatch.check(msg)
        if mi.error:
            ftlog.error('quit_match_queue the msg params error !', mi.error)
            mo = MsgPack()
            mo.setCmd('quit_match_queue')
            mo.setResult('gameId', mi.joinGameId)
            mo.setResult('userId', mi.userId)
            mo.setResult('result', 'msg params error')
            tyrpcconn.sendToUser(mi.userId, mo)
        else:
            sex = _rpc_user_info.getUserSexInfo(mi.userId)
            if sex == 1:
                result = DaoCasualGameMatch.quitMatchGameQueueMale(mi.userId, mi.joinGameId)
            else:
                result = DaoCasualGameMatch.quitMatchGameQueueFemale(mi.userId, mi.joinGameId)
            if result == 0:
                mo = MsgPack()
                mo.setCmd('quit_match_queue')
                mo.setResult('gameId', mi.joinGameId)
                mo.setResult('userId', mi.userId)
                mo.setResult('result', 'already quit queue')
                tyrpcconn.sendToUser(mi.userId, mo)
            else:
                mo = MsgPack()
                mo.setCmd('quit_match_queue')
                mo.setResult('gameId', mi.joinGameId)
                mo.setResult('userId', mi.userId)
                mo.setResult('result', 'ok')
                tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd='join_big_queue', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doJoinBigMatchQueue(self, msg):
        '''
        制定游戏加入匹配队列
        '''
        if _DEBUG:
            debug('doJoinBigMatchQueue->', msg)
        mi = self.basechecker.check(msg)
        if mi.error:
            ftlog.error('doJoinBigMatchQueue the msg params error !', mi.error)
            mo = MsgPack()
            mo.setCmd('join_big_queue')
            mo.setResult('userId', mi.userId)
            mo.setResult('result', 'msg params error')
            tyrpcconn.sendToUser(mi.userId, mo)
        else:
            sex = _rpc_user_info.getUserSexInfo(mi.userId)

            rpcproxy = getRpcProxy(9992, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
            rfc = rpcproxy.srvhttp.doGetUserBigGameDemandInfo(mi.userId)

            demandSex = "rand"
            if not rfc.getResult() is None:
                demandSex = rfc.getResult()

            if _DEBUG:
                debug('doJoinBigMatchQueue->   demandSex =', demandSex)

            if sex == 1:
                result = DaoCasualGameMatch.joinBigMatchQueueMaleHash(mi.userId, demandSex[0])
            else:
                result = DaoCasualGameMatch.joinBigMatchQueueFemaleHash(mi.userId, demandSex[0])
            if result == 1024:
                mo = MsgPack()
                mo.setCmd('join_big_queue')
                mo.setResult('userId', mi.userId)
                mo.setResult('result', 'already in queue')
                tyrpcconn.sendToUser(mi.userId, mo)
            elif result == 1:
                mo = MsgPack()
                mo.setCmd('join_big_queue')
                mo.setResult('userId', mi.userId)
                mo.setResult('result', 'ok')
                tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    # @typlugin.markPluginEntry(cmd='join_big_queue', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    # def doJoinBigMatchQueue(self, msg):
    #     '''
    #     制定游戏加入匹配队列
    #     '''
    #     if _DEBUG:
    #         debug('doJoinBigMatchQueue->', msg)
    #     mi = self.basechecker.check(msg)
    #     if mi.error:
    #         ftlog.error('doJoinBigMatchQueue the msg params error !', mi.error)
    #         mo = MsgPack()
    #         mo.setCmd('join_big_queue')
    #         mo.setResult('userId', mi.userId)
    #         mo.setResult('result', 'msg params error')
    #         tyrpcconn.sendToUser(mi.userId, mo)
    #     else:
    #         sex = _rpc_user_info.getUserSexInfo(mi.userId)
    #         if sex == 1:
    #             result = DaoCasualGameMatch.joinBigMatchQueueMale(mi.userId)
    #         else:
    #             result = DaoCasualGameMatch.joinBigMatchQueueFemale(mi.userId)
    #         if result == 0:
    #             mo = MsgPack()
    #             mo.setCmd('join_big_queue')
    #             mo.setResult('userId', mi.userId)
    #             mo.setResult('result', 'already in queue')
    #             tyrpcconn.sendToUser(mi.userId, mo)
    #         else:
    #             mo = MsgPack()
    #             mo.setCmd('join_big_queue')
    #             mo.setResult('userId', mi.userId)
    #             mo.setResult('result', 'ok')
    #             tyrpcconn.sendToUser(mi.userId, mo)
    #     return 1

    @typlugin.markPluginEntry(cmd='quit_big_queue', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doQuitBigMatchQueue(self, msg):
        '''
        退出制定游戏匹配队列
        '''
        if _DEBUG:
            debug('doQuitBigMatchQueue->', msg)
        mi = self.basechecker.check(msg)
        if mi.error:
            ftlog.error('doQuitBigMatchQueue the msg params error !', mi.error)
            mo = MsgPack()
            mo.setCmd('quit_big_queue')
            mo.setResult('userId', mi.userId)
            mo.setResult('result', 'msg params error')
            tyrpcconn.sendToUser(mi.userId, mo)
        else:
            sex = _rpc_user_info.getUserSexInfo(mi.userId)
            if sex == 1:
                result = DaoCasualGameMatch.quitBigMatchQueueMale(mi.userId)
            else:
                result = DaoCasualGameMatch.quitBigMatchQueueFemale(mi.userId)
            if result == 0:
                mo = MsgPack()
                mo.setCmd('quit_big_queue')
                mo.setResult('userId', mi.userId)
                mo.setResult('result', 'already quit queue')
                tyrpcconn.sendToUser(mi.userId, mo)
            else:
                mo = MsgPack()
                mo.setCmd('quit_big_queue')
                mo.setResult('userId', mi.userId)
                mo.setResult('result', 'ok')
                tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd='big_match_ready', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doBigMatchReady(self, msg):
        '''
        制定游戏加入匹配队列
        '''
        if _DEBUG:
            debug('doBigMatchReady->', msg)
        mi = self.checkFriedMatch.check(msg)
        if mi.error:
            ftlog.error('doBigMatchReady the msg params error !', mi.error)
            mo = MsgPack()
            mo.setCmd('big_match_ready')
            mo.setResult('gameId', mi.joinGameId)
            mo.setResult('userId', mi.userId)
            mo.setResult('result', 'msg params error')
            tyrpcconn.sendToUser(mi.userId, mo)
        else:
            _srvutil_handler.doFriendMatch(mi.userId, mi.friendId, mi.gameId)
            #返回给A的还有对战要求的回复消息
            mo = MsgPack()
            mo.setCmd('big_match_ready')
            mo.setResult('gameId', mi.gameId)
            mo.setResult('userId', mi.userId)
            mo.setResult('friendId', mi.friendId)
            mo.setResult('result', 'big_match_ready ok')
            tyrpcconn.sendToUser(mi.userId, mo)
            #发送给B的好友对战邀请的回复消息
            mo = MsgPack()
            mo.setCmd('big_match_ready')
            mo.setResult('gameId', mi.gameId)
            mo.setResult('userId', mi.friendId)
            mo.setResult('friendId', mi.userId)
            mo.setResult('result', 'big_match_ready ok')
            tyrpcconn.sendToUser(mi.friendId, mo)


    @typlugin.markPluginEntry(cmd='friend_match', srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def doFriendMatchGameQueue(self, msg):
        '''
        好友匹配
        '''
        if _DEBUG:
            debug('friend_match->', msg)
        mi = self.checkFriedMatch.check(msg)
        if mi.error:
            ftlog.error('friend_match the msg params error !', mi.error)
            mo = MsgPack()
            mo.setCmd('friend_match')
            mo.setResult('gameId', mi.gameId)
            mo.setResult('userId', mi.userId)
            mo.setResult('MsgId', mi.MsgId)
            mo.setResult('result', 'msg params error')
            tyrpcconn.sendToUser(mi.userId, mo)
        else:
            if _DEBUG:
                debug("IN doJoinMatchGameQueue userId = ", mi.userId, " friendId = ", mi.friendId,
                      " mi.joinGameId = ", mi.joinGameId)
            #流程A发出邀请,B接受邀请后,A发送friend_match消息给服务器的匹配模块,服务器的匹配模块接受到消息后,走正常的匹配成功后的流程,同时发送好友匹配成功的消息给客户端
            _srvutil_handler.doFriendMatch(mi.userId, mi.friendId, mi.joinGameId)
            #返回给A的还有对战要求的回复消息
            mo = MsgPack()
            mo.setCmd('friend_match')
            mo.setResult('gameId', mi.gameId)
            mo.setResult('userId', mi.userId)
            mo.setResult('friendId', mi.friendId)
            mo.setResult('joinGameId', mi.joinGameId)
            mo.setResult('MsgId', mi.MsgId)
            mo.setResult('result', 'friend_match ok')
            tyrpcconn.sendToUser(mi.userId, mo)
            #发送给B的好友对战邀请的回复消息
            mo = MsgPack()
            mo.setCmd('friend_match')
            mo.setResult('gameId', mi.gameId)
            mo.setResult('userId', mi.friendId)
            mo.setResult('joinGameId', mi.joinGameId)
            mo.setResult('friendId', mi.userId)
            mo.setResult('MsgId', mi.MsgId)
            mo.setResult('result', 'friend_match ok')
            tyrpcconn.sendToUser(mi.friendId, mo)
