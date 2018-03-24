# -*- coding: utf-8 -*-
'''
Created on 2016年5月1日

@author: zqh
'''
from freetime5.util import ftlog
from hall5.entity import hallchecker
from hall5.entity.hallevent import HallUserEventLogin
from hall5.plugins.halluser._private import _checker
from hall5.plugins.halluser._private import _user
from tuyoo5.core import tygame
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpcsdk
from tuyoo5.core import tyrpcgdss

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginUser(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginUser, self).__init__()
        self.checkBase = hallchecker.CHECK_BASE.clone()
        self.checkAuthor = hallchecker.CHECK_BASE.clone()
        self.checkUpdate = hallchecker.CHECK_BASE.clone()
        self.checkMyCard = hallchecker.CHECK_BASE.clone()
        self.checkAuthor.addCheckFun(_checker.check_authorCode)
        self.checkUpdate.addCheckFun(_checker.check_purl)
        self.checkUpdate.addCheckFun(_checker.check_sex)
        self.checkMyCard.addCheckFun(_checker.check_realName)
        self.checkMyCard.addCheckFun(_checker.check_idCardNum)

    @typlugin.markPluginEntry(cmd='bind_game5', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doBindGame(self, msg):
        '''
        获取游戏数据
        客户端第一次进入游戏时获取游戏数据
        同时可以进行一些游戏的初始化、每日登录等业务逻辑处理
        '''
        if _DEBUG:
            debug('doBindGame->', msg)
        mi = self.checkBase.check(msg)
        if _DEBUG:
            debug('doBindUser->', mi)
        if mi.error:
            return 0
        _user._sendGameDataResponse(mi.userId, mi.gameId, mi.clientId, mi.apiVersion)
        return 1

    @typlugin.markPluginEntry(cmd='bind_user5', act='', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doBindUser(self, msg):
        '''
        客户端的第一个命令响应
        CONN进程查询，用户上线处理
        客户端通知，用户登录处理，返回用户的基本数据信息及其他登录流程的必要信息
        '''
        if _DEBUG:
            debug('doBindUser->', msg)
        mi = self.checkAuthor.check(msg)
        # firstUserInfo = msg.getKeyInt('firstUserInfo')
        if _DEBUG:
            debug('doBindUser->', mi)
        if mi.error:
            return 0
        return _user.doBindUser(mi.userId, mi.gameId, mi.clientId, mi.authorCode, mi.apiVersion)

    @typlugin.markPluginEntry(event=HallUserEventLogin, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onHallUserEventLogin(self, event):
        # 异步延迟监听用户上线事件，即为bind_user的逻辑中，可以异步延迟处理的逻辑
        _user.doBindUserAsync(event.userId, event)

    @typlugin.markPluginEntry(cmd='user', act='heartbeat', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doUserHeartBeatOld(self, msg):
        '''
        客户端通知，用户心跳处理
        '''
        self.doUserHeartBeat(msg)
        return 1

    @typlugin.markPluginEntry(cmd='user5', act='heartbeat', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doUserHeartBeat(self, msg):
        '''
        客户端通知，用户心跳处理
        '''
        if _DEBUG:
            debug('doUserHeartBeat->', msg)
        mi = self.checkBase.check(msg)
        if mi.error:
            return 0
        _user.doUserHeartBeat(mi.userId, msg.getParamInt('must'), mi.clientId)
        return 1

    @typlugin.markPluginEntry(cmd='user5', act='connlost', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doUserOffline(self, msg):
        '''
        CONN进程查询，用户下线处理
        '''
        if _DEBUG:
            debug('doUserOffline->', msg)
        userId = msg.getParamInt('userId')
        if userId > 0:
            _user.doUserOffline(userId)
        return 1

    @typlugin.markPluginEntry(cmd='user_info5', act='', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doUserInfo(self, msg):
        """
        客户端查询用户账号数据，与bind_user中返回的账号数据响应一致，
        只是bind_user为客户端第一次进入当前游戏
        user_info为游戏中，账号数据发生变化时，重新请求账号数据内容
        """
        if _DEBUG:
            debug('doUserInfo->', msg)
        mi = self.checkBase.check(msg)
        if mi.error:
            return 0
        # 发送udata响应消息
        _user._sendUserInfoResponse(mi.userId, mi.gameId, mi.clientId, mi.apiVersion)
        return 1

    @typlugin.markPluginEntry(cmd='game_data5', act='', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doGameData(self, msg):
        """
        客户端查询游戏数据, 与bind_game响应一致，
        只是bind_game为客户端第一次进入当前游戏
        game_data为游戏中，游戏数据发生变化时，重新请求游戏数据内容
        """
        if _DEBUG:
            debug('doGameData->', msg)
        mi = self.checkBase.check(msg)
        if mi.error:
            return 0
        chip, coupon = _user._sendGameDataResponse(mi.userId, mi.gameId, mi.clientId, mi.apiVersion)
        # TODO 当客户端进入子游戏时，如果金币或奖券发生变化，那么会触发此命令，
        # TODO 由于现在的hall37的金币和奖券的添加删除方法没有发出事件，
        # TODO 那么在此处做一个事件补偿，触发 福袋 的任务系统进行任务刷新
        # TODO 当hall37完全消失时，去掉此2行代码即可
        typlugin.asyncTrigerEvent(tygame.ChipChangedEvent(mi.userId, mi.gameId, 0, chip))
        typlugin.asyncTrigerEvent(tygame.CouponChangedEvent(mi.userId, mi.gameId, 0, coupon))

    @typlugin.markPluginEntry(cmd='user5', act='setinfo', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doSetUserInfo(self, msg):
        """
        客户端更新用户信息，目前看只有sex更改
        """
        if _DEBUG:
            debug('doGameData->', msg)
        mi = self.checkUpdate.check(msg)
        if mi.error:
            return 0
        retCode = tyrpcsdk.setUserInfo(mi.userId, mi.sex, mi.purl)
        _user._sendSetUserInfoResponse(mi.userId, mi.gameId, mi.clientId, mi.apiVersion, retCode)
        return 1

    @typlugin.markPluginEntry(cmd='user5', act='verifyuseridcard', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doVerifyUserIdCard(self, msg):
        """
        验证客户端内嵌的身份信息验证
        """
        if _DEBUG:
            debug('doVerifyUserIdCard->', msg)
        mi = self.checkMyCard.check(msg)
        if mi.error:
            return 0

        retCode, retMsg = tyrpcgdss.queryCheckMyIdcard(mi.realName, mi.idCardNum)

        if retCode == 0:
            sdkRetCode = tyrpcsdk.setUserInfo(mi.userId, myCardNo=retMsg.get("myCardNo"),
                                           myRealName=retMsg.get("myRealName"),
                                           mySex=retMsg.get("mySex"),
                                           myBirth=retMsg.get("myBirth"),
                                           myProvince=retMsg.get("myProvince")
                                        )
            if sdkRetCode == 0:
                _user._sendUserQueryCardInfo(mi.userId, mi.gameId, mi.clientId, mi.apiVersion, sdkRetCode, "query user info ok!")
            else:
                _user._sendUserQueryCardInfo(mi.userId, mi.gameId, mi.clientId, mi.apiVersion, sdkRetCode, "set user info failed")
        else:
            _user._sendUserQueryCardInfo(mi.userId, mi.gameId, mi.clientId, mi.apiVersion, retCode, retMsg)
        return 1

