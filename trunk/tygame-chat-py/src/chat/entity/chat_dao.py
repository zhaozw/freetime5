# -*- coding=utf-8 -*-
"""
Created on 2017年11月02日10:14:41

@author: yzx

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

class DaoChatRecord(object):

    def __init__(self):
        super(DaoChatRecord, self).__init__()

    def save_message_record(self, message_id, info):
        raise NotImplementedError

    def save_user_record(self, user_id, target_user_id, message_id, now):
        raise NotImplementedError

    def update_record(self, user_id, target_user_id,message_id, ret):
        raise NotImplementedError

    def save_record_result(self, user_id, target_user_id,message_id, ret):
        raise NotImplementedError

    def get_record_list(self, user_id, target_user_id):
        raise NotImplementedError

    def get_next_record_list(self, user_id, target_user_id, score):
        raise NotImplementedError

    def get_record_info(self, message_id):
        raise NotImplementedError

    # def update_user_chat_list(self, user_id, target_user_id, info):
    #     raise NotImplementedError

    # def get_user_chat_list(self, user_id):
    #     raise NotImplementedError

    # def get_user_chat_list_detail(self, user_id):
    #     raise NotImplementedError

    def del_user_chat(self, user_id, target_user_id):
        raise NotImplementedError

    def get_user_chat_score(self, user_id, target_user_id, message_id):
        raise NotImplementedError

class DaoChatRecordRedis(DaoChatRecord):
    def __init__(self):
        super(DaoChatRecordRedis, self).__init__()

    def save_message_record(self, message_id, info):
        DaoChatRecordHash.HSET(0, message_id, info)

    def save_user_record(self, user_id, target_user_id, message_id, now):
        DaoUserChatRecordZSet.ZADD(user_id, now, message_id,  "%s:%s" % (user_id,target_user_id))
        DaoUserChatRecordZSet.ZADD(target_user_id, now, message_id, "%s:%s" % (target_user_id,user_id))

    def update_record(self, user_id, target_user_id, message_id, content):
        debug("update record: ", user_id, target_user_id,message_id, content)
        info = DaoChatRecordHash.HGET(0, message_id)
        if info:
            debug("update record: ", user_id, target_user_id, info)
            DaoChatRecordHash.HSET(0, message_id, content)

    def save_record_result(self, user_id, target_user_id, message_id,win_user_id):
        debug("save record:  ", user_id, target_user_id,message_id, win_user_id)
        info = DaoChatRecordHash.HGET(0, message_id)
        if info:
            debug("save record: ", user_id, target_user_id, info, type(info))
            content = info.get("content")
            # TODO 应该都是字符串吧
            content_obj = ftstr.loads(content)
            content_obj["code"] = "result"
            content_obj["winUserId"] = win_user_id
            info["content"]=ftstr.dumps(content_obj)
            DaoChatRecordHash.HSET(0, message_id, info)


    def get_record_list(self, user_id, target_user_id):
        return DaoUserChatRecordZSet.ZRANGE(user_id, 0, -1,True , "%s:%s" % (user_id,target_user_id))

    def get_next_record_list(self, user_id, target_user_id, score):
        return DaoUserChatRecordZSet.ZRANGEBYSCORE(user_id, "("+str(score), "+inf",True ,None,None,None, "%s:%s" % (user_id,target_user_id))
        # return DaoUserChatRecordZSet.ZRANGE(user_id, score, -1,True ,"%s:%s" % (user_id,target_user_id))

    def get_record_info(self, message_id):
        return DaoChatRecordHash.HGET(0, message_id)

    # def update_user_chat_list(self, user_id, target_user_id, info):
        #最后一条消息
        # DaoUserChatListHash.HSET(user_id, target_user_id, info)
        # DaoUserChatListHash.HSET(target_user_id, user_id, info)

    # def get_user_chat_list_detail(self, user_id):
        # return  DaoUserChatListHash.HGETALL(user_id)

    # def get_user_chat_list(self, user_id):
    #     return  DaoUserChatListHash.HKEYS(user_id)

    def del_user_chat(self, user_id, target_user_id):
        DaoUserChatRecordZSet.DEL(user_id,target_user_id)

    def get_user_chat_score(self,user_id, target_user_id, message_id):
        return DaoUserChatRecordZSet.ZSCORE(user_id,message_id,"%s:%s" % (user_id, target_user_id))
        # return DaoUserChatRecordZSet.ZRANK(user_id,message_id,"%s:%s" % (user_id, target_user_id))


class DaoUserChatRecordZSet(tydao.DataSchemaZset):
    """
    用户聊天记录的Redis存储实现.

    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'chat:record:{}'
    DBNAME = 'user'

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY.format(mainKeyExt)


class DaoChatRecordHash(tydao.DataSchemaHashSameKeys):
    """
    聊天记录的Redis存储实现.

    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'chat:record'
    DBNAME = 'mix'
    # TODO 单独的库,分库
    SUBVALDEF = tydao.DataAttrObjDict('record_info', {}, 256)

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY

# class DaoUserChatListHash(tydao.DataSchemaHashSameKeys):
#     """
#     用户聊天对话的Redis存储实现.
#
#     MAINKEY,数据键值
#     user,决定数据存储的库
#     """
#     MAINKEY = 'chat:chatlist:%s'
#     DBNAME = 'user'
#     # TODO 单独的库
#     SUBVALDEF = tydao.DataAttrObjDict('follow_info', {}, 256)