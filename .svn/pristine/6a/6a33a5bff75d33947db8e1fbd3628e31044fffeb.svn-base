# -*- coding:utf-8 -*-
"""
Created on 2017年8月18日

@author: zhaojiangang
"""
import json
import random
import time
from datetime import datetime
from redis.client import StrictRedis
import sys

from biz.mock import patch, DEFAULT

from freetime5.util import ftlog
from matchcomm.matchs.dao import removeRoomInfo, DaoRoomInfo, DaoMatchStatus, DaoMatchSigninRecord, DaoMatchPlayerInfo, \
    DaoUserSigninRecord, DaoUserMatchHistory, saveRoomInfo, saveMatchStatus, getMatchStatus, saveMatchSigninRecord, \
    loadMatchSigninRecord, removeMatchSigninRecord, loadUserSigninRecord, saveUserSigninRecord, removeUserSigninRecord, \
    saveUserMatchHistory, saveMatchPlayerInfo, getMatchPlayerInfo, removeMatchPlayerInfo, loadMatchPlayerInfo
from tuyoo5.core import tyglobal
from tuyoo5.core.tygame import TYGame
from freetime5.util import fttime

from freetime5.twisted import ftcore
from freetime5.twisted import ftredis

from matchcomm.matchs.interface import MatchPlayerIF, MatchTableController, \
    MatchPlayerNotifier, MatchRankRewardsIF, MatchRankRewards, MatchSigninFeeIF, \
    MatchSigninRecordDao
from matchcomm.matchs.models import MatchTableManager, MatchRoomInfo
from matchcomm.matchs.stage_match.conf import StageMatchConf, StageMatchRulesConfASS
from matchcomm.matchs.stage_match.interfacegame import PokerMatchPlayerNotifier
from matchcomm.matchs.stage_match.match_status import StageMatchStatusDao
from matchcomm.matchs.stage_match.match import MatchArea, MatchMaster, \
    MatchAreaStubLocal, MatchMasterStubLocal

from freetime5._tyserver._entity import ftglobal as __tyglobal




matchConf = {
        "name": "血流成河iPhoneX争霸赛",
        "desc": "20:00开赛\n报名费：12万金币或60钻石或3枚幸运戒指",
        "taskDesc": "赢6局得1元红包",
        "timeRange": "20分钟",
        "fees": [
            {
                "count": 0,
                "itemId": "user:chip",
                "desc": "12万金币",
                "params": {
                    "failure": "您的金币不足，选择其他报名条件或者买个金币礼包吧",
                    "payOrder": {
                        "contains": {
                            "count": 300000,
                            "itemId": "user:chip"
                        },
                        "shelves": [
                            "lessbuychip"
                        ]
                    }
                }
            },
            {
                "count": 0,
                "itemId": "user:diamond",
                "desc": "60钻石",
                "params": {
                    "failure": "您的报名条件不足，请前往钻石商城购买钻石再来抢夺大奖",
                    "payOrder": {
                        "priceDiamond": {
                            "count": 60,
                            "minCount": 60,
                            "maxCount": -1
                        },
                        "buyTypes": [
                            "charge"
                        ]
                    }
                }
            },
            {
                "count": 0,
                "itemId": "item:1020",
                "desc": "3枚幸运戒指",
                "params": {
                    "failure": "您的费用不足，本比赛报名费需3枚幸运戒指"
                }
            }
        ],
        "rank.rewards": [
            {
                "desc": "1元微信红包",
                "rankRange": [1,1],
                "rewards": [
                    {
                        "count": 1,
                        "itemId": "item:2050"
                    }
                ]
            },
            {
                "desc": "1万金币",
                "rankRange": [2,2],
                "rewards": [
                    {
                        "count": 1000000,
                        "itemId": "user:chip"
                    }
                ]
            },
            {
                "desc": "6000金币",
                "rankRange": [3,3],
                "rewards": [
                    {
                        "count": 600000,
                        "itemId": "user:chip"
                    }
                ]
            },
            {
                "desc": "5000金币",
                "rankRange": [4,4],
                "rewards": [
                    {
                        "count": 500000,
                        "itemId": "user:chip"
                    }
                ]
            },
            {
                "desc": "4000金币",
                "rankRange": [5,8],
                "rewards": [
                    {
                        "count": 400000,
                        "itemId": "user:chip"
                    }
                ]
            },
            {
                "desc": "2600金币",
                "rankRange": [9,16],
                "rewards": [
                    {
                        "count": 260000,
                        "itemId": "user:chip"
                    }
                ]
            },
            {
                "desc": "1800金币",
                "rankRange": [17,32],
                "rewards": [
                    {
                        "count": 180000,
                        "itemId": "user:chip"
                    }
                ]
            }
        ],
        "stages": [
            {
                "card.count": 2,
                "name": "晋级赛",
                "rise.user.count": 16,
                "rules": {
                    "rise.user.refer": 80,
                    "score.base.grow": {
                        "base": 200,
                        "incr": 100,
                        "typeId": "incr"
                    },
                    "score.base.grow.times": 60,
                    "score.lose": {
                        "loseScore": 100,
                        "typeId": "fixed"
                    },
                    "typeId": "ass"
                },
                "score.base": 1000,
                "score.calc": {
                    "score": 20000,
                    "typeId": "set"
                }
            },
            {
                "card.count": 2,
                "name": "16强赛",
                "rise.user.count": 8,
                "rules": {
                    "typeId": "dieout"
                },
                "score.base": 100,
                "score.calc": {
                    "rate": 0.2,
                    "typeId": "rate"
                }
            },
            {
                "card.count": 2,
                "name": "8强赛",
                "rise.user.count": 4,
                "rules": {
                    "typeId": "dieout"
                },
                "score.base": 100,
                "score.calc": {
                    "rate": 0.2,
                    "typeId": "rate"
                }
            },
            {
                "card.count": 2,
                "name": "决赛",
                "rise.user.count": 1,
                "rules": {
                    "typeId": "dieout"
                },
                "score.base": 100,
                "score.calc": {
                    "rate": 0.2,
                    "typeId": "rate"
                }
            }
        ],
        "start": {
            "fee.type": 1,
            "maxplaytime": 10800,
            "prepare.times": 10,
            "selectFirstStage": 0,
            "signin.maxsize": 80000,
            "signin.times": 86400,
            "start.speed": 8,
            "table.times": 480,
            "times": {
                "days": {
                    "count": 365,
                    "first": "",
                    "interval": "1d"
                },
                "times_in_day": {
                    "count": 2000,
                    "first": "00:00",
                    "interval": 1
                }
            },
            "type": 2,
            "user.groupsize": 20000,
            "user.maxsize": 20000,
            "user.minsize": 4,
            "user.next.group": 0
        },
        "table.seat.count" : 4,
        "tips": {
            "infos": [
                "积分相同时，按报名先后顺序确定名次。",
                "积分低于淘汰分数线会被淘汰，称打立出局。",
                "打立赛制有局数上限，打满局数会等待他人。",
                "打立阶段，轮空时会记1局游戏。",
                "定局赛制，指打固定局数后按积分排名。",
                "每局会按照开局时的底分结算。",
                "比赛流局时，可能会有积分惩罚。"
            ],
            "interval": 5
        }
    }


class MatchMasterTest(object):
    def __init__(self, matchId, conf):
        self.matchId = matchId
        self.matchConf = conf
        self.groupMap = {}
        
    def groupFinish(self, group):
        pass


class MatchAreaTest(MatchArea):
    def __init__(self, matchId, conf, tableManager):
        self.matchId = matchId
        self.matchConf = conf
        self.tableManager = tableManager
        self._groupMap = {}
        

class RoomTest(object):
    def __init__(self, mathId, roomId, gameId, roomConf):
        self.roomId = roomId
        self.gameId = gameId
        self.conf = roomConf
        self.bigRoomId= mathId
    


class MatchRankRewardsIFTest(MatchRankRewardsIF):
    def __init__(self):
        self.rankRewards = MatchRankRewards()
        self.rankRewards.rankRange = (0, -1)
        self.rankRewards.rewards = [{'itemId':'user:chip', 'count':100}]
        
    def getRankRewards(self, player):
        """
        获取奖励配置
        """
        return self.rankRewards
    
    def sendRankRewards(self, player, rankRewards):
        """
        发放比赛奖励
        """
        ftlog.info('MatchRankRewardsIFTest.sendRankRewards',
                   'userId=', player.userId,
                   'rank=', player.rank,
                   'items=', rankRewards.rewards)


class TableControllerTest(MatchTableController):
    def _winlose(self, table):
        ftlog.info('TableControllerTest._winlose')
        winSeatIndex = random.randint(0, len(table.seats) - 1)
        winlose = table.group.stageConf.baseScore
        seatWinloses = [-winlose for _ in xrange(len(table.seats))]
        seatWinloses[winSeatIndex] = winlose * (len(table.seats) - 1)
        ret = { x:seatWinloses[idx] for idx,x in enumerate(table.getUserIdList())}
        table.group.tableWinlose(table.tableId, table.ccrc, ret)
    
    def startTable(self, table):
        ftlog.info('TableControllerTest.startTable')
        ftcore.runOnceDelay(1, self._winlose, table)


class MatchPlayerIFTest(MatchPlayerIF):
    def setPlayerActive(self, matchId, userId):
        """
        指定player为活动的Player
        @return: True/False
        """
        return True
    
    def savePlayer(self, matchId, userId, instId, roomId, state):
        """
        更新player信息
        """
        pass
    
    def removePlayer(self, matchId, instId, userId):
        """
        删除player信息
        """
        pass


class MatchPlayerNotifierTest(MatchPlayerNotifier):
    def notifyMatchWait(self, player, reason):
        ftlog.info('MatchPlayerNotifierTest.notifyMatchWait',
                   'userId=', player.userId,
                   'reason=', reason)
        ftlog.info('loseScore', player.group.matchRules.loseScore if player.group.stageConf.rulesConf.TYPE_ID ==
                                                                        StageMatchRulesConfASS.TYPE_ID else 0)

    def notifyMatchStart(self, instId, signers):
        ftlog.info('MatchPlayerNotifierTest.notifyMatchStart')

    def notifyStageStart(self, player):
        """
        通知用户进入下一阶段(晋级).
        """
        ftlog.info('MatchPlayerNotifierTest.notifyStageStart',
                   'stageIndex=', player.group.stageIndex,
                   'startStageIndex=', player.group.startStageIndex)


class TGDizhuTest(TYGame):
    def __init__(self):
        super(TGDizhuTest, self).__init__()

    def gameId(self):
        return 6


class MatchStatusDaoTest(StageMatchStatusDao):
    def __init__(self):
        # map<(gameId,matchId), StageMatchStatus>
        self._statusMap = {}
        
    def load(self, gameId, matchId):
        return self._statusMap.get((gameId, matchId))
    
    def save(self, gameId, status):
        self._statusMap[(gameId, status.matchId)] = status
    

redisClient = None
def runRedisCmd(dbName,cIndex,*cmds):
    print cmds
    return redisClient.execute_command(*cmds)


def startSignin(area, master):
    userId = 1001
    for i in xrange(100):
        area.signin(userId + i, 0, {})


class MatchSigninFeeIFTest(MatchSigninFeeIF):
    def collectSigninFee(self, matchInst, userId, feeIndex, signinParams):
        """
        获取报名费
        @return: TYContentItem/None
        """
        pass
    
    def returnSigninFee(self, matchInst, userId, fee):
        """
        退还报名费
        """
        pass
    

class MatchSigninRecordDaoTest(MatchSigninRecordDao):
    def buildKey(self, gameId, matchId, instId, roomId):
        return 'msignin5:%s:%s:%s:%s' % (gameId, matchId, instId, roomId)

    # def save(self, gameId, matchId, instId, roomId, record):
    #     """
    #     记录报名记录
    #     """
    #     jstr = record.toDict()
    #     daobase.executeMixCmd('hset', self.buildKey(gameId, matchId, instId, roomId), record.userId, jstr)

    def save(self, gameId, matchId, instId, roomId, record):
        """
        记录报名记录
        """
        pass
    
    def loadAll(self, gameId, matchId, instId, roomId):
        """
        加载所有报名记录
        """
        return []
    
    def remove(self, gameId, matchId, instId, roomId, userId):
        """
        删除报名记录
        """
        pass
    
    def removeAll(self, gameId, matchId, instId, roomId):
        """
        删除所有报名记录
        """
        pass

    def saveRank(self, gameId, matchId, userId, rank):
        pass


def getBigRoomId(roomId):
    return 6888

def _buildMatchDesc(matchConfig):
    """
    构建比赛简介.

    """
    matchDesc = {}
    matchDesc["name"] = matchConfig.name  # 比赛名称
    matchDesc["desc"] = matchConfig.desc  # 比赛名称
    # 比赛类型 matchConf.start.type
    # 人满  USER_COUNT = 1
    # 定时  TIMING = 2
    matchDesc["startType"] = matchConfig.startConf.type
    if matchDesc["startType"] == 1:
        matchDesc["condition"] = matchConfig.startConf.userCount  # 最少开赛人数
    else:
        matchDesc["condition"] = datetime.fromtimestamp(matchConfig.startConf.calcNextStartTime()).strftime('%Y-%m-%d %H:%M')  # 最近的开赛时间
    matchDesc["ranks"] = [{"start":rank.rankRange[0],"end": rank.rankRange[1],"desc":rank.desc} for rank in
    matchConfig.rankRewardsList]
    matchDesc["fees"] = [fee.desc for fee in matchConfig.fees]
    # TODO totalUserCount
    matchDesc["stages"] = [{"name":stage.name,"riseUserCount":stage.riseUserCount,"totalUserCount":stage.userCountPerGroup} for
                           stage in\
            matchConfig.stages]
    matchDesc["tips"] = matchConfig.tipsConf
    print matchDesc
    return matchDesc

def initDao():
    global redisClient
    redisClient = StrictRedis('127.0.0.1', 6379, 0)
    DaoRoomInfo._ftredis =  MockRedis()
    DaoMatchStatus._ftredis =  MockRedis()
    DaoMatchSigninRecord._ftredis =  MockRedis()
    DaoUserSigninRecord._ftredis =  MockRedis()
    DaoMatchPlayerInfo._ftredis =  MockRedis()
    DaoUserMatchHistory._ftredis =  MockRedis()


def main():
    conf = StageMatchConf(6, 6888).decodeFromDict(matchConf)
    roomId = 68881001
    tableManager = MatchTableManager(conf.gameId, conf.tableSeatCount)
    tableManager.addTables(roomId, roomId * 10000, 500)
    
    tgdizhu = TGDizhuTest()
    # gdata.getBigRoomId = getBigRoomId
    # gdata._datas['tygame.instance.dict'] = {}
    # gdata._datas['tygame.instance.dict'][6] = tgdizhu
    # roomConf = {'name':'测试比赛'}
    # ftcon.global_config['server_id'] = 68881000
    # gdata._datas['big_roomids_map'] = {6888:[68881000]}
    
    initDao()

    room = RoomTest(6888, roomId, 6, conf)
    matchMaster = MatchMaster(room, 6888, conf)
    matchArea = MatchArea(room, 6888, conf, None)
    matchArea.matchPlayerIF = MatchPlayerIFTest()
    matchArea.tableController = TableControllerTest()
    # matchArea.playerNotifier = MatchPlayerNotifierTest()
    matchArea.playerNotifier = PokerMatchPlayerNotifier(room)
    matchArea.tableManager = tableManager
    matchArea.matchSigninFeeIF = MatchSigninFeeIFTest()
    matchArea.signinRecordDao = MatchSigninRecordDaoTest()
    matchArea.matchRankRewardsIF = MatchRankRewardsIFTest()

    matchMaster.matchStatusDao = MatchStatusDaoTest()

    matchMaster.addAreaStub(MatchAreaStubLocal(matchMaster, matchArea))
    matchArea.masterStub = MatchMasterStubLocal(matchMaster)
    matchArea.matchRankRewards = MatchRankRewardsIFTest()


    room.matchArea = matchArea
    
    matchMaster.start()
    matchArea.start()
    
    ftcore.runOnceDelay(5, startSignin, matchArea, matchMaster)



def testConf():
    conf = StageMatchConf(701, 701230).decodeFromDict(matchConf)
    _buildMatchDesc(conf)

def mock():

    patcher4 = patch('tuyoo5.core.tyrpcconn.sendToUser')
    MockClass4 = patcher4.start()
    MockClass4.return_value = DEFAULT

    patcher5 = patch('tuyoo5.core.tyrpcconn.sendToUserList')
    MockClass5 = patcher5.start()
    MockClass5.return_value = DEFAULT


class MockRedis(object):

    def __init__(self):
        self.executeClusterCmd = runRedisCmd


def testRoomInfo():
    roomInfo = MatchRoomInfo()
    roomInfo.roomId = 6666
    roomInfo.playerCount = 5
    roomInfo.signinCount = 10
    roomInfo.startType = 1
    roomInfo.instId = 1001
    roomInfo.startTime = fttime.getCurrentTimestamp()
    roomInfo.signinTime = fttime.getCurrentTimestamp()
    # saveRoomInfo(6,roomInfo)
    removeRoomInfo(6, 6666)
    # redisClient.execute_command('HDEL', 'roomInfo:6', 'aaaa')

def testMatchStatus():
    d = {'seq': 1, 'startTime': fttime.getCurrentTimestamp()}
    jstr = json.dumps(d)
    saveMatchStatus(6, 6666, jstr)

    print getMatchStatus(6, 6666)

def testMatchSigninRecord():
    gameId = 6
    matchId = 6666
    instId = 1010
    roomId = 66661000
    userId = 100001
    jstr ='{"name":"kkk","rank":1}'
    saveMatchSigninRecord(gameId, matchId, instId, roomId, userId,jstr)
    # print loadMatchSigninRecord(gameId, matchId, instId, roomId)
    removeMatchSigninRecord(gameId, matchId, instId, roomId, userId)

def testUserSigninRecord():
    userId = 10001
    record = '{"name":"kkk","rank":1}'
    saveUserSigninRecord(userId, record)
    print loadUserSigninRecord(userId)
    removeUserSigninRecord(userId, record)
    # saveUserMatchHistory(userId,record)

def testMatchPlayerInfo():
    userId = 10001
    matchId = 6666
    info = '{"name":"kkk","rank":1}'
    saveMatchPlayerInfo(userId, matchId, info)
    print getMatchPlayerInfo(userId, matchId)
    # print loadMatchPlayerInfo(userId)
    removeMatchPlayerInfo(userId, matchId)


def testDao():
    initDao()
    # testRoomInfo()
    # testMatchStatus()
    # testMatchSigninRecord()
    # testUserSigninRecord()
    testMatchPlayerInfo()


def testRun():
    ftlog.info('===main===')
    mock()
    ftcore.runOnce(main)
    ftcore.mainloop()

def testRedis():
    redisClient = StrictRedis('127.0.0.1', 6379, 0)
    print redisClient.execute_command("hgetall", 'msignin5:6:6666:1010:66661000')
    print redisClient.hgetall('msignin5:6:6666:1010:66661000')
    print redisClient.execute_command("HGETALL", 'msignin5:6:6666:1010:66661000')
    print "*"*5
    print redisClient.execute_command("hgetall", 'mstatus2:6')
    print redisClient.hgetall('mstatus2:6')
    print redisClient.execute_command("HGETALL", 'mstatus2:6')


if __name__ == '__main__':
    reload(sys)  # reload 才能调用 setdefaultencoding 方法
    sys.setdefaultencoding('utf-8')  # 设置 'utf-8'
    # testRedis()
    # testConf()
    testDao()
    # testRun()
    # print fttime.fromtimestamp(time.time())