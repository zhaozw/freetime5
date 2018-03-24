# coding=UTF-8
'''房间基类Mixin
'''
from freetime5.util.ftmark import noException
from freetime5.util.ftmsg import MsgPack
from majiang2.poker2.entity import hallrpcutil
from majiang2.poker2.entity.game.rooms import tyRoomConst
from tuyoo5.core import tyconfig
from tuyoo5.core import tyrpcconn
from tuyoo5.core.typlugin import gameRpcRoomOne
from tuyoo5.game import tybireport
from tuyoo5.game import tysessiondata


__author__ = [
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]


class TYRoomMixin(object):
    '''房间Mixin基类
    '''

    @classmethod
    def sendRoomQuickStartReq(cls, msg, roomId, tableId, **kwargs):
        msg.setCmd("room")
        msg.setParam("action", "quick_start")
        msg.setParam("roomId", roomId)
        msg.setParam("tableId", tableId)
        for key in kwargs:
            msg.setParam(key, kwargs[key])
        gameRpcRoomOne.srvroom.doQuickStart(roomId, msg.getDict(), 0)
        return 1

    @classmethod
    def queryRoomQuickStartReq(cls, msg, roomId, tableId, **kwargs):
        msg.setCmd("room")
        msg.setParam("action", "quick_start")
        msg.setParam("roomId", roomId)
        msg.setParam("tableId", tableId)
        for key in kwargs:
            msg.setParam(key, kwargs[key])
        rfc = gameRpcRoomOne.srvroom.doQuickStart(roomId, msg.getDict(), 1)
        return rfc.getResult()

    @classmethod
    def queryRoomGetPlayingTableListReq(cls, shadowRoomId, **kwargs):
        msg = MsgPack()
        msg.setCmd("room")
        msg.setParam("action", "playingTableList")
        msg.setParam("roomId", shadowRoomId)
        for key in kwargs:
            msg.setParam(key, kwargs[key])
        rfc = gameRpcRoomOne.srvtable.getPlayingTableList(shadowRoomId, msg.getDict())
        return rfc.getResult()

    @classmethod
    def makeSitReq(cls, userId, shadowRoomId, tableId, clientId):
        mpSitReq = MsgPack()
        mpSitReq.setCmd("table")
        mpSitReq.setParam("action", "sit")
        mpSitReq.setParam("userId", userId)
        mpSitReq.setParam("roomId", shadowRoomId)
        mpSitReq.setParam("tableId", tableId)
        mpSitReq.setParam("clientId", clientId)
        mpSitReq.setParam("gameId", tyconfig.getRoomGameId(shadowRoomId))
        return mpSitReq

    @classmethod
    def sendSitReq(cls, userId, shadowRoomId, tableId, clientId, extParams=None):
        mpSitReq = cls.makeSitReq(userId, shadowRoomId, tableId, clientId)
        if extParams:
            moParams = mpSitReq.getKey('params')
            for k, v in extParams.items():
                if not k in moParams:
                    moParams[k] = v
        gameRpcRoomOne.srvtable.doSitDown(shadowRoomId, mpSitReq.getDict(), 0)
        return 1

    @classmethod
    def querySitReq(cls, userId, shadowRoomId, tableId, clientId, extParams=None):
        mpSitReq = cls.makeSitReq(userId, shadowRoomId, tableId, clientId)
        if extParams:
            moParams = mpSitReq.getKey('params')
            for k, v in extParams.items():
                if not k in moParams:
                    moParams[k] = v
        rfc = gameRpcRoomOne.srvtable.doSitDown(shadowRoomId, mpSitReq.getDict(), 1)
        return rfc.getResult()

    @classmethod
    def sendTableCallObserveReq(cls, userId, shadowRoomId, tableId, clientId):
        mpReq = MsgPack()
        mpReq.setCmd("table_call")
        mpReq.setParam("action", "observe")
        mpReq.setParam("userId", userId)
        mpReq.setParam("roomId", shadowRoomId)
        mpReq.setParam("tableId", tableId)
        mpReq.setParam("clientId", clientId)
        gameRpcRoomOne.srvtable.doTableCallObserve(shadowRoomId, mpReq.getDict(), 0)

    @classmethod
    def makeTableManageReq(cls, userId, shadowRoomId, tableId, clientId, action, params=None):
        mpReq = MsgPack()
        mpReq.setCmd("table_manage")
        mpReq.setParam("action", action)
        mpReq.setParam("userId", userId)
        mpReq.setParam("gameId", tyconfig.getRoomGameId(shadowRoomId))
        mpReq.setParam("roomId", shadowRoomId)
        mpReq.setParam("tableId", tableId)
        mpReq.setParam("clientId", clientId)
        if params:
            mpReq.updateParam(params)
        return mpReq

    @classmethod
    def queryTableManageSitReq(cls, userId, shadowRoomId, tableId, clientId):
        mpReq = cls.makeTableManageReq(userId, shadowRoomId, tableId, clientId, 'sit')
        rfc = gameRpcRoomOne.srvtable.doTableManageSit(shadowRoomId, mpReq.getDict(), 1)
        return rfc.getResult()

    @classmethod
    def queryTableManageTableStandupReq(cls, userId, shadowRoomId, tableId, seatId, clientId, reason):
        mpReq = cls.makeTableManageReq(userId, shadowRoomId, tableId, clientId, 'standup', {
            'seatId': seatId, 'reason': reason})
        rfc = gameRpcRoomOne.srvtable.doTableManageStandup(shadowRoomId, mpReq.getDict(), 1)
        return rfc.getResult()

    @classmethod
    def queryTableManageTableLeaveReq(cls, userId, shadowRoomId, tableId, clientId, params=None):
        mpReq = cls.makeTableManageReq(userId, shadowRoomId, tableId, clientId, 'leave', params)
        rfc = gameRpcRoomOne.srvtable.doTableManageLeave(shadowRoomId, mpReq.getDict(), 1)
        return rfc.getResult()

    def sendTableManageGameStartReq(self, shadowRoomId, tableId, userIds, recyclePlayersN=0, params=None):
        '''recyclePlayersN表示需要从牌桌回收到队列的人数
        '''
        mpReq = self.makeTableManageReq(0, shadowRoomId, tableId, None, 'game_start',
                                        {'recyclePlayersN': recyclePlayersN})
        mpReq.setParam("userIds", userIds)
        if self.roomConf['typeName'] == tyRoomConst.ROOM_TYPE_NAME_MTT and self.state == self.MTT_STATE_FINALS:
            mpReq.setParam("isFinalTable", True)
        if params:
            mpReq.updateParam(params)
        gameRpcRoomOne.srvtable.doTableManageGameStart(shadowRoomId, mpReq.getDict(), 0)

    @classmethod
    def queryTableManageClearPlayersReq(cls, shadowRoomId, tableId):
        mpReq = cls.makeTableManageReq(0, shadowRoomId, tableId, None, 'clear_players')
        rfc = gameRpcRoomOne.srvtable.doTableManageClearPlayers(shadowRoomId, mpReq.getDict(), 1)
        return rfc.getResult()

    @classmethod
    def sendChangeBetsConfReq(cls, shadowRoomId, betsConf):
        mpReq = MsgPack()
        mpReq.setCmd("room")
        mpReq.setParam("action", "change_betsConf")
        mpReq.setParam("roomId", shadowRoomId)
        mpReq.setParam("betsConf", betsConf)
        gameRpcRoomOne.srvtable.doChangeBetsConf(shadowRoomId, mpReq.getDict(), 0)

    @classmethod
    def sendChangeBetsConfReqToAllShadowRoom(cls, ctrlRoomId, betsConf):
        for shadowRoomId in tyconfig.getRoomDefine(ctrlRoomId).shadowRoomIds:
            cls.sendChangeBetsConfReq(shadowRoomId, betsConf)

    @classmethod
    def sendTableClothRes(cls, gameId, userId, tableType, tableTheme=None):
        mpTableClothRes = MsgPack()
        mpTableClothRes.setCmd('table_cloth')
        mpTableClothRes.setResult('userId', userId)
        mpTableClothRes.setResult('gameId', gameId)
        mpTableClothRes.setResult('tableType', tableType)
        mpTableClothRes.setResult('tableTheme', tableTheme)
        tyrpcconn.sendToUser(userId, mpTableClothRes)

    @classmethod
    def sendQuickStartRes(cls, gameId, userId, reason, roomId=0, tableId=0, info=""):
        mpQuickRes = MsgPack()
        mpQuickRes.setCmd('quick_start')
        mpQuickRes.setResult('info', info)
        mpQuickRes.setResult('userId', userId)
        mpQuickRes.setResult('gameId', gameId)
        mpQuickRes.setResult('roomId', roomId)
        mpQuickRes.setResult('tableId', tableId)
        mpQuickRes.setResult('seatId', 0)  # 兼容检查seatId参数的地主客户端
        mpQuickRes.setResult('reason', reason)
        tyrpcconn.sendToUser(userId, mpQuickRes)

    @noException()
    def reportBiGameEvent(self, eventId, userId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, tag=''):
        finalUserChip = hallrpcutil.getChip(userId)
        finalTableChip = 0
        clientId = tysessiondata.getClientId(userId)
        tybireport.reportGameEvent(eventId,
                                   userId,
                                   self.gameId,
                                   roomId,
                                   tableId,
                                   roundId,
                                   detalChip,
                                   state1,
                                   state2,
                                   cardlist,
                                   clientId,
                                   finalTableChip,
                                   finalUserChip)
