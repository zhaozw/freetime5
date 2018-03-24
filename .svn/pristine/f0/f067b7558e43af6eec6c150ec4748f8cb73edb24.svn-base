# -*- coding=utf-8 -*-
'''
Created on 2015年9月28日

@author: zhaol
'''

import time

from freetime5.util import ftlog, ftstr
from majiang2.table.friend_table_define import MFTDefine
from majiang2.table.table_config_define import MTDefine
from tuyoo5.core import tyconfig, tyrpcconn
from freetime5.util.ftmsg import MsgPack
from majiang2.poker2.entity.game.quick_start import BaseQuickStartDispatcher,\
    BaseQuickStart
from majiang2.poker2.entity.game.rooms.room import TYRoom
from majiang2.poker2.entity.game.rooms.room_mixin import TYRoomMixin
from majiang2.poker2.entity import pokerconf, hallrpcutil
from tuyoo5.core.typlugin import pluginCross, gameRpcRoomOne


def isFriendRoom(roomId):
    if roomId <= 0:
        return False

    roomType = tyconfig.getRoomDefine(roomId).configure
    tableType = roomType.get('tableType', 'normal')
    return tableType == 'create'

class MajiangQuickStartDispatcher(BaseQuickStartDispatcher):
    '''
    按clientId分发快速开始请求
    '''
    @classmethod
    def dispatchQuickStart(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
        isCreate = isFriendRoom(roomId)
        if isCreate:
            return MajiangQuickStartFriend.onCmdQuickStart(msg, userId, gameId, roomId, tableId, playMode, clientId)
        else:
            return MajiangQuickStartCoin.onCmdQuickStart(msg, userId, gameId, roomId, tableId, playMode, clientId) 

class MajiangCreateTable(object):
    '''创建牌桌
            1.找到符合需求的房间
            2.找到该房间所有的桌子
            3.排除已经创建的牌桌，从剩余的桌子选择合适的进入(quick_start)并且坐下
    '''
    @classmethod
    def _canQuickEnterCreateRoom(cls, userId, gameId, roomId):
        if isFriendRoom(roomId):
            return TYRoom.ENTER_ROOM_REASON_OK
        return TYRoom.ENTER_ROOM_REASON_ROOM_ID_ERROR
    
    @classmethod
    def _chooseCreateRoom(cls, userId, gameId, playMode, playerCount=4, hasRobot=0, itemId=None):
        '''服务端为玩家选择要创建的房间'''
        candidateRoomIds = MajiangQuickStartCoin._getCandidateRoomIds(gameId, playMode)
        ftlog.debug("MajiangCreateTable._chooseCreateRoom:", candidateRoomIds
                    , ' playMode=', playMode
                    , ' playerCount=', playerCount
                    , ' hasRobot=', hasRobot)

        for roomId in candidateRoomIds :

            roomConfig = tyconfig.getRoomDefine(roomId).configure
            tableConf = roomConfig.get('tableConf', {})
            
            if roomConfig.get(MFTDefine.IS_CREATE, 0) \
                and (tableConf.get(MTDefine.MAXSEATN, 4) == playerCount) \
                and (roomConfig.get(MTDefine.HAS_ROBOT, 0) == hasRobot):
                roomItemId = roomConfig.get(MFTDefine.CREATE_ITEM, 0)
                if not hasRobot and itemId and (itemId != roomItemId):
                    ftlog.debug('MajiangCreateTable.check playMode ok, hasRobot ok, but fangKa item no ok, curRoomConsume:', roomItemId
                                , ' findRoomConsume:', itemId)
                    continue
                
                ret = cls._canQuickEnterCreateRoom(userId, gameId, roomId)
                ftlog.debug("MajiangCreateTable.check roomId, ret:", roomId, ret, caller=cls)
                if ret == TYRoom.ENTER_ROOM_REASON_OK:
                    return roomId, TYRoom.ENTER_ROOM_REASON_OK
            else:
                ftlog.debug('_chooseCeateRoom roomConf:', roomConfig)
        return 0, TYRoom.ENTER_ROOM_REASON_LESS_MIN
    
    @classmethod
    def _onEnterCreateRoomFailed(cls, checkResult, userId, gameId, clientId, roomId=0):
        '''进入创建房间失败回调函数'''
        ftlog.warn("|userId, reason, roomId:", userId, checkResult, roomId, caller=cls)
        mo = MsgPack()
        mo.setCmd('quick_start') 
        mo.setResult('gameId', gameId)
        mo.setResult('userId', userId)        
        mo.setResult('reason', checkResult) 
        tyrpcconn.sendToUser(userId, mo)
    
class MajiangQuickStartCoin(BaseQuickStart):

    @classmethod
    def saveQuickStartTime(cls, userId, gameId, nowTime):
        '''
        保存最近一次的快速开始成功时间
        '''
        pluginCross.mj2dao.setQuickStartCoinTimeStamp(userId, nowTime)

    @classmethod
    def onCmdQuickStart(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
        '''UT server中处理来自客户端的quick_start请求  
        Args:
            msg
                cmd : quick_start
                if roomId == 0:
                    表示快速开始，服务器为玩家选择房间，然后将请求转给GR
                    
                if roomId > 0 and tableId == 0 : 
                    表示玩家选择了房间，将请求转给GR
                    
                if roomId > 0 and tableId == roomId * 10000 :
                    表示玩家在队列里断线重连，将请求转给GR
                    
                if roomId > 0 and tableId > 0:
                    if onlineSeatId > 0: 
                        表示玩家在牌桌里断线重连，将请求转给GT
                    else:
                        表示玩家选择了桌子，将请求转给GR
        '''
        assert isinstance(userId, int) and userId > 0
        assert isinstance(roomId, int) and roomId >= 0
        assert isinstance(tableId, int) and tableId >= 0
        ftlog.debug("MajiangQuickStartCoin.onCmdQuickStart clientId:", clientId
                   , " userId:", userId
                   , " roomId:", roomId
                   , " tableId:", tableId
                   , " gameId:", gameId
                   , " playMode:", playMode)
        
        gTimeStamp = pluginCross.mj2dao.getQuickStartCoinTimeStamp(userId)
        cTimeStamp = time.time()
        ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart gTimeStamp:', gTimeStamp, 'cTimeStamp:', cTimeStamp)
        # 判断两次quick_start间隔是否超过5秒，没有超过5秒，则不匹配
        if cTimeStamp - gTimeStamp < 3:
            ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart cTimeStamp - gTimeStamp < 5 !!!')
            return 
        
        # 单开, 无论何时quick_start进入都检查loc
        if not pokerconf.isOpenMoreTable(clientId) :
            truelocs, _onTableIds = pluginCross.onlinedata.checkUserLoc(userId, clientId, gameId)
            ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart checkUserLoc:', truelocs, caller=cls)
            for loc in truelocs:
                lgameId, lroomId, ltableId, lseatId = loc.split('.')
                lgameId, lroomId, ltableId, lseatId = ftstr.parseInts(lgameId, lroomId, ltableId, lseatId)
                if lgameId == gameId and lroomId > 0:
                    roomId = lroomId
                    tableId = ltableId
                    ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart old client roomId:', roomId
                                , ' tableId:', tableId
                                , caller=cls)

        if roomId == 0 :  # 玩家点击快速开始
            chosenRoomId, checkResult = cls._chooseRoom(userId, gameId, playMode)
            ftlog.info("MajiangQuickStartCoin.onCmdQuickStart after choose room userId:", userId
                       , " chosenRoomId:", chosenRoomId
                       , " checkResult:", checkResult
                       , caller=cls)
            if checkResult == TYRoom.ENTER_ROOM_REASON_OK :
                # 找到合适的房间 根据roomId找到合适的table
                TYRoomMixin.queryRoomQuickStartReq(msg, chosenRoomId, 0)  # 请求转给GR
                cls.saveQuickStartTime(userId, gameId, cTimeStamp)
            else:
                candidateRoomIds = cls._getCandidateRoomIds(gameId, playMode)
                if candidateRoomIds :
                    rid = candidateRoomIds[0]
                    msg.setParam('candidateRoomId', rid)
                cls._onEnterRoomFailed(msg, checkResult, userId, clientId, roomId)
            return         
        
        if tableId == 0:  # 玩家只选择了房间
            bigRoomId = tyconfig.getBigRoomId(roomId)
            ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart bigRoomId:', bigRoomId)
            if bigRoomId == 0 :
                cls._onEnterRoomFailed(msg, TYRoom.ENTER_ROOM_REASON_ROOM_ID_ERROR, userId, gameId, clientId, roomId)
                return
            
            ctrRoomIds = tyconfig.getControlRoomIds(bigRoomId)
            ctrlRoomId = ctrRoomIds[userId % len(ctrRoomIds)]
            qsParams = msg.getParam('where', 'roomlist')
            reason = cls._canQuickEnterRoom(userId, gameId, ctrlRoomId, True, qsParams)
            ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart reason:', reason, 'ctrRoomIds:', ctrRoomIds, 'ctrlRoomId', ctrlRoomId)
            if reason == TYRoom.ENTER_ROOM_REASON_OK:
                TYRoomMixin.queryRoomQuickStartReq(msg, ctrlRoomId, 0)  # 请求转给GR或GT
                cls.saveQuickStartTime(userId, gameId, cTimeStamp)
            else:
                cls._onEnterRoomFailed(msg, reason, userId, gameId, clientId, roomId, playMode)
            return

        if tableId == roomId * 10000:  # 玩家在队列里断线重连
            ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart tableId:', tableId)
            TYRoomMixin.queryRoomQuickStartReq(msg, roomId, tableId)  # 请求转给GR
            cls.saveQuickStartTime(userId, gameId, cTimeStamp)
            return
        
        onlineSeat = pluginCross.onlinedata.getOnLineLocSeatId(userId, roomId, tableId)
        
        if onlineSeat:
            ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart tableId:', tableId)
            extParam = {}
            extParam['seatId'] = onlineSeat
            moParams = msg.getKey('params')
            for k, v in moParams.items() :
                if not k in extParam :
                    extParam[k] = v
            ftlog.debug('extParam=', extParam)
            TYRoomMixin.querySitReq(userId, roomId, tableId, clientId, extParam)  # 玩家断线重连，请求转给GT
            cls.saveQuickStartTime(userId, gameId, cTimeStamp)
        else:  # 玩家选择了桌子, 
            ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart tableId:', tableId)
            shadowRoomId = tyconfig.getTableRoomId(tableId)
            ctrRoomId = tyconfig.getRoomDefine(shadowRoomId).parentId
            TYRoomMixin.queryRoomQuickStartReq(msg, ctrRoomId, tableId, shadowRoomId=shadowRoomId)  # 请求转给GR
            cls.saveQuickStartTime(userId, gameId, cTimeStamp)
    
    @classmethod
    def _chooseRoom(cls, userId, gameId, playMode):
        '''服务端为玩家选择房间'''
        candidateRoomIds = cls._getCandidateRoomIds(gameId, playMode)
        if ftlog.is_debug():
            ftlog.debug("<<|candidateRoomIds:", candidateRoomIds, 'playMode=', playMode, caller=cls)
        
        for roomId in candidateRoomIds :
            ret = cls._canQuickEnterRoom(userId, gameId, roomId, False)
            if ftlog.is_debug():
                ftlog.debug("|roomId, ret:", roomId, ret, caller=cls)
            if ret == TYRoom.ENTER_ROOM_REASON_OK:
                return roomId, TYRoom.ENTER_ROOM_REASON_OK

        return 0, TYRoom.ENTER_ROOM_REASON_LESS_MIN
       
    @classmethod
    def _getCandidateRoomIds(cls, gameId, playMode):
        return super(MajiangQuickStartCoin, cls)._getCandidateRoomIds(gameId, playMode)

    @classmethod
    def _onEnterRoomFailed(cls, msg, checkResult, userId, gameId, clientId, roomId=0, playMode=''):
        '''
        进入房间失败回调函数
        playMode为''，则进房间失败不用在帮用户选择房间
        '''
        ftlog.warn("|userId, reason, roomId:", userId, checkResult, roomId, caller=cls)  # 调用最小房间金币不够充值提醒的todotask
        if not roomId:
            roomId = msg.getParam('candidateRoomId', 0)
        if checkResult == TYRoom.ENTER_ROOM_REASON_LESS_MIN or checkResult == 104:
            product, _ = pluginCross.mj2productselector.selectLessbuyProduct(userId, clientId, roomId)
            if product:
                chooseRoomId, _ = cls._chooseRoom(userId, gameId, playMode)
                pluginCross.mj2todotask.sendQuickStartNeedCharge(gameId, userId, product, chooseRoomId)

        if checkResult == TYRoom.ENTER_ROOM_REASON_GREATER_MAX and playMode:
            chooseRoomId, checkResult = cls._chooseRoom(userId, gameId, playMode)
            if checkResult == TYRoom.ENTER_ROOM_REASON_OK:
                roomConfig = tyconfig.getRoomDefine(chooseRoomId).configure
                nameDesc = roomConfig['tableConf']['nameDesc'] if 'nameDesc' in roomConfig['tableConf'] else '富豪'
                tipStr = '您已是%s，快去%s找角搓麻吧' % (nameDesc, roomConfig['name'])

                pluginCross.mj2todotask.sendQuickStartJumpRoom(gameId, userId, chooseRoomId, playMode, tipStr)

        #=======================================================================
        # tipStr = '进入房间失败，请稍后重试'
        # mo = MsgPack()
        # mo.setCmd('quick_start')
        # mo.setResult('gameId', gameId)
        # mo.setResult('userId', userId)
        # mo.setError(checkResult, tipStr)
        # router.sendToUser(mo, userId)
        #=======================================================================
        
    @classmethod
    def _canQuickEnterRoom(cls, userId, gameId, roomId, isUserChoosed, where='roomlist'):
        '''
        是用户选择的，校验用户金币是否在[minCoin, maxCoin]之间
        牌桌内的快速开始，校验用户的金币是否在[minCoin, maxTableCoin]之间
        是服务推荐的，校验用户的金币是否在[minCoinQS, maxCoinQS]之间
        
        房间的minCoin/maxCoin可以重叠
        minCoinQS/maxCoinQS最好不要重叠
        '''
        if isFriendRoom(roomId):
            return TYRoom.ENTER_ROOM_REASON_NOT_QUALIFIED
            
        try :
            chip = hallrpcutil.getChip(userId)
            ftlog.debug('MajiangQuickStartCoin:', tyconfig.getRoomDefine(roomId).configure, caller=cls)
            roomConfig = tyconfig.getRoomDefine(roomId).configure
            ismatch = roomConfig.get('ismatch')
            isBigMatch = False
            if roomConfig.get('typeName', '') == 'majiang_bigmatch':
                isBigMatch = True
            if ismatch and not isBigMatch:
                return cls._canQuickEnterMatch(userId, gameId, roomId, chip)
            
            if isUserChoosed :
                minCoinQs = roomConfig[MTDefine.MIN_COIN]
                maxCoinQs = roomConfig[MTDefine.MAX_COIN]
                if where == 'table':
                    maxCoinQs = roomConfig.get(MTDefine.MAX_TABLE_COIN, maxCoinQs)
                    ftlog.debug('quick_start from table, maxCoinQS:', maxCoinQs)
            else:
                minCoinQs = roomConfig[MTDefine.MIN_COIN_QS]
                maxCoinQs = roomConfig[MTDefine.MAX_COIN_QS]
            
            ftlog.debug('MajiangQuickStartCoin roomId:', roomId
                        , 'minCoinQs:', minCoinQs
                        , 'maxCoinQs:', maxCoinQs
                        , 'chip:', chip
                        , caller=cls)

            if chip < minCoinQs and (minCoinQs != -1):
                return TYRoom.ENTER_ROOM_REASON_LESS_MIN
            
            if maxCoinQs > 0 and chip > maxCoinQs:
                return TYRoom.ENTER_ROOM_REASON_GREATER_MAX

            return TYRoom.ENTER_ROOM_REASON_OK

        except Exception as e:
            ftlog.error(e)
            return TYRoom.ENTER_ROOM_REASON_INNER_ERROR

    @classmethod
    def _canQuickEnterMatch(cls, userId, gameId, roomId, userChip):
        ret = gameRpcRoomOne.svrroom.checkCanEnter(roomId, userId, userChip).getResult()
        return ret
    
class MajiangQuickStartFriend(BaseQuickStart):
    
    @classmethod
    def onCmdQuickStart(cls, msg, userId, gameId, roomId, tableId, playMode, clientId):
        '''UT server中处理来自客户端的quick_start请求  
        Args:
            msg
                cmd : quick_start
                if roomId == 0:
                    表示快速开始，服务器为玩家选择房间，然后将请求转给GR
                    
                if roomId > 0 and tableId == 0 : 
                    表示玩家选择了房间，将请求转给GR
                    
                if roomId > 0 and tableId == roomId * 10000 :
                    表示玩家在队列里断线重连，将请求转给GR
                    
                if roomId > 0 and tableId > 0:
                    if onlineSeatId > 0: 
                        表示玩家在牌桌里断线重连，将请求转给GT
                    else:
                        表示玩家选择了桌子，将请求转给GR
        '''
        assert isinstance(userId, int) and userId > 0
        assert isinstance(roomId, int) and roomId >= 0
        assert isinstance(tableId, int) and tableId >= 0
        ftlog.debug("MajiangQuickStartFriend.onCmdQuickStart clientId:", clientId
                   , " userId:", userId
                   , " roomId:", roomId
                   , " tableId:", tableId
                   , " gameId:", gameId
                   , " playMode:", playMode)
        
        tableId = 0
        # 单开, 无论何时quick_start进入都检查loc
        if not pokerconf.isOpenMoreTable(clientId) :
            truelocs, _onTableIds = pluginCross.onlinedata.checkUserLoc(userId, clientId, gameId)
            ftlog.debug('MajiangQuickStartFriend.onCmdQuickStart checkUserLoc:', truelocs, caller=cls)
            for loc in truelocs:
                lgameId, lroomId, ltableId, lseatId = loc.split('.')
                lgameId, lroomId, ltableId, lseatId = ftstr.parseInts(lgameId, lroomId, ltableId, lseatId)
                if lgameId == gameId and lroomId > 0 and isFriendRoom(lroomId):
                    roomId = lroomId
                    tableId = ltableId
                    ftlog.debug('MajiangQuickStartFriend.onCmdQuickStart old client roomId:', roomId, ' tableId:', tableId, caller=cls)

        if roomId > 0 and tableId > 0:
            onlineSeat = pluginCross.onlinedata.getOnlineLocSeatId(userId, roomId, tableId)
            if onlineSeat:
                extParam = {}
                extParam['seatId'] = onlineSeat
                moParams = msg.getKey('params')
                for k, v in moParams.items() :
                    if not k in extParam :
                        extParam[k] = v
                ftlog.debug('extParam=', extParam)
                TYRoomMixin.querySitReq(userId, roomId, tableId, clientId, extParam)  # 玩家断线重连，请求转给GT
            return
          
        ftlog.debug('MajiangQuickStartFriend.onCmdQuickStart friendTable not isReconnect or roomId == 0 or tableId == 0, dissolved')  
        cls._onEnterRoomFailed(msg, TYRoom.ENTER_ROOM_REASON_FRIEND_DISSOLVE, userId, clientId, roomId)
    #===========================================================================
    # 相同函数名，入参也相同，不清楚什么用，先注掉
    # @classmethod
    # def _onEnterRoomFailed(cls, msg, checkResult, userId, gameId, clientId, roomId=0):
    #     '''进入房间失败回调函数'''
    #     ftlog.warn("|userId, reason, roomId:", userId, checkResult, roomId, caller=cls)  # 调用最小房间金币不够充值提醒的todotask
    #     if not roomId:
    #         roomId = msg.getParam('candidateRoomId', 0)
    #                 
    #     mo = MsgPack()
    #     mo.setCmd('quick_start') 
    #     mo.setResult('gameId', gameId) 
    #     mo.setResult('userId', userId) 
    #     mo.setError(checkResult, '进入房间失败，请稍后重试')       
    #     router.sendToUser(mo, userId)
    #===========================================================================
