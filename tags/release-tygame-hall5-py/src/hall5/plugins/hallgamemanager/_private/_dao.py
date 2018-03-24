# -*- coding=utf-8 -*-
"""
Created on 2017年11月02日10:14:41

@author: yzx
"""

from tuyoo5.core import tydao


class DaoGameList5Set(tydao.DataSchemaZset):
    """
    用户自定义gamelist5的存储实现.

    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'gamelist5:%s'
    DBNAME = 'user'


def loadUserGamelistRecord(userId):
    """
    获取用户的自定义gamelist5列表.
    """
    return DaoGameList5Set.ZRANGE(userId, 0, -1)


def addUserGameListNode(userId, timeScore, gameNode):
    """
    向用户的自定义gamelist5添加节点.
    """
    return DaoGameList5Set.ZADD(userId, timeScore, gameNode)


def delUserGameListNode(userId, gameNode):
    """
    删除用户的自定义gamelist5节点.
    """
    return DaoGameList5Set.ZREM(userId, gameNode)
