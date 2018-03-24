# -*- coding: utf-8 -*-
'''
Created on 2016年8月1日

@author: zqh
'''
from freetime5.util import ftlog
from tuyoo5.core.tyconfig import TyCachedConfigByHall
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.core.typlugin import pluginCross


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

'''
confKey = game5:<gameId>:gamelist:sc
confKey = game5:<gameId>:gamelist:tc
confKey = game5:<gameId>:gamelist:vc
'''

gamelistconf = TyCachedConfigByHall('gamelist')


def getUiInfo(userId, intClientId, nowdate):
    if _DEBUG:
        debug('_tygamelist.getUiInfo IN->', userId, intClientId, nowdate)

    nodes = []
    inners = []
    gamelist = {'nodes': nodes, 'innerGames': inners}

    gameInfo = gamelistconf.getConfigByClientId(intClientId)
    if not gameInfo:
        ftlog.warn('_tygamelist.getUiInfo, then config not found ! userId=', userId, 'clientId=', intClientId)
        return gamelist

    _filterGameNodes(userId, intClientId, gameInfo.get('innerGames', []), inners)
    _filterGameNodes(userId, intClientId, gameInfo.get('nodes', []), nodes)

    if _DEBUG:
        debug('_tygamelist.getUiInfo OUT->', userId, gamelist)
    return gamelist


def _filterGameNodes(userId, intClientId, nodeList, nodeIds):
    for n in nodeList:
        cids = n.get('conditions', [])
        if pluginCross.condition.checkConditions(HALL_GAMEID, userId, intClientId, cids, gameNone=n):
            uiNode = {'id': n['id']}
            subNodeList = n.get('nodes', [])
            if subNodeList:
                subNodeIds = []
                _filterGameNodes(userId, intClientId, subNodeList, subNodeIds)
                uiNode['nodes'] = subNodeIds
            nodeIds.append(uiNode)
        else:
            if _DEBUG:
                debug('_tygamelist.getUiInfo, user condition check false', n, userId, intClientId)
