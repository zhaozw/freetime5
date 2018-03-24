# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''
from freetime5.util import ftlog, ftstr
from freetime5.util import fttime
from hall5.entity.hallevent import HallUserEventLogin
from hall5.entity.hallevent import HallUserEventOffLine
from hall5.plugins.halldata._daohalldata import DaoGameDataHall
from hall5.plugins.halldata._daouserdata import DaoTableChip
from hall5.plugins.halldata._daouserdata import DaoUserData
from hall5.plugins.halldata._halldata import _HallPluginDataHall
from hall5.plugins.halldata._userdata import _HallPluginDataUser
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import HallKeys, ChipNotEnoughOpMode
from tuyoo5.game import tybireport


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginData(typlugin.TYPlugin, _HallPluginDataUser, _HallPluginDataHall):

    def destoryPlugin(self):
        '''
        当插件被动态卸载时，执行此方法，进行清理工作
        '''
        DaoUserData.finalize()
        DaoGameDataHall.finalize()
        DaoTableChip.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        DaoUserData.initialize()
        DaoGameDataHall.initialize()
        DaoTableChip.initialize()

    @typlugin.markPluginEntry(event=HallUserEventLogin, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onHallUserEventLogin(self, event):
        # 记录上线时间
        ct = fttime.formatTimeMs()
        DaoGameDataHall.HMSET(event.userId, {
            HallKeys.ATT_ALIVE_TIME: ct,
            HallKeys.ATT_AUTHOR_TIME: ct
        })
        # 登录天数加1
        if event.isDayfirst:
            DaoGameDataHall.HINCRBY(event.userId, HallKeys.ATT_LOGIN_DAYS, 1)
        # 登录次数加1
        DaoGameDataHall.HINCRBY(event.userId, HallKeys.ATT_LOGIN_SUM, 1)

    @typlugin.markPluginEntry(event=HallUserEventOffLine, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def on_user_logout(self, event):
        # 记录下线时间
        ct = fttime.formatTimeMs()
        DaoGameDataHall.HMSET(event.userId, {
            HallKeys.ATT_ALIVE_TIME: ct,
            HallKeys.ATT_OFFLINE_TIME: ct
        })

    def _moveHall51DataBack(self, userId, gameId, clientId):
        try:
            flag = DaoGameDataHall.HGET(userId, 'userChipMoveGame')
            ftlog.info('_moveHall51DataBack', userId, gameId, flag)
            if flag > 0:
                # 当前用户登录过HALL51
                chip, exp, charm, coupon = DaoGameDataHall.HMGET(userId, ['chip', 'exp', 'charm', 'coupon'])
                chip, exp, charm, coupon = ftstr.parseInts(chip, exp, charm, coupon)
                ftlog.info('_moveHall51DataBack data->', userId, gameId, chip, exp, charm, coupon)
                if charm > 0:
                    self.incrCharm(userId, charm)
                if exp > 0:
                    self.incrExp(userId, exp)
                if coupon > 0:
                    trueDelta, finalCount = self.incrCoupon(userId, gameId, coupon, ChipNotEnoughOpMode.NOOP, 'SYSTEM_REPAIR', 0)
                    ftlog.info('_moveHall51DataBack data coupon->', userId, gameId, coupon, trueDelta, finalCount)
                if chip > 0:
                    trueDelta, finalCount = self.incrChip(userId, gameId, chip, ChipNotEnoughOpMode.NOOP, 'SYSTEM_REPAIR', 0)
                    ftlog.info('_moveHall51DataBack data chip->', userId, gameId, chip, trueDelta, finalCount)
                DaoGameDataHall.HDEL(userId, ['chip', 'exp', 'charm', 'coupon', 'userChipMoveGame'])
                pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, 'chip')
        except:
            ftlog.error()

    @typlugin.markPluginEntry(export=1)
    def doBindUser(self, userId, gameId, intClientId):
        '''
        用户TCP连接建立，绑定用户，检查并建立用户的主游戏基础数据，并返回是否是新用户
        '''
        self._moveHall51DataBack(userId, gameId, intClientId)
        ret = DaoGameDataHall.checkAndInit(userId)
        if ret:
            tybireport.reportGameEvent('CREATE_GAME_DATA',
                                       userId,
                                       gameId,
                                       0, 0, 0, 0, 0, 0, [],
                                       intClientId, 0, 0)
        return ret
