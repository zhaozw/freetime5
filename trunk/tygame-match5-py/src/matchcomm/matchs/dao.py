from freetime5.util import ftlog
from freetime5.util import ftstr
from matchcomm.matchs.models import RoomInfo
from tuyoo5.core import tydao


class DaoRoomInfo(tydao.DataSchemaHashSameKeys):
    DBNAME = 'mix'
    MAINKEY = 'roomInfo:%s'
    SUBVALDEF = tydao.DataAttrStr('room_info', '', 256)

class DaoMatchStatus(tydao.DataSchemaHashSameKeys):
    DBNAME = 'mix'
    MAINKEY = 'mstatus2:%s'
    SUBVALDEF = tydao.DataAttrStr('match_status', '', 256)

class DaoMatchSigninRecord(tydao.DataSchemaHashSameKeys):
    DBNAME = 'mix'
    MAINKEY = 'msignin5:%s:%s:%s:%s'
    SUBVALDEF = tydao.DataAttrStr('signin_record', '', 256)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY % mainKeyExt


class DaoUserSigninRecord(tydao.DataSchemaSet):
    DBNAME = 'user'
    MAINKEY = 'usersignin5:%s'

class DaoMatchPlayerInfo(tydao.DataSchemaHashSameKeys):
    DBNAME = 'user'
    MAINKEY = 'minfo2:%s'
    SUBVALDEF = tydao.DataAttrStr('player_info', '', 256)

class DaoUserMatchHistory(tydao.DataSchemaList):
    MAINKEY = 'mhistory5:%s'
    DBNAME = 'user'


# def decodeRoomInfo(roomId, jstr):
#     d = ftstr.loads(jstr)
#     return RoomInfo.fromDict(roomId, d)
#
# def loadAllRoomInfo(gameId):
#     ret = {}
#     datas = DaoRoomInfo.HGETALL(gameId)
#     if datas:
#         i = 0
#         while i + 1 < len(datas):
#             try:
#                 roomId = datas[i]
#                 ret[roomId] = decodeRoomInfo(roomId, datas[i + 1])
#             except:
#                 ftlog.error('roominfo.loadAllRoomInfo gameId=', gameId,
#                             'roomId=', datas[i],
#                             'roomInfo=', datas[i + 1])
#             i += 2
#     return ret
#
#
# def loadRoomInfo(gameId, roomId):
#     jstr = DaoRoomInfo.HGET(roomId)
#     if jstr:
#         return decodeRoomInfo(roomId, jstr)
#     return None


def saveRoomInfo(gameId, roomInfo):
    d = roomInfo.toDict()
    jstr = ftstr.dumps(d)
    DaoRoomInfo.HSET(gameId, roomInfo.roomId, jstr)

def removeRoomInfo(gameId, roomId):
    DaoRoomInfo.HDEL(gameId,roomId)

def saveMatchStatus(gameId, matchId,jstr):
    DaoMatchStatus.HSET(gameId, matchId, jstr)

def getMatchStatus(gameId, matchId):
    return DaoMatchStatus.HGET(gameId, matchId)


def loadUserSigninRecord(userId):
    return DaoUserSigninRecord.SMEMBERS(userId)


def saveUserSigninRecord(userId, record):
    DaoUserSigninRecord.SADD(userId,record)


def removeUserSigninRecord(userId, record):
    DaoUserSigninRecord.SREM(userId,record)


def saveMatchSigninRecord(gameId, matchId, instId, roomId,userId,jstr):
    DaoMatchSigninRecord.HSET(0,userId, jstr,mainKeyExt=(gameId, matchId, instId, roomId))


def loadMatchSigninRecord(gameId, matchId, instId, roomId):
    return DaoMatchSigninRecord.HGETALL(0,mainKeyExt=(gameId, matchId, instId, roomId))


def removeMatchSigninRecord(gameId, matchId, instId, roomId, userId):
    DaoMatchSigninRecord.HDEL(0,userId, mainKeyExt=(gameId, matchId, instId, roomId))


def saveMatchPlayerInfo(userId,matchId,info):
    DaoMatchPlayerInfo.HSET(userId,matchId,info)


def getMatchPlayerInfo(userId,matchId):
    return DaoMatchPlayerInfo.HGET(userId,matchId)


def removeMatchPlayerInfo(userId,matchId):
    DaoMatchPlayerInfo.HDEL(userId,matchId)


def loadMatchPlayerInfo(userId):
    return DaoMatchPlayerInfo.HGETALL(userId)


def saveUserMatchHistory(userId,record):
    DaoUserMatchHistory.RPUSH(userId,record)