# -*- coding=utf-8 -*-
"""
@file  : _task
@date  : 2016-11-25
@author: GongXiaobo
"""
from tuyoo5.game import tycontent
from tuyoo5.plugins.task import tytask
from datetime import datetime
from freetime5.util import ftlog


def check_taskId(msg, result, name):
    val = msg.getParamInt(name, 0)
    if val <= 0:
        return None, 'the param %s = %s error !' % (name, val)
    return val, None


def check_itemId(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def encodeUserTaskList(userTaskUnit):
    taskList = []
    if userTaskUnit:
        taskKindPool = userTaskUnit.taskKindPool
        for taskId in taskKindPool.taskIdList:
            task = userTaskUnit.findTaskByTaskId(taskId)
            if task and (task.status == tytask.TYUserTask.STATUS_NORMAL or
                         task.status == tytask.TYUserTask.STATUS_FINISHED or
                         task.status == tytask.TYUserTask.STATUS_GOTREWARD or
                         task.status == tytask.TYUserTask.STATUS_LOCKED
                         ):
                data = [
                    taskId,  # 任务ID
                    task.kindId,  # 任务类型ID,
                    task.progress,  # 任务进度
                    task.status  # 显示按钮的序号 0 继续努力 1 可领取 2 已经领取 3 锁定 4 未进行隐藏 5 已领取隐藏
                ]
                taskList.append(data)
    return taskList


def encodeUserTaskListFull(userTaskUnit):
    taskList = []
    if userTaskUnit:
        taskKindPool = userTaskUnit.taskKindPool
        for taskId in taskKindPool.taskIdList:
            asserts = None
            task = userTaskUnit.findTaskByTaskId(taskId)
            if task:
                if isinstance(task.taskKind.rewardContent, tycontent.TYChoiceContent):
                    asserts = []
                    for x in task.taskKind.rewardContent._generators:
                        asserts.append(x._assetKindId)
                data = [
                    taskId,  # 任务ID
                    task.kindId,  # 任务类型ID,
                    task.progress,  # 任务进度
                    task.status,  # 显示按钮的序号 0 继续努力 1 可领取 2 已经领取 3 锁定 4 未进行隐藏 5 已领取隐藏
                    task.taskKind.name,
                    asserts,
                    datetime.fromtimestamp(task.updateTime).strftime('%Y-%m-%d %H:%M:%S'),
                    task.taskKind.progressMax,
                    task.finishCount,
                    task.taskKind.totalLimit,
                ]
                taskList.append(data)
            else:
                ftlog.warn('encodeUserTaskListFull not found->', userTaskUnit.userId, taskId, task)
    return taskList
