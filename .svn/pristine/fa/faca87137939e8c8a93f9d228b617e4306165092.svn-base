# -*- coding:utf-8 -*-
'''
Created on 2017年09月27日

@author: zhaol
'''

from majiang2.table.friend_table_define import MFTDefine
from majiang2.table.table_config_define import MTDefine
from tuyoo5.core import tyglobal, tyconfig
from tuyoo5.game import tybireport
from freetime5.util import ftlog

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass
    
def fetchAllRoomInfos(uid, gid, playMode):
    '''
    获取所有的现金桌房间信息
    '''
    if _DEBUG:
        debug('fetchAllRoomInfos->', uid, gid, playMode)
    roomInfos = []
    if playMode:
        ucount_infos = tybireport.getRoomOnLineUserCount(gid, True)
        bigRoomIds = tyglobal.bigRoomIdsMap().keys()
        bigRoomIds.sort()

        if _DEBUG:
            debug('bigRoomIds->', uid, gid, bigRoomIds)

        for bigRoomId in bigRoomIds:
            roomDef = tyconfig.getRoomDefine(bigRoomId)
            roomConfig = roomDef.configure
            if roomConfig.get('playMode', None) == playMode \
                and (not roomConfig.get('ismatch', 0)) \
                and (not roomConfig.get(MFTDefine.IS_CREATE, 0)):
                # 有playMode 非比赛 非自建桌
                roomDesc = {}
                roomDesc["play_mode"] = roomConfig["playMode"]
                roomDesc["min_coin"] = roomConfig[MTDefine.MIN_COIN]
                roomDesc["max_coin"] = roomConfig[MTDefine.MAX_COIN]
                roomDesc["max_table_coin"] = roomConfig.get(MTDefine.MAX_TABLE_COIN, roomDesc["max_coin"])
                roomDesc["base_chip"] = roomConfig["tableConf"]["base_chip"]
                roomDesc["service_fee"] = roomConfig["tableConf"]["service_fee"]
                roomDesc["maima"] = roomConfig["tableConf"].get("maima",0)
                roomDesc["macount"] = roomConfig["tableConf"].get("macount", 0)
                roomDesc["laizi"] = roomConfig["tableConf"].get("laizi", 0)
                roomNameDesc = roomConfig['name']
                roomTaskDesc = roomConfig['tableConf']['taskDesc'] if 'taskDesc' in roomConfig['tableConf'] else ''
                playerCount = ucount_infos[1].get(str(roomDef.bigRoomId), 0)
                ftlog.debug('ucount_infos:', ucount_infos[1]
                            , ' bigRoomId:', roomDef.bigRoomId
                            , ' playerCount:', playerCount)
                
                roomInfos.append([
                    bigRoomId,
                    playerCount,
                    roomNameDesc,
                    roomTaskDesc,
                    "",
                    roomDesc
                ])
    return roomInfos


def fetchAllMatchInfos(uid, gid, playMode):
    '''
    获取所有的比赛桌房间信息
    '''
    roomInfos = []
    if playMode:
        ucount_infos = tybireport.getRoomOnLineUserCount(gid, True)
        bigRoomIds = tyglobal.bigRoomIdsMap().keys()
        bigRoomIds.sort()

        if _DEBUG:
            debug('bigRoomIds->', uid, gid, bigRoomIds)

        for bigRoomId in bigRoomIds:
            roomDef = tyconfig.getRoomDefine(bigRoomId)
            roomConfig = roomDef.configure
            if (roomConfig.get('playMode', None) == playMode) and (roomConfig.get('ismatch', 0)):
                # 比赛
                roomDesc = {}
                roomDesc["play_mode"] = roomConfig["playMode"]
                roomDesc["min_coin"] = roomConfig[MTDefine.MIN_COIN]
                roomDesc["max_coin"] = roomConfig[MTDefine.MAX_COIN]
                roomDesc["max_table_coin"] = roomConfig.get(MTDefine.MAX_TABLE_COIN, roomDesc["max_coin"])
                roomDesc["base_chip"] = roomConfig["tableConf"]["base_chip"]
                roomDesc["service_fee"] = roomConfig["tableConf"]["service_fee"]
                roomNameDesc = roomConfig['name']
                roomTaskDesc = roomConfig['tableConf']['taskDesc'] if 'taskDesc' in roomConfig['tableConf'] else ''
                playerCount = ucount_infos[1].get(str(roomDef.bigRoomId), 0)
                ftlog.debug('ucount_infos:', ucount_infos[1]
                            , ' bigRoomId:', roomDef.bigRoomId
                            , ' playerCount:', playerCount)
                
                roomInfos.append([
                    bigRoomId,
                    playerCount,
                    roomNameDesc,
                    roomTaskDesc,
                    "",
                    roomDesc
                ])
    return roomInfos

if __name__ == '__main__':
    pass
