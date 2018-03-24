# -*- coding=utf-8 -*-

from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from tuyoo5.core import tygame, tyrpcconn
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin


_DEBUG, debug = ftlog.getDebugControl(__name__)


class HallPluginShare(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginShare, self).__init__()

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        pass

    @typlugin.markPluginEntry(cmd='share5/weixin', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doWeiXinShare(self, msg):
        '''
        客户端通知服务器，完成了一次微信分享
        '''
        mi = hallchecker.CHECK_BASE.check(msg)
        if _DEBUG:
            debug('doWeiXinShare IN->', mi)

        mo = MsgPack()
        mo.setCmd('share5')
        mo.setResult('action', 'weixin')

        if mi.error:
            mo.setError(1, mi.error)
        else:
            event = tygame.WeiXinSharedEvent(mi.userId, mi.gameId)
            typlugin.syncTrigerEvent(event)
            mo.setResult('ok', 1)

        if mi.hasUserId:
            tyrpcconn.sendToUser(mi.userId, mo)

        if _DEBUG:
            debug('doWeiXinShare OUT')
        return 1
