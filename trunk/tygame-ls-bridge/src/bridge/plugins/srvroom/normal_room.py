# coding=UTF-8
'''普通房间类
'''

from bridge.plugins.srvroom.room import TYRoom
from bridge.plugins.srvroom.room_mixin import TYRoomMixin




class TYNormalRoom(TYRoom, TYRoomMixin):
    '''普通房间类'''

    def __init__(self, roomDefine):
        super(TYNormalRoom, self).__init__(roomDefine)

    #     # GT重启创建Room对象时清空牌桌评分历史数据
    #     roomdao.DaoTableScore.clearTableScore(self.roomId)
    #
    # def getTableScoresKey(self, shadowRoomId):
    #     return "ts:" + str(shadowRoomId)

#     def doReloadConf(self, roomDefine):
#         '''GT刷新配置时，如果桌子数变了需要清空桌子评分历史数据,
#             此处桌子实例数量未改变，redis中也无需改变，换句话而言，不允许动态桌子'''
# #         if self.roomDefine.tableCount != roomDefine.tableCount:
# #             daobase.executeTableCmd(self.roomId, 0, "ZREM", self.getTableScoresKey(self.roomId))
#
#         super(TYNormalRoom, self).doReloadConf(roomDefine)
#
#     def dispatchShadowRoomsForClient(self, clientVer):
#         dispatchConf = self.openShadowRoomIdsDispatch
#         if not dispatchConf:
#             return None
#         allShadows = []
#         for conf in dispatchConf:
#             if clientVer >= conf["version"]["start"]\
#                     and clientVer < conf["version"]["end"]:
#                 for rid in range(conf["shadowRoomIds"]["start"], conf["shadowRoomIds"]["end"] + 1):
#                     allShadows.append(rid)
#                 break
#         return allShadows
#
#     def getShadowRoomIdx(self, roomDefine, clientId, showHuafei):
#         clientVer = tyconfig.getClientIdVer(clientId)
#         if clientVer >= 3.785 and showHuafei or clientId.startswith("robot"):
#             allShadows = self.dispatchShadowRoomsForClient(clientVer)
#             if not allShadows:
#                 allShadows = self.openShadowRoomIds
#         else:
#             allShadows = self.shelterShadowRoomIds
#         ftlog.debug("getShadowRoomIdx", 1, allShadows, clientVer)
#         selectId = choice(allShadows)
#         ftlog.debug("getShadowRoomIdx", clientId, selectId, clientVer)
#         return selectId
#
#     def doQuickStart(self, msg):
#         '''
#         Note:
#             1> 由于不同游戏评分机制不同，例如德州会根据游戏阶段评分，所以把桌子评分存到redis里，方便各游戏服务器自由刷新。
#             2> 为了防止同一张桌子同时被选出来分配座位，选桌时会把tableScore里选出的桌子删除，玩家坐下成功后再添加回去，添回去之前无需刷新该桌子的评分。
#             3> 玩家自选桌时，可能选中一张正在分配座位的桌子，此时需要休眠后重试，只到该桌子完成分配或者等待超时。
#         '''
#         assert self.roomId == msg.getParam("roomId")
#
#         userId = msg.getParam("userId")
#         shadowRoomId = msg.getParam("shadowRoomId")
#         tableId = msg.getParam("tableId")
#         exceptTableId = msg.getParam('exceptTableId')
#         clientId = msg.getParam("clientId")
#         ftlog.hinfo("doQuickStart <<", "|userId, clientId, roomId, shadowRoomId, tableId:", userId, clientId, self.roomId, shadowRoomId, tableId)
#
#         if tableId == 0:  # 服务器为玩家选择桌子并坐下
#             shadowRoomId = choice(self.roomDefine.shadowRoomIds)
#             tableId = self.getBestTableId(userId, shadowRoomId, exceptTableId)
#         else:  # 玩家自选桌子坐下
#             assert isinstance(shadowRoomId, int) and tyconfig.getBigRoomId(shadowRoomId) == self.roomDefine.bigRoomId
#             tableId = self.enterOneTable(userId, shadowRoomId, tableId)
#
#         if not tableId:
#             ftlog.error("doQuickStart getFreeTableId timeout", "|userId, roomId, tableId:", userId, self.roomId, tableId)
#             return
#
#         if ftlog.is_debug():
#             ftlog.info("doQuickStart after choose table", "|userId, shadowRoomId, tableId:", userId, shadowRoomId, tableId)
#         extParams = msg.getKey('params')
#         self.querySitReq(userId, shadowRoomId, tableId, clientId, extParams)
#
#     def getBestTableId(self, userId, shadowRoomId, exceptTableId=None):
#         '''原子化从redis里获取和删除评分最高的桌子Id
#         Return:
#             None: tableScores 队列为空， 所有桌子都在分配座位中
#         '''
#
#         def getBestTableIdFromRedis(shadowRoomId):
#             '''从redis里取出并删除一个评分最高的牌桌
#             '''
#             tableId, tableScore = 0, 0
#             datas = roomdao.DaoTableScore.getBestTableId(shadowRoomId)
#             if datas and len(datas) == 2:
#                 tableId, tableScore = datas[0], datas[1]
#             return tableId, tableScore
#
#         if ftlog.is_debug():
#             ftlog.debug("<<", "|shadowRoomId, exceptTableId:", shadowRoomId, exceptTableId, caller=self)
#         pigTables = []
#         tableId = 0
#         for _ in xrange(5):  # 所有桌子有可能正在分配座位，如果取桌子失败，需要休眠后重试
#             if tyconfig.getRoomDefine(shadowRoomId).tableCount == 1:
#                 tableId = shadowRoomId * 10000 + 1
#                 # tableScore = 100
#             else:
#                 tableId, tableScore = getBestTableIdFromRedis(shadowRoomId)  # 从redis取一个牌桌
#
#                 # 该牌桌被客户端指定排除了，另外再取一个牌桌
#                 if exceptTableId and tableId and exceptTableId == tableId:
#                     tableId1, tableScore1 = getBestTableIdFromRedis(shadowRoomId)
#
#                     # 把之前从redis取出的牌桌加回redis
#                     self._updateTableScore(shadowRoomId, tableScore, tableId, force=True)
#                     tableId, tableScore = tableId1, tableScore1
#
#             if ftlog.is_debug():
#                 ftlog.debug('getBestTableId shadowRoomId, tableId, tableScore=', shadowRoomId, tableId, tableScore)
#             if tableId:
#                 if tyglobal.gameIns().isWaitPigTable(userId, self, tableId):
#                     pigTables.append([shadowRoomId, tableScore, tableId])
#                     tableId = 0
#                     continue
#                 else:
#                     break
#             else:
#                 ftcore.sleep(0.2)
#         if ftlog.is_debug():
#             ftlog.debug('getBestTableId pigTables=', pigTables)
#         if pigTables:
#             for pig in pigTables:
#                 self._updateTableScore(pig[0], pig[1], pig[2], False)
#         return tableId
#
#     def enterOneTable(self, userId, shadowRoomId, tableId):
#         '''指定桌子坐下
#         Returns
#             False: 重试超过次数
#         '''
#         if ftlog.is_debug():
#             ftlog.debug("<< |userId, roomId, shadowRoomId, tableId", userId, self.roomId, shadowRoomId, tableId,
#                         caller=self)
#
#         if tyconfig.getRoomDefine(shadowRoomId).tableCount == 1:
#             return tableId
#
#         for _ in xrange(5):  # 这张桌子有可能正在分配座位，如果取桌子失败，需要休眠后重试
#             result = roomdao.DaoTableScore.removeTableScore(shadowRoomId, tableId)
#             if ftlog.is_debug():
#                 ftlog.debug("after ZREM tableId", "|userId, shadowRoomId, tableId, result:",
#                             userId, shadowRoomId, tableId, result, caller=self)
#             if result == 1:
#                 return tableId
#
#             ftcore.sleep(1)
#
#         return 0
#
#     def _updateTableScore(self, shadowRoomId, tableScore, tableId, force=False):
#         roomdao.DaoTableScore.updateTableScore(shadowRoomId, tableId, tableScore, force)
#
#     def updateTableScore(self, tableScore, tableId, force=False):
#         '''更新redis中的table score,
#         Args:
#             force:
#                 True  强制往redis里添加或更新评分，只有玩家sit时做此操作
#                 False 表示只有redis有该牌桌评分时，才可以更新
#         '''
#         self._updateTableScore(self.roomId, tableScore, tableId, force)
