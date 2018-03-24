# -*- coding=utf-8 -*-

from datetime import datetime
import time

from freetime5.util import ftlog, ftstr
from freetime5.util.ftmsg import MsgPack
from majiang2.entity import majiang_conf
from tuyoo5.core import tyrpcconn
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tycontent
from majiang2.poker2.entity import hallrpcutil


ROUND_COUNT = 'roundCount'
REMAIN_MAX_TIME = 'continueSeconds'
ROOMID = 'roomId'
PLAYTIMES = 'playTimes'
LASTTIME = 'lastTime'

# 房间配置名称
ROOM_PATH = 'loop.active.task'

def _getTbData(userId, gameId, roomId):
    '''
    获取循环任务进度
    '''
    data = pluginCross.mj2weakdata.getDayData(userId, _getDBKey(roomId))
    if not ROOMID in data:
        data[ROOMID] = 0
    if not PLAYTIMES in data:
        data[PLAYTIMES] = 0
    if not LASTTIME in data:
        data[LASTTIME] = 0
    ftlog.debug('LoopActiveTask._getTbData userId:', userId
                , ' gameId:', gameId
                , ' roomId:', roomId
                , ' data:', data)
    return data

def _setTbData(userId, gameId, roomId, data):
    '''
    保存循环任务进度
    '''
    rData = pluginCross.mj2weakdata.setDayData(userId, _getDBKey(roomId), data)
    ftlog.debug('LoopActiveTask._setTbData userId:', userId
                , ' gameId:', gameId
                , ' roomId:', roomId
                , ' data:', data
                , ' rData:', rData)
    return rData

def notifyMsg(userId, gameId, roomId, data, config, ratio):
    '''
    通知客户端
    '''
    mp = MsgPack()
    mp.setCmd('game')
    mp.setResult('action', 'loopActiveTask')
    mp.setResult('gameId', gameId)
    mp.setResult('roomId', roomId)
    mp.setResult('userId', userId)
    mp.setResult(ROUND_COUNT, config.get(ROUND_COUNT))
    mp.setResult(PLAYTIMES, data[PLAYTIMES])
    mp.setResult('prize', getTreasureTableTip(gameId, roomId))
    mp.setResult('award', config.get('prize'))
    awardItems = config['reward']['items'] if 'reward' in config and 'items' in config['reward'] else None
    mp.setResult('awardItems', awardItems)
    tyrpcconn.sendToUser(userId, mp)

def _getDBKey(roomId):
    '''
    获取DB键值
    '''
    return 'treasurebox_' + str(roomId)

def getUserTbInfo(userId, gameId, bigRoomId):
    '''
    获取用户的循环任务奖励信息
    '''
    datas = _getTbData(userId, gameId, bigRoomId)
    tbplaytimes = datas[PLAYTIMES]
    tblasttime = datas[LASTTIME]
    ftlog.debug('LoopActiveTask.getUserTbInfo userId:', userId
                , ' gameId:', gameId
                , ' bigRoomId:', bigRoomId
                , PLAYTIMES, tbplaytimes
                , LASTTIME, tblasttime
                , 'data:', datas)
    return tbplaytimes, tblasttime, datas

def getTreasureBoxState(userId, gameId, bigRoomId):
    '''
    获取用户的循环任务奖励状态
    '''
    tbplaytimes, tblasttime, _ = getUserTbInfo(userId, gameId, bigRoomId)
    tbconfigers = majiang_conf.getTreasureBoxRoomInfo(gameId, bigRoomId, ROOM_PATH)
    if tbconfigers :
        ctime = int(time.time())
        tbplaycount = tbconfigers[ROUND_COUNT]
        tbcontinuesecodes = tbconfigers[REMAIN_MAX_TIME]
        if tbplaycount < 2 or abs(ctime - tblasttime) > tbcontinuesecodes:
            if tbplaycount < 2:
                tbplaycount = 1
            tbplaytimes = 0
    else:
        tbplaycount = 1
        tbplaytimes = 0
    if tbplaytimes > tbplaycount:
        tbplaytimes = tbplaycount
    ftlog.debug('LoopActiveTask.getTreasureBoxState->userIds=', userId
                , 'bigRoomId=', bigRoomId
                , tbplaytimes, '/', tbplaycount)
    return tbplaytimes, tbplaycount

def getTreasureRewardItem(gameId, bigRoomId):
    '''
    获取用户的循环任务奖励信息
    '''
    tbconfigers = majiang_conf.getTreasureBoxRoomInfo(gameId, bigRoomId, ROOM_PATH)
    itemId = ''
    itemCount = 0 
    if tbconfigers :
        items = tbconfigers.get('reward', {}).get('items', [])
        for item in items:
            if item['count'] > 0:
                itemId = item['itemId']
                itemCount = item['count']
    ftlog.debug('LoopActiveTask.getTreasureRewardItem->bigRoomId=', bigRoomId
                , 'itemId=', itemId
                , 'itemCount=', itemCount)
    return itemId, itemCount

def getTreasureTableTip(gameId, bigRoomId):
    '''
    获取循环任务奖励描述
    '''
    tbconfigers = majiang_conf.getTreasureBoxRoomInfo(gameId, bigRoomId, ROOM_PATH)
    if tbconfigers :
        desc = majiang_conf.getTreasureBoxDescInfo(gameId, ROOM_PATH)
        rRound = tbconfigers.get(ROUND_COUNT, 0)
        prize = tbconfigers.get('prize', '')
        if rRound > 0:
            newDesc = ftstr.replaceParams(desc, {"round": rRound, "prize": prize})
            return newDesc
    return ''


def getLoopTaskInfoProcess(userId, gameId, bigRoomId):
    '''
    获取周期任务信息格式如下：玩1/6局:20金币
    '''
    tbPlayTimes, tbPlayCount = getTreasureBoxState(userId, gameId, bigRoomId)
    tbConfig = majiang_conf.getTreasureBoxRoomInfo(gameId, bigRoomId, ROOM_PATH)
    if tbConfig:
        prize = tbConfig.get('prize', '')
        return ("玩%d/%d局:%s" % (int(tbPlayTimes), int(tbPlayCount), str(prize)))
    return None
    

def updateTreasureBoxState(userId, gameId, bigRoomId):
    '''
    更新循环任务奖励
    '''
    tbconfigers = majiang_conf.getTreasureBoxRoomInfo(gameId, bigRoomId, ROOM_PATH)
    ftlog.debug('LoopActiveTask.updateTreasureBoxState tbconfigers:', tbconfigers)
    if not tbconfigers:
        return
    
    tbplaycount = tbconfigers[ROUND_COUNT]
    tbcontinuesecodes = tbconfigers[REMAIN_MAX_TIME]
    tbplaytimes, tblasttime, datas = getUserTbInfo(userId, gameId, bigRoomId)
    ctime = int(time.time())
    ftlog.debug('LoopActiveTask.updateTreasureBoxState roundCount:', tbplaycount
                , ' continueSeconds:', tbcontinuesecodes
                , ' playTimes:', tbplaytimes
                , ' lastTime:', tblasttime
                , ' delta-T:', abs(ctime - tblasttime))
    
    if abs(ctime - tblasttime) > tbcontinuesecodes:
        tbplaytimes = 0
    tbroomid = bigRoomId
    tblasttime = ctime
    tbplaytimes += 1
    datas[ROOMID] = tbroomid
    datas[LASTTIME] = tblasttime
    ftlog.debug('LoopActiveTask.updateTreasureBoxState->userIds=', userId, 'bigRoomId=', bigRoomId, 'datas=', datas)
    if tbplaytimes == tbplaycount:
        # 自动发奖
        datas[PLAYTIMES] = tbplaytimes
        doTreasureBox(userId, gameId, bigRoomId, datas, tbconfigers)
    else:
        datas[PLAYTIMES] = tbplaytimes % tbplaycount
        _setTbData(userId, gameId, bigRoomId, datas)
        notifyMsg(userId, gameId, bigRoomId, datas, tbconfigers, _getDoubleInfos(gameId))

def doTreasureBox(userId, gameId, bigRoomId, datas, tbconfiger):
    ftlog.debug('LoopActiveTask.doTreasureBox userId=', userId
                , ' bigRoomId=', bigRoomId
                , ' datas:', datas
                , ' uChip:', hallrpcutil.getChip(userId))
    # 判定房间配置
    if not tbconfiger or not tbconfiger.get('reward', None) :
        ftlog.debug('LoopActiveTask.doTreasureBox->userIds=', userId, 'bigRoomId=', bigRoomId, 'not tbox room !')
        return
    
    # tips = getTreasureTableTip(gameId, bigRoomId)
    # 活动加成
    dRatio = _getDoubleInfos(gameId)
    notifyMsg(userId, gameId, bigRoomId, datas, tbconfiger, dRatio)

    # 更新宝箱状态 
    datas[LASTTIME] = int(time.time())
    datas[PLAYTIMES] = 0
    _setTbData(userId, gameId, bigRoomId, datas)

    rewards = tbconfiger['reward']
    content = tycontent.decodeFromDict(rewards)
    sitems = content.getItems()
    for si in sitems :
        si.count = int(si.count * dRatio)
    
    # 发送道具
    contentItems = content.getItemsDict()
    aslist = hallrpcutil.addAssets(userId,
                                   gameId,
                                   contentItems,
                                   'TASK_OPEN_TBOX_REWARD',
                                   bigRoomId)
    ftlog.debug('LoopActiveTask.doTreasureBox->userIds=', userId,
                'bigRoomId=', bigRoomId, 'aslist=', aslist)


START_DATE = 'start.date'
END_DATE = 'end.date'
START_TIME = 'start.time'
END_TIME = 'end.time'
PRIZE_RATIO = 'ratio'

def _getDoubleInfos(gameId):
    '''
    获取加倍比率
    '''
    try:
        act_conf = majiang_conf.getTreasureBoxDoubleInfo(gameId, ROOM_PATH)
        if not act_conf:
            return 1
        dt = datetime.now()
        start_date = datetime.strptime(act_conf[START_DATE], '%Y-%m-%d').date()
        end_date = datetime.strptime(act_conf[END_DATE], '%Y-%m-%d').date()
        cur_date = dt.date()
        if cur_date < start_date or cur_date >= end_date:
            return 1
         
        double_start_time = datetime.strptime(act_conf[START_TIME], '%H:%M').time()
        double_end_time = datetime.strptime(act_conf[END_TIME], '%H:%M').time()
         
        cur_time = dt.time()
        if cur_time >= double_start_time and cur_time < double_end_time:
            return act_conf[PRIZE_RATIO]
    except:
        ftlog.error()
    return 1
