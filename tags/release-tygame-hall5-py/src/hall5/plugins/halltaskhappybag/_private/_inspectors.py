# -*- coding=utf-8 -*-
"""
@file  : _taskinspector
@date  : 2016-11-28
@author: GongXiaobo
"""

from freetime5.util import fttime
from tuyoo5.core import tygame
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import UserKeys
from tuyoo5.plugins.task import tytask
from tuyoo5.plugins.task.exceptions import TYTaskConfException
from freetime5._tyserver._games.ftgame import getBigRoomId as getBigRoomId


class InspectorFishtotalFishCount(tytask.TYTaskInspector):
    """
    捕鱼插件的捕鱼数量
    由：子游戏通过 hallrpc.sendEventToHallHU 方法远程发送事件
    """
    TYPE_ID = 'hall.play.user.fish.total.count'

    def __init__(self):
        super(InspectorFishtotalFishCount, self).__init__([tygame.GameOverEvent])
        self.gameId = 0
        self.totalFishCount = 0

    def _decodeFromDictImpl(self, d):
        self.gameId = d.get('gameId')
        if not isinstance(self.gameId, int):
            raise TYTaskConfException(d, 'InspectorFishtotalFishCount.gameId must be int')
        return self

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.GameOverEvent):
            if event.gameId == self.gameId:  # 胜利
                return task.setProgress(task.progress + int(event.kwargs.get('totalFishCount')), event.timestamp)
        return False


class InspectorFishBossFishCount(tytask.TYTaskInspector):
    """
    捕鱼插件的捕boss鱼数量
    由：子游戏通过 hallrpc.sendEventToHallHU 方法远程发送事件
    """
    TYPE_ID = 'hall.play.user.fish.boss.count'

    def __init__(self):
        super(InspectorFishBossFishCount, self).__init__([tygame.GameOverEvent])
        self.gameId = 0
        self.roomIds = []

    def _decodeFromDictImpl(self, d):
        self.gameId = d.get('gameId')
        if not isinstance(self.gameId, int):
            raise TYTaskConfException(d, 'InspectorFishBossFishCount.gameId must be int')
        return self

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.GameOverEvent):
            if event.gameId == self.gameId:  # 胜利
                return task.setProgress(task.progress + int(event.kwargs.get('bossFishCount')), event.timestamp)
        return False

class InspectorPlayNormalTotalCount(tytask.TYTaskInspector):
    """
    任意游戏胜利次数
    由：子游戏通过 hallrpc.sendEventToHallHU 方法远程发送事件
    """
    TYPE_ID = 'hall.play.normal.total.count'

    def __init__(self):
        super(InspectorPlayNormalTotalCount, self).__init__([tygame.GameOverEvent])

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.GameOverEvent):
            if event.gameResult == 1:  # 胜利
                return task.setProgress(task.progress + 1, event.timestamp)
        return False


class InspectorPlayMatchTotalCount(tytask.TYTaskInspector):
    """
    参加比赛的次数累积
    由：子游戏通过 hallrpc.sendEventToHallHU 方法远程发送事件
    """
    TYPE_ID = 'hall.play.match.total.count'

    def __init__(self):
        super(InspectorPlayMatchTotalCount, self).__init__([tygame.MatchOverEvent])

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.MatchOverEvent):
            # 只要参加就算，不看比赛成绩
            return task.setProgress(task.progress + 1, event.timestamp)
        return False

class InspectorGamePlayWinTotalCount(tytask.TYTaskInspector):
    """
    同一个gameid任意游戏胜利次数
    由：子游戏通过 hallrpc.sendEventToHallHU 方法远程发送事件
    """
    TYPE_ID = 'hall.play.user.win.total.count'

    def __init__(self):
        super(InspectorGamePlayWinTotalCount, self).__init__([tygame.GameOverEvent])
        self.gameId = 0
        self.roomIds = []

    def _decodeFromDictImpl(self, d):
        self.gameId = d.get('gameId')
        self.roomIds = d.get('roomId')
        if not isinstance(self.gameId, int):
            raise TYTaskConfException(d, 'InspectorGamePlayWinTotalCount.gameId must be int')
        if not isinstance(self.roomIds, list):
            raise TYTaskConfException(d, 'InspectorGamePlayWinTotalCount.roomIds must be list')
        return self

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.GameOverEvent):
            if event.gameId == self.gameId and event.gameResult == 1:  # 胜利
                return task.setProgress(task.progress + 1, event.timestamp)
        return False

class InspectorGamePlayTotalCount(tytask.TYTaskInspector):
    """
    任意游戏次数
    由：子游戏通过 hallrpc.sendEventToHallHU 方法远程发送事件
    """
    TYPE_ID = 'hall.play.user.total.count'

    def __init__(self):
        super(InspectorGamePlayTotalCount, self).__init__([tygame.GameOverEvent])
        self.gameId = 0
        self.roomIds = []

    def _decodeFromDictImpl(self, d):
        self.gameId = d.get('gameId')
        self.roomIds = d.get('roomId')
        if not isinstance(self.gameId, int):
            raise TYTaskConfException(d, 'InspectorGamePlayTotalCount.userId must be int')
        if not isinstance(self.roomIds, list):
            raise TYTaskConfException(d, 'InspectorGamePlayTotalCount.roomIds must be list')
        return self

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.GameOverEvent):
            if event.gameId == self.gameId:
                return task.setProgress(task.progress + 1, event.timestamp)
        return False


class InspectorPlayWinningStreakCount(tytask.TYTaskInspector):
    """
    子游戏连续胜利次数
    由：子游戏通过 hallrpc.sendEventToHallHU 方法远程发送事件
    """
    TYPE_ID = 'hall.play.winning.streak.total.count'

    def __init__(self):
        super(InspectorPlayWinningStreakCount, self).__init__([tygame.GameOverEvent])
        self.gameId = 0
        self.roomIds = []

    def _decodeFromDictImpl(self, d):
        self.gameId = d.get('gameId')
        self.roomIds = d.get('roomId')
        if not isinstance(self.gameId, int):
            raise TYTaskConfException(d, 'InspectorPlayWinningStreakCount.gameId must be int')
        if not isinstance(self.roomIds, list):
            raise TYTaskConfException(d, 'InspectorPlayWinningStreakCount.roomIds must be list')
        return self

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.GameOverEvent):
            if event.gameResult == 1 and event.gameId == self.gameId:  # 胜利
                return task.setProgress(int(event.winningStreak), event.timestamp)
        return False

class InspectorGameRoomPlayWinningStreakCount(tytask.TYTaskInspector):
    """
    子游戏同一个房间连续胜利次数
    由：子游戏通过 hallrpc.sendEventToHallHU 方法远程发送事件
    """
    TYPE_ID = 'hall.play.winning.streak.game.room.total.count'

    def __init__(self):
        super(InspectorGameRoomPlayWinningStreakCount, self).__init__([tygame.GameOverEvent])
        self.gameId = 0
        self.roomIds = []

    def _decodeFromDictImpl(self, d):
        self.gameId = d.get('gameId')
        self.roomIds = d.get('roomId')
        if not isinstance(self.gameId, int):
            raise TYTaskConfException(d, 'InspectorGameRoomPlayWinningStreakCount.gameId must be int')
        if not isinstance(self.roomIds, list):
            raise TYTaskConfException(d, 'InspectorGameRoomPlayWinningStreakCount.roomIds must be list')
        return self

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.GameOverEvent):
            roomId = event.roomId if len(str(event.roomId)) == 4 else getBigRoomId(event.roomId)
            if event.gameResult == 1 and event.gameId == self.gameId and roomId in self.roomIds:  # 胜利
                return task.setProgress(int(event.winningStreak), event.timestamp)
        return False

class InspectorCouponCount(tytask.TYTaskInspector):
    """
    奖券数量到达一定的值
    由：大厅内部 halldata 插件进行触发事件
    """
    TYPE_ID = 'hall.coupon.count'

    def __init__(self):
        super(InspectorCouponCount, self).__init__([tygame.CouponChangedEvent])

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.CouponChangedEvent):
            return task.setProgress(int(event.finalCount), event.timestamp)
        return False

class InspectorChipCount(tytask.TYTaskInspector):
    """
    金币数量到达一定的值
    由：大厅内部 halldata 插件进行触发事件
    """
    TYPE_ID = 'hall.chip.count'

    def __init__(self):
        super(InspectorChipCount, self).__init__([tygame.ChipChangedEvent])

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.ChipChangedEvent):
            return task.setProgress(int(event.finalCount), event.timestamp)
        return False

    def _onTaskCreated(self, task):
        chip_num = pluginCross.halldata.getUserDataList(task.userTaskUnit.userId, UserKeys.ATT_CHIP)
        if chip_num > 0:
            task.setProgress(task.progress + chip_num, fttime.getCurrentTimestamp())


class InspectorSubGameDataChange(tytask.TYTaskInspector):
    """
    插件游戏数据发生变化
    由：子游戏通过 hallrpc.sendEventToHallHU 方法远程发送事件
    """
    TYPE_ID = 'hall.sub.game.data.change'

    def __init__(self):
        super(InspectorSubGameDataChange, self).__init__([tygame.GameDataChangedEvent])
        self.gameId = 0
        self.filedName = ''

    def _decodeFromDictImpl(self, d):
        self.gameId = d.get('gameId')
        if not isinstance(self.gameId, int):
            raise TYTaskConfException(d, 'InspectorSubGameDataChange.game must be int')
        self.filedName = d.get('filedName')
        if not isinstance(self.filedName, (str, unicode)) or not self.filedName:
            raise TYTaskConfException(d, 'InspectorSubGameDataChange.filedName must be string')
        return self

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.GameDataChangedEvent):
            if event.gameId == self.gameId and event.filedName == self.filedName:
                return task.setProgress(int(event.filedValue), event.timestamp)
        return False


class InspectorWeiXinShared(tytask.TYTaskInspector):
    """
    微信每日分享
    由：客户端上报 至 大厅内部 hallshare 插件进行事件触发
    """
    TYPE_ID = 'hall.weixin.share.daily.count'

    def __init__(self):
        super(InspectorWeiXinShared, self).__init__([tygame.WeiXinSharedEvent])

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.WeiXinSharedEvent):
            return task.setProgress(task.progress + 1, event.timestamp)
        return False


class InspectorFirstChargeCount(tytask.TYTaskInspector):
    """
    单笔充值数量到达一定的值
    由： SDK发送充值通知 至 大厅内部 hallstore 插件进行事件触发
    """
    TYPE_ID = 'hall.charge.frist.count'

    def __init__(self):
        super(InspectorFirstChargeCount, self).__init__([tygame.ChargeNotifyEvent])

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.ChargeNotifyEvent):
            return task.setProgress(int(event.rmbs), event.timestamp)
        return False

    def _onTaskCreated(self, task):
        RMB_num = pluginCross.halldata.getUserDataList(task.userTaskUnit.userId, UserKeys.ATT_CHARGE_TOTAL)
        if RMB_num > 0:
            task.setProgress(task.progress + RMB_num, fttime.getCurrentTimestamp())


class InspectorBindPhone(tytask.TYTaskInspector):
    """
    绑定手机
    由： SDK发送充值通知 至 大厅内部 hallsubgame 插件进行事件触发
    """
    TYPE_ID = 'hall.user.bindPhone'

    def __init__(self):
        super(InspectorBindPhone, self).__init__([tygame.AccountBindPhoneEvent])

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.AccountBindPhoneEvent):
            return task.setProgress(task.progress + 1, event.timestamp)
        return False

    def _onTaskCreated(self, task):
        # bindMobile 如果已经绑定了，那么直接可以领取
        bindMobile = pluginCross.halldata.getUserDataList(task.userTaskUnit.userId, UserKeys.ATT_BIND_MOBILE)
        if bindMobile and len(str(bindMobile)) == 11:
            task.setProgress(task.progress + 1, fttime.getCurrentTimestamp())


class InspectorBindWeiXin(tytask.TYTaskInspector):
    """
    绑定微信
    由： SDK发送充值通知 至 大厅内部 hallsubgame 插件进行事件触发
    """
    TYPE_ID = 'hall.user.bindWeixin'

    def __init__(self):
        super(InspectorBindWeiXin, self).__init__([tygame.AccountBindWeiXinEvent])

    def _processEventImpl(self, task, event):
        if isinstance(event, tygame.AccountBindWeiXinEvent):
            return task.setProgress(task.progress + 1, event.timestamp)
        return False

    def _onTaskCreated(self, task):
        # snsId 如果已经绑定了，那么直接可以领取
        snsId = pluginCross.halldata.getUserDataList(task.userTaskUnit.userId, UserKeys.ATT_SNSID)
        if snsId and isinstance(snsId, (str, unicode)) and snsId.find('wx:') == 0:
            task.setProgress(task.progress + 1, fttime.getCurrentTimestamp())
