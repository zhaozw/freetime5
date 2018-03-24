# -*- coding=utf-8 -*-
"""
@file  : _tasksubsys
@date  : 2016-11-28
@author: GongXiaobo
"""

from freetime5.util import fttime
from tuyoo5.core import tyglobal
from tuyoo5.core.typlugin import pluginCross, pluginSafeCross
from tuyoo5.game import tycontent, tysessiondata
from tuyoo5.game import tybireport
from tuyoo5.plugins.task import tytask
from tuyoo5.plugins.task.tytask import TYUserTask


class HappyBagTaskUnit(tytask.TYTaskUnit):

    def __init__(self, taskUnitId, dataDao, taskKindMap):
        super(HappyBagTaskUnit, self).__init__(taskUnitId, dataDao, taskKindMap)

    def _newUserTaskUnit(self, userId):
        return HappyBagUserTaskUnit(userId, self)

    def _onTaskFinished(self, userTask, timestamp):
        pluginSafeCross.hallredpoint.setItemUnRead(userTask.userTaskUnit.userId, 'happybag5', [userTask.taskId])
        userId = userTask.userTaskUnit.userId
        clientId = tysessiondata.getClientIdInt(userId)
        tybireport.reportGameSimpleEvent('HAPPY_BAG_TASK', userId,  tyglobal.gameId(), clientId,
                                         userTask.taskId, userTask.kindId, userTask.status)


class HappyBagUserTaskUnit(tytask.TYUserTaskUnit):

    def __init__(self, userId, taskUnit):
        super(HappyBagUserTaskUnit, self).__init__(userId, taskUnit)

    def removeAllTask(self):
        taskIds = super(HappyBagUserTaskUnit, self).removeAllTask()
        pluginSafeCross.hallredpoint.resetItemIds(self.userId, 'happybag5', [])
        return taskIds

    def removeTask(self, task):
        taskId = super(HappyBagUserTaskUnit, self).removeTask(task)
        pluginSafeCross.hallredpoint.removeItemIds(self.userId, 'happybag5', [taskId])
        return taskId


def _sendTaskReward(userId, task, clientId, timestamp, **kwargs):
    assetList = []
    content = task.taskKind.rewardContent
    if content:
        if isinstance(content, tycontent.TYChoiceContent):
            itemId = kwargs['itemId']
            itemList = content.getItems(itemId)
            if not itemList:
                raise Exception('the param itemId = [%s] error ! userId=%s  taskId=%s kwargs=%s' % (itemId, userId, task.taskId, str(kwargs)))
        else:
            itemList = content.getItems()
        assetList = pluginCross.hallitem.sendContentItemList(tyglobal.gameId(),
                                                             userId,
                                                             itemList,
                                                             1,
                                                             True,
                                                             timestamp,
                                                             'HAPPY_BAG_TASK',
                                                             task.kindId)
        tybireport.reportGameSimpleEvent('HAPPY_BAG_TASK', userId, tyglobal.gameId(), clientId, task.taskId, task.kindId, task.status)
    if not assetList:
        raise Exception('sendContentItemList return empty list error ! userId=%s taskId=%s kwargs=%s' % (userId, task.taskId, str(kwargs)))
    return assetList


def _initUserFirstTaskList(userId, taskUnit):
    '''
    最原始的任务列表初始化
    '''
    # 建立新对象
    userTaskUnit = taskUnit._newUserTaskUnit(userId)
    # 分配第一个池子中的所有任务
    taskKindPool = taskUnit.poolList[0]
    userTaskUnit.taskKindPool = taskKindPool
    # 增加对小红点检测
    unreadTaskIds = []
    readTaskIds = []
    for taskId in taskKindPool.taskIdList:
        taskKind = taskUnit.findTaskKindByTaskId(taskId)
        if not taskKind or taskKind.deprecated == 1:  # 不推荐或过时的任务不进行分配
            continue
        userTask = taskKind.newTask(taskId)
        userTaskUnit.addTask(userTask)

        # 检测红点设置情况
        task = userTaskUnit.findTaskByTaskId(taskId)
        task.taskKind._checkTaskStatus(task)
        # 检测对已经完成任务的小红点的显示
        if task.status == TYUserTask.STATUS_FINISHED:
            unreadTaskIds.append(taskId)
        else:
            readTaskIds.append(taskId)
    # 初始化的任务默认已读，后续有变化才添加红点
    # if len(readTaskIds) > 0:
    #     pluginSafeCross.hallredpoint.resetItemIds(userTaskUnit.userId, 'happybag5', readTaskIds, 0)
    # 对小红点的状态做设置: 1 未读  0 已读
    if len(unreadTaskIds) > 0:
        pluginSafeCross.hallredpoint.resetItemIds(userTaskUnit.userId, 'happybag5', unreadTaskIds, 1)
    return userTaskUnit


def _checkIfNeedAddNewTask(userTaskUnit):
    '''
    检查配置中有，而用户身上没有的task，并添加
    '''
    if userTaskUnit:
        taskKindPool = userTaskUnit.taskKindPool
        # 检查配置中没有有的，而用户身有的task，并删除
        delIds = []
        # 增加对小红点检测
        unreadTaskIds = []
        readTaskIds = []
        for taskId in userTaskUnit.taskIdMap:
            if not taskId in taskKindPool.taskIdList:
                delIds.append(taskId)

        for taskId in delIds:
            userTaskUnit.removeTask(userTaskUnit.taskIdMap[taskId])

        # 检查配置中有，而用户身上没有的task，并添加
        timestamp = 0
        for taskId in taskKindPool.taskIdList:
            if not userTaskUnit.findTaskByTaskId(taskId):
                taskKind = userTaskUnit.taskUnit.findTaskKindByTaskId(taskId)
                if not taskKind or taskKind.deprecated == 1:  # 不推荐或过时的任务不进行分配
                    continue
                if timestamp <= 0:
                    timestamp = fttime.getCurrentTimestamp()
                userTask = taskKind.newTask(taskId)
                userTaskUnit.addTask(userTask)

                # 检测红点设置情况
                task = userTaskUnit.findTaskByTaskId(taskId)
                task.taskKind._checkTaskStatus(task)
                # 检测对已经完成任务的小红点的显示
                if task.status == TYUserTask.STATUS_FINISHED:
                    unreadTaskIds.append(taskId)
                else:
                    readTaskIds.append(taskId)
        # 初始化的任务默认已读，后续有变化才添加红点
        # if len(readTaskIds) > 0:
        #     pluginSafeCross.hallredpoint.resetItemIds(userTaskUnit.userId, 'happybag5', readTaskIds, 0)
        # 对小红点的状态做设置: 1 未读  0 已读
        if len(unreadTaskIds) > 0:
            pluginSafeCross.hallredpoint.resetItemIds(userTaskUnit.userId, 'happybag5', unreadTaskIds, 1)
    return userTaskUnit


def _checkAllTaskStatus(userTaskUnit):
    '''
    检查所有的任务，修改任务状态等操作
    '''
    if userTaskUnit:
        taskKindPool = userTaskUnit.taskKindPool
        taskIds = []
        for taskId in taskKindPool.taskIdList:
            task = userTaskUnit.findTaskByTaskId(taskId)
            if task:
                assert(not isinstance(task.finishCount, int) or
                       not isinstance(task.gotRewardCount, int) or
                       task.finishCount < 0 or
                       task.gotRewardCount < 0 or
                       not (task.finishCount > 0 and task.gotRewardCount > task.finishCount)), \
                    'userId=%s taskId=%s finishCount=%s gotRewardCount=%s task=%s' % (
                        userTaskUnit.userId, taskId, task.finishCount, task.gotRewardCount,  str(task))
                task.taskKind._checkTaskStatus(task)
                # if task.status == TYUserTask.STATUS_FINISHED or task.status == TYUserTask.STATUS_NORMAL:
                if task.status == TYUserTask.STATUS_FINISHED:
                    taskIds.append(taskId)
        userTaskUnit.flushDao()
        pluginSafeCross.hallredpoint.resetItemIds(userTaskUnit.userId, 'happybag5', taskIds)
    return userTaskUnit
