# -*- coding=utf-8 -*-
'''
Created on 2015年9月28日

@author: liaoxx
'''
from freetime5.util import ftlog, fttime, ftstr
from majiang2.entity.quick_start import MajiangQuickStartDispatcher,\
    MajiangCreateTable
from tuyoo5.core import tyglobal, tyrpcconn
from freetime5.util.ftmsg import MsgPack
from majiang2.table.friend_table_define import MFTDefine
from majiang2.entity import majiang_conf
from majiang2.entity.util import Majiang2Util, sendPopTipMsg
from majiang2.poker2.entity.game.rooms.room import TYRoom
from majiang2.entity.create_table_record import MJCreateTableRecord
from majiang2.entity.create_table import CreateTableData


def doGameQuickStart(userId, gameId, clientId, roomId0, tableId0, playMode, sessionIndex, msg):
    ftlog.debug('doGameQuickStart', userId, gameId, clientId, roomId0, tableId0, playMode, sessionIndex)
    if roomId0 < 1000:
        roomIdx = roomId0
        ftlog.info('doGameQuickStart error roomId:', roomIdx)
        roomId0 = 0

    MajiangQuickStartDispatcher.dispatchQuickStart(msg, userId, gameId, roomId0, tableId0, playMode, clientId)


def doAwardCertificate(userId, gameId, match_id, clientId, msg):
    '''
    TCP 发送的至UTIL服务的quick_start暂时不能用lock userid的方式, 
    因为,消息流 CO->UT->GR->GT->UT会死锁
    '''
    roomId = msg.getParam("roomId")
    ftlog.debug('doAwardCertificate', userId, gameId, roomId, match_id)
    if len(str(roomId)) != 4 and len(str(roomId)) != 8 and len(str(roomId)) != 0:
        roomIdx = roomId
        roomId = roomId * 100
        ftlog.info("doAwardCertificate roomID error, from %d change to %d" % (roomIdx, roomId))

    allrooms = tyglobal.roomIdDefineMap()
    ctrlRoomId = roomId
    if roomId in allrooms:
        roomDef = allrooms[roomId]
        if roomDef.parentId > 0:  # this roomId is shadowRoomId
            ctrlRoomId = roomDef.parentId
    else:
        ftlog.warn("doAwardCertificate, error roomId", roomId)
        return

    ftlog.debug("ctrlRoomId:", ctrlRoomId)

    msg1 = MsgPack()
    msg1.setCmd('room')
    msg1.setParam('gameId', gameId)
    msg1.setParam('userId', userId)
    msg1.setParam('roomId', ctrlRoomId)
    msg1.setParam('action', "match_award_certificate")
    msg1.setParam('match_id', match_id)
    msg1.setParam('clientId', clientId)

    router.sendRoomServer(msg1, roomId)


def doGetCreatTableInfo(userId, gameId, clientId, hasRobot, msg):
    """获取创建牌桌配置信息
    """
    playModes = msg.getParam('playModes')  # 用来过滤playMode,避免返回这个gameId下所有玩法的配置信息,造成无用的一堆冗余数据
    ftlog.debug('GameTcpHandler.doGetCreatTableInfo userId:', userId, ' gameId:', gameId, ' clientId:', clientId, ' hasRobot:', hasRobot, ' playModes:', playModes)
    configList = []
    config = majiang_conf.getCreateTableTotalConfig(gameId)
    for playMode in config:
        if playModes is not None and playMode not in playModes:
            continue
        pConfig = config.get(playMode)
        pConfig['playMode'] = playMode
        if hasRobot > 0:
            pConfig['hasRobot'] = 1
            cardCounts = pConfig.get('cardCount', [])
            newCardCounts = []
            for card in cardCounts:
                ftlog.debug('game_handler.doGetCreatTableInfo card in cardCount:', card)
                if 'hasRobot' in card:
                    newCardCounts.append(card.get('hasRobot', {}))
            pConfig['cardCount'] = newCardCounts

            cardCounts4 = pConfig.get('cardCount4', [])
            newCardCount4 = []
            for card in cardCounts4:
                ftlog.debug('game_handler.doGetCreatTableInfo card in cardCount4:', card)
                if 'hasRobot' in card:
                    newCardCount4.append(card.get('hasRobot', {}))
                else:
                    newCardCount4.append(card)
            pConfig['cardCount4'] = newCardCount4
            if newCardCount4[0]['type'] == MFTDefine.CARD_COUNT_ROUND:
                pConfig['paramType']['cardCount4'] = '选择局数'

            cardCounts3 = pConfig.get('cardCount3', [])
            newCardCount3 = []
            for card in cardCounts3:
                ftlog.debug('game_handler.doGetCreatTableInfo card in cardCount3:', card)
                if 'hasRobot' in card:
                    newCardCount3.append(card.get('hasRobot', {}))
                else:
                    newCardCount3.append(card)
            pConfig['cardCount3'] = newCardCount3

            cardCounts2 = pConfig.get('cardCount2', [])
            newCardCounts2 = []
            for card in cardCounts2:
                ftlog.debug('game_handler.doGetCreatTableInfo card in cardCount2:', card)
                if 'hasRobot' in card:
                    newCardCounts2.append(card.get('hasRobot', {}))
                else:
                    newCardCounts2.append(card)
            pConfig['cardCount2'] = newCardCounts2

        paramType = pConfig.get('paramType', {})
        ftlog.debug('doGetCreatTableInfo paramType:', paramType)
        showOrder = pConfig.get('showOrder', [])
        ftlog.debug('doGetCreatTableInfo showOrder:', showOrder)

        if isinstance(paramType, dict):
            pConfig['paramType'] = Majiang2Util.dict_sort(paramType, showOrder)

        configList.append(pConfig)
    ftlog.debug('doGetCreatTableInfo configList:', configList)

    mo = MsgPack()
    mo.setCmd("create_table")
    mo.setResult('action', 'info')
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('list', configList)
    tyrpcconn.sendToUser(userId, mo)


def _canEnterGame(userId, gameId):
    """是否可进入游戏"""
    gameTime = gamedata.getGameAttrInt(userId, gameId, 'createTableTime')
    nowTime = fttime.getCurrentTimestamp()
    ftlog.debug('Majiang2 game_handler _canEnterGame gameTime:', gameTime, ' nowTime:', nowTime)
    return (nowTime - gameTime) >= 5


def doCreateTable(userId, gameId, clientId, roomId0, tableId0, playMode, hasRobot=0, msg=None):
    """房主创建牌桌"""
    if not playMode:
        ftlog.error('game_handler, cat not create table without playMode...')

    loc = onlinedata.checkUserLoc(userId, clientId, gameId)
    lgameId, lroomId, ltableId, lseatId = loc.split('.')
    lgameId, lroomId, ltableId, lseatId = ftstr.parseInts(lgameId, lroomId, ltableId, lseatId)
    if lgameId > 0 and lroomId > 0 and ltableId > 0 and lseatId >= 0:
        ftlog.warn('create_table error, user in table', lgameId, lroomId, ltableId, lseatId)
        sendPopTipMsg(userId, "请稍候,正在进桌...")
        config = {
            "type": "quickstart",
            "pluginParams": {
                "roomId": lroomId,
                "tableId": ltableId,
                "seatId": lseatId
            }
        }
        todotask = TodoTaskEnterGameNew(lgameId, config)
        mo = MsgPack()
        mo.setCmd('todo_tasks')
        mo.setResult('gameId', gameId)
        mo.setResult('pluginId', lgameId)
        mo.setResult('userId', userId)
        mo.setResult('tasks', TodoTaskHelper.encodeTodoTasks(todotask))
        router.sendToUser(mo, userId)
    elif _canEnterGame(userId, gameId):
        # 保存建桌时间戳
        gamedata.setGameAttr(userId, gameId, 'createTableTime', fttime.getCurrentTimestamp())

        itemParams = msg.getParam("itemParams")

        playerCount = 4
        playerTypeId = itemParams.get(MFTDefine.PLAYER_TYPE, 1)
        playerTypeConfig = majiang_conf.getCreateTableConfig(gameId, playMode, MFTDefine.PLAYER_TYPE, playerTypeId)
        if not playerTypeConfig:
            ftlog.info('MajiangCreateTable.doCreateTable playerTypeId:', playerTypeId, ' playerTypeConfig:', playerTypeConfig)

            sendPopTipMsg(userId, '人数配置有误，请稍后重试')
            return

        playerCount = playerTypeConfig.get('count', 4)
        ftlog.debug('MajiangCreateTable.create_table playerCount:', playerCount)
        cardCountKey = playerTypeConfig.get(MFTDefine.CARD_COUNT, MFTDefine.CARD_COUNT)

        cardCountId = itemParams.get(cardCountKey, 0)
        cardCountConfig = majiang_conf.getCreateTableConfig(gameId, playMode, cardCountKey, cardCountId)
        if not cardCountConfig:
            sendPopTipMsg(userId, '房卡配置有误，请稍后重试')
            return

        if hasRobot == 1 and 'hasRobot' in cardCountConfig:
            cardCountConfig = cardCountConfig.get('hasRobot', {})
            ftlog.debug('MajiangCreateTable.create_table hasRobot == 1:')
        fangka_count = cardCountConfig.get('fangka_count', 1)
        ftlog.debug('MajiangCreateTable.create_table fangka_count:', fangka_count, ' cardCountConfig:', cardCountConfig)

        msg.setParam('isCreateTable', 1)  # 标记创建的桌子是 自建桌
        '''
        根据五个因素筛选合适的房间
        1）gameId         游戏ID
        2）playMode       游戏玩法
        3）playerCount    玩家个数
        4）hasRobot       是否有机器人
        5）itemId         房卡道具
        '''
        itemId = hall_fangka.queryFangKaItem(gameId, userId, clientId)
        if itemId:
            ftlog.debug('MajiangCreateTable._chooseCreateRoom fangKa itemId:', itemId)
        roomId, checkResult = MajiangCreateTable._chooseCreateRoom(userId, gameId, playMode, playerCount, hasRobot, itemId)
        ftlog.debug('MajiangCreateTable._chooseCreateRoom roomId:', roomId, ' checkResult:', checkResult)

        if checkResult == TYRoom.ENTER_ROOM_REASON_OK:
            msg1 = MsgPack()
            msg1.setCmdAction("room", "create_table")
            msg1.setParam("roomId", roomId)
            msg1.setParam("itemParams", itemParams)
            msg1.setParam('needFangka', fangka_count)
            ftlog.debug('MajiangCreateTable._chooseCreateRoom send message to room:', msg1)

            router.sendRoomServer(msg1, roomId)
        else:
            sendPopTipMsg(userId, "暂时无法创建请稍后重试")

    else:
        ftlog.info('majiang2 game_handler, ignore enter game request...')


def doJoinCreateTable(userId, gameId, clientId, roomId0, tableId0, playMode, msg):
    """用户加入自建牌桌
    """
    loc = onlinedata.checkUserLoc(userId, clientId, gameId)
    lgameId, lroomId, ltableId, lseatId = loc.split('.')
    lgameId, lroomId, ltableId, lseatId = ftstr.parseInts(lgameId, lroomId, ltableId, lseatId)
    if lgameId > 0 and lroomId > 0 and ltableId > 0 and lseatId >= 0:
        ftlog.warn('create_table error, user in table')
        sendPopTipMsg(userId, "请稍候,正在进桌...")
        config = {
            "type": "quickstart",
            "pluginParams": {
                "roomId": lroomId,
                "tableId": ltableId,
                "seatId": lseatId
            }
        }
        todotask = TodoTaskEnterGameNew(lgameId, config)
        mo = MsgPack()
        mo.setCmd('todo_tasks')
        mo.setResult('gameId', gameId)
        mo.setResult('pluginId', lgameId)
        mo.setResult('userId', userId)
        mo.setResult('tasks', TodoTaskHelper.encodeTodoTasks(todotask))
        tyrpcconn.sendToUser(userId, mo)
    else:
        createTableNo = msg.getParam('createTableNo', 0)
        if not createTableNo:
            return
        tableId0, roomId0 = CreateTableData.getTableIdByCreateTableNo(createTableNo)
        if not tableId0 or not roomId0:
            sendPopTipMsg(userId, "找不到您输入的房间号")
            return
        msg1 = MsgPack()
        msg1.setParam("shadowRoomId", roomId0)
        msg1.setParam("roomId", roomId0)
        msg1.setParam("tableId", tableId0)
        msg1.setParam("createTableNo", createTableNo)
        msg1.setCmdAction("room", "join_create_table")
        router.sendRoomServer(msg1, roomId0)


def doGetCreateTableRecord(userId, gameId, clientId, msg):
    """全量请求牌桌记录
    """
    startRecordIndex = msg.getParam('startRecordIndex', None)
    if not startRecordIndex:
        startRecordIndex = 0
    endRecordIndex = msg.getParam('endRecordIndex', None)
    if not endRecordIndex:
        endRecordIndex = 19

    MJCreateTableRecord.sendAllRecordToUser(userId, gameId, startRecordIndex, endRecordIndex)


def doGetCreateTableRecordForCustomer(userId, gameId, clientId, msg):
    """全量请求他人的牌桌记录
    """
    targetUserId = msg.getParam('targetUserId', None)
    targetTableNo = msg.getParam('targetTableNo', None)
    playMode = msg.getParam('playMode', None)

    startRecordIndex = msg.getParam('startRecordIndex', None)
    if not startRecordIndex:
        startRecordIndex = 0
    endRecordIndex = msg.getParam('endRecordIndex', None)
    if not endRecordIndex:
        endRecordIndex = 19

    MJCreateTableRecord.sendAllRecordToUserForCustomer(userId, gameId, playMode, targetUserId, targetTableNo, startRecordIndex, endRecordIndex)
