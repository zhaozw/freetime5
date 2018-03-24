# -*- coding=utf-8 -*-
"""
@file  : _task
@date  : 2016-11-25
@author: GongXiaobo
"""

from tuyoo5.core import tydao
from tuyoo5.core import tyglobal
from tuyoo5.plugins.task import tytask


class DaoUserTask(tydao.DataSchemaHashSameKeys):
    DBNAME = 'user'
    MAINKEY = 'happybag:{}:%s'.format(tyglobal.gameId())
    SUBVALDEF = tydao.DataAttrStr('task', '', 128)
    MAX_DATA_LENGTH = 0  # 任务先不限制长度


class HallTaskDataDao(tytask.TYTaskDataDao):
    """
    启用缓存机制,详细说明参考TYItemDao
    """

    def __init__(self):
        pass

    def loadAll(self, userId):
        '''
        加载用户所有任务
        '''
        datas = DaoUserTask.HGETALL(userId)
        return datas

    def saveTask(self, userId, task):
        '''
        保存一个用户的task
        '''
        taskDataBytes = task.encodeToBytes()
        DaoUserTask.HSET(userId, task.taskId, taskDataBytes)

    def removeTask(self, userId, kindIds):
        '''
        删除一个用户的task
        '''
        DaoUserTask.HDEL(userId, kindIds)
