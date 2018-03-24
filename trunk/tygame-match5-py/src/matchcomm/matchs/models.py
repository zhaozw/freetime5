# -*- coding:utf-8 -*-
"""
Created on 2017年8月15日

@author: zhaojiangang
"""
import random
from tuyoo5.game.tycontent import TYContentItem
from matchcomm.matchs.const import MatchWaitReason


class MatchPlayerData(object):
    def __init__(self, userId):
        # 用户ID
        self.userId = userId
        # 用户名称
        self.userName = ''
        # 报名时间
        self.signinTime = 0
        # clientId
        self.clientId = ''
        # 积分
        self.score = 0
        # 排名
        self.rank = 0
        # 牌桌排名
        self.tableRank = 0
        # 排名费用
        self.feeIndex = 0


class MatchPlayer(MatchPlayerData):
    def __init__(self, userId):
        super(MatchPlayer, self).__init__(userId)
        # 当前阶段打了几幅牌
        self.cardCount = 0
        # 座位
        self._seat = None

    @property
    def seat(self):
        return self._seat

    @property
    def table(self):
        return self._seat.table

class StageMatchPlayer(MatchPlayer):
    def __init__(self, userId):
        super(StageMatchPlayer, self).__init__(userId)
        # 所在分组
        self.group = None
        # 是否退出了比赛
        self.isQuit = False
        # 排序积分
        self._sortScore = None
        # 实例ID
        self.instId = None
        # 等待原因
        self.waitReason = MatchWaitReason.UNKNOWN
        # 退赛时候的排名
        self.lastRank = None

    def __lt__(self, other):
        return self._sortScore < other._sortScore

class MatchSeat(object):
    """MatchTable 比赛游戏座位.

        :param table: 游戏桌对象
        :param seatId: 座位ID，从1开始
        :param player: 玩家对象
        """

    def __init__(self, table, seatId):
        self._table = table
        self._seatId = seatId
        self._location = '%s.%s.%s.%s' % (table.gameId, table.roomId, table.tableId, seatId)
        self._player = None

    @property
    def gameId(self):
        return self.table.gameId

    @property
    def table(self):
        return self._table

    @property
    def seatId(self):
        return self._seatId

    @property
    def roomId(self):
        return self.table.roomId

    @property
    def tableId(self):
        return self.table.tableId

    @property
    def location(self):
        """
        玩家位置信息：游戏ID.房间ID.游戏桌ID.座位ID
        """
        return self._location

    @property
    def userId(self):
        return self._player.userId if self._player else 0

    @property
    def player(self):
        return self._player


class MatchTable(object):
    """    MatchTable 比赛游戏桌.

    :param gameId: 游戏ID.
    :param roomId: 房间ID
    :param tableId: 游戏桌ID
    :param seatCount: 游戏桌人数
    """

    def __init__(self, gameId, roomId, tableId, seatCount):
        # 游戏ID
        self._gameId = gameId
        # 房间ID
        self._roomId = roomId
        # 座位ID
        self._tableId = tableId
        # 所有座位
        self._seats = self._makeSeats(seatCount)
        # 空闲座位
        self._idleSeats = self._seats[:]
        # 使用该桌子的比赛
        self._group = None
        # 当前牌局开始时间
        self.playTime = None
        # 当前牌局ccrc
        self.ccrc = 0
        # 桌子Location
        self._location = '%s.%s.%s' % (self.gameId, self.roomId, self.tableId)

    @property
    def gameId(self):
        return self._gameId

    @property
    def roomId(self):
        return self._roomId

    @property
    def tableId(self):
        return self._tableId

    @property
    def seats(self):
        return self._seats

    @property
    def group(self):
        return self._group

    @property
    def location(self):
        return self._location

    @property
    def seatCount(self):
        return len(self._seats)

    @property
    def idleSeatCount(self):
        """
        空闲座位的数量
        """
        return len(self._idleSeats)

    def getPlayerList(self):
        """
        获取本桌的所有player
        """
        return [seat.player for seat in self.seats if seat.player]

    def getUserIdList(self):
        """
        获取本桌所有userId
        """
        ret = []
        for seat in self.seats:
            ret.append(seat.player.userId if seat.player else 0)
        return ret

    def sitdown(self, player):
        """
        玩家坐下
        """
        assert (player._seat is None)
        assert (len(self._idleSeats) > 0)
        seat = self._idleSeats[-1]
        del self._idleSeats[-1]
        seat._player = player
        player._seat = seat

    def standup(self, player):
        """
        玩家离开桌子
        """
        assert (player._seat and player._seat.table == self)
        seat = player.seat
        seat._player._seat = None
        seat._player = None
        self._idleSeats.append(seat)

    def clear(self):
        """
        清理桌子上的所有玩家
        """
        for seat in self._seats:
            if seat._player:
                self.standup(seat._player)

    def _clearSeat(self, seat):
        seat._player._seat = None
        seat._player = None
        self._idleSeats.append(seat)

    def _makeSeats(self, count):
        assert (count > 0)
        seats = []
        for i in xrange(count):
            seats.append(MatchSeat(self, i + 1))
        return seats


class MatchTableManager(object):
    """
    MatchTableManager 比赛桌管理器
    :param gameId: 游戏ID.
    :param tableSeatCount: 游戏每桌人数

    """

    def __init__(self, gameId, tableSeatCount):
        self.gameId = gameId
        self._tableSeatCount = tableSeatCount
        self._idleTables = []
        self._allTableMap = {}
        self._roomIds = set()

    @property
    def tableSeatCount(self):
        """游戏每桌分组人数"""
        return self._tableSeatCount

    @property
    def roomCount(self):
        """比赛桌房间数量，比赛可以有多个房间"""
        return len(self._roomIds)

    @property
    def allTableCount(self):
        return len(self._allTableMap)

    @property
    def idleTableCount(self):
        """空闲桌数量"""
        return len(self._idleTables)

    @property
    def busyTableCount(self):
        """忙桌数量"""
        return max(0, self.allTableCount - self.idleTableCount())

    def getTableCountPerRoom(self):
        """房间平均游戏桌数量"""
        return len(self._allTableMap) / max(1, self.roomCount)

    def addTables(self, roomId, baseId, count):
        """
        比赛添加游戏桌
        :param roomId: 房间ID
        :param baseId: 游戏桌起始ID
        :param count: 游戏桌数量
        """
        if count > 0:
            self._roomIds.add(roomId)
        for i in xrange(count):
            tableId = baseId + i + 1  # 新框架里tableId 从 1开始计数， 0表示队列。
            table = MatchTable(self.gameId, roomId, tableId, self._tableSeatCount)
            self._idleTables.append(table)
            self._allTableMap[tableId] = table

    def borrowTables(self, count):
        assert (self.idleTableCount >= count)
        ret = self._idleTables[0:count]
        self._idleTables = self._idleTables[count:]
        return ret

    def returnTables(self, tables):
        for table in tables:
            assert (self._allTableMap.get(table.tableId, None) == table)
            assert (not table.getPlayerList())
            self._idleTables.append(table)

    def findTable(self, roomId, tableId):
        return self._allTableMap.get(tableId, None)

    def shuffleIdleTable(self):
        random.shuffle(self._idleTables)


class MatchSigner(object):
    def __init__(self, userId, instId):
        self.userId = userId
        self.instId = instId
        self.userName = ''
        self.clientId = None
        self.signinTime = None
        self.signinParams = None
        self.fee = None
        self.isEnter = False
        self.isLocked = False
        self.inst = None
        self.feeIndex = None


class MatchRiser(object):
    def __init__(self, userId, score, rank, tableRank):
        self.userId = userId
        self.score = score
        self.rank = rank
        self.tableRank = tableRank


class RoomInfo(object):
    clzMap = {}

    def __init__(self, roomType):
        self._roomType = roomType
        self.roomId = None
        self.playerCount = 0

    @classmethod
    def registerRoomType(cls, typeName, clz):
        cls.clzMap[typeName] = clz

    @classmethod
    def fromDict(cls, roomId, d):
        roomType = d['roomType']
        clz = cls.clzMap.get(roomType)
        if clz:
            ret = clz()
            ret.roomId = roomId
            ret.playerCount = d.get('playerCount', 0)
            return ret.fromDict(d)
        return None

    def toDict(self):
        d = {}
        self._toDictImpl(d)
        d['roomType'] = self._roomType
        d['playerCount'] = self.playerCount
        return d

    def _toDictImpl(self, d):
        pass


class MatchRoomInfo(RoomInfo):
    def __init__(self):
        super(MatchRoomInfo, self).__init__('match')
        self.signinCount = 0
        self.startType = None
        self.instId = None
        self.fees = None
        self.startTime = None
        self.signinTime = None

    def fromDict(self, d):
        self.signinCount = d.get('signinCount', 0)
        self.startType = d.get('startType')
        self.instId = d.get('instId')
        self.startTime = d.get('startTime')
        self.signinTime = d.get('signinTime')
        fees = d.get('fees')
        if fees:
            self.fees = TYContentItem.decodeList(fees)
        return self

    def _toDictImpl(self, d):
        d['signinCount'] = self.signinCount
        d['startType'] = self.startType
        d['instId'] = self.instId
        d['startTime'] = self.startTime
        d['signinTime'] = self.signinTime
        if self.fees:
            d['fees'] = TYContentItem.encodeList(self.fees)

RoomInfo.registerRoomType('match', MatchRoomInfo)