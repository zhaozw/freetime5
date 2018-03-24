# -*- coding=utf-8 -*-
"""
Created on 2018年03月16日

@author: yzx

{
    "time": 1521167582886,
    "userId": 10003,
    "targetUserId": 10007,
    "msgType": 2,
    "content": "{\"miniGameId\":602,\"code\":\"refuse\"}"
}

{
    "time": 1521167580705,
    "userId": 10003,
    "targetUserId": 10007,
    "msgType": 0,
    "content": "{\"text\":\"fsdfasdfasd\"}"
}

"""
import json

from freetime5.util import ftstr


class ChatMessage(object):
    """
    聊天消息
    """
    def __init__(self, user_id,target_user_id,msg_type,time,content):
        # 用户ID
        self._userId = user_id
        # 目标用户ID
        self._targetUserId = target_user_id
        # 消息类型
        self._msgType = msg_type
        # 消息时间戳
        self._time = time
        # 消息内容
        self._content = content


    @property
    def userId(self):
        return self._userId

    @property
    def targetUserId(self):
        return self._targetUserId

    @property
    def msgType(self):
        return self._msgType

    @property
    def time(self):
        return self._time

    @property
    def content(self):
        return self._content


    def pack(self):
        object_dict = lambda o: { key.lstrip('_') : value  for
                                  key, value in o.__dict__.items() if key.startswith('_') and not key.endswith('_')}
        return json.dumps(self,default=object_dict, separators=(',', ':'))

    def getDict(self):
        return { key.lstrip('_') : value  for
                                  key, value in self.__dict__.items() if key.startswith('_') and not key.endswith('_')}

    # def unpack(self, jstr):
    #     try:
    #         # self.__dict__ = json.loads(jstr)
    #         pass
    #     except Exception, e:
    #         raise Exception('unpack error ! '+ str(e) + ' jstr=' + repr(jstr))

class GameChatMessage(ChatMessage):
    """
    聊天中的游戏消息
    """
    def __init__(self, user_id,target_user_id,msg_type,time,content):
        super(GameChatMessage, self).__init__(user_id,target_user_id,msg_type,time,content)
        self._miniGameId_ = 0
        self._code_ = ""
        self._winUserId_ = 0
        self._init_game()

    def _init_game(self):
        _obj = ftstr.loads(self._content)
        self._miniGameId_ = _obj.get("miniGameId")
        self._code_ = _obj.get("code")
        self._winUserId_ = _obj.get("winUserId", "-1")

    @classmethod
    def load_info(cls,info):
        _userId = info.get("userId")
        _targetUserId = info.get("targetUserId")
        _msgType = info.get("msgType")
        _time = info.get("time")
        _content = info.get("content")
        return cls(_userId,_targetUserId,_msgType,_time,_content)

    @property
    def code(self):
        return self._code_

    @code.setter
    def code(self, code):
        self._code_ = code
        self._content = ftstr.dumps({"miniGameId":self._miniGameId_,"code":self._code_})





class SystemChatMessage(ChatMessage):
    """
    聊天中的游戏消息
    """
    def __init__(self, user_id,target_user_id,msg_type,time,content):
        super(SystemChatMessage, self).__init__(user_id,target_user_id,msg_type,time,content)
        # 系统消息模块
        self._code_ = "sns"
        # 系统消息状态
        self._status_ = "accept"
    #     self._init_message()

    # def _init_message(self):
    #     _obj = ftstr.loads(self._content)
    #     self._status_ = _obj.get("status")
    #     self._code_ = _obj.get("code")

