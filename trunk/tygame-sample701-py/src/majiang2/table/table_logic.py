# -*- coding=utf-8
'''
Created on 2016年9月23日
麻将的逻辑类，只关心麻将的核心玩法

新麻将的核心为牌桌状态及其对应的处理器。
切记，避免直接在状态与状态之间做切换。

@author: zhaol
'''
from majiang2.poker2.entity import hallrpcutil
from majiang2.poker2.entity.game.tables.table_player import TYPlayer
from tuyoo5.game import tybireport
from tuyoo5.core.typlugin import pluginCross
'''
一炮多响，抢杠胡问题备忘
1）wins从对应的processor中提取
2）测试2个人胡，1胡2不胡的情况
需要在playerCancel里额外处理一些内容
'''

from freetime5.util import ftlog, fttime
from majiang2 import player
from majiang2.ai.play_mode import MPlayMode
from majiang2.ai.tile_value import MTileValue
from majiang2.ai.ting import MTing
from majiang2.banker.banker import MBanker
from majiang2.banker.banker_factory import BankerFactory
from majiang2.chi_rule.chi_rule_factory import MChiRuleFactory
from majiang2.drop_card_strategy.drop_card_strategy_factory import MDropCardStrategyFactory
from majiang2.entity import loop_active_task, win_streak_task, loop_win_task
from majiang2.entity import util
from majiang2.entity.util import Majiang2Util
from majiang2.flower_rule.flower_base import MFlowerRuleBase
from majiang2.gang_rule.gang_rule_factory import MGangRuleFactory
from majiang2.gua_da_feng_rule.dafeng_base import MDaFengRuleBase
from majiang2.mao_rule.mao_rule_factory import MMaoRuleFactory
from majiang2.msg_handler.msg_factory import MsgFactory
from majiang2.peng_rule.peng_rule_factory import MPengRuleFactory
from majiang2.player.hand.hand import MHand
from majiang2.player.player import MPlayer, MPlayerTileGang
from majiang2.table.friend_table_define import MFTDefine
from majiang2.table.run_mode import MRunMode
from majiang2.table.table_config_define import MTDefine
from majiang2.table_schedule.schedule_factory import MTableScheduleFactory
from majiang2.table_state.state import MTableState
from majiang2.table_state.state_factory import TableStateFactory
from majiang2.table_state_processor.absence_processor import MAbsenceProcessor
from majiang2.table_state_processor.add_card_hu_processor import MAddCardHuProcessor
from majiang2.table_state_processor.add_card_processor import MAddCardProcessor
from majiang2.table_state_processor.charge_processor import MChargeProcessor
from majiang2.table_state_processor.da_feng_processor import MDafengProcessor
from majiang2.table_state_processor.double_processor import MDoubleProcessor
from majiang2.table_state_processor.drop_card_hu_processor import MDropCardHuProcessor
from majiang2.table_state_processor.drop_card_processor import MDropCardProcessor
from majiang2.table_state_processor.extend_info import MTableStateExtendInfo
from majiang2.table_state_processor.flower_processor import MFlowerProcessor
from majiang2.table_state_processor.huansanzhang_processor import MHuanSanZhangProcessor
from majiang2.table_state_processor.lou_hu_processor import MLouHuProcessor
from majiang2.table_state_processor.pause_processor import MPauseProcessor
from majiang2.table_state_processor.piao_processor import MPiaoProcessor
from majiang2.table_state_processor.qiang_exmao_hu_processor import MQiangExmaoHuProcessor
from majiang2.table_state_processor.qiang_exmao_peng_processor import MQiangExmaoPengProcessor
from majiang2.table_state_processor.qiang_gang_hu_processor import MQiangGangHuProcessor
from majiang2.table_state_processor.shuffle_hu_processor import MShuffleHuProcessor
from majiang2.table_state_processor.tian_hu_processor import MTianHuProcessor
from majiang2.table_state_processor.ting_before_add_card_processor import MTingBeforeAddCardProcessor
from majiang2.table_state_processor.zhisaizi_processor import ZhisaiziProcessor
from majiang2.table_statistic.statistic import MTableStatistic
from majiang2.table_tile.table_tile import MTableTile
from majiang2.table_tile.table_tile_factory import MTableTileFactory
from majiang2.tile.tile import MTile
from majiang2.tile_pattern_checker.tile_pattern_checker_factory import MTilePatternCheckerFactory
from majiang2.ting_rule.ting_rule_factory import MTingRuleFactory
from majiang2.win_loose_result.one_result import MOneResult
from majiang2.win_loose_result.one_result_factory import MOneResultFactory
from majiang2.win_loose_result.round_results import MRoundResults
from majiang2.win_loose_result.table_results import MTableResults
from majiang2.win_rule.win_rule import MWinRule
from majiang2.win_rule.win_rule_factory import MWinRuleFactory
import copy
import random

class MajiangTableLogic(object):
    def __init__(self, playerCount, playMode, runMode):
        super(MajiangTableLogic, self).__init__()
        # 用户数量
        self.__playerCount = playerCount
        # 玩法
        self.__playMode = playMode
        # 运行方式
        self.__run_mode = runMode
        # 牌桌配置
        self.__table_config = {}
        # 房间配置
        self.__room_config = {}
        # 根据玩法获取发牌器
        self.__table_tile_mgr = MTableTileFactory.getTableTileMgr(self.__playerCount, self.__playMode, runMode)
        # 本局玩家
        self.__players = [ None for _ in range(self.playerCount) ]
        # 玩家网络状态
        self.__players_ping = {}
        # 手牌张数
        self.__hand_card_count = 13
        # 庄家
        self.__banker_mgr = BankerFactory.getBankerAI(self.playMode)
        # 当前操作座位号
        self.__cur_seat = 0
        # 上牌状态
        self.__add_card_processor = MAddCardProcessor(self.tableConfig)
        self.__add_card_processor.setTableTileMgr(self.tableTileMgr)
        # 上牌前的听牌状态
        self.__ting_before_add_card_processor = MTingBeforeAddCardProcessor(self.tableConfig)
        # 漏胡处理器
        self.__lou_hu_processor = MLouHuProcessor(self.tableConfig)
        # 刮大风处理器
        self.__da_feng_processor = MDafengProcessor(self.tableConfig)
        # 天胡处理器
        self.__tian_hu_processor = MTianHuProcessor(self.tableConfig)
        # 摸排胡处理器
        self.__add_card_hu_processor = MAddCardHuProcessor(self.tableConfig)
        # 出牌胡的处理器
        self.__drop_card_hu_processor = MDropCardHuProcessor(self.tableConfig)
        # 发牌胡
        self.__shuffle_hu_processor = MShuffleHuProcessor(self.tableConfig)
        # 出牌状态
        self.__drop_card_processor = MDropCardProcessor(self.playerCount, playMode, self.tableConfig)
        self.__drop_card_processor.setTableTileMgr(self.tableTileMgr)
        # 抢杠和状态
        self.__qiang_gang_hu_processor = MQiangGangHuProcessor(self.playerCount, self.tableConfig)
        self.__qiang_gang_hu_processor.setTableTileMgr(self.tableTileMgr)
        # 抢锚碰状态
        self.__qiang_exmao_peng_processor = MQiangExmaoPengProcessor(self.playerCount, self.tableConfig)
        # 抢锚碰状态
        self.__qiang_exmao_hu_processor = MQiangExmaoHuProcessor(self.playerCount, self.tableConfig)
        # 定飘的处理器
        self.__piao_processor = MPiaoProcessor(self.playerCount, playMode, self.tableConfig)
        self.__piao_processor.setTableTileMgr(self.tableTileMgr)
        # 换三张的处理器
        self.__huansanzhang_processor = MHuanSanZhangProcessor(self.playerCount, playMode, self.tableConfig)
        # 充值的处理器
        self.__charge_processor = MChargeProcessor(self.playerCount, self.tableConfig)
        # 翻倍的处理器
        self.__double_processor = MDoubleProcessor(self.playerCount, playMode, self.tableConfig)
        # 定缺的处理器
        self.__absence_processor = MAbsenceProcessor(self.playerCount, playMode, self.tableConfig)
        # 掷塞子的处理器 
        self.__zhisaizi_processor = ZhisaiziProcessor(self.playerCount, playMode, self.tableConfig)
        # 补花的处理器
        self.__flower_processor = MFlowerProcessor(self.playerCount, playMode, self.tableConfig)
        # 暂停处理器
        self.__pause_processor = MPauseProcessor(self.tableConfig)
        # 和牌状态
        self.__table_win_state = MTableState.TABLE_STATE_NONE
        # 消息处理者
        self.__msg_processor = MsgFactory.getMsgProcessor(runMode)
        self.__msg_processor.setTableTileMgr(self.tableTileMgr)
        # 吃牌AI
        self.__chi_rule_mgr = MChiRuleFactory.getChiRule(self.playMode)
        self.__chi_rule_mgr.setTableTileMgr(self.tableTileMgr)
        # 碰牌AI
        self.__peng_rule_mgr = MPengRuleFactory.getPengRule(self.playMode)
        self.__peng_rule_mgr.setTableTileMgr(self.tableTileMgr)
        # 杠牌AI
        self.__gang_rule_mgr = MGangRuleFactory.getGangRule(self.playMode)
        self.__gang_rule_mgr.setTableTileMgr(self.tableTileMgr)
        # 和牌管理器
        self.__win_rule_mgr = MWinRuleFactory.getWinRule(self.playMode)
        self.__win_rule_mgr.setTableTileMgr(self.tableTileMgr)
        self.__win_rule_mgr.setWinRuleTableConfig(self.tableConfig)
        self.__win_rule_mgr.setMsgProcessor(self.msgProcessor)
        # 锚牌管理器
        self.__mao_rule_mgr = MMaoRuleFactory.getMaoRule(self.playMode)

        # 牌桌状态机
        self.__table_stater = TableStateFactory.getTableStates(self.playMode)
        self.__table_stater.setPlayMode(self.playMode)
        # 听牌管理器
        if self.checkTableState(MTableState.TABLE_STATE_TING):
            self.__ting_rule_mgr = MTingRuleFactory.getTingRule(self.playMode)
            self.__ting_rule_mgr.setWinRuleMgr(self.__win_rule_mgr)
            self.__ting_rule_mgr.setTableTileMgr(self.tableTileMgr)
        else:
            self.__ting_rule_mgr = None
        # 牌桌最新操作标记，摸牌actionID加1，出牌actionID加1

        self.__action_id = 0
        # 圈/风
        self.__quan_men_feng = 0
        # 算分结果
        self.__round_result = None
        # 牌桌结果
        self.__table_result = MTableResults()
        # 牌局记录上传记录url
        self.__record_url = []
        # 牌局记录每局底和局数
        self.__record_base_id = []
        # 记录上一局的结果
        self.__win_loose = 0
        # 记录上一局的胜利者
        self.__last_win_seatId = 0
        # 杠牌记录,用来判定杠上花和杠上炮,每次成功杠牌后设置,每次出牌后或者抢杠胡后清空,设置值为座位号,默认值-1
        self.__latest_gang_seatId = -1
        # 牌桌观察者
        self.__table_observer = None
        # 牌桌类型
        self.__table_type = MTDefine.TABLE_TYPE_NORMAL
        # 发起解散的人
        self.__vote_host = -1
        # 游戏ID
        self.__gameId = 0
        self.__roomId = 0
        self.__tableId = 0
        self.__bigRoomId = 0
        self.__schedule_mgr = MTableScheduleFactory.getTableSchedule('')
        # 记录玩家和牌次数winNum 和牌顺序winOrder 和牌的次数winTimes
        self.__winNum = 0
        self.__winOrder = [0 for _ in range(self.playerCount)]
        self.__winTimes = [0 for _ in range(self.playerCount)]
        # 跟庄牌
        self.__genTile = 0
        self.__genTileCount = 0
        # 番型检测器
        self.__tile_pattern_checker = MTilePatternCheckerFactory.getTilePatternChecker(self.playMode)
        self.msgProcessor.setTilePatternChecker(self.tilePatternChecker)
        if self.tingRuleMgr:
            self.tingRuleMgr.setTilePatternChecker(self.tilePatternChecker)
        if self.winRuleMgr:
            self.winRuleMgr.setTilePatternChecker(self.tilePatternChecker)
        
        self.chargeProcessor.setMsgProcessor(self.msgProcessor)
        self.chargeProcessor.setGameId(self.gameId)
        self.chargeProcessor.setTableId(self.tableId)
        self.doubleProcessor.setMsgProcessor(self.msgProcessor)
        self.absenceProcessor.setMsgProcessor(self.msgProcessor)
        # 超时发送通知消息
        self.dropCardProcessor.setMsgProcessor(self.msgProcessor)
        self.addCardHuProcessor.setMsgProcessor(self.msgProcessor)
        self.addCardProcessor.setMsgProcessor(self.msgProcessor)
        self.tingBeforeAddCardProcessor.setMsgProcessor(self.msgProcessor)
        self.louHuProcesssor.setMsgProcessor(self.msgProcessor)
        self.daFengProcessor.setMsgProcessor(self.msgProcessor)
        self.tianHuProcessor.setMsgProcessor(self.msgProcessor)
        self.dropCardHuProcessor.setMsgProcessor(self.msgProcessor)
        self.shuffleHuProcessor.setMsgProcessor(self.msgProcessor)
        self.qiangGangHuProcessor.setMsgProcessor(self.msgProcessor)
        self.qiangExmaoPengProcessor.setMsgProcessor(self.msgProcessor)
        self.qiangExmaoHuProcessor.setMsgProcessor(self.msgProcessor)
        self.piaoProcessor.setMsgProcessor(self.msgProcessor)
        self.huanSanZhangProcessor.setMsgProcessor(self.msgProcessor)
        self.flowerProcessor.setMsgProcessor(self.msgProcessor)
        
    @property
    def dropCardStrategy(self):
        return self.__drop_card_strategy
    
    def setDropCardStrategy(self, strategy):
        self.__drop_card_strategy = strategy
    
    @property
    def tilePatternChecker(self):
        return self.__tile_pattern_checker
    
    def setTilePatternChecker(self, checker):
        self.__tile_pattern_checker = checker

    @property
    def genTile(self):
        return self.__genTile

    def setGenTile(self, tile):
        self.__genTile = tile
    
    @property
    def bankerHuaZhuDaJiao(self):
        return self.__banker_huazhudajiao
    
    @property
    def winNum(self):
        ftlog.debug('MTableLogic.winNum:', self.__winNum)
        return self.__winNum
    
    def incrWinNum(self):
        self.__winNum += 1
    
    def incrWinTimes(self, seatId):
        self.__winTimes[seatId] += 1

    # 返回座位号ID的和牌顺序 
    @property
    def winOrder(self):
        return self.__winOrder
    
    @property
    def winTimes(self):
        return self.__winTimes
    
    def setWinOrder(self, seatId):
        self.incrWinNum()
        self.incrWinTimes(seatId)
        if self.__winOrder[seatId] == 0:
            self.__winOrder[seatId] = self.winNum
        ftlog.debug('MTableLogic.setWinOrder winNum:', self.__winNum
                            , 'seatId:', seatId
                            , 'winOrder:', self.winOrder
                            , 'winTimes:', self.winTimes)

    # 获取第一个胡的玩家ID
    def getFirstWinId(self):
        for seatId in range(self.playerCount):
            if 1 == self.winOrder[seatId]:
                return seatId
        return -1

    # 从花猪大叫玩家中获取第一个花猪大叫ID
    def getBankerFromHuaZhuDaJiao(self, looserIds):
        for _ in range(self.playerCount):
            nextSeatId = (self.bankerMgr.queryBanker() + 1) % self.playerCount
            if nextSeatId in looserIds:
                self.bankerMgr.setHuaZhuDaJiaoId(nextSeatId)
                break

    def resetWinNum(self):
        self.__winNum = 0
        self.__winOrder = [0 for _ in range(self.playerCount)]
        self.__winTimes = [0 for _ in range(self.playerCount)]

    @property
    def scheduleMgr(self):
        return self.__schedule_mgr

    def setScheduleMgr(self, mgr):
        self.__schedule_mgr = mgr

    def setGameInfo(self, gameId, bigRoomId, roomId, tableId):
        self.__gameId = gameId
        self.__bigRoomId = bigRoomId
        self.__roomId = roomId
        self.__tableId = tableId
        self.chargeProcessor.setGameId(self.gameId)
        self.chargeProcessor.setRoomId(self.roomId)
        self.chargeProcessor.setTableId(self.tableId)

    @property
    def gameId(self):
        return self.__gameId

    @property
    def bigRoomId(self):
        return self.__bigRoomId

    @property
    def roomId(self):
        return self.__roomId

    @property
    def tableId(self):
        return self.__tableId

    @property
    def playersPing(self):
        return self.__players_ping

    def setPlayersPing(self, ping):
        self.__players_ping = ping

    @property
    def maoRuleMgr(self):
        return self.__mao_rule_mgr

    def setMaoRuleMgr(self, maoRuleMgr):
        self.__mao_rule_mgr = maoRuleMgr

    @property
    def lastWinSeatId(self):
        return self.__last_win_seatId

    def setLastWinSeatId(self, lastWinSeatId):
        ftlog.debug('MajiangTableLogic.setLastWinSeatId:', lastWinSeatId)
        self.__last_win_seatId = lastWinSeatId

    @property
    def winLoose(self):
        return self.__win_loose

    def setWinLoose(self, winLoose):
        self.__win_loose = winLoose

    @property
    def bankerMgr(self):
        return self.__banker_mgr

    def setBankerMgr(self, bankerMgr):
        self.__banker_mgr = bankerMgr

    @property
    def tableStater(self):
        return self.__table_stater

    def setTableStater(self, tableStater):
        self.__table_stater = tableStater

    @property
    def chiRuleMgr(self):
        return self.__chi_rule_mgr

    def setChiRuleMgr(self, chiRuleMgr):
        self.__chi_rule_mgr = chiRuleMgr

    @property
    def pengRuleMgr(self):
        return self.__peng_rule_mgr

    def setPengRuleMgr(self, pengRuleMgr):
        self.__peng_rule_mgr = pengRuleMgr

    @property
    def gangRuleMgr(self):
        return self.__gang_rule_mgr

    def setGangRuleMgr(self, gangRuleMgr):
        self.__gang_rule_mgr = gangRuleMgr

    @property
    def tableType(self):
        return self.__table_type

    def setTableType(self, tableType):
        self.__table_type = tableType

        self.addCardProcessor.setTableType(tableType)
        self.dropCardProcessor.setTableType(tableType)
        self.qiangGangHuProcessor.setTableType(tableType)
        self.piaoProcessor.setTableType(tableType)
        self.doubleProcessor.setTableType(tableType)
        self.zhisaiziProcessor.setTableType(tableType)
        self.flowerProcessor.setTableType(tableType)

    def setLatestGangSeatId(self, seatId=-1):
        '''
        设置最近杠的seatId，默认为－1
        '''
        ftlog.debug('MaJiangTableLogic.setLatestGangSeatId oldSeatId:', self.latestGangSeatId, 'newSeatId:', seatId)
        self.__latest_gang_seatId = seatId

    @property
    def latestGangSeatId(self):
        return self.__latest_gang_seatId

    @property
    def tableResult(self):
        return self.__table_result

    def setTableResult(self, tableResult):
        self.__table_result = tableResult

    @property
    def recordUrl(self):
        return self.__record_url

    def setRecordUrl(self, recordUrl):
        self.__record_url = recordUrl

    def appendRecordUrl(self, recordUrl):
        self.__record_url.append(recordUrl)

    @property
    def recordBaseId(self):
        return self.__record_base_id

    def setRecordBaseId(self, recordBaseId):
        self.__record_base_id = recordBaseId

    @property
    def tableWinState(self):
        return self.__table_win_state

    def setTableWinState(self, tableWinState):
        self.__table_win_state = tableWinState

    @property
    def tableObserver(self):
        return self.__table_observer

    def setTableObserver(self, observer):
        self.__table_observer = observer

    @property
    def roundResult(self):
        return self.__round_result

    def setRoundResult(self, roundResult):
        self.__round_result = roundResult

    @property
    def runMode(self):
        return self.__run_mode

    def setRunMode(self, runMode):
        self.__run_mode = runMode

    @property
    def voteHost(self):
        return self.__vote_host

    def setVoteHost(self, voteHost):
        ftlog.debug('MajiangTableLogic.setVoteHost:', voteHost)
        self.__vote_host = voteHost

    @property
    def tingRule(self):
        """听牌规则管理器"""
        return self.__ting_rule_mgr

    @property
    def tingRuleMgr(self):
        return self.__ting_rule_mgr

    @property
    def addCardProcessor(self):
        """摸牌管理器"""
        return self.__add_card_processor

    @property
    def tingBeforeAddCardProcessor(self):
        return self.__ting_before_add_card_processor

    def setTingBeforeAddCardProcessor(self, processor):
        self.__ting_before_add_card_processor = processor

    @property
    def louHuProcesssor(self):
        return self.__lou_hu_processor

    def setLouHuProcessor(self, louHuProcessor):
        self.__lou_hu_processor = louHuProcessor

    @property
    def daFengProcessor(self):
        return self.__da_feng_processor

    def setDaFengProcessor(self, processor):
        self.__da_feng_processor = processor

    @property
    def tianHuProcessor(self):
        return self.__tian_hu_processor

    def setTianHuProcesor(self, tianHuProcessor):
        self.__tian_hu_processor = tianHuProcessor

    @property
    def addCardHuProcessor(self):
        return self.__add_card_hu_processor

    def setAddCardHuProcessor(self, addCardHuProcessor):
        self.__add_card_hu_processor = addCardHuProcessor

    @property
    def dropCardHuProcessor(self):
        return self.__drop_card_hu_processor

    def setDropCardHuProcessor(self, dropCardHuProcessor):
        self.__drop_card_hu_processor = dropCardHuProcessor

    @property
    def shuffleHuProcessor(self):
        return self.__shuffle_hu_processor

    def setShuffleHuProcessor(self, shuffleHuProcessor):
        self.__shuffle_hu_processor = shuffleHuProcessor

    @property
    def dropCardProcessor(self):
        """出牌管理器"""
        return self.__drop_card_processor

    @property
    def qiangGangHuProcessor(self):
        return self.__qiang_gang_hu_processor

    @property
    def qiangExmaoPengProcessor(self):
        return self.__qiang_exmao_peng_processor

    @property
    def qiangExmaoHuProcessor(self):
        return self.__qiang_exmao_hu_processor

    @property
    def absenceProcessor(self):
        return self.__absence_processor

    def setAbsenceProcessor(self, absenceProcessor):
        self.__absence_processor = absenceProcessor

    @property
    def piaoProcessor(self):
        return self.__piao_processor

    def setPiaoProcessor(self, piaoProcessor):
        self.__piao_processor = piaoProcessor

    @property
    def huanSanZhangProcessor(self):
        return self.__huansanzhang_processor

    def setHuanSanZhangProcessor(self, huanProcessor):
        self.__huansanzhang_processor = huanProcessor

    @property
    def chargeProcessor(self):
        return self.__charge_processor

    def setChargeProcessor(self, processor):
        self.__charge_processor = processor

    @property
    def zhisaiziProcessor(self):
        return self.__zhisaizi_processor

    def setZhisaiziProcessor(self, zhisaiziProcessor):
        self.__zhisaizi_processor = zhisaiziProcessor

    @property
    def flowerProcessor(self):
        return self.__flower_processor

    def setFlowerProcessor(self, flowerProcessor):
        self.__flower_processor = flowerProcessor

    @property
    def pauseProcessor(self):
        return self.__pause_processor

    def setPauseProcessor(self, pauseProcessor):
        self.__pause_processor = pauseProcessor

    @property
    def doubleProcessor(self):
        return self.__double_processor

    def setDoubleProcessor(self, doubleProcessor):
        self.__double_processor = doubleProcessor

    @property
    def playerCount(self):
        """获取本局玩家数量"""
        return self.__playerCount

    @property
    def msgProcessor(self):
        """获取消息处理对象"""
        return self.__msg_processor

    @property
    def actionID(self):
        """获取当前的操作标记"""
        return self.__action_id

    def incrActionId(self, reason):
        self.__action_id += 1
        ftlog.info('MajiangTableLogic.incrActionId now:', self.actionID
                   , ' reason:', reason)

    def setActionId(self, actionId):
        self.__action_id = actionId

    @property
    def playMode(self):
        """获取本局玩法"""
        return self.__playMode

    def setPlayMode(self, playMode):
        self.__playMode = playMode

    @property
    def player(self):
        """获取玩家"""
        return self.__players

    @property
    def players(self):
        return self.__players

    def setPlayer(self, player):
        self.__players = player

    @property
    def quanMenFeng(self):
        """获取圈/风设置"""
        return self.__quan_men_feng

    def setQuanMenFeng(self, quanMenFeng):
        self.__quan_men_feng = quanMenFeng

    @property
    def handCardCount(self):
        """获取初始手牌张数
        """
        return self.__hand_card_count

    def setHandCardCount(self, count):
        """设置初始手牌张数
        """
        self.__hand_card_count = count

    @property
    def curSeat(self):
        """当前操作座位号
        """
        return self.__cur_seat

    def setCurSeat(self, seat):
        """设置当前操作座位号
        """
        self.__cur_seat = seat

    @property
    def tableTileMgr(self):
        return self.__table_tile_mgr

    def setTableTileMgr(self, tableTileMgr):
        self.__table_tile_mgr = tableTileMgr

    @property
    def winRuleMgr(self):
        return self.__win_rule_mgr

    def setWinRuleMgr(self, winRuleMgr):
        self.__win_rule_mgr = winRuleMgr


    def nextRound(self):
        """
        下一把
            下一局开始前调用
        """
        self.setCurSeat(0)
        self.addCardProcessor.reset()
        self.tingBeforeAddCardProcessor.reset()
        self.dropCardProcessor.reset()
        self.qiangGangHuProcessor.reset()
        self.qiangExmaoPengProcessor.reset()
        self.qiangExmaoHuProcessor.reset()
        self.piaoProcessor.reset()
        self.zhisaiziProcessor.reset()
        self.louHuProcesssor.reset()
        self.flowerProcessor.reset()
        self.absenceProcessor.reset()
        self.huanSanZhangProcessor.reset()
        self.chargeProcessor.reset()
        if self.playMode == MPlayMode.PANJIN:  # 盘锦麻将double状态不重置
            self.doubleProcessor.resetButPoints()
        else:
            self.doubleProcessor.reset()
        self.setTableWinState(MTableState.TABLE_STATE_NONE)
        ftlog.info('MajiangTableLogic.nextRound tableWinState:', self.tableWinState)

        self.setActionId(0)
        self.setQuanMenFeng(0)
        self.setVoteHost(-1)
        self.tableTileMgr.reset()

        for player in self.player:
            if player:
                player.reset()

    # 血战玩法 获取下一句的庄家
    def getBankerExtendInfo(self):
        extendInfo = {}
        if not self.isTableFlow():
            extendInfo['firstHuId'] = self.getFirstWinId()
            extendInfo['isGameFlow'] = False
        else:
            extendInfo['isGameFlow'] = True

        ftlog.debug("getBankerExtendInfo  extendInfo: ", extendInfo)
        return extendInfo

    def resetGame(self, winLoose):
        """
        重置游戏
        每一小局结束之后调用
        """
        self.setWinLoose(winLoose)
        self.setLastWinSeatId(self.curSeat)
        # 当前游戏信息备忘
        finishBanker = self.queryBanker()
        # 确定下一局的庄家
        curRoundCount = self.scheduleMgr.curCount
        ftlog.debug("MajiangTableLogic.resetGame befor curRoundCount:", self.scheduleMgr.curCount)
        lastSeatId = self.lastWinSeatId

        # 打印用户牌桌金币
        for cp in self.players:
            if not cp:
                continue
            
            ftlog.debug('MajiangTableLogic tableCoin:', cp.getTableCoin(self.gameId, self.tableId), 'uChip:', hallrpcutil.getChip(cp.userId))

        if self.playMode == MPlayMode.XUEZHANDAODI \
                or self.playMode == MPlayMode.XUELIUCHENGHE:
            extendInfo = self.getBankerExtendInfo()
        else:
            extendInfo = {MBanker.GANG_COUNT: self.tableTileMgr.gangCount}

        newbanker, remains, noresults = self.bankerMgr.getBanker(self.playerCount
            , (curRoundCount == 0)
            , self.winLoose
            , lastSeatId
            , extendInfo)
        ftlog.debug('MajiangTableLogic.resetGame Remains:', remains
                    , 'Banker:', newbanker
                    , 'Noresults:', noresults
                    , ' OldBanker:', finishBanker
                    , "curSeat", self.curSeat)
        self.scheduleMgr.setBanker(newbanker)

        # 牌桌记录生成
        recordName = self.getCreateTableRecordName()
        recordUrl = self.msgProcessor.saveRecord(recordName)
        self.appendRecordUrl(recordUrl)
        # 标记游戏结束状态
        self.setTableWinState(MTableState.TABLE_STATE_GAME_OVER)
        ftlog.info('MajiangTableLogic.resetGame tableWinState:', self.tableWinState)
        # 牌局手牌管理器reset
        self.tableTileMgr.reset()
        # 游戏结束后，记录牌局事件
        if self.tableObserver:
            # 游戏事件记录
            userIds = self.msgProcessor.getBroadCastUIDs()
            self.tableObserver.onBeginGame(userIds, finishBanker)
            self.tableObserver.onGameEvent(MTableStatistic.TABLE_WIN
                    , self.player
                    , self.getTableConfig(MTDefine.TABLE_ROUND_ID, fttime.getCurrentTimestamp()))
        # 清空__round_result 否则在一局结束下局未开始时断线重连会取到错误的积分数据
        self.setRoundResult(MRoundResults())
        self.piaoProcessor.reset()
        self.absenceProcessor.reset()
        self.huanSanZhangProcessor.reset()
        # 清空winNum winOrder
        self.resetWinNum()
        for player in self.player:
            if not player:
                continue
            
            if player.isIgnoreMessage():
                self.players[player.curSeatId] = None
                self.msgProcessor.setPlayers(self.__players)
                
    def reset(self):
        """
        重置
            牌桌清理时调用
        """
        self.nextRound()
        self.bankerMgr.reset()
        self.setPlayer([ None for _ in range(self.playerCount) ])
        self.setRoundResult(None)
        self.tableResult.reset()
        self.piaoProcessor.resetPiaoCount()
        self.doubleProcessor.reset()
        self.louHuProcesssor.reset()
        self.setRecordUrl([])
        self.setRecordBaseId([])
        self.scheduleMgr.reset()
        self.msgProcessor.reset()
        self.pauseProcessor.reset()
        ftlog.debug('MajiangTableLogic.reset call.....')

    def isFriendTablePlaying(self):
        if self.getTableConfig(MFTDefine.IS_CREATE, 0):
            ftlog.debug('MajiangTableLogic.isFriendTablePlaying curCount:', self.scheduleMgr.curCount
                                , 'isOver:', self.scheduleMgr.isOver()
                                , 'isPlaying:', self.isPlaying())
            curCount = self.scheduleMgr.curCount
            return (curCount > 0) and (not self.scheduleMgr.isOver())

        return self.isPlaying()

    def isPlaying(self):
        """游戏是否开始"""
        if self.__table_win_state == MTableState.TABLE_STATE_NEXT:
            return True
        return False

    def curState(self):
        """当前状态
        """
        return self.addCardProcessor.getState() \
                + self.tingBeforeAddCardProcessor.getState() \
                + self.dropCardProcessor.getState() \
                + self.tableWinState \
                + self.qiangGangHuProcessor.getState() \
                + self.qiangExmaoPengProcessor.getState() \
                + self.qiangExmaoHuProcessor.getState() \
                + self.piaoProcessor.getState() \
                + self.doubleProcessor.getState() \
                + self.louHuProcesssor.getState() \
                + self.absenceProcessor.getState() \
                + self.daFengProcessor.getState() \
                + self.addCardHuProcessor.getState() \
                + self.dropCardHuProcessor.getState() \
                + self.shuffleHuProcessor.getState() \
                + self.tianHuProcessor.getState() \
                + self.zhisaiziProcessor.getState() \
                + self.flowerProcessor.getState() \
                + self.pauseProcessor.getState() \
                + self.huanSanZhangProcessor.getState() \
                + self.chargeProcessor.getState()

    def setTableConfig(self, config, roomConfig={}):
        """设置牌桌配置"""
        self.__table_config = config
        self.__room_config = roomConfig

        if MTDefine.TRUSTTEE_TIMEOUT not in self.__table_config:
            self.__table_config[MTDefine.TRUSTTEE_TIMEOUT] = 1
        if self.checkTableState(MTableState.TABLE_STATE_TING):
            self.__ting_rule_mgr.setTableConfig(config)

        # 将TableConfig传递到tableTileMgr，方便各种特殊操作的判断
        self.tableTileMgr.setTableConfig(self.tableConfig)
        self.addCardProcessor.setTableConfig(self.tableConfig)
        self.dropCardProcessor.setTableConfig(self.tableConfig)
        self.qiangGangHuProcessor.setTableConfig(self.tableConfig)
        self.piaoProcessor.setTableConfig(self.tableConfig)
        self.doubleProcessor.setTableConfig(self.tableConfig)
        self.zhisaiziProcessor.setTableConfig(self.tableConfig)
        self.flowerProcessor.setTableConfig(self.tableConfig)
        self.pauseProcessor.setTableConfig(self.tableConfig)
        self.absenceProcessor.setTableConfig(self.tableConfig)
        self.huanSanZhangProcessor.setTableConfig(self.tableConfig)
        self.chargeProcessor.setTableConfig(self.tableConfig)
        self.chargeProcessor.setRoomConfig(self.roomConfig)
        self.msgProcessor.setRoomInfo(self.roomConfig, self.tableConfig)
        cardCount = self.getTableConfig(MTDefine.HAND_COUNT, MTDefine.HAND_COUNT_DEFAULT)
        self.setHandCardCount(cardCount)
        # 出牌智能AI
        self.__drop_card_strategy = MDropCardStrategyFactory.getDropCardStrategy(self.playMode, self.getTableConfig(MTDefine.ROBOT_LEVEL, MTDefine.ROBOT_LEVEL_HIGH))

    def initScheduleMgr(self, cType, cValue, cCount):
        """
        cType - 计费类型
        cValue - 数值
        cCount - 房卡数量
        """
        self.setScheduleMgr(MTableScheduleFactory.getTableSchedule(cType))
        self.scheduleMgr.setValue(cValue)
        self.scheduleMgr.setFangkaCount(cCount)

    def getTableConfig(self, key, default):
        """获取牌桌配置"""
        value = self.__table_config.get(key, default)
        return value

    @property
    def tableConfig(self):
        return self.__table_config

    @property
    def roomConfig(self):
        return self.__room_config

    def queryBanker(self):
        """查询庄家
        """
        return self.bankerMgr.queryBanker()

    def updateScheduleQuan(self, playerCount, winLoose, winSeatId):
        """计算圈数
        """
        # 圈+1
        if self.playMode == MPlayMode.XUEZHANDAODI \
            or self.playMode == MPlayMode.XUELIUCHENGHE:
            extendInfo = self.getBankerExtendInfo()
        else:
            extendInfo = {MBanker.GANG_COUNT: self.tableTileMgr.gangCount}

        newbanker = self.bankerMgr.calcNextBanker(playerCount, winLoose, winSeatId, extendInfo)
        oldBanker = self.queryBanker()
        self.scheduleMgr.udpateQuan(oldBanker, newbanker)

    def getPlayerState(self, seatId):
        """获取用户状态"""
        if seatId >= self.__playerCount:
            return None

        return self.__players[seatId].state

    def getPlayer(self, seatId):
        """获取用户名称"""
        return self.__players[seatId]

    def addPlayer(self, player, seatId, isAutoDecide=False):
        """添加玩家"""
        if player in self.__players:
            ftlog.debug('already in table...')
            return
        if seatId >= self.__playerCount:
            ftlog.debug('no seat any more...')
            return

        ftlog.debug('MajiangTableLogic.addPlayer name:', player.name
                    , ' seatId:', seatId
                    , ' isAutoDecide:', isAutoDecide)

        self.players[seatId] = player
        ftlog.debug('MajiangTableLogic.addPlayer seatId:', seatId)
        self.msgProcessor.setPlayers(self.player)
        self.addCardProcessor.setPlayers(self.player)
        self.tingBeforeAddCardProcessor.setPlayers(self.player)
        self.dropCardProcessor.setPlayers(self.player)
        self.qiangGangHuProcessor.setPlayers(self.player) 
        self.qiangExmaoPengProcessor.setPlayers(self.player)
        self.qiangExmaoHuProcessor.setPlayers(self.player)
        self.piaoProcessor.setPlayers(self.player)
        self.doubleProcessor.setPlayers(self.player)
        self.absenceProcessor.setPlayers(self.player)
        self.huanSanZhangProcessor.setPlayers(self.player)
        self.chargeProcessor.setPlayers(self.player)
        player.setSeatId(seatId)
        player.setAutoDecide(isAutoDecide)

    def removePlayer(self, seatId):
        """
        删除玩家
        1）一般玩法，直接删除玩家
        2）血战到底，设置玩家离开，牌局结束后删除
        """
        if not self.players[seatId]:
            ftlog.debug("MajiangTableLogic.removePlayer seatId player is None")
            return
        ftlog.debug('MajiangTableLogic.removePlayer seatId:', seatId
                    , ' userState:', self.player[seatId].state
                    , ' isPlayIng:', self.isPlaying()
                    , ' userId:', self.player[seatId].userId
                    , ' playMode :', self.playMode)
        
        if self.isPlaying():
            if self.player[seatId].isConfirmLoose():
                # 认输也置玩家为leave，否则会多次remove玩家
                ftlog.debug('MajiangTableLogic.removePlayer already confirmLoose')
                self.player[seatId].leave()
                return
                
            if self.playMode == MPlayMode.XUEZHANDAODI and self.player[seatId].isWon():
                ftlog.debug('MajiangTableLogic.removePlayer set WonUserLeave')
                self.player[seatId].leave()
                return

        self.sendPlayerLeaveMsg(seatId)
        self.players[seatId] = None
        self.msgProcessor.setPlayers(self.__players)
        if self.isEmpty():
            self.reset()

    def isEmpty(self):
        """是否空桌"""
        for player in self.__players:
            if player:
                return False
        return True

    def setAutoDecideValue(self, seatId, adValue):
        """设置玩家的托管状态"""
        if self.players[seatId]:
            if not self.getTableConfig(MFTDefine.IS_CREATE, 0):
                ftlog.debug('MajiangTableLogic.setAutoDecideValue not in createTable Mode')
                self.players[seatId].setAutoDecide(adValue)

    def getSeats(self):
        seats = [0 for _ in range(self.playerCount)]
        for index, _ in enumerate(seats):
            if self.players[index]:
                seats[index] = self.__players[index].userId
        return seats

    def isTableFlow(self):
        '''
        在牌桌结束的时候判断是否流局
        有人胡->未流局
        没有胡->流局
        '''
        ftlog.debug('MajiangTableLogic.isTableFlow winNum:', self.winNum)
        if self.winNum == 0:
            return True
        else:
            return False

    def isThisRoundOver(self):
        '''牌桌是否为结束分为：
        1）剩余牌为0，则牌桌结束
        2）达到玩法的结束条件，也需要考虑认输情况
        '''
        ftlog.debug('MajiangTableLogic.isThisRoundOver playMode:', self.playMode)
        # 有三个人和了、离开、认输，游戏结束

        if self.tableTileMgr.getTilesLeftCount() == 0:
            return True

        if (self.tableStater.states & MTableState.TABLE_STATE_XUEZHAN) \
            or (self.tableStater.states & MTableState.TABLE_STATE_XUELIU):
            okNum = 0
            for player in self.player:
                if player.isObserver():
                    okNum += 1
            if okNum >= self.playerCount - 1:
                return True
        else:
            for player in self.player:
                if player.isWon():
                    return True
                
        return False

    def isGameOver(self):
        """是否已结束"""
        return self.tableWinState == MTableState.TABLE_STATE_GAME_OVER

    def shuffle(self):
        """洗牌
        """
        if len(self.players) != self.playerCount:
            ftlog.debug('seats error...')
            return

        ftlog.debug('table_logic shuffle win_automatically:', self.tableConfig.get(MTDefine.WIN_AUTOMATICALLY, 0))
        if self.tableConfig.get(MTDefine.WIN_AUTOMATICALLY, 0) or self.winRuleMgr.canDirectHuAfterTing():
            self.addCardProcessor.setAutoWin(True)
            self.qiangGangHuProcessor.setAutoWin(True)
            self.dropCardProcessor.setAutoWin(True)
            self.msgProcessor.setAutoWin(True)
        else:
            self.addCardProcessor.setAutoWin(False)
            self.qiangExmaoHuProcessor.setAutoWin(False)
            self.dropCardProcessor.setAutoWin(False)
            self.msgProcessor.setAutoWin(False)

        tiles_no_pao = self.tableConfig.get(MTDefine.TILES_NO_PAO, 0)
        self.tableTileMgr.setHaidilaoCount(tiles_no_pao)

        # 对局提示
        uids = self.msgProcessor.getBroadCastUIDs()
        self.scheduleMgr.sendScheduleTips(uids, self.gameId)

        banker = self.bankerMgr.queryBanker()
        # 调整发牌
        if self.tableConfig.get(MTDefine.REMOVE_FENG_ARROW_TILES):
            self.tableTileMgr.setRemoveArrow(1)
            self.tableTileMgr.setRemoveFeng(1)
        else:
            self.tableTileMgr.setRemoveArrow(0)
            self.tableTileMgr.setRemoveFeng(0)
        # 根据需要与规则计算好牌点和初始张数
        # 好牌点1，放在发牌的最前面，table负责将好牌派发给正确的人
        # 手牌张数13
        self.tableTileMgr.shuffle(1, self.handCardCount)
        ftlog.debug('Round Tiles:', self.tableTileMgr.getTiles(), "len of round", len(self.tableTileMgr.getTiles()))

        # 发牌
        self.setCurSeat(banker)
        cur_seat = self.curSeat

        for _ in range(self.playerCount):
            handCards = self.tableTileMgr.popTile(self.handCardCount)
            curPlayer = self.players[cur_seat]
            curPlayer.actionBegin(handCards)
            cur_seat = (cur_seat + 1) % self.playerCount
            
        # 四川麻将对玩家手牌排序
        self.tableTileMgr.sortHandTileColor(self.players, False)
        for seatId in xrange(self.playerCount):
            if self.tableTileMgr.handTileColorSort[seatId]:
                self.msgProcessor.table_call_hand_tile_sort(seatId, self.tableTileMgr.handTileColorSort[seatId])
        
        # 发送手牌的消息
        for cp in self.player:
            self.msgProcessor.sendMsgInitTils(cp.copyHandTiles()
                        , self.bankerMgr.queryBanker()
                        , cp.userId, cp.curSeatId)

        """结束"""
        pigus = self.tableTileMgr.getPigus()
        if pigus and len(pigus) > 0:
            self.msgProcessor.table_call_fanpigu(pigus)
            
        # 下发赖子
        self.sendLaiziInfo()
        magicFactors = self.tableTileMgr.getMagicFactors()
        if len(magicFactors) > 0:
            self.tableTileMgr.setMenTileInfo(magicFactors, banker)
        ftlog.debug('MajiangTableLogic.shuffle left tiles:', self.tableTileMgr.tiles)
        
    def sendLaiziInfo(self, isReconnect=False):
        '''
        下发赖子
        '''
        banker = self.bankerMgr.queryBanker()
        magicTiles = self.tableTileMgr.getMagicTiles()
        magicFactors = self.tableTileMgr.getMagicFactors()
        if len(magicTiles) > 0:
            self.msgProcessor.table_call_laizi(magicTiles, magicFactors, banker, isReconnect)
            
        # 前端先播放癞子动画，再播放马牌动画，马牌配置放到这里发送
        self.msgProcessor.table_call_maConfig(self.tableConfig.get(MTDefine.MAIMA, ''), self.tableConfig.get(MTDefine.MAIMA_COUNT, 0), isReconnect)

    def checkTableState(self, state):
        """校验牌桌状态机
        """
        return state & self.tableStater.states

    def popOneTile(self, seatId):
        """获取后面的length张牌"""
        tiles = self.tableTileMgr.popTile(1)
        if len(tiles) == 0:
            return None
        else:
            self.tableTileMgr.setAddTileInfo(tiles[0], seatId)
        return tiles[0]

    def isFirstAddTile(self, seatId):
        '''
        是本局的第一手牌
        '''
        return len(self.tableTileMgr.dropTiles[seatId]) == 0  # 出牌区没有牌

    def checkGameFlow(self, player):
        """
        检查是否流局
        返回值
            True 流局
            False 不流局
        """
        restTilesCount = self.tableTileMgr.getCheckFlowCount()
        if restTilesCount <= 0:
            ftlog.debug("no tile left, game flow...")
            self.gameFlow(player.curSeatId)
            return True

        if self.playMode == MPlayMode.XUEZHANDAODI \
                or self.playMode == MPlayMode.XUELIUCHENGHE:
            obCount = 0
            for player in self.players:
                if player and player.isObserver():
                    obCount += 1
                    
            ftlog.debug('MajiangTableLogic.checkGameFlow obCount:', obCount)
            if obCount >= self.playerCount - 1:
                ftlog.debug('one player left, game flow...')
                self.gameFlow(player.curSeatId)
                return True
        return False

    def double(self, seatId):
        ftlog.debug('MajiangTableLogic.double seatId:', seatId)
        self.doubleProcessor.double(seatId)
        if self.doubleProcessor.getState() == 0:
            self.beginGame()

    def noDouble(self, seatId):
        ftlog.debug('MajiangTableLogic.nodouble seatId:', seatId)
        self.doubleProcessor.noDouble(seatId)
        if self.doubleProcessor.getState() == 0:
            self.beginGame()

    def getChiPengGangExtendInfo(self, seatId):
        extendInfo = {}
        extendInfo['seatId'] = seatId
        if self.checkTableState(MTableState.TABLE_STATE_ABSENCE):
            extendInfo['absenceColor'] = self.tableTileMgr.absenceColors[seatId]
        return extendInfo

    def extendMao(self, seatId, extend, maoType):
        if not self.checkTableState(MTableState.TABLE_STATE_FANGMAO):
            ftlog.error('WRONG table action extendMao ...')
            return False

        ftlog.debug('MajiangTableLogic.extendMao seatId:', seatId
                    , ' tile:', extend
                    , ' maoType:', maoType)
        if self.addCardProcessor.getState() != 0:

            ftlog.debug('MajiangTableLogic.extendMao, self.__add_card_processor.getState() != 0')
            # 判断其他玩家是否可以抢锚碰
            # 如果没有玩家抢锚碰，给当前玩家发牌
            # 如果有玩家抢，等待改玩家的抢结果
            canExMao = True
            if self.checkTableState(MTableState.TABLE_STATE_QIANG_EXMAO) \
                or self.checkTableState(MTableState.TABLE_STATE_QIANG_EXMAO_HU) and (not self.tableTileMgr.isHaidilao()):
                ftlog.debug('MajiangTableLogic.extendMao, MTableState.TABLE_STATE_QIANG_EXMAO')
                for index in range(1, self.playerCount):
                    newSeatId = (seatId + index) % self.playerCount
                    # 判断是否抢
                    player = self.player[newSeatId]

                    checkTile = extend
                    pTiles = player.copyTiles()
                    pTiles[MHand.TYPE_HAND].append(checkTile)

                    hasPeng = False
                    hasHu = False
                    exInfo = MTableStateExtendInfo()
                    state = MTableState.TABLE_STATE_NEXT

                    if self.checkTableState(MTableState.TABLE_STATE_QIANG_EXMAO):
                        pengSolutions = self.pengRuleMgr.hasPeng(pTiles, checkTile, self.getChiPengGangExtendInfo(newSeatId))
                        ftlog.debug('MajiangTableLogic.extendMao, pTiles = player.copyTiles()', pTiles
                                     , ' checkTile', checkTile
                                     , ' pengSolutions', pengSolutions)
                        newPengSolutions = []
                        for peng in pengSolutions:
                            if checkTile in peng:
                                canDrop, _ = player.canDropTile(checkTile, self.playMode)
                                if canDrop:
                                    newPengSolutions.append(peng)
                                    break
                        ftlog.debug('MajiangTableLogic.extendMao, pTiles = player.copyTiles()', pTiles
                                     , ' checkTile', checkTile
                                     , ' newPengSolutions', newPengSolutions)


                        gangSolutions = self.gangRuleMgr.hasGang(pTiles, checkTile, MTableState.TABLE_STATE_NEXT, self.getChiPengGangExtendInfo(seatId))
                        ftlog.debug('MajiangTableLogic.extendMao, pTiles = player.copyTiles()', pTiles
                                     , ' checkTile', checkTile
                                     , ' gangSolutions', gangSolutions)
                        newGangSolutions = []
                        for gang in gangSolutions:
                            # 补锚抢杠只能抢算法里面的暗杠
                            if gang['style'] == MPlayerTileGang.MING_GANG:
                                continue

                            if checkTile in gang['pattern']:
                                canDrop, _ = player.canDropTile(checkTile, self.playMode)
                                if canDrop:
                                    gang['style'] = MPlayerTileGang.MING_GANG
                                    newGangSolutions.append(gang)
                                    break
                        ftlog.debug('MajiangTableLogic.extendMao, pTiles = player.copyTiles()', pTiles
                                     , ' checkTile', checkTile
                                     , ' newGangSolutions', newGangSolutions)

                        if len(newPengSolutions) > 0:
                            ftlog.debug('MajiangTableLogic.extendMao, qiangPeng')
                            # 可以抢锚碰，给用户选择
                            hasPeng = True
                            state = state | MTableState.TABLE_STATE_PENG
                            exInfo.appendInfo(MTableState.TABLE_STATE_PENG, newPengSolutions[0])
                            ftlog.debug('MajiangTableLogic.extendMao, user:', newSeatId
                                         , ' can peng. extendInfo:', exInfo)

                        if len(newGangSolutions) > 0:
                            ftlog.debug('MajiangTableLogic.extendMao, has qiangGang')
                            hasPeng = True
                            state = state | MTableState.TABLE_STATE_GANG
                            exInfo.appendInfo(MTableState.TABLE_STATE_GANG, newGangSolutions[0])
                            ftlog.debug('MajiangTableLogic.extendMao, user:', newSeatId
                                        , ' can Gang. extengInfo:', exInfo)

                        if hasPeng:
                            # 继续检查此人是
                            canExMao = False
                            timeOut = self.tableStater.getTimeOutByState(state)
                            self.addCardProcessor.reset()
                            self.dropCardProcessor.reset()
                            self.qiangGangHuProcessor.reset()
                            self.qiangExmaoPengProcessor.initProcessor(self.actionID
                                    , self.curSeat  # 补锚的人
                                    , maoType  # 补锚的类型
                                    , newSeatId  # 抢锚的人
                                    , state  # 抢锚的state
                                    , exInfo  # 抢锚人的exInfo
                                    , extend
                                    , timeOut)


                    if self.checkTableState(MTableState.TABLE_STATE_QIANG_EXMAO_HU):
                        winResult, winPattern = self.winRuleMgr.isHu(pTiles, checkTile, False, MWinRule.WIN_BY_OTHERS, [], [], newSeatId)
                        ftlog.debug('extenMao qianghu winResult:', winResult, ' winPattern:', winPattern)

                        if winResult:
                            hasHu = True
                            state = state | MTableState.TABLE_STATE_HU
                            winInfo = {}
                            winInfo['tile'] = checkTile
                            exInfo.appendInfo(state, winInfo)

                        if hasHu:
                            canExMao = False
                            timeOut = self.tableStater.getTimeOutByState(state)
                            self.addCardProcessor.reset()
                            self.dropCardProcessor.reset()
                            self.qiangGangHuProcessor.reset()
                            self.qiangExmaoHuProcessor.initProcessor(self.actionID
                                    , self.curSeat  # 补锚的人
                                    , maoType  # 补锚的类型
                                    , newSeatId  # 抢锚hu的人
                                    , MTableState.TABLE_STATE_QIANG_EXMAO_HU  # 抢锚的state
                                    , exInfo  # 抢锚人的胡牌exInfo
                                    , extend
                                    , timeOut)

                    if hasPeng or hasHu:
                        # 给玩家发送一个可以碰牌消息
                        message = self.msgProcessor.table_call_drop(self.curSeat
                            , player
                            , checkTile
                            , state
                            , exInfo
                            , self.actionID
                            , timeOut)
                        ftlog.debug('MajiangTableLogic.extendMao, table_call_drop: mmessage' , message)
                        self.msgProcessor.send_message(message, [player.userId])

            if canExMao:
                ftlog.debug('MajiangTableLogic.extendMao, self.justExmao(seatId,extend,maoType):')
                self.justExmao(seatId, extend, maoType)

        ftlog.debug('extendMao(self, seatId, extend, maoType) return True')
        return True

    # 不用检查抢 直接exmao
    def justExmao(self, seatId, extend, maoType):

        ftlog.debug('MTableLogic.justExmao seatId:', seatId, ' extend:', extend, 'maoType:', maoType)

        player = self.player[seatId]
        result, mao = player.actionExtendMao(extend, maoType)
        if not result:
            ftlog.info('table_logic.justExmao error, please check....')
            return False

        self.incrActionId('justExmao')
        # 广播补锚消息
        for index in range(self.playerCount):
            self.msgProcessor.table_call_after_extend_mao(self.curSeat, index, mao, self.actionID, self.player[index])

        # 记录锚杠牌得分
        gangBase = self.getTableConfig(MTDefine.GANG_BASE, 0)
        ftlog.debug('MajiangTableLogic.justExmao gangBase: ', gangBase)

        if gangBase > 0:
            result = self.initOneResult(MOneResult.RESULT_GANG, [], [], [], self.curSeat, self.curSeat, self.actionId, -1, MPlayerTileGang.EXMao_GANG)
            result.calcScore()

            # 设置牌局过程中的补锚番型信息
            if result.isResultOK():
                self.roundResult.setPlayMode(self.playMode)
                self.roundResult.setPlayerCount(self.playerCount)
                self.roundResult.addRoundResult(result)
                # 加上牌桌上局数总分
                tableScore = [0 for _ in range(self.playerCount)]
                if self.tableResult.score:
                    tableScore = self.tableResult.score
                currentScore = [0 for _ in range(self.playerCount)]
                allCoin = [0 for _ in range(self.playerCount)]
                allTableCoin = [0 for _ in range(self.playerCount)]
                for i in range(self.playerCount):
                    currentScore[i] = tableScore[i] + self.roundResult.score[i]

                allCoin, allTableCoin = self.getCoinInfo()
                self.msgProcessor.table_call_score(allCoin
                                                   , allTableCoin
                                                   , currentScore
                                                   , self.roundResult.delta
                                                   , False)

        # 补锚之后判断是否换宝
        self.changeMagicTileAfterChiPengExmao()
        self.processAddTile(player)
        return True

    def changeMagicTileAfterChiPengExmao(self):
        if self.playMode == MPlayMode.BAICHENG:
            changeMagicConfig = self.tableConfig.get(MTDefine.CHANGE_MAGIC, 0)
            if changeMagicConfig:
                bChanged = False
                magics = self.tableTileMgr.getMagicTiles(True)
                while (len(magics) > 0) and (self.tableTileMgr.getVisibleTilesCount(magics[0]) == 3):
                    if not self.tableTileMgr.updateMagicTile():
                        break

                    bChanged = True
                    magics = self.tableTileMgr.getMagicTiles(True)

                if bChanged:
                    # 发送换宝通知
                    self.updateBao()

    def fangMao(self, seatId, mao):
        '''
            放锚/放蛋
        '''
        if not self.checkTableState(MTableState.TABLE_STATE_FANGMAO):
            ftlog.error('WRONG table action...')
            return False

        maoPattern = mao['pattern']
        if len(maoPattern) != 3:
            ftlog.info('table_logic.fangMao card num error!!!')
            return False

        maoType = mao['type']
        ftlog.debug('table_logic.fangMao pattern:', maoPattern, ' type:', maoType)

        maoDanSetting = self.tableConfig.get(MTDefine.MAO_DAN_SETTING, MTDefine.MAO_DAN_NO)
        if not self.maoRuleMgr.checkMao(maoPattern, maoType, maoDanSetting):
            ftlog.info('table_logic.fangMaos mao:', mao , ' not valid!!!!!')
            return False

        ftlog.debug('table_logic.fangMao seatId:', seatId, ' mao:', mao)

        cp = self.player[seatId]
        if not cp.actionFangMao(maoPattern, maoType, self.actionID):
            ftlog.info('table_logic.fangMaos, execute fangMao to user error!!! maoPattern:', maoPattern, ' maoType:', maoType, ' actionId:', self.actionID)
            return False

        # 增加actionID
        self.incrActionId('fangMao')
        # 记录锚杠牌得分
        gangBase = self.getTableConfig(MTDefine.GANG_BASE, 0)
        ftlog.debug('MajiangTableLogic.fangMao gangBase: ', gangBase)

        if gangBase > 0:
            style = -1
            if maoType & MTDefine.MAO_DAN_ZFB:
                style = MPlayerTileGang.ZFB_GANG
            elif (maoType & MTDefine.MAO_DAN_YAO) or (maoType & MTDefine.MAO_DAN_JIU):
                style = MPlayerTileGang.YAOJIU_GANG
            result = self.initOneResult(MOneResult.RESULT_GANG, [], [], [], self.curSeat, self.curSeat, self.actionID - 1, -1, style)

            result.calcScore()

            # 设置牌局过程中的放锚番型信息
            if result.isResultOK():
                self.roundResult.setPlayMode(self.playMode)
                self.roundResult.setPlayerCount(self.playerCount)
                self.roundResult.addRoundResult(result)
                # 加上牌桌上局数总分
                tableScore = [0 for _ in range(self.playerCount)]
                if self.tableResult.score:
                    tableScore = self.tableResult.score
                currentScore = [0 for _ in range(self.playerCount)]
                for i in range(self.playerCount):
                    currentScore[i] = tableScore[i] + self.roundResult.score[i]

                allCoin, allTableCoin = self.getCoinInfo()
                self.msgProcessor.table_call_score(allCoin
                                                   , allTableCoin
                                                   , currentScore
                                                   , self.roundResult.delta
                                                   , False)


        tile = cp.curTile
        if tile not in cp.handTiles:
            tile = cp.handTiles[-1]
        ftlog.debug('MajiangTableLogic.fangMaocheck tile:', tile)
        state = MTableState.TABLE_STATE_NEXT
        state, extend = self.calcAddTileExtendInfo(cp, state, tile, {})

        timeOut = self.__table_stater.getTimeOutByState(state)
        for index in range(self.__playerCount):
            ftlog.debug('MajiangTableLogic.fangMaocheck self.__cur_seat=:', (self.__cur_seat), "index = ", index)
            if self.__cur_seat == index:
                self.__msg_processor.table_call_fang_mao(self.__players[index]
                            , mao
                            , self.player[self.curSeat].copyMaoTile()
                            , state
                            , index
                            , timeOut
                            , self.actionID
                            , extend)
            else:
                self.__msg_processor.table_call_fang_mao_broadcast(self.curSeat
                            , timeOut
                            , self.actionID
                            , self.__players[index].userId
                            , self.player[self.curSeat].copyMaoTile()
                            , mao)

        self.changeMagicTileAfterChiPengExmao()

    def ifCalcFangDan(self, seatId):
        '''
        是否计算放蛋/锚
        '''
        ftlog.debug('table_logic.ifCalcFangDan seatId:', seatId
                    , ' tileLeft:', self.tableTileMgr.getTilesLeftCount()
                    , ' maoDanSetting:', self.tableConfig.get(MTDefine.MAO_DAN_SETTING, MTDefine.MAO_DAN_NO)
                    , ' fangDanSetting:', self.tableConfig.get(MTDefine.MAO_DAN_FANG_TIME, MTDefine.MAO_DAN_FANG_FIRST_CARD)
                    , ' isFirstAddTile: ', self.isFirstAddTile(seatId))

        # 牌堆还有8张牌时，不放锚/蛋，8张未经过具体计算，先加一个范围
        if self.tableTileMgr.getTilesLeftCount() <= 8:
            return False

        maoDanSetting = self.tableConfig.get(MTDefine.MAO_DAN_SETTING, MTDefine.MAO_DAN_NO)
        if maoDanSetting == MTDefine.MAO_DAN_NO:
            return False

        return True

    def calcAddTileExtendInfo(self, cp, state, tile, addInfo={}):
        # 从抢杠听转过来听牌的处理需求
        mustTing = (state & MTableState.TABLE_STATE_GRABTING)
        # 扩展数据
        exInfo = MTableStateExtendInfo()
        # 判断和之外的状态，是否可听，可杠
        state = MTableState.TABLE_STATE_NEXT

        if self.checkTableState(MTableState.TABLE_STATE_BUFLOWER):
            oneFlowers = MFlowerRuleBase.hasFlower(cp.copyHandTiles())
            flowers = [[] for _ in range(self.playerCount)]
            flowers[cp.curSeatId] = oneFlowers
            flowerCount = MFlowerRuleBase.getFlowerCount(flowers)
            if flowerCount > 0:
                self.flowerProcessor.initProcessor(MTableState.TABLE_STATE_BUFLOWER, flowers, False, cp.curSeatId)
                return state, exInfo

        # 牌桌变为等待出牌状态
        if (not mustTing) and self.checkTableState(MTableState.TABLE_STATE_DROP):
            state = MTableState.TABLE_STATE_DROP

        # 自己上的牌，判断杠/胡，不需要判断吃。判断暗杠
        ftlog.debug('MTableLogic.calcAddTileExtendInfo mustTing:', mustTing, 'self.tableState:', self.tableStater.states)
        if (not mustTing) and self.checkTableState(MTableState.TABLE_STATE_GANG):
            tiles = cp.copyTiles()
            gangs = self.gangRuleMgr.hasGang(tiles, tile, MTableState.TABLE_STATE_NEXT, self.getChiPengGangExtendInfo(cp.curSeatId))

            if self.checkTableState(MTableState.TABLE_STATE_FANPIGU):
                pigus = self.tableTileMgr.getPigus()
                exInfo.appendInfo(MTableState.TABLE_STATE_FANPIGU, pigus)

            for gang in gangs:
                # 可以杠，给用户杠的选择，听牌后，要滤掉影响听口的杠
                canGang = True
                if self.playMode == MPlayMode.PANJIN:
                    if self.tableConfig.get(MTDefine.HUI_PAI, 0):
                        magics = self.tableTileMgr.getMagicTiles(True)
                        if gang["tile"] == magics[0]:
                            canGang = False

                if self.playMode == MPlayMode.MUDANJIANG:
                    if (gang['style'] == MPlayerTileGang.MING_GANG) and (tile not in gang['pattern']):
                        canGang = False
                    if cp.isStateFixeder():
                        # 听牌后不能暗杠
                        canGang = False

                if canGang and cp.canGang(gang, True, tiles, tile, self.winRuleMgr, self.tableTileMgr.getMagicTiles(cp.isTing()), self.tingRule):
                    state = state | MTableState.TABLE_STATE_GANG
                    exInfo.appendInfo(MTableState.TABLE_STATE_GANG, gang)

        # 判断听牌, 处于定缺时不做判听
        allTiles = cp.copyTiles()
        if self.checkTableState(MTableState.TABLE_STATE_TING) and self.absenceProcessor.getState() == 0 and self.tableTileMgr.isAbsenceFinish:
            # 玩家没有听并且在摸牌之后听的时候，计算听
            if not cp.isTing() and (self.tableConfig.get(MTDefine.TING_BEFORE_ADD_TILE, 0) == 0):
                """摸到一张牌，判断是否可以听牌"""
                tingResult, tingReArr = self.tingRule.canTing(allTiles, self.tableTileMgr.tiles, tile, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.curSeatId)
                ftlog.debug('MajiangTableLogic.processAddTile canTing result: ', tingResult, ' solution:', tingReArr, ' length: ', len(tingReArr))
                if tingResult and len(tingReArr) > 0:
                    # 可以听牌
                    state = state | MTableState.TABLE_STATE_TING
                    exInfo.appendInfo(MTableState.TABLE_STATE_TING, tingReArr)
                    '''
                    一种情况是玩家上来就胡牌，不会走tingAfterDropCard，则winNode为空，后续判断是否可杠会出问题
                    在这里判断如果winNode为空，则设置winNode为胡牌的winNodes
                    '''
                    if not cp.winNodes:
                        winNodes = []
                        for _nodes in tingReArr:
                            if _nodes['dropTile'] == tile:
                                winNodes.extend(_nodes['winNodes'])
                                cp.setWinNodes(winNodes)
                else:
                    cp.setWinNodes([])

        # 判断锚/蛋牌
        if self.checkTableState(MTableState.TABLE_STATE_FANGMAO):
            maoInfo = {}
            if self.ifCalcFangDan(cp.curSeatId) and (not cp.isTing()):
                isFirstAddtile = self.isFirstAddTile(cp.curSeatId)
                maos = self.maoRuleMgr.hasMao(cp.copyHandTiles()
                               , self.tableConfig.get(MTDefine.MAO_DAN_SETTING, MTDefine.MAO_DAN_NO)
                               , cp.getMaoTypes(), isFirstAddtile
							   , {"maoType":cp.getPengMaoTypes()})
                if len(maos) > 0:
                    maoInfo['mao_tiles'] = maos

            if not cp.isTing():
                extendMaos = self.maoRuleMgr.hasExtendMao(cp.copyHandTiles(), cp.getMaoTypes())
                if len(extendMaos) > 0:
                    maoInfo['mao_extends'] = extendMaos

            if ('mao_tiles' in maoInfo) or ('mao_extends' in maoInfo):
                state = state | MTableState.TABLE_STATE_FANGMAO
                exInfo.appendInfo(MTableState.TABLE_STATE_FANGMAO, maoInfo)


        # 判断是否自摸和牌
        magics = self.tableTileMgr.getMagicTiles(cp.isTing())
        if self.tableConfig.get(MTDefine.HONG_ZHONG_BAO, 0) and MTile.TILE_HONG_ZHONG not in magics:
            magics.append(MTile.TILE_HONG_ZHONG)

        if self.absenceProcessor.getState() == 0:  # 不在定缺阶段才做判胡
            winResult, winPattern = self.winRuleMgr.isHu(cp.copyTiles(), tile, cp.isTing(), MWinRule.WIN_BY_MYSELF, magics, cp.winNodes, cp.curSeatId)
            ftlog.debug('MajiangTable.processAddTile winResult:', winResult, ' winPattern:', winPattern)

            if winResult and self.checkTableState(MTableState.TABLE_STATE_HU):
                # 可以和，给用户和的选择
                state = state | MTableState.TABLE_STATE_HU
                winInfo = {}
                winInfo['tile'] = tile
                if addInfo.get('buFlower', 0):
                    winInfo['huaCi'] = 1
                exInfo.appendInfo(MTableState.TABLE_STATE_HU, winInfo)
        else:  # 记录在定缺，用来在send_tile消息时做判断提示让玩家不能打牌
            exInfo.appendInfo(MTableState.TABLE_STATE_ABSENCE, True)
        # 发牌处理
        ftlog.debug('MajiangTableLogic.processAddTile cp = :', cp.copyHandTiles())
        ftlog.debug('MajiangTableLogic.processAddTile tile:', tile)
        ftlog.debug('MajiangTableLogic.processAddTile extendInfo:', exInfo)

        if self.tableConfig.get(MTDefine.WIN_AUTOMATICALLY, 0) and state & MTableState.TABLE_STATE_HU:
            ftlog.debug('MajiangTableLogic.processAddTile win_auto state old:', state)
            state = MTableState.TABLE_STATE_HU
            ftlog.debug('MajiangTableLogic.processAddTile win_auto state new:', state)

        timeOut = self.tableStater.getTimeOutByState(state)
        self.addCardProcessor.initProcessor(self.actionID, state, cp.curSeatId, tile, exInfo, timeOut)
        return state, exInfo

    def processAddTileSimple(self, cp):
        if self.checkGameFlow(cp):
            return

        tile = self.popOneTile(cp.curSeatId)
        cp.actionAdd(tile)
        self.incrActionId('addTileSimple')
        state = MTableState.TABLE_STATE_NEXT
        extendInfo = MTableStateExtendInfo()
        # 补花补上来的牌，增加标记isBuFlower
        if self.checkTableState(MTableState.TABLE_STATE_BUFLOWER):
            bustate = MTableState.TABLE_STATE_BUFLOWER
            buInfo = {}
            buInfo['isBuFlowerAddTile'] = 1
            extendInfo.appendInfo(bustate, buInfo)
        self.sendMsgAddTile(state, tile, extendInfo, cp.curSeatId)

    def checkGenZhuang(self, cp):
        '''
        判断是否跟庄,之后放倒dropcardProcessor里实现
        :return:
        '''
        if self.tableConfig.get(MTDefine.GENZHUANG, 0):
            ftlog.debug("genzhuang,MTDefine.GENZHUANG:0")
            if cp.curSeatId == self.queryBanker() and len(self.tableTileMgr.dropTiles[cp.curSeatId]) == 1:
                gentile = self.tableTileMgr.dropTiles[cp.curSeatId][0]
                ftlog.debug("genzhuang,gentile:", gentile)
                isgentile = True
                for x in range(0, self.playerCount):
                    if x != cp.curSeatId:
                        if len(self.tableTileMgr.dropTiles[x]) == 1 \
                                and gentile == self.tableTileMgr.dropTiles[x][0]:
                            ftlog.debug("genzhuang,pass:")
                            pass
                        else:
                            isgentile = False
                            ftlog.debug("genzhuang,False:")
                            break

                if isgentile:
                    # 跟庄了，给前端发送通知
                    looses = [self.curSeat]
                    wins = []
                    observers = []
                    for player in self.players:
                        if player.curSeatId != self.curSeat:
                            if not player.isObserver():
                                wins.append(player.curSeatId)

                    for player in self.players:
                        seat = player.curSeatId
                        if (seat not in wins) and (seat not in looses):
                            observers.append(seat)

                    result = self.initOneResult(MOneResult.RESULT_GENZHUANG, wins, looses, observers, self.curSeat)
                    result.calcScore()

                    scoreList, NoContinueAddTile = self.updateCoinWithOneResult([], [], result.results[MOneResult.KEY_SCORE])
                    result.setCoinScore(scoreList)

                    self.roundResult.getChangeScore(result.results)
                    if MOneResult.KEY_DETAIL_CHANGE_SCORES in result.results:
                        detailChangeScores = result.results[MOneResult.KEY_DETAIL_CHANGE_SCORES]

                    if result.isResultOK():
                        self.roundResult.setPlayMode(self.playMode)
                        self.roundResult.setPlayerCount(self.playerCount)
                        self.roundResult.addRoundResult(result)

                        # 加上牌桌上局数总分
                        tableScore = [0 for _ in range(self.playerCount)]
                        if self.tableResult.score:
                            tableScore = self.tableResult.score
                        currentScore = [0 for _ in range(self.playerCount)]
                        allCoin = [0 for _ in range(self.playerCount)]
                        allTableCoin = [0 for _ in range(self.playerCount)]
                        for i in range(self.playerCount):
                            currentScore[i] = tableScore[i] + self.roundResult.score[i]

                        allCoin, allTableCoin = self.getCoinInfo()
                        self.msgProcessor.table_call_score(allCoin
                                                           , allTableCoin
                                                           , currentScore
                                                           , self.roundResult.delta
                                                           , False)
                        double = self.tableConfig.get(MTDefine.GENZHUANGJIABEI, MTDefine.GENZHUANGJIABEI_NO)
                        genZhuangScores = result.results[MOneResult.KEY_GENZHUANG_SCORE]
                        extendInfo = {}
                        if MOneResult.KEY_DETAIL_CHANGE_SCORES in result.results:
                            detailChangeScores = result.results[MOneResult.KEY_DETAIL_CHANGE_SCORES]
                            if detailChangeScores:
                                extendInfo['detailChangeScores'] = detailChangeScores
                        for player in self.player:
                            self.msgProcessor.table_call_update_genzhuang(player.userId, gentile, double,
                                                                          genZhuangScores, extendInfo)

                        # 发送对局流水信息
                        self.sendTurnoverResult()

                    ftlog.debug("genzhuang,gentile:", gentile, " scores: ", genZhuangScores)


    def processAddTile(self, cp, special_tile=None, addInfo={}):
        """上一张牌并处理
        参数：
            cp - 当前玩家
            tile - 当前上牌
        """
        # 玩家摸牌前，判断是否跟庄
        self.checkGenZhuang(cp)

        # 每次在玩家摸牌时，重置其过胡分数
        cp.resetGuoHuPoint()
        state = MTableState.TABLE_STATE_NEXT
        tile = 0

        if self.checkGameFlow(cp):
            ftlog.debug('MajiangTableLogic gameFlow with no tile...')
            return

        if self.checkTableState(MTableState.TABLE_STATE_FANPIGU) and special_tile:
            tile = special_tile
            self.tableTileMgr.updatePigu(special_tile)
            pigus = self.tableTileMgr.getPigus()
            self.msgProcessor.table_call_fanpigu(pigus)
        elif self.checkTableState(MTableState.TABLE_STATE_ABSENCE) and special_tile:
            tile = special_tile
        else:
            tile = self.popOneTile(cp.curSeatId)

        if not tile:
            return

        cp.actionAdd(tile)

        if self.winRuleMgr.isPassHu():
            # 清空之前漏胡的牌
            ftlog.debug("passHuClear", cp.curSeatId)
            self.tableTileMgr.clearPassHuBySeatId(cp.curSeatId)

        self.incrActionId('addTile')

        # 发牌之后几种胡牌的情况
        # 1）天胡
        # 5）地胡
        # 2）加牌胡，比如曲靖麻将，拿到4幺鸡，直接胡
        # 3）刮大风，比如牡丹江麻将，哈尔滨麻将
        # 4）发牌胡，比如鸡西麻将的无对胡，发牌后，手里没有对子，则直接胡

        # 天胡
        if self.winRuleMgr.isTianHu(cp, self.actionID, tile, self.tableTileMgr, self.tingRule):
            state = MTableState.TABLE_STATE_HU
            exInfo = MTableStateExtendInfo()
            winInfo = {}
            winInfo['tile'] = tile
            exInfo.appendInfo(state, winInfo)
            timeOut = self.tableStater.getTimeOutByState(state)
            self.tianHuProcessor.initProcessor(self.actionID, cp.curSeatId, state, tile, exInfo, timeOut)
            self.sendMsgAddTile(state, tile, exInfo, self.curSeat)
            return

        # 摸牌胡，比如曲靖麻将判断四幺鸡,注意在上一步tile加到cp手上以后再调用
        if self.winRuleMgr.isAddHu(cp, tile):
            state = MTableState.TABLE_STATE_HU
            exInfo = MTableStateExtendInfo()
            winInfo = {}
            winInfo['tile'] = tile
            winInfo['addHu'] = 1
            exInfo.appendInfo(state, winInfo)
            timeOut = self.tableStater.getTimeOutByState(state)
            self.addCardHuProcessor.initProcessor(self.actionID, cp.curSeatId, state, tile, exInfo, timeOut)
            self.sendMsgAddTile(state, tile, exInfo, self.curSeat)
            return

        # 判断刮大风情况
        if self.tableConfig.get(MTDefine.GUA_DA_FENG, 0) and cp.isTing():
            if MDaFengRuleBase.canWinByDaFeng(cp, cp.copyTiles(), tile, self.gangRuleMgr, self.winRuleMgr, self.tableTileMgr):
                state = MTableState.TABLE_STATE_HU
                exInfo = MTableStateExtendInfo()
                winInfo = {}
                winInfo['tile'] = tile
                winInfo['daFeng'] = 1
                exInfo.appendInfo(state, winInfo)
                timeOut = self.tableStater.getTimeOutByState(state)
                self.daFengProcessor.initProcessor(self.actionID, cp.curSeatId, state, tile, exInfo, timeOut)
                self.sendMsgAddTile(state, tile, exInfo, self.curSeat)
                return

        # 发牌胡，比如鸡西的无对胡
        if self.actionID == 1:
            for sId in range(self.playerCount):
                if self.winRuleMgr.isShuffleWin(self.player[sId].copyTiles(), tile, sId, self.playerCount):
                    state = MTableState.TABLE_STATE_HU
                    exInfo = MTableStateExtendInfo()
                    winInfo = {}
                    winInfo['tile'] = tile
                    winInfo['shuffleWin'] = 1
                    exInfo.appendInfo(state, winInfo)
                    timeOut = self.tableStater.getTimeOutByState(state)
                    self.shuffleHuProcessor.initProcessor(self.actionID, sId, state, tile, exInfo, timeOut)
                    self.sendMsgAddTile(state, tile, exInfo, self.curSeat)
                    return

        state, exInfo = self.calcAddTileExtendInfo(cp, state, tile, addInfo)

        if self.tableTileMgr.isHaidilao():
            # 海底捞只判断是否自摸
            state = state & MTableState.TABLE_STATE_HU
            if state > 0:
                newExInfo = MTableStateExtendInfo()
                if MTableStateExtendInfo.WIN in exInfo.extend:
                    newExInfo.appendInfo(MTableState.TABLE_STATE_HU, exInfo.extend[MTableStateExtendInfo.WIN][0])
                exInfo = newExInfo
            else:
                exInfo = MTableStateExtendInfo()
        ftlog.debug('MajiangTableLogic.processAddTile calcAddTileExtendInfo state:', state
                    , ' exInfo:', exInfo)

        self.sendMsgAddTile(state, tile, exInfo, self.curSeat)
        # 在牌池剩余30、10张牌时，提示用户
        if self.tableTileMgr.getTilesLeftCount() == 30 or self.tableTileMgr.getTilesLeftCount() == 10:
            for player in self.players:
                self.msgProcessor.table_call_show_tips(MTDefine.TIPS_NUM_11, player)
            

    def sendMsgAddTile(self, state, tile, exInfo, curSeat):
        timeOut = self.tableStater.getTimeOutByState(state)
        # 给curSeat位置发牌
        self.msgProcessor.table_call_add_card(self.players[curSeat]
                , tile, state, curSeat
                , timeOut
                , self.actionID
                , exInfo)
        # 通知其他人给curSeat位置发牌
        uids = self.msgProcessor.getBroadCastUIDs(self.players[curSeat].userId)
        self.msgProcessor.table_call_add_card_broadcast(self.curSeat
                                                        , timeOut
                                                        , self.actionID
                                                        , uids
                                                        , tile)


        if self.checkTableState(MTableState.TABLE_STATE_ABSENCE):
            # 第一次发牌为庄家发牌 定缺 前两次缺牌 提示
            colorOnSeatId = self.absenceProcessor.absenceColor[curSeat]
            ftlog.debug('MajiangTableLogic.sendMsgAddTile colorOnSeatId:', colorOnSeatId, "handTiles:", self.player[curSeat].handTiles)
            if MTile.getTileCountByColor(MTile.changeTilesToValueArr(self.player[curSeat].handTiles), colorOnSeatId) > 0:
                self.msgProcessor.table_call_show_tips(MTDefine.TIPS_NUM_8, self.players[curSeat])

        
        if self.players[curSeat].isRobot() and (not self.players[curSeat].isWon()):
            # 胡牌之后不再延时思考
            nPause = random.randint(1, 3)
            self.pauseProcessor.addPauseEvent(nPause * 0.5)

    def getCreateTableInfo(self, isReconnect=False):
        """获取自建桌信息"""
        if self.tableType != MTDefine.TABLE_TYPE_CREATE:
            return None
        
        cFinal = 0
        if self.scheduleMgr.isOver():
            cFinal = 1
        currentProgress = self.scheduleMgr.getCurrentProgress(isReconnect)

        # 风圈
        FengQuan = ['东', '南', '西', '北']
        FengQuanTile = FengQuan[self.scheduleMgr.curQuan % self.playerCount]

        ctInfo = {"create_table_no": self.getTableConfig(MFTDefine.FTID, '000000'),
            "time": fttime.getCurrentTimestamp(),
            "create_final": cFinal,
            "create_now_cardcount": self.scheduleMgr.curCount,
            "create_total_cardcount": self.scheduleMgr.totalCount,
            "quancount_now": self.scheduleMgr.curQuan,
            "quancount_total": self.scheduleMgr.totalQuan,
            "fengquan": FengQuanTile,
            "currentProgress": currentProgress,
            "currentBase": 0,
            "itemParams": self.getTableConfig(MFTDefine.ITEMPARAMS, {}),
            "hostUserId": self.getTableConfig(MFTDefine.FTOWNER, 0),
            'create_table_desc_list': self.getTableConfig(MFTDefine.CREATE_TABLE_DESCS, []),
            'create_table_option_name_list': self.getTableConfig(MFTDefine.CREATE_TABLE_OPTION_NAMES, []),
            'create_table_play_desc_list': self.getTableConfig(MFTDefine.CREATE_TABLE_PLAY_DESCS, []),
            'isBaoPaiShow': not self.getTableConfig(MTDefine.MAGIC_HIDE, 0),
            'voteHost': self.voteHost  # -1表示没人解散牌桌，0-3表示对应座位号的人解散牌桌
        }
        ftlog.info('MajiangTableLogic.getCreateTableInfo ctInfo:', ctInfo)

        return ctInfo

    def getCreateTableRecordName(self):
        """获取牌桌记录信息"""
        if self.runMode == MRunMode.CONSOLE:
            return 'console.json'

        curCount = self.scheduleMgr.curCount
        totalCount = self.scheduleMgr.totalCount
        recordName = '%s-%s-%d-%d-%d' % (self.playMode, self.getTableConfig(MFTDefine.FTID, '000000'), curCount, totalCount, fttime.getCurrentTimestamp())
        ftlog.debug('MajiangTableLogic.getCreateTableRecordName recordName:', recordName)
        return recordName

    def getCreateExtendBudgets(self):
        '''
        大结算时需要返回给客户端的统计信息
        '''
        createExtendBudgets = self.tableResult.createExtendBudgets(self.playerCount, self.playMode)
        return createExtendBudgets

    def sendCreateExtendBudgetsInfo(self, terminate):
        if self.tableType != MTDefine.TABLE_TYPE_CREATE:
            return

        # add by taoxc 本桌牌局结束进行大结算
        cebInfo = self.getCreateExtendBudgets()
        # 结算，局数不加1
        ctInfo = self.getCreateTableInfo()

        ftlog.debug('table_logic.shuffle cebInfo:', cebInfo)
        self.msgProcessor.table_call_game_all_stat(terminate, cebInfo, ctInfo)

    def calcBeginBanker(self):
        curRoundCount = self.scheduleMgr.curCount
        ftlog.debug('table_logic.shuffle curRoundCount:', curRoundCount)
        if 0 == curRoundCount:
            self.bankerMgr.getBanker(self.playerCount
                , True
                , 0
                , 0)

    def getCoinInfo(self):
        allCoin = [0 for _ in range(self.playerCount)]
        allTableCoin = [0 for _ in range(self.playerCount)]
        for i in range(self.playerCount):
            if self.player[i]:
                allCoin[i] = self.player[i].coin
                allTableCoin[i] = self.player[i].getTableCoin(self.gameId, self.tableId)
        return allCoin, allTableCoin

    def sendMsgTableInfo(self, seatId, isReconnect=False):
        """
        发送牌桌信息-创建牌桌及重连
        """
        ftlog.info('MajiangTableLogic.sendMsgTableInfo seatId:', seatId, ' isReconnect:', isReconnect)
        if not self.players[seatId]:
            ftlog.error('MajiangTableLogic.sendMsgTableInfo player info err:', self.players)

        deltaScore = [0 for _ in range(self.playerCount)]
        allScore = [0 for _ in range(self.playerCount)]
        allCoin, allTableCoin = self.getCoinInfo()
        if isReconnect:
            self.msgProcessor.setActionId(self.actionID)
            # 刷新一次当前分数
            tableScore = [0 for _ in range(self.playerCount)]
            if self.tableResult and self.tableResult.score:
                tableScore = self.tableResult.score
            roundScore = [0 for _ in range(self.playerCount)]
            if self.roundResult and self.roundResult.score:
                roundScore = self.roundResult.score
            for i in range(self.playerCount):
                allScore[i] = tableScore[i] + roundScore[i]

        ctInfo = self.getCreateTableInfo(isReconnect)
        btInfo, atInfo = self.getMagicInfo()

        dtInfo = self.tableConfig.get(MFTDefine.CREATE_TABLE_PLAY_INFO, None)

        self.msgProcessor.table_call_table_info(self.players[seatId].userId
                , self.bankerMgr.queryBanker()
                , self.bankerMgr.queryBankerLasttime()
                , seatId
                , isReconnect
                , 1
                , self.curSeat
                , 'play'
                , ctInfo
                , btInfo
                , dtInfo)
        if isReconnect:
            self.msgProcessor.table_call_score(allCoin
                                               , allTableCoin
                                               , allScore
                                               , deltaScore
                                               , isReconnect)
            
        self.playerOnline(seatId)
        self.sendPlayerLeaveMsg(self.players[seatId].userId)

        # 补发宝牌消息
        if ((not btInfo) or (len(btInfo) == 0)) and ((not atInfo) or (len(atInfo) == 0)):
            return

        self.msgProcessor.table_call_baopai(self.player[seatId], btInfo, atInfo)

    def playerReady(self, seatId, isReady):
        """玩家准备"""
        ftlog.info('MajiangTableLogic.playerReady seatId:', seatId, ' isReady:', isReady, ' tableState:', self.tableWinState, 'player:', self.player)
        if seatId < 0:
            return False

        if seatId == 0:
            self.refixTableStateByConfig()
            self.refixTableMultipleByConfig()

        if self.tableWinState == MTableState.TABLE_STATE_NONE or self.tableWinState == MTableState.TABLE_STATE_GAME_OVER:
            if isReady:
                self.player[seatId].ready()
                # 通知前端玩家状态为准备
                self.msgProcessor.table_ready_succ_response(self.player[seatId].userId, seatId)
                if self.tableType == MTDefine.TABLE_TYPE_NORMAL and (not self.player[seatId].isRobot()):
                    # 继续游戏时自动补充金币
                    self.chargeProcessor.autoChargeCoin(seatId)
            else:
                self.player[seatId].wait()

            tableBegin = self._isTableBegin()
            if tableBegin:
                self.playGameByState(self.tableStater.getStandUpSchedule(MTableState.TABLE_STATE_NONE))

            return tableBegin

    def playGameByState(self, state):
        ftlog.debug('MajiangTableLogic.playGameByState state:', state)

        if state == MTableState.TABLE_STATE_SAIZI:
            self.zhisaiziProcessor.initProcessor(MTableState.TABLE_STATE_SAIZI
                            , 3
                            , self.bankerMgr
                            , self.msgProcessor)
        elif state == MTableState.TABLE_STATE_NEXT:
            self.beginGame()
        elif state == MTableState.TABLE_STATE_PIAO:
            self.piaoProcessor.reset()
            self.piaoSchedule()
        elif state == MTableState.TABLE_STATE_DOUBLE:
            self.doubleSchedule()

    def absenceSchedule(self):
        self.absenceProcessor.beginAbsence()

    def doubleSchedule(self):
        self.doubleProcessor.beginDouble(self.actionID, self.tableConfig.get(MTDefine.DOUBLE_TIMEOUT, 9))

    def piaoSchedule(self):
        self.piaoProcessor.setBiPiaoPoint(self.tableConfig.get(MTDefine.BIPIAO_POINT, 0))
        self.piaoProcessor.setSchedule(MPiaoProcessor.SCHEDULE_PIAO_ORNOT)
        self.piaoProcessor.setPiaoTimeOut(self.tableConfig.get(MTDefine.PIAO_ORNOT_TIMEOUT, 5))
        self.piaoProcessor.setAcceptPiaoTimeOut(self.tableConfig.get(MTDefine.ACCEPT_PIAO_ORNOT_TIMEOUT, 5))
        self.piaoProcessor.setShowPiaoTimeOut(2)
        piaoList = self.tableConfig.get(MTDefine.PIAO_LIST, [1, 3, 5])
        self.piaoProcessor.beginPiao(self.msgProcessor, piaoList)

    def huanSanZhangSchedule(self):
        self.huanSanZhangProcessor.setSchedule(MHuanSanZhangProcessor.SCHEDULE_HUAN_INIT)
        self.huanSanZhangProcessor.setHuanSanZhangTimeOut(self.tableConfig.get(MTDefine.CHANGE_TILES_TIMEOUT, 12))
        self.huanSanZhangProcessor.beginHuanSanZhang(self.msgProcessor, self.actionID, self.pauseProcessor)

    def processChangeTiles(self, seatId):
        if 0 == self.huanSanZhangProcessor.getState():
            return
        ftlog.debug('MajiangTableLogic.processChangeTiles seatId:', seatId)
        self.huanSanZhangProcessor.autoDecide(seatId, self.msgProcessor)
        self.huanSanZhangEnd()

    def processAbsence(self, seatId):
        if 0 == self.absenceProcessor.getState():
            return
        ftlog.debug('MajiangTableLogic.processAbsence seatId:', seatId)
        self.absenceProcessor.autoDecide(seatId, self.msgProcessor, self.actionID)
        self.handleAbsenceEnd()

    def processCharge(self, seatId, chargeResult):
        ftlog.debug('MajiangTableLogic.processCharge seatId:', seatId
                    , ' chargeResult:', chargeResult)
        if not self.chargeProcessor.updateProcessor(self.actionID, seatId, chargeResult):
            return

        # 刷新金币
        delta = [0 for _ in range(self.playerCount)]
        allCoin, allTableCoin = self.getCoinInfo()
        self.msgProcessor.table_call_score(allCoin
                                           , allTableCoin
                                           , self.roundResult.score
                                           , delta
                                           , False)
        if self.chargeProcessor.isAllCharged():
            cp = self.player[self.curSeat]
            if self.isThisRoundOver():
                self.gameFlow(seatId)
                return
            # 有人离开，判断是否开始血战到底
            self.processCombol()
            gangInfo = self.chargeProcessor.gangInfo
            if gangInfo:
                self.processAddTile(cp, gangInfo.get('tile', None), gangInfo.get('info', {}))
            self.chargeProcessor.setGangInfo(None)

    def autoDecidePiao(self, seatId):
        if 0 == self.piaoProcessor.getState():
            return

        self.piaoProcessor.autoDecide(seatId, self.msgProcessor)
        self.checkPiaoOver()
        self.checkShowPiaoOver()

    def autoDecideDouble(self, seatId):
        if 0 == self.doubleProcessor.getState():
            return

        ftlog.debug('table_logic.autoDecideDouble seatId:', seatId, ' noDouble...')
        self.doubleProcessor.noDouble(seatId)
        if self.doubleProcessor.getState() == 0:
            self.playGameByState(self.tableStater.getStandUpSchedule(MTableState.TABLE_STATE_DOUBLE))

    def autoDecideCrapShoot(self):
        self.playGameByState(self.tableStater.getStandUpSchedule(MTableState.TABLE_STATE_SAIZI))

    def piao(self, seatId, piaoPoint):
        if 0 == self.piaoProcessor.getState():
            return
        self.piaoProcessor.piao(seatId, piaoPoint, self.msgProcessor)
        self.checkPiaoOver()

    def acceptPiao(self, seatId, piaoSirId, acceptOrNot):
        ftlog.debug('table_logic.acceptPiao seatId:', seatId
                    , ' piaoSeatId:', piaoSirId
                    , ' acceptOrNot', acceptOrNot)
        if 0 == self.piaoProcessor.getState():
            return
        self.piaoProcessor.acceptPiao(seatId, piaoSirId, acceptOrNot, self.msgProcessor)
        self.checkPiaoOver()

    def checkPiaoOver(self):
        ftlog.debug('table_logic checkPiaoOver')
        if self.piaoProcessor.isAllAcceptPiao():
            self.piaoProcessor.setAcceptPiaoTimeOut(0)
            self.piaoProcessor.broadCastPiao(self.msgProcessor)
            if self.playMode == MPlayMode.JINAN:
                self.piaoProcessor.setSchedule(self.piaoProcessor.SCHEDULE_SHOW_PIAO_SCORE)
            else:
                self.playGameByState(self.tableStater.getStandUpSchedule(MTableState.TABLE_STATE_PIAO))

    def checkShowPiaoOver(self):
        if self.piaoProcessor.updateShowPiao() and  self.playMode == MPlayMode.JINAN:
            self.playGameByState(self.tableStater.getStandUpSchedule(MTableState.TABLE_STATE_PIAO))

    def isAllPlayersReady(self):
        '''
        判断所有玩家是否都准备
        '''
        already = True
        for seat in range(self.playerCount):
            if (self.players[seat] == None) or (not self.players[seat].isReady()):
                ftlog.debug('Seat:', seat, ' nor ready....')
                already = False
                break

        ftlog.debug('MajiangTableLogic.isAllPlayersReady isAllReady:', already)
        return already

    def _isTableBegin(self):
        '''
        判断牌桌是否开始
        '''
        # 判断所有玩家是否都准备
        isAllReady = self.isAllPlayersReady()
        if not isAllReady:
            return isAllReady
        # 初始化本局结果
        self.setRoundResult(MRoundResults())
        self.tableConfig[MTDefine.TABLE_ROUND_ID] = self.getRoundId()
        self.scheduleMgr.changeCurCount(1)
        self.scheduleMgr.setBanker(self.bankerMgr.queryBanker())
        self.roundResult.setRoundIndex(self.scheduleMgr.curCount)
        self.resetWinNum()

        for seatId in range(self.playerCount):
            self.player[seatId].play()
        self.tableTileMgr.setPlayers(self.player)

        # 发牌之后修改牌桌状态
        self.setTableWinState(MTableState.TABLE_STATE_NEXT)
        ftlog.debug('tableWinState:', self.tableWinState)
        if self.tableObserver:
            self.tableObserver.onGameEvent(MTableStatistic.TABLE_START
                    , self.player
                    , self.getTableConfig(MTDefine.TABLE_ROUND_ID, fttime.getCurrentTimestamp()))

        # 更新当前圈数
        self.msgProcessor.table_call_update_round_count(self.scheduleMgr.curCount, self.scheduleMgr.totalCount)
        return True

    def beginGame(self):
        """
        开始游戏
        """
        
        # 记录游戏开始的日志
        ftlog.info('MajiangTableLogic.beginGame players:', self.msgProcessor.getBroadCastUIDs())

        if self.tableType == MTDefine.TABLE_TYPE_NORMAL and self.playMode == MPlayMode.JIPINGHU:
            # 结算服务费
            serviceScore = [0 for _ in range(self.playerCount)]
            self.ConsumeServiceFee(range(self.playerCount), serviceScore)
            # 刷新金币
            delta = [0 for _ in range(self.playerCount)]
            allCoin, allTableCoin = self.getCoinInfo()
            self.msgProcessor.table_call_score(allCoin
                                               , allTableCoin
                                               , self.roundResult.score
                                               , delta
                                               , False)

        # 判断胡是否需要庄家id
        banker = self.queryBanker()
        if self.winRuleMgr.isNeedBankId():
            self.winRuleMgr.setBankerId(banker)
        # 发送任务信息
        self.sendTaskInfoToUser()
        
        # 前端要求发送一下这个消息
        if self.playMode == MPlayMode.XUEZHANDAODI \
            or self.playMode == MPlayMode.XUELIUCHENGHE:
            for index in range(self.playerCount):
                self.msgProcessor.table_call_detail_desc(self.player[index].userId, index, 0, [], str(self.tableConfig.get(MTDefine.MAX_FAN, 0)) + "倍封顶")
        
        # 判断是否连庄 提示用户  金币场不提示
        if self.bankerMgr.bankerRemainCount > 0 and self.tableType != MTDefine.TABLE_TYPE_NORMAL:
            for player in self.player:
                util.sendPopTipMsg(player.userId, "恭喜玩家" + self.player[banker].name + "连庄")

        # 发牌
        self.shuffle()

        # 开局全体补花
        if self.checkTableState(MTableState.TABLE_STATE_BUFLOWER):
            flowers = MFlowerRuleBase.getAllFlowers(self.player)
            flowerCount = MFlowerRuleBase.getFlowerCount(flowers)
            if flowerCount > 0:
                self.flowerProcessor.initProcessor(MTableState.TABLE_STATE_BUFLOWER, flowers, True, self.curSeat)
                return

        # 给庄家发一张牌，等待庄家出牌 定缺、换三张情况下 简单发送手牌信息
        cp = self.player[self.curSeat]
        if self.checkTableState(MTableState.TABLE_STATE_ABSENCE) or self.checkTableState(MTableState.TABLE_STATE_CHANGE_TILE):
            self.processAddTileSimple(cp)
        else:
            self.processAddTile(cp)

        if self.playMode == MPlayMode.BAICHENG \
            or (self.playMode == MPlayMode.PANJIN and self.getTableConfig(MTDefine.HUI_PAI, 0)):
            self.updateBao()

        # 有换三张玩法的且人数为4 先进入换三张状态，后进入定缺状态，庄家摸完牌以后，才进行换牌选择
        if self.checkTableState(MTableState.TABLE_STATE_CHANGE_TILE):
            mixValueColor = self.getMixValueTilesColor(3)
            suggestTiles = self.getThreeTilesInHand(mixValueColor)
            forbidChangeTiles = self.getForbidChangeTileInHand()
            self.huanSanZhangProcessor.reset()
            self.huanSanZhangProcessor.setSuggestTiles(suggestTiles)
            self.huanSanZhangProcessor.setForbidChangeTiles(forbidChangeTiles)
            self.huanSanZhangSchedule()
        # 有定缺玩法的，设置进入定缺状态，庄家起手摸牌时不能打牌，且不显示胡牌 此时庄稼摸完第一张牌，开始让玩家做定缺选择
        elif self.checkTableState(MTableState.TABLE_STATE_ABSENCE):
            mixValueColor = self.getMixValueTilesColor(0)
            self.absenceProcessor.reset()
            self.absenceProcessor.setSuggestColor(mixValueColor)
            self.absenceSchedule()
            # 对局开始定缺，需要给前端播放动画的时间
            self.absenceProcessor.onBankerAddedFirstTile(self.actionID, self.pauseProcessor)


        # 赖子玩法开局加暂停
        mts = self.tableTileMgr.getMagicTiles()
        if len(mts)>0 and cp.isRobot():
            ftlog.debug('mingsong addPauseEvent')
            self.pauseProcessor.addPauseEvent(10)

        return True

    def getForbidChangeTileInHand(self):
        '''
        获取小于三张的牌
        '''
        forbidChangeTiles = [[] for _ in range(self.playerCount)]
        TILE_COLORS = [MTile.TILE_WAN, MTile.TILE_TONG, MTile.TILE_TIAO]
        for index in range(self.playerCount):
            handTiles = self.player[index].copyHandTiles()
            for color in TILE_COLORS:
                colorTiles = MTile.filterTiles(handTiles, color)
                if len(colorTiles) < 3:
                    forbidChangeTiles[index].extend(colorTiles)

        ftlog.debug('MajiangTableLogic.getForbidChangeTileInHand forbidChangeTiles:', forbidChangeTiles)
        return forbidChangeTiles

    def getMixValueTilesColor(self, tileLen=0):
        '''
        获取手牌中权值最小的花色
        参数：
        tileLen-待计算的手牌长度，比如为3时，该花色大于等于3张牌时开始计算，不足3张牌的不计算。
        '''
        TILE_COLORS = [MTile.TILE_WAN, MTile.TILE_TONG, MTile.TILE_TIAO]

        mixValueColor = [0 for _ in range(self.playerCount)]
        for cp in self.player:
            mixValue = 100000
            mixColor = 0  # 默认值为万
            handTiles = cp.copyHandTiles()
            for color in TILE_COLORS:
                colorTiles = MTile.filterTiles(handTiles, color)
                if tileLen != 0 and len(colorTiles) < tileLen:
                    continue
                colorValue = MTileValue.getGroupTilesValue(colorTiles)

                if mixValue > colorValue:
                    mixValue = colorValue
                    mixColor = color

            mixValueColor[cp.curSeatId] = mixColor
            ftlog.debug('MajiangTableLogic.getMixValueTilesColor seatId:', cp.curSeatId
                        , ' handTiles:', handTiles
                        , ' mixValue:', mixColor)

        ftlog.debug('MajiangTableLogic.getMixValueTilesColor mixValueColor:', mixValueColor)
        return mixValueColor

    def getThreeTiles(self, tiles):
        '''
        从手牌中获取三张牌，在牌数大于三张的情况下，去掉相同的牌，或者顺牌
        若去除后的牌小于3张，则随机从剩余的牌中获取，达到3张
        '''
        if len(tiles) <= 3:
            return tiles

        tiles.sort()
        newTiles = []
        removeTiles = []
        threeTiles = []
        for tile in tiles:
            if tile not in newTiles:
                if (tile - 1) in newTiles and (tile - 2) in newTiles:
                    newTiles.append(tile)
                    newTiles.remove(tile - 1)
                    removeTiles.append(tile - 1)
                else: newTiles.append(tile)
            else:
                removeTiles.append(tile)

        random.shuffle(newTiles)
        random.shuffle(removeTiles)
        ftlog.debug('MajiangTableLogic.getThreeTiles newTiles:', newTiles, 'removeTiles:', removeTiles)
        newLen = len(newTiles)
        if newLen != 3:
            if newLen > 3:
                for index in range(3):
                    threeTiles.append(newTiles[index])
            elif newLen < 3:
                threeTiles.extend(newTiles)
                for index in range(3 - newLen):
                    threeTiles.append(removeTiles[index])
            return threeTiles
        else:
            return newTiles

    def getThreeTilesInHand(self, mixValueColor):
        '''
        根据花色获取玩家手牌中该花色三张牌
        '''
        if len(mixValueColor) != self.playerCount:
            ftlog.debug('MajiangTableLogic.getThreeTilesInHand mixValueColor error')
            return []

        changeTiles = [[] for _ in range(self.playerCount)]
        for index in range(self.playerCount):
            handTiles = self.player[index].copyHandTiles()
            color = mixValueColor[index]
            handTiles = MTile.filterTiles(handTiles, color)
            changeTiles[index] = self.getThreeTiles(handTiles)

        return changeTiles

    def getRoundId(self):
        """
        获取局ID
        """
        if self.runMode == MRunMode.CONSOLE:
            return fttime.getCurrentTimestamp()
        else:
            return pluginCross.mj2dao.incrMajiang2RoundId()

    def checkLouHu(self, seatId):
        """
        判断当前座位号是否可以漏胡
        返回值：
        1）True 可以漏胡
        2）False 不可以漏胡
        """
        cp = self.players[seatId]
        if not cp.isTing():
            return False
        magicTiles = self.tableTileMgr.getMagicTiles(cp.isTing())
        ftlog.debug('MajiangTableLogic.checkLouHu seatId:', seatId
                    , ' magics:', magicTiles)

        # 鸡西听后如果胡的是宝牌则直接胡(通宝／宝边 宝中宝／宝夹） 哈尔滨也追加此功能
        duiBaoConfig = self.tableConfig.get(MTDefine.DUI_BAO, 0)
        if duiBaoConfig:
            hzConfig = self.tableConfig.get(MTDefine.HONG_ZHONG_BAO, 0)
            isMagicAfterTingHu = self.winRuleMgr.isMagicAfertTingHu(cp.isTing()
                            , cp.winNodes
                            , magicTiles
                            , {"hongZhong": hzConfig})
            if isMagicAfterTingHu:
                # 扩展数据
                self.setCurSeat(seatId)
                state = MTableState.TABLE_STATE_PASS_HU
                exInfo = MTableStateExtendInfo()
                winInfo = {}
                magicTiles = self.tableTileMgr.getMagicTiles(True)
                tile = magicTiles[0]
                winInfo['tile'] = tile  # 直接把宝牌给过去
                winInfo['magicAfertTing'] = 1
                exInfo.appendInfo(state, winInfo)
                timeOut = self.tableStater.getTimeOutByState(state)
                self.louHuProcesssor.initProcessor(self.actionID, cp.curSeatId, state, tile, exInfo, timeOut)
                self.addCardProcessor.reset()
                self.dropCardProcessor.reset()
                return True

        # 第二种漏胡的情况，刮大风漏宝
        if self.tableConfig.get(MTDefine.GUA_DA_FENG, 0) and \
            cp.isTing() and \
            self.tableConfig.get(MTDefine.GUA_DA_FENG_CALC_MAGIC, 0) and \
            len(magicTiles) > 0:

            magicTile = magicTiles[0]
            mTiles = cp.copyTiles()
            # 加入手牌
            mTiles[MHand.TYPE_HAND].append(magicTile)
            if MDaFengRuleBase.canWinByDaFeng(cp, mTiles, magicTile, self.gangRuleMgr, self.winRuleMgr, self.tableTileMgr):
                self.setCurSeat(seatId)
                state = MTableState.TABLE_STATE_PASS_HU
                exInfo = MTableStateExtendInfo()
                winInfo = {}
                winInfo['tile'] = magicTile
                winInfo['daFeng'] = 1
                exInfo.appendInfo(state, winInfo)
                timeOut = self.tableStater.getTimeOutByState(state)
                self.louHuProcesssor.initProcessor(self.actionID, cp.curSeatId, state, magicTile, exInfo, timeOut)
                self.addCardProcessor.reset()
                self.dropCardProcessor.reset()
                return True

        return False

    def checkChangeMagic(self, dropTile=None):
        '''
        检查是否换宝
        dropTile-出牌
        如果出牌时宝牌时，需调整检测换宝的条件，出牌需经过其他玩家的确认后才会落到牌池里，但这张牌已经是会被大家看到的牌了。
        此时dropTile+牌池里已有的牌，如果满三张，触发换宝。
        '''
        changeMagicConfig = self.tableConfig.get(MTDefine.CHANGE_MAGIC, 0)
        canChangeMagic = True
        if self.playMode == MPlayMode.JIXI or self.playMode == MPlayMode.HAERBIN \
            or self.playMode == MPlayMode.MUDANJIANG:
            playerTing = False
            for player in self.player:
                if player.isTing():
                    playerTing = True
                    break
            if not playerTing:
                canChangeMagic = False

        if changeMagicConfig and canChangeMagic:
            magics = self.tableTileMgr.getMagicTiles(True)
            while (len(magics) > 0) and ((self.tableTileMgr.getVisibleTilesCount(magics[0]) == 3) or (dropTile and self.tableTileMgr.getVisibleTilesCount(magics[0]) == 2 and magics[0] == dropTile)):
                if not self.tableTileMgr.updateMagicTile():
                    break

                magics = self.tableTileMgr.getMagicTiles(True)
                # 发送换宝通知
                self.updateBao()
                # 换宝后，从自己开始判漏
                for nextIndex in range(0, self.playerCount):
                    seatId = (self.curSeat + nextIndex) % self.playerCount
                    if self.checkLouHu(seatId):
                        # 有人漏胡，处理漏胡 漏胡为自摸
                        self.setCurSeat(seatId)
                        return True

        return False

    def gameNext(self):
        """
        下一步，游戏的主循环
        """
        if self.checkChangeMagic():
            return

        if self.curState() == MTableState.TABLE_STATE_NEXT:
            self.setCurSeat(self.nextSeatId(self.curSeat))
            ftlog.debug('table.gameNext now curSeatId:', self.curSeat)
            cp = self.player[self.curSeat]
            ftlog.debug('MajiangTableLogic.gameNext, canTingBeforeAddTile:',
                        self.tableConfig.get(MTDefine.TING_BEFORE_ADD_TILE, 0),
                        self.checkTableState(MTableState.TABLE_STATE_TING), cp.isTing())
            if self.checkTableState(MTableState.TABLE_STATE_TING) and \
                self.tableConfig.get(MTDefine.TING_BEFORE_ADD_TILE, 0) and \
                (not cp.isTing()):
                # 测试当前玩家是否可以听
                canTing, winNodes = self.tingRule.canTingBeforeAddTile(cp.copyTiles()
                                                   , self.tableTileMgr.tiles
                                                   , self.tableTileMgr.getMagicTiles(cp.isTing())
                                                   , cp.curSeatId)
                ftlog.debug('MajiangTableLogic.gameNext, check ting before add tile, canTing:', canTing
                            , ' winNodes:', winNodes)
                if canTing:
                    self.tingBeforeAddCardProcessor.initProcessor(self.actionID, MTableState.TABLE_STATE_TING, cp.curSeatId, winNodes, 9)
                    winTiles = self.tingBeforeAddCardProcessor.getWinTiles()
                    tingResult = MTing.calcTingResult(winNodes[0]['winNodes'], cp.curSeatId, self.tableTileMgr)
                    ftlog.debug('MajiangTableLogic.gameNext tingBeforeAddCardProcessor winTiles:', winTiles)
                    self.msgProcessor.table_call_ask_ting(cp.curSeatId, self.actionID, winTiles, tingResult, 9)
                    return

            self.processAddTile(cp)
            # 清空上一次杠的状态
            self.setLatestGangSeatId(-1)

    def nextSeatId(self, seatId):
        """计算下一个seatId
        newSeatId = (seatId + 1) % self.playerCount
        if self.players[newSeatId].isObserver():
            return self.nextSeatId(newSeatId)
        else:
            return newSeatId
         """
        for index in range(self.playerCount):
            newSeatId = (seatId + index + 1) % self.playerCount
            if self.players[newSeatId]:
                if self.players[newSeatId].isObserver():
                    continue
                else:
                    return newSeatId
        ftlog.warn("MajiangTableLogic.nextSeatId all players is Observer...")
        return 0

    def dropTile(self, seatId, dropTile, exInfo={}, key=None):
        """
        玩家出牌
        参数
        seatId - 座位号
        dropTile - 待出的牌
        exInfo - 扩展信息
        """
        ftlog.debug('table.dropTile seatId:', seatId, ' dropTile:', dropTile)

        if self.curSeat != seatId:
            # 如果不是轮到此玩家出牌，不响应
            ftlog.debug('table.dropTile wrong seatId...')
            return
        if (len(self.players[seatId].handTiles) % 3) != 2:
            # 再出牌就是相公了
            return

        # 定缺的时候不让打牌
        if self.absenceProcessor.getState() != 0:
            return

        # 花牌走补花处理
        if self.tableTileMgr.isFlower(dropTile):
            return self.buFlower(seatId, dropTile)

        # 当前玩家
        cp = self.players[seatId]

        cp.actionDrop(dropTile)

        # 重置玩家的过碰状态，和连杠次数
        cp.resetGuoPengTiles()
        cp.recordAndResetLianGangNum()

        # 设置出牌信息
        self.tableTileMgr.setDropTileInfo(dropTile, seatId)

        dropSeat = self.curSeat
        # 设置出牌
        self.addCardProcessor.reset()
        self.dropCardProcessor.reset()
        self.qiangGangHuProcessor.reset()
        self.qiangExmaoPengProcessor.reset()
        self.dropCardProcessor.initTile(dropTile, self.curSeat)

        # 修改操作标记
        self.incrActionId('dropTile')

        # 判断dropHu,必须在上一步设置出牌信息之后,因为取的是上一步dropTile加到已出牌组里后的数据
        winResultDrop, _ = self.winRuleMgr.isDropHu(cp)
        if winResultDrop:
            self.dropCardHuProcessor.initProcessor(self.actionID, self.curSeat, MTableState.TABLE_STATE_HU, dropTile, {}, 9)
            # 向玩家发送出牌结果，其他人收的到出牌结果么？
            for seat in range(self.playerCount):
                newSeat = (seatId + seat) % self.playerCount
                message = self.msgProcessor.table_call_drop(dropSeat, self.player[newSeat], dropTile, 0, {}, self.actionID, 0)
                self.msgProcessor.send_message(message, [self.player[ newSeat].userId])
            return

        # 测试其他玩家对于这张牌的处理
        dropMessages = [None for _ in range(self.playerCount)]
        dropStates = MTableState.TABLE_STATE_NEXT
        for seat in range(0, self.playerCount):
            newSeat = (seatId + seat) % self.playerCount
            if newSeat == dropSeat:
                winTiles = None
                if self.tableConfig.get(MFTDefine.CALC_WIN_TILES_AT_DROP, 0):
                    winTiles = self.winRuleMgr.calcWinTiles(cp.copyTiles())
                message = self.msgProcessor.table_call_drop(dropSeat, cp, dropTile, 0, {}, self.actionID, 0, winTiles)
                dropMessages[dropSeat] = message
            elif self.player[newSeat]:
                playerDropState, message = self.processDropTile(dropSeat, self.player[newSeat], dropTile)
                dropMessages[newSeat] = message
                dropStates |= playerDropState
                
        if dropStates:
            for message in dropMessages:
                message.setResult('hasAction', True)
                message.setResult('timeout', self.dropCardProcessor.timeOut)

        # 如果大家都对这张出牌没有反应，加入门前牌堆
        isAddedToMenTile = False
        if self.dropCardProcessor.getState() == 0:
            ftlog.debug('dropTile, no user wants tile:', dropTile, ' put to men tiles. seatId:', seatId)
            self.tableTileMgr.setMenTileInfo(dropTile, seatId)
            isAddedToMenTile = True

        # 最后一起给大家发送消息
        for index in range(self.playerCount):
            if index == seatId:
                dropMessages[index].setResult('key', key)
            self.msgProcessor.send_message(dropMessages[index], [self.player[index].userId])

        # 弃牌更新听牌预览
        self.updateTingResult(dropTile, False, seatId)

        # 检查换宝
        if exInfo.get('updateBao', False) and (self.playMode == MPlayMode.JIXI or \
            self.playMode == MPlayMode.HAERBIN  or \
            self.playMode == MPlayMode.MUDANJIANG):
            '''
            听牌之后的漏胡牌情况处理
            1）先算点炮，点炮时，根据是否胡牌计算漏胡
            1.1 不胡，计算漏胡
            1.2 胡牌，不计算漏胡
            2）其他状态，吃/碰/杠，充值状态，马上漏胡
            '''
            isDianPao = self.dropCardProcessor.getState() & MTableState.TABLE_STATE_HU
            if isDianPao:
                # 点炮，正常把宝发下去
                self.updateBao()
            else:
                # 不点炮，高优先级处理漏胡
                if self.checkLouHu(seatId):
                    ftlog.debug('MajiangTable.dropTile louhu seatId:', seatId)
                else:
                    if isAddedToMenTile:
                        if not self.checkChangeMagic():
                            self.updateBao()
                    else:
                        if not self.checkChangeMagic(dropTile):
                            self.updateBao()

    def processDropTile(self, dropSeat, cp, tile):
        '''
        处理出牌
        参数
        dropSeat - 出牌人的座位号
        cp - 当前玩家，对出牌是否感兴趣
        tile - 出牌
        '''
        ftlog.debug('MajiangTable.processDropTile...tile:', tile, 'seatId:', cp.curSeatId)
        nextSeatId = self.nextSeatId(self.curSeat)
        state = 0
        laiziPiNoPeng = 0
        exInfo = MTableStateExtendInfo()
        if cp.isObserver():
            # 玩家为观察者模式，则不关心他人出牌
            state = MTableState.TABLE_STATE_NEXT
            message = self.msgProcessor.table_call_drop(dropSeat, cp, tile, state, exInfo, self.actionID, 0)
            return state, message

        # 取出手牌
        tiles = cp.copyTiles()
        tiles[MHand.TYPE_HAND].append(tile)
        oriTiles = cp.copyTiles()
        oriTiles[MHand.TYPE_HAND].append(tile)
        if (not self.tableTileMgr.isHaidilao()):  # 海底牌不能吃、碰、杠、点炮，只能自摸
            # 听牌了不可以吃
            chiResults = []
            if (not cp.isTing()) and self.checkTableState(MTableState.TABLE_STATE_CHI):
                # 检测是否可吃
                chiResults = self.chiRuleMgr.hasChi(tiles, tile)
                if len(chiResults) != 0 and \
                    self.winRuleMgr.canWinAfterChiPengGang(tiles):
                    if nextSeatId == cp.curSeatId:
                        state |= MTableState.TABLE_STATE_CHI
                        ftlog.debug('MajiangTable.processDropTile seatId:', cp.curSeatId, ' can chi:', chiResults)
                        exInfo.setInfo(MTableState.TABLE_STATE_CHI, chiResults)

                    # 判断吃牌里面的吃听
                    if self.checkTableState(MTableState.TABLE_STATE_GRABTING):
                        for chiResult in chiResults:
                            for _tile in chiResult:
                                tiles[MHand.TYPE_HAND].remove(_tile)
                            tiles[MHand.TYPE_CHI].append(chiResult)

                            # 判断吃听 吃之后加听
                            tingResult, tingArr = self.tingRule.canTing(tiles, self.tableTileMgr.tiles, tile, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.curSeatId)
                            if tingResult:
                                state |= MTableState.TABLE_STATE_GRABTING
                                chiTing = {}
                                chiTing['tile'] = tile
                                chiTing['pattern'] = chiResult
                                chiTing['ting'] = tingArr
                                exInfo.appendInfo(MTableState.TABLE_STATE_CHI | MTableState.TABLE_STATE_GRABTING, chiTing)
                                ftlog.debug('MajiangTable.processDropTile seatId:', cp.curSeatId, ' can ting with chi patter:', chiResult)
                            # 还原手牌
                            tiles[MHand.TYPE_CHI].pop(-1)
                            tiles[MHand.TYPE_HAND].extend(chiResult)

            # 碰
            if (not cp.isStateFixeder()) and self.checkTableState(MTableState.TABLE_STATE_PENG) and not laiziPiNoPeng \
                    and self.maoRuleMgr.checkPengMao(tile, self.tableConfig.get(MTDefine.MAO_DAN_SETTING, MTDefine.MAO_DAN_NO),
                                         tiles[MHand.TYPE_MAO]):
                pengSolutions = self.pengRuleMgr.hasPeng(tiles, tile, self.getChiPengGangExtendInfo(cp.curSeatId))
                canDrop, _ = cp.canDropTile(tile, self.playMode)
                if not canDrop:
                    pengSolutions = []

                ftlog.debug('MajiangTable.processDropTile hasPeng pengSolution:', pengSolutions)
                if len(pengSolutions) > 0 and self.winRuleMgr.canWinAfterChiPengGang(tiles):
                    # 可以碰，给用户碰的选择
                    state = state | MTableState.TABLE_STATE_PENG
                    ftlog.debug('MajiangTable.processDropTile seatId:', cp.curSeatId, ' can peng')
                    exInfo.setInfo(MTableState.TABLE_STATE_PENG, pengSolutions)

                    for pengSolution in pengSolutions:
                        ftlog.debug('MajiangTable.processDropTile check pengSolution:', pengSolution, ' canTingOrNot')
                        if self.checkTableState(MTableState.TABLE_STATE_GRABTING):
                            for _tile in pengSolution:
                                tiles[MHand.TYPE_HAND].remove(_tile)
                            tiles[MHand.TYPE_PENG].append(pengSolution)

                            # 判断碰听，碰加听
                            tingResult, tingArr = self.tingRule.canTing(tiles, self.tableTileMgr.tiles, tile, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.curSeatId)
                            if tingResult:
                                state |= MTableState.TABLE_STATE_GRABTING
                                ftlog.debug('MajiangTable.processDropTile seatId:', cp.curSeatId, ' can ting with peng')
                                pengTing = {}
                                pengTing['tile'] = tile
                                pengTing['ting'] = tingArr
                                pengTing['pattern'] = pengSolution
                                exInfo.appendInfo(MTableState.TABLE_STATE_PENG | MTableState.TABLE_STATE_GRABTING, pengTing)
                            # 还原手牌
                            tiles[MHand.TYPE_PENG].pop(-1)
                            tiles[MHand.TYPE_HAND].extend(pengSolution)

            # 粘
            if (not cp.isTing()) and self.checkTableState(MTableState.TABLE_STATE_ZHAN):
                # 判断粘听，粘加听
                # 粘必须手里有这张牌
                ftlog.debug('MajiangTable.processDropTile try zhan, tile:', tile
                            , ' handTiles:', oriTiles[MHand.TYPE_HAND])

                tempcount = MTile.getTileCount(tile, oriTiles[MHand.TYPE_HAND])
                if tempcount == 2 or tempcount == 4:
                    tingResult, tingArr = self.tingRule.canTing(oriTiles, self.tableTileMgr.tiles, tile, self.tableTileMgr.getMagicTiles(cp.isTing()))
                    ftlog.debug('MajiangTable.processDropTile try zhan result tingResult:', tingResult
                                , ' tingArr:', tingArr)

                    if tingResult and len(tingArr) > 0:
                        newTingArr = []
                        for tingSolutin in tingArr:
                            newTingSolution = {}
                            winNodes = tingSolutin['winNodes']
                            newWinNodes = []
                            for winNode in winNodes:
                                pattern = winNode['pattern']
                                if len(pattern) == 7:
                                    newWinNodes.append(winNode)
                            if len(newWinNodes) > 0:
                                newTingSolution['dropTile'] = tingSolutin['dropTile']
                                newTingSolution['winNodes'] = newWinNodes
                                newTingArr.append(newTingSolution)
                        ftlog.debug('MajiangTable.processDropTile try zhan adjust result:', newTingArr)

                        if len(newTingArr) > 0:
                            # ting QiDui
                            zhanSolution = [tile, tile]
                            ftlog.debug('MajiangTable.processDropTile hasPeng zhanSolution:', zhanSolution)
                            state |= MTableState.TABLE_STATE_ZHAN
                            state |= MTableState.TABLE_STATE_GRABTING
                            ftlog.debug('MajiangTable.processDropTile seatId:', cp.curSeatId, ' can ting with zhan')
                            zhanTing = {}
                            zhanTing['tile'] = tile
                            zhanTing['ting'] = newTingArr
                            zhanTing['pattern'] = zhanSolution
                            exInfo.appendInfo(MTableState.TABLE_STATE_ZHAN | MTableState.TABLE_STATE_GRABTING, zhanTing)
                            tiles[MHand.TYPE_HAND].remove(tile)
                            tiles[MHand.TYPE_HAND].extend(zhanSolution)

            # 杠，出牌时，只判断手牌能否组成杠
            canGang = True
            if (self.playMode == MPlayMode.BAICHENG or self.playMode == MPlayMode.HAERBIN or self.playMode == MPlayMode.JIXI or self.playMode == MPlayMode.MUDANJIANG) \
                and cp.isTing():
                canGang = False
            if canGang and self.checkTableState(MTableState.TABLE_STATE_GANG) and (not (state & MTableState.TABLE_STATE_ZHAN)):
                gangs = self.gangRuleMgr.hasGang(tiles, tile, MTableState.TABLE_STATE_DROP, self.getChiPengGangExtendInfo(cp.curSeatId))
                newGangs = []
                for gang in gangs:
                    checkTile = gang['pattern'][0]
                    canDrop, _ = cp.canDropTile(checkTile, self.playMode)
                    if canDrop:
                        newGangs.append(gang)
                gangs = newGangs

                if len(gangs) > 0 and self.winRuleMgr.canWinAfterChiPengGang(tiles):
                    for gang in gangs:
                        if gang['style'] != MPlayerTileGang.MING_GANG and gang['style'] != MPlayerTileGang.CHAOTIANXIAO_MING:
                            continue
                        # 可以杠，给用户杠的选择，听牌后，要滤掉影响听口的杠
                        if cp.canGang(gang, True, tiles, tile, self.winRuleMgr, self.tableTileMgr.getMagicTiles(cp.isTing()), self.tingRule):
                            state = state | MTableState.TABLE_STATE_GANG
                            ftlog.debug('MajiangTable.processDropTile seatId:', cp.curSeatId, ' can gang: ', gang)
                            exInfo.appendInfo(MTableState.TABLE_STATE_GANG, gang)
                            if self.checkTableState(MTableState.TABLE_STATE_FANPIGU):
                                pigus = self.tableTileMgr.getPigus()
                                exInfo.appendInfo(MTableState.TABLE_STATE_FANPIGU, pigus)

                        # 如果杠完，上任何一张牌，都可以听，则可以有杠听。此时确定不了听牌的听口，需杠牌上牌后确定听口
                        if (not cp.isTing()) and self.checkTableState(MTableState.TABLE_STATE_GRABTING):
                            ftlog.debug('handTile:', tiles[MHand.TYPE_HAND])
                            for _tile in gang['pattern']:
                                tiles[MHand.TYPE_HAND].remove(_tile)
                            tiles[MHand.TYPE_GANG].append(gang)

                            leftTiles = copy.deepcopy(self.tableTileMgr.tiles)
                            newTile = leftTiles.pop(0)
                            tiles[MHand.TYPE_HAND].append(newTile)

                            # 判断杠听，杠加听
                            tingResult, tingArr = self.tingRule.canTing(tiles, leftTiles, tile, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.curSeatId)
                            if tingResult:
                                state |= MTableState.TABLE_STATE_GRABTING
                                ftlog.debug('MajiangTable.processDropTile seatId:', cp.curSeatId, ' can ting with gang')
                                gangTing = {}
                                gangTing['tile'] = tile
                                gangTing['ting'] = tingArr
                                gangTing['pattern'] = gang['pattern']
                                gangTing['style'] = gang['style']
                                exInfo.appendInfo(MTableState.TABLE_STATE_GANG | MTableState.TABLE_STATE_TING, gangTing)

                            # 还原手牌
                            tiles[MHand.TYPE_GANG].pop(-1)
                            tiles[MHand.TYPE_HAND].extend(gang['pattern'])
                            tiles[MHand.TYPE_HAND].remove(newTile)

        winResult = False
        needZimo = False
        if self.checkTableState(MTableState.TABLE_STATE_TING) \
            and self.tableConfig.get(MTDefine.ZIMO_AFTER_TING, 0) == 1 \
            and cp.isTing():
            needZimo = True

        if self.tableConfig.get(MTDefine.WIN_BY_ZIMO, MTDefine.WIN_BY_ZIMO_NO) == MTDefine.WIN_BY_ZIMO_OK:
            needZimo = True

        # 牌池数少于某个设置时，不和点炮
        ftlog.debug('start MajiangTable.processDropTile', tile)
        if (not self.tableTileMgr.isHaidilao()) and (not needZimo):
            magics = self.tableTileMgr.getMagicTiles(cp.isTing())
            if self.tableConfig.get(MTDefine.HONG_ZHONG_BAO, 0) and MTile.TILE_HONG_ZHONG not in magics:
                magics.append(MTile.TILE_HONG_ZHONG)

            # 给winMgr传入当前杠牌的座位号
            self.winRuleMgr.setLastGangSeat(self.latestGangSeatId)
            self.winRuleMgr.setCurSeatId(self.curSeat)
            winResult, winPattern = self.winRuleMgr.isHu(tiles, tile, cp.isTing(), MWinRule.WIN_BY_OTHERS, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.winNodes, cp.curSeatId)
            self.winRuleMgr.setCurSeatId(-1)
            ftlog.debug('MajiangTable.processDropTile, winResutl:', winResult, 'tile', tile, 'winPattern:', winPattern)

        if self.checkTableState(MTableState.TABLE_STATE_HU) and winResult:
            # 可以和，给用户和的选择
            state = state | MTableState.TABLE_STATE_HU
            if self.tableConfig.get(MTDefine.WIN_AUTOMATICALLY, 0):
                state = MTableState.TABLE_STATE_HU

            ftlog.debug('MajiangTable.processDropTile seatId:', cp.curSeatId, ' can win stats:', state)

        timeOut = self.tableStater.getTimeOutByState(state)
        self.dropCardProcessor.initProcessor(self.actionID, cp.curSeatId, state, exInfo, timeOut)

        message = self.msgProcessor.table_call_drop(dropSeat, cp, tile, state, exInfo, self.actionID, timeOut)
        # 返回结果
        return state, message

    def getMagicInfo(self):
        """
        获取宝牌的协议信息
        """
        bNodes = []
        magics = self.tableTileMgr.getMagicTiles(True)
        for magic in magics:
            bNode = {}
            bNode['tile'] = magic
            bNodes.append(bNode)

        abandones = self.tableTileMgr.getAbandonedMagics()
        aNodes = []
        for ab in abandones:
            aNode = {}
            aNode['tile'] = ab
            aNodes.append(aNode)

        ftlog.debug('MajiangTable.getMagicInfo baopaiInfo:', bNodes, ' abandonesInfo:', aNodes)
        return bNodes, aNodes

    def updateBao(self):
        """
        通知已听牌玩家宝牌
        """
        bNodes, aNodes = self.getMagicInfo()
        ftlog.debug('MajiangTable.updateBao bNodes:', bNodes, ' aNodes:', aNodes)
        if len(bNodes) == 0 and len(aNodes) == 0:
            return

        # 鸡西设置了暗宝 不通知客户端
        if  self.tableConfig.get(MTDefine.MAGIC_HIDE, 1):
            bNodes = None

        for player in self.player:
            if player.isTing() or self.playMode == MPlayMode.BAICHENG or self.playMode == MPlayMode.PANJIN:
                self.msgProcessor.table_call_baopai(player, bNodes, aNodes)
            else:
                self.msgProcessor.table_call_baopai(player, None, aNodes)

    def tingBeforeAddCard(self, seatId, actionId):
        '''
        摸牌前上听
        '''
        if self.tingBeforeAddCardProcessor.updateProcessor(actionId, MTableState.TABLE_STATE_TING, seatId):
            winNodes = self.tingBeforeAddCardProcessor.winNodes
            ftlog.debug('MajiangTable.tingBeforeAddCard seatId:', seatId
                        , ' actionId:', actionId
                        , ' winNodes:', winNodes)
            self.player[seatId].actionTing(winNodes[0]['winNodes'])
            self.tableTileMgr.appendTingIndex(seatId)
            tingResult = MTing.calcTingResult(winNodes[0]['winNodes'], seatId, self.tableTileMgr)
            self.player[seatId].setTingResult(tingResult)
            self.setCurSeat(seatId)

            # actionTingLiang当中会根据听亮模式，来决定是否亮牌，默认不亮牌
            self.player[seatId].actionTingLiang(self.tableTileMgr, -1, self.actionID, [])

            allWinTiles = []
            for player in self.player:
                if player.tingLiangWinTiles:
                    allWinTiles.append(player.tingLiangWinTiles)
                else:
                    allWinTiles.append(None)

            self.incrActionId('tingBeforeAddCard')
            # 重置状态机
            self.tingBeforeAddCardProcessor.reset()
            for player in self.player:
                # 把听牌信息发送给所有玩家，给自己主要是标示自己要胡的牌
                self.msgProcessor.table_call_after_ting(self.player[self.curSeat]
                    , self.actionID
                    , player.userId
                    , allWinTiles
                    , tingResult)
            # 发牌
            self.processAddTile(self.player[seatId])

    def tingAfterDropCard(self, seatId, dropTile, tingFlag, kouTiles, exInfo, key=None):
        """
        听牌状态 有的玩法不用听牌就可以胡 所以要计算
        """
        # 判断玩家是否可以打这张牌
        curPlayer = self.players[seatId]
        magicTiles = self.tableTileMgr.getMagicTiles()
        canDrop, reason = curPlayer.canDropTile(dropTile, self.playMode, magicTiles)
        if not canDrop:
            Majiang2Util.sendShowInfoTodoTask(curPlayer.userId, 9999, reason)
            return
        
        winNodes = []
        if exInfo:
            winNodes, ishuAll = exInfo.getWinNodesByDropTile(dropTile)
            ftlog.info('MajiangTable.tingAfterDropCard, winNodes:', winNodes)
        if winNodes:
            tingResult = MTing.calcTingResult(winNodes, seatId, self.tableTileMgr)
            self.players[seatId].setTingResult(tingResult)
            self.player[seatId].setWinNodes(winNodes)
            self.player[seatId].setishuAll(ishuAll)
        else:
            self.player[seatId].setTingResult([])
            self.player[seatId].setWinNodes([])
            self.player[seatId].setishuAll(False)

        self.setCurSeat(seatId)
        # 重置状态机
        self.addCardProcessor.reset()
        self.dropCardProcessor.reset()
        self.qiangGangHuProcessor.reset()
        self.qiangExmaoPengProcessor.reset()

        if self.tableTileMgr.isHaveTing() and tingFlag:
            ftlog.debug('MajiangTable.tingAfterDropCard dropTile:', dropTile, 'tingFlag:', tingFlag)
            allWinTiles = []
            self.players[seatId].actionTing(winNodes)
            self.tableTileMgr.appendTingIndex(seatId)
            # actionTingLiang当中会根据听亮模式，来决定是否亮牌，默认不亮牌
            self.players[seatId].actionTingLiang(self.tableTileMgr, dropTile, self.actionID, kouTiles)
            for player in self.players:
                if player.tingLiangWinTiles:
                    allWinTiles.append(player.tingLiangWinTiles)
                else:
                    allWinTiles.append(None)
            for player in self.players:
                # 把听牌信息发送给所有玩家，给自己主要是标示自己要胡的牌
                self.msgProcessor.table_call_after_ting(self.players[seatId]
                    , self.actionID
                    , player.userId
                    , allWinTiles
                    , tingResult)
        
        infoExtend = {}
        if tingFlag:
            infoExtend = {"updateBao": True}

        # 出牌
        self.dropTile(seatId, dropTile, infoExtend, key)

    """
    以下四种情况为别人打出的牌，其他人可以有的行为
    分别是
        吃
        碰
        杠
        胡
    同一人或者多个人有不同的选择，状态机的大小代表优先级。
    响应的规则是：
    优先响应最高优先级的操作，最高优先级的操作取消，响应次高优先级的操作。
    一人放弃响应，此人的状态机重置
    
    特殊说明：
        此时当前座位还是出牌的人
        获取出牌之外的人的状态进行比较
    """
    def chiTile(self, seatId, chiTile, chiPattern, state=MTableState.TABLE_STATE_CHI):
        """吃别人的牌
        只有一个人，且只判断__drop_card_processor
        """
        ftlog.info('MajiangTable.chiTile chiTile:', chiTile
                   , ' chiPattern:', chiPattern
                   , ' seatId:', seatId)
        # 调整pattern顺序
        chiPattern.sort()

        cp = self.players[seatId]

        if self.playMode == MPlayMode.PANJIN:
            # 别人出牌检查过胡
            # pass后将漏胡的牌加入过胡牌数组,下次轮到自己回合时清空
            if self.winRuleMgr.isPassHu() and self.dropCardProcessor.getStateBySeatId(seatId) & MTableState.TABLE_STATE_HU:
                passHuTile = []
                cp = self.player[seatId]
                for testTile in xrange(1, 40):
                    allTile = cp.copyTiles()
                    allTile[MHand.TYPE_HAND].append(testTile)
                    winResult, _ = self.winRuleMgr.isHu(allTile, testTile, cp.isTing(), MWinRule.WIN_BY_OTHERS, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.winNodes, cp.curSeatId)
                    if winResult:
                        passHuTile.append(testTile)

                ftlog.debug("addPassHuTileByDrop chi", seatId, passHuTile)
                for tmpTile in passHuTile:
                    self.tableTileMgr.addPassHuBySeatId(seatId, tmpTile)

        # 只传吃牌的组合，如果在听牌吃牌中，自动听牌，暂时做的是这样
        if self.dropCardProcessor.updateProcessor(self.actionID, seatId, state, chiTile, chiPattern):
            exInfo = self.dropCardProcessor.getExtendResultBySeatId(seatId)
            self.dropCardProcessor.reset()
            lastSeatId = self.curSeat
            cp.actionAdd(chiTile)
            cp.actionChi(chiPattern, chiTile, self.actionID, lastSeatId)
            self.setCurSeat(cp.curSeatId)
            self.incrActionId('chiTile')

            chiTingNotGrab = False
            if self.checkTableState(MTableState.TABLE_STATE_TING) and self.tingRuleMgr.canTingAfterPeng(cp.copyTiles()):
                _, tingArr = self.tingRuleMgr.canTing(cp.copyTiles()
                                                          , self.tableTileMgr.tiles
                                                          , chiTile
                                                          , self.tableTileMgr.getMagicTiles(cp.isTing())
                                                          , cp.curSeatId)
                if len(tingArr) > 0:
                    exInfo.appendInfo(MTableState.TABLE_STATE_TING, tingArr)
                    chiTingNotGrab = True
                    ftlog.debug('MajiangTable.chiTile seatId:', cp.curSeatId, ' can ting with chi (not grab ting)')
                else:
                    cp.setWinNodes([])

            timeOut = self.tableStater.getTimeOutByState(state)
            # 吃牌转出牌，抢听变为听
            if state & MTableState.TABLE_STATE_GRABTING or chiTingNotGrab:
                self.addCardProcessor.initProcessor(self.actionID, MTableState.TABLE_STATE_TING, cp.curSeatId, chiTile, exInfo, timeOut)
                self.addCardProcessor.setMustTing(state & MTableState.TABLE_STATE_GRABTING)
            else:
                self.addCardProcessor.initProcessor(self.actionID, MTableState.TABLE_STATE_DROP, cp.curSeatId, chiTile, exInfo, timeOut)

            ftlog.debug('chiTile init addCardProcessor state:', state
                    , ' chiTile:', chiTile
                    , ' exInfo.extend:', exInfo.extend)

            actionInfo = {}
            if state & MTableState.TABLE_STATE_GRABTING:
                # {'tile': 28, 'pattern': [27, 28, 29], 'ting': [{'winNodes': [{'winTile': 24, 'pattern': [[28, 28], [23,       24, 25], [6, 7, 8]], 'winTileCount': 2}], 'dropTile': 15}]}
                ting_action = None
                ftlog.debug('chiTile grabTing exInfo.extend:', exInfo.extend)
                tingInfo = exInfo.extend['chiTing'][0]
                ftlog.debug('chiTile grabTing tingInfo:', tingInfo)
                # [8,[[12,1,1]]]
                ting_action = exInfo.getGrabTingAction(tingInfo, seatId, self.tableTileMgr, True)
                ftlog.debug('chiTile after chi, ting_action:', ting_action)
                actionInfo['ting_action'] = ting_action

            # 非抢听情况下，部分玩法如果能碰后听牌，需要马上听牌
            if chiTingNotGrab:
                ting_action_not_grab = exInfo.getTingResult(self.player[seatId].copyTiles(), self.tableTileMgr, seatId, self.tilePatternChecker)
                if ting_action_not_grab:
                    tingliang_action = exInfo.getTingLiangResult(self.tableTileMgr)
                    if tingliang_action:
                        actionInfo['tingliang_action'] = tingliang_action
                    kou_ting_action = exInfo.getCanKouTingResult(self.tableTileMgr, seatId)
                    if kou_ting_action:
                        actionInfo['kou_ting_action'] = kou_ting_action
                    # 抢听把ting_action占用了，只能用ting_action_not_grab区分
                    actionInfo['ting_action_not_grab'] = ting_action_not_grab

            # 吃碰完能补杠,现在只有曲靖有需求,暂时加上playMode判断
            if self.tableTileMgr.canGangAfterPeng():
                gang = self.gangRuleMgr.hasGang(cp.copyTiles(), 0, state, self.getChiPengGangExtendInfo(cp.curSeatId))
                if gang:
                    actionInfo['gang_action'] = gang
                pigus = self.tableTileMgr.getPigus()
                if pigus:
                    actionInfo['fanpigu_action'] = pigus
            ftlog.debug("chiTileAfterActionInfo", actionInfo)

            # 判断锚/蛋牌
            if self.checkTableState(MTableState.TABLE_STATE_FANGMAO):
                maoInfo = {}
                if self.ifCalcFangDan(cp.curSeatId) and (not cp.isTing()):
                    isFirstAddtile = self.isFirstAddTile(cp.curSeatId)
                    maos = self.maoRuleMgr.hasMao(cp.copyHandTiles()
                                       , self.tableConfig.get(MTDefine.MAO_DAN_SETTING, MTDefine.MAO_DAN_NO)
                                       , cp.getMaoTypes(), isFirstAddtile
									   , {"maoType":cp.getPengMaoTypes()})
                    if len(maos) > 0:
                        maoInfo['mao_tiles'] = maos

                if not cp.isTing():
                    extendMaos = self.maoRuleMgr.hasExtendMao(cp.copyHandTiles(), cp.getMaoTypes())
                    if len(extendMaos) > 0:
                        maoInfo['mao_extends'] = extendMaos

                if ('mao_tiles' in maoInfo) or ('mao_extends' in maoInfo):
                    exInfo.appendInfo(MTableState.TABLE_STATE_FANGMAO, maoInfo)

            # 判断补花
            if self.checkTableState(MTableState.TABLE_STATE_BUFLOWER):
                cp = self.player[seatId]
                flowers = MFlowerRuleBase.hasFlower(cp.copyHandTiles())  # 手中剩余花牌
                if len(flowers) > 0:
                    if flowers[0] and self.tableTileMgr.isFlower(flowers[0]):
                        # 执行补花
                        cp.actionBuFlower(flowers[0])
                        self.tableTileMgr.setFlowerTileInfo(flowers[0], seatId)

                        # 累计花分
                        cp.addFlowerScores(1)
                        self.tableTileMgr.addFlowerScores(1, seatId)
                        self.msgProcessor.table_call_bu_flower_broadcast(seatId, flowers[0], cp.flowers,
                                                                         self.tableTileMgr.flowerScores(seatId))
                        self.processAddTileSimple(cp)

            # 吃完出牌，广播吃牌，如果吃听，通知用户出牌听牌
            for player in self.player:
                self.msgProcessor.table_call_after_chi(lastSeatId
                        , self.curSeat
                        , chiTile
                        , chiPattern
                        , timeOut
                        , self.actionID
                        , player
                        , actionInfo
                        , exInfo)

        self.changeMagicTileAfterChiPengExmao()

    def pengTile(self, seatId, tile, pengPattern, state):
        """碰别人的牌
        只有一个人，有可能是碰别人打出的牌，也有可能是抢锚碰
        """
        cp = self.players[seatId]
        exInfo = None
        checkPassDropPro = self.dropCardProcessor.updateProcessor(self.actionID, seatId, state, tile, pengPattern)
        ftlog.debug('MajiangTableLogic.pengTile, checkPassDropPro', checkPassDropPro)
        checkPassQiangExmaoPro = False
        if checkPassDropPro:
            exInfo = self.dropCardProcessor.getExtendResultBySeatId(seatId)
            self.dropCardProcessor.reset()
        else:
            checkPassQiangExmaoPro = self.qiangExmaoPengProcessor.updateProcessor(self.actionID, seatId, MTableState.TABLE_STATE_PENG, tile, pengPattern)
            ftlog.debug('MajiangTableLogic.pengTile, checkPassQiangExmaoPro', checkPassQiangExmaoPro)
            if checkPassQiangExmaoPro:
                exInfo = self.qiangExmaoPengProcessor.exmaoExtend
                cpExmao = self.player[self.qiangExmaoPengProcessor.curSeatId]
                cpExmao.actionDrop(tile)
                # 广播其出牌
                for seatIndex in range(self.playerCount):
                    message = self.msgProcessor.table_call_drop(self.curSeat
                        , self.player[seatIndex]
                        , tile
                        , MTableState.TABLE_STATE_NEXT
                        , {}
                        , self.actionID
                        , 0)
                    ftlog.debug('MajiangTableLogic.extendMao, table_call_drop: mmessage' , message)
                    self.msgProcessor.send_message(message, [self.player[seatIndex].userId])

        if self.playMode == MPlayMode.PANJIN:
            # 别人出牌检查过胡
            # pass后将漏胡的牌加入过胡牌数组,下次轮到自己回合时清空
            if self.winRuleMgr.isPassHu() and self.dropCardProcessor.getStateBySeatId(seatId) & MTableState.TABLE_STATE_HU:
                passHuTile = []
                cp = self.player[seatId]
                for testTile in xrange(1, 40):
                    allTile = cp.copyTiles()
                    allTile[MHand.TYPE_HAND].append(testTile)
                    winResult, _ = self.winRuleMgr.isHu(allTile, testTile, cp.isTing(), MWinRule.WIN_BY_OTHERS, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.winNodes, cp.curSeatId)
                    if winResult:
                        passHuTile.append(testTile)

                ftlog.debug("addPassHuTileByDrop peng", seatId, passHuTile)
                for tmpTile in passHuTile:
                    self.tableTileMgr.addPassHuBySeatId(seatId, tmpTile)

        if checkPassDropPro or checkPassQiangExmaoPro:
            lastSeatId = self.curSeat
            cp.actionAdd(tile)
            cp.actionPeng(tile, pengPattern, self.actionID, lastSeatId)

            self.setCurSeat(cp.curSeatId)
            self.incrActionId('pengTile')

            # 白城麻将如果碰牌是宝牌，算杠
            if self.playMode == MPlayMode.BAICHENG:
                magicTiles = self.tableTileMgr.getMagicTiles(True)
                if magicTiles[0] == tile:
                    result = self.initOneResult(MOneResult.RESULT_GANG, [], [], [], seatId, lastSeatId, -1, MPlayerTileGang.BaoZhong_MING_GANG)
                    result.calcScore()
                    if result.isResultOK():
                        self.roundResult.setPlayMode(self.playMode)
                        self.roundResult.setPlayerCount(self.playerCount)
                        self.roundResult.addRoundResult(result)
                    # 加上牌桌上局数总分
                    tableScore = [0 for _ in range(self.playerCount)]
                    if self.tableResult.score:
                        tableScore = self.tableResult.score
                    currentScore = [0 for _ in range(self.playerCount)]
                    allCoin = [0 for _ in range(self.playerCount)]
                    allTableCoin = [0 for _ in range(self.playerCount)]
                    for i in range(self.playerCount):
                        currentScore[i] = tableScore[i] + self.roundResult.score[i]

                    allCoin, allTableCoin = self.getCoinInfo()
                    self.msgProcessor.table_call_score(allCoin
                                    , allTableCoin
                                    , currentScore
                                    , self.roundResult.delta
                                    , False)

            timeOut = self.tableStater.getTimeOutByState(state)

            pengTingNotGrab = False
            if self.checkTableState(MTableState.TABLE_STATE_TING) and self.tingRule.canTingAfterPeng(cp.copyTiles()):
                _, tingArr = self.tingRule.canTing(cp.copyTiles(), self.tableTileMgr.tiles, tile, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.curSeatId)
                if len(tingArr) > 0:
                    exInfo.appendInfo(MTableState.TABLE_STATE_TING, tingArr)
                    pengTingNotGrab = True
                    ftlog.debug('MajiangTable.pengTile seatId:', cp.curSeatId, ' can ting with peng (not grab ting)')
                else:
                    cp.setWinNodes([])

            '''
            初始化处理器，抢听完了转听 
            addCardProcessor 初始化tile应为手牌最后一张
            碰的牌已经不在手中，托管会出问题
            '''
            if (state & MTableState.TABLE_STATE_GRABTING) or pengTingNotGrab:
                self.addCardProcessor.initProcessor(self.actionID, MTableState.TABLE_STATE_TING, cp.curSeatId, cp.copyHandTiles()[-1], exInfo, timeOut)
                self.addCardProcessor.setMustTing(state & MTableState.TABLE_STATE_GRABTING)
            else:
                self.addCardProcessor.initProcessor(self.actionID, MTableState.TABLE_STATE_DROP, cp.curSeatId, cp.copyHandTiles()[-1], exInfo, timeOut)

            actionInfo = {}
            ting_action = None
            if state & MTableState.TABLE_STATE_GRABTING:
                tingInfo = exInfo.extend['pengTing'][0]
                ftlog.debug('pengTile grabTing tingInfo:', tingInfo)
                ting_action = exInfo.getGrabTingAction(tingInfo, seatId, self.tableTileMgr, True)
                actionInfo['ting_action'] = ting_action
            # 吃碰完能补杠
            if self.tableTileMgr.canGangAfterPeng():
                gang = self.gangRuleMgr.hasGang(cp.copyTiles(), 0, state, self.getChiPengGangExtendInfo(cp.curSeatId))
                if gang:
                    actionInfo['gang_action'] = gang
                pigus = self.tableTileMgr.getPigus()
                if pigus:
                    actionInfo['fanpigu_action'] = pigus

            # 判断锚/蛋牌
            if self.checkTableState(MTableState.TABLE_STATE_FANGMAO):
                maoInfo = {}
                if self.ifCalcFangDan(cp.curSeatId) and (not cp.isTing()):
                    isFirstAddtile = self.isFirstAddTile(cp.curSeatId)
                    maos = self.maoRuleMgr.hasMao(cp.copyHandTiles()
                                       , self.tableConfig.get(MTDefine.MAO_DAN_SETTING, MTDefine.MAO_DAN_NO)
                                       , cp.getMaoTypes(), isFirstAddtile
									   , {"maoType":cp.getPengMaoTypes()})
                    if len(maos) > 0:
                        maoInfo['mao_tiles'] = maos

                if not cp.isTing():
                    extendMaos = self.maoRuleMgr.hasExtendMao(cp.copyHandTiles(), cp.getMaoTypes())
                    if len(extendMaos) > 0:
                        maoInfo['mao_extends'] = extendMaos

                if ('mao_tiles' in maoInfo) or ('mao_extends' in maoInfo):
                    exInfo.appendInfo(MTableState.TABLE_STATE_FANGMAO, maoInfo)

            # 判断补花
            if self.checkTableState(MTableState.TABLE_STATE_BUFLOWER):
                cp = self.player[seatId]
                flowers = MFlowerRuleBase.hasFlower(cp.copyHandTiles())  # 手中剩余花牌
                if len(flowers) > 0:
                    if flowers[0] and self.tableTileMgr.isFlower(flowers[0]):
                        # 执行补花
                        cp.actionBuFlower(flowers[0])
                        self.tableTileMgr.setFlowerTileInfo(flowers[0], seatId)

                        # 累计花分
                        cp.addFlowerScores(1)
                        self.tableTileMgr.addFlowerScores(1, seatId)
                        self.msgProcessor.table_call_bu_flower_broadcast(seatId
                                            , flowers[0]
                                            , cp.flowers
                                            , self.tableTileMgr.flowerScores(seatId))
                        self.processAddTileSimple(cp)

            # 山东济南 风刻算花分
            if self.playMode == MPlayMode.JINAN:
                if MTile.getColor(tile) >= 3:
                    cp.addFlowerScores(1)
                    self.tableTileMgr.addFlowerScores(1, seatId)
                    actionInfo['flower_score'] = self.tableTileMgr.flowerScores(seatId)

            # 非抢听情况下，部分玩法如果能碰后听牌，需要马上听牌
            if pengTingNotGrab:
                ting_action_not_grab = exInfo.getTingResult(self.player[seatId].copyTiles(), self.tableTileMgr, seatId, self.tilePatternChecker)
                if ting_action_not_grab:
                    tingliang_action = exInfo.getTingLiangResult(self.tableTileMgr)
                    if tingliang_action:
                        actionInfo['tingliang_action'] = tingliang_action
                    kou_ting_action = exInfo.getCanKouTingResult(self.tableTileMgr, seatId)
                    if kou_ting_action:
                        actionInfo['kou_ting_action'] = kou_ting_action
                    # 抢听把ting_action占用了，只能用ting_action_not_grab区分
                    actionInfo['ting_action_not_grab'] = ting_action_not_grab

            # 是否可以报警
            isCanAlarm = 0
            if self.getTableConfig(MTDefine.SWITCH_FOR_ALARM, 0):
                isCanAlarm = cp.canAlarm(cp.copyTiles(), tile)

            # 碰消息广播
            for player in self.player:
                self.msgProcessor.table_call_after_peng(lastSeatId
                        , self.curSeat
                        , tile
                        , timeOut
                        , self.actionID
                        , player
                        , pengPattern
                        , actionInfo
                        , exInfo)

                # 广播报警
                if isCanAlarm:
                    self.msgProcessor.table_call_alarm(seatId, player, isCanAlarm)

            self.changeMagicTileAfterChiPengExmao()

        if checkPassQiangExmaoPro:
            self.qiangExmaoPengProcessor.reset()
            
        if cp.isRobot():
            # 机器人碰牌后延迟1s出牌
            ftlog.debug('addPauseEvent by robot pengTile...')
            self.pauseProcessor.addPauseEvent(1)

    def zhanTile(self, seatId, tile, zhanPattern, state, special_tile):
        """粘别人的牌
        只有一个人，且只判断__drop_card_processor
        """
        cp = self.players[seatId]
        if self.dropCardProcessor.updateProcessor(self.actionID, seatId, state, tile, zhanPattern):
            exInfo = self.dropCardProcessor.getExtendResultBySeatId(seatId)
            self.dropCardProcessor.reset()
            # cp.actionAdd(tile) 加入之后actionZhan还是要移除
            cp.actionZhan(tile, zhanPattern, self.actionID)
            lastSeatId = self.curSeat
            self.setCurSeat(cp.curSeatId)
            self.incrActionId('zhanTile')

            timeOut = self.tableStater.getTimeOutByState(state)
            # 初始化处理器，抢听完了转听
            if state & MTableState.TABLE_STATE_GRABTING:
                self.addCardProcessor.initProcessor(self.actionID, MTableState.TABLE_STATE_TING, cp.curSeatId, tile, exInfo, timeOut)
                self.addCardProcessor.setMustTing(state & MTableState.TABLE_STATE_GRABTING)
            else:
                self.addCardProcessor.initProcessor(self.actionID, MTableState.TABLE_STATE_DROP, cp.curSeatId, tile, exInfo, timeOut)

            ftlog.debug('after zhanTile init addCardProcessor state:', state
                    , ' curSeatId:', cp.curSeatId
                    , ' exInfo.extend:', exInfo.extend)

            actionInfo = {}
            ting_action = None
            if state & MTableState.TABLE_STATE_GRABTING:
                tingInfo = exInfo.extend['zhanTing'][0]
                ftlog.debug('zhanTile grabTing tingInfo:', tingInfo)
                ting_action = exInfo.getGrabTingAction(tingInfo, seatId, self.tableTileMgr, True)
                actionInfo['ting_action'] = ting_action

            # 粘消息广播
            for player in self.player:
                self.msgProcessor.table_call_after_zhan(lastSeatId
                        , self.curSeat
                        , tile
                        , timeOut
                        , self.actionID
                        , player
                        , zhanPattern
                        , actionInfo)

        else:
            ftlog.debug('zhanTile error, need check....')

    def justGangThreeTile(self, lastSeatId, seatId, gangTile, gangPattern, style, state, afterAdd, special_tile=None, qiangGangSeats=[], tmpState=0):
        '''
        潜江晃晃，三张赖子皮当作一个杠
        以style=6和7为区别，杠完直接打牌，且可以听
        '''
        ftlog.debug('MTableLogic.justGangTile lastSeatId', lastSeatId
                    , ' seatId:', seatId
                    , ' gangTile:', gangTile
                    , ' gangPattern:', gangPattern
                    , ' style:', style
                    , ' state:', state)
        # 牌局手牌管理器记录杠的数量
        self.tableTileMgr.incGangCount()

        # 发送给客户端的结构
        gang = {}
        gang['tile'] = gangTile
        gang['pattern'] = gangPattern
        gang['style'] = style
        cp = self.player[seatId]
        # 潜江晃晃的朝天笑，确认杠
        if style == MPlayerTileGang.CHAOTIANXIAO_MING:
            cp.actionAdd(gangTile)
        ftlog.info("justGangTileChaoTian:", lastSeatId, seatId, gangTile, state, afterAdd)
        cp.actionChaoTian(gangPattern, gangTile, self.actionID, style, lastSeatId)
        
        # 设置本次杠牌seatId
        self.setLatestGangSeatId(seatId)
        self.winRuleMgr.setLastGangSeat(seatId)
        ftlog.debug("gangTilesetLatestGangState = ", seatId)
        self.incrActionId('gangThreeTile')
        state = MTableState.TABLE_STATE_DROP
        exInfo = MTableStateExtendInfo()
        # 判断是否能听
        tingResult, tingReArr = self.tingRule.canTing(cp.copyTiles(), self.tableTileMgr.tiles, gangTile, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.curSeatId)
        ftlog.debug('MajiangTableLogic.justGangThreeTile canTing result: ', tingResult, ' solution:', tingReArr, ' length: ', len(tingReArr))
        if tingResult and len(tingReArr) > 0:
            # 可以听牌
            state = state | MTableState.TABLE_STATE_TING
            exInfo.appendInfo(MTableState.TABLE_STATE_TING, tingReArr)
        if lastSeatId == seatId:
            tiles = cp.copyTiles()
            gangs = self.gangRuleMgr.hasGang(cp.copyTiles(), gangTile, MTableState.TABLE_STATE_NEXT, self.getChiPengGangExtendInfo(cp.curSeatId))
            canGang = True
            for tmpGang in gangs:
                if tmpGang["tile"] == self.tableTileMgr.laizi:
                    canGang = False
                if canGang and cp.canGang(gang, True, tiles, gangTile, self.winRuleMgr, self.tableTileMgr.getMagicTiles(cp.isTing()), self.tingRule):
                    state = state | MTableState.TABLE_STATE_GANG
                    exInfo.appendInfo(MTableState.TABLE_STATE_GANG, tmpGang)
        # 判断锚/蛋牌
        if self.checkTableState(MTableState.TABLE_STATE_FANGMAO):
            maoInfo = {}
            if self.ifCalcFangDan(cp.curSeatId) and (not cp.isTing()):
                isFirstAddtile = self.isFirstAddTile(cp.curSeatId)
                maos = self.maoRuleMgr.hasMao(cp.copyHandTiles()
                                   , self.tableConfig.get(MTDefine.MAO_DAN_SETTING, MTDefine.MAO_DAN_NO)
                                   , cp.getMaoTypes(), isFirstAddtile
								   , {"maoType":cp.getPengMaoTypes()})
                if len(maos) > 0:
                    maoInfo['mao_tiles'] = maos

            if not cp.isTing():
                extendMaos = self.maoRuleMgr.hasExtendMao(cp.copyHandTiles(), cp.getMaoTypes())
                if len(extendMaos) > 0:
                    maoInfo['mao_extends'] = extendMaos

            if ('mao_tiles' in maoInfo) or ('mao_extends' in maoInfo):
                exInfo.appendInfo(MTableState.TABLE_STATE_FANGMAO, maoInfo)

        # 判断补花
        if self.checkTableState(MTableState.TABLE_STATE_BUFLOWER):
            cp = self.player[seatId]
            flowers = MFlowerRuleBase.hasFlower(cp.copyHandTiles())  # 手中剩余花牌
            if len(flowers) > 0:
                if flowers[0] and self.tableTileMgr.isFlower(flowers[0]):
                    # 执行补花
                    cp.actionBuFlower(flowers[0])
                    self.tableTileMgr.setFlowerTileInfo(flowers[0], seatId)

                    # 累计花分
                    cp.addFlowerScores(1)
                    self.tableTileMgr.addFlowerScores(1, seatId)
                    self.msgProcessor.table_call_bu_flower_broadcast(seatId, flowers[0], cp.flowers,
                                                                     self.tableTileMgr.flowerScores(seatId))
                    self.processAddTileSimple(cp)

        timeOut = self.tableStater.getTimeOutByState(state)
        self.addCardProcessor.initProcessor(self.actionID, state, cp.curSeatId, gangTile, exInfo, timeOut)
        extendInfo = {
            'addInfo':exInfo
            }
        # 给所有人发送杠牌结果(只有结果 没有抢杠和信息)
        ftlog.debug('table_call_after_gang seatId = ', seatId, 'qiangGangSeats= ', qiangGangSeats)
        for player in self.player:
            if player.curSeatId not in qiangGangSeats:
                self.msgProcessor.table_call_after_gang(lastSeatId
                    , seatId
                    , gangTile
                    , [lastSeatId]
                    , self.actionID
                    , player
                    , gang  # 此时的杠是三张牌的朝天笑
                    , extendInfo)
        # 杠牌之后设置当前位置为杠牌人的位置
        self.setCurSeat(cp.curSeatId)

        # 记录杠牌得分
        gangBase = self.getTableConfig(MTDefine.GANG_BASE, 0)
        ftlog.debug('MajiangTableLogic.justGangTile gangBase: ', gangBase)

        if gangBase > 0:
            result = self.initOneResult(MOneResult.RESULT_GANG, [], [], [], self.curSeat, lastSeatId, self.actionID, -1, style)
            result.calcScore()

            if result.results.get(MOneResult.KEY_GANG_STYLE_SCORE, None):
                ftlog.debug('MajiangTableLogic.justGangTile add gang score to cp: ', result.results[MOneResult.KEY_GANG_STYLE_SCORE], ',actionID', self.actionID)
                cp.addGangScore(self.actionID, result.results[MOneResult.KEY_GANG_STYLE_SCORE])

            # 设置牌局过程中的明杠和暗杠番型信息
            if result.isResultOK():
                self.roundResult.setPlayMode(self.playMode)
                self.roundResult.setPlayerCount(self.playerCount)
                self.roundResult.addRoundResult(result)

                # 加上牌桌上局数总分
                tableScore = [0 for _ in range(self.playerCount)]
                if self.tableResult.score:
                    tableScore = self.tableResult.score
                currentScore = [0 for _ in range(self.playerCount)]
                allCoin, allTableCoin = self.getCoinInfo()
                for i in range(self.playerCount):
                    currentScore[i] = tableScore[i] + self.roundResult.score[i]

                self.msgProcessor.table_call_score(allCoin
                        , allTableCoin
                        , currentScore
                        , self.roundResult.delta
                        , False)

    def justGangTile(self, lastSeatId, seatId, gangTile, gangPattern, style, state, afterAdd, special_tile=None, qiangGangSeats=[]):
        '''
        不用检查抢杠和 直接杠牌 包含明杠和暗杠
        '''
        ftlog.info('MTableLogic.justGangTile lastSeatId', lastSeatId
                    , ' seatId:', seatId
                    , ' gangTile:', gangTile
                    , ' gangPattern:', gangPattern
                    , ' style:', style
                    , ' state:', state)
        # 牌局手牌管理器记录杠的数量
        self.tableTileMgr.incGangCount()

        # 发送给客户端的结构
        gang = {}
        gang['tile'] = gangTile
        gang['pattern'] = gangPattern
        gang['style'] = style
        cp = self.player[seatId]
        cp.curLianGangNum += 1  # 连杠次数+1
        if afterAdd:
            # 加入带赖子的补杠
            magicTiles = self.tableTileMgr.getMagicTiles()
            cp.actionGangByAddCard(gangTile, gangPattern, style, self.actionID, magicTiles, lastSeatId)
        # after drop
        else:
            # 明杠
            cp.actionAdd(gangTile)
            cp.actionGangByDropCard(gangTile, gangPattern, self.actionID, lastSeatId)

        # 是否可以报警
        isCanAlarm = 0
        if self.getTableConfig(MTDefine.SWITCH_FOR_ALARM, 0):
            isCanAlarm = cp.canAlarm(cp.copyTiles(), gangTile)

        # 设置本次杠牌状态
        self.setLatestGangSeatId(seatId)
        self.winRuleMgr.setLastGangSeat(seatId)
        ftlog.debug("gangTilesetLatestGangState = ", seatId)
        self.incrActionId('gangTile')

        # 山东济南 杠牌计算花分
        if self.playMode == MPlayMode.JINAN:
            if MTile.isFeng(gangPattern[0]) or MTile.isArrow(gangPattern[0]) :
                cp.addFlowerScores(1)
                self.tableTileMgr.addFlowerScores(1, seatId)

            if style == 0:
                cp.addFlowerScores(2)
                self.tableTileMgr.addFlowerScores(2, seatId)
            else:
                cp.addFlowerScores(1)
                self.tableTileMgr.addFlowerScores(1, seatId)
            gang['flower_score'] = self.tableTileMgr.flowerScores(seatId)


        # 杠牌之后设置当前位置为杠牌人的位置
        self.setCurSeat(cp.curSeatId)

        # 记录杠牌得分
        gangBase = self.getTableConfig(MTDefine.GANG_BASE, 0)
        ftlog.debug('MajiangTableLogic.justGangTile gangBase: ', gangBase)

        wins = [self.curSeat]
        looses = []
        observers = []
        if self.curSeat == lastSeatId:
            for player in self.players:
                if player.curSeatId != self.curSeat:
                    if player.isObserver():
                        continue
                    looses.append(player.curSeatId)
        else:
            looses.append(lastSeatId)

        for player in self.players:
            seat = player.curSeatId
            if (seat not in wins) and (seat not in looses):
                observers.append(seat)

        NoContinueAddTile = False
        detailChangeScores = None
        extendInfo = {}
        if gangBase > 0:
            result = self.initOneResult(MOneResult.RESULT_GANG, wins, looses, observers, self.curSeat, lastSeatId, self.actionID, gangTile, style)
            result.calcScore()
            scoreList, NoContinueAddTile = self.updateCoinWithOneResult([], [], result.results[MOneResult.KEY_SCORE])
            result.setCoinScore(scoreList)
            if NoContinueAddTile:
                self.chargeProcessor.setGangInfo({"tile":special_tile, "info":{"lastSeatId": lastSeatId, "seatId": seatId}})

            ftlog.debug('table_logic gang', result.results[MOneResult.KEY_SCORE])
            self.roundResult.getChangeScore(result.results)

            if result.results.get(MOneResult.KEY_GANG_STYLE_SCORE, None):
                ftlog.debug('MajiangTableLogic.justGangTile add gang score to cp: ', result.results[MOneResult.KEY_GANG_STYLE_SCORE], ',actionID', self.actionID)
                # 杠牌算分时，需要找到杠牌时的actionId，杠本身+1，所以此处-1
                cp.addGangScore(self.actionID - 1, result.results[MOneResult.KEY_GANG_STYLE_SCORE])

            if MOneResult.KEY_DETAIL_CHANGE_SCORES in result.results:
                detailChangeScores = result.results[MOneResult.KEY_DETAIL_CHANGE_SCORES]

            # 设置牌局过程中的明杠和暗杠番型信息
            if result.isResultOK():
                self.roundResult.setPlayMode(self.playMode)
                self.roundResult.setPlayerCount(self.playerCount)
                self.roundResult.addRoundResult(result)
                # 加上牌桌上局数总分
                tableScore = [0 for _ in range(self.playerCount)]
                if self.tableResult.score:
                    tableScore = self.tableResult.score
                currentScore = [0 for _ in range(self.playerCount)]
                allCoin, allTableCoin = self.getCoinInfo()
                for i in range(self.playerCount):
                    currentScore[i] = tableScore[i] + self.roundResult.score[i]
                self.msgProcessor.table_call_score(allCoin
                                                   , allTableCoin
                                                   , currentScore
                                                   , self.roundResult.delta
                                                   , False)
                # 发送对局流水信息
                self.sendTurnoverResult()

        if detailChangeScores:
            extendInfo['detailChangeScores'] = detailChangeScores
        ftlog.debug('table_call_after_gang seatId = ', seatId, 'qiangGangSeats= ', qiangGangSeats)
        for player in self.player:
            if player.curSeatId not in qiangGangSeats:
                self.msgProcessor.table_call_after_gang(lastSeatId
                    , seatId
                    , gangTile
                    , [lastSeatId]
                    , self.actionID
                    , player
                    , gang
                    , extendInfo)

            # 广播报警
            if isCanAlarm:
                self.msgProcessor.table_call_alarm(seatId, player, isCanAlarm)

        # 更新听牌预览的结果
        self.updateTingResult(gangTile, True)
        # 杠完上牌，应该先算杠分，后上牌。因为上牌后可能再杠或者和了，这样算分就乱了
        if not NoContinueAddTile:
            # 延时杠补，给前端展示杠牌动画的时间
            self.pauseProcessor.addPauseEvent(2, 'justGangTile', {"seatId": seatId, "lastSeatId": lastSeatId, "tile": special_tile})

    def processDelayGangTile(self, data):
        '''
        杠牌后的延时杠补
        '''
        tile = data['tile']
        seatId = data['seatId']
        lastSeatId = data['lastSeatId']
        cp = self.player[seatId]
        self.processAddTile(cp, tile, {"lastSeatId": lastSeatId, "seatId": seatId})

    def gangTile(self, seatId, tile, gangPattern, style, state, special_tile=None):
        """
        杠别人的牌，只有一个人
        """
        ftlog.debug('MajiangTableLogic.gangTile seatId:', seatId
                    , ' tile:', tile
                    , ' gangPattern:', gangPattern
                    , ' style:', style
                    , ' self.addCardProcessor.getState:', self.addCardProcessor.getState()
                    , ' self.qiangGangHuProcessor.getState:', self.qiangGangHuProcessor.getState())
        lastSeatId = self.curSeat
        # 发送给客户端的结构
        gang = {}
        gang['tile'] = tile
        gang['pattern'] = gangPattern
        gang['style'] = style

        if self.addCardProcessor.getState() != 0:
            if not self.addCardProcessor.updateProcessor(self.actionID, MTableState.TABLE_STATE_GANG, seatId):
                return

            # 如果是明杠，判断其他玩家是否可以抢杠和
            # 如果没有玩家抢杠和，给当前玩家发牌
            # 如果有玩家抢杠和，等待改玩家的抢杠和结果
            # 检测抢杠和
            qiangGangWin = False
            winSeats = [-1 for _ in range(self.playerCount)]
            canQiangGang = False
            if style == MPlayerTileGang.MING_GANG:
                canQiangGang = True
            else:
                if self.playMode == MPlayMode.JIXI:
                    canQiangGang = True

            # 只能自摸胡时，不允许抢杠
            if self.tableConfig.get(MTDefine.WIN_BY_ZIMO, MTDefine.WIN_BY_ZIMO_NO) == MTDefine.WIN_BY_ZIMO_OK:
                canQiangGang = False

            ftlog.debug('MajiangTableLogic.gangTile after gang, canQiangGang===:', canQiangGang
                        , ' check state MTableState.TABLE_STATE_QIANGGANG:', self.checkTableState(MTableState.TABLE_STATE_QIANGGANG)
                        , ' check state MTableState.TABLE_STATE_HU:', self.checkTableState(MTableState.TABLE_STATE_HU))

            if canQiangGang and self.checkTableState(MTableState.TABLE_STATE_QIANGGANG) and self.checkTableState(MTableState.TABLE_STATE_HU):
                rulePass = False
                rule = self.tableTileMgr.qiangGangRule
                if lastSeatId == seatId:
                    # 自己出牌自己杠
                    # 暗杠0x001
                    # 补杠0x010
                    if style == MPlayerTileGang.AN_GANG and rule & MTableTile.QIANG_GANG_RULE_AN:
                            rulePass = True
                    elif style == MPlayerTileGang.MING_GANG and rule & MTableTile.QIANG_GANG_RULE_HUI_TOU:
                            rulePass = True
                else:
                    if style == MPlayerTileGang.MING_GANG and rule & MTableTile.QIANG_GANG_RULE_OTHER:
                    # 杠别人的牌0x100
                        rulePass = True

                for index in range(1, self.playerCount):
                    newSeatId = (seatId + index) % self.playerCount
                    # 判断是否抢杠和牌
                    player = self.player[newSeatId]
                    magics = self.tableTileMgr.getMagicTiles(player.isTing())
                    # 红中宝不能抢杠胡
                    checkTile = gangPattern[-1]
                    pTiles = player.copyTiles()
                    pTiles[MHand.TYPE_HAND].append(checkTile)
                    winResult, winPattern = self.winRuleMgr.isHu(pTiles, gangPattern[-1], player.isTing(), MWinRule.WIN_BY_QIANGGANGHU, magics, player.winNodes, player.curSeatId)
                    ftlog.debug('MajiangTable.gangTile after gang, check qiangGangHu winResult:', winResult
                                 , ' winPattern:', winPattern)

                    if winResult and rulePass:
                        # 可以和，给用户和的选择
                        state = MTableState.TABLE_STATE_QIANGGANG
                        winInfo = {}
                        # 前端需求 tile需发杠的牌
                        winInfo['tile'] = gangPattern[-1]
                        winInfo['qiangGang'] = 1
                        winInfo['gangSeatId'] = self.curSeat
                        exInfo = MTableStateExtendInfo()
                        exInfo.appendInfo(state, winInfo)
                        ftlog.debug('MajiangTableLogic.gangTile after gang, qiangGangHu extendInfo:', exInfo)
                        timeOut = self.tableStater.getTimeOutByState(state)
                        qiangGangWin = True
                        winSeats[player.curSeatId] = player.curSeatId

                        self.incrActionId('qiangGangHu')
                        self.qiangGangHuProcessor.initProcessor(self.actionID
                                , player.curSeatId
                                , state
                                , exInfo
                                , timeOut)

            if qiangGangWin:
                # 清空杠玩家最近的消息，防止玩家短线重连后，再给玩家发杠的消息
                self.msgProcessor.latestMsg[lastSeatId] = None

                self.qiangGangHuProcessor.initTile(gangPattern[-1], self.curSeat, state, gangPattern, style, special_tile)
                # 给自己发送杠牌结果
                for player in self.player:
                    if player.curSeatId in winSeats:
                        self.msgProcessor.table_call_grab_gang_hu(lastSeatId
                                                                  , player.curSeatId
                                                                  , self.actionID
                                                                  , player
                                                                  , gang
                                                                  , self.qiangGangHuProcessor.getExtendResultBySeatId(player.curSeatId))
                # 如果抢杠胡,需要给客户端发送屁股牌消息,让客户端关闭界面
                if self.checkTableState(MTableState.TABLE_STATE_FANPIGU):
                    pigus = self.tableTileMgr.getPigus()
                    self.msgProcessor.table_call_fanpigu(pigus)
                return

            elif style in [MPlayerTileGang.CHAOTIANXIAO_MING, MPlayerTileGang.CHAOTIANXIAO_AN]:
                self.justGangThreeTile(lastSeatId, seatId, tile, gangPattern, style, state, True, special_tile)
            else:
                # 直接杠牌
                self.justGangTile(lastSeatId, seatId, tile, gangPattern, style, state, True, special_tile)

        elif self.dropCardProcessor.getState() != 0:
            if self.dropCardProcessor.updateProcessor(self.actionID, seatId, state, tile, gang):
                self.dropCardProcessor.reset()
                if style in [MPlayerTileGang.CHAOTIANXIAO_MING, MPlayerTileGang.CHAOTIANXIAO_AN]:
                    self.justGangThreeTile(lastSeatId, seatId, tile, gangPattern, style, state, False, special_tile)
                else:
                    # 直接杠牌
                    self.justGangTile(lastSeatId, seatId, tile, gangPattern, style, state, False, special_tile)
        elif self.qiangExmaoPengProcessor.getState() != 0:
            checkPassQiangExmaoPro = self.qiangExmaoPengProcessor.updateProcessor(self.actionID, seatId, MTableState.TABLE_STATE_GANG, tile, gangPattern)
            if checkPassQiangExmaoPro:
                cpExmao = self.player[self.qiangExmaoPengProcessor.curSeatId]
                cpExmao.actionDrop(tile)
                # 广播其出牌
                for seatIndex in range(self.playerCount):
                    # 已经向exmaoSeatId广播过出牌了
                    if seatIndex == self.qiangExmaoPengProcessor.exmaoSeatId:
                        continue

                    message = self.msgProcessor.table_call_drop(self.curSeat
                        , self.player[seatIndex]
                        , tile
                        , MTableState.TABLE_STATE_NEXT
                        , {}
                        , self.actionID
                        , 0)
                    ftlog.debug('MajiangTableLogic.extendMao, table_call_drop: mmessage' , message)
                    self.msgProcessor.send_message(message, [self.player[seatIndex].userId])
                self.qiangExmaoPengProcessor.reset()
                # 直接杠牌
                self.justGangTile(lastSeatId, seatId, tile, gangPattern, style, state, False, special_tile)

    def addZFBGang(self, winSeatId):
        result = MOneResultFactory.getOneResult(self.playMode)
        result.setResultType(MOneResult.RESULT_GANG)
        result.setStyle(MPlayerTileGang.ZFB_GANG)
        result.setLastSeatId(winSeatId)
        result.setWinSeatId(winSeatId)
        result.setPlayerCount(self.playerCount)
        result.setTableConfig(self.tableConfig)
        result.setTableType(self.tableType)
        result.calcScore()
        if result.isResultOK():
            self.roundResult.setPlayMode(self.playMode)
            self.roundResult.setPlayerCount(self.playerCount)
            self.roundResult.addRoundResult(result)

    def ConsumServiceFeeDaHu(self, wins, theoryScore, realScore, bigFees):
        '''
        收取大胡服务费
        :param adjustChip:默认值-1,不收取服务费
        '''
        if self.tableType != MTDefine.TABLE_TYPE_NORMAL:
            return False

        serviceFeeRate = self.tableConfig.get(MTDefine.SERVICE_FEE_DAHU_RATE, 0)
        serviceFeeOn = self.tableConfig.get(MTDefine.SERVICE_FEE_DAHU_ON, 0.5)
        serviceFeeFan = self.tableConfig.get(MTDefine.SERVICE_FEE_DAHU_FAN, 16)
        ftlog.debug('MajiangTableLogic.ConsumServiceFeeDaHu rate:', serviceFeeRate
                    , ' serviceFeeOn:', serviceFeeOn
                    , ' serviceFeeFan:', serviceFeeFan)
        for win in wins:
            baseChip = self.tableConfig.get(MTDefine.BASE_CHIP, 1)
            if (theoryScore[win] / baseChip >= serviceFeeFan) \
                and (theoryScore[win] * serviceFeeOn < realScore[win]):
                bigFee = int(realScore[win] * serviceFeeRate)
                if TYPlayer.isHuman(self.player[win].userId):
                    chip = hallrpcutil.getTableChip(self.player[win].userId, self.gameId, self.tableId)
                    ftlog.debug('MajiangTableLogic.ConsumeServiceFeeDaHu insufficient chip:', chip
                                , 'bigFee:', bigFee)
                    if chip < bigFee:
                        bigFee = chip
                    if bigFee <= 0:
                        continue
                    clientId = Majiang2Util.getClientId(self.player[win].userId)
                    trueDelta, finalcount = hallrpcutil.incrTableChip(self.player[win].userId
                            , self.gameId
                            , -bigFee
                            , 0
                            , 'BIG_WIN_FEE'
                            , self.roomId
                            , clientId
                            , self.tableId
                    )
                    self.player[win].setTableCoin(finalcount)
                    ftlog.debug('MajiangTableLogic.ConsumeServiceFeeDaHu player.userId:', self.player[win].userId
                                    , ' bigFee:', bigFee, ' chip:', chip)
    
                    if trueDelta != -bigFee:  # 失败
                        ftlog.warn('coin not enougth: ', bigFee)
                        return False
                    tybireport.tableRoomFee(self.gameId, bigFee)
                    bigFees[win] = trueDelta
                else:
                    # 机器人也收取大胡服务费
                    tableCoin = self.player[win].getTableCoin(self.gameId, self.tableId)
                    if tableCoin < bigFee:
                        bigFee = tableCoin
                    if bigFee <= 0:
                        continue
                    self.player[win].setTableCoin(tableCoin - bigFee)
                    bigFees[win] = -bigFee
                ftlog.info('Majiang2.logAnalyse userId:', self.player[win].userId
                                , 'tableCoin:', self.player[win].getTableCoin(self.gameId, self.tableId)
                                , 'WinFee:', -bigFees[win]
                                , 'tableId:', self.tableId
                                , 'WinFee')
                    
    def ConsumeServiceFee(self, seatIds, serviceScore):
        """
        扣除金币赛服务费，在扣除输赢金币之前扣除
        只针对输赢玩家收取服务费
        服务费1:普通结算
             2:大胡结算
        :param seatIds:扣除服务费的seatId集合
        :param serviceScore:扣除的服务费
        """
        if self.tableType != MTDefine.TABLE_TYPE_NORMAL or not seatIds:
            return False
        
        servicefee = self.tableConfig.get(MTDefine.SERVICE_FEE, 10)
        ftlog.debug('MajiangTableLogic.ConsumeServiceFee servicefee:', servicefee, 'seatIds:', seatIds)

        # 普通结算收取服务费
        for player in self.player:
            if not player or player.curSeatId not in seatIds:
                continue

            tempServiceFee = servicefee
            if TYPlayer.isHuman(player.userId):
                clientId = Majiang2Util.getClientId(player.userId)
                chip = hallrpcutil.getTableChip(player.userId, self.gameId, self.tableId)
                if chip < tempServiceFee:
                    if self.roomConfig.get('level', MTDefine.FREE) == MTDefine.FREE:
                        # 系统赔付，给改用户补齐服务费
                        hallrpcutil.incrTableChip(player.userId
                            , self.gameId
                            , (tempServiceFee - chip)
                            , 0
                            , 'MAJIANG_ROOM_PAID'
                            , self.roomId
                            , clientId
                            , self.tableId
                        )
                        ftlog.info('Majiang2.logAnalyse userId:', player.userId, 'tableCoin:', chip, 'PaidChip:', tempServiceFee - chip, 'tableId:', self.tableId, 'RoomPaid')
                    else:
                        ftlog.debug('MajiangTableLogic.ConsumeServiceFee insufficient chip:', chip, 'serviceFee', servicefee)
                        tempServiceFee = chip

                trueDelta, finalcount = hallrpcutil.incrTableChip(player.userId
                        , self.gameId
                        , -tempServiceFee
                        , 0
                        , 'ROOM_GAME_FEE'
                        , self.roomId
                        , clientId
                        , self.tableId
                )
                ftlog.info('Majiang2.logAnalyse userId:', player.userId, 'tableCoin:', chip, 'GameFee:', tempServiceFee, 'tableId:', self.tableId, 'GameFee')
                player.setTableCoin(finalcount)
                ftlog.debug('MajiangTableLogic.ConsumeServiceFee player.userId:', player.userId
                            , ' servicefee:', servicefee
                            , ' chipBefore:', chip
                            , ' chipAfter:', finalcount
                            , ' deltaChip:', trueDelta)

                if trueDelta != -tempServiceFee:  # 失败
                    ftlog.warn('coin not enougth: ', tempServiceFee)
                    return False
                tybireport.tableRoomFee(self.gameId, tempServiceFee)
                serviceScore[player.curSeatId] = trueDelta
            else:
                # 机器人也收取服务费
                tableCoin = player.getTableCoin(self.gameId, self.tableId)
                if servicefee > tableCoin:
                    tempServiceFee = tableCoin
                else:
                    tempServiceFee = servicefee
                ftlog.info('Majiang2.logAnalyse userId:', player.userId, 'tableCoin:', tableCoin, 'GameFee:', tempServiceFee, 'tableId:', self.tableId, 'GameFee')
                ftlog.debug('MajiangTableLogic.ConsumeServiceFee tableCoin:', tableCoin)
                player.setTableCoin(tableCoin - tempServiceFee)
                serviceScore[player.curSeatId] -= tempServiceFee

    def calcGangInHand(self, winSeatId, lastSeatId, winTile, winNodes):
        alltiles = [[] for _ in range(self.playerCount)]
        for index in range(self.playerCount):
            alltiles[index] = self.player[index].copyTiles()
        if self.playMode == MPlayMode.BAICHENG:
            for seatId in range(self.playerCount):
                ftlog.debug('MajiangTableLogic.calcGangInHand seatId:', seatId, 'self.playerCount', self.playerCount)
                handTile = copy.deepcopy(alltiles[seatId][MHand.TYPE_HAND])
                if seatId == winSeatId:
                    handTile.append(winTile)
                    # 赢家中发白算明杠
                    magicTiles = self.tableTileMgr.getMagicTiles()
                    magicTile = magicTiles[0]
                    if winSeatId == lastSeatId and winTile == magicTile:
                        # 自摸并且摸宝,判断是否有中发白杠。其他情况都是看手中牌
                        hasZFB = False
                        for wn in winNodes:
                            if not hasZFB:
                                patterns = wn['pattern']
                                for p in patterns:
                                    if p == [35, 36, 37]:
                                        result = MOneResultFactory.getOneResult(self.playMode)
                                        result.setResultType(MOneResult.RESULT_GANG)
                                        result.setStyle(MPlayerTileGang.ZFB_GANG)
                                        result.setLastSeatId(seatId)
                                        if winTile in p:
                                            result.setLastSeatId(lastSeatId)
                                        result.setWinSeatId(seatId)
                                        result.setPlayerCount(self.playerCount)
                                        result.setTableConfig(self.tableConfig)
                                        result.setTableType(self.tableType)
                                        result.calcScore()
                                        if result.isResultOK():
                                            self.roundResult.setPlayMode(self.playMode)
                                            self.roundResult.setPlayerCount(self.playerCount)
                                            self.roundResult.addRoundResult(result)
                                        hasZFB = True
                                        break
                    else:
                        if (35 in handTile) and (36 in handTile) and (37 in handTile):
                            result = MOneResultFactory.getOneResult(self.playMode)
                            result.setResultType(MOneResult.RESULT_GANG)
                            result.setStyle(MPlayerTileGang.ZFB_GANG)
                            result.setLastSeatId(seatId)
                            result.setWinSeatId(seatId)
                            result.setPlayerCount(self.playerCount)
                            result.setTableConfig(self.tableConfig)
                            result.setTableType(self.tableType)
                            result.calcScore()
                            # 设置牌局过程中的放锚番型信息
                            if result.isResultOK():
                                self.roundResult.setPlayMode(self.playMode)
                                self.roundResult.setPlayerCount(self.playerCount)
                                self.roundResult.addRoundResult(result)

                else:
                    if (35 in handTile) and (36 in handTile) and (37 in handTile):
                        result = MOneResultFactory.getOneResult(self.playMode)
                        result.setResultType(MOneResult.RESULT_GANG)
                        result.setStyle(MPlayerTileGang.ZFB_GANG)
                        result.setLastSeatId(seatId)
                        result.setWinSeatId(seatId)
                        result.setPlayerCount(self.playerCount)
                        result.setTableConfig(self.tableConfig)
                        result.setTableType(self.tableType)
                        result.calcScore()
                        # 设置牌局过程中的放锚番型信息
                        if result.isResultOK():
                            self.roundResult.setPlayMode(self.playMode)
                            self.roundResult.setPlayerCount(self.playerCount)
                            self.roundResult.addRoundResult(result)

                ftlog.debug('MajiangTableLogic.calcGangInHand handTile:', handTile)


                # 手里三张和宝牌一样算暗杠
                if seatId == winSeatId and winSeatId != lastSeatId:
                    handTile.remove(winTile)

                handtileArr = MTile.changeTilesToValueArr(handTile)
                magicTiles = self.tableTileMgr.getMagicTiles(True)
                magictile = 0
                if len(magicTiles) > 0:
                    magictile = magicTiles[0]

                if handtileArr[magictile] == 3:
                    result = MOneResultFactory.getOneResult(self.playMode)
                    result.setResultType(MOneResult.RESULT_GANG)
                    result.setStyle(MPlayerTileGang.BaoZhong_AN_GANG)
                    result.setLastSeatId(seatId)
                    result.setWinSeatId(seatId)
                    result.setPlayerCount(self.playerCount)
                    result.setTableConfig(self.tableConfig)
                    result.setTableType(self.tableType)
                    result.calcScore()
                    # 设置牌局过程中的放锚番型信息
                    if result.isResultOK():
                        self.roundResult.setPlayMode(self.playMode)
                        self.roundResult.setPlayerCount(self.playerCount)
                        self.roundResult.addRoundResult(result)


    def CalcCoinResult(self, coinScore, seats=None):
        '''
        金币赛扣除
        由于金币桌金币结算需要根据玩家的自身金币数量有关，所以金币桌的score数组形式与自建桌不一样。
        1、输家最多输带进桌子的金币 赢家赢的金币不得超过带入桌子的金币
        2、若输家总共的金币不够赢家总共赢的金币，则赢家共赢输家所有的金币，按照比例分配
        3、金币的调整在OneResult调整过了，在这里要去掉扣除服务费所带来的影响
        '''
        if self.tableType != MTDefine.TABLE_TYPE_NORMAL:
            return

        ftlog.debug('MajiangTableLogic.before CalcCoinResult coinScore:', coinScore)

        # 调整扣除服务费所带来的影响
        for i in range(self.playerCount):
            if seats and i not in seats:
                continue
            coinVal = coinScore[i]
            chipTable = self.player[i].getTableCoin(self.gameId, self.tableId)
            ftlog.debug('MajiangTableLogic calcCoinResult seatId:', i, 'coinVal:', coinVal, 'tableCoin:', chipTable)
            if coinVal < 0 and abs(coinVal) > chipTable:
                coinScore[i] = -chipTable
        ftlog.debug('MajiangTableLogic calcCoinResult coinScore:', coinScore)
        needCharge = False

        for i in range(self.playerCount):
            if seats and (i not in seats):
                continue

            coinChange = coinScore[i]
            # 金币变化为0 就不进行下面的操作
            if coinChange == 0:
                continue

            if TYPlayer.isHuman(self.player[i].userId):
                chip = hallrpcutil.getTableChip(self.player[i].userId, self.gameId, self.tableId)
                clientId = Majiang2Util.getClientId(self.player[i].userId)
                trueDelta, finalChip = hallrpcutil.incrTableChip(
                        self.player[i].userId
                        , self.gameId
                        , coinChange
                        , 0
                        , 'GAME_WINLOSE'
                        , self.roomId
                        , clientId
                        , self.tableId
                )
                
                self.player[i].setTableCoin(finalChip)
                ftlog.debug('MajiangTableLogic.CalcCoinResult player.userId:', self.player[i].userId
                                , ' coinChange:', coinChange
                                , ' chipBefore:', chip
                                , ' chipAfter:', self.player[i].getTableCoin(self.gameId, self.tableId))

                if trueDelta != coinChange:  # 失败
                    # 这种情况不该发生，如果发生，一定有问题
                    ftlog.error('MajiangTableLogic.wrong coin trueDelta != coinChange: ', coinChange)
                    continue
                
                tybireport.gcoin('out.interactive_expression', self.gameId, coinChange)
                coinScore[i] = trueDelta
            else:
                # 机器人也要计算金币变化
                self.player[i].setTableCoin(self.player[i].getTableCoin(self.gameId, self.tableId) + coinChange)
            ftlog.info('Majiang2.logAnalyse userId:', self.player[i].userId
                            , 'tableCoin:', self.player[i].getTableCoin(self.gameId, self.tableId)
                            , 'GameWinLose:', coinChange
                            , 'tableId:', self.tableId
                            , 'GameWinLose')
            
            """
            如果此人牌桌金币为0，且牌局未结束，提示此人充值，同时向其他人广播此人的充值消息
            充值的逻辑
            1）优先补充牌桌外金币，带入[minCoin, uChip/buyin]的最大值。
            2）如果uChip低于minCoin，弹转运礼包。游戏UT监听购买成功消息，如果当前用户在该游戏中，则想牌桌发送table_manage消息，充值金币继续游戏。
            3）超时内玩不成金币补充或者玩家不购买金币，则玩家认输。
            4）玩家已经成为观察者，则不需充值
            """
            if (self.player[i].getTableCoin(self.gameId, self.tableId) < self.tableConfig.get(MTDefine.BASE_CHIP, 0)) \
                and (not self.player[i].isObserver()) \
                and (self.roomConfig.get('level', MTDefine.FREE) != MTDefine.FREE) \
                and (coinScore[i] <= 0):
                self.chargeProcessor.addUser(i)
                needCharge = True

        if needCharge and (not self.isThisRoundOver()):
            self.incrActionId('charge')
            ftlog.debug('MajiangTableLogic chargeProcess actionId:', self.actionID)
            self.chargeProcessor.setPlayers(self.player)
            self.chargeProcessor.initProcessor(self.actionID, self.roomConfig.get(MTDefine.CHARGE_TIMEOUT, 20), self.pauseProcessor)
            return True
        
        return False

    def initOneResult(self, typeResult=-1, wins=[], looses=[], observers=[], winSeatId=-1, lastSeatId=-1, actionId=-1, winTile=-1, style=-1, exInfo={}):
        '''
        初始化one Result模块 需要设置的太多比较乱，放在一起
        一致属性：playMode players tableConfig banker playerCount playerAllTiles playerGangTiles tableType tableTileMgr
        需要设属性：type, wins, looses, observers, self.curSeat, exInfo
        '''
        result = MOneResultFactory.getOneResult(self.playMode, self.tilePatternChecker, self.playerCount)
        result.setPlayMode(self.playMode)
        result.setPlayers(self.players)
        result.setTableConfig(self.tableConfig)
        result.setBankerSeatId(self.queryBanker())
        result.setTableType(self.tableType)
        result.setPiaoProcessor(self.piaoProcessor)
        result.setDoublePoints(self.doubleProcessor.doublePoints)
        result.setTableTileMgr(self.tableTileMgr)
        result.setWinRuleMgr(self.winRuleMgr)
        result.setMultiple(self.winRuleMgr.multiple)
        result.setRoundIndex(self.scheduleMgr.curCount)
        # 设置上一个杠的seatId，杠上炮、杠上花
        result.setLatestGangSeatId(self.latestGangSeatId)
        # 设置手牌
        tingState = [0 for _ in range(self.playerCount)]
        colorState = [0 for _ in range(self.playerCount)]
        menState = [0 for _ in range(self.playerCount)]
        ziState = [[0, 0, 0, 0, 0, 0, 0] for _ in range(self.playerCount)]
        playerAllTiles = [0 for _ in range(self.playerCount)]
        playerGangTiles = [0 for _ in range(self.playerCount)]
        playerScore = [0 for _ in range(self.playerCount)]
        for player in self.player:
            # 听牌状态
            if not player:
                continue

            if player.isTing():
                tingState[player.curSeatId] = 1
            # 花色状态    
            pTiles = player.copyTiles()
            tileArr = MTile.changeTilesToValueArr(MHand.copyAllTilesToList(pTiles))
            colorState[player.curSeatId] = MTile.getColorCount(tileArr)
            # 字
            tempTiles = MTile.traverseTile(MTile.TILE_FENG)
            ziState[player.curSeatId] = tileArr[tempTiles[0]:tempTiles[len(tempTiles) - 1] + 1]
            # 玩家牌的情况
            playerAllTiles[player.curSeatId] = player.copyTiles()
            playerGangTiles[player.curSeatId] = player.copyGangArray()
            # 门清状态
            handTiles = player.copyHandTiles()
            gangTiles = player.copyGangArray()
            _, an = MTile.calcGangCount(gangTiles)
            if len(handTiles) == self.handCardCount - an * 3:
                menState[player.curSeatId] = 1
        result.setColorState(colorState)
        result.setZiState(ziState)
        result.setPlayerAllTiles(playerAllTiles)
        result.setPlayerGangTiles(playerGangTiles)
        result.setMenState(menState)
        result.setTingState(tingState)
        result.setPlayerCurScore(playerScore)
        result.setWinSeats(wins)
        result.setLooseSeats(looses)
        result.setObserverSeats(observers)
        
        if typeResult != -1:
            result.setResultType(typeResult)
        if winSeatId != -1:
            result.setWinSeatId(winSeatId)
        if lastSeatId != -1:  
            result.setLastSeatId(lastSeatId)
        if actionId != -1:
            result.setActionID(actionId)
        if style != -1:
            result.setStyle(style)
        if winTile != -1:
            result.setWinTile(winTile)
            
        return result

    def gameWin(self, seatId, tile, grabHuGang=False):
        """
        胡牌
        1）出牌时 可以有多个人和牌
        2）摸牌时，只有摸牌的人和牌
        """
        lastSeatId = self.curSeat
        cp = self.player[seatId]
        
        ftlog.info('MajiangTableLogic.gameWin seatId:', seatId
                     , ' lastSeatId:', lastSeatId
                     , ' tile:', tile
                     , ' grabHuGang:', grabHuGang)
        
        # 听牌状态->结算用
        tingState = [0 for _ in range(self.playerCount)]
        for player in self.player:
            if player and player.isTing():
                tingState[player.curSeatId] = 1
        ftlog.debug('MajiangTableLogic.gameWin tingState:', tingState)
        wins = [seatId]
        looses = []
        observers = []
        daFeng = False
        baoZhongBao = False
        huaCi = False
        magicAfertTing = False
        tianHu = False
        wuDuiHu = False
        winNode = None

        if grabHuGang and self.qiangGangHuProcessor.getState() != 0:
            self.qiangGangHuProcessor.updateProcessor(self.actionID, seatId, MTableState.TABLE_STATE_QIANGGANG, tile, None)
            wins = self.qiangGangHuProcessor.getAllCanWins()
            if self.qiangGangHuProcessor.updateDuoHu(self.actionID, wins, MTableState.TABLE_STATE_QIANGGANG):
                # 不用客户端传过来的这张牌
                tile = self.qiangGangHuProcessor.tile
                self.qiangGangHuProcessor.reset()
                # 从被抢杠者手牌里去掉这张牌
                if self.tableConfig.get(MTDefine.REMOVE_GRABBED_GANG_TILE, 1):
                    self.players[lastSeatId].actionGrabGangHu(tile)
                looses = [lastSeatId]
                for winSeat in wins:
                    winPlayer = self.player[winSeat]
                    winPlayer.actionHuFromOthers(tile, self.curSeat)
                
                for player in self.players:
                    ftlog.debug('MajiangTableLogic.gameWin player name:', player.name
                                    , 'handTile:', player.copyHandTiles()
                                    , 'userId:', player.userId)
                
                # 抢杠胡成功以后，需要广播一下，前端好刷新手牌
                for index in range(self.playerCount):
                    self.msgProcessor.table_call_notify_grab_gang(lastSeatId, self.actionID, self.players[index], tile)
            else:
                return
        elif self.addCardProcessor.getState() != 0:
            ftlog.debug('MajiangTableLogic.gameWin process by addCardProcessor...')
            exInfo = self.addCardProcessor.extendInfo
            winNode = exInfo.getWinNodeByTile(tile)
            if winNode and ('baoZhongBao' in winNode) and winNode['baoZhongBao']:
                baoZhongBao = True 
            if winNode and ('huaCi' in winNode) and winNode['huaCi']:
                huaCi = True
            ftlog.debug('table_logic gameWin winNode:', winNode)
              
            self.addCardProcessor.updateProcessor(self.actionID, MTableState.TABLE_STATE_HU, seatId)
            cp.actionHuByMyself(tile, not (baoZhongBao))
            # 自摸，一个人和，其他人都输
            for player in self.player:
                if player.curSeatId != seatId:
                    if player.isObserver():
                        continue
                    looses.append(player.curSeatId)
        elif self.dropCardProcessor.getState() != 0:
            ftlog.debug('MajiangTableLogic.gameWin process by dropCardProcessor...')
            winState = MTableState.TABLE_STATE_HU
            self.dropCardProcessor.updateProcessor(self.actionID, seatId, winState, tile, None)
            wins = self.dropCardProcessor.getAllCanWins()
            if self.dropCardProcessor.updateDuoHu(self.actionID, wins, winState):
                self.louHuProcesssor.reset()
                self.dropCardProcessor.reset()
                for winSeat in wins:
                    winPlayer = self.player[winSeat]
                    winPlayer.actionHuFromOthers(tile, self.curSeat)
                looses.append(lastSeatId)
            else:
                return
        elif self.louHuProcesssor.getState() != 0:
            ftlog.debug('MajiangTableLogic.gameWin process by louHuProcesssor...')
            if self.louHuProcesssor.updateProcessor(self.actionID, MTableState.TABLE_STATE_PASS_HU, seatId):
                winState = MTableState.TABLE_STATE_PASS_HU
                magicAfertTing = True
                exInfo = self.louHuProcesssor.extendInfo
                winNode = exInfo.getWinNodeByTile(tile)
                if winNode and ('baoZhongBao' in winNode) and winNode['baoZhongBao']:
                    baoZhongBao = True    
                cp.actionAdd(tile) 
                cp.actionHuByMyself(tile, not baoZhongBao)
                # 自摸，一个人和，其他人都输
                for player in self.player:
                    if player.curSeatId != seatId:
                        if player.isObserver():
                            # 观察者不添加到loose中
                            continue
                        looses.append(player.curSeatId) 
                            
                self.louHuProcesssor.reset()
                
        elif self.daFengProcessor.getState() != 0:
            ftlog.debug('MajiangTableLogic.gameWin process by daFengProcessor...')
            if self.daFengProcessor.updateProcessor(self.actionID, MTableState.TABLE_STATE_HU, seatId):
                daFeng = True
                cp.actionHuByMyself(tile, True)
                # 自摸，一个人和，其他人都输
                for player in self.player:
                    if player.curSeatId != seatId:
                        looses.append(player.curSeatId)
                self.daFengProcessor.reset()
                
        elif self.tianHuProcessor.getState() != 0:
            ftlog.debug('MajiangTableLogic.gameWin process by tianHuProcessor...')
            if self.tianHuProcessor.updateProcessor(self.actionID, MTableState.TABLE_STATE_HU, seatId):
                tianHu = True
                cp.actionHuByMyself(tile, True)
                for player in self.player:
                    if player.curSeatId != seatId:
                        if player.isObserver():
                            continue
                        looses.append(player.curSeatId)
                self.tianHuProcessor.reset()
                
        elif self.shuffleHuProcessor.getState() != 0:
            ftlog.debug('MajiangTableLogic.gameWin process by shuffleHuProcessor...')
            if self.shuffleHuProcessor.updateProcessor(self.actionID, MTableState.TABLE_STATE_HU, seatId):
                wuDuiHu = True
                cp.actionHuByMyself(tile, True)
                for player in self.player:
                    if player.curSeatId != seatId:
                        looses.append(player.curSeatId)
                self.shuffleHuProcessor.reset()
                
        elif self.addCardHuProcessor.getState() != 0:
            ftlog.debug('MajiangTableLogic.gameWin process by addCardHuProcessor...')
            if self.addCardHuProcessor.updateProcessor(self.actionID, MTableState.TABLE_STATE_HU, seatId):
                cp.actionHuByMyself(tile, True)
                for player in self.player:
                    if player.curSeatId != seatId:
                        if player.isObserver():
                            continue
                        looses.append(player.curSeatId)
                self.addCardHuProcessor.reset()
            
        elif self.dropCardHuProcessor.getState() != 0:
            ftlog.debug('MajiangTableLogic.gameWin process by dropCardHuProcessor...')
            if self.dropCardHuProcessor.updateProcessor(self.actionID, MTableState.TABLE_STATE_HU, seatId):
                for player in self.player:
                    if player.curSeatId != seatId:
                        looses.append(player.curSeatId)
                self.dropCardHuProcessor.reset()
        
        elif self.qiangExmaoHuProcessor.getState() != 0:
            ftlog.debug('MajiangTableLogic.gameWin process by qiangExmaoHuProcessor...')
            if self.qiangExmaoHuProcessor.updateProcessor(self.actionID, seatId, MTableState.TABLE_STATE_QIANG_EXMAO_HU, tile, None):
                # 补锚的那个人被抢胡，所以补锚的那个人弃牌
                cpExmao = self.player[self.qiangExmaoHuProcessor.curSeatId]
                cpExmao.actionDrop(tile)
                # 广播其出牌
                for seatIndex in range(self.playerCount):
                    message = self.msgProcessor.table_call_drop(self.curSeat
                        , self.player[seatIndex]
                        , tile
                        , MTableState.TABLE_STATE_NEXT
                        , {}
                        , self.actionID
                        , 0)
                    ftlog.debug('MajiangTableLogic.extendMao, table_call_drop: mmessage' , message)
                    self.msgProcessor.send_message(message, [self.player[seatIndex].userId])
                
                ftlog.debug('MajiangTableLogic.gameWin qiangExmaoHuProcessor.updateProcessor')
                self.qiangExmaoHuProcessor.reset()
                cp.actionHuFromOthers(tile, self.curSeat)
                looses.append(lastSeatId)
            else:
                # 有上家同时和牌 那么当前玩家不给予响应 除非上家过牌
                return
        else:
            return
        
        for player in self.player:
            if (player.curSeatId not in wins) and (player.curSeatId not in looses):
                observers.append(player.curSeatId)
                            
        self.incrActionId('gameWin')
        # 从lastSeatId开始逆时针遍历，设置最后一个胡的人为curSeat
        for index in range(self.playerCount):
            newSeatId = (lastSeatId + index) % self.playerCount
            if newSeatId in wins:
                self.setCurSeat(newSeatId) 
                
        # 设置玩家和牌顺序
        for _id in wins:
            self.setWinOrder(_id)
        # 记录杠牌得分
        winBase = self.getTableConfig(MTDefine.WIN_BASE, 1)
        ftlog.debug('MajiangTableLogic.gameWin winBase: ', winBase
                    , ' wins:', wins
                    , ' looses:', looses
                    , ' observers:', observers)
        
        winMode = [MOneResult.WIN_MODE_LOSS for _ in range(len(self.player))]
        fanPattern = [[] for _ in range(len(self.player))]
        awardInfo = []
        awardScores = [0 for _ in range(len(self.player))]
        currentScore = [0 for _ in range(self.playerCount)]
        roundScores = [0 for _ in range(self.playerCount)]
        allCoin = [0 for _ in range(self.playerCount)]
        allTableCoin = [0 for _ in range(self.playerCount)]
        piaoPoints = None
        flowerScores = None
        horseResult = None
        NeedDropTiles = False
        displayExtends = None
        bankerWin = False
        # 判断是否为一炮多响
        if len(wins) > 1:
            for winPlayer in wins:
                self.players[winPlayer].setMultiWinTiles()
                if winPlayer == self.bankerMgr.queryBanker():
                    bankerWin = True
            self.tableTileMgr.setMultiTileNum(tile, len(wins) - 1)
            if self.playMode == MPlayMode.JIPINGHU:
                # 广东一炮多响如果庄家赢，继续坐庄，否则下家坐庄
                ftlog.debug('mingsong setMultiPaoId bankerid: ', self.bankerMgr.queryBanker()
                            , 'wins:', wins
                            , 'next:', (self.bankerMgr.queryBanker() + 1) % self.playerCount
                            )
                if bankerWin:
                    self.bankerMgr.setMultiPaoId(self.bankerMgr.queryBanker())
                else:
                    self.bankerMgr.setMultiPaoId((self.bankerMgr.queryBanker() + 1) % self.playerCount)
            else:
                self.bankerMgr.setMultiPaoId(lastSeatId)
            
        if winBase > 0:
            result = None
            if self.playMode == MPlayMode.XUELIUCHENGHE or self.playMode == MPlayMode.XUEZHANDAODI:
                result = self.OneResultCalcSiChuan(MOneResult.RESULT_WIN, wins, looses, observers, self.curSeat, lastSeatId, self.actionID, tile, grabHuGang)
            else:
                result = self.initOneResult(MOneResult.RESULT_WIN, wins, looses, observers, self.curSeat, lastSeatId, self.actionID, tile)
                if grabHuGang:
                    result.setQiangGang(True)
                result.setHuaCi(huaCi)
                result.setBaoZhongBao(baoZhongBao)
                result.setMagicAfertTing(magicAfertTing)
                result.setMagics(self.tableTileMgr.getMagicTiles(True))
                result.setTianHu(tianHu)
                result.setWuDuiHu(wuDuiHu)
                result.setQuanIndex(self.scheduleMgr.curQuan)
                if len(self.roundResult.roundResults) > 0:
                    result.setLatestOneResult(self.roundResult.roundResults[-1])
                if self.checkTableState(MTableState.TABLE_STATE_TING):
                    result.setWinNodes(cp.winNodes)
                if self.getTableConfig(MTDefine.SWITCH_FOR_ALARM, 0):
                    result.setAlarmNodes(cp.alarmInfo)
    
                    jiaoPaiConf = self.getTableConfig("jiaopai_rule", {})
                    result.setJiaoPaiConf(jiaoPaiConf[str(self.winRuleMgr.multiple)])
    
                    fanRuleConf = self.getTableConfig("fan_rule", {})
                    result.setFanRuleConf(fanRuleConf[str(self.winRuleMgr.multiple)])
    
                mingState = [0 for _ in range(self.playerCount)]
                tingState = [0 for _ in range(self.playerCount)]
                for player in self.player:
                    # 明牌状态
                    if player.isMing():
                        mingState[player.curSeatId] = 1
    
                result.setTingState(tingState)
                result.setMingState(mingState)
                
                # 抽奖牌
                if self.playMode == MPlayMode.JIXI:
                    awardTileCount = self.tableConfig.get(MTDefine.AWARD_TILE_COUNT, 1)
                    awardTiles = self.tableTileMgr.popTile(awardTileCount)
                    result.setAwardTiles(awardTiles)
    
                result.setDaFeng(daFeng)
                result.calcScore()
            
                if result.dropHuFlag == 1:
                    NeedDropTiles = True
                
                # 金币结算
                scoreList, _ = self.updateCoinWithOneResult(wins, looses, result.results[MOneResult.KEY_SCORE])
                result.setCoinScore(scoreList)
                
            self.roundResult.setPlayMode(self.playMode)
            self.roundResult.setPlayerCount(self.playerCount)
            self.roundResult.addRoundResult(result)
            # 计算手牌杠
            self.calcGangInHand(seatId, lastSeatId, tile, result.winNodes)
            self.roundResult.getChangeScore(result.results)
            tableScore = [0 for _ in range(self.playerCount)]

            if self.tableResult.score:
                tableScore = self.tableResult.score

            for i in range(self.playerCount):
                currentScore[i] = tableScore[i] + self.roundResult.score[i]
                roundScores[i] = self.roundResult.delta[i]
                allCoin[i] = self.player[i].coin
                allTableCoin[i] = self.player[i].getTableCoin(self.gameId, self.tableId)

            allCoin, allTableCoin = self.getCoinInfo()
            # roundScores = self.roundResult.delta
            # self.msgProcessor.table_call_score(allCoin
            #                 , allTableCoin
            #                 , currentScore
            #                 , roundScores
            #                 , False)

            messageScore = self.msgProcessor.table_call_score_message(allCoin
                            , allTableCoin
                            , currentScore
                            , roundScores
                            , False)
            self.msgProcessor.send_message(messageScore, self.msgProcessor.getBroadCastUIDs())
            self.msgProcessor.addMsgRecord(messageScore, self.msgProcessor.getBroadCastUIDs())

            if MOneResult.KEY_WIN_MODE in result.results:
                winMode = result.results[MOneResult.KEY_WIN_MODE]
            if MOneResult.KEY_FAN_PATTERN in result.results:
                fanPattern = result.results[MOneResult.KEY_FAN_PATTERN]
            
            fantotalPattern = result.results[MOneResult.KEY_FAN_TOTALBEI_PATTERN] if MOneResult.KEY_FAN_TOTALBEI_PATTERN in result.results else None
            
            # 带上明杠暗杠oneResult中的番型信息
            # fanPattern = self.appendGangFanPattern(fanPattern)
            loserFanPattern = None
            if MOneResult.KEY_LOSER_FAN_PATTERN in result.results:
                loserFanPattern = result.results[MOneResult.KEY_LOSER_FAN_PATTERN]
            
            detailChangeScores = None 
            if MOneResult.KEY_DETAIL_CHANGE_SCORES in result.results:
                detailChangeScores = result.results[MOneResult.KEY_DETAIL_CHANGE_SCORES]
                # if MOneResult.KEY_HORSE_SCORES in result.results:
                    # horseScores = result.results[MOneResult.KEY_HORSE_SCORES]
                    # detailChangeScores = [detailChangeScores[i] - horseScores[i] for i in range(self.playerCount)]

            if MOneResult.KEY_AWARD_INFO in result.results:
                awardInfo = result.results[MOneResult.KEY_AWARD_INFO]
            if MOneResult.KEY_AWARD_SCORE in result.results:
                awardScores = result.results[MOneResult.KEY_AWARD_SCORE]
            if self.playMode == MPlayMode.WEIHAI or self.playMode == MPlayMode.JINAN or self.playMode == MPlayMode.YANTAI:
                piaoPoints = result.results[MOneResult.KEY_PIAO_POINTS]
            if self.playMode == MPlayMode.JINAN:
                flowerScores = result.results[MOneResult.KEY_FLOWER_SCORES]
            if self.playMode == MPlayMode.JIPINGHU:
                horseResult = result.results[MOneResult.KEY_HORSE]

            if MOneResult.KEY_DISPLAY_EXTEND in result.results:
                displayExtends = result.results[MOneResult.KEY_DISPLAY_EXTEND]

        if grabHuGang:
            self.tableResult.addResult(self.roundResult)
            # 从被抢杠胡的人开始逆时针遍历，最后一个胡牌的为当前玩家
            for index in range(self.playerCount):
                newSeatId = (lastSeatId + index) % self.playerCount
                if newSeatId in wins:
                    self.setCurSeat(newSeatId)

        scoreBase = self.getTableConfig(MTDefine.SCORE_BASE, 0)
        # 更新圈数
        self.updateScheduleQuan(self.playerCount, 1 , seatId)
        ctInfo = self.getCreateTableInfo()
        btInfo, _ = self.getMagicInfo()
        # 获取最后特殊牌的协议信息
        lstInfo = self.tableTileMgr.getLastSpecialTiles(self.bankerMgr.queryBanker())
        customInfo = {
            'ctInfo':ctInfo,
            'btInfo':btInfo,
            'lstInfo':lstInfo,
            'awardInfo':awardInfo,
            'awardScores':awardScores,
            'winNum':self.winOrder,
            'hideTiles':self.player[seatId].isWon(),
            'todo':['continue'],
            'reconnect':False,
            'detailChangeScores':detailChangeScores,
        }
        # 补充winNode
        if winNode:
            customInfo['winNode'] = winNode
        # 血战血流一次输赢并不会结束，隐藏手牌
        if self.playMode == MPlayMode.XUEZHANDAODI \
                or self.playMode == MPlayMode.XUELIUCHENGHE:
            customInfo['hideHandTiles'] = True
        
        # 十风或者十三幺时显示打出的牌
        dropTiles = self.tableTileMgr.dropTiles[seatId]
        if NeedDropTiles:
            customInfo['dropTiles'] = dropTiles
            
        scores = {}
        scores['totalScore'] = self.tableResult.score
        scores['deltaScore'] = self.roundResult.score

        scores['deltaGenzhuangScore'] = self.roundResult.getRoundGangResult()
        scores['deltaGangScore'] = self.roundResult.getRoundGangResult()
        scores['deltaWinScore'] = self.roundResult.getRoundWinResult()

        self.sendTurnoverResult(True)
        isGameEnd = self.isThisRoundOver()
            
        self.msgProcessor.table_call_game_win_loose(wins
                , looses
                , observers
                , winMode
                , tile
                , scores
                , scoreBase
                , fanPattern
                , customInfo
                , piaoPoints
                , flowerScores
                , horseResult
                , displayExtends
                , loserFanPattern
                , fantotalPattern)
        
        self.updateTingResult(tile, True)

        if self.playMode == MPlayMode.JIPINGHU:
            # 发送结算信息
            self.sendRoundResult()
            # 更新任务信息
            self.updateTaskInfoProcess()
            # 牌局结束，更新tableResult
            self.tableResult.addResult(self.roundResult)
            self.resetGame(1)
        else:
            # 添加延时，延迟1s执行胡牌的后续逻辑
            self.pauseProcessor.addPauseEvent(2 + result.delayTime, 'gameWin', {
                    "gameEnd": isGameEnd
                    , 'huaZhuDaJiaoId': result.huaZhuDaJiaoId
                    , 'wins': wins
                    , 'lastSeatId': lastSeatId})
            
    def processDelayGameWin(self, data):
        '''
        胡牌的后处理
        '''
        ftlog.debug('MPauseProcessor.processDelayGameWin data:', data)
        isGameEnd = data['gameEnd']
        huaZhuDaJiaoId = data['huaZhuDaJiaoId']
        # 处理胡牌，判断游戏是否结束，没结束继续游戏
        if isGameEnd:
            # 血战血流算庄规则
            if self.playMode == MPlayMode.XUELIUCHENGHE or self.playMode == MPlayMode.XUEZHANDAODI:
                self.getBankerFromHuaZhuDaJiao(huaZhuDaJiaoId)
            # 发送结算信息
            self.sendRoundResult()
            # 更新任务信息
            self.updateTaskInfoProcess()
            # 牌局结束，更新tableResult
            self.tableResult.addResult(self.roundResult)
            self.resetGame(1)
        else:
            # 若需要充值，充值后，再发送血战到底
            if self.chargeProcessor.getState() == 0:
                self.processCombol()
    
    def processDelayGameFlow(self, data):
        '''
        流局的后处理
        '''
        ftlog.debug('MPauseProcessor.processDelayGameFlow data:', data)
        # 发送大胡信息
        self.sendRoundResult() 
        # 更新任务信息
        self.updateTaskInfoProcess()
        # 处理流局，判断游戏是否结束
        self.resetGame(0)
    
    def processPauseEvents(self, ids):
        '''
        延迟事件分派器
        '''
        for event in ids:
            if event['id'] == 'gameWin':
                self.processDelayGameWin(event['data'])
            elif event['id'] == 'gameFlow':
                self.processDelayGameFlow(event['data'])
            elif event['id'] == 'justGangTile':
                self.processDelayGangTile(event['data'])
                
    def sendTaskInfoToUser(self, userId=-1):
        # 开局后发送任务信息
        if self.tableType == MTDefine.TABLE_TYPE_CREATE:
            return
        for index in range(self.playerCount):
            if userId != -1 and self.player[index].userId != userId:
                continue
            loopTaskDesc = loop_active_task.getLoopTaskInfoProcess(self.player[index].userId, self.gameId, self.bigRoomId)
            loopWinTimesDesc = loop_win_task.getLoopTaskInfoProcess(self.player[index].userId, self.gameId, self.bigRoomId)
            winStreakDesc = win_streak_task.getWinStreakTaskInfoProcess(self.player[index].userId
                                                                        , self.gameId, self.bigRoomId
                                                                        , self.getTableConfig(MTDefine.WIN_STREAK_TASKS_DESC, None))
            winStreakAllInfo = win_streak_task.getWinStreakTaskAllDesc(self.getTableConfig(MTDefine.WIN_STREAK_TASKS_DESC, None))
            self.msgProcessor.table_call_tips_task(self.player[index].userId, loopTaskDesc, winStreakDesc, loopWinTimesDesc, winStreakAllInfo)
         
    def updateCoinWithOneResult(self, wins, looses, scores):
        '''
        OneResult 金币与金币转换 包含：服务费扣除 积分与金币调整 大胡服务费扣除
        三种结算 此处的赢与输应该是根据scores中的值的正负来判断
        1）一赢多输
        结算每个输家，汇总结算赢家
        2）一赢一输
        结算输家，结算赢家
        3）多赢一输
        结算输家，按比例结算赢家
        
        结算流程：
        先结算输家
            扣除服务费，直至0
            扣除输分，直至0
        再结算赢家
            先结算赢分
            扣除服务费
            扣除大胡服务费
        输家 前端显示 金币值：服务费＋输家金币
        赢家 前端显示 金币值：输家金币－服务费-大胡服务费
        return  scoreList 是否需要充值
        '''
        ftlog.debug('MajiangTableLogic.updateCoinWithOneResult wins:', wins
                        , 'looses:', looses
                        , 'scores:', scores)
        scoreList = [0 for _ in range(self.playerCount)]
        needCharge = False
        # 不是金币桌 则返回
        if self.tableType != MTDefine.TABLE_TYPE_NORMAL:
            return scores, False
        theoryScore = copy.deepcopy(scores)
        baseChip = self.getTableConfig(MTDefine.BASE_CHIP, 1)
        # 转换为金币
        for seatId in range(self.playerCount):
            theoryScore[seatId] = theoryScore[seatId] * baseChip
        # 获取score输赢的seatid 
        scoreWinIds = []
        scoreLooseIds = []
        for seatId in range(self.playerCount):
            if theoryScore[seatId] > 0:
                scoreWinIds.append(seatId)
            elif theoryScore[seatId] < 0:
                scoreLooseIds.append(seatId)
        # 扣除输家服务费
        serviceScore = [0 for _ in range(self.playerCount)]
        # 只有胡牌扣除服务费,JIPINGHU开局收取服务费
        if self.playMode != MPlayMode.JIPINGHU:
            self.ConsumeServiceFee(looses, serviceScore)
        ftlog.debug('CalcResult first, consume loosers serviceFee, loosers:', looses
                    , ' serviceScore:', serviceScore)
        # 扣除输家金币
        realScore = copy.deepcopy(scores)
        # 是否需要转换为金币
        for seatId in range(self.playerCount):
            realScore[seatId] = realScore[seatId] * baseChip
            
        needCharge |= self.CalcCoinResult(realScore, scoreLooseIds)
        ftlog.debug('CalcResult second, consume loosers coin, loosers:', scoreLooseIds
                    , ' realScore:', realScore)
        
        # 结算赢家的金币，根据输家的金币实际扣除情况计算赢家的金币数
        if len(scoreWinIds) == 1:
            realScore[scoreWinIds[0]] = 0
            for loose in scoreLooseIds:
                realScore[scoreWinIds[0]] += abs(realScore[loose])
        elif (len(scoreLooseIds) == 1 and len(scoreWinIds) > 1):
            loose = scoreLooseIds[0]
            if realScore[loose] != theoryScore[loose]:
                allWins = 0
                for win in scoreWinIds:
                    allWins += realScore[win]
                for win in scoreWinIds:
                    realScore[win] = abs(realScore[loose]) * realScore[win] / allWins
        needCharge |= self.CalcCoinResult(realScore, scoreWinIds)
        ftlog.debug('CalcResult third, consume wins coin, wins:', scoreWinIds
                    , ' realScore:', realScore
                    , ' theoryScore:', theoryScore
        )
        
        # 免费场赢家的系统包赔
        if self.roomConfig.get('level', MTDefine.FREE) == MTDefine.FREE:
            for win in scoreWinIds:
                sysScore = theoryScore[win] - realScore[win]
                if sysScore > 0:
                    realScore[win] = theoryScore[win]
                    if not self.player[win].isRobot():
                        # 正常玩家系统补助
                        clientId = Majiang2Util.getClientId(self.player[win].userId)
                        _, finalChip = hallrpcutil.incrTableChip(
                            self.player[win].userId
                            , self.gameId
                            , sysScore
                            , 0
                            , 'MAJIANG_ROOM_PAID'
                            , self.roomId
                            , clientId
                            , self.tableId
                        )
                        self.player[win].setTableCoin(finalChip)
                        ftlog.info('Majiang2.logAnalyse userId:', self.player[win].userId
                                        , 'tableCoin:', self.player[win].getTableCoin(self.gameId, self.tableId)
                                        , 'PaidChip:', sysScore
                                        , 'tableId:', self.tableId
                                        , 'RoomPaid')
                    else:
                        # 机器人系统补助
                        self.player[win].setTableCoin(self.player[win].getTableCoin(self.gameId, self.tableId) + sysScore)
                        ftlog.info('Majiang2.logAnalyse userId:', self.player[win].userId
                                   , 'tableCoin:', self.player[win].getTableCoin(self.gameId, self.tableId)
                                   , 'PaidChip:', sysScore
                                   , 'tableId:', self.tableId
                                   , 'RoomPaid')
                        
                    ftlog.debug('MajiangTableLogic.updateCoinWithOneResult sysExtend player.userId:', self.player[win].userId)
        
        # 结算赢家的服务费
        if self.playMode != MPlayMode.JIPINGHU:
            self.ConsumeServiceFee(wins, serviceScore)
        ftlog.debug('CalcResult forth, consume wins serviceFee, wins:', scoreWinIds
                    , ' serviceScore:', serviceScore)
            
        bigFees = [0 for _ in range(self.playerCount)]
        # 收取大胡服务费
        self.ConsumServiceFeeDaHu(scoreWinIds, theoryScore, realScore, bigFees)
        ftlog.debug('CalcResult fifth, consume wins bigFee, wins:', scoreWinIds
                    , ' bigFees:', bigFees)
        
        # 整理玩家真实的金币变化值 
        for seatId in range(self.playerCount):
            scoreList[seatId] = realScore[seatId] + serviceScore[seatId] + bigFees[seatId]
        ftlog.debug('MajiangTable.CalcResult scoreList:', scoreList)
        return scoreList, needCharge
         
    def OneResultCalcSiChuan(self, typeResult=-1, wins=[], looses=[], observers=[], winSeatId=-1, lastSeatId=-1, actionId=-1, winTile=-1, grabGangHu=False):
        '''
        四川麻将：结算部分细分
        赢局 流局
        '''
        ftlog.debug('MajiangTableLogic.OneResultCalcSiChuan...')
        oneResultList = []
        # 胡牌结算
        result = self.initOneResult(typeResult, wins, looses, observers, winSeatId, lastSeatId, actionId, winTile)
        result.setQiangGang(grabGangHu)
        if len(self.roundResult.roundResults) > 0:
            result.setLatestOneResult(self.roundResult.roundResults[-1])
        result.calcScore()
        # 金币结算
        scoreList, _ = self.updateCoinWithOneResult(wins, looses, result.results[MOneResult.KEY_SCORE])
        result.setCoinScore(scoreList)
        if result.needCallTransfer:
            callTranResult = self.initOneResult(MOneResult.RESULT_CALLTRAN, wins, looses)
            if len(self.roundResult.roundResults) > 0:
                callTranResult.setLatestOneResult(self.roundResult.roundResults[-1])
                callTranResult.calcScore()
                scoreList, _ = self.updateCoinWithOneResult([], [], callTranResult.results[MOneResult.KEY_SCORE])
                callTranResult.setCoinScore(scoreList)
                oneResultList.append(callTranResult)
        if self.isThisRoundOver():
            # 退税计算
            tuiShuiLooseIds = result.huaZhuLooseIds + result.daJiaoLooseIds
            ftlog.debug('MajiangTableLogic OneResultCalcSiChuan tuiShuiLooseIds:', tuiShuiLooseIds)
            for oneResult in self.roundResult.roundResults:
                if oneResult.results[MOneResult.KEY_TYPE] == MOneResult.KEY_TYPE_NAME_GANG \
                        and not oneResult.hasCallTransfer \
                        and oneResult.winSeatId in tuiShuiLooseIds:
                    ftlog.debug('MajiangTableLogic OneResultCalcSiChuan TuiShui...')
                    tuiShuiResult = self.initOneResult(MOneResult.RESULT_TUISHUI) 
                    tuiShuiResult.setLatestOneResult(oneResult)
                    tuiShuiResult.calcScore()
                    scoreList, _ = self.updateCoinWithOneResult([], [], tuiShuiResult.results[MOneResult.KEY_SCORE])
                    tuiShuiResult.setCoinScore(scoreList)
                    oneResultList.append(tuiShuiResult)
            # 花猪计算 一次计算一个输家 多个赢家
            ftlog.debug('MajiangTableLogic OneResultCalcSiChuan huaZhuLooseIds:', result.huaZhuLooseIds, 'huaZhuWinIds:', result.huaZhuWinIds)
            if len(result.huaZhuWinIds) > 0:
                for looseId in result.huaZhuLooseIds:
                    loserOneResult = self.initOneResult(MOneResult.RESULT_HUAZHU, result.huaZhuWinIds, looseId)
                    loserOneResult.calcScore()
                    scoreList, _ = self.updateCoinWithOneResult(result.huaZhuWinIds, [looseId], loserOneResult.results[MOneResult.KEY_SCORE])
                    loserOneResult.setCoinScore(scoreList)
                    oneResultList.append(loserOneResult)
            # 大叫计算 一次计算一个输家 多个赢家
            ftlog.debug('MajiangTableLogic OneResultCalcSiChuan daJiaoLooserIds:', result.daJiaoLooseIds, 'daJiaoWinIds:', result.daJiaoWinIds)
            if len(result.daJiaoWinIds) > 0:
                for looseId in result.daJiaoLooseIds:
                    loserOneResult = self.initOneResult(MOneResult.RESULT_DAJIAO, result.daJiaoWinIds, looseId)
                    loserOneResult.calcScore()
                    scoreList, _ = self.updateCoinWithOneResult(result.daJiaoWinIds, [looseId], loserOneResult.results[MOneResult.KEY_SCORE])
                    loserOneResult.setCoinScore(scoreList)
                    oneResultList.append(loserOneResult)
        # 信息合并
        result.updateInfo(oneResultList) 
        
        return result 
    
    def updateTaskInfoProcess(self, curSeatId=-1):
        '''
        更新任务消息
        '''
        if self.tableType == MTDefine.TABLE_TYPE_CREATE:
            return
        
        ftlog.debug('MajiangTableLogic.updateTaskInfoProcess curSeatId:', curSeatId)
        ftlog.debug('MajiangTableLogic.updateTaskInfoProcess scoreChange:', self.roundResult.scoreChange
                        , 'winOrder:', self.winOrder)
        winStateList = [False for _ in range(self.playerCount)]
        userTileInfo = [{} for _ in range(self.playerCount)]
        winNumList = [0 for _ in range(self.playerCount)]
        # 需要更新的seatId集合
        totalSeatIds = []
        for seatId in range(self.playerCount):
            if not self.players[seatId]:
                continue
            
            if curSeatId != -1 and seatId != curSeatId:
                # curSeatId 不为－1时，指定更新curSeatId任务状态
                continue
            elif self.players[seatId].isIgnoreMessage():
                # 玩家离开或者认输时，已经更新过了任务状态，不重复更新
                continue
            
            totalSeatIds.append(seatId)
            totalScore = self.roundResult.scoreChange[seatId] if self.roundResult.scoreChange else 0
            if totalScore > 0:
                winStateList[seatId] = True
                winNumList[seatId] = self.winTimes[seatId]
                userTileInfo[seatId] = {
                    "tiles": self.player[seatId].copyHandTiles(),  # [1,2,3,4,5]
                    "gang": self.player[seatId].copyGangArray(),  # [[1,1,1,1],[9,9,9,9]] 明1&暗杠0, 花色
                    "chi": self.player[seatId].copyChiArray(),  # [[2,3,4]]代表吃(1,2,3),(5,6,7)
                    "peng": self.player[seatId].copyPengArray(),  # [1,2]代表吃(1,1,1),(2,2,2)
                    "zhan": self.player[seatId].zhanTiles,
                    "tile" : self.player[seatId].copyHuArray()
                    }
        
        ftlog.debug('MajiangTableLogic.winStateList:', winStateList, 'totalSeatIds:', totalSeatIds)   
        # 记录任务奖励前的金币信息   
        oldTableCoin = [0 for _ in range(self.playerCount)]
        for cp in self.player:
            if not cp:
                continue
            
            if not cp.isRobot():
                oldTableCoin[cp.curSeatId] = hallrpcutil.getTableChip(cp.userId, self.gameId, self.tableId)
            else:
                oldTableCoin[cp.curSeatId] = cp.tableCoin
                
        if self.tableObserver:
            # 连胜任务
            winStreaksConfig = self.getTableConfig(MTDefine.WIN_STREAK_TASKS_DESC, None)
            self.tableObserver.upDateUserWinStreaks(self.players, winStateList, winStreaksConfig, winNumList, userTileInfo, totalSeatIds)
        
        # 任务奖励后的金币信息
        for cp in self.player:
            if not cp:
                continue
            
            if not cp.isRobot():
                changeChip = hallrpcutil.getTableChip(cp.userId, self.gameId, self.tableId) - oldTableCoin[cp.curSeatId] 
            else:
                changeChip = cp.tableCoin - oldTableCoin[cp.curSeatId] 
            ftlog.info('Majiang2.logAnalyse userId:', cp.userId
                            , 'tableCoin:', cp.getTableCoin(self.gameId, self.tableId)
                            , 'TaskChip:', changeChip
                            , 'tableId:', self.tableId
                            , 'TaskReward')
      
    def processCombol(self, seatId=-1):
        if self.playMode == MPlayMode.XUEZHANDAODI:
            # comb特效 
            combIds = self.getNoWinPlayerId()
            ftlog.debug('MTableLogic.processCombol combIds:', combIds, 'playerCount:', self.playerCount)
            if len(combIds) == (self.playerCount - 2):
                if seatId == -1:
                    for player in self.players: 
                        if not player.isIgnoreMessage() and seatId == -1:
                            message = self.msgProcessor.table_call_ask_comb(player, player.curSeatId, combIds, False)
                            self.pauseProcessor.addDelayTask(2, player.userId, message, self.msgProcessor)
                else:          
                    message = self.msgProcessor.table_call_ask_comb(self.players[seatId], self.players[seatId].curSeatId, combIds, True)
                    self.pauseProcessor.addDelayTask(0, self.players[seatId].userId, message, self.msgProcessor)
 
    def sendWinerInfo(self, seatId):
        # 断线重练使用，发送赢家的消息
        ftlog.debug('MTableLogic.sendWinerInfo tableResult.score: ', self.tableResult.score
                    , 'roundResultScore: ', self.roundResult.score
                    , 'gangResult: ', self.roundResult.getRoundGangResult()
                    , 'winResult: ', self.roundResult.getRoundWinResult())
        for _id in range(self.playerCount):
            if self.player[_id] and self.player[_id].isWon():
                tableResultScore = self.tableResult.score
                if not tableResultScore:
                    tableResultScore = [0 for _ in range(self.playerCount)] 
                roundResultScore = self.roundResult.score
                if not tableResultScore:
                    roundResultScore = [0 for _ in range(self.playerCount)]
                gangResultScore = self.roundResult.getRoundGangResult()
                if not gangResultScore:
                    gangResultScore = [0 for _ in range(self.playerCount)]
                genResultScore = self.roundResult.getRoundGenzhuangResult()
                if not genResultScore:
                    genResultScore = [0 for _ in range(self.playerCount)]
                
                winResultScore = self.roundResult.getRoundWinResult()
                if not winResultScore:
                    winResultScore = [0 for _ in range(self.playerCount)]
                
                scoreBase = self.getTableConfig(MTDefine.SCORE_BASE, 0)
                
                # 流局，局数不加1
                ctInfo = self.getCreateTableInfo()
                btInfo, _ = self.getMagicInfo()
                # 获取最后的特殊牌协议
                lstInfo = self.tableTileMgr.getLastSpecialTiles(self.bankerMgr.queryBanker())
                customInfo = {
                    'ctInfo':ctInfo,
                    'btInfo':btInfo,
                    'lstInfo':lstInfo,
                    'winNum':self.winOrder,
                    'hideTiles':self.player[seatId].isWon(),
                    'todo':['continue'],
                    'reconnect':True
                    }

                self.msgProcessor.table_call_game_win(self.player[_id]
                                            , 1
                                            , self.player[_id].copyHuArray()
                                            , [self.player[seatId].userId]
                                            , tableResultScore[_id]
                                            , roundResultScore[_id]
                                            , gangResultScore[_id]
                                            , winResultScore[_id]
                                            , scoreBase
                                            , ""
                                            , customInfo
                                            , 0
                                            , 0
                                            , None)

    def sendTurnoverResult(self, gamewin=False, seatId=-1):
        '''
        发送对局流水消息 seatId=0 则是群发
        '''  
        if self.playMode == MPlayMode.XUEZHANDAODI \
            or self.playMode == MPlayMode.XUELIUCHENGHE \
            or self.playMode == MPlayMode.JIPINGHU:
                # 发送对局流水
            detailDesc = [[] for _ in range(self.playerCount)]
            for ri in range(0, len(self.roundResult.roundResults)):
                if MOneResult.KEY_DETAIL_DESC_LIST in self.roundResult.roundResults[ri].results:
                    detailResult = self.roundResult.roundResults[ri].results[MOneResult.KEY_DETAIL_DESC_LIST]
                    for detail in detailResult:
                        for index in range(self.playerCount):
                            if detail[index] != ['', '', 0, '']:
                                detailDesc[index].append(detail[index])
            
            maxFan = self.tableConfig.get(MTDefine.MAX_FAN, 0)
            ftlog.debug('MajiangTableLogic maxFan:', maxFan)
            if maxFan > 0:
                maxFanDesc = str(maxFan) + "倍封顶"
            else:
                maxFanDesc = ""
            ftlog.debug("MajiangTableLogic.sendTurnoverResult score:", self.roundResult.score, 'detailDesc:', detailDesc)
            if self.roundResult.score:
                if self.playMode == MPlayMode.JIPINGHU:
                    for index in range(self.playerCount):
                        self.msgProcessor.table_call_detail_desc(self.player[index].userId, index,
                                                                 self.roundResult.scoreChange, detailDesc,
                                                                 maxFanDesc)
                        '''
                        messageTemp = self.msgProcessor.table_call_detail_desc_message(self.player[index].userId, index,
                                                                 self.roundResult.scoreChange[index], detailDesc[index],
                                                                 maxFanDesc)
                        self.pauseProcessor.addDelayTask(5, self.player[index].userId, messageTemp, self.msgProcessor)
                        '''
                        ftlog.debug("self.pauseProcessor.addDelayTask(6")
                else:
                    if seatId != -1:
                        self.msgProcessor.table_call_detail_desc(self.player[seatId].userId, seatId, self.roundResult.score[seatId], detailDesc[seatId], maxFanDesc)
                    else:
                        for index in range(self.playerCount):
                            self.msgProcessor.table_call_detail_desc(self.player[index].userId, index, self.roundResult.scoreChange[index], detailDesc[index], maxFanDesc)

    def sendRoundResult(self):
        """
        发送当前牌桌结算消息
        """
        cFinal = 0
        if self.scheduleMgr.isOver():
            cFinal = 1
        totalBei = self.roundResult.getTotalFanSummary()
        exinfoHuResult = self.roundResult.getDaHuResult(self.playerCount)
        ftlog.debug("MajiangTableLogic sendRoundResult fanSymbol: ", exinfoHuResult)
        infos = [{} for _ in range(self.playerCount)]
        for seatId in range(self.playerCount):
            if not self.players[seatId]:
                continue
            
            infos[seatId]['userId'] = self.players[seatId].userId
            infos[seatId]['seatId'] = seatId
            
            # 这个字段判断是不是大胡
            if MOneResult.EXINFO_BIGWIN in exinfoHuResult[seatId]:
                if self.playMode == MPlayMode.JIPINGHU:
                    infos[seatId]['patternInfo'] = exinfoHuResult[seatId][MOneResult.EXINFO_BIGWIN]
                else:
                    infos[seatId]['patternInfo'] = [exinfoHuResult[seatId][MOneResult.EXINFO_BIGWIN]]
            
            if self.playMode == MPlayMode.XUEZHANDAODI or self.playMode == MPlayMode.XUELIUCHENGHE:
                if MOneResult.EXINFO_WINTIMES in exinfoHuResult[seatId]:
                    if self.playMode == MPlayMode.XUEZHANDAODI:
                        infos[seatId]['totalFan'] = exinfoHuResult[seatId][MOneResult.EXINFO_WINTIMES]
                    else:
                        infos[seatId]['totalFan'] = self.winTimes[seatId]
                
                    
                if MOneResult.EXINFO_HU_ACTION in exinfoHuResult[seatId]:
                    infos[seatId]['actionHuInfo'] = exinfoHuResult[seatId][MOneResult.EXINFO_HU_ACTION] 
                    
                if MOneResult.EXINFO_WINTILE in exinfoHuResult[seatId]:
                    infos[seatId]['winTile'] = exinfoHuResult[seatId][MOneResult.EXINFO_WINTILE]
            
            if self.playMode == MPlayMode.JIPINGHU:
                infos[seatId]['totalFan'] = totalBei[seatId]
                if MOneResult.EXINFO_JIPING_ISWIN in exinfoHuResult[seatId]:
                    infos[seatId]['iswin'] = exinfoHuResult[seatId][MOneResult.EXINFO_JIPING_ISWIN]
                
            infos[seatId]['totalScore'] = self.roundResult.scoreChange[seatId]
            infos[seatId]['tilesInfo'] = {
                "tiles": self.player[seatId].copyHandTiles(),  # [1,2,3,4,5]
                "gang": self.player[seatId].copyGangArray(),  # [[1,1,1,1],[9,9,9,9]] 明1&暗杠0, 花色
                "chi": self.player[seatId].copyChiArray(),  # [[2,3,4]]代表吃(1,2,3),(5,6,7)
                "peng": self.player[seatId].copyPengArray(),  # [1,2]代表吃(1,1,1),(2,2,2)
                "zhan": self.player[seatId].zhanTiles,
                "tile" : self.player[seatId].copyHuArray()
                }
            # 判断玩家是否破产
            tableCoin = self.player[seatId].getTableCoin(self.gameId, self.tableId)
            # tableCoin = userchip.getTableChip(self.players[seatId].userId, self.gameId, self.tableId)
            infos[seatId]['bankrupt'] = True if (tableCoin <= 0 and self.tableType == MTDefine.TABLE_TYPE_NORMAL) else False
            ftlog.debug('MajaingTableLogic tableCoin:', tableCoin, 'tableType:', self.tableType, 'bankrupt:', infos[seatId]['bankrupt'])
        isGameFlow = self.isTableFlow()
        self.msgProcessor.round_result_game_over(isGameFlow, infos, cFinal)
    
    def gameFlow(self, seatId):
        """
        流局,所有人都是lose,gameflow字段为1
        """
        ftlog.debug('MajiangTableLogic.gameFlow seatId:', seatId)
        
        # 结算的类型
        # 1 吃和
        # 0 自摸
        # -1 输牌
        tile = 0
        wins = []
        looses = []
        observers = []
        for player in self.player:
            if (not player) or (player.isIgnoreMessage()):
                continue
            looses.append(player.curSeatId)
            
        if self.addCardProcessor.getState() != 0:
            exInfo = self.addCardProcessor.extendInfo
            if exInfo:
                ftlog.debug('gameFlow exInfo:', exInfo)
        elif self.dropCardProcessor.getState() != 0:
            self.dropCardProcessor.updateProcessor(self.actionID, seatId, MTableState.TABLE_STATE_HU, tile, None)
            self.dropCardProcessor.reset()
                    
        # 记录杠牌得分
        winBase = self.getTableConfig(MTDefine.WIN_BASE, 1)
        ftlog.debug('MajiangTableLogic.gameFlow winBase: ', winBase)
        
        winMode = [MOneResult.WIN_MODE_LOSS for _ in range(len(self.players))]
        fanPattern = [[] for _ in range(len(self.players))]
        currentScore = [0 for _ in range(self.playerCount)]
        piaoPoints = None
        flowerScores = None
        horseResult = None
        displayExtends = None
        if winBase > 0:
            if self.playMode == MPlayMode.XUEZHANDAODI or self.playMode == MPlayMode.XUELIUCHENGHE:
                result = self.OneResultCalcSiChuan(MOneResult.RESULT_FLOW, [], [], [], -1, seatId, self.actionID)
            else:
                result = self.initOneResult(MOneResult.RESULT_FLOW, [], [], [], -1, seatId, self.actionID)
                result.calcScore()
            self.roundResult.setPlayMode(self.playMode)
            self.roundResult.setPlayerCount(self.playerCount)
            self.roundResult.addRoundResult(result)
            # 保存这一局的积分变化，需要发送给前端
            self.roundResult.getChangeScore(result.results)
            # 加上牌桌上局数总分
            tableScore = [0 for _ in range(self.playerCount)]
            allCoin, allTableCoin = self.getCoinInfo()
            if self.tableResult.score:
                tableScore = self.tableResult.score
            for i in range(self.playerCount):
                currentScore[i] = tableScore[i] + self.roundResult.score[i]
            self.msgProcessor.table_call_score(allCoin
                                               , allTableCoin
                                               , currentScore
                                               , self.roundResult.delta
                                               , False)
            # 计算手牌杠
            self.calcGangInHand(-1, seatId, tile, result.winNodes)

            if MOneResult.KEY_FAN_PATTERN in result.results:
                fanPattern = result.results[MOneResult.KEY_FAN_PATTERN]
            # 带上明杠暗杠oneResult中的番型信息
            fanPattern = self.appendGangFanPattern(fanPattern)
            
            loserFanPattern = None
            if MOneResult.KEY_LOSER_FAN_PATTERN in result.results:
                loserFanPattern = result.results[MOneResult.KEY_LOSER_FAN_PATTERN]
            detailChangeScores = None
            if MOneResult.KEY_DETAIL_CHANGE_SCORES in result.results:
                detailChangeScores = result.results[MOneResult.KEY_DETAIL_CHANGE_SCORES]
                
            if self.playMode == MPlayMode.WEIHAI or self.playMode == MPlayMode.JINAN or self.playMode == MPlayMode.YANTAI:
                piaoPoints = result.results[MOneResult.KEY_PIAO_POINTS]
            if self.playMode == MPlayMode.JINAN:
                flowerScores = result.results[MOneResult.KEY_FLOWER_SCORES]
            if MOneResult.KEY_DISPLAY_EXTEND in result.results:
                displayExtends = result.results[MOneResult.KEY_DISPLAY_EXTEND]

        # 处理流局
        scoreBase = self.getTableConfig(MTDefine.SCORE_BASE, 0)
        self.tableResult.addResult(self.roundResult)
        # 更新圈数        
        self.updateScheduleQuan(self.playerCount, 0, seatId)
        # 流局，局数不加1
        ctInfo = self.getCreateTableInfo()
        btInfo, _ = self.getMagicInfo()
        # 获取最后的特殊牌协议
        lstInfo = self.tableTileMgr.getLastSpecialTiles(self.bankerMgr.queryBanker())
        customInfo = {
            'ctInfo':ctInfo,
            'btInfo':btInfo,
            'lstInfo':lstInfo,
            'winNum':self.winOrder,
            'hideTiles':self.player[seatId].isWon(),
            'todo':['continue'],
            'reconnect':False,
            'detailChangeScores':detailChangeScores
            }

        scores = {}
        scores['totalScore'] = self.tableResult.score
        scores['deltaScore'] = self.roundResult.score
        scores['deltaGenzhuangScore'] = self.roundResult.getRoundGenzhuangResult()
        scores['deltaGangScore'] = self.roundResult.getRoundGangResult()
        scores['deltaWinScore'] = self.roundResult.getRoundWinResult()

        # 发送对局流水信息
        self.sendTurnoverResult()
        
        self.msgProcessor.table_call_game_win_loose(wins
                , looses
                , observers
                , winMode
                , -1
                , scores
                , scoreBase
                , fanPattern
                , customInfo
                , piaoPoints
                , flowerScores
                , horseResult
                , displayExtends
                , loserFanPattern)
        
        if self.playMode == MPlayMode.XUELIUCHENGHE or self.playMode == MPlayMode.XUEZHANDAODI:
            self.getBankerFromHuaZhuDaJiao(result.huaZhuDaJiaoId)
        # 延迟1s执行流局的后续逻辑    
        self.pauseProcessor.addPauseEvent(2, 'gameFlow', {})
        
    def getNoWinPlayerId(self):
        noWonId = []
        for player in self.players:
            if player and not player.isObserver():
                noWonId.append(player.curSeatId)
        return noWonId
    
    def playerCancel(self, seatId, beforeDrop=False):
        """用户选择放弃
        """
        cancelPlayer = self.player[seatId]
        tile = 0
        if self.dropCardProcessor.getState() != 0:
            ftlog.debug("MajiangTableLogic.playerCancel Drop seatId:", seatId)
            tile = self.dropCardProcessor.getTile()
            lastSeatId = self.dropCardProcessor.curSeatId

            # 别人出牌检查过胡
            # pass后将漏胡的牌加入过胡牌数组,下次轮到自己回合时清空
            # 遍历所有牌，检测玩家所有可以胡的牌，全部加到列表
            if self.winRuleMgr.isPassHu():
                if self.dropCardProcessor.getStateBySeatId(seatId) & MTableState.TABLE_STATE_HU:
                    passHuTile = []
                    cp = self.player[seatId]
                    if self.playMode == MPlayMode.JINAN \
                            or self.playMode == MPlayMode.XUELIUCHENGHE \
                            or self.playMode == MPlayMode.XUEZHANDAODI:
                        allTile = cp.copyTiles()
                        allTile[MHand.TYPE_HAND].append(tile)
                        winResult, _ = self.winRuleMgr.isHu(allTile, tile, cp.isTing(),
                                                                         MWinRule.WIN_BY_OTHERS,
                                                                         self.tableTileMgr.getMagicTiles(cp.isTing()),
                                                                         cp.winNodes, cp.curSeatId)
                        if winResult:
                            passHuTile.append(tile)
                    else:
                        for testTile in xrange(1, 40):
                            allTile = cp.copyTiles()
                            allTile[MHand.TYPE_HAND].append(testTile)
                            winResult, _ = self.winRuleMgr.isHu(allTile, testTile, cp.isTing(), MWinRule.WIN_BY_OTHERS, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.winNodes, cp.curSeatId)
                            if winResult:
                                passHuTile.append(testTile)
    
    
                    ftlog.debug("MajiangTableLogic.addPassHuTileByDrop drop cancel", seatId, passHuTile)
                    for tmpTile in passHuTile:
                        self.tableTileMgr.addPassHuBySeatId(seatId, tmpTile)

            playerProcessor = self.dropCardProcessor.processors[seatId]
            self.dropCardProcessor.resetSeatId(seatId)
            dropState = self.dropCardProcessor.getState()
            ftlog.debug('MajiangTableLogic.playerCancel dropState:', dropState)

            if playerProcessor['state'] & MTableState.TABLE_STATE_PENG:  # 过碰
                pengs = playerProcessor['extendInfo'].getChiPengGangResult(MTableState.TABLE_STATE_PENG)
                if pengs:
                    for peng in pengs:
                        cancelPlayer.guoPengTiles.add(peng[0])
            if playerProcessor['state'] & MTableState.TABLE_STATE_HU:  # 过胡
                cancelPlayer.guoHuPoint = cancelPlayer.totalWinPoint
                if self.checkLouHu(lastSeatId):
                    ftlog.debug('MajiangTableLogic.playerCancel user:', seatId, ' cancelWin, user:', lastSeatId, ' louhu...')
        if self.addCardProcessor.getState() != 0:
            if self.playMode == MPlayMode.PANJIN and beforeDrop == False:
                if self.winRuleMgr.isPassHu():
                    if self.addCardProcessor.getState() & MTableState.TABLE_STATE_HU:
                        passHuTile = []
                        cp = self.player[seatId]
                        for testTile in xrange(1, 40):
                            allTile = cp.copyTiles()
                            allTile[MHand.TYPE_HAND].append(testTile)
                            
                            winResult, _ = self.winRuleMgr.isHu(allTile, testTile, cp.isTing(), MWinRule.WIN_BY_OTHERS, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.winNodes, cp.curSeatId)
                            if winResult:
                                passHuTile.append(testTile)
        
                        ftlog.debug("addPassHuTileByDrop add cancel", seatId, passHuTile)
                        for tmpTile in passHuTile:
                            self.tableTileMgr.addPassHuBySeatId(seatId, tmpTile)
                        
                        
            ftlog.debug("playerCancel Add", seatId)
            tile = copy.deepcopy(self.addCardProcessor.getTile())
            addState = copy.deepcopy(self.addCardProcessor.state)
            if self.playMode == MPlayMode.JIXI and cancelPlayer.isTing() and addState & MTableState.TABLE_STATE_HU:
                ftlog.debug('MajiangTableLogic.playerCancel playMode jixi cant pass hu')
                return
            # 成功取消才继续
            if self.addCardProcessor.updateProcessor(self.actionID, 0, seatId):
                ftlog.debug('MajiangTableLogic.playerCancel tile:', tile, ' addState:', addState)
                if cancelPlayer.isTing() and addState & MTableState.TABLE_STATE_HU:
                    ftlog.debug('MajiangTableLogic.playerCancel, user pass win, drop tile directly....')
                    if self.tableTileMgr.isHaidilao() and not self.tableTileMgr.canDropWhenHaidiLao():
                        pass
                    else:
                        self.dropTile(seatId, tile)

            if addState & MTableState.TABLE_STATE_HU:
                cancelPlayer.guoHuPoint = cancelPlayer.totalWinPoint  # 过胡

        if self.qiangGangHuProcessor.getState() != 0:
            ftlog.debug("playerCancel QiangGangHu", seatId)
            if self.playMode == MPlayMode.JIXI:
                ftlog.debug('MajiangTableLogic.playerCancel playMode jixi cant pass qiang gang hu')
                return
            tile = self.qiangGangHuProcessor.tile
            self.qiangGangHuProcessor.resetSeatId(seatId)
            if self.qiangGangHuProcessor.getState() == 0:
                ftlog.debug('__qiang_gang_hu_processor all player check')
                # 恢复挂起的杠牌状态 允许原来杠牌的玩家继续杠牌
                gangSeatId = self.qiangGangHuProcessor.curSeatId
                gangState = self.qiangGangHuProcessor.gangState
                gangSpecialTile = self.qiangGangHuProcessor.specialTile
                gangTile = self.qiangGangHuProcessor.tile
                gangPattern = self.qiangGangHuProcessor.gangPattern
                gangStyle = self.qiangGangHuProcessor.style
                self.justGangTile(self.curSeat, gangSeatId, gangTile, gangPattern, gangStyle, gangState, True, gangSpecialTile, self.__qiang_gang_hu_processor.qiangGangSeats)
                ftlog.debug('qiangGangHuProcessor.qiangGangSeats = ', self.qiangGangHuProcessor.qiangGangSeats)
                self.qiangGangHuProcessor.clearQiangGangSeats()
            if self.curState() == 0:
                self.setCurSeat((self.__cur_seat - 1) % self.playerCount)
            # 过胡
            cancelPlayer.guoHuPoint = cancelPlayer.totalWinPoint

        if self.qiangExmaoPengProcessor.getState() != 0:
            ftlog.debug("playerCancel Qiangmaopeng", seatId)

            tile = self.qiangExmaoPengProcessor.tile
            self.qiangExmaoPengProcessor.resetSeatId(seatId)
            if self.qiangExmaoPengProcessor.getState() == 0:
                ftlog.debug('qiangExmaoPengProcessor all player check')
                # 恢复挂起的exmao状态 允许原来exmao的玩家继续exmao
                maoSeatId = self.qiangExmaoPengProcessor.curSeatId
                maoTile = self.qiangExmaoPengProcessor.tile
                maoStyle = self.qiangExmaoPengProcessor.style
                self.justExmao(maoSeatId, maoTile, maoStyle)
                
                self.qiangExmaoPengProcessor.reset()
            if self.curState() == 0:
                self.setCurSeat((self.__cur_seat - 1) % self.playerCount)
                
        if self.qiangExmaoHuProcessor.getState() != 0:
            ftlog.debug("playerCancel qiangExmaoHuProcessor", seatId)

            tile = self.qiangExmaoHuProcessor.tile
            self.qiangExmaoHuProcessor.resetSeatId(seatId)
            if self.qiangExmaoHuProcessor.getState() == 0:
                ftlog.debug('qiangExmaoHuProcessor all player check')
                # 恢复挂起的exmao状态 允许原来exmao的玩家继续exmao
                maoSeatId = self.qiangExmaoHuProcessor.curSeatId
                maoTile = self.qiangExmaoHuProcessor.tile
                maoStyle = self.qiangExmaoHuProcessor.style
                self.justExmao(maoSeatId, maoTile, maoStyle)
                
                self.qiangExmaoHuProcessor.reset()
            if self.curState() == 0:
                self.setCurSeat((self.curSeat - 1) % self.playerCount)
                
        if self.tingBeforeAddCardProcessor.getState() != 0:
            ftlog.debug('playerCancel minglou...')
            if self.tingBeforeAddCardProcessor.updateProcessor(self.actionID, MTableState.TABLE_STATE_NEXT, seatId):
                self.tingBeforeAddCardProcessor.reset()
                self.processAddTile(self.player[seatId])

        if self.louHuProcesssor.getState() != 0:
            ftlog.debug('playerCancel louhu...')
            if self.louHuProcesssor.updateProcessor(self.actionID, MTableState.TABLE_STATE_NEXT, seatId):
                self.louHuProcesssor.reset()

        
    def appendGangFanPattern(self, fanPattern):
        for ri in range(0, len(self.roundResult.roundResults) - 1)[::-1]:
            if self.roundResult.roundResults[ri].results[MOneResult.KEY_TYPE] == MOneResult.KEY_TYPE_NAME_HU:
                # 倒序统计杠牌信息
                break
            else:
                # 本局的杠牌记录
                if MOneResult.KEY_STAT in self.roundResult.roundResults[ri].results:
                    roundStat = self.roundResult.roundResults[ri].results[MOneResult.KEY_STAT]
                    for rsi in range(len(roundStat)):
                        for statItems in roundStat[rsi]:
                            for oneStatItemKey in statItems.keys():
                                if oneStatItemKey == MOneResult.STAT_MINGGANG:
                                    mingGangName = self.roundResult.roundResults[ri].statType[MOneResult.STAT_MINGGANG]["name"]
                                    mingGangFanPattern = [mingGangName, str(1) + "番"]
                                    if mingGangFanPattern not in fanPattern[rsi]:
                                        fanPattern[rsi].append(mingGangFanPattern)
                                        
                                if oneStatItemKey == MOneResult.STAT_ANGANG:
                                    anGangName = self.roundResult.roundResults[ri].statType[MOneResult.STAT_ANGANG]["name"]
                                    anGangFanPattern = [anGangName, str(1) + "番"]
                                    if anGangFanPattern not in fanPattern[rsi]:
                                        fanPattern[rsi].append(anGangFanPattern)

                                if oneStatItemKey == MOneResult.STAT_BaoZhongGANG:
                                    ftlog.info("appendGangFanPattern STAT_BaoZhongGANG:")
                                    GangName = self.roundResult.roundResults[ri].statType[MOneResult.STAT_BaoZhongGANG]["name"]
                                    GangFanPattern = [GangName, str(1) + "番"]
                                    if GangFanPattern not in fanPattern[rsi]:
                                        fanPattern[rsi].append(GangFanPattern)
                                        
                                if oneStatItemKey == MOneResult.STAT_CaiGANG:
                                    ftlog.info("appendGangFanPattern STAT_CaiGANG:")
                                    GangName = self.roundResult.roundResults[ri].statType[MOneResult.STAT_CaiGANG]["name"]
                                    GangFanPattern = [GangName, str(1) + "番"]
                                    if GangFanPattern not in fanPattern[rsi]:
                                        fanPattern[rsi].append(GangFanPattern)
        return fanPattern
        
    def printTableTiles(self):
        """打印牌桌的所有手牌信息"""
        for player in self.player:
            player.printTiles()
        self.tableTileMgr.printTiles()
            
    def refixTableStateByConfig(self):
        """根据自建房配置调整牌桌状态"""
        chipengSetting = self.tableConfig.get(MTDefine.CHIPENG_SETTING, 0)
        ftlog.info("refixTableStateByConfig chipengSetting:", chipengSetting)
        if chipengSetting == MTDefine.NOT_ALLOW_CHI:
            if self.checkTableState(self.tableStater.TABLE_STATE_CHI):
                self.tableStater.clearState(self.tableStater.TABLE_STATE_CHI)
                ftlog.debug("refixTableStateByConfig remove TABLE_STATE_CHI, now chi state =", self.checkTableState(self.__table_stater.TABLE_STATE_CHI))
        elif chipengSetting == MTDefine.ALLOW_CHI:
            if not self.checkTableState(self.tableStater.TABLE_STATE_CHI):
                self.tableStater.setState(self.tableStater.TABLE_STATE_CHI)
                ftlog.debug("refixTableStateByConfig add TABLE_STATE_CHI, now chi state =", self.checkTableState(self.__table_stater.TABLE_STATE_CHI))


        gangSetting = self.tableConfig.get(MTDefine.GANG_SETTING, 0)
        ftlog.info("refixTableStateByConfig gangSetting:", gangSetting)
        if gangSetting == 1:  # can not gang
            if self.checkTableState(self.tableStater.TABLE_STATE_GANG):
                self.tableStater.clearState(self.tableStater.TABLE_STATE_GANG)
                ftlog.info("refixTableStateByConfig gangSetting:gangSetting == 1:#can not gang")
        elif gangSetting == 2:  # can gang
            if not self.checkTableState(self.tableStater.TABLE_STATE_GANG):
                self.tableStater.setState(self.tableStater.TABLE_STATE_GANG)
                ftlog.info("refixTableStateByConfig gangSetting:gangSetting == 2:#can gang")
        ftlog.info("refixTableStateByConfig ", self.checkTableState(self.tableStater.TABLE_STATE_GANG))


        tingSetting = self.tableConfig.get(MTDefine.TING_SETTING, MTDefine.TING_UNDEFINE)
        ftlog.debug('refixTableStateByConfig tingSetting:', tingSetting)
        if tingSetting == MTDefine.TING_YES:
            if not self.checkTableState(MTableState.TABLE_STATE_TING):
                self.tableStater.setState(MTableState.TABLE_STATE_TING)
                self.tingRuleMgr = MTingRuleFactory.getTingRule(self.playMode)
                self.tingRuleMgr.setWinRuleMgr(self.__win_rule_mgr)
                self.tingRuleMgr.setTableTileMgr(self.tableTileMgr)
                ftlog.debug('refixTableStateByConfig add TABLE_STATE_TING...')
        elif tingSetting == MTDefine.TING_NO:
            if self.checkTableState(MTableState.TABLE_STATE_TING):
                self.tableStater.clearState(MTableState.TABLE_STATE_TING)
                ftlog.debug('refixTableStateByConfig clear TABLE_STATE_TING...')

        piaoSetting = self.tableConfig.get(MTDefine.PIAO_SETTING, MTDefine.PIAO_UNDEFINE)
        ftlog.debug('refixTableStateByConfig piaoSetting:', piaoSetting)
        if piaoSetting == MTDefine.PIAO_YES:
            if not self.checkTableState(MTableState.TABLE_STATE_PIAO):
                self.tableStater.setState(MTableState.TABLE_STATE_PIAO)
                ftlog.debug('refixTableStateByConfig add TABLE_STATE_PIAO...')
        elif piaoSetting == MTDefine.PIAO_NO:
            if self.checkTableState(MTableState.TABLE_STATE_PIAO):
                self.tableStater.clearState(MTableState.TABLE_STATE_PIAO)
                ftlog.debug('refixTableStateByConfig clear TABLE_STATE_PIAO...')

        doubleSetting = self.tableConfig.get(MTDefine.DOUBLE_SETTING, MTDefine.DOUBLE_UNDEFINE)
        ftlog.debug('refixTableStateByConfig doubleSetting:', doubleSetting)
        if doubleSetting == MTDefine.DOUBLE_YES:
            if not self.checkTableState(MTableState.TABLE_STATE_DOUBLE):
                self.tableStater.setState(MTableState.TABLE_STATE_DOUBLE)
                ftlog.debug('refixTableStateByConfig add TABLE_STATE_DOUBLE...')
        elif doubleSetting == MTDefine.DOUBLE_NO:
            if self.checkTableState(MTableState.TABLE_STATE_DOUBLE):
                self.tableStater.clearState(MTableState.TABLE_STATE_DOUBLE)
                ftlog.debug('refixTableStateByConfig clear TABLE_STATE_DOUBLE...')

        huanSanZhangSetting = self.tableConfig.get(MTDefine.THREE_TILE_CHANGE, MTDefine.HUANSANZHANG_UNDEFINE)
        ftlog.debug('refixTableStateByConfig huanSanZhangSetting:', huanSanZhangSetting)
        if huanSanZhangSetting == MTDefine.HUANSANZHANG_YES:
            if not self.checkTableState(MTableState.TABLE_STATE_CHANGE_TILE):
                self.tableStater.setState(MTableState.TABLE_STATE_CHANGE_TILE)
                ftlog.debug('refixTableStateByConfig add TABLE_STATE_CHANGE_TILE...')
        elif huanSanZhangSetting == MTDefine.HUANSANZHANG_NO:
            if self.checkTableState(MTableState.TABLE_STATE_CHANGE_TILE):
                self.tableStater.clearState(MTableState.TABLE_STATE_CHANGE_TILE)
                ftlog.debug('refixTableStateByConfig clear TABLE_STATE_CHANGE_TILE...')

        qiangganghu = self.tableConfig.get(MTDefine.QIANGGANGHU, MTDefine.QIANGGANGHU_UNDEFINE)
        ftlog.debug('refixTableStateByConfig QIANGGANGHU:', qiangganghu)
        if qiangganghu == MTDefine.QIANGGANGHU_YES:
            if not self.checkTableState(MTableState.TABLE_STATE_QIANGGANG):
                self.tableStater.setState(MTableState.TABLE_STATE_QIANGGANG)
                ftlog.debug('refixTableStateByConfig add TABLE_STATE_QIANGGANG...')
        elif qiangganghu == MTDefine.QIANGGANGHU_NO:
            if self.checkTableState(MTableState.TABLE_STATE_QIANGGANG):
                self.tableStater.clearState(MTableState.TABLE_STATE_QIANGGANG)
                ftlog.debug('refixTableStateByConfig clear TABLE_STATE_QIANGGANG...')
        
        ftlog.debug('refixTableStateByConfig tableState:', self.tableStater.states)

    def refixTableMultipleByConfig(self):
        """根据传入配置调整输赢倍数"""
        multiple = self.tableConfig.get(MTDefine.MULTIPLE, MTDefine.MULTIPLE_MIN)
        ftlog.info('refixTableMutipleByConfig multiple:', multiple)
        if multiple >= MTDefine.MULTIPLE_MIN and multiple <= MTDefine.MULTIPLE_MAX:
            self.winRuleMgr.setMultiple(multiple)

        # 调整胡牌方式
        winType = self.tableConfig.get(MTDefine.WIN_SETTING, 0)
        ftlog.info('refixTableMutipleByConfig winType:', winType)
        if winType:
            self.winRuleMgr.setWinType(winType)

    def playerLeave(self, seatId):
        player = self.getPlayer(seatId)
        if not player:
            return
        
        player.setOffline()
        
    def playerEnterBackGround(self, seatId):
        self.player[seatId].setBackForeState(MPlayer.BACK_GROUND)
        
    def playerResumeForeGround(self, seatId):
        self.player[seatId].setBackForeState(MPlayer.FORE_GROUND)
        
    def playerOnline(self, seatId):
        player = self.getPlayer(seatId)
        player.setOnline()
        player.setBackForeState(MPlayer.FORE_GROUND)

    def sendPlayerLeaveMsg(self, userId):
        online_info_list = []
        for player in self.player:
            if not player:
                continue
            
            online_info = {}
            online_info['userId'] = player.userId
            online_info['seatId'] = player.curSeatId
            online_info['online'] = player.onlineState
            online_info['state'] = player.backForeState
            online_info_list.append(online_info)
            ftlog.info('leave players info:', online_info)

        self.msgProcessor.table_call_player_leave(online_info_list)

    def sendUserNetState(self, userId, seatId, ping, time):
        ftlog.debug('userNetState:', userId, ping)
        self.playersPing[userId] = ping
        ping_info = [0 for _ in range(self.playerCount)]
        seats = [0 for _ in range(self.playerCount)]
        for index, _ in enumerate(seats):
            if self.players[index]:
                if self.playersPing.has_key(self.players[index].userId) != True:
                    self.playersPing[self.players[index].userId] = 0
                ping_info[index] = self.playersPing[self.players[index].userId]
        self.msgProcessor.table_call_ping(userId, ping_info, time)

    def buFlower(self, seatId, tile):
        """
        补花，怀宁麻将需要人工请求补花
        """
        if not self.tableTileMgr.isFlower(tile):
            return

        cp = self.player[seatId]
        if tile not in cp.handTiles:
            return
        # 执行补花
        cp.actionBuFlower(tile)
        self.msgProcessor.table_call_bu_flower_broadcast(seatId, tile, cp.flowers, self.tableTileMgr.flowerScores(seatId))

        state = MTableState.TABLE_STATE_NEXT
        if self.tableConfig.get(MFTDefine.BU_FLOWER_AS_GANG, 0):
            state |= MTableState.TABLE_STATE_GANG
            cp.curLianGangNum += 1  # 连杠次数+1

        # 摸牌
        self.processAddTile(cp)

    def autoBuFlower(self):
        """
        自动补花
        """
        isBeginGame = self.flowerProcessor.isBegin
        nextSeatId = self.flowerProcessor.seatId
        flower, seatId = self.flowerProcessor.getFlower(self.curSeat)
        if flower and self.tableTileMgr.isFlower(flower):
            cp = self.player[seatId]
            # 执行补花
            cp.actionBuFlower(flower)
            self.tableTileMgr.setFlowerTileInfo(flower, seatId)

            # 累计花分
            cp.addFlowerScores(1)
            self.tableTileMgr.addFlowerScores(1, seatId)
            self.msgProcessor.table_call_bu_flower_broadcast(seatId, flower, cp.flowers, self.tableTileMgr.flowerScores(seatId))
            if isBeginGame:
                self.processAddTileSimple(cp)
            else:
                self.processAddTile(self.player[seatId], None, {"buFlower": 1})
            ftlog.debug('MajiangTableLogic.bu_flower flower:', flower
                        , ' seatId:', seatId
                        , ' handTiles:', cp.handTiles
                        , ' flowers:', cp.flowers)

        # 开局阶段的全体补花完毕
        if self.flowerProcessor.getState() == MTableState.TABLE_STATE_NEXT and isBeginGame:
            self.processAddTile(self.player[nextSeatId])
    
    def changePlayerHandTiles(self, getTiles, removeTiles):
        '''
        玩家要去掉的牌及得到的牌
        '''
        ftlog.debug('MajiangTableLogic.changePlayerHandTiles removeTiles:', removeTiles, 'getTiles:', getTiles)
        for index in range(self.playerCount):
            self.player[index].changeHandTiles(getTiles[index], removeTiles[index])
    
    def huanSanZhangEnd(self):
        """
        判定换三张结束
        """
        if self.huanSanZhangProcessor.getState() == 0:
            self.incrActionId('MajiangTableLogic.huanSanZhangEnd')
            
            for index in range(self.playerCount):
                ftlog.debug("MajiangTableLogic.huanSanZhangEnd player seatId:", index, 'befor handTiles:', self.player[index].handTiles)
                
            self.changePlayerHandTiles(self.huanSanZhangProcessor.afterChangeTiles, self.huanSanZhangProcessor.getTilesFromUser)
            
            for index in range(self.playerCount):
                ftlog.debug("MajiangTableLogic.huanSanZhangEnd player seatId:", index, 'after handTiles:', self.player[index].handTiles)
                
            # 向玩家发送换牌完毕，换牌的情况
            for seatId in xrange(self.playerCount):
                cp = self.players[seatId]
                self.msgProcessor.table_call_huanSanZhang_end(cp.userId
                        , seatId
                        , self.huanSanZhangProcessor.afterChangeTiles[seatId]
                        , self.huanSanZhangProcessor.getTilesFromUser[seatId]
                        , cp.copyHandTiles()
                        , self.huanSanZhangProcessor.randType
                        , self.actionID)

            # 换牌结束后，定缺功能
            self.handleChangeThreeTiles()        
    
    def confirmSanZhang(self, userId, seatId, tiles):
        '''
        换三张
        
        参数：
            seatId: 座位号
            tiles: 当前座位号对应的换三张牌
        '''
        if self.huanSanZhangProcessor.getState() == 0:
            ftlog.debug('MajiangTableLogic.confirmSanZhang state error!!!')
            return
        
        self.huanSanZhangProcessor.setTilesFromUser(seatId, tiles, self.msgProcessor)
        self.huanSanZhangEnd()

    def dingAbsence(self, userId, seatId, color):
        """
        定缺
        
        参数：
            seatId: 座位号
            color: 缺牌颜色
        """
        if self.absenceProcessor.getState() == 0:
            ftlog.debug('MajiangTableLogic.dingAbsence state error!!!')
            return

        self.absenceProcessor.dingAbsence(seatId, color, self.actionID)
        self.handleAbsenceEnd()

    def handleChangeThreeTiles(self):
        """
        换完三张，进行定缺
        """
        mixValueColor = self.getMixValueTilesColor(0)
        self.absenceProcessor.reset()
        self.absenceProcessor.setSuggestColor(mixValueColor)
        self.absenceSchedule()
        # 前端要求：换三张结束，定缺数据立马发给前端，但是也要给前端播放动画的时间
        self.absenceProcessor.onBankerAddedFirstTile(self.actionID, self.pauseProcessor, False)

    def handleAbsenceEnd(self):
        """
        定缺结束处理
        """
        if self.absenceProcessor.getState() != 0:
            return
        
        self.incrActionId('absenceEnd')
        # 现在不处于定缺阶段，表明所有人都已定完缺
        self.tableTileMgr.setAbsenceColors(self.absenceProcessor.absenceColor)
        # 定缺以后 排序玩家授牌
        self.tableTileMgr.sortHandTileColor(self.player)
        # 发送玩家手牌展现顺序
        for seatId in xrange(self.playerCount):
            if self.tableTileMgr.handTileColorSort[seatId]:
                self.msgProcessor.table_call_hand_tile_sort(seatId, self.tableTileMgr.handTileColorSort[seatId])
        # 向玩家广播定缺完毕, 定缺的情况
        banker = self.bankerMgr.queryBanker()
        for seatId in xrange(self.playerCount):
            cp = self.players[seatId]
            if seatId == banker:
                handTiles = copy.deepcopy(self.player[seatId].copyHandTiles())
                handTiles.sort()
                _tile = handTiles[-1]
                # 校正最后一张牌为缺牌的最大牌
                for ht in handTiles:
                    if MTile.getColor(ht) == self.absenceProcessor.absenceColor[seatId]:
                        _tile = ht
                # 通知庄家定缺后的下一步操作，胡/听/杠/出牌
                _state = MTableState.TABLE_STATE_NEXT
                state, exInfo = self.calcAddTileExtendInfo(cp, _state, _tile)
                ftlog.debug('table_logic.processAddTile calcAddTileExtendInfo state:', state
                            , ' exInfo:', exInfo, 'handTiles: ', handTiles)
                self.msgProcessor.table_call_absence_end(cp.userId
                        , seatId
                        , self.absenceProcessor.absenceColor
                        , self.player[seatId]
                        , _tile
                        , False
                        , state
                        , exInfo
                        , self.actionID
                        , banker
                        , 12)
                # 如果庄家手牌中有缺牌发送提示信息 
                if MTile.getTileCountByColor(MTile.changeTilesToValueArr(cp.handTiles), self.absenceProcessor.absenceColor[seatId]) > 0:
                    self.msgProcessor.table_call_show_tips(MTDefine.TIPS_NUM_8, self.players[seatId])
            else:
                # 通知定缺结束
                self.msgProcessor.table_call_absence_end(cp.userId
                        , seatId
                        , self.absenceProcessor.absenceColor
                        , self.player[seatId]
                        , 0
                        , False
                        , 0
                        , None
                        , 0
                        , banker
                        , 12)
                # 非庄家玩家，判断是否可以听牌，听牌更新winNode，并通知前端
                allTiles = cp.copyTiles()
                tingResult, tingReArr = self.tingRule.canTingBeforeAddTile(allTiles, self.tableTileMgr.tiles, self.tableTileMgr.getMagicTiles(cp.isTing()), cp.curSeatId)
                ftlog.debug('MajiangTableLogic.handleAbsenceEnd canTingBeforeAddTile result: ', tingResult, ' solution:', tingReArr, ' length: ', len(tingReArr))
                if tingResult and len(tingReArr) > 0:
                    if not cp.winNodes:
                        winNodes = []
                        for _nodes in tingReArr:
                            winNodes.extend(_nodes['winNodes'])
                            cp.setWinNodes(winNodes)
                    # 通知前端听牌预览消息
                    self.updateTingResult(-1, True, cp.curSeatId)
        
    def getAbsenceColor(self, seatId):
        '''
        获取定缺的颜色
        '''
        return self.absenceProcessor.absenceColor[seatId]
    
    def updateTingResult(self, tile=-1, volatileFlag=False, seatId=-1):
        '''
        更新听牌预览结果，数据还放在player的tingResult中
        在胡牌、过胡、杠牌的时候进行更新，别的情况不会影响
        
        :param tile:当前更新的手牌
        :param volatileFlag:是否实时计算还是直接－1
        :param seatId:玩家座位号
        '''
        # 如果玩家听牌，更新听牌预览信息
        for index in range(self.playerCount):
            if self.players[index].isObserver():
                continue
            if seatId != -1 and self.players[index].curSeatId == seatId:
                continue
            if not self.player[index].tingResult and self.player[index].winNodes:
                tingResult = MTing.calcTingResult(self.player[index].winNodes, index, self.tableTileMgr)
                self.players[index].setTingResult(tingResult)
            ftlog.debug('MajiangTableLogic.updateTingResult tile:', tile, 'tingResult:', self.players[index].tingResult)
            if tile == -1:
                self.msgProcessor.table_call_update_ting_result(self.players[index])
            elif MTing.updateTingResult(self.players[index], tile, self.tableTileMgr, volatileFlag):
                self.msgProcessor.table_call_update_ting_result(self.players[index])
                
    def isUserChipNotEnough(self, seatId):
        '''
        用户身上的金币是否不够在本房间玩儿
        '''
        if self.tableType != MTDefine.TABLE_TYPE_NORMAL:
            return False
        
        if self.roomConfig.get('level', MTDefine.FREE) == MTDefine.FREE:
            # 免费场不弹出充值引导
            return False
        
        return self.chargeProcessor.isUserChipNotEnough(seatId)
    
    def isUserChipMoreThanMax(self, seatId):
        '''
        用户牌桌金币是否超过房间上限
        '''
        if self.tableType != MTDefine.TABLE_TYPE_NORMAL:
            return False
        
        maxCoin = self.roomConfig.get(MTDefine.MAX_COIN, -1)
        maxTableCoin = self.roomConfig.get(MTDefine.MAX_TABLE_COIN, maxCoin)
        ftlog.debug('MajiangTableLogic。isUserChipMoreThanMax maxCoin:', maxCoin, ' maxTableCoin', maxTableCoin)
        
        if maxTableCoin == -1:
            return False
        
        tableCoin = self.players[seatId].getTableCoin(self.gameId, self.tableId)
        return tableCoin > maxTableCoin
    
    def processSmartOperate(self, seatId):
        '''
        用户选择智能提示
        '''
        if not self.player[seatId]:
            return
        self.player[seatId].incrSmartOperateCount()
        self.msgProcessor.table_call_smart_operate(self.player[seatId], self.actionID)
        
if __name__ == "__main__":
    pass
