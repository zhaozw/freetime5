# -*- coding: utf-8 -*-
'''
Created on 2016年10月26日

@author: zqh
'''
from freetime5.util import ftlog
from freetime5.util import fttime
from hall5.entity.hallevent import HallUserEventLogin
from tuyoo5.core import tyconfig
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.plugins.item import itemsys
from tuyoo5.plugins.item.itemexceptions import TYItemConfException
from hall5.plugins.hallitem._private.itemhelper import ItemHelper


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


def _onUserLogin(gameId, userId, clientId, isCreate, isDayfirst):
    if _DEBUG:
        debug('item.onUserLogin->', gameId, userId, clientId, isCreate, isDayfirst)
    timestamp = fttime.getCurrentTimestamp()
    userAssets = itemsys.itemSystem.loadUserAssets(userId)
    userBag = userAssets.getUserBag()
    if isCreate:
        _initUserBag(gameId, userId, clientId, userBag)
    userBag.processWhenUserLogin(gameId, clientId, isDayfirst, timestamp)

    ItemHelper.resetHallItemRed(userId)


def _initUserBag(gameId, userId, clientId, userBag):
    initItems = _getInitItemsByClientId(clientId) or []
    timestamp = fttime.getCurrentTimestamp()
    for itemKind, count in initItems:
        userBag.addItemUnitsByKind(gameId, itemKind, count, timestamp, 0, 'USER_CREATE', 0)
    ftlog.info('hallitem._initUserBag addItemUnitsByKind gameId=', gameId,
               'userId=', userId,
               'initItems=', [(k.kindId, c) for k, c in initItems])
    return userBag


def _getInitItemsByClientId(clientId):
    datas = tyconfig.getTcContentByGameId('newuser', None, HALL_GAMEID, clientId, None)
    ret = []
    for d in datas['items']:
        itemKindId = d.get('itemKindId')
        itemKind = itemsys.itemSystem.findItemKind(itemKindId)
        if not itemKind:
            raise TYItemConfException(d, 'Not found itemKindId %s for initItems' % itemKindId)
        count = d.get('count')
        if not isinstance(count, int) or count <= 0:
            raise TYItemConfException(d, 'InitItem.count must int > 0')
        ret.append((itemKind, count))
    return ret


class HallPluginItemEvent(object):

    @typlugin.markPluginEntry(event=HallUserEventLogin, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def on_user_login(self, event):
        if not event.isReconnect and event.isDayfirst:
            _onUserLogin(event.gameId, event.userId, event.intClientId, event.isCreate, event.isDayfirst)
