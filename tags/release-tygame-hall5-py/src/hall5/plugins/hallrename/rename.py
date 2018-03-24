# -*- coding=utf-8 -*-

from freetime5.twisted.ftlock import lockargname
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpcconn
from tuyoo5.core import tyrpcsdk
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import ChipNotEnoughOpMode
from tuyoo5.core.tyrpchall import UserKeys


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

RENAME_FEE_DIAMOND = 10


def check_name(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) <= 0:
        return None, 'the param %s error' % (name)
    return val, None


class HallPluginRename(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginRename, self).__init__()
        self.checker = hallchecker.CHECK_BASE.clone()
        self.checker.addCheckFun(check_name)
        self.checkerBase = hallchecker.CHECK_BASE.clone()


    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        pass

    @typlugin.markPluginEntry(cmd='change_name5', act='try', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doChangeNameTry(self, msg):
        mi = self.checker.check(msg)
        if mi.error:
            ftlog.warn('doChangeNameTry', msg, mi.error)
            return 0
        code, info, diamond = self._doChangeNameTry(mi.userId, mi.gameId, mi.name, mi.clientId)
        if _DEBUG:
            debug('doChangeNameTry', mi, mi.name,  code, info)
        mo = MsgPack()
        mo.setCmd('change_name5')
        mo.setResult('action', 'try')
        if code != 0:
            mo.setResult('ok', 0)
            mo.setError(code, info)
        else:
            mo.setResult('ok', 1)
            mo.setResult('name', mi.name)
            mo.setResult('diamond', diamond)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @lockargname('hall5.rename', 'userId')
    def _doChangeNameTry(self, userId, gameId, newName, clientId):
        finalCount = -1
        if not newName:
            return -1, '请输入新的昵称', 0

        count = pluginCross.halldata.getSetNameSum(userId)
        if _DEBUG:
            debug('doChangeNameTry count', userId, count)
        if count > 0:
            # 第一次免费，以后扣除钻石
            trueDelta, finalCount = pluginCross.halldata.incrDiamond(userId, gameId, -RENAME_FEE_DIAMOND,
                                                                     ChipNotEnoughOpMode.NOOP,
                                                                     'RENAME5_REDUCE_DIAMOND', 0, clientId)
            if _DEBUG:
                debug('doChangeNameTry reduce userId=', userId,
                      'diamondIncr=', -RENAME_FEE_DIAMOND, 'diamondDelta=', trueDelta,
                      'diamondFinal=', finalCount)

            if trueDelta != -RENAME_FEE_DIAMOND:
                return -1, '钻石不足，请充值', 0

        # SDK改名
        errCode, errMsg = tyrpcsdk.changeName(userId, newName)

        if errCode != 0:
            errMsg = '昵称已被占用，请重新输入' if errCode == 1 else errMsg  # SDK的errMsg为空
            if count > 0:
                # 改名失败，回退钻石
                trueDelta, finalCount = pluginCross.halldata.incrDiamond(userId, gameId, RENAME_FEE_DIAMOND,
                                                                         ChipNotEnoughOpMode.NOOP,
                                                                         'RENAME5_ROOLBACK_DIAMOND', 0, clientId)
                if _DEBUG:
                    debug('doChangeNameTry roolback userId=', userId,
                          'diamondIncr=', RENAME_FEE_DIAMOND, 'diamondDelta=', trueDelta,
                          'diamondFinal=', finalCount, 'sdkerror=', errCode, errMsg)
            return errCode, errMsg, 0

        pluginCross.halldata.incrSetNameSum(userId, 1)
        if finalCount < 0:
            finalCount = pluginCross.halldata.getUserDataList(userId, UserKeys.ATT_DIAMOND)
        return 0, '修改成功', finalCount

    @typlugin.markPluginEntry(cmd='change_name5', act='get', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doChangeNameGet(self, msg):
        # by yuanzx at 2017年09月11日17:16:59
        mi = self.checkerBase.check(msg)
        if mi.error:
            ftlog.warn('doChangeNameGet', msg, mi.error)
            return 0
        code, info = self._doChangeNameGet(mi.userId, mi.gameId, mi.clientId)
        if _DEBUG:
            debug('doChangeNameGet', mi, code, info)
        mo = MsgPack()
        mo.setCmd('change_name5')
        mo.setResult('action', 'get')
        if code != 0:
            mo.setResult('ok', 0)
            mo.setError(code, info)
        else:
            mo.setResult('ok', 1)
            mo.setResult('nickName', info)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    def _doChangeNameGet(self, userId, gameId, clientId):
        # SDK随机名称
        code, nickName = tyrpcsdk.getRandUniqueNickName()

        if code != 0:
            errMsg = '数据异常，请稍候重试' if code == 1 else nickName  # SDK的errMsg为空
            if _DEBUG:
                debug('doChangeNameGet error userId=', userId,
                      'gameId=', gameId, 'gameId=', clientId, 'sdkerror=', code, errMsg)
            return code, errMsg

        return 0, nickName
