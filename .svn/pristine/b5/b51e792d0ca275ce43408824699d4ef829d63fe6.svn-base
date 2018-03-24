# -*- coding: utf-8 -*-
"""
站内消息,类似邮箱功能,可以带附件
"""

from tuyoo5.core import tygame
from tuyoo5.core.tyconst import HALL_GAMEID


class HallUserEventLogin(tygame.UserEventLogin):
    '''
    用户登录事件，监听此事件的业务，应为需要在登录过程中同步处理用户信息的业务
    若不需要同步处理，则可监听HallUserEventOnLine事件
    '''

    def __init__(self, userId, isCreate, isDayfirst, isReconnect, intClientId):
        super(HallUserEventLogin, self).__init__(userId, HALL_GAMEID, isCreate, isDayfirst, isReconnect, intClientId)


class HallUserEventOnLine(tygame.UserEventOnLine):

    def __init__(self, userId, isCreate, isDayfirst, isReconnect, intClientId):
        super(HallUserEventOnLine, self).__init__(userId, HALL_GAMEID, isCreate, isDayfirst, isReconnect, intClientId)


class HallUserEventOffLine(tygame.UserEventOffLine):

    def __init__(self, userId):
        super(HallUserEventOffLine, self).__init__(userId, HALL_GAMEID)


class TYEventRouletteDiamond(tygame.UserEvent):
    """
    钻石抽奖事件
    """

    def __init__(self, userid, gameid, number):
        super(TYEventRouletteDiamond, self).__init__(userid, gameid)
        self.number = number


class HallShareEvent(tygame.UserEvent):

    def __init__(self, gameid, userid, shareid):
        super(HallShareEvent, self).__init__(userid, gameid)
        self.shareid = shareid


class MonthCheckinEvent(tygame.UserEvent):

    def __init__(self, userId, gameId, status):
        super(MonthCheckinEvent, self).__init__(userId, gameId)
        self.status = status


class MonthCheckinOkEvent(MonthCheckinEvent):

    def __init__(self, userId, gameId, status, checkinDate):
        super(MonthCheckinOkEvent, self).__init__(userId, gameId, status)
        self.checkinDate = checkinDate


class MonthSupCheckinOkEvent(MonthCheckinEvent):

    def __init__(self, userId, gameId, status, checkinDate):
        super(MonthSupCheckinOkEvent, self).__init__(userId, gameId, status)
        self.checkinDate = checkinDate


class TYUserVipLevelUpEvent(tygame.UserEvent):

    def __init__(self, gameId, userId, oldVipLevel, newVipLevel):
        super(TYUserVipLevelUpEvent, self).__init__(userId, gameId)
        self.oldVipLevel = oldVipLevel
        self.newVipLevel = newVipLevel
