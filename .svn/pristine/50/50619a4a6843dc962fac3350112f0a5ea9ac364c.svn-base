# -*- coding=utf-8 -*-
"""
Created on 2018年03月15日17:12:09

@author: yzx

"""

class ChatMessageType(object):
    """聊天消息类型枚举.

    文本 0 {"text":"hello"}
    表情 1 {"emoticon":"hello"}
    游戏邀请 2 {"miniGameId":601,"code":"invite"}
    游戏应答 2 {"msgId":601,"code":"accept/refuse/leave/result"}
    语音 4 {"voice":"abcd","second":3}
    文件 5 {"file":"abcd"}
    小视频 6 {"video":"abcd","second":2,"pic":"aaa"}
    系统消息 7 {"code":"sns","status":"invite|accept"}
    语音聊天
    视频聊天

    """
    TEXT = 0
    EMOTICON = 1
    GAME = 2
    VOICE = 4
    FILE = 5
    VIDEO = 6
    SYSTEM = 7
    VALID_TYPES = (TEXT, EMOTICON, GAME, VOICE, FILE, VIDEO, SYSTEM)

    @classmethod
    def is_valid(cls, value):
        return value in cls.VALID_TYPES

class ChatGameCode(object):
    """聊天游戏状态枚举.

    邀请/接受/拒绝/离开/结束
    invite/accept/refuse/leave/result

    """
    INVITE = "invite"
    ACCEPT = "accept"
    REFUSE = "refuse"
    LEAVE = "leave"
    RESULT = "result"

    VALID_TYPES = (INVITE, ACCEPT, REFUSE, LEAVE, RESULT)

    @classmethod
    def is_valid(cls, value):
        return value in cls.VALID_TYPES

class SNSFollowCode(object):
    """好友follow状态枚举.

    邀请/接受/拒绝
    invite/accept/refuse

    """
    INVITE = "invite"
    ACCEPT = "accept"
    REFUSE = "refuse"

    VALID_TYPES = (INVITE, ACCEPT, REFUSE)

    @classmethod
    def is_valid(cls, value):
        return value in cls.VALID_TYPES