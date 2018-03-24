# -*- coding=utf-8 -*-
"""
@file  : _dao
@date  : 2016-12-02
@author: GongXiaobo
"""
from freetime5.twisted import ftcore, ftlock
from freetime5.util import ftcache, ftlog
from tuyoo5.core import tydao, tyglobal


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class DataSchemaRedPoint(tydao.DataSchemaHashSameKeys):
    DBNAME = 'user'
    MAINKEY = 'red5:{}:%s'.format(tyglobal.gameId())
    SUBVALDEF = tydao.DataAttrObjList('redpoint', [], 1024)
    MAX_DATA_LENGTH = 128


class DaoRedPoint(object):

    def __init__(self):
        self.updates = {}
        self.removes = {}
        self._flushTimer = None

    def updatePoints(self, userId, points):
        if _DEBUG:
            debug('DaoRedPoint.updatePoints', userId)
        # 记录变化的内容，定时，延迟写入数据库
        self.updates[userId] = points
        # 启动延迟写入
        self._startDelayFlushData()

    def removePoint(self, userId, pointId):
        if _DEBUG:
            debug('DaoRedPoint.removePoint', userId, pointId)
        # 记录变化的内容
        if not userId in self.removes:
            self.removes[userId] = []
        self.removes[userId].append(pointId)
        # 启动延迟写入
        self._startDelayFlushData()

    def _startDelayFlushData(self):
        # 启动延迟写入计时器
        if self._flushTimer is None:
            self._flushTimer = ftcore.runOnceDelay(3, self._delayFlushData)

    @ftlock.lockgroup('DaoRedPoint._delayFlushData')
    def _delayFlushData(self):
        # 延迟写入数据库
        if self._flushTimer:
            self._flushTimer.cancel()
            self._flushTimer = None

        updates = self.updates
        removes = self.removes
        self.updates = {}
        self.removes = {}
        if _DEBUG:
            debug('DaoRedPoint._delayFlushData IN', len(updates), len(removes))

        try:
            for userId, points in updates.iteritems():
                datas = {}
                for point in points.values():
                    if point._changed:
                        datas[point.moduleId] = point.encodeDbData()
                        point._changed = 0
                if datas:
                    DataSchemaRedPoint.HMSET(userId, datas)

            for userId, moduleIds in removes.iteritems():
                DataSchemaRedPoint.HDEL(userId, moduleIds)
        except:
            ftlog.error()

        if _DEBUG:
            debug('DaoRedPoint._delayFlushData OUT')

    @ftlock.lockargname('DaoRedPoint.loadAll', 'userId')
    def loadAll(self, userId, moduleIds):
        return self._loadAll(userId, moduleIds)

    @ftcache.lfu_cache(maxsize=1024, cache_key_args_index=1)
    def _loadAll(self, userId, moduleIds):
        if _DEBUG:
            debug('DaoRedPoint._loadAll IN', userId, moduleIds)
        points = {}
        datas = DataSchemaRedPoint.HGETALL(userId)
        for moduleId, data in datas.iteritems():
            if moduleId not in moduleIds:
                self.removePoint(userId, moduleId)
            else:
                rp = RedPoint(moduleId).decodeDbData(data)
                if rp:
                    points[rp.moduleId] = rp
        if _DEBUG:
            debug('DaoRedPoint._loadAll OUT', userId, points)
        return points


class RedPoint(object):

    STATUS_READ = 0  # 已读
    STATUS_UNREAD = 1  # 未读

    def __init__(self, moduleId):
        self._changed = 0  # 数据是否发送变化
        self.moduleId = moduleId  # 模块ID
        self.unReadCount = 0  # 未读数量
        self.itemDatas = {}  # key=itemId, val=unReadCount

    def encodeDbData(self):
        reads = []
        unreads = []
        for itemId, status in self.itemDatas.iteritems():
            if status == RedPoint.STATUS_UNREAD:
                unreads.append(itemId)
            else:
                reads.append(itemId)
        return [self.unReadCount, reads, unreads]

    def decodeDbData(self, data):
        try:
            self.unReadCount = data[0]
            for itemId in data[1]:
                self.itemDatas[itemId] = RedPoint.STATUS_READ
            for itemId in data[2]:
                self.itemDatas[itemId] = RedPoint.STATUS_UNREAD
            return self
        except:
            ftlog.error('RedPoint=', self, 'data=', data)
            return None
