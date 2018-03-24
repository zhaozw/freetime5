# -*- coding=utf-8 -*-

from freetime5.twisted.ftlock import lockargname
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpcconn
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.core.typlugin import pluginCross, pluginSafeCross
from tuyoo5.core.tyrpchall import ChipNotEnoughOpMode
from tuyoo5.game import tybireport


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginStartChip(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginStartChip, self).__init__()
        self.newuserconf = TyCachedConfig('newuser', tyglobal.gameId())

    def _getStartChipConf(self, clientId):
        # 查找对应的clientid使用的配置
        confs = self.newuserconf.getConfigByClientId(clientId)
        if not confs:
            ftlog.error('the newuser config not found !', clientId)
        if confs:
            return confs['startchip'], confs['autosend'] == 1
        return 0, False

    def _needSendStartChip(self, userId, gameId, clientId):
        '''
        是否需要发放启动资金
        '''
        startchip, autosend = self._getStartChipConf(clientId)
        if _DEBUG:
            debug('_needSendStartChip->', userId, gameId, startchip, autosend)
        if startchip <= 0:
            return False, autosend, 0
        sendMeGift = pluginCross.halldata.getNewUserFlg(userId)
        if _DEBUG:
            debug('_needSendStartChip->', userId, gameId, sendMeGift, type(sendMeGift), startchip)
        return 1 == sendMeGift, autosend, startchip

    @typlugin.markPluginEntry(export=1)
    @lockargname('halluser.startchip', 'userId')
    def sendStartChip(self, userId, gameId, clientId, startChip):
        """
        发放启动资金
        """
        canGive = False
        final = 0
        if startChip is None:
            _, _, startChip = self._needSendStartChip(userId, gameId, clientId)
        if startChip <= 0:
            return canGive, startChip, final

        count = pluginCross.halldata.delNewUserFlg(userId)
        if count == 1:
            canGive = True
            _, final = pluginCross.halldata.incrChip(userId, gameId, startChip, ChipNotEnoughOpMode.NOOP, 'USER_STARTUP', 0)
            tybireport.gcoin('in.chip.newuser.startchip', gameId, startChip)
            if _DEBUG:
                debug('hallstartchip.sendStartChip userId=', userId, 'gameId=', gameId, 'clientId=', clientId,
                      'chip=', startChip, 'final=', final)
        return canGive, startChip, final

    @typlugin.markPluginEntry(export=1)
    def autoSendStartChip(self, userId, gameId, clientId):
        needConfirm = 0
        needSend, auto, startchip = self._needSendStartChip(userId, gameId, clientId)
        if _DEBUG:
            debug('HallPluginStartChip.autoSendStartChip', needSend, auto, userId, gameId, clientId)
        if needSend:
            if auto:
                isSend, _, _ = self.sendStartChip(userId, gameId, clientId, startchip)
                if isSend:
                    needConfirm = 0
                else:
                    needConfirm = 1
            else:
                needConfirm = 1
        else:
            needConfirm = 0
        return needConfirm

    @typlugin.markPluginEntry(export=1)
    def sendStartChipConfirm(self, userId, gameId, clientId):
        needSend, auto, startchip = self._needSendStartChip(userId, gameId, clientId)
        if _DEBUG:
            debug('HallPluginStartChip.sendStartChipConfirm', needSend, auto, userId, gameId, clientId)
        if needSend:
            if auto:
                # 补充处理发送成功后，发送界面信息更新提示
                isSend, _, _ = self.sendStartChip(userId, gameId, clientId, startchip)
                if isSend:
                    pluginSafeCross.halldatanotify.sendDataChangeNotify(userId, gameId, ['chip'])
            else:
                # 需要发资金切非自动发放（需手动领取），客户端弹启动资金领取弹框，界面资源全部在客户端资源包中
                pluginSafeCross.halltodotask.sendTodoTaskStartChip(gameId, userId, startchip, 0, '', '')
        return 1

    @typlugin.markPluginEntry(cmd='new_user_reward5/receive', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doNewUserRewardReceive(self, msg):
        '''
        客户端点击“领取”按钮，领取新手启动资金
        '''
        mi = hallchecker.CHECK_BASE.check(msg)
        if mi.error :
            ftlog.warn('doNewUserRewardReceive', msg, mi.error)
            return 0
        isSend, startChip, _final = self.sendStartChip(mi.userId, mi.gameId, mi.clientId, None)
        mo = MsgPack()
        mo.setCmd('new_user_reward5')
        mo.setResult('action', 'receive')
        mo.setResult('chip', startChip if isSend else 0)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1
    