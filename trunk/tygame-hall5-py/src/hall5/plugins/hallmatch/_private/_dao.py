# -*- coding=utf-8 -*-
"""
Created on 2017年10月23日10:31:44

@author: yzx
"""
from tuyoo5.core import tydao


def _filterAndGroupHistory(data):
    """
    过滤并按照游戏进行分组
    """
    groups = {}
    for item in data:
        _ = item.split("|")
        gameId = int(_[0])
        roomId = int(_[1])
        if gameId in groups:
            groups.get(gameId).append(roomId)
        else:
            groups[gameId] = [roomId]
    return [{"gameId": x, "roomList": groups.get(x)} for x in groups]

class DaoMatchHistory(tydao.DataSchemaList):
    MAINKEY = 'mhistory5:%s'
    DBNAME = 'user'


class DaoMatchSignin(tydao.DataSchemaSet):
    MAINKEY = 'usersignin5:%s'
    DBNAME = 'user'


def loadHistoryRecord(userId):
    """
    获取用户的比赛历史记录.

    返回15条历史记录。
    判断历史记录长度，大于50条清理成剩余15条。

    :param userId:
    :return:
    """
    data = DaoMatchHistory.LRANGE(userId, 0, 14)
    if data:
        total = DaoMatchHistory.LLEN(userId)
        if total > 50:
            DaoMatchHistory.LTRIM(userId, 0, 14)
        return _filterAndGroupHistory(data)
    return []


def loadSiginRecord(userId):
    """
    获取用户的比赛报名记录.

    :param userId:
    :return:
    """
    userMatchs = DaoMatchSignin.SMEMBERS(userId)
    if userMatchs:
        return _filterAndGroupHistory(userMatchs)
    return []



