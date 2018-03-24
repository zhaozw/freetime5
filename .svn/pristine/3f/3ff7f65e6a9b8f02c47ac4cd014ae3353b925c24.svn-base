# -*- coding=utf-8
'''
Created on 2015年8月25日

@author: zhaojiangang
'''

from freetime5.util import ftlog
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tygameitem
from tuyoo5.plugins.condition.condition import UserCondition


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallUserConditionIsMemberNotSub(UserCondition):
    """
    是会员但不是订阅会员
    """
    TYPE_ID = 'user.cond.isMemberNotSub'

    def check(self, gameId, userId, clientId, timestamp, kwargs):
        if pluginCross.hallsubmember.isSubmember(userId):
            return False
        return pluginCross.hallitem.getAssets(userId, tygameitem.ASSET_ITEM_MEMBER_NEW_KIND_ID) > 0

    def decodeFromDict(self, d):
        self.params = {}
        return self
