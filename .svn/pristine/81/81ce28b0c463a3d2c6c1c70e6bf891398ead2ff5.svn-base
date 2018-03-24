# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from freetime5.util import ftlog, fttime
from majiang2.ai.play_mode import MPlayMode
from majiang2.entity import uploader, majiang_conf
from majiang2.msg_handler.msg import MMsg
from majiang2.table.table_config_define import MTDefine
from majiang2.table_state.state import MTableState
from majiang2.win_loose_result.one_result import MOneResult
import json
import random
import time
from tuyoo5.game import tysessiondata
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tyrpcconn
from freetime5.twisted import ftcore
from majiang2.poker2.entity.game.tables.table_player import TYPlayer

class MMsgLongNet(MMsg):
    TABLE_CALL = 'table_call'
    
    CHI_DETAILS = 'chi_details'
    PENG_DETAILS = 'peng_details'
    GANG_DETAILS = 'gang_details'
    
    def __init__(self):
        super(MMsgLongNet, self).__init__()
        self.__tipsStr = {
            0 : "赖子皮需要杠完才能胡",
            1 : "赖子是万能牌，但不能吃、碰、杠 ",
            2 : "需开口满足起胡番数才能胡",
            3 : "全求人时需2、5、8作将才能胡",
            4 : "屁胡时，手中有2个赖子及以上不能胡",
            5 : "清一色大胡时，不需2、5、8作将",
            6 : "将一色大胡时，需2、5、8作将",
            7 : "风一色大胡时，不需2、5、8作将",
            8 : "缺一门，才能胡",
            9 : "牌局结束时未打完缺牌要被扣分哦",
            10 : "您已经过胡，本轮无法再胡相同的牌",
            11 : "剩余牌数%d张",
            12 : "鸡胡只能自摸，不能被点炮"
            }
    
    @property
    def tipsStr(self):
        return self.__tipsStr
      
    def table_call_add_card(self, player, tile, state, seatId, timeOut, actionId, extendInfo):
        """给玩家发牌，只给收到摸牌的玩家发这条消息
        参数说明：
        seatId - 发牌玩家的座位号
        {
            "cmd": "send_tile",
            "result": {
                "gameId": 7,
                "gang_tiles": [],
                "peng_tiles": [],
                "chi_tiles": [],
                "timeout": 9,
                "tile": 6,
                "remained_count": 53,
                "seatId": 0,
                "trustee": 0,
                "standup_tiles": [
                    2,
                    3,
                    4,
                    8,
                    12,
                    12,
                    14,
                    19,
                    19,
                    22,
                    23,
                    24,
                    35
                ],
                "action_id": 1
            }
        }
        
        "ting_action": [
            [
                8,
                [
                    [
                        12,
                        1,
                        1
                    ]
                ]
            ],
            [
                2,
                [
                    [
                        12,
                        1,
                        1
                    ]
                ]
            ],
            [
                12,
                [
                    [
                        2,
                        1,
                        3
                    ],
                    [
                        5,
                        1,
                        0
                    ],
                    [
                        8,
                        1,
                        1
                    ]
                ]
            ],
            [
                5,
                [
                    [
                        12,
                        1,
                        1
                    ]
                ]
            ]
        ]
        """
        message = self.createMsgPackResult('send_tile')
        message.setResult('gang_tiles', player.copyGangArray())
        message.setResult('gangFromSeat', player.gangTilesFromSeat)
        message.setResult(self.GANG_DETAILS, player.copyGangDetails())
        
        message.setResult('peng_tiles', player.copyPengArray())
        message.setResult('pengFromSeat', player.pengTilesFromSeat)
        message.setResult(self.PENG_DETAILS, player.copyPengDetails())
        
        message.setResult('chi_tiles', player.copyChiArray())
        message.setResult('chiFromSeat', player.chiTilesFromSeat)
        message.setResult(self.CHI_DETAILS, player.copyChiDetails())
        
        message.setResult('zhan_tiles', player.zhanTiles)
        message.setResult('kou_tiles', player.kouTiles)
        message.setResult('flower_tiles', player.flowers)
        # AI运算需要，这时已经把牌加到手牌中了，消息中挪出新增的牌
        handTiles = player.copyHandTiles()
        if tile in handTiles:
            handTiles.remove(tile)
            
        zhanTiles = player.zhanTiles
        if zhanTiles and zhanTiles in handTiles:
            handTiles.remove(zhanTiles)
        kouTiles = player.kouTiles
        if kouTiles:
            for kouTilePattern in kouTiles:
                for kouTile in kouTilePattern:
                    if kouTile in handTiles:
                        handTiles.remove(kouTile)
        message.setResult('standup_tiles', handTiles)
        ftlog.debug('msg_long_net.table_call_add_card tile:', tile
                          , ' handTilesInPlayer:', player.copyHandTiles()
                          , ' handTilesInMsg:', handTiles)
        
        message.setResult('timeout', timeOut)
        message.setResult('tile', tile)
            
        message.setResult('remained_count', self.tableTileMgr.getTilesLeftCount())
        message.setResult('seatId', seatId)
        message.setResult('trustee', 1 if player.autoDecide else 0)
        message.setResult('action_id', actionId)

        # 定缺时，不能让用户做动作及胡牌。必须先选完缺哪一门 (庄家起手牌要定缺时)
        if not extendInfo.getIsInAbsence():
            gang = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_GANG)
            if gang:
                message.setResult('gang_action', gang)
                pigus = extendInfo.getPigus(MTableState.TABLE_STATE_FANPIGU)
                if pigus:
                    message.setResult('fanpigu_action', pigus)
            ting_action = extendInfo.getTingResult(self.players[seatId].copyTiles(), self.tableTileMgr, seatId, self.tilePatternChecker)
            # 胡牌以后，不发送ting_action字段
            if ting_action and not self.players[seatId].isWon():
                tingliang_action = extendInfo.getTingLiangResult(self.tableTileMgr)
                if tingliang_action:
                    message.setResult('tingliang_action', tingliang_action)
                kou_ting_action = extendInfo.getCanKouTingResult(self.tableTileMgr, seatId)
                if kou_ting_action:
                    message.setResult('kou_ting_action', kou_ting_action)
                else:
                    message.setResult('ting_action', ting_action)

            mao_action = extendInfo.getMaoResult(self.tableTileMgr, seatId)
            if mao_action:
                message.setResult('mao_action', mao_action)

            flower_action = extendInfo.getFlowerResult(self.tableTileMgr, seatId)
            if flower_action:
                message.setResult('flower_action', flower_action)
        
            # 自动胡的时候不下发胡的行为给前端
            if not self.autoWin:
                wins = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_HU)
                if wins and len(wins) > 0:
                    ftlog.debug('table_call_add_card wins: ', wins)
                    message.setResult('win_tile', wins[0]['tile'])
                    message.setResult('win_degree', 1)

        # 定缺时不能继续打牌的
        if extendInfo.getIsInAbsence():
            message.setResult('can_not_play', 1)

        # 缓存消息    
        self.latestMsg[player.curSeatId] = message
        self.send_message(message, player.userId)
        recordUserIds = self.getBroadCastUIDs()
        self.addMsgRecord(message, recordUserIds)
    
    def table_call_tips_task(self, userId, loopTaskInfo='', winStreakInfo='', loopWinTimesInfo='', winStreakAllInfo=[]):
        '''
        发送连胜、周期任务
        '''
        if not loopTaskInfo and not winStreakInfo and not loopWinTimesInfo:
            return 
        message = self.createMsgPackResult('showTaskTips')
        if loopTaskInfo:
            message.setResult('loopTaskInfo', loopTaskInfo)
        if winStreakInfo:
            message.setResult('winStreakInfo', winStreakInfo)
        if loopWinTimesInfo:
            message.setResult('loopWinTimesInfo', loopWinTimesInfo)
        if winStreakAllInfo:
            message.setResult('winStreakAllDesc', winStreakAllInfo)
        self.addMsgRecord(message, userId)
        self.send_message(message, userId)
        
    
    def table_call_show_tips(self, tips_num, player):
        """发送提示消息 前端根据tips_num来显示对应的消息
        """
        if player.isRobot():
            return 
        # 缺牌提示，利用player中showTipQueTimes控制次数
        if tips_num == MTDefine.TIPS_NUM_8:
            if player.showTipsQueTimes > 1 or player.isWon():
                return 
            else:
                player.incrShowTipsQueTimes()
        
        if tips_num == MTDefine.TIPS_NUM_11:
            tips_str = self.tipsStr.get(tips_num, "%d") % self.tableTileMgr.getTilesLeftCount()
        else:
            tips_str = self.tipsStr.get(tips_num, "")
              
        message = self.createMsgPackResult('showtips')
        message.setResult('tips', tips_str)
        self.addMsgRecord(message, player.userId)
        self.send_message(message, player.userId)
    
    def table_call_notifyTimeOut(self, seatId, timeOut, times):
        '''
        玩家超时消息通知，1、12秒 
        广播消息
        '''
        uidList = self.getBroadCastUIDs()
        message = self.createMsgPackResult('notifyTimeOut')
        message.setResult('seatId', seatId)
        message.setResult('timeOut', timeOut)
        message.setResult('times', times)
        self.addMsgRecord(message, uidList)
        self.send_message(message, uidList)
      
    def table_call_absence_end(self, userId, seatId, absenceColor, player, tile, isReconnect=False, state=0, extendInfo=None, actionId=0, banker=-1, timeOut=12):
        """所有人定缺完毕"""
        message = self.createMsgPackResult('absence_end')
        message.setResult('seatId', seatId)
        message.setResult('color', absenceColor)
        message.setResult('timeOut', timeOut)
        
        message.setResult('reconnect', isReconnect)

        if banker != -1:   
            message.setResult('banker', banker)
        if actionId:
            message.setResult('action_id', actionId)
        if tile:
            message.setResult('tile', tile)
            message.setResult('gang_tiles', player.copyGangArray())
            message.setResult('gangFromSeat', player.gangTilesFromSeat)
            message.setResult(self.GANG_DETAILS, player.copyGangDetails())
            
            message.setResult('peng_tiles', player.copyPengArray())
            message.setResult('pengFromSeat', player.pengTilesFromSeat)
            message.setResult(self.PENG_DETAILS, player.copyPengDetails())
            
            message.setResult('chi_tiles', player.copyChiArray())
            message.setResult('chiFromSeat', player.chiTilesFromSeat)
            message.setResult(self.CHI_DETAILS, player.copyChiDetails())
            
            handTiles = player.copyHandTiles()
            if (tile in handTiles):
                handTiles.remove(tile)
            message.setResult('standup_tiles', handTiles)
        
        if (0 == state) or (not extendInfo):
            self.send_message(message, userId)
            self.addMsgRecord(message, userId)
            return
        
        # 定缺时，不能让用户做动作及胡牌。必须先选完缺哪一门 (庄家起手牌要定缺时)
        gang = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_GANG)
        if gang:
            message.setResult('gang_action', gang)
            pigus = extendInfo.getPigus(MTableState.TABLE_STATE_FANPIGU)
            if pigus:
                message.setResult('fanpigu_action', pigus)
                
        ting_action = extendInfo.getTingResult(self.players[seatId].copyTiles(), self.tableTileMgr, seatId, self.tilePatternChecker)
        if ting_action:
            tingliang_action = extendInfo.getTingLiangResult(self.tableTileMgr)
            if tingliang_action:
                message.setResult('tingliang_action', tingliang_action)
            kou_ting_action = extendInfo.getCanKouTingResult(self.tableTileMgr, seatId)
            if kou_ting_action:
                message.setResult('kou_ting_action', kou_ting_action)
            else:
                message.setResult('ting_action', ting_action)

        mao_action = extendInfo.getMaoResult(self.tableTileMgr, seatId)
        if mao_action:
            message.setResult('mao_action', mao_action)

        flower_action = extendInfo.getFlowerResult(self.tableTileMgr, seatId)
        if flower_action:
            message.setResult('flower_action', flower_action)
    
        # 自动胡的时候不下发胡的行为给前端
        if not self.autoWin:
            wins = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_HU)
            if wins and len(wins) > 0:
                ftlog.debug('table_call_add_card wins: ', wins)
                message.setResult('win_tile', wins[0]['tile'])
                message.setResult('win_degree', 1)
        self.send_message(message, userId)
        self.addMsgRecord(message, userId)
        if not isReconnect:
            self.latestMsg[seatId] = message
        
    def table_call_ask_ting(self, seatId, actionId, winNodes, tingAction, timeOut):
        message = self.createMsgPackResult('table_call', 'ask_ting')
        message.setResult('action_id', actionId)
        message.setResult('seatId', seatId)
        message.setResult('all_win_tiles', winNodes)
        message.setResult('timeout', timeOut)
        message.setResult('ting_result', tingAction)
        
        self.latestMsg[seatId] = message
        self.send_message(message, self.players[seatId].userId)
        self.addMsgRecord(message, self.players[seatId].userId)

    def table_call_tian_ting_over(self, seatId, actionId):
        message = self.createMsgPackResult('table_call', 'tian_ting_over')
        message.setResult('action_id', actionId)
        message.setResult('seatId', seatId)
        self.send_message(message, self.players[seatId].userId)
        self.addMsgRecord(message, self.players[seatId].userId)

    def table_call_fang_mao(self
                             , player
                             , mao
                             , maos
                             , state
                             , seatId
                             , timeOut
                             , actionID
                             , extendInfo):
        message = self.createMsgPackResult('fang_mao')
        message.setResult('gang_tiles', player.copyGangArray())
        message.setResult('gangFromSeat', player.gangTilesFromSeat)
        message.setResult(self.GANG_DETAILS, player.copyGangDetails())
        
        message.setResult('peng_tiles', player.copyPengArray())
        message.setResult('pengFromSeat', player.pengTilesFromSeat)
        message.setResult(self.PENG_DETAILS, player.copyPengDetails())
        
        message.setResult('chi_tiles', player.copyChiArray())
        message.setResult('chiFromSeat', player.chiTilesFromSeat)
        message.setResult(self.CHI_DETAILS, player.copyChiDetails())
        
        message.setResult('zhan_tiles', player.zhanTiles)
        message.setResult('kou_tiles', player.kouTiles)
        
        # AI运算需要，这时已经把牌加到手牌中了，消息中挪出新增的牌
        handTiles = player.copyHandTiles()
        ftlog.debug("add_card handTiles = ", handTiles)
            
        zhanTiles = player.zhanTiles
        if zhanTiles and zhanTiles in handTiles:
            handTiles.remove(zhanTiles)
        kouTiles = player.kouTiles
        if kouTiles:
            for kouTilePattern in kouTiles:
                for kouTile in kouTilePattern:
                    if kouTile in handTiles:
                        handTiles.remove(kouTile)
        message.setResult('standup_tiles', handTiles)
        ftlog.debug("add_card standup_tiles = ", handTiles)
        
        message.setResult('timeout', timeOut)
        message.setResult('mao_tiles', player.copyMaoTile())
        message.setResult('mao', mao)
        message.setResult('remained_count', self.tableTileMgr.getTilesLeftCount())
        message.setResult('seatId', seatId)
        message.setResult('trustee', 1 if player.autoDecide else 0)
        message.setResult('action_id', actionID)
        
        gang = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_GANG)
        if gang:
            message.setResult('gang_action', gang)
            pigus = extendInfo.getPigus(MTableState.TABLE_STATE_FANPIGU)
            if pigus:
                message.setResult('fanpigu_action', pigus)
        ting_action = extendInfo.getTingResult(self.players[seatId].copyTiles(), self.tableTileMgr, seatId, self.tilePatternChecker)
        if ting_action:
            tingliang_action = extendInfo.getTingLiangResult(self.tableTileMgr)
            if tingliang_action:
                message.setResult('tingliang_action', tingliang_action)
            kou_ting_action = extendInfo.getCanKouTingResult(self.tableTileMgr, seatId)
            if kou_ting_action:
                message.setResult('kou_ting_action', kou_ting_action)
            else:
                message.setResult('ting_action', ting_action)
                
        mao_action = extendInfo.getMaoResult(self.tableTileMgr, seatId)
        if mao_action:
            message.setResult('mao_action', mao_action)
            
        wins = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_HU)
        if wins and len(wins) > 0:
            ftlog.debug('table_call_add_card wins: ', wins)
            message.setResult('win_tile', wins[0]['tile'])
            message.setResult('win_degree', 1)
         
        # 缓存消息    
        self.latestMsg[player.curSeatId] = message
        self.send_message(message, player.userId)
        self.addMsgRecord(message, player.userId)

    def table_call_add_card_broadcast(self, seatId, timeOut, actionId, uids, tile):
        """通知其他人给某个人发牌
        参数说明：
        seatId 发牌玩家的座位号
        {
            "cmd": "send_tile",
            "result": {
                "remained_count": 54,
                "seatId": 3,
                "gameId": 7,
                "timeout": 9,
                "action_id":12
            }
        }
        """
        message = self.createMsgPackResult('send_tile')
        message.setResult('seatId', seatId)
        message.setResult('remained_count', self.tableTileMgr.getTilesLeftCount())
        message.setResult('timeout', timeOut)
        message.setResult('action_id', actionId)
        if self.tableTileMgr and self.tableTileMgr.players:
            message.setResult('flower_tiles', self.tableTileMgr.players[seatId].flowers)

        if self.players[seatId].isTingLiang():
            # 亮牌时，输出当前用户抓到的牌，否则不要输出用户抓到的牌
            message.setResult('tile', tile)
        ftlog.debug('MMsgLongNet.table_call_add_card_broadcast broadcast add card msg to user:', uids, ' message:', message)
        self.send_message(message, uids)
        
    def table_call_fang_mao_broadcast(self
                        , seatId
                        , timeOut
                        , actionID
                        , userId
                        , maos
                        , mao):
        message = self.createMsgPackResult('fang_maos')
        message.setResult('seatId', seatId)
        message.setResult('remained_count', self.tableTileMgr.getTilesLeftCount())
        message.setResult('timeout', timeOut)
        message.setResult('action_id', actionID)
        message.setResult('mao_tiles', maos)
        message.setResult('mao', mao)
        ftlog.debug('MMsgLongNet.table_call_fang_mao_broadcast broadcast add tiles after fangMao to user:', userId
                    , ' message:', message)
        self.send_message(message, userId)
        
    def table_call_drop(self, seatId, player, tile, state, extendInfo, actionId, timeOut, winTiles=None):
        """通知玩家出牌
        参数：
            seatId - 出牌玩家的ID
            player - 针对出牌做出牌操作的玩家
            tile - 本次出牌
            state - 通知玩家可以做出的选择
            extendInfo - 扩展信息
            actionId - 当前的操作ID
            winTiles - 可能胡哪些牌，某些玩法没有听牌功能，但也要每次提示玩家可胡哪些牌
            tingResult - 可以听牌的牌剩余张数  番薯 还有几张 [番薯，和牌，余数]
        eg:
        {'ting': {'chiTing': []}, 'chi': [[12, 13, 14]]}
        """
        ftlog.debug('table_call_drop longnet player drop tile:', tile
                    , ' seatId:', seatId
                    , ' actionId:', actionId)
        
        message = self.createMsgPackResult('play')
        message.setResult('tile', tile)
        message.setResult('seatId', seatId)
        message.setResult('remained_count', self.tableTileMgr.getTilesLeftCount())
        message.setResult('action_id', actionId)

        hasAction = False
        # 吃
        if state & MTableState.TABLE_STATE_CHI:
            hasAction = True
            patterns = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_CHI)
            message.setResult('chi_action', patterns)
        
        # 碰
        if state & MTableState.TABLE_STATE_PENG:
            hasAction = True
            patterns = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_PENG)
            message.setResult('peng_action', patterns)
            
        # exmao碰
        if state & MTableState.TABLE_STATE_QIANG_EXMAO:
            hasAction = True
            patterns = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_QIANG_EXMAO)
            message.setResult('peng_action', patterns)
        
        # 杠
        if state & MTableState.TABLE_STATE_GANG:
            hasAction = True
            pattern = extendInfo.getChiPengGangResult(MTableState.TABLE_STATE_GANG)
            message.setResult('gang_action', pattern)
            pigus = extendInfo.getPigus(MTableState.TABLE_STATE_FANPIGU)
            if pigus:
                message.setResult('fanpigu_action', pigus)
            
        # 听
        if state & MTableState.TABLE_STATE_GRABTING:
            # "grabTing_action":{"chi_action":[2],"peng_action":27}
            hasAction = True
            grabTingAction = {}
            ces = extendInfo.getChiPengGangTingResult(MTableState.TABLE_STATE_CHI)
            if ces:
                grabTingAction['chi_action'] = ces
                
            pes = extendInfo.getChiPengGangTingResult(MTableState.TABLE_STATE_PENG)
            if pes:
                grabTingAction['peng_action'] = pes
                
            ges = extendInfo.getChiPengGangTingResult(MTableState.TABLE_STATE_GANG)
            if ges:
                grabTingAction['gang_action'] = ges
            
            ges = extendInfo.getChiPengGangTingResult(MTableState.TABLE_STATE_ZHAN)
            if ges:
                grabTingAction['zhan_action'] = ges
            message.setResult('grabTing_action', grabTingAction)
        
        # 和
        if (state & MTableState.TABLE_STATE_HU) and (not self.autoWin):
            hasAction = True
            message.setResult('win_degree', 1)
            message.setResult('win_action', 1)
            
        if hasAction:
            message.setResult('player_seat_id', player.curSeatId)
            message.setResult('timeout', timeOut)
            
        if winTiles is not None:
            message.setResult('winTiles', winTiles)

        tingliang_action = None
        if extendInfo and self.players[seatId].isTing():
            # 客户端听亮和听
            tingliang_action = extendInfo.getTingLiangResult(self.tableTileMgr)
            if tingliang_action:
                message.setResult('tingliang_action', tingliang_action)
        if self.players[seatId].isTing() and not tingliang_action:
            message.setResult('ting', 1)
             
        if player.tingResult:
            message.setResult('ting_result', player.tingResult)
            message.setResult('ishuAll', player.ishuAll)
        # 保存最新的消息
        if hasAction or (player.curSeatId == seatId):
            ftlog.debug('table_call_drop save latestMsg hasAction:', hasAction
                        , ' seatId:', seatId
                        , ' player.seatId:', player.curSeatId)
            self.latestMsg[player.curSeatId] = message
            
        self.addMsgRecord(message, player.userId)
        return message
    
    def sendTableEvent(self, count, userId, seatId):
        """发送table_event消息，实时更新牌桌人数"""
        msg = self.createMsgPackResult('table_event')
        msg.setResult('count', count)
        msg.setResult('players', self.getPlayersInMsg(seatId, False))
        uids = self.getBroadCastUIDs()
        self.send_message(msg, uids)
        self.addMsgRecord(msg, userId)
    
    def broadcastUserSit(self, seatId, userId, is_reconnect, is_host=False):
        """广播用户坐下消息"""
        message = self.createMsgPackResult('sit')
        message.setResult('isTableHost', 1 if is_host else 0)
        message.setResult('seatId', seatId)
        message.setResult('userId', userId)
        message.setResult('ip', tysessiondata.getClientIp(userId))
        message.setResult('name', self.players[seatId].name)
        message.setResult('pic', self.players[seatId].purl)
        message.setResult('sex', self.players[seatId].sex)
        message.setResult('state', self.players[seatId].state)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, userId)
        
    def send_location_message(self, seatId, userId):
        '''
        通知用户的location
        {
            "cmd": "location",
            "result": {
                "gameId": 7,
                "maxSeatN": 4,
                "play_mode": "harbin",
                "players": [
                    {
                        "master_point_level_diff": [
                            26,
                            100
                        ],
                        "name": "MI 3C",
                        "pic": "http://ddz.image.tuyoo.com/avatar/head_coffee.png",
                        "userId": 10788,
                        "master_point": 126,
                        "sex": 0,
                        "week_master_point": 126,
                        "charm": 0,
                        "max_win_sequence_count": 12,
                        "win_sequence_count": 0,
                        "seatId": 0,
                        "coin": 0,
                        "master_point_level": 5,
                        "max_degree": 4,
                        "new_win_sequence_count": 0
                    }
                ],
                "tableId": 750410010200,
                "seatId": 0,
                "roomId": 75041001,
                "tableType": "create"
            }
        }
        
        TODO:
        补充master_point_level等信息
        '''
        message = self.createMsgPackResult('location')
        message.setResult('seatId', seatId)
        message.setResult('maxSeatN', self.playerCount)
        message.setResult('play_mode', self.playMode)
        message.setResult('tableType', self.tableType)

        players = self.getPlayersInMsg(seatId, False)
        message.setResult('players', players)
        self.send_message(message, userId)
        # 录入牌局记录
        self.addMsgRecord(message, userId)
        
    def getPlayersInMsg(self, mySeatId, isReconnect=False):
        ftlog.debug('msg_longnet.getPlayersInMsg players:', self.players
                    , ' playerCount:', self.playerCount)
        
        players = []
        allWinTtiles = [[] for _ in range(self.playerCount)]
        for i in range(self.playerCount):
            if not self.players[i]:
                continue
            allWinTtiles[i] = self.players[i].tingLiangWinTiles
            
        for i in range(self.playerCount):
            if not self.players[i]:
                continue
            
            player = {}
            player['ip'] = tysessiondata.getClientIp(self.players[i].userId)
            player['userId'] = self.players[i].userId
            player['name'] = self.players[i].name
            player['pic'] = self.players[i].purl
            player['sex'] = self.players[i].sex
            player['coin'] = self.players[i].coin
            player['tableCoin'] = self.players[i].getTableCoin(self.gameId, self.tableId)
            player['seatId'] = i
            player['state'] = self.players[i].state
            player['ting'] = self.players[i].isTing()
                
            if isReconnect:
                # 机器人一直是托管状态，不向真实玩家展示托管状态
                player['trustee'] = True if self.players[i].autoDecide and not self.players[i].isRobot() else False
                userHands = self.players[i].copyHandTiles()
                zhanTiles = self.players[i].zhanTiles
                if zhanTiles and zhanTiles in userHands:
                    userHands.remove(zhanTiles)
                player['standup_tiles'] = userHands
                if self.players[i].isTingLiang():
                    # 亮牌时，输出当前用户手牌
                    ftlog.debug('msg_longnet.sendMsgTableInfo seatId:', i
                                , ' isTingLiang')
                    player['tingLiang'] = True
                    player['all_win_tiles'] = allWinTtiles
                   
                # 整理handTile    
                if i != mySeatId:
                    if self.players[i].isTingLiang():
                        # 亮牌情况下，当前用户手牌发放
                        ftlog.debug('msg_longnet.sendMsgTableInfo seatId:', i
                                    , ' isTingLiang, broadcast handTiles to client...')
                        ftlog.debug('tingLiangTilesCurrent Tile', self.players[i].tingLiangTilesCurrent)
                        newHands = []
                        for _ in range(len(userHands) - len(self.players[i].tingLiangTilesCurrent)):
                            newHands.append(0)
                        newHands.extend(self.players[i].tingLiangTilesCurrent)    
                        player['standup_tiles'] = newHands
                        player['liang_tiles'] = self.players[i].tingLiangTilesCurrent
                        ftlog.debug('msg_longnet.sendMsgTableInfo seatId:', i
                                    , ' standup_tiles:', newHands)
                    else:
                        # 隐藏其他玩家手牌
                        ftlog.debug('msg_longnet.sendMsgTableInfo hide handTiles, oldTiles:', self.players[i].copyHandTiles(), 'tiles:', userHands)
                        player['standup_tiles'] = [0 for _ in range(len(userHands))]
                # 玩家换三张的数据
                if i != mySeatId:
                    player['change_tiles'] = [0, 0, 0]
                else:
                    player['change_tiles'] = self.players[i].changeTiles
                    # 添加手牌展示顺序
                    if self.tableTileMgr.handTileColorSort[self.players[i].curSeatId]:
                        player['color_sort'] = self.tableTileMgr.handTileColorSort[self.players[i].curSeatId]
                player['change_tiles_model'] = self.players[i].changeTilesModel
                
                player['gang_tiles'] = self.players[i].copyGangArray()
                player['gangFromSeat'] = self.players[i].gangTilesFromSeat
                player[self.GANG_DETAILS] = self.players[i].copyGangDetails()
                
                player['peng_tiles'] = self.players[i].copyPengArray()
                player['pengFromSeat'] = self.players[i].pengTilesFromSeat
                player[self.PENG_DETAILS] = self.players[i].copyPengDetails()
                
                player['chi_tiles'] = self.players[i].copyChiArray()
                player['chiFromSeat'] = self.players[i].chiTilesFromSeat
                player[self.CHI_DETAILS] = self.players[i].copyChiDetails()
                
                player['ting_tiles'] = self.players[i].copyTingArray()
                player['drop_tiles'] = self.tableTileMgr.menTiles[self.players[i].curSeatId]
                ftlog.debug('msg_longnet.sendMsgTableInfo now dropTiles:', player['drop_tiles'])
                player['zhan_tiles'] = self.players[i].zhanTiles
                player['flower_tiles'] = self.players[i].flowers
                player['flower_scores'] = self.players[i].flowerScores
                # 添加听牌预览断线重连
                player['ting_result'] = self.players[i].copyTingArray()

                gangTiles = [] 
                for gang in self.players[i].copyGangArray():          
                    for gangTile in gang['pattern']:
                        gangTiles.append(gangTile)
                kouTiles = []
                for kouPattern in self.players[i].kouTiles:
                    for kouTile in kouPattern:
                        if kouTile not in gangTiles:
                            kouTiles.append([kouTile, kouTile, kouTile])
                            break
                player['kou_tiles'] = kouTiles
                player['mao_tiles'] = self.players[i].copyMaoTile()
                player['multiWinTiles'] = self.players[i].multiWinTiles
                message = self.latestMsg[mySeatId]
                ftlog.debug('msg_longnet.sendMsgTableInfo lastMsg:', message
                            , ' seatId:', i
                            , ' seatIdReConnected:', mySeatId
                            , ' actionId:', self.actionId)
                
                if message:
                    if i == mySeatId:
                        if (self.actionId == message.getResult('action_id', 0)) and \
                            (message.getCmd() == 'send_tile'):
                            # 发送快照中的手牌
                            ftlog.debug('msg_longnet.sendMsgTableInfo lastMsg:', self.latestMsg
                                        , ' actionId:', self.actionId
                                        , ' seatId:', i)
                            player['standup_tiles'] = message.getResult('standup_tiles', [])
                            ftlog.debug('msg_longnet.sendMsgTableInfo now dropTiles after append:', player['drop_tiles'])
                    
                    '''
                        mySeatId是断线的人，i是play的人
                    '''
                    if True:  # i != mySeatId:
                        if (self.actionId == message.getResult('action_id', 0)) and \
                            (message.getCmd() == 'play') and \
                            (message.getResult('seatId', 0) == i):
                            ftlog.debug('msg_longnet.sendMsgTableInfo lastMsg:', self.latestMsg
                                        , ' actionId:', self.actionId
                                        , ' reconnectSeatId:', mySeatId
                                        , ' seatId:', i, ' play, but I need tile to rebuild..')
                            player['standup_tiles'].append(message.getResult('tile', 0))
                
            ftlog.debug('msg_longnet.sendMsgTableInfo pack player info:', player)        
            players.append(player)
        return players

    def sendMsgInitTils(self, tiles, banker, userId, seatId):
        """发牌
        {
            "cmd": "init_tiles",
            "result": {
                "tiles": [
                    22,
                    24,
                    29,
                    8,
                    14,
                    3,
                    12,
                    12,
                    4,
                    23,
                    2,
                    19,
                    35
                ],
                "gameId": 7,
                "header_seat_id": 0
            }
        }
        """
        message = self.createMsgPackResult('init_tiles')
        message.setResult('tiles', tiles)
        message.setResult('seatId', seatId)
        message.setResult('header_seat_id', banker)
        self.send_message(message, userId)
        self.addMsgRecord(message, userId)
        
    def createMsgPackRequest(self, cmd, action=None):
        """消息里面的公共信息"""
        mp = MsgPack()
        mp.setCmd(cmd)
        if action: 
            mp.setParam('action', action)
        mp.setParam('gameId', self.gameId)
        mp.setParam('roomId', self.roomId)
        mp.setParam('tableId', self.tableId)
        return mp
    
    def createMsgPackResult(self, cmd, action=None):
        """消息里面的公共信息"""
        mp = MsgPack()
        mp.setCmd(cmd)
        if action: 
            mp.setResult('action', action)
        mp.setResult('gameId', self.gameId)
        mp.setResult('roomId', self.roomId)
        mp.setResult('tableId', self.tableId)
        return mp
    
    def getMsgReadyTimeOut(self):
        """自建桌的准备超时"""
        message = self.createMsgPackRequest('table_call', 'friend_table_ready_time_out')
        return message
    
    def table_call_hand_tile_sort(self, seatId, colorList):
        '''
        发送玩家手牌展示顺序
        '''
        message = self.createMsgPackResult('table_call', 'color_sort')
        message.setResult('color_sort', colorList)
        self.send_message(message, self.players[seatId].userId)
        
    
    def table_call_latest_msg(self, seatId):
        """补发最新的消息"""
        message = self.latestMsg[seatId]
        if not message:
            return
        ftlog.debug('table_call_latest_msg message: ', message)
        
        if self.actionId == message.getResult('action_id', 0):
            message.setResult('reconnect', True)
            self.send_message(message, self.players[seatId].userId)
        else:
            ftlog.debug('table_call_latest_msg actionId not match'
                        , ' actionId:', self.actionId
                        , ' actionIdInMsg:', message.getResult('action_id', 0)
                        , ' message:', message
                        , ' no need to send latest msg ......')
    
    def table_call_table_info(self, userId, banker, bankerlasttime, seatId, isReconnect, quanMenFeng, curSeat, tableState, cInfo=None, btInfo=None, dtInfo=None):
        """
        table_info消息
        参数
        1）userId - 发送table_info的用户
        2）banker - 庄家
        3）isReconnect - 是否断线重连
        例子：
        {
            "cmd": "table_info",
            "result": {
                "room_level": "master",
                "maxSeatN": 4,
                "room_coefficient": 6,
                "userId": 10788,
                "header_seat_id": 0,
                "table_product": [
                    {
                        "name": "36\\u4e07\\u91d1\\u5e01",
                        "price": "30",
                        "tip": "36\\u4e07\\u91d1\\u5e01",
                        "buy_type": "direct",
                        "needChip": 0,
                        "addchip": 360000,
                        "picurl": "http://111.203.187.150:8040/hall/pdt/imgs/goods_t300k_2.png",
                        "price_diamond": "300",
                        "type": 1,
                        "id": "TY9999D0030001",
                        "desc": "1\\u5143=12000\\u91d1\\u5e01"
                    }
                ],
                "table_raffle": 1,
                "base_chip": 1200,
                "reconnect": false,
                "seatId": 0,
                "roomId": 75041001,
                "quan_men_feng": 11,
                "tableType": "create",
                "gameId": 7,
                "interactive_expression_config": {
                    "0": {
                        "charm": 120,
                        "cost": 1200,
                        "chip_limit": 1320,
                        "ta_charm": -120
                    },
                    "1": {
                        "charm": 240,
                        "cost": 1200,
                        "chip_limit": 1320,
                        "ta_charm": 240
                    },
                    "2": {
                        "charm": 60,
                        "cost": 600,
                        "chip_limit": 1320,
                        "ta_charm": -60
                    },
                    "3": {
                        "charm": 120,
                        "cost": 600,
                        "chip_limit": 1320,
                        "ta_charm": 120
                    }
                },
                "play_mode": "harbin",
                "taskUnreward": true,
                "room_name": "\\u5927\\u5e08\\u573a",
                "current_player_seat_id": 0,
                "good_tile_chance": 1.5,
                "service_fee": 800,
                "min_coin": 10000,
                "play_timeout": 9,
                "max_coin": -1,
                "table_state": "play",
                "players": [
                    {
                        "ip": "111.203.187.129",
                        "pic": "http://ddz.image.tuyoo.com/avatar/head_coffee.png",
                        "userId": 10788,
                        "sex": 0,
                        "week_master_point": 126,
                        "max_win_sequence_count": 12,
                        "win_sequence_count": 0,
                        "seatId": 0,
                        "master_point_level": 5,
                        "vipInfo": {
                            "vipExp": 0,
                            "vipLevel": {
                                "level": 0
                            }
                        },
                        "ting": 0,
                        "new_win_sequence_count": 0,
                        "max_degree": 4,
                        "member": {
                            "flag": 0
                        },
                        "rank_name": "\\u5168\\u56fd\\u96c0\\u795e\\u699c",
                        "rank_index": 2,
                        "master_point_level_diff": [
                            26,
                            100
                        ],
                        "stat": "playing",
                        "charm": 0,
                        "coin": 21004366,
                        "name": "MI 3C",
                        "master_point": 126
                    },
                    {
                        "stat": "playing",
                        "name": "\\u6211\\u662f\\u738b",
                        "ip": "192.168.10.76",
                        "pic": "http://ddz.image.tuyoo.com/avatar/head_male_1.png",
                        "userId": 1057,
                        "sex": 1,
                        "ting": 0,
                        "seatId": 1,
                        "coin": 703440,
                        "vipInfo": {
                            "vipExp": 0,
                            "vipLevel": {
                                "level": 0
                            }
                        }
                    },
                    {
                        "stat": "playing",
                        "name": "\\u53c1\\u5343\\u5757\\u4e0a\\u4f60",
                        "ip": "192.168.10.76",
                        "pic": "http://ddz.image.tuyoo.com/avatar/head_lotus.png",
                        "userId": 1145,
                        "sex": 1,
                        "ting": 0,
                        "seatId": 2,
                        "coin": 811200,
                        "vipInfo": {
                            "vipExp": 0,
                            "vipLevel": {
                                "level": 0
                            }
                        }
                    },
                    {
                        "stat": "playing",
                        "name": "\\u5c0fEVA",
                        "ip": "192.168.10.76",
                        "pic": "http://ddz.image.tuyoo.com/avatar/head_feimao.png",
                        "userId": 1107,
                        "sex": 0,
                        "ting": 0,
                        "seatId": 3,
                        "coin": 637250,
                        "vipInfo": {
                            "vipExp": 0,
                            "vipLevel": {
                                "level": 0
                            }
                        }
                    }
                ],
                "tableId": 750410010200
            }
        }
        """
        ftlog.debug('MMsgLongNet.table_call_table_info actionId:', self.actionId)
        message = self.createMsgPackResult('table_info')
        message.setResult('action_id', self.actionId)
        message.setResult('maxSeatN', self.playerCount)
        message.setResult('header_seat_id', banker)
        message.setResult('bankerlasttime_id', bankerlasttime)
        message.setResult('room_level', self.roomConf.get('level', ''))
        message.setResult('room_coefficient', self.tableConf.get('room_coefficient', 1))
        if self.tableTileMgr.canDropWhenHaidiLao():
            message.setResult('no_drop_card_count', self.tableTileMgr.haidilaoCount)
        else:
            message.setResult('no_drop_card_count', 0)
        message.setResult('base_chip', self.tableConf.get('base_chip', 0))
        message.setResult('reconnect', isReconnect)
        message.setResult('seatId', seatId)
        message.setResult('quan_men_feng', quanMenFeng)
        message.setResult('tableType', self.tableType)
        message.setResult('play_mode', self.playMode)
        message.setResult('room_name', self.roomConf.get('name', ''))
        message.setResult('current_player_seat_id', curSeat)
        message.setResult('min_coin', self.roomConf.get(MTDefine.MIN_COIN, 0))
        message.setResult('play_timeout', -1)
        message.setResult('max_coin', self.roomConf.get(MTDefine.MAX_COIN, 0))
        message.setResult('table_state', tableState)
        message.setResult('service_fee', self.tableConf.get('service_fee', 0))
        message.setResult('remained_count', len(self.tableTileMgr.tiles))
        message.setResult('chat_chip', self.tableConf.get(MTDefine.TABLE_CHAT_CHIP, 0))
        message.setResult('chat_time', self.tableConf.get(MTDefine.TABLE_CHAT_TIME, 0))
        # 表情保护数值，小于此数值不扣金币
        protectValue = int(self.tableConf.get(MTDefine.BASE_CHIP, 0) * 1.1) + self.tableConf.get(MTDefine.TABLE_CHAT_CHIP, 0)
        message.setResult('protectValue', protectValue)
        pigus = self.tableTileMgr.getPigus()
        if pigus:
            message.setResult('pigus', pigus)
            
        if cInfo:
            message.setResult('create_table_extend_info', cInfo)
        
        if dtInfo:
            message.setResult('paramsOptionInfo', dtInfo)
         
        players = self.getPlayersInMsg(seatId, isReconnect)
        message.setResult('players', players)
        ftlog.debug('MMsgLongNet.table_call_table_info: ', message)
        
        if TYPlayer.isHuman(userId):
            message.setResult('userId', userId)
            self.send_message(message, userId)
            self.addMsgRecord(message, userId)
        else:
            return
        
    def table_call_after_chi(self, lastSeatId, seatId, tile, pattern, timeOut, actionId, player, actionInfo=None, exInfo=None):
        """吃/碰后的广播
        1）吃
        {
            "cmd": "chi",
            "result": {
                "tile": 22,
                "pattern": [22, 23, 24],
                "seatId": 1,
                "player_seat_id": 0,
                "timeout": 12,
                "action_id": 17,
                "gameId": 7
            }
        }
        
         {'ting_action_not_grab': [[1, [[1, 1, 2]]], [26, [[26, 1, 3], [29, 1, 4]]], [27, [[27, 1, 3]]], [28, [[25, 1, 3], [28, 1, 2]]]]}
         
        """
        ftlog.debug('MsgLongnet.table_call_after_chi playerChi:', seatId
                    , ' playerChied:', lastSeatId
                    , ' nowPlayerUserId:', player.curSeatId
                    , ' actionInfo:', actionInfo)
        
        message = self.createMsgPackResult('chi')
        message.setResult('tile', tile)
        message.setResult('pattern', pattern)
        message.setResult('seatId', seatId)
        message.setResult('player_seat_id', lastSeatId)
        message.setResult('timeout', timeOut)
        message.setResult('action_id', actionId)

        hasAction = False
        if (player.curSeatId == seatId):
            if actionInfo.has_key('ting_action'):
                ting_action = actionInfo.get('ting_action', None)
                if ting_action:
                    message.setResult('grabTing', ting_action)
                    hasAction = True

            if actionInfo.has_key('gang_action'):
                gang_action = actionInfo.get('gang_action', None)
                if gang_action:
                    message.setResult('gang_action', gang_action)
                    hasAction = True

                fanpigu_action = actionInfo.get('fanpigu_action', None)
                if fanpigu_action:
                    message.setResult('fanpigu_action', fanpigu_action)
                    hasAction = True

            if actionInfo.has_key('tingliang_action'):
                tingliang_action = actionInfo.get('tingliang_action', None)
                if tingliang_action:
                    message.setResult('tingliang_action', tingliang_action)
                    hasAction = True

            if actionInfo.has_key('ting_action_not_grab'):
                # 和抢听不会并存
                ting_action = actionInfo.get('ting_action_not_grab', None)
                if ting_action:
                    kou_ting_action = actionInfo.get('kou_ting_action', None)
                    if kou_ting_action:
                        message.setResult('kou_ting_action', kou_ting_action)
                    else:
                        message.setResult('ting_action', ting_action)
                    hasAction = True

            # 吃牌后可以放锚
            mao_action = exInfo.getMaoResult(self.tableTileMgr, seatId)
            if mao_action:
                message.setResult('mao_action', mao_action)
                hasAction = True

        ftlog.debug('table_call_after_chi message:', message)
        self.send_message(message, player.userId)
        self.addMsgRecord(message, player.userId)
        if hasAction:
            self.latestMsg[player.curSeatId] = message

    def table_call_after_peng(self, lastSeatId, seatId, tile, timeOut, actionId, player, pattern, actionInfo=None, exInfo=None):
        """吃/碰后的广播
        1）碰
        {
            "cmd": "peng",
            "result": {
                "tile": 19,
                "seatId": 1,
                "player_seat_id": 0,
                "timeout": 12,
                "action_id": 12,
                "gameId": 7
            }
        }
        """
        ftlog.debug('MsgLongnet.table_call_after_peng')
        message = self.createMsgPackResult('peng')
        message.setResult('tile', tile)
        message.setResult('seatId', seatId)
        message.setResult('player_seat_id', lastSeatId)
        message.setResult('timeout', timeOut)
        message.setResult('action_id', actionId)
        if pattern is None:
            pattern = [tile, tile, tile]
        message.setResult('pattern', pattern)

        hasAction = False
        if (player.curSeatId == seatId):
            if actionInfo.has_key('ting_action'):
                ting_action = actionInfo.get('ting_action', None)
                if ting_action:
                    message.setResult('grabTing', ting_action)
                    hasAction = True
            if actionInfo.has_key('gang_action'):
                gang_action = actionInfo.get('gang_action', None)
                if gang_action:
                    message.setResult('gang_action', gang_action)
                    hasAction = True

                fanpigu_action = actionInfo.get('fanpigu_action', None)
                if fanpigu_action:
                    message.setResult('fanpigu_action', fanpigu_action)
                    hasAction = True

            if actionInfo.has_key('tingliang_action'):
                tingliang_action = actionInfo.get('tingliang_action', None)
                if tingliang_action:
                    message.setResult('tingliang_action', tingliang_action)
                    hasAction = True

            if actionInfo.has_key('ting_action_not_grab'):
                # 和抢听不会并存
                ting_action = actionInfo.get('ting_action_not_grab', None)
                if ting_action:
                    kou_ting_action = actionInfo.get('kou_ting_action', None)
                    if kou_ting_action:
                        message.setResult('kou_ting_action', kou_ting_action)
                    else:
                        message.setResult('ting_action', ting_action)
                    hasAction = True
                    
            # 碰牌后可以放锚
            mao_action = exInfo.getMaoResult(self.tableTileMgr, seatId)
            if mao_action:
                message.setResult('mao_action', mao_action)
                hasAction = True

        # 群发消息 花分显示更新
        if actionInfo.has_key('flower_score'):
            # 更新花分
            flower_score = actionInfo.get('flower_score', None)
            message.setResult('flower_score', flower_score)

        self.send_message(message, player.userId)
        self.addMsgRecord(message, player.userId)
        if hasAction:
            self.latestMsg[player.curSeatId] = message

    def table_call_notify_grab_gang(self, lastSeatId, actionId, player, tile):
        '''
        {
            "cmd": "notifyGrabGang",
            "result": {
                "gameId": 198393,
                "roomId":10901,
                "tableId":1309039,
                "tile":3  //被抢杠的牌
                "seatId": 3,      // 被抢杠胡的玩家座位号
                "action_id":9,
                "tilesInfo":Object{...} //遵照lose里面的tilesInfo消息
            }
        }
        '''
        message = self.createMsgPackResult('notifyGrabGang')
        message.setResult('seatId', lastSeatId)
        message.setResult('action_id', actionId)
        message.setResult('tile', tile)
        if player.curSeatId == lastSeatId:
            tileInfo = {
                "tiles": player.copyHandTiles(),  # [1,2,3,4,5]
                "gang": player.copyGangArray(),  # [[1,1,1,1],[9,9,9,9]] 明1&暗杠0, 花色
                "gangFromSeat": player.gangTilesFromSeat,
                self.GANG_DETAILS: player.copyGangDetails(),
                
                "chi": player.copyChiArray(),  # [[2,3,4]]代表吃(1,2,3),(5,6,7)
                "chiFromSeat": player.chiTilesFromSeat,
                self.CHI_DETAILS: player.copyChiDetails(),
                
                "peng": player.copyPengArray(),  # [1,2]代表吃(1,1,1),(2,2,2)
                "pengFromSeat": player.pengTilesFromSeat,
                self.PENG_DETAILS: player.copyPengDetails(),
                
                "zhan": player.zhanTiles,
                "tile" : player.copyHuArray()
                }
            message.setResult('tileInfo', tileInfo)
            
        self.latestMsg[player.curSeatId] = message
        self.send_message(message, player.userId)
        

    def table_call_grab_gang_hu(self, lastSeatId, seatId, actionId, player, gang, exInfo=None):
        ''' 抢杠胡消息
        {
 
            "cmd": "grabGangHu",
            "result": {
                "gameId": 198393,
                "roomId":10901,
                "tableId":1309039,
                "seatId": 3,      //要抢杠胡的玩家座位号
                "player_seat_id": 0,  //被抢杠胡玩家座位号
                "action_id":9,
                "win_tile": 21,           //被抢杠胡的牌
                "win_degree":1,
                "mao_action":1
            }
        }
        '''
        message = self.createMsgPackResult('grabGangHu')
        message.setResult('seatId', seatId)
        message.setResult('player_seat_id', lastSeatId)
        message.setResult('gang', gang)
        message.setResult('actionId', actionId)
        if exInfo:
            choose = exInfo.getChoosedInfo(MTableState.TABLE_STATE_QIANGGANG)
            if choose:
                message.setResult("win_tile", choose['tile'])
                message.setResult('win_degree', 1)
            # 杠牌后可以放锚
            mao_action = exInfo.getMaoResult(self.tableTileMgr, seatId)
            if mao_action:
                message.setResult('mao_action', mao_action)

        self.latestMsg[player.curSeatId] = message
        self.send_message(message, player.userId)

    def table_call_after_gang(self, lastSeatId, seatId, tile, loser_seat_ids, actionId, player, gang, exInfo=None):
        """杠牌广播消息
        {
            "cmd": "gang",
            "result": {
                "tile": 21,
                "pattern": [21, 21, 21, 21]
                "seatId": 3,
                "player_seat_id": 0,
                "loser_seat_ids": [
                    0
                ],
                "gameId": 7
            }
        }
        """
        message = self.createMsgPackResult('gang')
        message.setResult('tile', tile)
        message.setResult('gang', gang)
        message.setResult('seatId', seatId)
        message.setResult('player_seat_id', lastSeatId)
        message.setResult('action_id', actionId)
        message.setResult('loser_seat_ids', loser_seat_ids)

        # 潜江晃晃朝天笑后可以听可以继续杠
        if exInfo and 'addInfo' in exInfo:
            addInfo = exInfo['addInfo']
            gang_action = addInfo.getChiPengGangResult(MTableState.TABLE_STATE_GANG)
            if gang_action:
                message.setResult("gang_action", gang_action)
            ting_action = addInfo.getTingResult(self.players[seatId].copyTiles(), self.tableTileMgr, seatId, self.tilePatternChecker)
            if ting_action:
                message.setResult("ting_action", ting_action)
                
        if exInfo and 'detailChangeScores' in exInfo:
            message.setResult('detailChangeScores', exInfo['detailChangeScores'])
        self.send_message(message, player.userId)
        
        self.addMsgRecord(message, player.userId)


    def table_call_update_genzhuang(self, userId, genTile, double, scores, exInfo=None):
        '''更新跟庄信息
        '''
        message = self.createMsgPackResult('updateGenZhuang')
        message.setResult('genTile', genTile)
        message.setResult('scores', scores)
        message.setResult('double', double)
        if exInfo and 'detailChangeScores' in exInfo:
            message.setResult('detailChangeScores', exInfo['detailChangeScores'])
        self.send_message(message, userId)

        self.addMsgRecord(message, userId)

    def table_call_after_extend_mao(self, lastSeatId, seatId, mao, actionId, player):
        message = self.createMsgPackResult('extend_mao')
        message.setResult('mao', mao)
        message.setResult('seatId', seatId)
        message.setResult('player_seat_id', lastSeatId)
        message.setResult('action_id', actionId)
        self.send_message(message, player.userId)
        self.addMsgRecord(message, player.userId)
    
    def table_call_update_round_count(self, curCount, totalCount):
        '''更新圈数消息
        {
            "cmd": "table_call",
            "result":{
                "action": "updateRoundCount", //更新圈数
                "gameId": 701,
                "roomId": 7309011001,
                "tableId": 73090110010200,
                "curCount": 0, //当前圈数
                "totalCount": [0,1],     //总圈数
            }
        }
        '''
        message = self.createMsgPackResult('table_call', 'updateRoundCount')
        message.setResult('curCount', curCount)
        message.setResult('totalCount', totalCount)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        
    def table_call_smart_operate(self, player, actionId):
        '''
        通知前端响应智能操作
        '''
        message = self.createMsgPackResult('table_call', 'smart_operate')
        message.setResult('seatId', player.curSeatId)
        message.setResult('userId', player.userId)
        message.setResult('action_id', actionId)
        self.send_message(message, player.userId)
    
    def table_call_update_ting_result(self, player):
        '''
        通知前端更新听牌预览
        {
            "cmd": "table_call",
            "result":{
                "action": "updateTingResult", //更新听牌预览消息
                "gameId": 701,
                "roomId": 7309011001,
                "tableId": 73090110010200,
                "seatId":2 //座位号
                "tingResult": [] //list格式
                 
            }
        }    
        '''
        message = self.createMsgPackResult('table_call', 'updateTingResult')
        message.setResult('seatId', player.curSeatId)
        message.setResult('tingResult', player.tingResult)
        message.setResult('ishuAll', player.ishuAll)
        self.send_message(message, player.userId)
    
    
    def table_call_ask_comb(self, player, seatId, combIds, isReconnect):
        '''comb 消息
        
        {
            "cmd": "table_call",
            "result":{
                "action": "ask_comb", //换牌的action
                "gameId": 701,
                "roomId": 7309011001,
                "tableId": 73090110010200,
                "seatId": 0,
                "combId": [0,1],     //comb的两个玩家seatId
            }
        }
        '''
        message = self.createMsgPackResult('table_call', 'ask_comb') 
        message.setResult('seatId', seatId)
        message.setResult('combId', combIds)
        message.setResult('isReconnect', isReconnect)
        return message
            
    def table_call_after_zhan(self, lastSeatId, seatId, tile, timeOut, actionId, player, pattern, actionInfo=None):
        """粘牌广播消息
        {
            "cmd": "zhan",
            "result": {
                "tile": 21,
                "pattern": [21, 21]
                "seatId": 3,
                "player_seat_id": 0,
                "gameId": 7
            }
        }
        """
        ftlog.debug('MsgLongnet.table_call_after_peng')
        message = self.createMsgPackResult('zhan')
        message.setResult('tile', tile)
        message.setResult('seatId', seatId)
        message.setResult('player_seat_id', lastSeatId)
        message.setResult('timeout', timeOut)
        message.setResult('action_id', actionId)
        if pattern is None:
            pattern = [tile, tile]
        message.setResult('pattern', pattern)
        if (player.curSeatId == seatId):
            if actionInfo.has_key('ting_action'):
                ting_action = actionInfo.get('ting_action', None)
                if ting_action:
                    message.setResult('grabTing', ting_action)
        self.send_message(message, player.userId)
        self.addMsgRecord(message, player.userId)

    def table_call_after_ting(self, player, actionId, userId, allWinTiles, tingResult):
        """听牌消息"""
        isCurrentUser = False
        for userSeatId in range(self.playerCount):
            if self.players[userSeatId].userId == userId:
                if player.curSeatId == userSeatId:
                    isCurrentUser = True
                break
            
        message = self.createMsgPackResult('ting')
        message.setResult('gang_tiles', player.copyGangArray())
        message.setResult('gangFromSeat', player.gangTilesFromSeat)
        message.setResult(self.GANG_DETAILS, player.copyGangDetails())
        
        message.setResult('peng_tiles', player.copyPengArray())
        message.setResult('pengFromSeat', player.pengTilesFromSeat)
        message.setResult(self.PENG_DETAILS, player.copyPengDetails())
        
        message.setResult('chi_tiles', player.copyChiArray())
        message.setResult('chiFromSeat', player.chiTilesFromSeat)
        message.setResult(self.CHI_DETAILS, player.copyChiDetails())
        
        message.setResult('kou_tiles', player.kouTiles)
        
        handTiles = player.copyHandTiles()
        if isCurrentUser:
            message.setResult('standup_tiles', handTiles)
        else:
            newHands = []
            for _ in range(len(handTiles) - len(player.tingLiangTilesCurrent)):
                newHands.append(0)
            newHands.extend(player.tingLiangTilesCurrent)
            message.setResult('standup_tiles', newHands)
            
        message.setResult('mao_tiles', player.copyMaoTile())
        message.setResult('all_win_tiles', allWinTiles)
        message.setResult('ting_result', tingResult)
        message.setResult('seatId', player.curSeatId)
        self.send_message(message, userId)
        self.addMsgRecord(message, userId)

    def round_result_game_over(self, gameFlow, infos, cfFinal):
        '''
        结算协议，在牌局结束的时候发送
        gameFlow － 是否流局
        infos － 玩家的相关信息，包含手牌信息
        cfFinal － 好友桌是否结束，好友桌需要结算
        {
            "cmd":"round_result",
            "result":{
                "gameId":7,
                "roomId":8,
                "tableId" 8343894,
                "timestamp":1473782986.013167,
                "gameFlow":true,
                "create_final":1,
                "infos":[
                    {
                        "userId":1008,
                        "seatId":1,
                        "totalFan":4, //显示总共多少番 目前只有杠分+番型
                        "patternInfo": ["清一色"], //设置为列表，方便扩展
                        "totalScore":20，
                        "tilesInfo":Object{...} //遵照lose里面的tilesInfo消息           
                    },
                    {
         
                    }
                ]
            }
        }
        '''
        message = self.createMsgPackResult('round_result')
        message.setResult('gameFlow', gameFlow)
        message.setResult('timestamp', fttime.getCurrentTimestamp())  # 和牌时间戳
        message.setResult('create_final', cfFinal)
        message.setResult('infos', infos)
        uids = self.getBroadCastUIDs()
        ftlog.debug("msg_longnet.round_result_game_over message:", message)
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)

    def table_call_game_win_loose(self
            , wins
            , looses
            , observers
            , winMode
            , tile
            , scores
            , scoreBase
            , fanPattern
            , customInfo=None
            , piaoPoints=None
            , flowerScores=None
            , horseResult=None
            , displayExtends=None
            , loserFanPattern=None
            , fanPatternTotalBei=None
            ):
        """
        结算
        -1 点炮
        -2 不输不赢
        
        score - 当前积分
        total_score - 目前为止总的输赢积分
        delta_score - 当前局的输赢积分
        customInfo 包含之前的ctInfo btInfo lstInfo
        """
        uids = self.getBroadCastUIDs()
        
        totalScore = scores.get('totalScore')
        if not totalScore:
            totalScore = [0 for _ in range(self.playerCount)]
        deltaScore = scores.get('deltaScore')
        if not deltaScore:
            deltaScore = [0 for _ in range(self.playerCount)]
        deltaGangScore = scores.get('deltaGangScore')
        if not deltaGangScore:
            deltaGangScore = [0 for _ in range(self.playerCount)]
        deltaWinScore = scores.get('deltaWinScore')
        if not deltaWinScore:
            deltaWinScore = [0 for _ in range(self.playerCount)]

        if not customInfo:
            customInfo = {}
            
        ftlog.debug('msg_longnet.table_call_game_win_loose customInfo:', customInfo
                , ' wins:', wins
                , ' looses:', looses
                , ' observers:', observers
                , ' winMode:', winMode
                , ' totalScore:', totalScore
                , ' deltaGangScore:', deltaGangScore
                , ' deltaWinScore:', deltaWinScore
        )
        
        for loosePlayer in looses:
            self.table_call_game_loose(self.players[loosePlayer]
                    , winMode[loosePlayer]
                    , uids
                    , totalScore[loosePlayer]
                    , deltaScore[loosePlayer]
                    , deltaGangScore[loosePlayer]
                    , deltaWinScore[loosePlayer]
                    , scoreBase
                    , fanPattern[loosePlayer]
                    , customInfo
                    , piaoPoints
                    , flowerScores
                    , horseResult
                    , displayExtends[loosePlayer] if displayExtends else None
                    , loserFanPattern[loosePlayer] if loserFanPattern else None
                    , fanPatternTotalBei[loosePlayer] if fanPatternTotalBei else None)
        
        for winPlayer in wins:
            self.table_call_game_win(self.players[winPlayer]
                    , winMode[winPlayer]
                    , tile
                    , uids
                    , totalScore[winPlayer]
                    , deltaScore[winPlayer]
                    , deltaGangScore[winPlayer]
                    , deltaWinScore[winPlayer]
                    , scoreBase
                    , fanPattern[winPlayer]
                    , customInfo
                    , piaoPoints
                    , flowerScores
                    , horseResult
                    , displayExtends[winPlayer] if displayExtends else None
                    , fanPatternTotalBei[winPlayer] if fanPatternTotalBei else None)
        
        for ob in observers:
            self.table_call_game_loose(self.players[ob]
                    , winMode[ob]
                    , uids
                    , totalScore[ob]
                    , deltaScore[ob]
                    , deltaGangScore[ob]
                    , deltaWinScore[ob]
                    , scoreBase
                    , fanPattern[ob]
                    , customInfo
                    , piaoPoints
                    , flowerScores
                    , horseResult
                    , displayExtends[ob] if displayExtends else None)

    def table_call_game_win(self
                            , winPlayer
                            , winMode
                            , tile
                            , uids
                            , totalScore
                            , deltaScore
                            , gangScore
                            , winScore
                            , scoreBase
                            , fanPatternInfo
                            , customInfo
                            , piaoPoints
                            , flowerScores
                            , horseResult
                            , displayExtend=None
                            , fanPatternTotalBei=None):
        """
        注：给赢家发送和牌消息
        
        params：
        1）winType：0是自摸和，1是放炮和
        
        例子：
        {
        "cmd": "win",
        "result": {
            "gameId": 710,
            "roomId": 7105021001,
            "tableId": 71050210010199,
            "seatId": 2,
            "userId": 9597,
            "timestamp": 1479255694,
     
            //分数相关， 总分，这把的分变化，目前为止的分数变化
            "score": 4,
            "delta_score": 5,
            "total_delta_score": 5,
     
            //当前座位的玩家，宝牌信息[牌花，牌数]
            "baopai":[{
                "tile":1
            }],
            //结算界面不需要看，遗弃过的宝牌
             
            //胡牌的模式，cmd>=0 为自己胡
            "winMode": 1,
     
            //当前这把，是否是流局
            "gameFlow": 0,
            //番型 是个 二维数组 [番型名称，番数]
            "patternInfo": [],
            //自建桌信息 是个 对象
            create_table_extend_info : {
                //房间号
                "create_table_no":123456,
                //游戏时长
                "time":123123,
                //是否最后一把
                "create_final":0,
                //当前剩余房卡
                "create_now_cardcount":2,
                //起始时，使用房卡
                "create_total_cardcount":5
            },
            
            //牌面信息
            "tilesInfo": {
                "tiles": [
                    5,
                    5,
                    6,
                    6,
                    6,
                    22,
                    23,
                    18
                ],
                "chi": [
                    [
                        24,
                        25,
                        26
                    ]
                ],
                "peng": [],
                "gang": [
                    {
                        "pattern": [
                            5,
                            5,
                            5,
                            5
                        ],
                        "style": 0
                    }
                ],
                "tile": 18
            }
        }

        """
        message = self.createMsgPackResult('win')
        message.setResult('score', scoreBase + totalScore)
        message.setResult('total_delta_score', totalScore)
        message.setResult('seatId', winPlayer.curSeatId)  # 赢家座位号
        message.setResult('userId', winPlayer.userId)  # 赢家userId

        isBanker = 1
        ftlog.debug('msg_longnet.table_call_game_win customInfo:', customInfo) 
        if 'winNode' in customInfo:
            winNode = customInfo['winNode']
            ftlog.debug('msg_longnet.table_call_game_win winNode:', winNode)
            isBanker = winNode.get('isBanker', 1)
        ftlog.debug('msg_longnet.table_call_game_win isBanker:', isBanker)
        if isBanker:
            message.setResult('tile', tile)  # 和牌的牌
            
        message.setResult('timestamp', fttime.getCurrentTimestamp())  # 和牌时间戳
        # message.setResult('balance', 20000) #赢家金币总额
        # message.setResult('totalCharges', 1000) #该局赢家总钱数(赢了也可能输钱哦)
        # message.setResult('gameFlow', gameFlow) #是否流局(1 流局, 0 不流局)
        # message.setResult('score',  4) #番数, 输了不需要番数
        message.setResult('winMode', winMode)  # 该局赢的类型，0是自摸，1是放炮 -1输了
        if self.tableConf.get(MTDefine.WINLOSE_WINMODE_DESC, 0):
            message.setResult('winModeDesc', self._getWinModeDesc(winMode))
        if customInfo.has_key('ctInfo'):
            ctInfo = customInfo.get('ctInfo', None)
            if ctInfo:
                message.setResult('create_table_extend_info', ctInfo)
        if customInfo.has_key('btInfo'):
            btInfo = customInfo.get('btInfo', None)
            if btInfo:
                message.setResult('baopai', btInfo)
        if customInfo.has_key('lstInfo'):
            lstInfo = customInfo.get('lstInfo', None)
            if lstInfo:
                message.setResult('lastSpeicalTilesInfo', lstInfo)
        if customInfo.has_key('awardInfo'):
            awardInfo = customInfo.get('awardInfo', None)
            if awardInfo:
                message.setResult('awardInfo', awardInfo)
                
        if customInfo.has_key('detailChangeScores'):
            detailChangeScores = customInfo.get('detailChangeScores', None)
            if detailChangeScores:
                message.setResult('detailChangeScores', detailChangeScores[winPlayer.curSeatId])       
                
        if piaoPoints:
            message.setResult('piaoPoints', piaoPoints['points'][winPlayer.curSeatId])
            if self.playMode == MPlayMode.WEIHAI:
                message.setResult('biPiao', piaoPoints['biPiao'])
        if flowerScores:
            message.setResult('flowerScore', flowerScores['scores'][winPlayer.curSeatId])
        if horseResult:
            message.setResult('horseResult', horseResult)
        
        if customInfo.has_key('winNum'):
            winOrder = customInfo.get('winNum', [1, 1, 1, 1])
            if winOrder:
                message.setResult('winNum', winOrder[winPlayer.curSeatId])
        
        if customInfo.has_key('hideTiles'):
            hideTiles = customInfo.get('hideTiles', True)
            if hideTiles:
                message.setResult('hideTiles', 1)

        if customInfo.has_key('todo'):
            todo = customInfo.get('todo', ["leave"])
            if todo:
                message.setResult('todo', todo)
                
        if customInfo.has_key('reconnect'):
            isReconnect = customInfo.get('reconnect', False)
            if isReconnect:
                message.setResult('reconnect', True)
        # 一炮多响胡牌的位置
        message.setResult('multiWinTiles', winPlayer.multiWinTiles)
            
        # 鸡西兑奖分数
        showDeltaScore = deltaScore
        awordTileScore = None
        if customInfo.has_key('awardScores'):
            awordTileScores = customInfo.get('awardScores', None)
            if awordTileScores:
                awordTileScore = awordTileScores[winPlayer.curSeatId]
                showDeltaScore -= awordTileScore
                    
        ftlog.debug('MsgLongnet.table_call_game_win deltaScore:', deltaScore, 'showDeltaScore:', showDeltaScore, 'awordTileScore:', awordTileScore)
            
        # 结算分数发在detail里面
        detailData = {
            "delta_score":showDeltaScore,
            "deltaGangScore":gangScore,
            "deltaWinScore": winScore,
            "total_delta_score":totalScore,
            "score":scoreBase + totalScore,
            "patterns":fanPatternInfo,
            "fanPatternTotalBei": fanPatternTotalBei
        }
        if self.tableConf.get(MTDefine.WINLOSE_DISPLAY_EXTEND, 0):
            titlesConf = self.tableConf.get(MTDefine.DISPLAY_EXTEND_TITLES, [])
            if displayExtend is None:
                displayExtend = [0] * len(titlesConf)
            detailData['display_extend'] = {'titles': self.tableConf.get(MTDefine.DISPLAY_EXTEND_TITLES, []), 'details': displayExtend}

        if awordTileScore:
            detailData["awordTileScore"] = awordTileScore
            message.setResult('awordTileScore', awordTileScore)
            
        message.setResult('detail', detailData)
        message.setResult('delta_score', showDeltaScore)
        
        # 如果是曲靖的十风或者十三幺等特殊牌型,胡牌牌面显示打出的牌
        winHandTiles = winPlayer.copyHandTiles()
        # 有的玩法gameWin需要隐藏赢家手牌
        if customInfo.has_key('hideHandTiles'):
            hideHandTiles = customInfo.get('hideHandTiles', False)
            if hideHandTiles:
                winHandTiles = []
        if customInfo.has_key('dropTiles'):
            dropTiles = customInfo.get('dropTiles', None)
            if dropTiles:
                winHandTiles = dropTiles
        
        if isBanker and (len(winHandTiles) == 14) and (tile in winHandTiles):
            winHandTiles.remove(tile)
        # 手牌信息
        tilesInfo = {
            "tiles": winHandTiles,  # [1,2,3,4,5]
            "gang": winPlayer.copyGangArray(),  # [[1,1,1,1],[9,9,9,9]] 明1&暗杠0, 花色
            "gangFromSeat": winPlayer.gangTilesFromSeat,
            self.GANG_DETAILS: winPlayer.copyGangDetails(),
            
            "chi": winPlayer.copyChiArray(),  # [[2,3,4]]代表吃(1,2,3),(5,6,7)
            "chiFromSeat": winPlayer.chiTilesFromSeat,
            self.CHI_DETAILS: winPlayer.copyChiDetails(),
            
            "peng": winPlayer.copyPengArray(),  # [1,2]代表吃(1,1,1),(2,2,2)
            "pengFromSeat": winPlayer.pengTilesFromSeat,
            self.PENG_DETAILS: winPlayer.copyPengDetails(),
            
            "zhan": winPlayer.zhanTiles,
            "mao": winPlayer.copyMaoTile(),
            "win_tiles": winPlayer.copyHuArray(),
            "win_tiles_seatId": winPlayer.copyHuSeatIdArray()
        }
        ftlog.debug('msg_longnet.table_call_game_win tilesInfo:', tilesInfo)
        
        if isBanker:
            tilesInfo['tile'] = tile
        message.setResult('tilesInfo', tilesInfo)
        
        # 番数信息 patternInfo = [ ["连六", "1番"], ["连六", "1番"] ]
        # message.setResult('patternInfo', fanPatternInfo) #流局没有番型数据, 输了不需要番型数据
        ftlog.debug('msg_longnet.table_call_game_win message: ', message)
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)

    def table_call_game_loose(self
                              , loosePlayer
                              , winMode
                              , uids
                              , totalScore
                              , deltaScore
                              , gangScore
                              , winScore
                              , scoreBase
                              , fanPattern
                              , customInfo
                              , piaoPoints
                              , flowerScores
                              , horseResult
                              , displayExtend=None
                              , loserFanPattern=None
                              , fanPatternTotalBei=None):
        """失败消息
        {
            "cmd": "lose",
            "result": {
                "userId": 1008,
                "seatId": 1,
                "timestamp": 1473782986.013167,
                "gameFlow": true,
                "balance": 937780,
                "totalCharges": -27000,
                "continuous": 0,
                "score": 0,
                "masterPoint": 0,
                "basePoint": 0,
                "roomPoint": 0,
                "memberPoint": 0,
                "winMode": -1,
                "final": true,
                "tilesInfo": {
                    "tiles": [
                        5,
                        5,
                        22,
                        22,
                        22,
                        26,
                        26,
                        27,
                        28,
                        28
                    ],
                    "kong": [],
                    "chow": [
                        15
                    ],
                    "pong": [],
                    "tile": null
                },
                "patternInfo": [],
                "loserInfo": [],
                "gameId": 7,
            }
        }
        """
        message = self.createMsgPackResult('lose')
        message.setResult('score', scoreBase + totalScore)
        message.setResult('total_delta_score', totalScore)
        message.setResult('userId', loosePlayer.userId)
        message.setResult('seatId', loosePlayer.curSeatId)
        message.setResult('timestamp', fttime.getCurrentTimestamp())
        message.setResult('winMode', winMode)
        if self.tableConf.get(MTDefine.WINLOSE_WINMODE_DESC, 0):
            message.setResult('winModeDesc', self._getWinModeDesc(winMode))

        # 鸡西兑奖分数
        showDeltaScore = deltaScore
        awordTileScore = None
        if customInfo.has_key('awardScores'):
            awordTileScores = customInfo.get('awardScores', None)
            if awordTileScores:
                awordTileScore = awordTileScores[loosePlayer.curSeatId]
                showDeltaScore -= awordTileScore
        ftlog.debug('MsgLongnet.table_call_game_win deltaScore:', deltaScore, 'showDeltaScore:', showDeltaScore, 'awordTileScore:', awordTileScore)
        
        detailData = {
            "delta_score":showDeltaScore,
            "deltaGangScore":gangScore,
            "deltaWinScore": winScore,
            "total_delta_score":totalScore,
            "score":scoreBase + totalScore,
            "patterns":fanPattern,
            "loserFanPattern":loserFanPattern,
            "fanPatternTotalBei":fanPatternTotalBei
        }
        if self.tableConf.get(MTDefine.WINLOSE_DISPLAY_EXTEND, 0):
            titlesConf = self.tableConf.get(MTDefine.DISPLAY_EXTEND_TITLES, [])
            if displayExtend is None:
                displayExtend = [0] * len(titlesConf)
            detailData['display_extend'] = {'titles': self.tableConf.get(MTDefine.DISPLAY_EXTEND_TITLES, []), 'details': displayExtend}

        if awordTileScore:
            detailData["awordTileScore"] = awordTileScore
            message.setResult('awordTileScore', awordTileScore)
            
        message.setResult('detail', detailData)
        message.setResult('delta_score', showDeltaScore)
        
        message.setResult('tilesInfo', {
                "tiles": loosePlayer.copyHandTiles(),
                "gang": loosePlayer.copyGangArray(),
                "gangFromSeat": loosePlayer.gangTilesFromSeat,
                self.GANG_DETAILS: loosePlayer.copyGangDetails(),
                
                "chi": loosePlayer.copyChiArray(),
                "chiFromSeat": loosePlayer.chiTilesFromSeat,
                self.CHI_DETAILS: loosePlayer.copyChiDetails(),
                
                "peng": loosePlayer.copyPengArray(),
                "pengFromSeat": loosePlayer.pengTilesFromSeat,
                self.PENG_DETAILS: loosePlayer.copyPengDetails(),
                
                "zhan": loosePlayer.zhanTiles,
                "mao": loosePlayer.copyMaoTile()
        })

        if customInfo.has_key('ctInfo'):
            ctInfo = customInfo.get('ctInfo', None)
            if ctInfo:
                message.setResult('create_table_extend_info', ctInfo)
        if customInfo.has_key('btInfo'):
            btInfo = customInfo.get('btInfo', None)
            if btInfo:
                message.setResult('baopai', btInfo)
        if customInfo.has_key('lstInfo'):
            lstInfo = customInfo.get('lstInfo', None)
            if lstInfo:
                message.setResult('lastSpeicalTilesInfo', lstInfo)
        if customInfo.has_key('awardInfo'):
            awardInfo = customInfo.get('awardInfo', None)
            if awardInfo:
                message.setResult('awardInfo', awardInfo)
        if piaoPoints:
            message.setResult('piaoPoints', piaoPoints['points'][loosePlayer.curSeatId])
            if self.playMode == MPlayMode.WEIHAI:
                message.setResult('biPiao', piaoPoints['biPiao'])
        if flowerScores:
            message.setResult('flowerScore', flowerScores['scores'][loosePlayer.curSeatId])
        if horseResult:
            message.setResult('horseResult', horseResult)
        
        if customInfo.has_key('detailChangeScores'):
            detailChangeScores = customInfo.get('detailChangeScores', None)
            if detailChangeScores:
                message.setResult('detailChangeScores', detailChangeScores[loosePlayer.curSeatId])
        
        uids = []
        for player in self.players:
            uids.append(player.userId)
        
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)
        
    def table_call_game_all_stat(self, terminate, extendBudgets, ctInfo):
        """
        {
        "cmd":"gaming_leave_display_budget",
        "result":
        {
            "create_table_extend_info":
            {
                "create_final":1,
                "create_table_no":"000936",
                "create_now_cardcount":1,
                "create_total_cardcount":2,
                "time":1478278335
            },
            "roomId":78131001,
            "terminate":0 
            "detail":
            [
                {
                    "sid":1,
                    "total_delta_score":-2,
                    "statistics":[
                        {"desc":"自摸","value":0},
                        {"desc":"点炮","value":1},
                        {"desc":"明杠","value":0},
                        {"desc":"暗杠","value":0}
                        {"desc":"最大番数","value":2}
                    ],
                    "head_mark":"dianpao_most"
                },
                {
                    "sid":0,
                    "total_delta_score":2,
                    "statistics":[
                        {"desc":"自摸","value":0},
                        {"desc":"点炮","value":0},
                        {"desc":"明杠","value":0},
                        {"desc":"暗杠","value":0},
                        {"desc":"最大番数","value":2}
                    ],"head_mark":""
                }
            ],
            "gameId":7
            "calcTime":2017-03-14 09:28
        }
        }
            
        """
        calcTime = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        message = self.createMsgPackResult('gaming_leave_display_budget')
        message.setResult('create_table_extend_info', ctInfo)
        message.setResult('terminate', terminate)
        message.setResult('detail', extendBudgets)
        message.setResult('calcTime', calcTime)

        uids = []
        for player in self.players:
            uids.append(player.userId)
        ftlog.debug(message)
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)
        
    def table_call_baopai(self, player, baopai, abandones):
        """通知宝牌
        
        实例：
        {
            "cmd": "baopai",
            "result": {
                "gameId": 7,
                "userId": 10788,
                "tableId": 750410010200,
                "seatId": 0,
                "roomId": 75041001,
                "baopai": [
                    [
                        9,    花色
                        2,    倍数
                        3     剩余张数
                    ]
                ]
            }
        }
        """
        message = self.createMsgPackResult('baopai')
        message.setResult('userId', player.userId)
        message.setResult('seatId', player.curSeatId)
        if baopai:
            message.setResult('baopai', baopai)
        if abandones:
            message.setResult('abandoned', abandones)
        
        ftlog.debug(message)
        self.send_message(message, player.userId) 
        self.addMsgRecord(message, player.userId)

    def table_call_alarm(self, alarmId, player, isAlarm):
        """通知报警
        实例：
        {
            "cmd": "alarm_result",
            "result": {
                "gameId": 7,
                "userId": 10788,
                "tableId": 750410010200,
                "seatId": 0,
                "roomId": 75041001,
                "alarmId":1
                "isAlarm": 1
            }
        }
        """
        message = self.createMsgPackResult('alarm_result')
        message.setResult('userId', player.userId)
        message.setResult('seatId', player.curSeatId)
        message.setResult('alarmId', alarmId)
        if isAlarm:
            message.setResult('isAlarm', isAlarm)

        ftlog.debug(message)
        self.send_message(message, player.userId)
        self.addMsgRecord(message, player.userId)

    def table_chat_broadcast(self, uid, gameId, voiceIdx, msg):
        """广播聊天"""
        mo = self.createMsgPackResult('table_chat')
        mo.setResult('userId', uid)
        mo.setResult('gameId', gameId)
        mo.setResult('isFace', 0)
        if voiceIdx != -1:
            mo.setResult('voiceIdx', voiceIdx)
        mo.setResult('msg', msg)
        users = self.getBroadCastUIDs()
        mo = mo.pack()
        for uid in users :
            tyrpcconn.sendToUser(uid, mo)
        
    def table_chat_to_face(self, uid, gameId, voiceIdx, msg, player):
        """定向发消息"""
        mo = self.createMsgPackResult('table_chat')
        mo.setResult('userId', uid)
        mo.setResult('gameId', gameId)
        mo.setResult('isFace', 1)
        if voiceIdx != -1:
            mo.setResult('voiceIdx', voiceIdx)
        mo.setResult('msg', msg)
        mo.setResult('userName', player.name)
        tyrpcconn.sendToUser(player.userId, mo)
      
    def table_ready_succ_response(self, userId, seatId):
        '''
        通知前端准备成功
        :param userId:玩家id号
        :param seatId:玩家牌桌座位号
        {
            "cmd": "table_call",
            "result": {
                "action": "ready",
                "seatId": 0,
                "gameId": 7
            }
        }
        '''
        message = self.createMsgPackResult('table_call', 'ready')
        message.setResult('seatId', seatId)
        message.setResult('userId', userId)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)
        
        
    def create_table_succ_response(self, userId, seatId, action, tableHost):
        """
        {
            "cmd": "create_table",
            "result": {
                "isTableHost": 1,
                "action": "ready",
                "seatId": 0,
                "gameId": 7
            }
        }
        """
        message = self.createMsgPackResult('create_table', action)
        message.setResult('isTableHost', tableHost)
        message.setResult('seatId', seatId)
        message.setResult('userId', userId)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)
    
    def table_leave(self, userId, seatId, reason=''):
        '''
        后端通知前端leave，统一发送这条消息
        '''
        message = self.createMsgPackResult('leave')
        message.setResult('seatId', seatId)
        message.setResult('userId', userId)
        message.setResult('reason', reason)
        uids = self.getBroadCastUIDs()
        
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)
      
    def create_table_dissolve(self, userId, seatId, state):
        """    
        {
            "cmd": "create_table",
            "result": {
                "action": "leave",
                "seatId": 0,
                "state": "win",
                "gameId": 7
            }
        }
        """
        message = self.createMsgPackResult('create_table', 'leave')
        message.setResult('seatId', seatId)
        message.setResult('state', state)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)
        
    def create_table_dissolve_vote(self, userId, seatId, seatNum, vote_info, vote_detail, vote_name, vote_timeOut):
        message = self.createMsgPackResult('create_table_dissolution')
        message.setResult('seatId', seatId)
        message.setResult('userId', userId)
        message.setResult('seatNum', seatNum)
        message.setResult('vote_info', vote_info)
        message.setResult('vote_info_detail', vote_detail)
        message.setResult('name', vote_name)
        message.setResult('vote_cd', vote_timeOut)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)
        
    # 兼容客户端投票窗口关闭的协议，之后要优化合并 add by taoxc  添加是否需要弹出大结算界面
    def create_table_dissolve_close_vote(self, userId, seatId, isShowBuget=False):
        message = self.createMsgPackResult('user_leave_vote')
        message.setResult('seatId', seatId)
        message.setResult('userId', userId)
        message.setResult('vote_info_detail', [])
        message.setResult('close_vote_cd', 2)
        message.setResult('close_vote', 1)
        message.setResult('show_budget', isShowBuget)
        self.send_message(message, userId)
        self.addMsgRecord(message, userId)
        
    def table_call_fanpigu(self, pigus):
        """发送翻屁股消息"""
        message = self.createMsgPackResult('fanpigu')
        message.setResult('pigus', pigus)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)

    def table_call_buflower(self, tile, uids):
        """发送摸花牌消息"""
        message = self.createMsgPackResult('buflower')
        message.setResult('flower', tile)
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)

    def table_call_crapshoot(self, seatId, points):
        """掷骰子通知"""
        message = self.createMsgPackResult('table_call', 'crapshoot')
        message.setResult('seatId', seatId)  # 谁掷骰子
        message.setResult('points', points)  # 点数
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)

    def table_call_score_message(self, coin, tableCoin, score, delta, isReconnect=False, extendInfo={}):
        """牌桌积分变化"""
        message = self.createMsgPackResult('score')
        message.setResult('score', score)
        message.setResult('delta', delta)
        message.setResult('coin', coin)
        message.setResult('tableCoin', tableCoin)
        message.setResult('isReconnect', isReconnect)
        jiaoScore = extendInfo.get('jiaoScore', None)
        if jiaoScore:
            message.setResult('jiaoScore', jiaoScore)
        return message

    def table_call_score(self, coin, tableCoin, score, delta, isReconnect=False, extendInfo={}):
        """牌桌积分变化"""
        message = self.createMsgPackResult('score')
        message.setResult('score', score)
        message.setResult('delta', delta)
        message.setResult('coin', coin)
        message.setResult('tableCoin', tableCoin)
        message.setResult('isReconnect', isReconnect)
        jiaoScore = extendInfo.get('jiaoScore', None)
        if jiaoScore:
            message.setResult('jiaoScore', jiaoScore)

        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)

    def table_call_detail_desc_message(self, userId, seatId, totalScore, detailDescList, maxFanDesc, extendInfo={}):
        message = self.createMsgPackResult('detailInfo')
        message.setResult('seatId', seatId)
        message.setResult('userId', userId)
        message.setResult('detailDescList', detailDescList)
        message.setResult('totalScore', totalScore)
        message.setResult('maxFanDesc', maxFanDesc)
        self.addMsgRecord(message, userId)

        return message

    def table_call_detail_desc(self, userId, seatId, totalScore, detailDescList, maxFanDesc, extendInfo={}):
        message = self.createMsgPackResult('detailInfo')
        message.setResult('seatId', seatId)
        message.setResult('userId', userId)
        message.setResult('detailDescList', detailDescList)
        message.setResult('totalScore', totalScore)
        message.setResult('maxFanDesc', maxFanDesc)
        self.addMsgRecord(message, userId)
        self.send_message(message, userId)

    def table_call_laizi(self, magicTiles=[], magicFactors=[], banker_seat=0, isReconnect=False):
        """向所有人发送赖子"""
        if (not magicTiles) and (not magicFactors):
            return
        
        message = self.createMsgPackResult(self.TABLE_CALL, 'show_laizi_tiles')
        message.setResult('dice_points', [])
        message.setResult('laizi_tiles', {"tile": magicTiles, "factor": magicFactors})
        message.setResult('banker_seat', banker_seat)
        
        # 断线重连补发消息的标记
        if isReconnect:
            message.setResult('reconnect', isReconnect)
        uids = self.getBroadCastUIDs()
        ftlog.debug("table_call_laizi message:", message)
        self.send_message(message, uids)
        
        # 非断线重连时，保存消息
        if not isReconnect:
            self.addMsgRecord(message, uids)
            
    def table_call_maConfig(self, maType, maCount, isReconnect=False):
        '''
        下发马牌配置
        '''
        message = self.createMsgPackResult(self.TABLE_CALL, 'show_ma_config')
        message.setResult('maType', maType)
        message.setResult('maCount', maCount)
        if isReconnect:
            message.setResult('reconnect', isReconnect)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        # 断线重连不保存消息记录
        if not isReconnect:
            self.addMsgRecord(message, uids)

    def quick_start_err(self, userId):
        messsage = self.createMsgPackResult('quick_start')
        messsage.setError(1, '对不起,该房间已满员')
        self.send_message(messsage, userId)
    
    def trusteeInfo(self, seatId, isTrustee, uid):
        '''
        发送玩家托管状态 广播
        '''
        if isTrustee:
            message = self.createMsgPackResult('set_trustee')
        else:
            message = self.createMsgPackResult('remove_trustee')
            
        message.setResult('seatId', seatId)
        self.send_message(message, uid)

    def table_call_ask_absence(self, userId, seatId, color, timeOut, isReconnect=False, actionId=0):
        """通知前端开始定缺"""
        message = self.createMsgPackResult('ask_absence')
        message.setResult('seatId', seatId)
        message.setResult('color', color)
        message.setResult('timeOut', timeOut)
        # 需通知前端是否有换三张流程
        isChangeTile = self.tableConf.get(MTDefine.THREE_TILE_CHANGE, 0)
        message.setResult('reconnect', isReconnect)
        if not isReconnect and actionId:
            message.setResult('action_id', actionId)
        message.setResult('isChangeTile', isChangeTile)
        self.latestMsg[seatId] = message
        return message
    
    def table_call_notify_absence(self, userId, seatId, color, isReconnect=False, actionId=0):
        """断线重连后，告诉玩家自己选的que"""
        message = self.createMsgPackResult('notify_absence')
        message.setResult('seatId', seatId)
        message.setResult('color', color)
        
        message.setResult('reconnect', isReconnect)
        if not isReconnect and actionId:
            message.setResult('action_id', actionId)
        self.latestMsg[seatId] = message
        self.send_message(message, userId)
        self.addMsgRecord(message, userId)

      
    def table_call_huanSanZhang_end(self, userId, seatId, afterTiles, beforeTiles, handTiles, rule, actionId):
        '''换牌结束'''
        message = self.createMsgPackResult('table_call', 'accept_huanPai')
        message.setResult('seatId', seatId)
        message.setResult('tiles', handTiles)
        message.setResult('afterTiles', afterTiles)
        message.setResult('beforeTiles', beforeTiles)
        message.setResult('huanRule', rule)
        message.setResult('action_id', actionId)
        self.latestMsg[seatId] = message
        self.send_message(message, userId)
        self.addMsgRecord(message, userId)

    def table_call_ask_huansanzhang(self, userId, seatId, huanSolution, forbidChangeTiles, timeOut, actionId):
        message = self.createMsgPackResult('table_call', 'ask_huanPai')
        message.setResult('tiles', huanSolution)
        message.setResult('timeOut', timeOut)
        message.setResult('noChange', forbidChangeTiles)
        message.setResult('seatId', seatId)
        message.setResult('action_id', actionId)
        self.latestMsg[seatId] = message
        return message
    
    def table_call_notify_huansanzhang(self, userId, seatId, actionSeatId, tiles, actionId, isReconnect=False):
        '''
        玩家确认换牌后，通知玩家确认换牌成功
        :param userId: 玩家ID
        :param seatId: 玩家座位的座位号
        :param actionSeatId: 换牌的玩家座位号
        :param tiles:换的哪三张牌
        '''
        message = self.createMsgPackResult('table_call', 'notify_huanPai')
        message.setResult('seatId', actionSeatId)
        message.setResult('action_id', actionId)
        if seatId == actionSeatId:
            message.setResult('tiles', tiles)
            self.latestMsg[seatId] = message
        else:
            message.setResult('tiles', [0, 0, 0])
         
        if isReconnect:
            message.setResult('isReconnect', True)   
            
        self.send_message(message, userId)
        return message
        

    def table_call_ask_piao(self, userId, seatId, piaoSolution, piaoTimeOut):
        message = self.createMsgPackResult('table_call', 'ask_piao')
        message.setResult('setting', piaoSolution)
        message.setResult('timeOut', piaoTimeOut)
        message.setResult('seatId', seatId)
        self.latestMsg[seatId] = message
        self.send_message(message, userId)
        
    def table_call_accept_piao(self, userId, seatId, piaoSolution, piaoTimeOut):
        message = self.createMsgPackResult('table_call', 'accept_piao')
        message.setResult('solution', piaoSolution)
        message.setResult('timeOut', piaoTimeOut)
        message.setResult('seatId', seatId)
        self.latestMsg[seatId] = message
        self.send_message(message, userId)
        
    def table_call_accepted_piao(self, userId, seatId, piaoSolution):
        message = self.createMsgPackResult('table_call', 'accepted_piao')
        message.setResult('solution', piaoSolution)
        message.setResult('seatId', seatId)
        self.latestMsg[seatId] = message
        self.send_message(message, userId)
        
    def table_call_piao(self, userId, seatId, piao):
        message = self.createMsgPackResult('table_call', 'piao')
        message.setResult('piao', piao)
        message.setResult('seatId', seatId)
        self.send_message(message, userId)
        
    def table_call_double_ask(self, uids, actionId, timeOut, doublePoints):
        message = self.createMsgPackResult('table_call', 'ask_double')
        message.setResult('timeOut', timeOut)
        message.setResult('action_id', actionId)
        message.setResult('double', doublePoints)
        self.send_message(message, uids)
        
    def table_call_double_broadcast(self, uids, seatId, doubles):
        message = self.createMsgPackResult('table_call', 'double')
        message.setResult('seatId', seatId)
        message.setResult('double', doubles)
        self.send_message(message, uids)

    def table_call_player_leave(self , online_info_list):
        '''
        长连接掉线了
        '''
        message = self.createMsgPackResult('user_online_info')
        message.setResult('online_info', online_info_list)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        
    def table_call_ping(self, userIds , net_state, time):
        message = self.createMsgPackResult('table_call', 'ping')
        message.setResult('net_state', net_state)
        message.setResult('time', time)
        self.send_message(message, userIds)

    def table_call_bu_flower_broadcast(self, seatId, tile, flowerTiles, flowerScore):
        message = self.createMsgPackResult('bu_flower')
        message.setResult('seatId', seatId)
        message.setResult('tile', tile)
        message.setResult('flower_tiles', flowerTiles)
        message.setResult('flower_score', flowerScore)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)
      
    def table_call_broadcast_charging(self, seatId, actionId, timeOut):
        '''
        广播正在充值的状态
        '''
        message = self.createMsgPackResult('table_call', 'charging')
        message.setResult('seatId', seatId)
        message.setResult('action_id', actionId)
        message.setResult('timeout', timeOut)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)
        
    def table_call_ask_charge(self, seatId, actionId, timeOut, chip, dis, content, promote):
        '''
        询问充值
        '''
        message = self.createMsgPackResult('table_call', 'ask_charge')
        message.setResult('seatId', seatId)
        message.setResult('action_id', actionId)
        message.setResult('timeout', timeOut)
        message.setResult('dis', dis)
        message.setResult('content', content)
        message.setResult('promote', promote)
        # self.send_message(message, self.players[seatId].userId)
        self.addMsgRecord(message, self.players[seatId].curSeatId)
        return message
    
    def table_call_charged(self, seatId, actionId, result, dis):
        '''
        充值结果
        '''
        message = self.createMsgPackResult('table_call', 'charged')
        message.setResult('seatId', seatId)
        message.setResult('action_id', actionId)
        message.setResult('result', result)
        message.setResult('dis', dis)
        uids = self.getBroadCastUIDs()
        self.send_message(message, uids)
        self.addMsgRecord(message, uids)

    def table_call_coin_detail(self, seatId, chargeCoin, uChip, diamond):
        '''
        提示用户带入的多少金币，还剩多少金币，钻石数量等
        {
            "cmd": "table_call",
            "result": {
                "action": "coin_detail",
                "seatId": 0,
                "gameId": 7,
                "coin_content":[] //前端根据数组内容进行显示，几个元素就显示几行
            }
        }
        '''
        message = self.createMsgPackResult('table_call', 'coin_detail')
        message.setResult('seatId', seatId)    
        msgContent = ['补充金币：' + str(chargeCoin), '背包剩余：' + str(uChip), '钻石剩余：' + str(diamond)]
        message.setResult('coin_content', msgContent)
        self.send_message(message, self.players[seatId].userId)
            

    def saveRecord(self, recordName):
        """保存牌局记录"""
        trConfig = majiang_conf.getTableRecordConfig()
        ftlog.debug('Majiang2.saveRecord trConfig:', trConfig)
        uploadKey = trConfig.get('trUploadKey', '')
        uploadUrls = trConfig.get('trUploadUrls', [])
        if len(uploadUrls) == 0:
            return

        uploadUrl = random.choice(uploadUrls)
        uploadPath = trConfig.get('trFilePath', 'cdn37/majiang2/difang/')
        recordString = json.dumps(self.msgRecords)
        cdn = trConfig.get('trDownloadPath', 'http://ddz.dl.tuyoo.com/')
        cdn = cdn + uploadPath + recordName
        self.reset()
        
        ftlog.debug('Majiang2.saveRecord uploadUrl:', uploadUrl, 'uploadKey:', uploadKey, 'uploadPath:', uploadPath, 'recoredName:', recordName)
        
        def runUpload():
            ec, info = uploader.uploadVideo(uploadUrl, uploadKey, uploadPath + recordName, recordString)
            ftlog.debug('runupload ec=', ec, 'info=', info)
            if ec == 0:
                ftlog.info('Majiang2.saveRecord ok, recordName:', recordName, ' CDNPath:', cdn)
            else:
                ftlog.error('Majiang2.saveRecord error, code:', ec, ' info:', info)
                
        ftcore.runOnce(runUpload)
        return cdn
    
    def send_message(self, message, uidList):
        """发送消息"""
        if not message or not uidList:
            return
        
        if not isinstance(uidList, list):
            uidList = [uidList]
            
        newList = []
        for uid in uidList:
            if TYPlayer.isRobot(uid):
                continue
            # 认输的情况下还需要给前端发送消息，状态切换到离开，则不用发消息
            isLeave = False
            for player in self.players:
                if not player:
                    continue
                
                if player.userId == uid:
                    isLeave = player.isLeave()
                    break
                    
            if isLeave:
                ftlog.debug('msg_long_net.send_message user isLeave, userId:', uid
                            , ' do not send anymore...')
                continue
            
            newList.append(uid)
        
        for uid in newList :
            tyrpcconn.sendToUser(uid, message)


    def _getWinModeDesc(self, winMode):
        """根据winMode获取winMode描述"""
        if winMode == MOneResult.WIN_MODE_DIANPAO_BAOZHUANG:
            return "点炮包庄"
        elif winMode == MOneResult.WIN_MODE_LOSS:  # 输
            return ""
        elif winMode == MOneResult.WIN_MODE_DIANPAO:  # 点炮输
            return "点炮"
        elif winMode == MOneResult.WIN_MODE_ZIMO:  # 自摸胡
            return '自摸'
        elif winMode == MOneResult.WIN_MODE_PINGHU:  # 点炮胡
            return '胡'
        elif winMode == MOneResult.WIN_MODE_GANGKAI:
            return '杠开'
        elif winMode == MOneResult.WIN_MODE_QIANGGANGHU:
            return '抢杠'
        return ''

