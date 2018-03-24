# -*- coding=utf-8 -*-
"""
@file  : _dao
@date  : 2016-12-02
@author: GongXiaobo
"""

from freetime5.util import ftlog
from hall5.plugins.hallredpoint._private import _dao


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

MODULEIDS = {  # 有效的 模块ID, 避免不在控制内的数据，造成整体数据过于庞大
    'item5',
    'happybag5',
    'custom5',
    'notice5',
}


def check_moduleId(msg, result, name):
    val = msg.getParamStr(name)
    if not val:
        return None, 'params %s=[%s] error !!' % (name, val)
    return val, None


def check_itemId(msg, result, name):
    val = msg.getParamStr(name)
    if not val:
        return None, 'params %s=[%s] error !!' % (name, val)
    return val, None


class PointSystem(object):

    '''
    为啥此类不需要锁定？因为dao为延迟写入，读取锁定，因此此类中没有IO实际调用，均为同步方法，即没有tasklet切换过程
    '''

    def __init__(self, dao):
        self.points = {}
        self.dao = dao

    def loadUserPoints(self, userId):
        '''
        取得所有的红点数据
        返回 dict，key=moduleId value=RedPoint
        '''
        return self.dao.loadAll(userId, MODULEIDS)

    def loadUserPointByModuleId(self, userId, moduleId):
        points = self.loadUserPoints(userId)
        rp = points.get(moduleId)
        if not rp:
            rp = _dao.RedPoint(moduleId)
            rp._changed = 1
            points[rp.moduleId] = rp
            self.dao.updatePoints(userId, points)
        return points, rp

    def setModuleUnRead(self, userId, moduleId):
        changed = 0
        points, rp = self.loadUserPointByModuleId(userId, moduleId)
        if rp.unReadCount != _dao.RedPoint.STATUS_UNREAD:
            rp.unReadCount = _dao.RedPoint.STATUS_UNREAD
            rp._changed = 1
            changed = 1
        else:
            if _DEBUG:
                debug('setModuleUnRead itemId already unread !', moduleId, rp.itemDatas)
        if changed :
            self.dao.updatePoints(userId, points)
        return changed

    def setModuleRead(self, userId, moduleId):
        changed = 0
        points, rp = self.loadUserPointByModuleId(userId, moduleId)
        if rp.unReadCount != _dao.RedPoint.STATUS_READ:
            rp.unReadCount = _dao.RedPoint.STATUS_READ
            rp._changed = 1
            changed = 1
        else:
            if _DEBUG:
                debug('setModuleRead itemId already read !', moduleId, rp.itemDatas)
        if changed :
            self.dao.updatePoints(userId, points)
        return changed

    def getNoticePerlifeInfo(self, userId, moduleId, noticeid):
        _points, rp = self.loadUserPointByModuleId(userId, moduleId)
        for itemId in rp.itemDatas.keys():
            if itemId == noticeid:
                return 1
        return 0


    def resetItemIds(self, userId, moduleId, totalItemIds, defaultIsRead=0):
        points, rp = self.loadUserPointByModuleId(userId, moduleId)
        changed = 0
        # 删除不在totalItemIds中的数据
        for itemId in rp.itemDatas.keys()[:]:
            if not itemId in totalItemIds:
                del rp.itemDatas[itemId]
                rp._changed = 1
                changed = 1
                if _DEBUG:
                    debug('resetItemIds remove old itemId !', moduleId, itemId)

        # 添加itemDatas不存在的数据
        defaultIsRead = defaultIsRead if defaultIsRead == _dao.RedPoint.STATUS_READ else _dao.RedPoint.STATUS_UNREAD
        for itemId in totalItemIds:
            if not itemId in rp.itemDatas:
                rp.itemDatas[itemId] = defaultIsRead
                rp._changed = 1
                changed = 1
                if _DEBUG:
                    debug('resetItemIds add new itemId !', moduleId, itemId)

        if changed:
            self.dao.updatePoints(userId, points)
        return changed

    def setItemUnRead(self, userId, moduleId, unReadItemIds, needAdd):
        changed = 0
        points, rp = self.loadUserPointByModuleId(userId, moduleId)
        for itemId in unReadItemIds:
            if itemId in rp.itemDatas:
                status = rp.itemDatas[itemId]
                if status != _dao.RedPoint.STATUS_UNREAD:
                    rp.itemDatas[itemId] = _dao.RedPoint.STATUS_UNREAD
                    rp._changed = 1
                    changed = 1
                    if _DEBUG:
                        debug('setItemUnRead itemId change to unread !', moduleId, itemId, rp.itemDatas)
                else:
                    if _DEBUG:
                        debug('setItemUnRead itemId already unread !', moduleId, itemId, rp.itemDatas)
            else:
                if needAdd:
                    rp.itemDatas[itemId] = _dao.RedPoint.STATUS_UNREAD
                    rp._changed = 1
                    changed = 1
                    if _DEBUG:
                        debug('setItemUnRead itemId add to unread !', moduleId, itemId, rp.itemDatas)
                else:
                    if _DEBUG:
                        debug('setItemUnRead itemId not add !', moduleId, itemId, rp.itemDatas)
        if changed:
            self.dao.updatePoints(userId, points)
        return changed

    def removeItemIds(self, userId, moduleId, removeItemIds):
        changed = 0
        points, rp = self.loadUserPointByModuleId(userId, moduleId)
        for itemId in removeItemIds:
            if itemId in rp.itemDatas:
                del rp.itemDatas[itemId]
                rp._changed = 1
                changed = 1
            else:
                if _DEBUG:
                    debug('removeItemIds itemId not found !', moduleId, itemId, rp.itemDatas)

        if changed:
            self.dao.updatePoints(userId, points)
        return changed

    def readPoint(self, userId, moduleId, itemId):
        changed = 0
        points, rp = self.loadUserPointByModuleId(userId, moduleId)
        found = 1 if itemId in rp.itemDatas else 0
        if found == 0:
            # 有些时候，传递的是数字有时候传字符串
            try:
                intItemId = int(itemId)
                if intItemId in rp.itemDatas:
                    itemId = intItemId
                    found = 1
            except:
                pass

        if found:
            if rp.itemDatas[itemId] != _dao.RedPoint.STATUS_READ:
                rp.itemDatas[itemId] = _dao.RedPoint.STATUS_READ
                rp._changed = 1
                changed = 1
                self.dao.updatePoints(userId, points)
            else:
                if _DEBUG:
                    debug('readPoint itemId already read !', moduleId, itemId, rp.itemDatas)
        else:
            if _DEBUG:
                debug('readPoint itemId not found !', moduleId, itemId, rp.itemDatas)
        return changed

    def _toUiDict(self, rp):
        data = []
        count = 0
        if rp.itemDatas:
            for itemId, status in rp.itemDatas.iteritems():
                if status == _dao.RedPoint.STATUS_UNREAD:
                    count += 1
                    data.append(itemId)
        else:
            count = rp.unReadCount

        result = {'count': count}
        if data:
            result['items'] = data
        return {rp.moduleId: result}

    def encodeRedPointUiInfo(self, userId):
        datas = {}
        points = self.loadUserPoints(userId)
        for rp in points.itervalues():
            datas.update(self._toUiDict(rp))
        return datas
