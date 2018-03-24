# -*- coding: utf-8 -*-
'''
Created on 2016年5月1日

@author: zqh
'''
from freetime5._tyserver._entity import ftglobal
from freetime5.twisted.ftlock import lockargname
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from hall5.entity.hallevent import HallUserEventLogin
from hall5.entity.hallevent import HallUserEventOffLine
from tuyoo5.core import tyrpcconn, typlugin, tyconfig
from tuyoo5.core import tyrpcsdk
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import UserKeys
from tuyoo5.game import tybireport
from tuyoo5.game import tysessiondata
from tuyoo5.core.tyrpchall import ChipNotEnoughOpMode
from tuyoo5.core import tyglobal

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


USERATTS = [  # user_info 发送的数据字段列表
    UserKeys.ATT_NAME,
    UserKeys.ATT_SEX,
    UserKeys.ATT_IS_BIND,
    UserKeys.ATT_PHONE_NUMBER,
    UserKeys.ATT_BIND_MOBILE,
    UserKeys.ATT_PURL,
    UserKeys.ATT_DIAMOND,
    UserKeys.ATT_IDCARDNO,
    UserKeys.ATT_MY_REAL_CARD_NO,
    UserKeys.ATT_MY_REAL_NAME
]

GAMEATTS = [  # game_data 发送的数据字段列表
    UserKeys.ATT_CHARM,
    UserKeys.ATT_CHIP,
    UserKeys.ATT_EXP,
    UserKeys.ATT_COUPON,
]


@lockargname('hall5.offline', 'userId')
def doUserOffline(userId):
    # 同步触发登陆事件
    # halldata 基础大厅game数据处理，记录离线时间点
    typlugin.syncTrigerEvent(HallUserEventOffLine(userId))


@lockargname('hall5.heart', 'userId')
def doUserHeartBeat(userId, must, clientId):
    # 记录活动时间
    pluginCross.halldata.userAliveTime(userId)


def _sendSetUserInfoResponse(userId, gameId, intClientId, apiVersion, retCode):
    mo = MsgPack()
    mo.setCmd('user5')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('action', 'setinfo')
    if retCode == 0:
        mo.setResult('ok', 1)
    else:
        mo.setError(1, '设置失败')

    tyrpcconn.sendToUser(userId, mo)

    if retCode == 0:
        _sendUserInfoResponse(userId, gameId, intClientId, apiVersion)


def _sendUserInfoResponse(userId, gameId, intClientId, apiVersion):
    '''
    仅发送user_info命令, USER的主账户信息和游戏账户信息至客户端
    '''
    udatas = pluginCross.halldata.getUserDataDict(userId, USERATTS)
    mo = MsgPack()
    mo.setCmd('user_info5')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('intClientId', intClientId)
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('udata', udatas)
    tyrpcconn.sendToUser(userId, mo)


def _sendGameDataResponse(userId, gameId, intClientId, apiVersion):
    '''
    仅发送game_data命令, USER的大厅游戏数据至客户端
    '''
    gdatas = pluginCross.halldata.getUserDataDict(userId, GAMEATTS)
    gdatas['vipInfo'] = pluginCross.hallvip.getVipInfo(userId)
    mo = MsgPack()
    mo.setCmd('game_data5')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('intClientId', intClientId)
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('gdata', gdatas)
    tyrpcconn.sendToUser(userId, mo)
    return gdatas[UserKeys.ATT_CHIP], gdatas[UserKeys.ATT_COUPON]


def _sendUserGotoTable(userId, gameId, intClientId, apiVersion, locInfoList):
    mo = MsgPack()
    mo.setCmd('goto_table5')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('intClientId', intClientId)
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('locs', locInfoList)
    tyrpcconn.sendToUser(userId, mo)

def _sendUserQueryCardInfo(userId, gameId, intClientId, apiVersion, is_verify, ret_msg):
    mo = MsgPack()
    mo.setCmd('user_cardInfo')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('intClientId', intClientId)
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    mo.setResult('is_verify', is_verify)
    mo.setResult('ret_msg', ret_msg)
    tyrpcconn.sendToUser(userId, mo)

def _updateBiggestHallVersion(userId, gameId, clientId):
        '''
        记录更新该用户最高的版本号
        '''
        if gameId != tyglobal.gameId():
            return
        clientId_str = tyconfig.numberToClientId(clientId)
        _, clientVer, _ = tyconfig.parseClientId(clientId_str)
        if not clientVer:
            return
        bVer = 1.0
        biggestClientIdStr = pluginCross.halldata.getBiggestHallVersion(userId)
        if biggestClientIdStr:
            bVer = float(biggestClientIdStr)

        if clientVer > bVer:
            pluginCross.halldata.setBiggestHallVersion(userId, str(clientVer))
            ftlog.debug('update user biggest hallVersion:', clientVer)

@lockargname('hall5.binduser', 'userId')
def doBindUser(userId, gameId, intClientId, authorCode, apiVersion):
    '''
    TCP上第一个消息
    '''
    # 账号登录校验
    datas = tyrpcsdk.verifyAccount(userId, authorCode)
    if not datas:
        tyrpcconn.forceUserLogOut(userId, ftglobal.ERROR_SYS_LOGOUT_DATASWAP_ERROR)
        return 'tyrpcsdk.verifyAccount false'

    # 更新当前的session信息
    tysessiondata.updateSession(userId, gameId, datas['devId'],
                                datas['city_code'], datas['city_name'],
                                datas['ip'], intClientId)

    # 登录游戏处理
    isNewUser = pluginCross.halldata.doBindUser(userId, gameId, intClientId)
    if _DEBUG:
        debug('isNewUser->', userId, isNewUser)

    # 发送界面显示信息
    clientVer = tyconfig.getClientIdVer(intClientId)

    #增加升级版本到5.11奖励的内容
    if clientVer < 5.11:
        pluginCross.halldata.setLoginBeforeVersion511flag(userId)

    is_update = pluginCross.halldata.getUpdateToVersion511flag(userId)
    is_login_befor_511 = pluginCross.halldata.getLoginBeforeVersion511flag(userId)

    if not is_update and is_login_befor_511 and clientVer == 5.11:
            #chip_num = pluginCross.halldata.getUserDataList(userId, UserKeys.ATT_CHIP)
            pluginCross.halldata.incrChip(userId, gameId, 20000, ChipNotEnoughOpMode.NOOP, 'USER_UPDATE_511_REWARD', 0)
            pluginCross.halldata.setUpdateToVersion511flag(userId)

    #更新该用户最高的版本号
    _updateBiggestHallVersion(userId, gameId, intClientId)

    # 发送udata响应消息
    _sendUserInfoResponse(userId, gameId, intClientId, apiVersion)

    # 发送gdata响应消息
    _sendGameDataResponse(userId, gameId, intClientId, apiVersion)


    if _DEBUG:
        debug('clientVer->', userId, intClientId, clientVer)

    if clientVer < 5.11:
        pluginCross.hallui.sendHallUiGameList(userId, intClientId, apiVersion)
    else:
        # 发送新gamelist5
        pluginCross.hallgamemanager.sendAllHallGameManager(userId, intClientId, apiVersion)

    # 异步触发登陆事件
    # halluser 登录后处理，断线重连、首日登录、初始金币再次判定、日志输出等
    # halldata 基础大厅game数据处理，登录天数、登录次数、游戏时长、在线时间点等
    # hallitem 道具系统初始化、用户道具检查，自动更新用户道具的过期时间、多道具合并等
    evt = HallUserEventLogin(userId, isNewUser, 0, 0, intClientId)
    evt.apiVersion = apiVersion
    typlugin.asyncTrigerEvent(evt)
    return 1


@lockargname('hall5.binduserasync', 'userId')
def doBindUserAsync(userId, event):

    userId = event.userId
    gameId = event.gameId
    intClientId = event.intClientId
    apiVersion = event.apiVersion

    if _DEBUG:
        debug('doBindUserAsync->', userId, gameId, intClientId, apiVersion)

    if event.isCreate:
        # 新用户肯定没有断线重连信息和数据升级要求
        locInfoList, deltaChips = [], 0
    else:
        # 断线重连机制处理
        locInfoList, deltaChips = pluginCross.hallonline.doBindUser(userId, gameId, intClientId)

    # 发送新用户初始引导动画, 为避免再isNewUser时发送启动资金失败，追加chip为0的判定再次发放
    if _DEBUG:
        debug('doBindUserAsync->', userId, 'deltaChips=', deltaChips, 'locInfoList=', locInfoList)

    # 发送拉回牌桌的命令
    isReconnect = 0
    if locInfoList:
        isReconnect = 1
        _sendUserGotoTable(userId, gameId, intClientId, apiVersion, locInfoList)
    else:
        # 不需要拉回牌桌时，发一个空的locs，便于前端处理断线重连逻辑
        _sendUserGotoTable(userId, gameId, intClientId, apiVersion, [])

    event.isReconnect = isReconnect

    # 当日首次登陆处理
    event.isDayfirst = pluginCross.hallday1st.doBindUser(userId, intClientId)

    if _DEBUG:
        debug('doBindUserAsync->', userId, 'isDayfirst=', event.isDayfirst, 'isReconnect=', event.isReconnect)

    # BI日志统计
    tybireport.userBindUser(gameId, userId, intClientId)
    tybireport.reportGameEvent('BIND_USER', userId, gameId, 0, 0, 0, 0, 0, 0, [], intClientId)

#     # 异步触发HallUserEventOnLine处理
#     evt = HallUserEventOnLine(userId, isNewUser, isDayFirst, isReconnect, intClientId)
#     typlugin.asyncTrigerEvent(evt)

    return 1
