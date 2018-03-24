# -*- coding=utf-8 -*-

from freetime5.util import ftlog
from freetime5.util.ftcache import lfu_alive_cache
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.entity import hallconf
from hall5.entity.hallevent import HallUserEventLogin
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpcconn
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.core.typlugin import pluginSafeCross


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginNotice(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginNotice, self).__init__()
        self.config = TyCachedConfig('notice', tyglobal.gameId())
        self.configLogin = TyCachedConfig('notice_login', tyglobal.gameId())

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        pass

    @lfu_alive_cache(maxsize=100, cache_key_args_index=1, alive_second=60)
    def getNoticeInfoByClientId(self, clientId, userId = 0):
        '''
        变化不频繁，每分钟重新计算一次
        '''
        showNoticeIds = []
        showBannerIds = []
        noticeAddIds = []
        confs = self.config.getConfigByClientId(clientId)
        if confs:
            showBannerIds = hallconf.filterStartStopTime(confs['banners'], self.config, 'banners')
            showNoticeIds = hallconf.filterNoticeStartStopTime(confs['notices'], self.config, 'notices')
            if userId > 0:
                noticeAddIds = hallconf.filterNewPlayerTimeLimit(confs['notices'], self.config, 'notices', userId)
            if len(noticeAddIds):
                for idx in noticeAddIds:
                    showNoticeIds.append(idx)
        return showBannerIds, showNoticeIds

    @typlugin.markPluginEntry(event=HallUserEventLogin, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onHallUserEventLogin(self, event):
        if not event.isReconnect:
            # 发送登录弹窗
            self.sendNoticeLoginPopWnd(event)
            # 更新小红点提示信息
            _bannerIds, showIds = self.getNoticeInfoByClientId(event.intClientId, event.userId)
            pluginSafeCross.hallredpoint.resetItemIds(event.userId, 'notice5', showIds)

    @typlugin.markPluginEntry(cmd='notice5', act='list', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def getUserNoiceList(self, msg):
        mi = hallchecker.CHECK_BASE.check(msg)
        if mi.error:
            ftlog.warn('getUserNoiceList', msg, mi.error)
            return 0
        bannerIds, showIds = self.getNoticeInfoByClientId(mi.clientId, mi.userId)
        mo = MsgPack()
        mo.setCmd('notice5')
        mo.setResult('action', 'list')
        mo.setResult('banners', bannerIds)
        mo.setResult('notices', showIds)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    def sendNoticeLoginPopWnd(self, event):
        userId = event.userId
        gameId = event.gameId
        intClientId = event.intClientId
        isCreate = event.isCreate
        isDayfirst = event.isDayfirst
        if _DEBUG:
            debug('HallPluginNotice->sendNoticeLoginPopWnd IN=', userId, gameId, intClientId, isCreate, isDayfirst)

        # if not (isCreate or isDayfirst):
        #     return 0

        # 查找对应的clientid使用的配置
        confs = self.configLogin.getConfigByClientId(intClientId)
        if not confs:
            ftlog.warn('sendNoticeLoginPopWnd, the notice_login configLogin not found !', intClientId)
            return 0

        if _DEBUG:
            debug('HallPluginNotice->sendNoticeLoginPopWnd confs=', userId, gameId, intClientId, confs)

        notices = confs.get('notices', [])
        notices = hallconf.checkStartStopTimeList(notices)
        if _DEBUG:
            debug('HallPluginNotice->sendNoticeLoginPopWnd notices=', userId, gameId, intClientId, notices)

        # 用户条件判定
        newNotices = {}
        for notice in notices:
            conditions = notice['conditions']
            if pluginSafeCross.condition.checkConditions(gameId,
                                                         userId,
                                                         intClientId,
                                                         conditions,
                                                         isCreate=isCreate,
                                                         isDayfirst=isDayfirst):
                newNotices[notice['showStyle']] = notice

        if _DEBUG:
            debug('HallPluginNotice->sendNoticeLoginPopWnd newNotices=', userId, gameId, intClientId, newNotices)

        # 弹出时机判定
        noticeid = None

        noticeid_once = newNotices.get('oncePreLife', {}).get('noticeid')

        if noticeid_once is not None:
            # 更新小红点提示信息
            result = pluginSafeCross.hallredpoint.getNoticePerlifeInfo(event.userId, 'notice5', noticeid_once)
            if result == 0:
                noticeid = noticeid_once
        if not noticeid and isDayfirst:
            noticeid = newNotices.get('oncePreDay', {}).get('noticeid')

        if _DEBUG:
            debug('HallPluginNotice->sendNoticeLoginPopWnd noticeid=', userId, gameId, intClientId, noticeid)
        if not noticeid:
            return 0

        _bannerId, showIds = self.getNoticeInfoByClientId(intClientId, userId)
        if _DEBUG:
            debug('HallPluginNotice->sendNoticeLoginPopWnd popwnd=', userId, gameId, intClientId, noticeid, showIds)

        if noticeid in showIds:
            pluginSafeCross.halltodotask.sendNoticeLoginPopWnd(gameId, userId, noticeid)
            return 1

        return 0
