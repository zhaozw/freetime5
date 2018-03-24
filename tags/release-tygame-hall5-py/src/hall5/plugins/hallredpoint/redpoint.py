# -*- coding=utf-8 -*-

from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.entity.hallevent import HallUserEventLogin
from hall5.plugins.hallredpoint._private import _dao, _point
from tuyoo5.core import tyglobal, tyrpcconn, tychecker
from tuyoo5.core import typlugin
from tuyoo5.core.typlugin import hallRpcOne, pluginCross


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginRedPoint(typlugin.TYPlugin):
    '''
    界面使用的小红点的控制
    支持1级小红点：例如：客服n个未读，未读内容，未知
    支持2级小红点：例如：福袋n个未读，每个未读的id列表，详细控制到每个2级子项目
    如果需要3级及以上怎么吧？不支持，3级以上的由业务模块控制第3级的状态
        例如：公告，如果需要3级，那么1级和2级可以使用此模块控制，3级未读列表由具体的公告活动控制，
            3级项目都读取后通知本模块进行更新一个项目的已读取标记
    '''

    def __init__(self):
        super(HallPluginRedPoint, self).__init__()
        self.checkRead = hallchecker.CHECK_BASE.clone()
        self.checkRead.addCheckFun(_point.check_moduleId)
        self.checkRead.addCheckFun(_point.check_itemId)

        self.checkSetUnReadHttp = tychecker.Checkers(
            tychecker.check_userId,
            _point.check_moduleId
        )
        self.dao = _dao.DaoRedPoint()
        self.redPointSys = _point.PointSystem(self.dao)

    def destoryPlugin(self):
        debug('isInitialized->', _dao.DataSchemaRedPoint.isInitialized)
        _dao.DataSchemaRedPoint.finalize()
        self.dao._delayFlushData()
        debug('isInitialized->', _dao.DataSchemaRedPoint.isInitialized)

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        debug('isInitialized->', _dao.DataSchemaRedPoint.isInitialized)
        _dao.DataSchemaRedPoint.initialize()
        debug('isInitialized->', _dao.DataSchemaRedPoint.isInitialized)

    def _sendRedPointNotify(self, userId):
        pluginCross.halldatanotify.sendDataChangeNotify(userId, tyglobal.gameId(), ['redpoint5'])

    @typlugin.markPluginEntry(event=HallUserEventLogin, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onHallUserEventLogin(self, event):
        '''
        登录时，需要主动发送一次
        '''
        if not event.isReconnect:
            self._sendRedPointNotify(event.userId)

    @typlugin.markPluginEntry(cmd='redpoint5', act='ui', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def getRedPointUi(self, msg):
        '''
        客户端主动更新小红点信息
        '''
        if _DEBUG:
            debug('HallPluginRedPoint.getRedPointUi IN', msg)
        mi = hallchecker.CHECK_BASE.check(msg)

        mo = MsgPack()
        mo.setCmd('redpoint5')
        mo.setResult('action', 'ui')

        if mi.error:
            mo.setError(1, mi.error)
        else:
            mo.setResult('points', self.redPointSys.encodeRedPointUiInfo(mi.userId))

        if mi.hasUserId:
            tyrpcconn.sendToUser(mi.userId, mo)

        if _DEBUG:
            debug('HallPluginRedPoint.getRedPointUi OUT')
        return 1

    @typlugin.markPluginEntry(cmd='redpoint5', act='read', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def setRedPointRead(self, msg):
        '''
        客户端通知：某一个项目已经被看过了，消除对应的小红点标记
        '''
        if _DEBUG:
            debug('HallPluginRedPoint.setRedPointRead IN', msg)
        mi = self.checkRead.check(msg)

        mo = MsgPack()
        mo.setCmd('redpoint5')
        mo.setResult('action', 'read')

        if mi.error:
            mo.setError(1, mi.error)
        else:
            # 设置已读数据
            changed = self.redPointSys.readPoint(mi.userId, mi.moduleId, mi.itemId)
            if changed :
                self._sendRedPointNotify(mi.userId)
            mo.setResult('moduleId', mi.moduleId)
            mo.setResult('itemId', mi.itemId)

        if mi.hasUserId:
            tyrpcconn.sendToUser(mi.userId, mo)

        if _DEBUG:
            debug('HallPluginRedPoint.setRedPointRead OUT')
        return 1

    @typlugin.markPluginEntry(httppath='redpoint/setunread')
    def setModuleUnReadHttp(self, request):
        '''
        控制级别： 1级（模块级别）
        其他模块调用：设置对应模块为未读
        '''
        if _DEBUG:
            debug('HallPluginRedPoint.setModuleUnReadHttp IN', request.args)
        mi = self.checkSetUnReadHttp.check(request)
        if mi.error:
            ret = 'error:' + mi.error
        else:
            try:
                hallRpcOne.hallredpoint.setModuleUnRead(mi.userId, mi.moduleId)
                ret = 'success'
            except Exception, e:
                ret = 'error:' + str(e)
                ftlog.error()
        if _DEBUG:
            debug('HallPluginRedPoint.setModuleUnReadHttp OUT')
        return ret

    @typlugin.markPluginEntry(httppath='redpoint/setread')
    def setModuleReadHttp(self, request):
        '''
        控制级别： 1级（模块级别）
        其他模块调用：设置对应模块为已读
        '''
        if _DEBUG:
            debug('HallPluginRedPoint.setModuleReadHttp IN', request.args)
        mi = self.checkSetUnReadHttp.check(request)
        if mi.error:
            ret = 'error:' + mi.error
        else:
            try:
                hallRpcOne.hallredpoint.setModuleRead(mi.userId, mi.moduleId)
                ret = 'success'
            except Exception, e:
                ret = 'error:' + str(e)
                ftlog.error()
        if _DEBUG:
            debug('HallPluginRedPoint.setModuleReadHttp OUT')
        return ret

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def setModuleUnRead(self, userId, moduleId):
        '''
        控制级别： 1级（模块级别）
        其他模块调用：设置对应模块为未读
        '''
        if _DEBUG:
            debug('HallPluginRedPoint.setModuleUnRead IN', userId, moduleId)
        if self.redPointSys.setModuleUnRead(userId, moduleId):
            self._sendRedPointNotify(userId)
        if _DEBUG:
            debug('HallPluginRedPoint.setModuleUnRead OUT', userId)
        return 1

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def setModuleRead(self, userId, moduleId):
        '''
        控制级别： 1级（模块级别）
        其他模块调用：设置对应模块为已读
        '''
        if _DEBUG:
            debug('HallPluginRedPoint.setModuleRead IN', userId, moduleId)
        if self.redPointSys.setModuleRead(userId, moduleId):
            self._sendRedPointNotify(userId)
        if _DEBUG:
            debug('HallPluginRedPoint.setModuleRead OUT', userId)
        return 1

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def resetItemIds(self, userId, moduleId, totalItemIds, defaultIsRead=1):
        '''
        其他模块调用：重新整理所有的项目，
        将目前RedPoint中存储的itemIds和totalItemIds进行比较，
        删除废弃的itemId，添加新的itemId（读取状态为 defaultIsRead 1未读 或 0已读)
        '''
        if _DEBUG:
            debug('HallPluginRedPoint.resetItemIds IN', userId, moduleId, totalItemIds)
        if self.redPointSys.resetItemIds(userId, moduleId, totalItemIds, defaultIsRead):
            self._sendRedPointNotify(userId)
        if _DEBUG:
            debug('HallPluginRedPoint.resetItemIds OUT', userId)
        return 1

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def getNoticePerlifeInfo(self, userId, moduleId, noticeid):
        '''
        其他模块调用：重新整理所有的项目，

        '''
        if _DEBUG:
            debug('HallPluginRedPoint.getNoticePerlifeInfo IN', userId, moduleId, noticeid)
        result = self.redPointSys.getNoticePerlifeInfo(userId, moduleId, noticeid)
        if _DEBUG:
            debug('HallPluginRedPoint.getNoticePerlifeInfo OUT', userId, result)
        return result

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def setItemUnRead(self, userId, moduleId, unReadItemIds, needAdd=1):
        '''
        其他模块调用：设置对应模块下的一组项目ID为未读
        如果 needAdd = 1 且 unReadItemIds 中对应的itemId不在当前的小红点控制列表中,那么添加至控制列表
        '''
        if _DEBUG:
            debug('HallPluginRedPoint.setItemUnRead IN', userId, moduleId, unReadItemIds, needAdd)
        if self.redPointSys.setItemUnRead(userId, moduleId, unReadItemIds, needAdd):
            self._sendRedPointNotify(userId)
        if _DEBUG:
            debug('HallPluginRedPoint.setItemUnRead OUT', userId)
        return 1

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def removeItemIds(self, userId, moduleId, removeItemIds):
        '''
        其他模块调用：删除对应模块下的一组项目ID
        '''
        if _DEBUG:
            debug('HallPluginRedPoint.removeItemIds IN', userId, moduleId, removeItemIds)
        if self.redPointSys.removeItemIds(userId, moduleId, removeItemIds):
            self._sendRedPointNotify(userId)
        if _DEBUG:
            debug('HallPluginRedPoint.removeItemIds OUT', userId)
        return 1
