# -*- coding=utf-8 -*-
"""
@file  : _task
@date  : 2016-11-25
@author: GongXiaobo
"""

from freetime5.util import fttime, ftlog
from tuyoo5.plugins.task import tytask
from tuyoo5.plugins.task.exceptions import TYTaskConfException


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallTaskKindSimple(tytask.TYTaskKind):

    TYPE_ID = 'hall.task.simple'

    def __init__(self):
        super(HallTaskKindSimple, self).__init__()

    def _decodeFromDictImpl(self, d):
        return self

    def _checkTaskStatus(self, userTask):
        newStatus = -1
        if userTask.status == tytask.TYUserTask.STATUS_GOTREWARD:
            # 如果已经领取，那么判定是否显示
            if self.deleteWhenGetReward:
                newStatus = tytask.TYUserTask.STATUS_GOTREWARD_HIDDEN

        if newStatus != -1 and newStatus != userTask.status:
            # 状态发生改变，更新任务
            userTask.status = newStatus
            userTask.userTaskUnit.updateTask(userTask)


class HallTaskKindDepend(HallTaskKindSimple):

    TYPE_ID = 'hall.task.depend'

    def __init__(self):
        super(HallTaskKindDepend, self).__init__()
        self.dependKindId = 0
        self.dependUiStyle = 0

    def _decodeFromDictImpl(self, d):
        self.dependKindId = d.get('dependTask', 0)
        if not isinstance(self.dependKindId, int):
            raise TYTaskConfException(d, 'task.dependKindId must be int')

        self.dependUiStyle = d.get('dependUiStyle', 0)
        if self.dependUiStyle not in (0, 1):
            raise TYTaskConfException(d, 'task.dependUiStyle must be int in (0, 1)')
        return self

    def _checkTaskStatus(self, userTask):
        # 检查依赖的任务是否完成
        isDependOk = 0
        dtask = userTask.userTaskUnit.findTaskByKindId(self.dependKindId)
        # 以是否 完成 为基础，打开下一个任务
        # if dtask and dtask.finishCount > 0:
        #    isDependOk = 1
        # 以是否 领取 为基础，打开下一个任务
        if dtask and (dtask.status == tytask.TYUserTask.STATUS_GOTREWARD or dtask.status == tytask.TYUserTask.STATUS_GOTREWARD_HIDDEN):
            isDependOk = 1

        if _DEBUG:
            debug('HallTaskKindDepend._checkTaskStatus kindId=', self.kindId,
                  'dependKindId=', self.dependKindId,
                  'isDependOk=', isDependOk)
        newStatus = -1
        # 判定新的状态值
        if isDependOk:
            if (userTask.status == tytask.TYUserTask.STATUS_HIDDEN or userTask.status == tytask.TYUserTask.STATUS_LOCKED):
                # 依赖完成时，由隐藏、锁定状态转换为正常状态
                newStatus = tytask.TYUserTask.STATUS_NORMAL
            elif userTask.status == tytask.TYUserTask.STATUS_GOTREWARD:
                # 如果已经领取，那么判定是否显示
                if self.deleteWhenGetReward:
                    newStatus = tytask.TYUserTask.STATUS_GOTREWARD_HIDDEN
        else:
            if self.dependUiStyle == 0:
                # 依赖未完成时，隐藏
                newStatus = tytask.TYUserTask.STATUS_HIDDEN
            else:
                # 依赖未完成时，锁定
                newStatus = tytask.TYUserTask.STATUS_LOCKED

        if newStatus != -1 and newStatus != userTask.status:
            # 状态发生改变，更新任务
            userTask.status = newStatus
            userTask.userTaskUnit.updateTask(userTask)


class HallTaskKindDialy(HallTaskKindSimple):

    TYPE_ID = 'hall.task.daily'

    def __init__(self):
        super(HallTaskKindDialy, self).__init__()

    def _decodeFromDictImpl(self, d):
        return self

    def _checkTaskStatus(self, userTask):
        newStatus = -1
        if _DEBUG:
            debug('HallTaskKindDialy._checkTaskStatus->', userTask.userTaskUnit.userId, userTask.taskId, userTask.kindId)
        if userTask.status == tytask.TYUserTask.STATUS_GOTREWARD:
            # 如果已经领取，那么判定是否需要进行重置任务
            if _DEBUG:
                debug('HallTaskKindDialy._checkTaskStatus->', userTask.userTaskUnit.userId, userTask.taskId, userTask.kindId,
                      'totalLimit=', userTask.taskKind.totalLimit, 'finishCount=', userTask.finishCount)
            if userTask.taskKind.totalLimit <= 0 or userTask.taskKind.totalLimit > userTask.finishCount:
                # 再最大次数内进行状态转换
                isToday = fttime.is_same_day(userTask.updateTime, fttime.getCurrentTimestamp())
                if _DEBUG:
                    debug('HallTaskKindDialy._checkTaskStatus->', userTask.userTaskUnit.userId, userTask.taskId, userTask.kindId,
                          'isToday=', isToday)
                if not isToday:
                    # 最后更新为 领取 时间，已经跨天，重置任务 (并且要在最大次数以内）
                    newStatus = tytask.TYUserTask.STATUS_NORMAL
                    userTask.progress = 0

        if newStatus != -1 and newStatus != userTask.status:
            # 状态发生改变，更新任务
            userTask.status = newStatus
            userTask.userTaskUnit.updateTask(userTask)
