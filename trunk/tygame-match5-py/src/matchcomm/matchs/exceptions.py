# -*- coding:utf-8 -*-
"""
Created on 2017年8月23日

@author: zhaojiangang
"""
from tuyoo5.core.tyconfig import TYBizException


class MatchException(TYBizException):

    def __init__(self, ec, message):
        super(MatchException, self).__init__(ec, message)


class MatchSigninException(MatchException):
    def __init__(self, ec, message):
        super(MatchSigninException, self).__init__(ec, message)


class MatchSigninFeeNotEnoughException(MatchSigninException):
    def __init__(self, fee):
        super(MatchSigninFeeNotEnoughException, self).__init__(-1, u'报名费不足.')
        self.fee = fee


class MatchSigninNotStartException(MatchSigninException):
    def __init__(self):
        super(MatchSigninNotStartException, self).__init__(-1, u'比赛未能开启.')


class MatchSigninStoppedException(MatchSigninException):
    def __init__(self):
        super(MatchSigninStoppedException, self).__init__(-1, u'比赛已停止.')


class MatchSigninFullException(MatchSigninException):
    def __init__(self):
        super(MatchSigninFullException, self).__init__(-1, u'比赛报名人数已满.')


class UserAlreadySigninException(MatchSigninException):
    def __init__(self):
        super(UserAlreadySigninException, self).__init__(-1, u'用户已报名比赛.')


class UserAlreadyInMatchException(MatchSigninException):
    def __init__(self):
        super(UserAlreadyInMatchException, self).__init__(-1, u'用户已经在比赛中.')


class BadMatchStateException(MatchException):
    def __init__(self):
        super(BadMatchStateException, self).__init__(-1, u'未知的比赛状态.')


class MatchStoppedException(MatchException):
    def __init__(self):
        super(MatchStoppedException, self).__init__(-1, u'比赛已关闭.')
