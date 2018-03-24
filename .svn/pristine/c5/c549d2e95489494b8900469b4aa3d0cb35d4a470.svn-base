# -*- coding: utf-8 -*-
'''
Created on 2018年2月6日

@author: lx
'''
import time

from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tyrpcconn
from tuyoo5.core.tydao import DataSchemaSet
from casualmatch.plugins.srvutil._private import _rpc_user_info

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

BIG_GAME_QUEUE_TIMEOUT = 60

class DaoCasualGameMatch(DataSchemaSet):
    DBNAME = 'mix'
    MAINKEY = 'casualmatch'

    # _LUA_ADD_USER_TO_BIG_MATCH_MALE_HASH = '''
    # local joinGameQueueKey = tostring(KEYS[1])
    # local userId_str = tostring(KEYS[2])
    # local result = redis.call('HSET', joinGameQueueKey..userId, "demandSex", demandSex)
    # local result = redis.call('HSET', joinGameQueueKey..userId, "waittimes", 0)
    # return result
    # '''
    #
    # _LUA_BIG_MATCH_USER_LEN_HASH = '''
    # local matchQueueMaleKey = tostring(KEYS[1])
    # local matchQueueFemaleKey = tostring(KEYS[2])
    # local resultMale = redis.call('HLEN', matchQueueMaleKey)
    # local resultFemale = redis.call('HLEN', matchQueueFemaleKey)
    # local total_user_len = resultMale + resultFemale
    # return total_user_len
    # '''
    #
    # _LUA_BIG_MATCH_FEMALE_LEN_HASH = '''
    # local matchQueueFemaleKey = tostring(KEYS[1])
    # local resultFemale = redis.call('HLEN', matchQueueFemaleKey)
    # return resultFemale
    # '''
    #
    # _LUA_BIG_MATCH_MALE_LEN_HASH = '''
    # local matchQueueFemaleKey = tostring(KEYS[1])
    # local resultFemale = redis.call('HLEN', matchQueueFemaleKey)
    # return resultFemale
    # '''
    #
    # _LUA_ADD_USER_TO_BIG_MATCH_FEMALE_HASH = '''
    # local joinGameQueueKey = tostring(KEYS[1])
    # local userId = tostring(KEYS[2])
    # local demandSex = tostring(KEYS[3])
    # local result = redis.call('HLEN', joinGameQueueKey..userId)
    # if result == 0
    # then
    #     return 1024
    # end
    # local result = redis.call('HSET', joinGameQueueKey..userId, "demandSex", demandSex)
    # local result = redis.call('HSET', joinGameQueueKey..userId, "waittimes", 0)
    # return result
    # '''

    _LUA_ADD_USER_TO_BIG_MATCH_MALE = '''
    local joinGameQueueKey = tostring(KEYS[1])
    local userId = tostring(KEYS[2])
    local result = redis.call('SADD', joinGameQueueKey, userId)
    return result
    '''

    _LUA_DEL_USER_TO_BIG_MATCH_MALE = '''
    local joinGameQueueKey = tostring(KEYS[1])
    local userId = tostring(KEYS[2])
    local result = redis.call('SREM', joinGameQueueKey, userId)
    return result
    '''

    _LUA_ADD_USER_TO_BIG_MATCH_FEMALE = '''
    local joinGameQueueKey = tostring(KEYS[1])
    local userId = tostring(KEYS[2])
    local result = redis.call('SADD', joinGameQueueKey, userId)
    return result
    '''

    _LUA_DEL_USER_TO_BIG_MATCH_FEMALE = '''
    local joinGameQueueKey = tostring(KEYS[1])
    local userId = tostring(KEYS[2])
    local result = redis.call('SREM', joinGameQueueKey, userId)
    return result
    '''

    _LUA_BIG_MATCH_USER_LEN = '''
    local matchQueueMaleKey = tostring(KEYS[1])
    local matchQueueFemaleKey = tostring(KEYS[2])
    local resultMale = redis.call('SCARD', matchQueueMaleKey)
    local resultFemale = redis.call('SCARD', matchQueueFemaleKey)
    local total_user_len = resultMale + resultFemale
    return total_user_len
    '''

    _LUA_BIG_MATCH_MALE_LEN = '''
    local matchQueueMaleKey = tostring(KEYS[1])
    local resultMale = redis.call('SCARD', matchQueueMaleKey)
    return resultMale
    '''

    _LUA_BIG_MATCH_FEMALE_LEN = '''
    local matchQueueFemaleKey = tostring(KEYS[1])
    local resultFemale = redis.call('SCARD', matchQueueFemaleKey)
    return resultFemale
    '''

    _LUA_BIG_MATCH_USER_FEMALE = '''
    local bigMatchQueueFemaleKey = tostring(KEYS[1])
    local user_a = 0
    user_a = redis.call('SPOP', bigMatchQueueFemaleKey)
    return user_a
    '''

    _LUA_BIG_MATCH_USER_MALE = '''
    local bigMatchQueueMaleKey = tostring(KEYS[1])
    local user_b = 0
    user_b = redis.call('SPOP', bigMatchQueueMaleKey)
    return user_b
    '''


    _LUA_ADD_USER_TO_GAMEQUEUE_MALE = '''
    local joinGameQueueKey = tostring(KEYS[1])
    local userId = tostring(KEYS[2])
    local gameId = tostring(KEYS[3])
    local result = redis.call('SADD', joinGameQueueKey..gameId, userId)
    return result
    '''

    _LUA_DEL_USER_TO_GAMEQUEUE_MALE = '''
    local joinGameQueueKey = tostring(KEYS[1])
    local userId = tostring(KEYS[2])
    local gameId = tostring(KEYS[3])
    local result = redis.call('SREM', joinGameQueueKey..gameId, userId)
    return result
    '''

    _LUA_ADD_USER_TO_GAMEQUEUE_FEMALE = '''
    local joinGameQueueKey = tostring(KEYS[1])
    local userId = tostring(KEYS[2])
    local gameId = tostring(KEYS[3])
    local key = joinGameQueueKey..gameId
    local result = redis.call('sadd', key, userId)
    return result
    '''

    _LUA_DEL_USER_TO_GAMEQUEUE_FEMALE = '''
    local joinGameQueueKey = tostring(KEYS[1])
    local userId = tostring(KEYS[2])
    local gameId = tostring(KEYS[3])
    local key = joinGameQueueKey..gameId
    local result = redis.call('SREM', key, userId)
    return result
    '''

    _LUA_MATCH_GAME_USER_LEN = '''
    local matchGameQueueMaleKey = tostring(KEYS[1])
    local matchGameQueueFemaleKey = tostring(KEYS[2])
    local gameId = tostring(KEYS[3])
    local resultMale = redis.call('SCARD', matchGameQueueMaleKey..gameId)
    local resultFemale = redis.call('SCARD', matchGameQueueFemaleKey..gameId)
    local total_user_len = resultMale + resultFemale
    return total_user_len
    '''

    _LUA_MATCH_GAME_MALE_LEN = '''
    local matchGameQueueMaleKey = tostring(KEYS[1])
    local gameId = tostring(KEYS[2])
    local resultMale = redis.call('SCARD', matchGameQueueMaleKey..gameId)
    return resultMale
    '''

    _LUA_MATCH_GAME_FEMALE_LEN = '''
    local matchGameQueueFemaleKey = tostring(KEYS[1])
    local gameId = tostring(KEYS[2])
    local resultFemale = redis.call('SCARD', matchGameQueueFemaleKey..gameId)
    return resultFemale
    '''

    _LUA_MATCH_GAME_USER_FEMALE = '''
    local matchGameQueueFemaleKey = tostring(KEYS[1])
    local gameId = tostring(KEYS[2])
    local user_a = 0
    user_a = redis.call('SPOP', matchGameQueueFemaleKey..gameId)
    return user_a
    '''

    _LUA_MATCH_GAME_USER_MALE = '''
    local matchGameQueueMaleKey = tostring(KEYS[1])
    local gameId = tostring(KEYS[2])
    local user_b = 0
    user_b = redis.call('SPOP', matchGameQueueMaleKey..gameId)
    return user_b
    '''


    _LUA_MATCH_GAME_USER = '''
    local matchGameQueueMaleKey = tostring(KEYS[1])
    local matchGameQueueFemaleKey = tostring(KEYS[2])
    local gameId = tostring(KEYS[3])
    local resultMale = redis.call('SCARD', matchGameQueueMaleKey..gameId)
    local resultFemale = redis.call('SCARD', matchGameQueueFemaleKey..gameId)
    local total_user = resultMale + resultFemale
    local user_a = 0
    local user_b = 0
    if total_user >= 2
    then
        if resultFemale >= 1
        then
            user_a = redis.call('SPOP', matchGameQueueFemaleKey..gameId)
            if resultMale >= 1
            then
                user_b = redis.call('SPOP', matchGameQueueMaleKey..gameId)
            else
                user_b = redis.call('SPOP', matchGameQueueFemaleKey..gameId)
            end
        else
            user_a = redis.call('SPOP', matchGameQueueMaleKey..gameId)
            user_b = redis.call('SPOP', matchGameQueueMaleKey..gameId)
        end
    end
    return user_a, user_b
    '''

    @classmethod
    def _getMatchQueueMaleKeyHash(cls):
        return "bigmatchqueue:male"

    @classmethod
    def _getMatchQueueFemaleKeyHash(cls):
        return "bigmatchqueue:female"

    @classmethod
    def _getMatchQueueMaleKey(cls):
        return "matchqueue:male"

    @classmethod
    def _getMatchQueueFemaleKey(cls):
        return "matchqueue:female"

    @classmethod
    def _getMatchGameQueueMaleKey(cls):
        return "gamequeue:male:"

    @classmethod
    def _getMatchGameQueueFemaleKey(cls):
        return "gamequeue:female:"

    @classmethod
    def joinMatchGameQueueMale(cls, userId, gameId):
        if _DEBUG:
            ftlog.info("joinMatchGameQueueMale userId:", userId)
        keyList = [cls._getMatchGameQueueMaleKey(),
                   userId, gameId]
        result = cls.EVALSHA(0, cls._LUA_ADD_USER_TO_GAMEQUEUE_MALE, keyList)

        return result

    @classmethod
    def quitMatchGameQueueMale(cls, userId, gameId):
        if _DEBUG:
            ftlog.info("quitMatchGameQueueMale userId:", userId)
        keyList = [cls._getMatchGameQueueMaleKey(),
                   userId, gameId]
        result = cls.EVALSHA(0, cls._LUA_DEL_USER_TO_GAMEQUEUE_MALE, keyList)

        return result

    @classmethod
    def joinMatchGameQueueFemale(cls, userId, gameId):
        if _DEBUG:
            ftlog.info("joinMatchGameQueueFemale userId:", userId)
        key = cls._getMatchGameQueueFemaleKey()
        keyList = [key, userId, gameId]
        if _DEBUG:
            debug("In joinMatchGameQueueFemale @@@@@ keyList = ", keyList)
        result = cls.EVALSHA(0, cls._LUA_ADD_USER_TO_GAMEQUEUE_FEMALE, keyList)

        return result

    @classmethod
    def quitMatchGameQueueFemale(cls, userId, gameId):
        if _DEBUG:
            ftlog.info("quitMatchGameQueueFemale userId:", userId)
        keyList = [cls._getMatchGameQueueFemaleKey(),
                   userId, gameId]
        result = cls.EVALSHA(0, cls._LUA_DEL_USER_TO_GAMEQUEUE_FEMALE, keyList)

        return result

    @classmethod
    def joinBigMatchQueueMaleHash(cls, userId, demandSex):
        if _DEBUG:
            ftlog.info("joinBigMatchQueueMale userId:", userId, " demandSex = ", demandSex)

        match_str = '*%d*' % (userId)

        rdatas = cls.redisSSCAN(0, cls._getMatchQueueMaleKeyHash(), match_str)

        if _DEBUG:
            ftlog.info("IN joinBigMatchQueueMale userId:", userId, " rdatas = ", rdatas)

        if len(rdatas) == 1:
            ftlog.info("IN joinBigMatchQueueMaleHash @@ user has entered biggamequeue, userId = ", userId)
            return 1024

        userStr = str(userId) + ":" + str(demandSex) + ":" + str(int(time.time()))

        keyList = [cls._getMatchQueueMaleKeyHash(), userStr]
        result = cls.EVALSHA(0, cls._LUA_ADD_USER_TO_BIG_MATCH_MALE, keyList)
        return result

    @classmethod
    def joinBigMatchQueueFemaleHash(cls, userId, demandSex):
        match_str = '*%d*' % (userId)

        rdatas = cls.redisSSCAN(0, cls._getMatchQueueFemaleKeyHash(), match_str)

        if _DEBUG:
            ftlog.info("IN joinBigMatchQueueFemaleHash userId:", userId, " rdatas = ", rdatas)

        if len(rdatas) == 1:
            ftlog.info("IN joinBigMatchQueueFemaleHash @@ user has entered biggamequeue, userId = ", userId)
            return 1024

        userStr = str(userId) + ":" + str(demandSex) + ":" + str(int(time.time()))

        keyList = [cls._getMatchQueueFemaleKeyHash(), userStr]
        result = cls.EVALSHA(0, cls._LUA_ADD_USER_TO_BIG_MATCH_FEMALE, keyList)
        return result

    @classmethod
    def joinBigMatchQueueMale(cls, userId):
        if _DEBUG:
            ftlog.info("joinBigMatchQueueMale userId:", userId)
        keyList = [cls._getMatchQueueMaleKey(),
                   userId]

        result = cls.EVALSHA(0, cls._LUA_ADD_USER_TO_BIG_MATCH_MALE, keyList)
        return result

    @classmethod
    def quitBigMatchQueueMale(cls, userId):
        if _DEBUG:
            ftlog.info("quitBigMatchQueueMale userId:", userId)

        match_str = '%d:*' % (userId)

        rdatas = cls.redisSSCAN(0, cls._getMatchQueueMaleKeyHash(), match_str)

        keyList = [cls._getMatchQueueMaleKey(),
                   rdatas]
        result = cls.EVALSHA(0, cls._LUA_DEL_USER_TO_BIG_MATCH_MALE, keyList)
        return result

    @classmethod
    def joinBigMatchQueueFemale(cls, userId):
        if _DEBUG:
            ftlog.info("joinBigMatchQueueFemale userId:", userId)
        keyList = [cls._getMatchQueueFemaleKey(),
                   userId]
        result = cls.EVALSHA(0, cls._LUA_ADD_USER_TO_BIG_MATCH_FEMALE, keyList)
        return result

    @classmethod
    def quitBigMatchQueueFemale(cls, userId):
        if _DEBUG:
            ftlog.info("quitBigMatchQueueFemale userId:", userId)

        match_str = '%d:*' % (userId)

        rdatas = cls.redisSSCAN(0, cls._getMatchQueueFemaleKeyHash(), match_str)

        keyList = [cls._getMatchQueueFemaleKey(),
                   rdatas]
        result = cls.EVALSHA(0, cls._LUA_DEL_USER_TO_BIG_MATCH_FEMALE, keyList)
        return result

    @classmethod
    def getBigMatchQueueLength(cls):
        if _DEBUG:
            ftlog.info("getBigMatchQueueLength ")
        keyList = [cls._getMatchQueueMaleKey(), cls._getMatchQueueFemaleKey()]
        user_len = cls.EVALSHA(0, cls._LUA_BIG_MATCH_USER_LEN, keyList)

        if _DEBUG:
            ftlog.info("getBigMatchQueueLength total_user:", user_len)
        return user_len

    @classmethod
    def getBigMatchQueueLengthHash(cls):
        if _DEBUG:
            ftlog.info("getBigMatchQueueLengthHash ")
        keyList = [cls._getMatchQueueMaleKeyHash(), cls._getMatchQueueFemaleKeyHash()]
        user_len = cls.EVALSHA(0, cls._LUA_BIG_MATCH_USER_LEN, keyList)

        if _DEBUG:
            ftlog.info("getBigMatchQueueLength total_user:", user_len)
        return user_len

    @classmethod
    def getBigMatchQueueMaleLength(cls):
        if _DEBUG:
            ftlog.info("getBigMatchQueueMaleLength")
        keyList = [cls._getMatchQueueMaleKey()]
        user_len = cls.EVALSHA(0, cls._LUA_BIG_MATCH_MALE_LEN, keyList)

        if _DEBUG:
            ftlog.info("getBigMatchQueueMaleLength total_user:", user_len)
        return user_len

    @classmethod
    def getBigMatchQueueFemaleLengthHash(cls):
        if _DEBUG:
            ftlog.info("getBigMatchQueueFemaleLengthHash")
        keyList = [cls._getMatchQueueFemaleKeyHash()]
        user_len = cls.EVALSHA(0, cls._LUA_BIG_MATCH_FEMALE_LEN, keyList)

        if _DEBUG:
            ftlog.info("getBigMatchQueueFemaleLength total_user:", user_len)
        return user_len

    @classmethod
    def getBigMatchQueueFemaleLength(cls):
        if _DEBUG:
            ftlog.info("getBigMatchQueueFemaleLength")
        keyList = [cls._getMatchQueueFemaleKey()]
        user_len = cls.EVALSHA(0, cls._LUA_BIG_MATCH_FEMALE_LEN, keyList)

        if _DEBUG:
            ftlog.info("getBigMatchQueueFemaleLength total_user:", user_len)
        return user_len

    @classmethod
    def checkGameMatchCondition(cls, a1, a2, a3, b1, b2, b3):
        if _DEBUG:
            ftlog.info("checkGameMatchCondition @@@ a1 = ", a1,
                       "a2 =",  a2,
                       "a3 =",  a3,
                       "b1 =",  b1,
                       "b2 =",  b2,
                       "b3 =",  b3,
                       )
        if (a2>=2) or (b2>=2) or (a1>=1 and (b1>=1 or b2 >=1)) or (a2>=1 and (b1>=1 or b2>=1 or a3>=1)) or ((a3==1 and a2>=1) or a3>=2)\
                or (b1>=1 and (a1>=1 or a2 >=1)) or (b2>=1 and (a1>=1 or a2>=1 or b3>=1)) or ((b3==1 and b2>=1) or b3>=2):
            return True
        else:
            return False

    @classmethod
    def bigGameMatchResult(cls, group_a1, group_a2, group_a3, group_b1, group_b2, group_b3, callback):
        if _DEBUG:
            ftlog.info("bigGameMatchResult @@@ group_a1 = ", group_a1,
                       "group_a2",  group_a2,
                       "group_a3",  group_a3,
                       "group_b1",  group_b1,
                       "group_b2",  group_b2,
                       "group_b3",  group_b3,
                       )
        if len(group_a1)>=1:
            user_a, user_a_group = group_a1[0], 1

            if len(group_b1) >= 1:
                user_b, user_b_group = group_b1[0], 2
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_a1[0], group_b1[0]
            elif len(group_b2) >= 1:
                user_b,  user_b_group = group_b2[0], 2
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_a1[0], group_b2[0]

        if len(group_a2)>=1:
            user_a, user_a_group = group_a2[0], 1

            if len(group_b1) >= 1:
                user_b, user_b_group = group_b1[0], 2
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_a2[0], group_b1[0]
            elif len(group_b2) >= 1:
                user_b, user_b_group = group_b2[0], 2
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_a2[0], group_b2[0]
            elif len(group_a3) >= 1:
                user_b, user_b_group = group_a3[0], 2
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_a2[0], group_a3[0]
            elif len(group_a2) >= 2:
                user_b, user_b_group = group_a2[1], 1
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_a2[0], group_a2[1]

        if len(group_a3)>=1:
            user_a, user_a_group = group_a3[0], 1

            if len(group_a2) >= 1:
                user_b, user_b_group = group_a2[0], 1
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_a3[0], group_a2[0]
            elif len(group_a3) >= 2:
                user_b, user_b_group = group_a3[1], 1
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_a3[0], group_a3[1]

        if len(group_b1)>=1:
            user_a, user_a_group = group_b1[0], 2

            if len(group_a1) >= 1:
                user_b, user_b_group = group_a1[0], 1
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_b1[0], group_a1[0]
            elif len(group_a2) >= 1:
                user_b, user_b_group = group_a2[0], 1
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_b1[0], group_a2[0]

        if len(group_b2)>=1:
            user_a, user_a_group = group_b2[0], 2

            if len(group_a1) >= 1:
                user_b, user_b_group = group_a1[0], 1
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_b2[0], group_a1[0]
            elif len(group_a2) >= 1:
                user_b, user_b_group = group_a2[0], 1
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_b2[0], group_a2[0]
            elif len(group_b3) >= 1:
                user_b, user_b_group = group_b3[0], 2
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_b2[0], group_b3[0]
            elif len(group_b2) >= 2:
                user_b, user_b_group = group_b2[1], 2
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_a2[0], group_b2[1]

        if len(group_b3)>=1:
            user_a, user_a_group = group_b3[0], 2

            if len(group_b2) >= 1:
                user_b, user_b_group = group_b2[0], 2
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_b3[0], group_b2[0]
            elif len(group_b3) >= 2:
                user_b, user_b_group = group_b3[1], 2
                callback(user_a, user_a_group, user_b, user_b_group)
                del group_b3[0], group_b3[1]

    @classmethod
    def popBigGameMatchedPlayes(cls, user_a, user_a_group, user_b, user_b_group):
        if _DEBUG:
            ftlog.info("popBigGameMatchedPlayes @@@ user_a = ", user_a, " user_a_group =", user_a_group,
                       " user_b = ", user_b, " user_b_group = ", user_b_group)

        if user_a_group == 1:
            keyList = [cls._getMatchQueueFemaleKeyHash(), user_a]
            cls.EVALSHA(0, cls._LUA_DEL_USER_TO_BIG_MATCH_FEMALE, keyList)
        else:
            keyList = [cls._getMatchQueueMaleKeyHash(), user_a]
            cls.EVALSHA(0, cls._LUA_DEL_USER_TO_BIG_MATCH_MALE, keyList)

        if user_b_group == 1:
            keyList = [cls._getMatchQueueFemaleKeyHash(), user_b]
            cls.EVALSHA(0, cls._LUA_DEL_USER_TO_BIG_MATCH_FEMALE, keyList)
        else:
            keyList = [cls._getMatchQueueMaleKeyHash(), user_b]
            cls.EVALSHA(0, cls._LUA_DEL_USER_TO_BIG_MATCH_MALE, keyList)

        split_userId_a = user_a.rsplit(':', 3)
        userId_a = int(split_userId_a[0])

        split_userId_b = user_b.rsplit(':', 3)
        userId_b = int(split_userId_b[0])

        sendBigMatchMsgToPlayers(userId_a, userId_b)


    @classmethod
    def getBigMatchQueueUsersHash(cls):
        if _DEBUG:
            ftlog.info("getBigMatchQueueUsers ")
        match_str = '*boy*'
        male_boy_datas = cls.redisSSCAN(0, cls._getMatchQueueMaleKeyHash(), match_str)
        match_str = '*girl*'
        male_girl_datas = cls.redisSSCAN(0, cls._getMatchQueueMaleKeyHash(), match_str)
        match_str = '*rand*'
        male_rand_datas = cls.redisSSCAN(0, cls._getMatchQueueMaleKeyHash(), match_str)

        fematch_str = '*boy*'
        female_boy_datas = cls.redisSSCAN(0, cls._getMatchQueueFemaleKeyHash(), fematch_str)
        fematch_str = '*girl*'
        female_girl_datas = cls.redisSSCAN(0, cls._getMatchQueueFemaleKeyHash(), fematch_str)
        fematch_str = '*rand*'
        female_rand_datas = cls.redisSSCAN(0, cls._getMatchQueueFemaleKeyHash(), fematch_str)

        while(cls.checkGameMatchCondition(len(female_boy_datas), len(female_rand_datas), len(female_girl_datas),
                                          len(male_girl_datas), len(male_rand_datas), len(male_boy_datas))):
            cls.bigGameMatchResult(female_boy_datas, female_rand_datas, female_girl_datas,
                                   male_girl_datas, male_rand_datas, male_boy_datas, cls.popBigGameMatchedPlayes)

        return 1

    @classmethod
    def getBigMatchQueueUsers(cls):
        if _DEBUG:
            ftlog.info("getBigMatchQueueUsers ")

        user_a = 0
        user_b = 0
        if cls.getBigMatchQueueFemaleLength() >= 1:
            keyList = [cls._getMatchQueueFemaleKey()]
            user_a = cls.EVALSHA(0, cls._LUA_BIG_MATCH_USER_FEMALE, keyList)
            if cls.getBigMatchQueueMaleLength() >= 1:
                keyList = [cls._getMatchQueueMaleKey()]
                user_b = cls.EVALSHA(0, cls._LUA_BIG_MATCH_USER_MALE, keyList)
            else:
                keyList = [cls._getMatchQueueFemaleKey()]
                user_b = cls.EVALSHA(0, cls._LUA_BIG_MATCH_USER_FEMALE, keyList)
        else:
            keyList = [cls._getMatchQueueMaleKey()]
            user_a = cls.EVALSHA(0, cls._LUA_BIG_MATCH_USER_MALE, keyList)
            user_b = cls.EVALSHA(0, cls._LUA_BIG_MATCH_USER_MALE, keyList)

        if _DEBUG:
            ftlog.info("getBigMatchQueueUsers user_a:", user_a, " user_b:", user_b)
        return user_a, user_b

    @classmethod
    def getMatchGameQueueUsers(cls, gameId):
        if _DEBUG:
            ftlog.info("getMatchGameQueueUsers gameId:", gameId)

        user_a = 0
        user_b = 0
        if cls.getMatchGameQueueFemaleLength(gameId) >= 1:
            keyList = [cls._getMatchGameQueueFemaleKey(), gameId]
            user_a = cls.EVALSHA(0, cls._LUA_MATCH_GAME_USER_FEMALE, keyList)
            if cls.getMatchGameQueueMaleLength(gameId) >= 1:
                keyList = [cls._getMatchGameQueueMaleKey(), gameId]
                user_b = cls.EVALSHA(0, cls._LUA_MATCH_GAME_USER_MALE, keyList)
            else:
                keyList = [cls._getMatchGameQueueFemaleKey(), gameId]
                user_b = cls.EVALSHA(0, cls._LUA_MATCH_GAME_USER_FEMALE, keyList)
        else:
            keyList = [cls._getMatchGameQueueMaleKey(), gameId]
            user_a = cls.EVALSHA(0, cls._LUA_MATCH_GAME_USER_MALE, keyList)
            user_b = cls.EVALSHA(0, cls._LUA_MATCH_GAME_USER_MALE, keyList)

        if _DEBUG:
            ftlog.info("getMatchGameQueueUsers user_a:", user_a, " user_b:", user_b)
        return user_a, user_b

    @classmethod
    def getMatchGameQueueLength(cls, gameId):
        if _DEBUG:
            ftlog.info("getMatchGameQueueLength gameId:", gameId)
        keyList = [cls._getMatchGameQueueMaleKey(),
                          cls._getMatchGameQueueFemaleKey(),
                          gameId]
        user_len = cls.EVALSHA(0, cls._LUA_MATCH_GAME_USER_LEN, keyList)

        if _DEBUG:
            ftlog.info("getMatchGameQueueUsers total_user:", user_len)
        return user_len

    @classmethod
    def getMatchGameQueueMaleLength(cls, gameId):
        if _DEBUG:
            ftlog.info("getMatchGameQueueMaleLength gameId:", gameId)
        keyList = [cls._getMatchGameQueueMaleKey(), gameId]
        user_len = cls.EVALSHA(0, cls._LUA_MATCH_GAME_MALE_LEN, keyList)

        if _DEBUG:
            ftlog.info("getMatchGameQueueMaleLength total_user:", user_len)
        return user_len

    @classmethod
    def getMatchGameQueueFemaleLength(cls, gameId):
        if _DEBUG:
            ftlog.info("getMatchGameQueueFemaleLength gameId:", gameId)
        keyList = [cls._getMatchGameQueueFemaleKey(), gameId]
        user_len = cls.EVALSHA(0, cls._LUA_MATCH_GAME_FEMALE_LEN, keyList)

        if _DEBUG:
            ftlog.info("getMatchGameQueueFemaleLength total_user:", user_len)
        return user_len

    @classmethod
    def doCheckBigMatchQueueTimeOut(cls):
        if _DEBUG:
            ftlog.info("doCheckBigMatchQueueTimeOut")

        now_time = int(time.time())

        female_KeyStr = cls._getMatchQueueFemaleKeyHash()
        datas_female = cls._ftredis.executeClusterCmd(cls.DBNAME, 0, 'smembers', female_KeyStr)

        if len(datas_female) >= 1:
            for user_str in datas_female:
                split_str = user_str.rsplit(":", 3)
                userId = int(split_str[0])
                join_time = int(split_str[2])
                if abs(now_time - join_time) >= BIG_GAME_QUEUE_TIMEOUT:
                    result = cls._ftredis.executeClusterCmd(cls.DBNAME, 0, 'srem', female_KeyStr, user_str)
                    if _DEBUG:
                        debug("IN doCheckBigMatchQueueTimeOut @@ after srem @@ female_KeyStr = ", female_KeyStr,
                              " user_str = ", user_str, " result = ", result)
                    mo = MsgPack()
                    mo.setCmd('big_gamequeue_timeout')
                    mo.setResult('userId', userId)
                    mo.setResult('result', 'ok')
                    tyrpcconn.sendToUser(userId, mo)

        male_KeyStr = cls._getMatchQueueMaleKeyHash()
        datas_male = cls._ftredis.executeClusterCmd(cls.DBNAME, 0, 'smembers', male_KeyStr)

        if len(datas_male) >= 1:
            for user_str in datas_male:
                split_str = user_str.rsplit(":", 3)
                userId = int(split_str[0])
                join_time = int(split_str[2])
                if abs(now_time - join_time) >= BIG_GAME_QUEUE_TIMEOUT:
                    result = cls._ftredis.executeClusterCmd(cls.DBNAME, 0, 'srem', female_KeyStr, user_str)
                    if _DEBUG:
                        debug("IN doCheckBigMatchQueueTimeOut @@ after srem @@ female_KeyStr = ", female_KeyStr,
                              " user_str = ", user_str, " result = ", result)
                    mo = MsgPack()
                    mo.setCmd('big_gamequeue_timeout')
                    mo.setResult('userId', userId)
                    mo.setResult('result', 'ok')
                    tyrpcconn.sendToUser(userId, mo)


    @classmethod
    def redisSSCAN(cls, cIndex, keyStr, matchstr='*', count=1000, callback=None, *callbackArgs):
        '''
        SCAN
        获取数据库中的所有键值
        '''
        cur = 0
        dcount = 0
        results = []
        while cur >= 0:
            datas = cls._ftredis.executeClusterCmd(cls.DBNAME, cIndex, 'SSCAN', keyStr, cur, 'MATCH', matchstr, 'COUNT', count)
            cur = datas[0]
            if datas[1]:
                if callback :
                    dcount += 1
                    callback(datas[1], *callbackArgs)
                else:
                    results.extend(datas[1])
            if cur == 0:
                break
        if callback:
            return dcount
        else:
            return results

def sendBigMatchMsgToPlayers(player_A_userId, player_B_userId):
    if _DEBUG:
        debug("sendBigMatchMsgToPlayers @@@@ player_A_userId", player_A_userId, "player_B_userId", player_B_userId)

    table_Info = {}
    for userId in [player_A_userId, player_B_userId]:
        name, purl, sex, addr, citycode = _rpc_user_info.getUserBaseInfo(userId)
        table_Info[userId] = (name, purl, sex, addr, citycode)

    mo = MsgPack()
    mo.setCmd('big_match_result')
    mo.setResult('other_userId', player_B_userId)
    mo.setResult('table_Info', table_Info)
    mo.setResult('result', 'match success')
    tyrpcconn.sendToUser(player_A_userId, mo)

    mo = MsgPack()
    mo.setCmd('big_match_result')
    mo.setResult('other_userId', player_A_userId)
    mo.setResult('table_Info', table_Info)
    mo.setResult('result', 'match success')
    tyrpcconn.sendToUser(player_B_userId, mo)