# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''
from freetime5.util import ftlog
from freetime5.util import fttime
from hall5.entity import hallchecker
from hall5.entity.hallevent import HallUserEventOnLine
from hall5.plugins.hallsubmember import _submember
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginSubMember(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginSubMember, self).__init__()
        self.checker = hallchecker.CHECK_BASE.clone()
        self.checker.addCheckFun(self.check_isTempVipUser)

    def check_isTempVipUser(self, msg, result, name):
        val = msg.getParamInt(name)
        if val not in (0, 1):
            return None, 'the param %s error' % (name)
        return val, None

    @typlugin.markPluginEntry(event=HallUserEventOnLine, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def on_user_login(self, event):
        if event.isCreate:
            return
        _submember.checkSubMember(event.gameId, event.userId, '', 0)

    @typlugin.markPluginEntry(cmd='sub_member5', act='unsub', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doUnsubMember(self, msg):
        mi = hallchecker.CHECK_BASE.check(msg)
        timestamp = fttime.getCurrentTimestamp()
        _submember.unsubscribeMember(mi.gameId, mi.userId, mi.isTempVipUser, timestamp, 'UNSUB_MEMBER', 0)
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL, export=1)
    def isSubmember(self, userId):
        """
        用户是否是订阅会员
        @param userId: 用户ID
        """
        return self.submem_status_info(userId, 'isSub')

    @typlugin.markPluginEntry(export=1)
    def subscribeMember(self, gameId, userId, timestamp, eventId, intEventParam, param01='', param02=''):
        status = _submember.subscribeMember(gameId, userId, timestamp, eventId, intEventParam, param01=param01, param02=param02)
        return status.isSub

    @typlugin.markPluginEntry(export=1)
    def isSubExpires(self, userId, nowDT):
        memstatus = _submember.loadSubMemberStatus(userId)
        return memstatus.isSubExpires(nowDT)

    @typlugin.markPluginEntry(export=1)
    def loadSubMemberStatus(self, userId):
        memstatus = _submember.loadSubMemberStatus(userId)
        return memstatus

    @typlugin.markPluginEntry(export=1)
    def submem_status_info(self, userId, keys):
        memstatus = _submember.loadSubMemberStatus(userId)
        if not memstatus:
            return
        if isinstance(keys, (str, unicode)):
            return getattr(memstatus, keys, None)

        vals = []
        for key in keys:
            vals.append(getattr(memstatus, key, None))
        return vals
