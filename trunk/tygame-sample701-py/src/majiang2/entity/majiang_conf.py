# -*- coding=utf-8 -*-
'''
Created on 2015年9月25日

@author: liaoxx
'''

import copy

from majiang2.entity.uploader import uploadVideo as naviteUploadVideo
from tuyoo5.core import tyconfig
from tuyoo5.core import tyglobal
from freetime5.util import ftlog

ROUND_COUNT = 'roundCount'
REMAIN_MAX_TIME = 'continueSeconds'
ROOMID = 'roomId'
PLAYTIMES = 'playTimes'
LASTTIME = 'lastTime'
# 房间配置名称
ROOM_PATH = 'loop.active.task'

def getMajiangConf(gameId, mainKey, subKey, defaultRet=None):
    datas = tyconfig.getCacheGame0Data(mainKey, gameId, None, None, {})
    return datas.get(subKey, defaultRet)

def getTableRecordConfig():
    return tyconfig.getCacheGame0Data('table_record', tyglobal.gameId(), None, None, {})

def getNormalTableFinishUserLeave(gameId):
    return getMajiangConf(gameId, 'public', 'normal_table_finish_user_leave', 0)

def getNormalTableReadyTimeOut(gameId):
    return getMajiangConf(gameId, 'public', 'normal_table_ready_time_out', 30)

def getRobotInterval(gameId):
    return getMajiangConf(gameId, 'public', "robot-interval", 1)

def get_medal_ui_config(gameId):
    """ 获取medal的ui配置
    """
    return getMajiangConf(gameId, 'ui.config', 'medal.ui.config', {})


def get_room_other_config(gameId):
    """获取房间相关的其他配置"""
    datas = tyconfig.getCacheGame0Data('room_other', gameId, None, None, {})
    return copy.deepcopy(datas)


def getCreateTableConfig(gameId, playMode, key, itemId):
    """获取自建房的配置"""
    config = get_room_other_config(gameId)
    createTable = config.get('create_table_config', {})

    playModeSetting = createTable.get(playMode, None)
    if not playModeSetting:
        return None
    
    itemSetting = playModeSetting.get(key, None)
    if not itemSetting:
        return None
    
    for item in itemSetting:
        if item['id'] == itemId:
            return item
        
    return None

def getCreateTableTotalConfig(gameId):
    """获取自建桌的大配置"""
    config = get_room_other_config(gameId)
    createTable = config.get('create_table_config', {})
    return createTable

def get_play_mode_config_by_clientId(clientId):
    """根据clientId获取自建桌支持的玩法列表"""
    play_mode_list = tyconfig.getTcContentByGameId('room.other', None, tyglobal.gameId(), clientId, [], None)
    ftlog.debug('get_play_mode_config_by_clientId | clientId:', clientId, '| play_mode_list:', play_mode_list)
    return play_mode_list

def get_table_record_msg_path(tableRecordKey, cardCount):
    """ 获取单局牌桌协议文件下载路径
    """
    trConfig = getTableRecordConfig()
    downloadPath = trConfig.get('trDownloadPath', '')
    return '%s%s' % (downloadPath, get_table_record_msg_fileName(tableRecordKey, cardCount))

def get_table_record_msg_fileName(gameId, tableRecordKey, cardCount):
    """ 获取单局牌桌协议文件名
    """
    trConfig = getTableRecordConfig()
    filePath = trConfig.get('trFilePath', '')
    return  '%s/record_%s_%s_%s' % (filePath, gameId, tableRecordKey, cardCount)

def uploadVideo(key, data):
    '''
    key:文件名
    data:文件内容
    '''
    trConfig = getTableRecordConfig()
    uploadKey = trConfig.get('trUploadKey', '')
    uploadUrl = trConfig.get('trUploadUrl', '')
    return naviteUploadVideo(uploadUrl, uploadKey, key, data)

def getTreasureBoxRoomInfo(gameId, bigRoomId, roomPath=''):
    '''
    获取对应房间的循环任务配置
    '''
    if not roomPath:
        return None
    infos = tyconfig.getCacheGame0Data(roomPath, gameId, None, None, {})
    rooms = infos.get('rooms', {})
    return rooms.get(str(bigRoomId), None)

def getTreasureBoxDoubleInfo(gameId, roomPath=''):
    '''
    获取循环任务的翻倍活动配置
    '''
    if not roomPath:
        return None
    infos = tyconfig.getCacheGame0Data(roomPath, gameId, None, None, {})
    return infos.get('double', {})

def getTreasureBoxDescInfo(gameId, roomPath=''):
    '''
    获取循环任务的奖励描述配置
    '''
    if not roomPath:
        return None
    infos = tyconfig.getCacheGame0Data(roomPath, gameId, None, None, {})
    return infos.get('desc', '')
