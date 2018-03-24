# -*- coding: utf-8 -*-

# import freetime.util.log as ftlog
# from hall.entity import hallvip
# from hall.entity.hallconf import HALL_GAMEID
# from poker.entity.dao import gamedata, sessiondata
# from hall.entity.iploc import iploc
# from poker.util import strutil
# from poker.entity.configure import configure, pokerconf

from freetime5.util import ftlog
from hall5.plugins.hallgamemanager._private.iploc import iploc
from tuyoo5.core import tyconfig
from tuyoo5.core import tyglobal
from tuyoo5.core.tyconfig import TyCachedConfig
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import HallKeys
from tuyoo5.core.tyrpchall import UserKeys
from tuyoo5.game._private import _sessiondata as sessiondata

_DEBUG = 1


if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

# 大丰收，跑狗，百人牛牛，斗牛，红黑大战，金三顺，中发白，欢乐小丑 ，三张牌

hallshare2_config = TyCachedConfig('gamelistipfilter5', tyglobal.gameId())

def _getVIpLevel(userId):
    vipLevel = pluginCross.hallvip.getVipInfo(userId).get('level') or 0
    return vipLevel

def _getPlayTimes(userId):
    # totalTime = gamedata.getGameAttrInt(userId, HALL_GAMEID, 'totaltime')
    totalTime = pluginCross.halldata.getHallDataList(userId, HallKeys.ATT_TOTAL_TIME)
    return totalTime

def isUser2018(userId):
    try:
        createTime = pluginCross.halldata.getUserDataList(userId, UserKeys.ATT_CREATE_TIME)
        if createTime and str(createTime).find('2018') == 0 :
            return 1
    except:
        ftlog.error()
    return 0

def _isPrefilterConditions(userId, clientId):
    # conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    conf = hallshare2_config.getZeroConfig()
    if not conf.get('enableIpCheck', 0):
        return 1

#     intClientId = pokerconf.clientIdToNumber(clientId)
#     if intClientId not in conf.get('filterClientIds', []):
#         return 1

    #优先过滤白名单
    if iploc.isFilterUser(userId):
        if _DEBUG:
            ftlog.debug('_isPrefilterConditions', userId, 'enableUserCheck !')
        return 1

    passHall = conf.get('passHall', [])
    if passHall:
        for ph in passHall:
            if clientId.find(ph) > 0:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, clientId, ph, 'passHall !')
                return 1

    filterHallSpecial = conf.get('filterHall_special', [])
    if filterHallSpecial:
        for ph in filterHallSpecial:
            if clientId.find(ph) > 0:
                #限制大厅的版本在3.9以上
                passClientVerSpecial = conf.get('passClientVer_special_game', 0)
                if passClientVerSpecial > 0:
                    # _, cver, _ = strutil.parseClientId(clientId)
                    _, cver, _ = tyconfig.parseClientId(clientId)
                    if cver < passClientVerSpecial:
                        if _DEBUG:
                            ftlog.debug('gamelistipfilter === filterHall_special ', userId, clientId, passClientVerSpecial, 'passClientVer_special_game !')
                        return 1
                if _DEBUG:
                    ftlog.debug('_isPrefilterConditions', userId, clientId, ph, 'filterHallSpecial !')
                return 0

    filterHall = conf.get('filterHall', [])
    if filterHall:
        for ph in filterHall:
            if clientId.find(ph) > 0:
                #限制大厅的版本在4.5以上
                passClientVer = conf.get('passClientVer', 0)
                if passClientVer > 0:
                    # _, cver, _ = strutil.parseClientId(clientId)
                    _, cver, _ = tyconfig.parseClientId(clientId)
                    if cver < passClientVer:
                        if _DEBUG:
                            ftlog.debug('gamelistipfilter === filterHall', userId, clientId, passClientVer, 'passClientVer !')
                        return 1
                if _DEBUG:
                    ftlog.debug('_isPrefilterConditions', userId, clientId, ph, 'filterHall !')
                return 0

    #other hall limit version 4.5
    passClientVer = conf.get('passClientVer', 0)
    if passClientVer > 0:
        # _, cver, _ = strutil.parseClientId(clientId)
        _, cver, _ = tyconfig.parseClientId(clientId)
        if cver < passClientVer:
            if _DEBUG:
                ftlog.debug('gamelistipfilter === other hall', userId, clientId, passClientVer, 'passClientVer !')
            return 1

    if _DEBUG:
        ftlog.debug('in _isPrefilterConditions filtergamelist go filter !', userId)
    return 0

def _isfilterConditions_group1(userId, clientId):
    # conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    conf = hallshare2_config.getZeroConfig()

    ipstr = sessiondata.getClientIp(userId)
    if not iploc.isBjSzIp(ipstr):
        if _DEBUG:
            ftlog.debug('_isfilterConditions_group1', userId, ipstr, 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group1_passVipLevel = conf.get('group1_passVipLevel', 0)
        if group1_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group1_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group1', userId, vipLevel, group1_passVipLevel, 'group1_passVipLevel !')
                adjustVIP = 1

        group1_passTotalPlayTime = conf.get('group1_passTotalPlayTime', 0)
        if group1_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group1_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group1_passTotalPlayTime, 'group1_passTotalPlayTime !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1
    else:
        if _DEBUG:
                ftlog.debug('_isfilterConditions_group1 is in beijing or shenzhe!! userId = ', userId , 'enableIpCheck !')
        return 0

def _isfilterConditions_group2(userId, clientId):
    # conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    conf = hallshare2_config.getZeroConfig()

    ipstr = sessiondata.getClientIp(userId)
    if not iploc.isBjSzIp(ipstr):
        if _DEBUG:
            ftlog.debug('_isfilterConditions_group2', userId, ipstr, 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group2_passVipLevel = conf.get('group2_passVipLevel', 0)
        if group2_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group2_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group2', userId, vipLevel, group2_passVipLevel, 'group2_passVipLevel !')
                adjustVIP = 1

        group2_passTotalPlayTime = conf.get('group2_passTotalPlayTime', 0)
        if group2_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group2_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group2_passTotalPlayTime, 'group2_passTotalPlayTime !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1
    else:
        if _DEBUG:
                ftlog.debug('_isfilterConditions_group2 is in beijing or shenzhe!! userId = ', userId , 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group2_passVipLevel = conf.get('group2_key_area_passVipLevel', 0)
        if group2_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group2_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group2', userId, vipLevel, group2_passVipLevel, 'group2_passVipLevel !')
                adjustVIP = 1

        group2_passTotalPlayTime = conf.get('group2_passTotalPlayTime', 0)
        if group2_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group2_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group2_passTotalPlayTime, 'group2_passTotalPlayTime !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1


def _isfilterConditions_group3(userId, clientId):
    # conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    conf = hallshare2_config.getZeroConfig()

    ipstr = sessiondata.getClientIp(userId)
    if not iploc.isBjSzIp(ipstr):
        if _DEBUG:
            ftlog.debug('_isfilterConditions_group3', userId, ipstr, 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group3_passVipLevel = conf.get('group3_passVipLevel', 0)
        if group3_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group3_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group3', userId, vipLevel, group3_passVipLevel, '_isfilterConditions_group3 !')
                adjustVIP = 1

        group3_passTotalPlayTime = conf.get('group3_passTotalPlayTime', 0)
        if group3_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group3_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group3_passTotalPlayTime, '_isfilterConditions_group3 !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1
    else:
        if _DEBUG:
                ftlog.debug('_isfilterConditions_group3 is in beijing or shenzhe!! userId = ', userId , 'enableIpCheck !')

        adjustVIP = 0
        adjustPlayTime = 0
        group3_passVipLevel = conf.get('group3_key_area_passVipLevel', 0)
        if group3_passVipLevel > 0:
            vipLevel = _getVIpLevel(userId)
            if vipLevel >= group3_passVipLevel:
                if _DEBUG:
                    ftlog.debug('_isfilterConditions_group3', userId, vipLevel, group3_passVipLevel, 'group3_passVipLevel !')
                adjustVIP = 1

        group3_passTotalPlayTime = conf.get('group3_key_area_passTotalPlayTime', 0)
        if group3_passTotalPlayTime > 0:
            totalTime = _getPlayTimes(userId)
            if totalTime >= group3_passTotalPlayTime:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, totalTime, group3_passTotalPlayTime, 'group3_key_area_passTotalPlayTime !')
                adjustPlayTime = 1

        return adjustVIP == 1 and adjustPlayTime == 1


def _isOutOfBeijingIp(userId, clientId):
    # conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    conf = hallshare2_config.getZeroConfig()
    if not conf.get('enableIpCheck', 0):
        return 1

#     intClientId = pokerconf.clientIdToNumber(clientId)
#     if intClientId not in conf.get('filterClientIds', []):
#         return 1

    passHall = conf.get('passHall', [])
    if passHall:
        for ph in passHall:
            if clientId.find(ph) > 0:
                if _DEBUG:
                    ftlog.debug('gamelistipfilter', userId, clientId, ph, 'passHall !')
                return 1

    passClientVer = conf.get('passClientVer', 0)
    if passClientVer > 0:
        # _, cver, _ = strutil.parseClientId(clientId)
        _, cver, _ = tyconfig.parseClientId(clientId)
        if cver < passClientVer:
            if _DEBUG:
                ftlog.debug('gamelistipfilter', userId, clientId, passClientVer, 'passClientVer !')
            return 1

    ipstr = sessiondata.getClientIp(userId)
    if not iploc.isBjSzIp(ipstr):
        if _DEBUG:
            ftlog.debug('gamelistipfilter', userId, ipstr, 'enableIpCheck !')
        return 1

    passTotalPlayTime = conf.get('passTotalPlayTime', 0)
    if passTotalPlayTime > 0:
        totalTime = _getPlayTimes(userId)
        if totalTime >= passTotalPlayTime:
            if _DEBUG:
                ftlog.debug('gamelistipfilter', userId, totalTime, passTotalPlayTime, 'passTotalPlayTime !')
            return 1
    
    passVipLevel = conf.get('passVipLevel', 0)
    if passVipLevel > 0:
        vipLevel = _getVIpLevel(userId)
        if vipLevel >= passVipLevel:
            if _DEBUG:
                ftlog.debug('gamelistipfilter', userId, vipLevel, passVipLevel, 'passVipLevel !')
            return 1

    if _DEBUG:
        ftlog.debug('filtergamelist go filter !', userId, ipstr)
    return 0


def filtergamelist(gamelist, userId, clientId):
    try:
        clientId_str = tyconfig.numberToClientId(clientId)
        return _filtergamelist(gamelist, userId, clientId_str)
    except:
        ftlog.error()
        return gamelist



def _filtergamelist(gamelist, userId, clientId):
    if _DEBUG:
        ftlog.debug('gamelist =====> ', userId, clientId, gamelist)

    # if _isOutOfBeijingIp(userId, clientId):
    #     return games, pages, innerGames
    # 优先过滤2018用户, 2018年用户不可见放在了第一优先级
    is2018 = isUser2018(userId)
    if _DEBUG:
        ftlog.debug('_filtergamelist is2018=', userId, is2018)

    if not is2018 :
        if _isPrefilterConditions(userId, clientId):
            return gamelist

    # conf = configure.getGameJson(HALL_GAMEID, 'gamelistipfilter', {}, configure.DEFAULT_CLIENT_ID)
    conf = hallshare2_config.getZeroConfig()
    # filterGameIds = conf.get('filterGameIds', [])

    filterGameIds = []
    
    if is2018 :
        group2018_games = conf.get('group2018_games', [])
        filterGameIds.extend(group2018_games)

    group1_games = conf.get('group1_games', [])
    if not _isfilterConditions_group1(userId, clientId):
        for game in group1_games:
            filterGameIds.append(game)


    group2_games = conf.get('group2_games', [])
    if not _isfilterConditions_group2(userId, clientId):
        for game in group2_games:
            filterGameIds.append(game)

    group3_games = conf.get('group3_games', [])
    if not _isfilterConditions_group3(userId, clientId):
        for game in group3_games:
            filterGameIds.append(game)

    if _DEBUG:
        ftlog.debug('filtergamelist rm filterGameIds =====> ', userId, filterGameIds)

    cfg_nodes = []
    user_nodes = []
    todo_nodes = []

    cfg_nodes = gamelist.get('cfg_nodes', [])
    user_nodes = gamelist.get('user_nodes', [])
    todo_nodes = gamelist.get('todo_nodes', [])


    for x in xrange(len(cfg_nodes) - 1, -1, -1):
        # gameId = int(cfg_nodes[x].get('id').split(':', 2)[1])
        game = cfg_nodes[x].get('id').split(':', 2)[1] if len(cfg_nodes[x].get('id').split(':', 2)[1]) <= 4 else '0'
        gameId = int(game)
        if gameId in filterGameIds:
            if _DEBUG:
                ftlog.debug('filtergamelist rm cfg_nodes', userId, gameId)
            del cfg_nodes[x]

    for x in xrange(len(user_nodes) - 1, -1, -1):
        game = user_nodes[x].get('id').split(':', 2)[1] if len(user_nodes[x].get('id').split(':', 2)[1]) <= 4 else '0'
        gameId = int(game)
        if gameId in filterGameIds:
            if _DEBUG:
                ftlog.debug('filtergamelist rm user_nodes', userId, gameId)
            del user_nodes[x]

    for x in xrange(len(todo_nodes) - 1, -1, -1):
        # gameId = int(todo_nodes[x].get('id').split(':', 2)[1])
        game = todo_nodes[x].get('id').split(':', 2)[1] if len(todo_nodes[x].get('id').split(':', 2)[1]) <= 4 else '0'
        gameId = int(game)
        if gameId in filterGameIds:
            if _DEBUG:
                ftlog.debug('filtergamelist rm todo_nodes', userId, gameId)
            del todo_nodes[x]

    if _DEBUG:
        ftlog.debug('OUT@@@@ return gamelist = ', userId, gameId, gamelist)

    return gamelist
