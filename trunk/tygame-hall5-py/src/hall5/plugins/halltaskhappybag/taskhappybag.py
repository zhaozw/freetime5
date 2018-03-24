# -*- coding=utf-8 -*-
"""
@file  : task
@date  : 2016-11-25
@author: GongXiaobo
"""
from freetime5.twisted import ftlock
from freetime5.util import ftlog, fttime
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.entity.hallevent import HallUserEventLogin
from hall5.plugins.halltaskhappybag._private import _dao, _ui
from hall5.plugins.halltaskhappybag._private import _inspectors
from hall5.plugins.halltaskhappybag._private import _taskkinds
from hall5.plugins.halltaskhappybag._private import _taskpool
from hall5.plugins.halltaskhappybag._private import _taskunits
from tuyoo5.core import tyglobal, tyconfig
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpcconn
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tybireport
from tuyoo5.plugins.task import tytask


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginTaskHappyBag(tytask.TYTaskPlugin):

    def __init__(self):
        super(HallPluginTaskHappyBag, self).__init__()
        self.checkerGet = hallchecker.CHECK_BASE.clone()
        self.checkerGet.addCheckFun(_ui.check_taskId)
        self.checkerGet.addCheckFun(_ui.check_itemId)

    def destoryPlugin(self):
        _dao.DaoUserTask.finalize()
        tytask.REG_TASK_INSPECTOR.unRegisterModule(_inspectors, tytask.TYTaskInspector)
        tytask.REG_TASK_KIND.unRegisterModule(_taskkinds, tytask.TYTaskKind)
        tytask.REG_TASK_KIND_POOL.unRegisterModule(_taskpool, tytask.TYTaskKindPool)

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        _dao.DaoUserTask.initialize()
        tytask.REG_TASK_INSPECTOR.registerModule(_inspectors, tytask.TYTaskInspector)
        tytask.REG_TASK_KIND.registerModule(_taskkinds, tytask.TYTaskKind)
        tytask.REG_TASK_KIND_POOL.registerModule(_taskpool, tytask.TYTaskKindPool)

    @typlugin.markPluginEntry(confKeys=['game5:{}:task_happybag'.format(tyglobal.gameId())], srvType=[tyglobal.SRV_TYPE_HALL_UTIL])
    def onConfChanged(self, confKeys, changedKeys):
        self._onConfChanged('task_happybag', tyglobal.SRV_TYPE_HALL_UTIL)

    def newTaskUnit(self, taskUnitId, dataDao, taskKindMap):
        t = _taskunits.HappyBagTaskUnit(taskUnitId, dataDao, taskKindMap)
        return t

    def newTaskDataDao(self):
        d = _dao.HallTaskDataDao()
        return d

    @ftlock.lockargname('hall5.task_happybag', 'userId')
    def loadUserTaskUnit(self, userId, clientId=None):
        return super(HallPluginTaskHappyBag, self).loadUserTaskUnit(userId, clientId)

    @ftlock.lockargname('hall5.task_happybag', 'userId')
    def _handleTaskEvent(self, userId, event):
        if _DEBUG:
            debug('HallPluginTaskHappyBag->_handleTaskEvent IN', userId, event)
        ret = super(HallPluginTaskHappyBag, self)._handleTaskEvent(userId, event)
        if _DEBUG:
            debug('HallPluginTaskHappyBag->_handleTaskEvent OUT', userId, event)
        return ret

    @ftlock.lockargname('hall5.task_happybag', 'userId')
    def getTaskReward(self, userId, taskId, clientId, **kwargs):
        if _DEBUG:
            debug('HallPluginTaskHappyBag->getTaskReward IN', userId, taskId, clientId)
        ret = super(HallPluginTaskHappyBag, self).getTaskReward(userId, taskId, clientId, **kwargs)
        if _DEBUG:
            debug('HallPluginTaskHappyBag->getTaskReward OUT', userId, taskId, clientId, ret)
        return ret

    def _sendTaskReward(self, userId, task, clientId, timestamp, **kwargs):
        if _DEBUG:
            debug('HallPluginTaskHappyBag->_sendTaskReward IN', userId, task.taskId, task.kindId)
        assertList = _taskunits._sendTaskReward(userId, task, clientId, timestamp, **kwargs)
        if _DEBUG:
            debug('HallPluginTaskHappyBag->_sendTaskReward OUT', userId, task.taskId, task.kindId, assertList)
        return assertList

    def _checkUserTasksWhenLoad(self, userId, userTaskUnit, clientId):
        '''
        当用户的任务列表加载后，进行任务列表的整体检查，
        判定是否要进行任务的发放、删除或整理
        '''
        if _DEBUG:
            debug('HallPluginTaskHappyBag->_checkUserTasksWhenLoad IN clientId=', clientId, 'userId=', userId, 'userTaskUnit=', userTaskUnit)

        if userTaskUnit is None or len(userTaskUnit.taskIdMap) == 0:
            if clientId:
                # 没有任何任务，重新分配， 只有当有客户端消息触发时才进行分配，事件触发不进行分配，避免检查过多
                taskUnitId = tyconfig.getCacheTemplateName('task_happybag', clientId, tyglobal.gameId())
                if _DEBUG:
                    debug('HallPluginTaskHappyBag->_checkUserTasksWhenLoad clientId=', clientId, 'userId=', userId,
                          'taskUnitId=', taskUnitId, self.taskUnits.keys())
                taskUnit = self.taskUnits.get(taskUnitId)
                if taskUnit:
                    # 分配最初的任务列表
                    userTaskUnit = _taskunits._initUserFirstTaskList(userId, taskUnit)
                    # 清理缓存，下次在调用时，重新装载，使用缓存
                    self.removeUserTaskUnitCache(userId)
                else:
                    # 如果未配置对应clientId的任务列表，则不分配任务
                    pass
        else:
            # 检查任务的新增情况，注：删除功能已在 loadUserTaskUnit 中删除
            _taskunits._checkIfNeedAddNewTask(userTaskUnit)

        # 检查任务关联状态, 补充检查，避免事件丢失或异常而导致状态不能转换
        _taskunits._checkAllTaskStatus(userTaskUnit)

        if _DEBUG:
            debug('HallPluginTaskHappyBag->_checkUserTasksWhenLoad OUT clientId=', clientId, 'userId=', userId, 'userTaskUnit=', userTaskUnit)

        return userTaskUnit

    def _checkUserTasksAfterEvent(self, userTaskUnit):
        # 当事件出发后，如果任务属性发生变化，检查任务关联状态
        _taskunits._checkAllTaskStatus(userTaskUnit)

    def _checkUserTasksAfterGetReward(self, userTaskUnit):
        # 领取奖励后，检查任务关联状态
        _taskunits._checkAllTaskStatus(userTaskUnit)

    @typlugin.markPluginEntry(event=HallUserEventLogin, srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def onUserLoginHappybag(self, event):
        if not event.isReconnect and event.isDayfirst:
            # 只在每日首次登陆时，主动检查任务
            self.loadUserTaskUnit(event.userId, event.clientId)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _doRemoveAll(self, userId):
        userTaskUnit = self._loadUserTaskUnitCache(userId, None)
        if userTaskUnit:
            tasks = userTaskUnit.taskIdMap.values()[:]
            for task in tasks:
                userTaskUnit.removeTask(task)
            userTaskUnit.flushDao()
        self.removeUserTaskUnitCache(userId)
        return 'ok'

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _doHappyBagListFull(self, userId, clientId):
        userTaskUnit = self.loadUserTaskUnit(userId, clientId)
        taskList = _ui.encodeUserTaskListFull(userTaskUnit)
        return taskList

    @typlugin.markPluginEntry(cmd='happybag5/ui', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doHappyBagList(self, msg):
        if _DEBUG:
            debug('doHappyBagList IN->', msg)

        mi = hallchecker.CHECK_BASE.check(msg)
        mo = MsgPack()
        mo.setCmd('happybag5')
        mo.setResult('action', 'list')

        if mi.error:
            mo.setError(1, mi.error)
        else:
            userTaskUnit = self.loadUserTaskUnit(mi.userId, mi.clientId)
            taskList = _ui.encodeUserTaskList(userTaskUnit)
            mo.setResult('tasks', taskList)

        tyrpcconn.sendToUser(mi.userId, mo)

        # 记录BI统计，仅为数据统计
        if not mi.error:
            flg = pluginCross.hallday1st.getHappyBagFlg(mi.userId)
            if flg == 0:
                pluginCross.hallday1st.setHappyBagFlg(mi.userId)
                tybireport.reportGameSimpleEvent('HAPPY_BAG_TASK_LIST', mi.userId, mi.gameId, mi.clientId)

        if _DEBUG:
            debug('doHappyBagList OUT', mo)
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @ftlock.lockargname('hall5.task_happybag', 'userId')
    def _setProgress(self, userId, taskId, progress):
        userTaskUnit = self._loadUserTaskUnitCache(userId, None)
        if userTaskUnit:
            task = userTaskUnit.findTaskByTaskId(taskId)
            if task:
                timestamp = fttime.getCurrentTimestamp()
                if progress >= task.taskKind.progressMax or progress < 0:
                    progress = task.taskKind.progressMax
                task.setProgress(progress, timestamp)
                userTaskUnit.updateTask(task)
                userTaskUnit.taskUnit._onTaskUpdated(task)
                if task.status == tytask.TYUserTask.STATUS_FINISHED:
                    userTaskUnit.taskUnit._onTaskFinished(task, timestamp)
                self._checkUserTasksAfterEvent(userTaskUnit)
                userTaskUnit.flushDao()
        return 'ok'

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @ftlock.lockargname('hall5.task_happybag', 'userId')
    def _setUpdateTime(self, userId, taskId, updateTime):
        userTaskUnit = self._loadUserTaskUnitCache(userId, None)
        if userTaskUnit:
            task = userTaskUnit.findTaskByTaskId(taskId)
            if task:
                userTaskUnit.updateTask(task)
                userTaskUnit.flushDao(updateTime)
        return 'ok'

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _doGetReward(self, userId, taskId, itemId, clientId):
        code, result = self.getTaskReward(userId, taskId, clientId, itemId=itemId)
        if code == 0:
            rewardsList = []
            for assetItemTuple in result:
                assetItem = assetItemTuple[0]  # 0 - assetItem 1 - count 2 - final
                reward = {'name': assetItem.displayName, 'pic': assetItem.pic, 'count': assetItemTuple[1],
                          'kindId': assetItem.kindId}
                rewardsList.append(reward)
            rewardTodotask = pluginCross.halltodotask.makeTodoTaskShowRewards(rewardsList)
        else:
            rewardTodotask = pluginCross.halltodotask.makeTodoTaskShowInfo(result)
        return code, rewardTodotask.toDict()

    @typlugin.markPluginEntry(cmd='happybag5/getreward', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doHappyBagGetReward(self, msg):
        if _DEBUG:
            debug('doHappyBagGetReward IN->', msg)

        mi = self.checkerGet.check(msg)
        mo = MsgPack()
        mo.setCmd('happybag5')
        mo.setResult('action', 'getreward')

        if mi.error:
            mo.setError(1, mi.error)
        else:
            code, rewardDict = self._doGetReward(mi.userId, mi.taskId, mi.itemId, mi.clientId)
            mo.setResult('userId', mi.userId)
            mo.setResult('taskId', mi.taskId)
            mo.setResult('code', code)
            mo.setResult('todotasks', rewardDict)

        tyrpcconn.sendToUser(mi.userId, mo)

        if _DEBUG:
            debug('doHappyBagGetReward OUT', mo)
        return 1
