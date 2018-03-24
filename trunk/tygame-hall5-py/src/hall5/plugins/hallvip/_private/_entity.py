# -*- coding=utf-8
'''
Created on 2015年7月1日

@author: zhaojiangang
基于：newsvn/hall37-py/tags/tygame-hall5-release-20160913 进行移植

'''
from freetime5.util import ftlog
from hall5.plugins.hallvip._private import _excepttion
from tuyoo5.core import tyconfig
from tuyoo5.core import tygame
from tuyoo5.game import tycontent


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class TYUserVipGiftStatusData(object):

    def __init__(self):
        self.giftStateMap = {}  # key=level, value=state


class TYVipGiftState(object):
    STATE_UNGOT = 0
    STATE_GOT = 1

    def __init__(self, vipLevel, state):
        self.vipLevel = vipLevel
        self.state = state

    @property
    def level(self):
        return self.vipLevel.level


class TYUserVipGiftStatus(object):

    def __init__(self):
        self.giftStateMap = {}  # key=level, value=TYVipGiftState

    def getGiftStateByLevel(self, level):
        return self.giftStateMap.get(level)

    def setGiftState(self, level, giftState):
        assert (isinstance(giftState, TYVipGiftState))
        self.giftStateMap[level] = giftState


class TYUserVipGotGiftResult(object):

    def __init__(self, userVip, vipGiftState, giftItemList):
        self.userVip = userVip  # TYUserVip
        self.vipGiftState = vipGiftState  # TYUserVipGiftStatus
        self.giftItemList = giftItemList  # list<(AssetKindId, count, final)>


class TYUserVipGotGiftEvent(tygame.UserEvent):

    def __init__(self, gameId, userId, gotVipGiftResult):
        super(TYUserVipGotGiftEvent, self).__init__(userId, gameId)
        self.gotVipGiftResult = gotVipGiftResult


class TYUserVip(object):

    def __init__(self, userId, vipExp, vipLevel):
        assert (vipExp >= vipLevel.vipExp
                and (not vipLevel.nextVipLevel
                     or vipExp < vipLevel.nextVipLevel.vipExp))
        self.userId = userId
        self.vipExp = vipExp
        self.vipLevel = vipLevel

    def deltaExpToNextLevel(self):
        if self.vipLevel.nextVipLevel:
            return max(0, self.vipLevel.nextVipLevel.vipExp - self.vipExp)
        return 0


class TYVipLevel(tyconfig.TYConfable):

    def __init__(self):
        self.conf = None
        # 级别，数字
        self.level = None
        # 级别名称
        self.name = None
        # 当前级别最小VIP经验值
        self.vipExp = None
        # 图片
        self.pic = None
        # 说明
        self.desc = None
        # 达到该级别后给什么奖励
        self.rewardContent = None
        # 该级别的礼包
        self.giftContent = None
        # 经验说明
        self.expDesc = None
        # 上一个级别
        self.prevVipLevel = None
        # 下一个级别的level值
        self.nextVipLevelValue = None
        # 下一个级别对象
        self.nextVipLevel = None

    def initWhenLoaded(self, vipLevelMap):
        if self.nextVipLevelValue is not None:
            nextVipLevel = vipLevelMap.get(self.nextVipLevelValue)
            if not nextVipLevel:
                raise _excepttion.TYVipConfException(self.conf,
                                                     'Unknown next vip level %s for %s' % (self.nextVipLevelValue, self.level))
            if nextVipLevel.prevVipLevel:
                raise _excepttion.TYVipConfException(self.conf,
                                                     'The next vip level %s already has prev vip level %s' % (nextVipLevel.level))
            nextVipLevel.prevVipLevel = self
            self.nextVipLevel = nextVipLevel

    def decodeFromDict(self, d):
        self.conf = d
        self.level = d.get('level')
        if not isinstance(self.level, int):
            raise _excepttion.TYVipConfException(d, 'VipLevel.level must be int')
        self.name = d.get('name')
        if not isinstance(self.name, (str, unicode)) or not self.name:
            raise _excepttion.TYVipConfException(d, 'VipLevel.name must be valid string')
        self.vipExp = d.get('exp')
        if not isinstance(self.vipExp, int):
            raise _excepttion.TYVipConfException(d, 'VipLevel.vipExt must be int')
        self.pic = d.get('pic', '')
        if not isinstance(self.pic, (str, unicode)):
            raise _excepttion.TYVipConfException(d, 'VipLevel.pic must be string')
        self.desc = d.get('desc', [])
        if not isinstance(self.desc, list):
            raise _excepttion.TYVipConfException(d, 'VipLevel.desc must be list')
        if self.desc:
            for subDesc in self.desc:
                if not isinstance(subDesc, (str, unicode)):
                    raise _excepttion.TYVipConfException(d, 'VipLevel.desc.item must be string')
        rewardContent = d.get('rewardContent')
        if rewardContent:
            self.rewardContent = tycontent.decodeFromDict(rewardContent)
        giftContent = d.get('giftContent')
        if giftContent:
            self.giftContent = tycontent.decodeFromDict(giftContent)
        self.expDesc = d.get('expDesc', '')
        if not isinstance(self.expDesc, (str, unicode)):
            raise _excepttion.TYVipConfException(d, 'VipLevel.expDesc must be string')
        self.nextVipLevelValue = d.get('nextLevel')
        if (self.nextVipLevelValue is not None
                and not isinstance(self.nextVipLevelValue, int)):
            raise _excepttion.TYVipConfException(d, 'VipLevel.nextVipLevelValue must be int')
        return self
