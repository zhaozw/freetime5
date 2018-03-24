# -*- coding=utf-8 -*-

from freetime5.twisted import ftcore
from freetime5.util import ftlog
from hall5.entity import hallchecker
from tuyoo5.core import tychecker
from tuyoo5.core import tygame
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpchall


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


def check_bindType(msg, result, name):
    bindType = msg.getParamStr(name)
    if len(bindType) <= 0:
        return None, 'the param %s is empty' % (name)
    return bindType, None


class HallPluginSubGame(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginSubGame, self).__init__()
        self.checkAccountUp = tychecker.Checkers(
            hallchecker.check__sdkSignCode,
            tychecker.check_userId,
            check_bindType
        )

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL, tyglobal.SRV_TYPE_HALL_HTTP])
    def initPluginBefore(self):
        pass

    @typlugin.markPluginEntry(httppath='account/upgrade')
    def doUserAccountUpgrade(self, request):
        '''
        SDK 通知玩家绑定了手机或绑定微信等第三方账号
        成功返回: success
        '''
        ftlog.info('doUserAccountUpgrade IN->', request.getDict())
        mi = self.checkAccountUp.check(request)
        if mi.error:
            ret = 'error,' + str(mi.error)
        else:
            event = None
            if mi.bindType == 'wx':
                event = tygame.AccountBindWeiXinEvent(mi.userId, tyglobal.gameId())
            elif mi.bindType == 'mobile':
                event = tygame.AccountBindPhoneEvent(mi.userId, tyglobal.gameId())

            if event:
                tyrpchall.sendEventToHallHU(event)

            ret = 'success'
        ftlog.info('doUserAccountUpgrade OUT->', ret)
        return ret

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def asyncTrigerEvent(self, userId, eventName, eventDict):
        '''
        目前需要：GameDataChangedEvent、MatchOverEvent、GameOverEvent
        '''
        cls = getattr(tygame, eventName)
        if cls:
            ftcore.runOnceDelay(0.01, self._asyncTrigerEvent, userId, cls, eventDict)
            return 1
        return 0

    def _asyncTrigerEvent(self, userId, cls, eventDict):
        event = cls()
        event._decodeFromJsonDict(eventDict)
        typlugin.syncTrigerEvent(event)
