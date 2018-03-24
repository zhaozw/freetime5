# -*- coding:utf-8 -*-
'''
Created on 2017年12月25日

@author: lixi
'''

from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.plugins.hallshare2._private import _checker
from hall5.plugins.hallshare2._private import _dao
from hall5.plugins.hallshare2._private import _hall5_share2
from hall5.plugins.hallshare2._private import _hall5_short_url
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpcconn


_DEBUG, debug = ftlog.getDebugControl(__name__)


class HallPluginShare2(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginShare2, self).__init__()
        self.checkBase = hallchecker.CHECK_BASE.clone()
        self.checkGetShareReward = hallchecker.CHECK_BASE.clone()
        self.checkGetShareInfo = hallchecker.CHECK_BASE.clone()
        self.checkGetShareUrl = hallchecker.CHECK_BASE.clone()
        self.checkGetShareReward.addCheckFun(_checker.check_pointId)
        self.checkGetShareInfo.addCheckFun(_checker.check_pointId)
        self.checkGetShareInfo.addCheckFun(_checker.check_urlParams)
        self.checkGetShareUrl.addCheckFun(_checker.check_shareId)
        self.checkGetShareUrl.addCheckFun(_checker.check_urlParams)

    def destoryPlugin(self):
        _dao.Daohall5share2.finalize()
        _dao.DaoHall5ShareGetToken.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        if _DEBUG:
            debug("initPluginBefore share2 -> start initialize config!")
        _hall5_share2._initialize()
        _dao.Daohall5share2.initialize()
        _dao.DaoHall5ShareGetToken.initialize()

    @typlugin.markPluginEntry(confKeys=['game5:{}:share2:0'.format(tyglobal.gameId())],
                              srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onConfChanged(self, _confKeys, _changedKeys):
        _hall5_share2._onConfChanged(tyglobal.gameId())

    @classmethod
    def _doGetShareReward(self, gameId, userId, clientId, pointId, mp, timestamp=None):
        ok, assetList = _hall5_share2.gainShareReward(gameId, userId, clientId, pointId, timestamp)
        rewards = []
        if ok:
            for atup in assetList:
                rewards.append({'itemId':atup[0].kindId,
                                'name':atup[0].displayName,
                                'url':atup[0].pic,
                                'count':atup[1]})

        mp.setResult('gameId', gameId)
        mp.setResult('userId', userId)
        mp.setResult('rewards', rewards)
        return mp

    @typlugin.markPluginEntry(cmd='hall5_share2', act='get_reward', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doGetShareReward(self, msg):
        '''
        客户端回调奖励
        '''
        mo = MsgPack()
        mo.setCmd('hall5_share2')
        mo.setResult('action', 'get_reward')

        mi = self.checkGetShareReward.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            mo = self._doGetShareReward(mi.gameId, mi.userId, mi.clientId, mi.pointId, mo)

        if mo:
            tyrpcconn.sendToUser(mi.userId, mo)

    @classmethod
    def _doGetShareInfo(self, gameId, userId, clientId, pointId, urlParams, mp):
        parsedClientId = _hall5_share2.ParsedClientId.parseClientId(clientId)
        if _DEBUG:
            debug("IN _doGetShareInfo -> parsedClientId = ", parsedClientId)
        if not parsedClientId:
            mp.setResult('ec', -1)
            mp.setResult('info', 'clientId错误')
            return mp

        sharePoint, shareContent = _hall5_share2.getShareContent(gameId, userId, parsedClientId, pointId)

        if not shareContent:
            mp.setResult('ec', -1)
            mp.setResult('info', '没有找到分享')
            return mp

        url = shareContent.buildUrl(userId, parsedClientId, sharePoint.pointId, urlParams)
        url = _hall5_short_url.longUrlToShort(url)
        mp.setResult('gameId', gameId)
        mp.setResult('userId', userId)
        mp.setResult('shareId', shareContent.shareId)
        mp.setResult('pointId', sharePoint.pointId)
        mp.setResult('url', url)
        mp.setResult('shareMethod', shareContent.shareMethod)
        mp.setResult('whereToShare', shareContent.whereToShare)
        mp.setResult('shareRule', shareContent.shareRule)
        if shareContent.preview is not None:
            mp.setResult('preview', shareContent.preview)
        if shareContent.shareQR is not None:
            mp.setResult('shareQR', shareContent.shareQR)
        return mp

    @typlugin.markPluginEntry(cmd='hall5_share2', act='get_share_info', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doGetShareInfo(self, msg):
        '''
        客户端获取分享信息
        '''
        mo = MsgPack()
        mo.setCmd('hall5_share2')
        mo.setResult('action', 'get_share_info')

        mi = self.checkGetShareInfo.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            mo = self._doGetShareInfo(mi.gameId, mi.userId, mi.clientId, mi.pointId, mi.urlParams, mo)

        if mo:
            tyrpcconn.sendToUser(mi.userId, mo)

    @classmethod
    def _doGetShareUrl(self, gameId, userId, clientId, pointId, shareId, urlParams, mp):
        mp.setResult('gameId', gameId)
        mp.setResult('userId', userId)
        mp.setResult('shareId', shareId)
        mp.setResult('pointId', pointId)

        parsedClientId = _hall5_share2.ParsedClientId.parseClientId(clientId)
        if not parsedClientId:
            mp.setResult('ec', -1)
            mp.setResult('info', 'clientId错误')
            return mp

        sharePoint, shareContent = _hall5_share2.getShareContentWithShareId(gameId, userId, parsedClientId, pointId, shareId)

        if not shareContent:
            mp.setResult('ec', -1)
            mp.setResult('info', '没有找到分享')
            return mp

        url = shareContent.buildUrl(userId, parsedClientId, sharePoint.pointId, urlParams)
        url = _hall5_short_url.longUrlToShort(url)
        mp.setResult('url', url)
        return mp

    @typlugin.markPluginEntry(cmd='hall5_share2', act='get_share_url', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doGetShareUrl(self, msg):
        '''
        客户端获取短连接
        '''
        mo = MsgPack()
        mo.setCmd('hall5_share2')
        mo.setResult('action', 'get_share_url')

        mi = self.checkGetShareUrl.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            mo = self._doGetShareUrl(mi.gameId, mi.userId, mi.clientId, mi.pointId, mi.shareId, mi.urlParams, mo)

        if mo:
            tyrpcconn.sendToUser(mi.userId, mo)

