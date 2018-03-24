# -*- coding: utf-8 -*-
'''
Created on 2016年8月1日

@author: yzx
'''

from freetime5.util import ftlog, fttime
from freetime5.util.ftmsg import MsgPack
from hall5.plugins.hallgamemanager._private import _dao
from hall5.plugins.hallgamemanager._private.iploc.gamelistipfilter import filtergamelist
from hall5.plugins.hallgamemanager._private.iploc.iploc import getIpLocation
from tuyoo5.core import tyrpcconn
from tuyoo5.core.tyconfig import TyCachedConfigByHall, TyCachedConfig
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game._private import _sessiondata as sessiondata

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass
'''
confKey = game5:<gameId>:gamemanager_configured:tc
confKey = game5:<gameId>:gamemanager_configured:vc
confKey = game5:<gameId>:gamemanager_location:tc
confKey = game5:<gameId>:gamemanager_plus:tc
confKey = game5:<gameId>:gamemanager_plus:vc
'''

gamemgr_cfg_conf = TyCachedConfigByHall('gamemanager_configured')
gamemgr_pls_conf = TyCachedConfigByHall('gamemanager_plus')
gamemgr_loc_conf = TyCachedConfig('gamemanager_location', HALL_GAMEID)

def _getAllGames(userId, intClientId, location):
    if _DEBUG:
        debug('_tygamelist._getAllGames IN->', userId, intClientId, location)

    cfg_nodes = []
    user_nodes = []
    inners = []
    plus_sign = 0
    gamelist = {'cfg_nodes': cfg_nodes, 'user_nodes': user_nodes, 'innerGames': inners, 'plus_sign': plus_sign}
    # 获取标准配置
    cfg_gameInfo = gamemgr_cfg_conf.getConfigByClientId(intClientId)
    if not cfg_gameInfo:
        ftlog.warn('_tygamemanager.getAllGames, then cfg_gameInfo not found ! userId=', userId, 'clientId=', intClientId)
        return gamelist

    _filterGameNodes(userId, intClientId, cfg_gameInfo.get('nodes', []), cfg_nodes)

    # 获取推荐配置
    pls_gameInfo = gamemgr_pls_conf.getConfigByClientId(intClientId)
    if not pls_gameInfo:
        ftlog.warn('_tygamemanager.getAllGames, then pls_gameInfo not found ! userId=', userId, 'clientId=', intClientId)
        return gamelist

    plus_sign = pls_gameInfo.get("plus_sign", 0)
    # 重新设置plus_sign值
    gamelist["plus_sign"] = plus_sign
    plus_nodes = []
    _filterGameNodes(userId, intClientId, pls_gameInfo.get('nodes', []), plus_nodes)

    isFirst = pluginCross.halldata.isFirstGamelist5(userId)  # 用户gamelist5数据库默认值0

    if plus_sign == 1 and not isFirst:
        # 第一次使用，生成初始的自定义配置
        plus_count = pls_gameInfo.get("plus_count", 0)
        loc_count = pls_gameInfo.get("loc_count", 0)

        if len(plus_nodes) >= plus_count:
            _ = plus_nodes[0:plus_count]
            user_nodes.extend(_)
        else:
            user_nodes.extend(plus_nodes)

        # 根据IP获取地方配置
        loc_nodes = _getlocBylocation(location)
        if loc_nodes and len(loc_nodes) > 0 and loc_count > 0:
            if len(loc_nodes) >= loc_count:
                _ = loc_nodes[0:loc_count]
                user_nodes.extend(_)
            else:
                user_nodes.extend(loc_nodes)

        gameIds = [x.get("id") for x in iter(user_nodes)]
        _addGames(userId, gameIds)
        pluginCross.halldata.changeFirstGamelist5(userId)  # 更改用户gamelist5状态值
    else:
        user_node_data = _dao.loadUserGamelistRecord(userId)
        user_nodes = [{"id": x} for x in iter(user_node_data)]
        # 过滤掉已添加的插件被运营取消
        if len(user_nodes) > 0:
            user_nodes = _filterOfflineGameNodes(userId, plus_nodes, user_nodes)
        # 重新设置user_nodes引用
        gamelist["user_nodes"] = user_nodes

    # mock 一个节点客户端显示添加按钮
    if plus_sign == 1:
        plus_info = pls_gameInfo.get("plusinfo", {})
        if "id" in plus_info:
            plus_node = {
                "id": plus_info.get("id")
            }
            user_nodes.append(plus_node)
        else:
            ftlog.warn('_tygamelist._getAllGames get plus_button_info none')

    gamelist = filtergamelist(gamelist, userId, intClientId)
    return gamelist


def _getlocBylocation(location):
    # loc_gameInfo = gamemgr_loc_conf.getTcConfig().get("templates")
    # loc_items = None
    # for _ in loc_gameInfo:
    #     if _.get("des") == location:
    #         loc_items = _.get("nodes")
    #         break
    return None

def _getExtendGames(userId, intClientId, location):
    """
    获取扩展位游戏列表.
    """
    nodes = []
    gameInfo = gamemgr_pls_conf.getConfigByClientId(intClientId)
    if not gameInfo:
        ftlog.warn('_tygamemanager._getListGames, then pls_gameInfo not found ! userId=', userId, 'clientId=',
                   intClientId)
        return nodes
    pls_gameInfo = gameInfo.get('nodes', [])
    loc_gameInfo = _getlocBylocation(location)
    if loc_gameInfo:
        pls_gameInfo.extend(loc_gameInfo)  # 合并推荐和地域游戏信息
    _filterGameNodes(userId, intClientId, pls_gameInfo, nodes)
    return nodes


def _getListGames(userId, intClientId, location):
    if _DEBUG:
        debug('_tygamelist._getListGames in->', userId, intClientId, location)
    nodes = _getExtendGames(userId,intClientId,location)
    todo_nodes = []
    user_nodes = []
    user_node_data = _dao.loadUserGamelistRecord(userId)
    for info in nodes:
        if info.get("id") not in user_node_data:
            todo_nodes.append(info)
        else:
            user_nodes.append(info)
    # 用户待添加游戏及已添加游戏列表
    gamelist = {'todo_nodes': todo_nodes, 'user_nodes': user_nodes}

    gamelist = filtergamelist(gamelist, userId, intClientId)
    return gamelist


def _addGames(userId, gameIds):
    if _DEBUG:
        debug('_tygamelist5.addGames IN->', userId, gameIds)

    now = fttime.getCurrentTimestamp()
    for idx, node in enumerate(gameIds):
        _dao.addUserGameListNode(userId, now+idx, node)  # 制造一点时间差形成先后顺序
    return 1

def _safeAddGames(userId, intClientId, gameIds, location):
    """
    安全添加用户自定义数据.
    客户端传来的添加项，校验实际存在后再入库.
    """
    # TODO 和 _filterGameNodes 合并
    if _DEBUG:
        debug('_tygamelist5._addSafeGames IN->', userId, intClientId, gameIds)
    nodes = _getExtendGames(userId, intClientId, location)
    now = fttime.getCurrentTimestamp()
    idx = 0
    for info in nodes:
        nodeId = info.get("id", "")
        if nodeId in gameIds:
            # 节点数据真实存在才进行添加
            _dao.addUserGameListNode(userId, now + idx, nodeId)  # 制造一点时间差形成先后顺序
            idx += 1
            gameIds.remove(nodeId)

    if len(gameIds) > 0:
        # 不安全的输入数据,记录下来
        ftlog.warn('_tygamemanager._addSafeGames, the node not found ! userId=', userId, 'clientId=',
                   intClientId, 'gameIds=', gameIds, 'nodes', nodes)
    return 1

def _delGames(userId, gameIds):
    if _DEBUG:
        debug('_tygamelist5.delGames IN->', userId, gameIds)
    for node in gameIds:
        _dao.delUserGameListNode(userId, node)
    return 1


def _filterGameNodes(userId, intClientId, nodeList, nodeIds):
    for n in nodeList:
        cids = n.get('conditions', [])
        if pluginCross.condition.checkConditions(HALL_GAMEID, userId, intClientId, cids, gameNone=n):
            is_recommend = n.get('is_recommend',0)
            sn = n.get('sn',[0,0])
            uiNode = {'id': n['id'],'is_recommend':is_recommend,'sn':sn}
            subNodeList = n.get('nodes', [])
            if subNodeList:
                subNodeIds = []
                _filterGameNodes(userId, intClientId, subNodeList, subNodeIds)
                uiNode['nodes'] = subNodeIds
            nodeIds.append(uiNode)
        else:
            if _DEBUG:
                debug('_tygamelist.getGamelist, user condition check false', n, userId, intClientId)


def _filterOfflineGameNodes(userId, plus_nodes, user_nodes):
    """
    过滤掉用户已经添加，但是下线的游戏插件.
    """
    to_del_node = []

    def is_plus_node(node):
        for item in plus_nodes:
            if item.get("id") == node.get("id"):
                return True
        to_del_node.append(node.get("id"))
        return False
    user_nodes = filter(is_plus_node, user_nodes)
    if len(to_del_node) > 0:
        if _DEBUG:
            debug('_tygamelist5._filterOfflineGameNodes IN->', userId, to_del_node)
        _delGames(userId, to_del_node)
    return user_nodes



def allHallGameManager(userId, intClientId, apiVersion):
    ipstr = sessiondata.getClientIp(userId)
    location = getIpLocation(ipstr)
    mo = MsgPack()
    mo.setCmd('hall_gamelist5')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('action', "all")
    mo.setResult('gameId', HALL_GAMEID)
    mo.setResult('intClientId', intClientId)
    mo.setResult('userId', userId)
    mo.setResult('gamelist', _getAllGames(userId, intClientId, location))
    tyrpcconn.sendToUser(userId, mo)

def getHallGameManager(userId, intClientId, apiVersion):
    ipstr = sessiondata.getClientIp(userId)
    location = getIpLocation(ipstr)
    mo = MsgPack()
    mo.setCmd('hall_gamelist5')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('action', "get")
    mo.setResult('gameId', HALL_GAMEID)
    mo.setResult('intClientId', intClientId)
    mo.setResult('userId', userId)
    mo.setResult('gamelist', _getListGames(userId, intClientId, location))
    tyrpcconn.sendToUser(userId, mo)


def addHallGameManager(userId, intClientId, apiVersion, gameIds):
    ipstr = sessiondata.getClientIp(userId)
    location = getIpLocation(ipstr)
    mo = MsgPack()
    mo.setCmd('hall_gamelist5')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('action', "add")
    mo.setResult('gameId', HALL_GAMEID)
    mo.setResult('intClientId', intClientId)
    mo.setResult('userId', userId)
    mo.setResult('gameIds', gameIds)
    code = _safeAddGames(userId, intClientId, gameIds, location)
    if code != 1:
        mo.setResult('ok', 0)
        mo.setError(code, "")
    else:
        mo.setResult('ok', 1)
    tyrpcconn.sendToUser(userId, mo)


def delHallGameManager(userId, intClientId, apiVersion, gameIds):
    mo = MsgPack()
    mo.setCmd('hall_gamelist5')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('action', "del")
    mo.setResult('gameId', HALL_GAMEID)
    mo.setResult('intClientId', intClientId)
    mo.setResult('userId', userId)
    code = _delGames(userId, gameIds)
    if code != 1:
        mo.setResult('ok', 0)
        mo.setError(code, "")
    else:
        mo.setResult('ok', 1)
    tyrpcconn.sendToUser(userId, mo)
