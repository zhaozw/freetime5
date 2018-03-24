# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh

对应GH进程, 基本上为 http api 入口
'''

from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import typlugin, tyglobal


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class MatchPluginSrvHttp(typlugin.TYPlugin):

    def __init__(self):
        super(MatchPluginSrvHttp, self).__init__()
        ftlog.info('MatchPluginSrvHttp init')

    def destoryPlugin(self):
        super(MatchPluginSrvHttp, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_HTTP])
    def initPluginBefore(self):
        pass

    @typlugin.markPluginEntry(httppath='cmatch/signin')
    def doSignin(self, request):
        userId = request.getParamStr('userId')
        gameId = request.getParamStr('gameId')
        roomId0 = request.getParamStr('roomId0')
        fee = request.getParamStr('fee')
        ftlog.info('httpmatch_test.doSignin userId=', userId,gameId,roomId0)
        msg = MsgPack()
        msg.setCmd('match')
        msg.setAction('signin')
        msg.setParam('userId', userId)
        msg.setParam('gameId', gameId)
        msg.setParam('roomId', roomId0)
        msg.setParam('fee', fee)
        signinParams = {}
        msg.setParam('signinParams', signinParams)
        roomIns = tyglobal.rooms()[roomId0]
        roomIns._do_match__signin(msg)

        # router.sendRoomServer(msg, roomId0)
        return 'sign in ok'

    @typlugin.markPluginEntry(httppath='/gtest/cmatch/robotcallmatch')
    def doTestRobotCallMatch(self, gameId, roomId0, fee, count, start):
        ftlog.info('httpmatch_test.doTestRobotCallMatch start roomId=', roomId0,'count=', gameId, 'count=', count,
                   'start=', start)
        mo = MsgPack()
        mo.setCmd('match')
        mo.setParam('action', 'signin')
        mo.setParam('gameId', gameId)
        mo.setParam('roomId', roomId0)
        mo.setParam('fee', fee)
        signinParams = {}
        mo.setParam('signinParams', signinParams)

        for i in xrange(count):
            userId = start+i
            mo.setParam('userId', userId)
            # router.sendRoomServer(mo, roomId0)
        return 'sign in ok'


    @typlugin.markPluginEntry(httppath='/gtest/cmatch/signout')
    def doSignOut(self, userId, gameId, roomId0):
        ftlog.info('httpmatch_test.doSignout userId=', userId)
        msg = MsgPack()
        msg.setCmd('match')
        msg.setAction('signout')
        msg.setParam('userId', userId)
        msg.setParam('roomId', roomId0)
        msg.setParam('gameId', gameId)
        # router.sendRoomServer(msg, roomId0)
        return 'sign out ok'

    @typlugin.markPluginEntry(httppath='/gtest/cmatch/matchdesc')
    def doMatchDes(self, userId, gameId, roomId0):
        ftlog.info('httpmatch_test.doMatchDes userId=', userId)
        msg = MsgPack()
        msg.setCmd('match')
        msg.setAction('desc')
        msg.setParam('userId', userId)
        msg.setParam('gameId', gameId)
        msg.setParam('roomId', roomId0)

        # router.sendRoomServer(msg, roomId0)
        return 'matchDesc ok'

    @typlugin.markPluginEntry(httppath='/gtest/cmatch/matchupdate')
    def doMatchUpdate(self, userId, gameId, roomId0):
        ftlog.info('httpmatch_test.doMatchUpdate userId=', userId)
        msg = MsgPack()
        msg.setCmd('match')
        msg.setAction('update')
        msg.setParam('userId', userId)
        msg.setParam('gameId', gameId)
        msg.setParam('roomId', roomId0)

        # router.sendRoomServer(msg, roomId0)
        return 'matchUpdate ok'

    @typlugin.markPluginEntry(httppath='/gtest/cmatch/matchquick')
    def doMatchQuick(self, userId, gameId, roomId0, tableId0, matchId):
        ftlog.info('httpmatch_test.doMatchQuick userId=', userId,gameId,roomId0,tableId0,matchId)
        msg = MsgPack()
        """
        和客户端发送的协议略有差异，客户端cmd=quick_start由router补齐成room#quick_start
        """
        msg.setCmd('room')
        msg.setParam('action', 'quick_start')
        msg.setParam('userId', userId)
        msg.setParam('gameId', gameId)
        msg.setParam('roomId', roomId0)
        msg.setParam('tableId', tableId0)
        msg.setParam('clientId', "Android_5.1100_tyGuest,tyAccount,wechat.wechat,alipay,unionpay.0-hall9999.tuyoo.tu")

        # router.sendRoomServer(msg, matchId)
        return 'matchQuick ok'

    @typlugin.markPluginEntry(httppath='/gtest/cmatch/matchkill')
    def doMatchKill(self, userId, gameId, roomId0):
        """
        测试退出比赛信息.
        """
        ftlog.info('httpmatch_test.doMatchKill userId=', userId,
                   'roomId=', roomId0,
                   'gameId=', gameId)
        msg = MsgPack()
        msg.setCmd('match')
        msg.setParam('action', 'giveup')
        msg.setParam('gameId', gameId)
        msg.setParam('userId', userId)
        msg.setParam('roomId', roomId0)
        # router.sendRoomServer(msg, roomId0)
        return "kill ok"

    @typlugin.markPluginEntry(httppath='/gtest/cmatch/matchlist')
    def doMatchList(self, userId, gameId, rooms):
        """
        测试更新比赛信息.
        """
        ftlog.info('httpmatch_test.doMatchList userId=', userId,
                   'gameId=', gameId,
                   'roomList=', rooms)
        msg = MsgPack()
        msg.setCmd('game')
        msg.setParam('action', 'match_room_list')
        msg.setParam('gameId', gameId)
        msg.setParam('userId', userId)
        roomList = [int(x) for x in rooms.split("-")]
        msg.setParam('roomList', roomList)
        # router.sendUtilServer(msg, userId)
        return "do doMatchList ok"