# -*- coding=utf-8 -*-
"""
Created on 2017年12月27日

@author: lixi
"""

from tuyoo5.core import tydao
from tuyoo5.core import tyglobal

class Daohall5share2(tydao.DataSchemaHashAttrs):
    """
    用户自定义hall5share2的存储实现.
    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'share2.status:{}:%s'.format(tyglobal.gameId())
    DBNAME = 'user'

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY

def getUserHall5Share2Status(userId, pointId):
    """
    获取用户的hall5share2status列表.
    """
    return Daohall5share2.HGET(userId, pointId)

def setUserHall5Share2Status(userId, pointId, jstr):
    """
    设置用户的hall5share2status列表.
    """
    return Daohall5share2.HSET(userId, pointId, jstr)



class DaoHall5ShareGetToken(tydao.DataSchemaString):
    """
    用户自定义hall5share2的存储实现.
    MAINKEY,数据键值
    user,决定数据存储的库
    """
    MAINKEY = 'shortUrl.x3me:token'
    DBNAME = 'mix'

    @classmethod
    def getMainKey(cls, cIndex, mainKeyExt=None):
        return cls.MAINKEY

def getUserHall5Token():
    """
    获取用户的hall5shareToken
    """
    return DaoHall5ShareGetToken.GET(0)

def setUserHall5Token(tokenStr):
    """
    设置用户的hall5shareToken
    """
    return DaoHall5ShareGetToken.SET(0, tokenStr)