# -*- coding=utf-8
'''
Created on 2016年9月23日
下行消息通知

@author: zhaol
'''
from freetime5.util import ftlog
import json


class MMsg(object):
    
    def __init__(self):
        super(MMsg, self).__init__()
        self.__tableId = 0
        self.__roomId = 0
        self.__players = []
        self.__playMode = ''
        self.__tableTye = ''
        self.__gameId = 0
        self.__playerCount = 0
        self.__roomConf = {}
        self.__tableConf = {}
        self.__table_tile_mgr = None
        self.__latest_msgs = None
        self.__action_id = 0
        self.__msg_records = []
        self.__auto_win = False
        self.__tile_pattern_checker = None
        
    @property
    def tilePatternChecker(self):
        return self.__tile_pattern_checker
    
    def setTilePatternChecker(self, checker):
        self.__tile_pattern_checker = checker

    @property
    def autoWin(self):
        return self.__auto_win

    def setAutoWin(self, autoWin):
        self.__auto_win = autoWin

    def saveRecord(self, recordName):
        pass
        
    def reset(self):
        """重置消息模块"""
        self.__action_id = 0
        self.__latest_msgs = [None for _ in range(self.playerCount)]
        self.__msg_records = []
        
    @property
    def actionId(self):
        return self.__action_id
    
    def setActionId(self, actionId):
        self.__action_id = actionId
        
    @property
    def msgRecords(self):
        return self.__msg_records
    
    def addMsgRecord(self, message, uidList):
        if message.getResult('reconnect', False):
            return
        
        ftlog.info('addMsgRecord message:', message, 'toUidList:', uidList)
        mStr = message.pack()
        mObj = json.loads(mStr)
        if not isinstance(uidList, list):
            uidList = [uidList]
            
        mObj['record_uid_list'] = uidList
        mObj['isTableRecord'] = True
        self.__msg_records.append(mObj)
        
    @property
    def latestMsg(self):
        """玩家最新的消息"""
        return self.__latest_msgs
    
    def table_call_hand_tile_sort(self, seatId, colorList):
        '''
        发送玩家手牌展示顺序
        '''
    
    def table_call_coin_detail(self, seatId, chargeCoin, uChip, diamond):
        pass
    
    def table_call_latest_msg(self, seatId):
        """补发最新的消息"""
        pass
        
    @property
    def tableTileMgr(self):
        return self.__table_tile_mgr
    
    def setTableTileMgr(self, tableTileMgr):
        """设置牌桌手牌管理器"""
        self.__table_tile_mgr = tableTileMgr
        
    @property
    def roomConf(self):
        """房间配置"""
        return self.__roomConf
    
    @property
    def tableConf(self):
        """牌桌配置"""
        return self.__tableConf
        
    @property
    def playerCount(self):
        return self.__playerCount
    
    @property
    def playMode(self):
        return self.__playMode
    
    @property
    def tableType(self):
        return self.__tableTye    
    
    @property
    def tableId(self):
        return self.__tableId
    
    @property
    def roomId(self):
        return self.__roomId
    
    @property
    def gameId(self):
        return self.__gameId
    
    @property
    def players(self):
        return self.__players
    
    def setPlayers(self, players):
        """设置玩家"""
        ftlog.debug('msg.setPlayers:', self.players)
        self.__players = players
        
    def setInfo(self, gameId, roomId, tableId, playMode, tableType, playerCount):
        """设置三个公共信息"""
        ftlog.debug('[msg] gameId:', gameId
                    , ' roomId:', roomId
                    , ' tableId:', tableId
                    , ' playMode:', playMode
                    , ' tableType:', tableType
                    , ' playerCount:', playerCount)
        
        self.__gameId = gameId
        self.__roomId = roomId
        self.__tableId = tableId
        self.__playMode = playMode
        self.__tableTye = tableType
        self.__playerCount = playerCount
        self.__latest_msgs = [None for _ in range(playerCount)]
        
    def setRoomInfo(self, roomConf, tableConf):
        """设置房间配置"""
        self.__roomConf = roomConf
        self.__tableConf = tableConf
        
    def setTableId(self, tableId):
        """设置tableId
        """
        self.__tableId = tableId
        
    def setRoomId(self, roomId):
        """设置roomId
        """
        self.__roomId = roomId
   
    def getBroadCastUIDs(self, filter_id=-1):
        """获取待广播的UID集合，不包括filter_id及机器人
        不需要向机器人发送消息
        """
        uids = []
        if not self.players:
            return uids
        
        for player in self.players:
            if not player:
                continue
            
            if player.isRobot():
                continue
            
            if player.userId == filter_id:
                continue
            
            if player.isLeave():
                continue
            
            uids.append(player.userId)
            ftlog.debug('MMsg.getBroadCastUIDs uids:', uids)
        return uids
        
    def table_call_add_card(self, player, tile, state, seatId, timeOut, actionId, extendInfo, recordUserIds):
        """通知庄家游戏开始
        """
        pass
    
    def table_call_ask_ting(self, seatId, actionId, winNodes, tingAction, timeOut):
        """询问玩家是否听牌
        """
        pass

    def table_call_tian_ting_over(self, seatId, actionId):
        """通知庄家可以出牌
        """
        pass

    def table_call_add_card_broadcast(self, seatId, timeOut, actionId, uids, tile):
        """通知其他人游戏开始
        """
        pass
    
    def table_call_fang_mao(self
                             , player
                             , mao
                             , maos
                             , state
                             , seatId
                             , timeOut
                             , actionID
                             , extend):
        pass
    
    def table_call_fang_mao_broadcast(self
                        , seatId
                        , timeOut
                        , actionID
                        , userId
                        , maos
                        , mao):
        pass
        
    def table_call_drop(self, seatId, player, tile, state, extendInfo, actionId, timeOut, winTiles=None):
        """通知玩家出牌
        参数：
            player - 做出牌操作的玩家
            winTiles - 可能胡哪些牌，某些玩法没有听牌功能，但也要每次提示玩家可胡哪些牌
        """
        return None
    
    def table_call_after_chi(self, lastSeatId, seatId, tile, pattern, timeOut, actionId, player, actionInfo=None , exInfo=None):
        """吃牌广播"""
        pass
    
    def table_call_after_peng(self, lastSeatId, seatId, tile, timeOut, actionId, player, pengPattern, actionInfo=None, exInfo=None):
        """碰牌广播"""
        pass
    
    def table_call_after_gang(self, lastSeatId, seatId, tile, loser_seat_ids, actionId, player, gang, exInfo=None):
        """杠牌广播"""
        pass

    def table_call_update_genzhuang(self, lastSeatId, seatId, tile, loser_seat_ids, actionId, player, gang, exInfo=None):
        """跟庄广播"""
        pass

    def table_call_notify_grab_gang(self, lastSeatId, actionId, player, tile):
        '''通知抢杠胡成功消息，刷新手牌 广播消息'''
        pass
    
    def table_call_grab_gang_hu(self, lastSeatId, seatId, actionId, player, gang, exInfo=None):
        '''抢杠胡消息 单独'''
        pass
    
    def table_call_after_extend_mao(self, lastSeatId, seatId, mao, actionId, player):
        """补锚/补蛋广播"""
        pass
    
    def table_call_after_zhan(self, lastSeatId, seatId, tile, timeOut, actionId, player, pattern, actionInfo=None):
        """粘牌广播"""
        pass
    
    def sendMsgInitTils(self, tiles, banker, userId, seatId):
        """发牌"""
        pass
    
    def table_call_table_info(self
                , userId
                , banker
                , bankerLasttime
                , seatId
                , isReconnect
                , quanMenFeng
                , curSeat
                , tableState
                , cInfo=None
                , btInfo=None):
        """发送table_info"""
        pass
    
    def table_call_after_ting(self, player, actionId, userId, allWinTiles, tingResult):
        """听牌消息"""
        pass
    
    def table_call_grab_ting(self):
        pass
    
    def table_call_baopai(self, player, baopai, abandones):
        """宝牌通知"""
        pass
    
    def table_call_fanpigu(self, pigus):
        """翻屁股通知"""
        pass

    def table_call_addflower(self, tile, uids):
        """摸到花牌通知"""
        pass

    def table_call_crapshoot(self, seatId, points):
        """掷骰子通知"""
        pass
    
    def table_call_score(self, coin, tableCoin, score, delta, isReconnect=False, extendInfo={}):
        """牌桌积分变化"""
        pass
    
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
            , fanPatternTotalBei=None):
        """结算"""
        pass
    
    def table_call_game_all_stat(self, terminate, extendBudgets, ctInfo):
        """牌桌结束大结算"""
        pass
    
    def table_call_laizi(self, magicTiles=[], magicFactors=[], banker_seat=0, isReconnect=False):
        """下发赖子"""
        pass
    
    def table_call_maConfig(self, maType, maCount, isReconnect=False):
        '''
        下发马牌配置
        '''
        pass
    
    def table_call_ask_piao(self, userId, seatId, piaoSolution, piaoTimeOut):
        pass
    
    def table_call_accept_piao(self, userId, seatId, piaoSolution, piaoTimeOut):
        pass
    
    def table_call_accepted_piao(self, userId, seatId, piaoSolution):
        pass
    
    def table_call_piao(self, userId, seatId, piao):
        pass

    def table_call_ask_absence(self, userId, seatId, color, timeOut, isReconnect=False, actionId=0):
        """提示前端定缺"""
        pass
    
    def table_call_notify_absence(self, userId, seatId, color, isReconnect=False, actionId=0):
        """本人定缺的实时反馈"""
        pass


    def table_call_notifyTimeOut(self, seatId, timeOut, times):
        '''
        玩家超时消息通知，1、12秒 
        广播消息
        '''
        pass
    
    def table_call_tips_task(self, userId, loopTaskInfo='', winStreakInfo='', loopWinTimesInfo='', winStreakAllInfo=[]):
        '''
        开局后发送任务信息
        '''
        pass
    
    def table_call_show_tips(self, tips_num, player):
        """发送提示消息 前端根据tips_num来显示对应的消息
        """
        pass

    def table_call_absence_end(self, userId, seatId, absenceColor, player, tile, isReconnect=0, state=0, extend=None, actionId=0, banker=0, timeOut=12):
        """所有人定缺完毕"""
        pass


    def table_call_ask_huansanzhang(self, userId, seatId, huanSolution, forbidChangeTiles, timeOut, actionId):
        pass
    
    def table_call_notify_huansanzhang(self, userId, seatId, actionSeatId, tiles, actionId, isReconnect=False):
        pass
    
    def table_call_huanSanZhang_end(self, userId, seatId, afterTiles, beforeTiles, handTiles, rule, actionId):
        pass
    
    def table_call_double_broadcast(self, uids, seatid, doubles):
        pass
    
    def table_call_double_ask(self, uids, actionId, timeOut, doublePoints=[]):
        pass
    
    def table_call_update_round_count(self, curCount, totalCount):
        pass

    def table_call_update_ting_result(self, player):
        pass

    def table_call_ask_comb(self, player, seatId, combIds):
        pass
    
    def table_call_broadcast_charging(self, seatId, actionId, timeOut):
        pass
    
    def table_call_ask_charge(self, seatId, actionId, timeOut, chip, dis, content, promote):
        '''
        dis - 顶部的文案
        content - 兑换内容文案
        promote - 下部的提示
        '''
        pass
    
    def table_call_charged(self, seatId, actionId, result, dis):
        pass

    def send_message(self, message, uidList):
        """发送消息"""
        pass
    
    def table_ready_succ_response(self, userId, seatId):
        pass
    
    def create_table_succ_response(self, userId, seatId, action, tableHost):
        pass
    
    def table_leave(self, userId, seatId, reason):
        pass
    
    def create_table_dissolve(self, userId, seatId, state):
        pass
    
    def create_table_dissolve_vote(self, userId, seatId, seatNum, vote_info, vote_detail, vote_name, vote_timeOut):
        pass
    
    def table_chat_broadcast(self, uid, gameId, voiceIdx, msg):
        pass
    
    def sendTableEvent(self, count, userId, seatId):
        pass
    
    def broadcastUserSit(self, seatId, userId, is_reconnect, is_host=False):
        pass
    
    def table_call_bu_flower_broadcast(self, seatId, tile, flowerTiles, flowerScore):
        pass

    def round_result_game_over(self, gameFlow, infos, cfFinal):
        pass
    
    def table_call_player_leave(self , online_info_list):
        pass
    
    def table_call_detail_desc(self, userId, seatId, totalScore, detailDescList, maxFanDesc, extendInfo={}):
        pass
    
    def table_call_smart_operate(self, player, actionId):
        pass