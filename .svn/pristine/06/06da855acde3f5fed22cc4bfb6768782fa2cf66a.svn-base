# -*- coding=utf-8
'''
Created on 2015年7月1日

@author: zhaojiangang
基于：newsvn/hall37-py/tags/tygame-hall5-release-20160913 进行移植

'''
from freetime5.util import ftlog
from tuyoo5.core import tyconfig


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class TYVipException(tyconfig.TYBizException):

    def __init__(self, ec, message):
        super(TYVipException, self).__init__(ec, message)

    def __str__(self):
        return '%s:%s' % (self.errorCode, self.message)

    def __unicode__(self):
        return u'%s:%s' % (self.errorCode, self.message)


class TYVipLevelGiftAlreadyGotException(TYVipException):

    def __init__(self, level):
        super(TYVipLevelGiftAlreadyGotException, self).__init__(-1, '已经领取过VIP%s礼包' % (level))
        self.level = level

    def __str__(self):
        return '%s:%s %s' % (self.errorCode, self.message, self.level)

    def __unicode__(self):
        return u'%s:%s %s' % (self.errorCode, self.message, self.level)


class TYVipLevelNoGiftException(TYVipException):

    def __init__(self, level):
        super(TYVipLevelNoGiftException, self).__init__(-1, 'VIP级别%s没有礼包' % (level))
        self.level = level

    def __str__(self):
        return '%s:%s %s' % (self.errorCode, self.message, self.level)

    def __unicode__(self):
        return u'%s:%s %s' % (self.errorCode, self.message, self.level)


class TYVipLevelNotFoundException(TYVipException):

    def __init__(self, level):
        super(TYVipLevelNotFoundException, self).__init__(-1, '不能识别的VIP级别%s' % (level))
        self.level = level

    def __str__(self):
        return '%s:%s %s' % (self.errorCode, self.message, self.level)

    def __unicode__(self):
        return u'%s:%s %s' % (self.errorCode, self.message, self.level)


class TYVipLevelNotGotException(TYVipException):

    def __init__(self, required, actually):
        super(TYVipLevelNotGotException, self).__init__(-1, '还没有达到%s' % (required))
        self.required = required
        self.actually = actually

    def __str__(self):
        return '%s:%s %s:%s' % (self.errorCode, self.message, self.required, self.actually)

    def __unicode__(self):
        return u'%s:%s %s:%s' % (self.errorCode, self.message, self.required, self.actually)


class TYVipConfException(TYVipException):

    def __init__(self, conf, message):
        super(TYVipConfException, self).__init__(-1, message)
        self.conf = conf

    def __str__(self):
        return '%s:%s conf=%s' % (self.errorCode, self.message, self.conf)

    def __unicode__(self):
        return u'%s:%s conf=%s' % (self.errorCode, self.message, self.conf)


class TYAssistanceException(tyconfig.TYBizException):

    def __init__(self, ec, message):
        super(TYAssistanceException, self).__init__(ec, message)

    def __str__(self):
        return '%s:%s' % (self.errorCode, self.message)

    def __unicode__(self):
        return u'%s:%s' % (self.errorCode, self.message)


class TYAssistanceNotHaveException(TYAssistanceException):

    def __init__(self):
        super(TYAssistanceNotHaveException, self).__init__(-1, '对不起，您没有可用的VIP江湖救急余额呦～')


class TYAssistanceChipTooMuchException(TYAssistanceException):

    def __init__(self, chip, upperChipLimit):
        super(TYAssistanceChipTooMuchException, self).__init__(-1, '金币太多')
        self.chip = chip
        self.upperChipLimit = upperChipLimit
