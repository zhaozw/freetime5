# -*- coding=utf-8
'''
Created on 2015年7月1日

@author: zhaojiangang
基于：newsvn/hall37-py/tags/tygame-hall5-release-20160913 进行移植

'''
from freetime5.util import ftlog
from hall5.plugins.hallvip._private import _excepttion, _entity


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class TYVipSystem(object):

    def __init__(self):
        self._vipLevelMap = {}
        self._vipLevelList = []
        self._assistanceChip = 0
        self._assistanceChipUpperLimit = 0
        self._levelUpDesc = ''
        self._gotGiftDesc = ''
        self._gotAssistanceDesc = ''
        self._levelUpShelves = None
        self.levelUpPayOrder = None

    def reloadConf(self, conf):
        vipLevelMap = {}
        assistanceChip = conf.get('assistanceChip')
        if not isinstance(assistanceChip, int) or assistanceChip <= 0:
            raise _excepttion.TYVipConfException(conf, 'assistanceChip must be int > 0')
        assistanceChipUpperLimit = conf.get('assistanceChipUpperLimit')
        if not isinstance(assistanceChipUpperLimit, int) or assistanceChipUpperLimit < 0:
            raise _excepttion.TYVipConfException(conf, 'assistanceChip must be int >= 0')
        levelUpDesc = conf.get('levelUpDesc', '')
        if not isinstance(levelUpDesc, (str, unicode)):
            raise _excepttion.TYVipConfException(conf, 'levelUpDesc must be string')
        levelUpPayOrder = conf.get('levelUpPayOrder')
        if not isinstance(levelUpPayOrder, dict):
            raise _excepttion.TYVipConfException(conf, 'levelUpPayOrder must be dict')
        gotGiftDesc = conf.get('gotGiftDesc', '')
        if not isinstance(gotGiftDesc, (str, unicode)):
            raise _excepttion.TYVipConfException(conf, 'gotGiftDesc must be string')
        gotAssistanceDesc = conf.get('gotAssistanceDesc', '')
        if not isinstance(gotAssistanceDesc, (str, unicode)):
            raise _excepttion.TYVipConfException(conf, 'gotAssistanceDesc must be string')
        levelsConf = conf.get('levels')
        if not isinstance(levelsConf, list) or not levelsConf:
            raise _excepttion.TYVipConfException(conf, 'vip levels must be list')
        for levelConf in levelsConf:
            vipLevel = _entity.TYVipLevel()
            vipLevel.decodeFromDict(levelConf)
            if vipLevel.level in vipLevelMap:
                raise _excepttion.TYVipConfException(conf, 'duplicate vip level' % (vipLevel.level))
            vipLevelMap[vipLevel.level] = vipLevel

        for vipLevel in vipLevelMap.values():
            vipLevel.initWhenLoaded(vipLevelMap)

        vipLevelList = sorted(vipLevelMap.values(), cmp=lambda x, y: cmp(x.vipExp, y.vipExp))
        # 判读是否循环配置
        for vipLevel in vipLevelList:
            nextVipLevel = vipLevel.nextVipLevel
            while (nextVipLevel):
                if nextVipLevel == vipLevel:
                    raise _excepttion.TYVipConfException(conf, 'Loop vip level %s' % (vipLevel.level))
                nextVipLevel = nextVipLevel.nextVipLevel

        self._vipLevelMap = vipLevelMap
        self._vipLevelList = vipLevelList
        self._assistanceChip = assistanceChip
        self._assistanceChipUpperLimit = assistanceChipUpperLimit
        self._levelUpDesc = levelUpDesc
        self._gotGiftDesc = gotGiftDesc
        self._gotAssistanceDesc = gotAssistanceDesc
        self._levelUpPayOrder = levelUpPayOrder
        ftlog.info('TYVipSystemImpl.reloadConf successed allLevels=', self._vipLevelMap.keys(), 'list=',
                   [l.level for l in vipLevelList])

    def getAssistanceChip(self):
        '''
        获取江湖救急每次的金币数量
        '''
        return self._assistanceChip

    def getAssistanceChipUpperLimit(self):
        '''
        获取江湖救急金币上限
        '''
        return self._assistanceChipUpperLimit

    def getLevelUpDesc(self):
        return self._levelUpDesc

    def getLevelUpPayOrder(self):
        return self._levelUpPayOrder

    def getGotGiftDesc(self):
        return self._gotGiftDesc

    def getGotAssistanceDesc(self):
        return self._gotAssistanceDesc

    def findVipLevelByLevel(self, level):
        '''
        根据级别查找vip
        @param level: 要查找的vip的级别
        @return: 找到的 TYVip，没找到返回None
        '''
        return self._vipLevelMap.get(level)

    def findVipLevelByVipExp(self, vipExp):
        '''
        根据vip经验值查找对应的vip级别
        @param vipExp: vip经验值
        @return: 找到的对应的TYVip，没找到返回None 
        '''
        for vip in self._vipLevelList[::-1]:
            if vipExp >= vip.vipExp:
                return vip
        return self._vipLevelList[0]

    def getAllVipLevel(self):
        '''
        获取所有的vip
        @return: list<TYVipLevel>
        '''
        return self._vipLevelList


class TYUserVipSystem(object):

    def __init__(self, vipSystem, vipDao):
        self._vipSystem = vipSystem
        self._vipDao = vipDao

    def getUserVip(self, userId):
        '''
        获取用户vip
        @param userId: 要获取的用户ID 
        @return: TYUserVip
        '''
        vipExp = self._vipDao.loadVipExp(userId)
        vipLevel = self._vipSystem.findVipLevelByVipExp(vipExp)
        return _entity.TYUserVip(userId, vipExp, vipLevel)

    def getVipInfo(self, userId):
        userVip = self.getUserVip(userId)
        nextVipLevel = userVip.vipLevel.nextVipLevel if userVip.vipLevel.nextVipLevel else userVip.vipLevel
        return {
            'level': userVip.vipLevel.level,
            'name': userVip.vipLevel.name,
            'exp': userVip.vipExp,
            'expCurrent': userVip.vipLevel.vipExp,
            'expNext': nextVipLevel.vipExp,
        }

    def addUserVipExp(self, gameId, userId, toAddExp, eventId, intEventParam):
        '''
        增加vip经验值
        @param gameId: 在那个gameId中增加的经验值，用于统计 
        @param toAddExp: 要增加的经验值
        @param eventId: 导致经验值增加的事件ID
        @param intEventParam: eventId相关参数
        @return: TYUserVip
        '''
        return self._vipDao.incrVipExp(userId, toAddExp)
