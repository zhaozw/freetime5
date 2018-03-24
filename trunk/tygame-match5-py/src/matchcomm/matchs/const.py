# -*- coding:utf-8 -*-
"""
Created on 2017年8月8日

@author: zhaojiangang
"""

class StageType(object):
    # ASS
    ASS = 1
    # 定局
    DIEOUT = 2

    VALID_TYPES = (ASS, DIEOUT)

    @classmethod
    def isValid(cls, value):
        return value in cls.VALID_TYPES


class MatchFinishReason(object):
    """比赛结束原因枚举.

    0:正常结束

    1:用户数不足

    2:资源不足

    3:超时

    4:放弃比赛
    """
    # 正常结束
    FINISH = 0
    # 用户数不足
    USER_NOT_ENOUGH = 1
    # 资源不足
    RESOURCE_NOT_ENOUGH = 2
    # 超时
    TIMEOUT = 3
    # 放弃比赛
    GIVE_UP = 4
    # notenter
    NO_ENTER = 5


    @classmethod
    def toString(cls, reason):
        if reason == cls.USER_NOT_ENOUGH:
            return u'由于参赛人数不足,比赛取消'
        elif reason == cls.RESOURCE_NOT_ENOUGH:
            return u'由于比赛过多,系统资源不足,比赛取消'
        elif reason == cls.TIMEOUT:
            return u'比赛超时'
        elif reason == cls.NO_ENTER:
            return u'玩家没有进入'
        return u''


class MatchWaitReason(object):
    """比赛等待原因枚举.

    0:未知

    1:配桌中

    2:轮空等待

    3:晋级等待

    """
    UNKNOWN = 0
    # 配桌中
    WAIT_TABLE = 1
    # 轮空等待
    WAIT_BYE = 2
    # 晋级等待
    WAIT_RISE = 3
    # 首轮等待
    WAIT_FIRST = 4


class MatchStartType(object):
    """比赛开始类型枚举.

    1:人满开赛

    2:定时开赛

    """
    # 人满
    USER_COUNT = 1
    # 定时
    TIMING = 2
    VALID_TYPES = (USER_COUNT, TIMING)

    @classmethod
    def isValid(cls, value):
        return value in cls.VALID_TYPES


class MatchFeeType(object):
    """比赛费用枚举.

    0:不回退

    1:回退

    """
    TYPE_NO_RETURN = 0
    TYPE_RETURN = 1
    VALID_TYPES = (TYPE_NO_RETURN, TYPE_RETURN)

    @classmethod
    def isValid(cls, value):
        return value in cls.VALID_TYPES


class MatchPlayerState(object):
    """比赛玩家状态枚举.

    1:报名

    2:游戏

    """
    SIGNIN = 1
    PLAYING = 2


class MatchType(object):
    """
    比赛类型.
    """
    STAGE_MATCH ="stage_match"
    QUICK_UPGRADE_MATCH ="quick_upgrade_match"
    ARENA_MATCH ="arena_match"
