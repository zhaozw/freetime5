# -*- coding: utf-8 -*-
'''
Created on 2018年1月31日

@author: lx
'''
from freetime5.util import ftlog
from tuyoo5.core import typlugin, tyglobal



_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class CrossEliminationPluginSrvRoom(typlugin.TYPlugin):

    def __init__(self):
        super(CrossEliminationPluginSrvRoom, self).__init__()

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_ROOM])
    def initPluginBefore(self):
        pass

    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def doQuickStart(self, roomId, msgDict, isSync):
    #     if not isSync:
    #         ftcore.runOnce(self.doQuickStart, roomId, msgDict, 1)
    #         return 1
    #     # do sync code
    #     msg = MsgPack(msgDict)
    #     tyglobal.rooms()[roomId].doQuickStart(msg)
    #     return 1
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def doRoomLeave(self, ctrlRoomId, tableId,  userId,  reason, needSendRes, isSync):
    #     if not isSync:
    #         ftcore.runOnce(self.doRoomLeave, ctrlRoomId, tableId,  userId,  reason, needSendRes, 1)
    #         return 1
    #     # do sync code
    #     return 1
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def checkCanEnter(self, roomId, userId, userChip):
    #     ftlog.debug('checkCanEnter, input:', roomId, userId, userChip)
    #     roomIns = tyglobal.rooms()[roomId]
    #     return roomIns.check_enter(userId, userChip)
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def reportGameStart(self, roomId, tableId, matchId, userIds):
    #     ftlog.debug('reportGameStart, input:', roomId, tableId, matchId, userIds)
    #     roomIns = tyglobal.rooms()[roomId]
    #     return roomIns.mark_game_start(tableId, matchId, userIds)
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def reportGameEnd(self, roomId, tableId, matchId, userIds):
    #     ftlog.debug('reportGameEnd, input:', roomId, tableId, matchId, userIds)
    #     roomIns = tyglobal.rooms()[roomId]
    #     return roomIns.mark_game_end(tableId, matchId, userIds)
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def getMatchInfoAbstract(self, roomId, gameId, userId, notAwardList=False):
    #     ftlog.debug('getMatchInfoAbstract, input: ', roomId, gameId, userId, notAwardList)
    #     roomIns = tyglobal.rooms()[roomId]
    #     bigMatch = tyglobal.gameIns().getBigMatchPlugin()
    #     return bigMatch.getMatchInfoAbstract(roomIns, userId, notAwardList)
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def getMatchSimpleInfo(self, roomId, gameId, userId):
    #     ftlog.debug('getMatchSimpleInfo, input: ', roomId, gameId, userId)
    #     roomIns = tyglobal.rooms()[roomId]
    #     bigMatch = tyglobal.gameIns().getBigMatchPlugin()
    #     return bigMatch.getMatchSimpleInfo(roomIns, userId)
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def getMatchAwardListInfo(self, roomId, gameId, userId):
    #     ftlog.debug('getMatchAwardListInfo, input: ', roomId, gameId, userId)
    #     roomIns = tyglobal.rooms()[roomId]
    #     bigMatch = tyglobal.gameIns().getBigMatchPlugin()
    #     return bigMatch.getMatchAwardListInfo(roomIns, userId)
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def isUserInMatch(self, roomId, matchInstId, gameId, userId):
    #     ftlog.debug('isUserInMatch, input: ', roomId, gameId, userId, matchInstId)
    #     roomIns = tyglobal.rooms()[roomId]
    #     bigMatch = tyglobal.gameIns().getBigMatchPlugin()
    #     return bigMatch.isUserInMatch(roomIns, userId, matchInstId)
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def signinNextMatch(self, roomId, matchInstId, gameId, userId):
    #     ftlog.debug('signinNextMatch, input: ', roomId, gameId, userId, matchInstId)
    #     roomIns = tyglobal.rooms()[roomId]
    #     return roomIns.mj_signin_next_match(userId, roomId)
    #
    # @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_ROOM)
    # def getCreateTableByRoomId(self, roomId):
    #     return CreateTable.get_create_table_by_roomid(roomId)
    #
    # def _doMatchState(self, userId, gameId, roomId, match_id):
    #     '''
    #     获取比赛状态
    #     '''
    #     if match_id:  # 老比赛，由于前端新比赛也会发此消息，但没有match_id导致的问题，这里处理下
    #         state = tyglobal.rooms()[roomId].getMatchState(userId, gameId, match_id)
    #         current_ts = int(time.time())
    #         msg = MsgPack()
    #         msg.setCmd('match_state')
    #         msg.setResult('gameId', gameId)
    #         msg.setResult('userId', userId)
    #         msg.setResult('state', state)
    #         msg.setResult('match_id', match_id)
    #         msg.setResult('current_ts', current_ts)
    #         tyrpcconn.sendToUser(userId, msg)
    #
    # def _doMatchAwardCertificate(self, userId, gameId, roomId, match_id):
    #     '''
    #
    #     '''
    #     room = tyglobal.rooms()[roomId]
    #     if hasattr(room, 'get_award_certificate'):
    #         room.get_award_certificate(userId, gameId, match_id)

#     def _signinNextMatch(self, gameId, userId, room_id=0):
#         """
#         报名下一场比赛
#         """
#         ctlRoomIds = [bigRoomId * 10000 + 1000 for bigRoomId in gdata.gameIdBigRoomidsMap()[gameId]]
#         if roomId in ctlRoomIds:
#             room = gdata.rooms()[roomId]
#             if room:
#                 signinParams = gamedata.getGameAttrJson(userId, room.gameId, 'test.signinParams')
#                 room.doSignin(userId, signinParams)
#             else:
#                 ftlog.info('=======signinNextMatch==Trace==', roomId, userId)
# 
#     def _doCreateTableByRoomId(self, userId, gameId, roomId, msg):
#         """
#         自建桌创建
#             1.通过roomId得到房间对象
#             2.得到合适的tableId,然后sit
#         """
#         ftlog.info("<< doCreateTable | userId, clientId, roomId, msg:", userId, gameId, roomId)
# 
#         room = tyglobal.rooms()[roomId]
#         self._doCreateTable(room, msg, gameId)
# 
#     def _consumeFangKa(self, room, userId, gameId, itemParams, playMode, fangka_count):
#         '''
#         消耗房卡
#         '''
#         itemId = room.roomConf.get('create_item', None)
#         if not itemId:
#             sendPopTipMsg(userId, "未知房卡")
# 
#         ftlog.debug('itemParams', itemParams)
#         fangka_count = self._calcShareFangka(itemParams, gameId, playMode, fangka_count, itemId)
#         ftlog.debug('fangka share:', fangka_count)
#         if fangka_count == False and type(fangka_count) == bool:
#             sendPopTipMsg(userId, "房卡配置错误")
#             return False
# 
#         isFangKaEnough = True
#         consumeResult = user_remote.consumeItem(userId, gameId, itemId, fangka_count, room.roomId, room.bigRoomId)
#         if not consumeResult:
#             isFangKaEnough = False
#         if not isFangKaEnough:
#             sendPopTipMsg(userId, "房卡不足，请购买")
#             return False
# 
#         return True
# 
#     def _doCreateTable(self, room, msg, gameId):
#         """
#         选择合适的table,然后sit
#         """
#         assert room.roomId == msg.getParam("roomId")
# 
#         userId = msg.getParam("userId")
#         clientId = msg.getParam("clientId")
#         ftlog.info("<< _doCreateTable |userId, clientId, roomId, msg:", userId, clientId, room.roomId, msg)
#         fangka_count = msg.getParam("needFangka")
#         itemParams = msg.getParam("itemParams")
#         ftlog.debug('itemParams', itemParams)
#         playMode = msg.getParam('play_mode')
#         itemId = room.roomConf.get('create_item', None)
#         if (fangka_count > 0) and (not self.consumeFangKa(room, userId, gameId, itemParams, playMode, fangka_count)):
#             return
# 
#         # 扣卡成功，产生自建桌号，分配table
#         shadowRoomId = choice(room.roomDefine.shadowRoomIds)
#         tableId = room.getBestTableId(userId, shadowRoomId)
#         if not tableId:  # 拿不到桌子
#             sendPopTipMsg(userId, "哎呀呀，没有空桌子了……我们稍候会优先为您安排新桌，请稍等片刻~")
#             ftlog.error("getFreeTableId timeout", "|userId, roomId, tableId:", userId, room.roomId, tableId)
#             user_remote.resumeItemFromRoom(userId, gameId, itemId, fangka_count, room.roomId, room.bigRoomId)
#             return
# 
#         # 扣卡成功，产生自建桌号
#         for _ in range(10):
#             ftId = hall_friend_table.createFriendTable(gameId)
#             if ftId:
#                 ftlog.info("room._doCreateTable create_table ok, userId:", userId, " shadowRoomId:", shadowRoomId, " roomId:",
#                            room.roomId, " tableId:", tableId, " ftId:", ftId, " fangka_count:", fangka_count, room.roomConf)
#                 extParams = msg.getKey('params')
#                 extParams['ftId'] = ftId
#                 room.querySitReq(userId, shadowRoomId, tableId, clientId, extParams)
#                 return
# 
#         ftlog.error('room._doCreateTable request ftId error, return fangka item...')
#         user_remote.resumeItemFromRoom(userId, gameId, itemId, fangka_count, room.roomId, room.bigRoomId)

    # def doJoinCreateTable(self, userId, gameId, roomId, msg):
    #     """
    #     加入自建桌
    #     """
    #     ftlog.debug('RoomTcpHandler.doJoinCreateTable msg=', userId,
    #                 gameId, roomId, msg, caller=self)
    #     room = tyglobal.rooms()[roomId]
    #
    #     self._doJoinCreateTable(room, msg)
    #
    # def getFangKaCountByTableNo(self, tableNo, itemParams, userId, gameId, playMode):
    #     '''
    #     根据table号决定房卡数量
    #     '''
    #     playerTypeId = itemParams.get(MFTDefine.PLAYER_TYPE, 1)
    #     playerTypeConfig = majiang_conf.getCreateTableConfig(gameId, playMode, MFTDefine.PLAYER_TYPE, playerTypeId)
    #     if not playerTypeConfig:
    #         return -1
    #
    #     playerCount = playerTypeConfig.get('count', 4)
    #     ftlog.debug('MajiangCreateTable.create_table playerCount:', playerCount)
    #     cardCountKey = playerTypeConfig.get(MFTDefine.CARD_COUNT, MFTDefine.CARD_COUNT)
    #
    #     cardCountId = itemParams.get(cardCountKey, 0)
    #     cardCountConfig = majiang_conf.getCreateTableConfig(gameId, playMode, cardCountKey, cardCountId)
    #     if not cardCountConfig:
    #         return -1
    #
    #     fangka_count = cardCountConfig.get('fangka_count', 1)
    #     ftlog.debug('MajiangCreateTable.create_table fangka_count:', fangka_count, ' cardCountConfig:', cardCountConfig)
    #     return fangka_count
    #
    # def _calcShareFangka(self, itemParams, gameId, playMode, fangka_count, userId):
    #     '''
    #     计算分享房卡数目
    #     '''
    #     shareFangkaId = itemParams.get('shareFangka', 0)
    #     shareFangkaConfig = majiang_conf.getCreateTableConfig(gameId, playMode, 'shareFangka', shareFangkaId)
    #     ftlog.debug('share Fangkaconfig:', shareFangkaConfig)
    #     if shareFangkaConfig:
    #         shareFangka = shareFangkaConfig.get('share_fangka', 0)
    #         ftlog.debug('share Fangka:', shareFangka)
    #         if shareFangka:
    #             playerTypeId = itemParams.get(MFTDefine.PLAYER_TYPE, 1)
    #             playerTypeConfig = majiang_conf.getCreateTableConfig(gameId, playMode, MFTDefine.PLAYER_TYPE, playerTypeId)
    #             ftlog.debug('playerTypeConfig:', playerTypeConfig)
    #             if not playerTypeConfig:
    #                 sendPopTipMsg(userId, '人数配置有误，请稍后重试')
    #                 return False
    #
    #             playerCount = playerTypeConfig.get('count', 4)
    #             fangka_count = fangka_count / playerCount
    #             ftlog.debug('share Fangka :', fangka_count)
    #     return fangka_count
    #
    # def _doJoinCreateTable(self, room, msg):
    #     '''
    #     加入牌桌
    #     '''
    #     assert room.roomId == msg.getParam("roomId")
    #     userId = msg.getParam("userId")
    #     gameId = msg.getParam("gameId")
    #     shadowRoomId = msg.getParam("shadowRoomId")
    #     tableId = msg.getParam("tableId")
    #     clientId = msg.getParam("clientId")
    #     tableIdNo = msg.getParam("createTableNo")
    #     playMode = room.roomConf.get("playMode")
    #     initParams = CreateTableData.getTableParamsByCreateTableNo(tableIdNo)
    #     ftlog.debug('RoomTcpHandler._doJoinCreateTable tableNo:', tableIdNo, ' initParams:', initParams)
    #
    #     fangKaCount = self.getFangKaCountByTableNo(tableIdNo, initParams, userId, gameId, playMode)
    #     ftlog.info("RoomTcpHandler._doJoinCreateTable >>> userId, clientId, roomId, shadowRoomId, tableId, fangKaCount:", userId, clientId, room.roomId, shadowRoomId, tableId, fangKaCount)
    #     if (fangKaCount > 0) and (not self.consumeFangKa(room, userId, gameId, initParams, playMode, fangKaCount)):
    #         return
    #
    #     assert isinstance(shadowRoomId, int) and tyglobal.roomIdDefineMap()[shadowRoomId].bigRoomId == room.roomDefine.bigRoomId
    #     extParams = msg.getKey('params')
    #     room.querySitReq(userId, shadowRoomId, tableId, clientId, extParams)
    #
    # def doRoomQuickStart(self, roomId, userId, msg):
    #     '''
    #     房间快速开始
    #     '''
    #     ftlog.debug('msg=', msg, caller=self)
    #     tyglobal.rooms()[roomId].doQuickStart(msg)
