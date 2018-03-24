# -*- coding=utf-8 -*-
"""
@file  : _dao
@date  : 2016-12-02
@author: GongXiaobo
"""
import random

from freetime5.util import ftlog
from freetime5.util.ftcache import lfu_alive_cache
from hall5.plugins.hallexchange._private import _dao


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


def getItemCounts(itemIds):
    counts = []
    for itemId in itemIds:
        c = getItemExchangeCount(itemId)
        counts.append(c)
    return counts


def incrItemExchangeCount(itemId):
    # 实际数据操作
    _dao.incrItemExchangeCount(itemId)
    # 清除缓存
    getItemExchangeCount.clear_keys([itemId])
    # 再次加载
    getItemExchangeCount(itemId)


@lfu_alive_cache(maxsize=4096, cache_key_args_index=0, alive_second=60)
def getItemExchangeCount(itemId):
    '''
    变化不频繁，每分钟重新计算一次
    '''
    c = _dao.getItemExchangeCount(itemId)
    if c <= 1000:
        c = random.randint(1000, 20000)
        _dao.resetItemExchangeCount(itemId, c)
    return c
