# -*- coding=utf-8 -*-
"""
@file  : _dao
@date  : 2016-12-02
@author: GongXiaobo
"""
from freetime5.util import fttime, ftlog
from freetime5.util.ftcache import lfu_alive_cache
from hall5.entity import hallconf
from tuyoo5.core import tyconfig
from tuyoo5.core import tyglobal
from tuyoo5.core.tyconfig import TyCachedConfig


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

MAINCONF = None
SUBCONFS = {}
PRODUCT_MAP = {}

def reloadConfig():
    if _DEBUG:
        debug('hallexchange.reloadConfig in')
    mainconf = TyCachedConfig('exchange', tyglobal.gameId())
    extabs = mainconf.getScConfig().get('extabs', {})
    if _DEBUG:
        debug('hallexchange.reloadConfig mainconf=', mainconf)
    names = set()
    for _, tab in extabs.iteritems():
        names.add(tab['name'])
    subconfs = {}
    product_map = {}
    for name in names:
        subconfs[name] = TyCachedConfig('exchange:%s' % (name), tyglobal.gameId())

        #add product_map info added by lixi
        if subconfs[name]:
            confs = subconfs[name].getScConfig().get('exitems', {})
            for key, conf in confs.items():
                if key:
                    product_map[key] = confs[key]['productId']
                    if _DEBUG:
                        debug('hallexchange _private _conf reloadConfig %s', conf)
                else:
                    if _DEBUG:
                        debug('hallexchange _private _conf reloadConfig %s', conf)
    
    global MAINCONF, SUBCONFS, PRODUCT_MAP
    MAINCONF = mainconf
    SUBCONFS = subconfs
    PRODUCT_MAP = product_map
    # 清理缓存
    getExchangeQueryUiTabs.clear()
    _getExchangeQueryUiItems.clear()
    if _DEBUG:
        debug('hallexchange.reloadConfig out')


@lfu_alive_cache(maxsize=1024, cache_key_args_index=0, alive_second=60)
def getExchangeQueryUiTabs(clientId):
    '''
    变化不频繁，每分钟重新计算一次
    '''
    if _DEBUG:
        debug('getExchangeQueryUiTabs', type(clientId), clientId)
    bannerIds = []
    tabIds = []
    confs = MAINCONF.getConfigByClientId(clientId)
    if _DEBUG:
        debug('getExchangeQueryUiTabs', clientId, confs)
    if confs:
        bannerIds = hallconf.filterStartStopTime(confs['exbanners'], MAINCONF, 'exbanners')
        tabIds = hallconf.filterStartStopTime(confs['extabs'], MAINCONF, 'extabs')
    if _DEBUG:
        debug('getExchangeQueryUiTabs', clientId, bannerIds, tabIds)
    return bannerIds, tabIds


def getExchangeQueryUiItems(tabName, pageNum, clientId):
    if _DEBUG:
        debug('getExchangeQueryUiItems', tabName, pageNum, clientId)
    clientId = tyconfig.clientIdToNumber(clientId)
    items = _getExchangeQueryUiItems('%s:%s' % (tabName, clientId))
    pagesize = MAINCONF.getScConfig().get('pagesize', 20)
    index = pageNum * pagesize
    page = items[index: index + pagesize]
    if _DEBUG:
        debug('getExchangeQueryUiItems', tabName, pageNum, clientId, page)
    return page


@lfu_alive_cache(maxsize=4096, cache_key_args_index=0, alive_second=60)
def _getExchangeQueryUiItems(key):
    '''
    变化不频繁，每分钟重新计算一次
    '''
    if _DEBUG:
        debug('_getExchangeQueryUiItems', key)
    itemIds = []
    tks = key.split(':')
    tabName, clientId = tks[0], int(tks[1])
    tabConf = SUBCONFS.get(tabName, None)
    if tabConf:
        confs = tabConf.getConfigByClientId(clientId)
        if _DEBUG:
            debug('_getExchangeQueryUiItems ! tabName=', tabName, 'clientId=', clientId, 'confs=', confs)
        if confs:
            itemIds = hallconf.filterStartStopTime(confs['exitems'], tabConf, 'exitems')
        else:
            if _DEBUG:
                debug('_getExchangeQueryUiItems not config ! tabName=', tabName, 'clientId=', clientId)
    else:
        if _DEBUG:
            debug('_getExchangeQueryUiItems not config ! tabName=', tabName)
    if _DEBUG:
        debug('_getExchangeQueryUiItems', key, itemIds)
    return itemIds


def getItemInfo(tabName, itemId):
    if _DEBUG:
        debug('getItemInfo', tabName, itemId)
    info = None
    tabConf = SUBCONFS.get(tabName, None)
    if tabConf:
        conf = tabConf.getScConfig().get('exitems', {}).get(itemId)
        if conf:
            ct = fttime.formatTimeSecond()
            startTime = conf['startTime']
            endTime = conf['endTime']
            if ct < startTime or ct > endTime:
                info = None
            else:
                info  = conf
                if _DEBUG:
                    debug('getItemInfo item timeout', tabName, itemId, ct, conf)
        else:
            if _DEBUG:
                debug('getItemInfo item notfound', tabName, itemId, tabConf.getScConfig())
    else:
        if _DEBUG:
            debug('getItemInfo tabName notfound', tabName, itemId, SUBCONFS.keys())

    if _DEBUG:
        debug('getItemInfo', tabName, itemId, info)
    return info
