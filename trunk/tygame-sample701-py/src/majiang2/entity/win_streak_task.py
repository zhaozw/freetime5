# -*- coding=utf-8 -*-
from freetime5.util import ftlog, ftstr
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tyrpcconn
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tycontent
from majiang2.poker2.entity import hallrpcutil


# 历史连胜为所有玩法
HISTORY_WINSTREAKS = 'history_win_streak'
WIN_COUNT = 'winCount'
WIN_MAX_COUNT = 'winMaxCount'
WIN_TASKS = 'winTasks'
WIN_DESC = 'desc'
REWARDS = 'rewards'
ROOMID = 'roomId'
FIRSTBLOOD = 'firstBlood'
WIN_TIMES_ONE = 'winTimesOne'
USER_TILE_INFO = 'userTileInfo'
HAS_GET_COUPON = 'WinStreakGetCoupon'

def _getTbData(userId, gameId, roomId):
    '''
    获取连胜任务进度
    '''
    data = pluginCross.mj2weakdata.getDayData(userId, _getDBKey(roomId))
    historyWinStreaks = pluginCross.mj2dao.getHistoryWinStreak(userId)
    hasGetCoupon = pluginCross.mj2dao.getHasGetCoupon(userId)
    ftlog.debug('winStreakTask._getTbData historyWinStreak:', historyWinStreaks, 'historyWinStreaks type:', type(historyWinStreaks), 'hasGetCoupon:', hasGetCoupon)
    if not ROOMID in data:
        data[ROOMID] = 0
    if not WIN_COUNT in data:
        data[WIN_COUNT] = 0
    if not WIN_TIMES_ONE in data:
        data[WIN_TIMES_ONE] = 0
    if not USER_TILE_INFO in data:
        data[USER_TILE_INFO] = {}
    
    if not historyWinStreaks:
        historyWinStreaks = 0
    
    if not hasGetCoupon:
        hasGetCoupon = False
    
    ftlog.debug('winStreakTask._getTbData userId:', userId
                , ' gameId:', gameId
                , ' roomId:', roomId
                , ' data:', data
                , ' historyWinStreaks:', historyWinStreaks
                , ' hasGetCoupon:', hasGetCoupon)
    return data, historyWinStreaks, hasGetCoupon

def _setTbData(userId, gameId, roomId, data, historyWinStreaks, hasGetCoupon=1):
    '''
    保存连胜任务进度
    '''
    rData = pluginCross.mj2weakdata.setDayData(userId, _getDBKey(roomId), data)
    pluginCross.mj2dao.setHistoryWinStreak(userId, historyWinStreaks)
    # 如果之前获得过奖劵 则一直为true
    oldGetCoupon = pluginCross.mj2dao.getHasGetCoupon(userId)
    if not oldGetCoupon and hasGetCoupon:
        pluginCross.mj2dao.setHasGetCoupon(userId, hasGetCoupon)
    ftlog.debug('winStreakTask._setTbData userId:', userId
                , ' gameId:', gameId
                , ' roomId:', roomId
                , ' data:', data
                , ' rData:', rData
                , ' historyWinStreaks:', historyWinStreaks
                , ' hasGetCoupon:', hasGetCoupon)
    return rData

def notifyMsg(userId, gameId, roomId, data, historyWinStreaks, isHistoryMax, firstGetCoupon, config, winOrLoser):
    '''
    通知客户端
    '''
    mp = MsgPack()
    mp.setCmd('game')
    mp.setResult('action', 'winStreakTask')
    mp.setResult('gameId', gameId)
    mp.setResult('roomId', roomId)
    mp.setResult('userId', userId)
    mp.setResult(WIN_COUNT, data[WIN_COUNT])
    mp.setResult(WIN_MAX_COUNT, historyWinStreaks)
    mp.setResult('isHistoryMax', isHistoryMax)
    mp.setResult('firstGetCoupon', firstGetCoupon)
    mp.setResult(FIRSTBLOOD, data[FIRSTBLOOD])
    mp.setResult('winStreaks', winOrLoser)
    mp.setResult('userTileInfo', data[USER_TILE_INFO])
    mp.setResult('desc', config.get(WIN_TASKS, None))
    tyrpcconn.sendToUser(userId, mp)

def _getDBKey(roomId):
    '''
    获取DB键值
    '''
    return 'treasurebox_' + str(roomId)

def _getLastPrize(winCount, tbConfig):
    '''
    根据winCount获取最近的奖励信息
    '''
    result = {}
    if not tbConfig:
        return result
    winTaskInfo = tbConfig.get(WIN_TASKS, {})
    for _configInfo in winTaskInfo:
        configCount = _configInfo.get(WIN_COUNT, 0)
        tempCount = configCount if configCount > winCount else winCount + 1
        result[WIN_COUNT] = tempCount
        result['prize'] = _configInfo['prize']
        if configCount > winCount:
            break
    return result

def getWinStreakTaskAllDesc(tableConfig):
    '''
    获取连胜任务描述信息
    返回值：列表
    '''
    infoWinStreak = []
    if tableConfig and tableConfig.get(WIN_TASKS, None):
        winTaskList = tableConfig.get(WIN_TASKS, None)
        for winTask in winTaskList:
            winTaskMsg = '%d连胜奖励：%s' % (winTask[WIN_COUNT], winTask['prize'])
            infoWinStreak.append(winTaskMsg)
    ftlog.debug('WinStreakTask.getWinStreakTaskAllDesc infoWinStreak:', infoWinStreak)
    return infoWinStreak

def getWinStreakTaskInfoProcess(userId, gameId, bigRoomId, tableConfig):
    '''
    获取用户连胜状态信息
    '''
    datas, _, _ = _getTbData(userId, gameId, bigRoomId)
    prizeData = _getLastPrize(datas[WIN_COUNT], tableConfig)
    if not prizeData:
        return None
    return ("%d连胜:%s" % (int(prizeData[WIN_COUNT]), str(prizeData['prize'])))
    
def _getWinStreakInfo(tableConfig, winCount):
    # 根据winCount来获取配置信息
    '''
    return :
    {
        "winCount": 1,
        "rewards": {
            "items": [
                {
                    "count": 10,
                    "itemId": "user:chip"
                }
            ],
            "typeId": "FixedContent"
        },
        "prize": "10金币"
    }
    '''
    if not tableConfig or not winCount:
        return {}
    winTaskInfo = tableConfig.get(WIN_TASKS, {})
    winCount = len(winTaskInfo) if winCount > len(winTaskInfo) else winCount
    for _configInfo in winTaskInfo:
        configCount = _configInfo.get(WIN_COUNT, 0)
        if configCount == winCount:
            return _configInfo
    return {}

def getWinStreakItem(tableConfig, winCount):
    '''
    获取用户的连胜任务奖励信息
    '''
    itemId = ''
    itemCount = 0 
    winStreakInfo = _getWinStreakInfo(tableConfig, winCount)
    if winStreakInfo :
        items = winStreakInfo.get('rewards', {}).get('items', [])
        for item in items:
            if item['count'] > 0:
                itemId = item['itemId']
                itemCount = item['count']
    ftlog.debug('WinStreakTask.getWinStreakItem bigRoomId:', 'itemId=', itemId
                    , 'itemCount=', itemCount)
    return itemId, itemCount

def getWinStreakTableTip(tableConfig, winCount):
    '''
    获取连胜任务奖励描述
    '''
    if tableConfig :
        desc = tableConfig.get(WIN_DESC, None)
        winCountInfo = _getWinStreakInfo(tableConfig, winCount)
        ftlog.debug('WinStreakTask.getWinStreakTableTip tableConfig:', tableConfig
                            , 'desc:', desc
                            , 'winCountInfo:', winCountInfo)
        if winCountInfo:
            winCount = winCountInfo.get(WIN_COUNT, 0)
            prize = winCountInfo.get('prize', '')
            
        if winCount > 0:
            newDesc = ftstr.replaceParams(desc, {"round": winCount, "prize": prize})
            return newDesc
    return ''

def updateStateWithWinStreak(userId, gameId, bigRoomId, winState, tableConfig):
    '''
    更新连胜任务奖励
    winState 表示赢或输
    tableConfig 表示桌子配置信息
    '''
    ftlog.debug('WinStreakTask.updateStateWithWinStreak tableConfig:', tableConfig)
    if not tableConfig.get('roomConfig', None):
        return
    
    roomConfig = tableConfig.get('roomConfig', None)
    winNumList = tableConfig.get('winNumList', 0)
    userTileInfo = tableConfig.get('userTileInfo', {})
    
    # 获取数据库中的相关信息
    datas, historyWinStreaks, hasGetCoupon = _getTbData(userId, gameId, bigRoomId)
    ftlog.debug('WinStreakTask.updateStateWithWinStreak userId:', userId
                , ' gameId:', gameId
                , ' bigRoomId:', bigRoomId
                , 'data:', datas
                , 'historyWinStreaks:', historyWinStreaks
                , 'hasGetCoupon:', hasGetCoupon)
    
    ftlog.debug('WinStreakTask.updateTreasureBoxState->userIds=', userId, 'bigRoomId=', bigRoomId, 'datas=', datas)
    
    # 判断是否为首次连胜，只有在首次连胜中断时为True
    # 首次中断 之前历史战绩为0 玩家loser
    firstFlag = True if (not winState and historyWinStreaks == 0 and datas[WIN_COUNT] != 0) else False
    ftlog.debug('WinStreakTask.updateUserInfoWithWinStreak firstFlag:', firstFlag)
    datas[FIRSTBLOOD] = firstFlag
    datas[ROOMID] = bigRoomId
    rewardCouponFlag = False
    if winState:
        # 如果胜，自动发奖，连胜＋1
        datas[WIN_COUNT] += 1
        if datas[WIN_TIMES_ONE] <= winNumList:
            datas[WIN_TIMES_ONE] = winNumList
            datas[USER_TILE_INFO] = userTileInfo
        rewardCouponFlag = doTreasureBox(userId, gameId, bigRoomId, datas, historyWinStreaks, hasGetCoupon, roomConfig)
    else:
        # 先更新最佳连胜
        isHistoryMax = False
        if historyWinStreaks < datas[WIN_COUNT]:
            historyWinStreaks = datas[WIN_COUNT]
            isHistoryMax = True
        
        notifyMsg(userId, gameId, bigRoomId, datas, historyWinStreaks, isHistoryMax, False, roomConfig, False)
        # 连胜纪录清零
        datas[WIN_COUNT] = 0
    ftlog.debug('WinStreakTask.updateTreasureBoxState historyWinStreaks:', historyWinStreaks)
    # 数据保存
    _setTbData(userId, gameId, bigRoomId, datas, historyWinStreaks, rewardCouponFlag)
        

def doTreasureBox(userId, gameId, bigRoomId, datas, historyWinStreaks, hasGetCoupon, tableConfig):
    # 发送奖励
    ftlog.debug('WinStreakTask.doTreasureBox userId=', userId
                , ' bigRoomId=', bigRoomId
                , ' datas:', datas
                , ' uChip:', hallrpcutil.getChip(userId)
                , ' hasGetCoupon:', hasGetCoupon)
    tbconfiger = _getWinStreakInfo(tableConfig, datas[WIN_COUNT])
    ftlog.debug('WinStreakTask.doTreasureBox tbConfiger:', tbconfiger)
    # 判定房间配置
    if not tbconfiger or not tbconfiger.get('rewards', None) :
        ftlog.debug('WinStreakTask.doTreasureBox->userIds=', userId, 'bigRoomId=', bigRoomId, 'not tbox room !')
        return
    rewards = tbconfiger['rewards']
    
    # 判断奖品是否为奖劵
    rewardCouponFlag = 0
    if 'items' in rewards and 'itemId' in rewards['items'][0]:
        itemId = rewards['items'][0]['itemId']
        if itemId == 'user:coupon':
            rewardCouponFlag = 1
            
    ftlog.debug('WinStreakTask.doTreasureBox hasGetCoupon:', hasGetCoupon, 'rewardCouponFlag:', rewardCouponFlag)
    
    if (not hasGetCoupon) and rewardCouponFlag:
        firstGetCoupon = True
    else:
        firstGetCoupon = False
    ftlog.debug('WinStreakTask.doTreasureBox firstGetCoupon:', firstGetCoupon)
    notifyMsg(userId, gameId, bigRoomId, datas, historyWinStreaks, False, firstGetCoupon, tableConfig, True)

    content = tycontent.decodeFromDict(rewards)
    sitems = content.getItems()
    for si in sitems :
        si.count = int(si.count)
    # 发送道具
    contentItems = content.getItemsDict()
    aslist = hallrpcutil.addAssets(userId,
                                   gameId,
                                   contentItems,
                                   'TASK_OPEN_TBOX_REWARD',
                                   bigRoomId)
    ftlog.debug('winStreakTask.doTreasureBox->userIds=', userId, 'bigRoomId=', bigRoomId, datas)
    
    # 返回是否第一次获得奖卷
    return rewardCouponFlag
