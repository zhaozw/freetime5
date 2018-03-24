# -*- coding=utf-8 -*-
"""
Created on 2017年11月02日10:14:41

@author: yzx

# TODO 同时加互相为好友
"""

from freetime5.util import ftstr, ftlog
from tuyoo5.core import tydao

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

class DaoFollow(object):

    def __init__(self):
        super(DaoFollow, self).__init__()

    def do_follow_launch(self, user_id, target_user_id, info):
        raise NotImplementedError

    def do_follow_landfall(self, user_id, target_user_id, info):
        raise NotImplementedError

    def get_follow_list(self, user_id):
        raise NotImplementedError


class DaoBan(object):
    def __init__(self):
        super(DaoBan, self).__init__()


class DaoFriend(object):
    def __init__(self):
        super(DaoFriend, self).__init__()

    def create_friend(self, user_id, target_user_id, info):
        raise NotImplementedError

    def get_friend_list(self, user_id):
        raise NotImplementedError

    def get_friend(self,user_id, target_user_id):
        raise NotImplementedError

    def del_friend(self,user_id, target_user_id):
        raise NotImplementedError

class DaoVSRecord(object):
    def __init__(self):
        super(DaoVSRecord, self).__init__()

    def save_vs_record(self, user_id, target_user_id, result):
        raise NotImplementedError

    def get_vs_record(self, user_id, target_user_id):
        raise NotImplementedError

    def get_vs_record_list(self, user_id):
        raise NotImplementedError

    def setting_demand_record(self, user_id, info):
        raise NotImplementedError

    def get_demand_record(self, user_id):
        raise NotImplementedError

    def setting_preference_record(self, user_id, info):
        raise NotImplementedError

    def get_preference_record(self, user_id):
        raise NotImplementedError

    def save_game_record(self, user_id, mini_game_id, info):
        raise NotImplementedError

    def get_game_record(self, user_id, mini_game_id):
        raise NotImplementedError

    def get_game_record_list(self, user_id):
        raise NotImplementedError


class DaoFollowRedis(DaoFollow):
    def __init__(self):
        super(DaoFollowRedis, self).__init__()

    def do_follow_launch(self, user_id, target_user_id, info):
        ## 发送关注请求，两个人都有对方的user_id,info
        DaoUserFollowRedis.HSET(user_id, target_user_id, info)
        DaoUserFollowRedis.HSET(target_user_id, user_id, info)

    def do_follow_landfall(self, user_id, target_user_id, ret):
        ## 用户登陆后接受关注请求
        info = DaoUserFollowRedis.HGET(user_id, target_user_id)
        if info:
            # info = ftstr.loads(info_str)
            info["status"] = ret
            # info2 = ftstr.dumps(info)
            debug("do_follow_landfall: ", user_id, target_user_id, info)
            DaoUserFollowRedis.HSET(user_id, target_user_id, info)
            DaoUserFollowRedis.HSET(target_user_id, user_id, info)
            return 1
        else:
            return 0

    def get_follow_list(self, user_id):
        return DaoUserFollowRedis.HGETALL(user_id)


class DaoFriendRedis(DaoFriend):
    def __init__(self):
        super(DaoFriendRedis, self).__init__()

    def create_friend(self, user_id, target_user_id, info):
        DaoUserFriendRedis.HSET(user_id, target_user_id, info)
        DaoUserFriendRedis.HSET(target_user_id, user_id, info)
        return 1

    def get_friend_list(self, user_id):
        return DaoUserFriendRedis.HGETALL(user_id)

    def get_friend(self,user_id,target_user_id):
        return DaoUserFriendRedis.HGET(user_id, target_user_id)

    def del_friend(self,user_id,target_user_id):
        DaoUserFriendRedis.HDEL(user_id, target_user_id)
        DaoUserFriendRedis.HDEL(target_user_id,user_id)

class DaoVSRecordRedis(DaoVSRecord):
    def __init__(self):
        super(DaoVSRecordRedis, self).__init__()

    def save_vs_record(self, user_id, target_user_id, result):
        DaoUserVSRecordRedis.HSET(user_id, target_user_id, result)

    def get_vs_record(self, user_id, target_user_id):
        return DaoUserVSRecordRedis.HGET(user_id, target_user_id)

    def get_vs_record_list(self, user_id):
        return DaoUserVSRecordRedis.HGETALL(user_id)

    def setting_demand_record(self, user_id, info):
        DaoUserVSDemandHash.HSET(0, user_id, info)

    def get_demand_record(self, user_id):
        return DaoUserVSDemandHash.HGET(0, user_id)

    def setting_preference_record(self, user_id, info):
        DaoUserPreferenceHash.HSET(0, user_id, info)

    def get_preference_record(self, user_id):
        return DaoUserPreferenceHash.HGET(0, user_id)

    def save_game_record(self, user_id, mini_game_id, info):
        DaoUserGameRecordRedis.HSET(user_id, mini_game_id, info)

    def get_game_record(self, user_id, mini_game_id):
        return DaoUserGameRecordRedis.HGET(user_id, mini_game_id)

    def get_game_record_list(self, user_id):
        return DaoUserGameRecordRedis.HGETALL(user_id)


class DaoUserFollowRedis(tydao.DataSchemaHashSameKeys):
    """
    用户follow的Redis存储实现.

    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'sns:follow:%s'
    # 采用%做定位符，运行时会自动补全userId
    DBNAME = 'user'
    # TODO 单独的库
    SUBVALDEF = tydao.DataAttrObjDict('follow_info', {}, 256)


class DaoUserBanRedis(tydao.DataSchemaList):
    MAINKEY = 'sns:ban:%s'
    DBNAME = 'user'


class DaoUserFriendRedis(tydao.DataSchemaHashSameKeys):
    """
    用户friend的Redis存储实现.

    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'sns:friend:%s'
    DBNAME = 'user'
    SUBVALDEF = tydao.DataAttrObjDict('friend_info', {}, 256)


class DaoUserVSRecordRedis(tydao.DataSchemaHashSameKeys):
    """
    用户VSRecord的Redis存储实现.

    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'sns:vsrecord:%s'
    DBNAME = 'user'
    SUBVALDEF = tydao.DataAttrObjDict('record_info', {}, 256)

class DaoUserGameRecordRedis(tydao.DataSchemaHashSameKeys):
    """
    用户游戏Record的Redis存储实现.

    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'sns:gamerecord:%s'
    DBNAME = 'user'
    SUBVALDEF = tydao.DataAttrObjList('record_info', [], 256)


class DaoUserVSDemandHash(tydao.DataSchemaHashSameKeys):
    """
    匹配偏好的Redis存储实现.

    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'sns:demand'
    DBNAME = 'mix'
    # TODO 单独的库
    SUBVALDEF = tydao.DataAttrObjList('demand_info', [], 256)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY

class DaoUserPreferenceHash(tydao.DataSchemaHashSameKeys):
    """
    匹配偏好的Redis存储实现.

    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'sns:preference'
    DBNAME = 'mix'
    # TODO 单独的库
    SUBVALDEF = tydao.DataAttrObjDict('preference_info', {}, 256)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY