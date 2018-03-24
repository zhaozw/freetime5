# -*- coding=utf-8
'''
Created on 2016年9月23日

一条和牌结果

@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.player.player import MPlayerTileGang
from majiang2.table.table_config_define import MTDefine

class MOneResult(object):
    '''
    OneResult粒度应该是结算中的每个部分
    之前OneResult结算全部的会导致金币桌金币变化出问题
    '''
    # 杠牌，刮风下雨
    RESULT_GANG = 1
    # 和牌
    RESULT_WIN = 2
    # 流局
    RESULT_FLOW = 3
    # 跟庄
    RESULT_GENZHUANG = 4
    # 呼叫转移
    RESULT_CALLTRAN = 5
    # 退税
    RESULT_TUISHUI = 6
    # 查花猪
    RESULT_HUAZHU = 7
    # 查大叫
    RESULT_DAJIAO = 8
    # 杠牌和胡牌都会产生一个OneResult 在OneResult中存放winMode,番型,统计信息 每局输赢后提供数据给客户端，最后牌桌结束后一起将统计数据提供给客户端
    KEY_TYPE = 'type'  # 杠牌 和牌 
    KEY_NAME = 'name'  # 明杠 暗杠
    KEY_SCORE = 'score'  # 每局的分数(变化部分)统计 [seatId] = value
    KEY_SCORE_TEMP = 'scoreTemp'  # result字段，用户保存临时score
    KEY_WIN_MODE = 'winMode'  # 输赢类型 [seatId] = value
    KEY_FAN_PATTERN = 'fanPattern'  # 番型统计 [seatId] = value
    KEY_FAN_TOTALBEI_PATTERN = 'fanPatternTotalBei'
    KEY_LOSER_FAN_PATTERN = 'loserFanPattern'  # 输家番型 前端要求
    KEY_STAT = 'stat'  # 最后大结算需要的统计数据 [seatId] = value {"desc":"自摸","value":0},{"desc":"点炮","value":0},{"desc":"明杠","value":0},{"desc":"暗杠","value":0},{"desc":"最大番数","value":2}
    KEY_AWARD_INFO = 'awardInfo'
    KEY_AWARD_SCORE = 'awardScore'
    KEY_GANG_STYLE_SCORE = 'gangStyleScore'  # 杠牌时，无论是否放杠，此杠型的分数，返回这个，记录在牌桌上，用于后续处理，如杠上杠、杠上炮算分
    KEY_PIAO_POINTS = 'piaoPoints'  # 玩家各自飘的分
    KEY_FLOWER_SCORES = 'flowerScores'  # 玩家各自花分
    KEY_HORSE = 'horseResult'
    KEY_HORSE_SCORES = 'horseScore'
    
    KEY_GENZHUANG_SCORE = "genZhuangScore"  # 跟庄
    # 对局流水信息（血战麻将）
    KEY_DETAIL_DESC_LIST = 'detailDescList' 
    # detailDescList是一个二维数组 下标 0代表descPattern 1代表fanPatter 2代表score 3代表descId
    # 详细的分数变化
    KEY_DETAIL_CHANGE_SCORES = 'detailChangeScores'
    INDEX_DESCPATTERN = 0
    INDEX_FANPATTERN = 1
    INDEX_SCORE = 2
    INDEX_DESCID = 3
    INDEX_YES = 4  # 是否买中马
    
    # 大胡相关字段
    KEY_DAHU_DETAIL = 'dahuDetail'
    # 胡牌方式 自摸 杠开等
    EXINFO_HU_ACTION = 'huAction'
    # 是否是大胡
    EXINFO_BIGWIN = 'bigWin'
    # 本次番数
    EXINFO_WINFAN = 'winFan'
    # 胡了几次
    EXINFO_WINTIMES = 'winTimes'
    # 鸡平胡
    EXINFO_JIPING_ISWIN = 'jiPingIsWin'
    # 胡牌
    EXINFO_WINTILE = 'winTile'
    
 
    # 保存每一次杠分的 赢家的seatId actionId 及分数列表，以便退税时，进行结算
    KEY_DETAIL_GANG_LIST = 'gangDetailList'

    KEY_DISPLAY_EXTEND = 'displayExtend'  # 显示额外信息，江西安徽使用

    KEY_TYPE_NAME_GANG = '杠牌'
    KEY_TYPE_NAME_HU = '和牌'
    KEY_TYPE_NAME_FLOW = '流局'
    KEY_TYPE_NAME_GEN = '跟庄'
    KEY_TYPE_NAME_CALLTRAN = '呼叫转移'
    KEY_TYPE_NAME_TUISHUI = '退税'
    KEY_TYPE_NAME_HUAZHU = '花猪'
    KEY_TYPE_NAME_DAJIAO = '大叫'
    
    # stat type
    STAT_WIN = 'win'
    STAT_ZIMO = 'ziMO'
    STAT_MOBAO = 'moBao'
    STAT_DIANPAO = 'dianPao'
    STAT_MINGGANG = 'mingGang'
    STAT_XUGAANG = 'xuGang'
    STAT_ANGANG = 'anGang'
    STAT_ZFBGANG = 'zfbGang'
    STAT_YAOJIUGANG = 'yaojiuGang'
    STAT_ExmaoGANG = 'exmaoGang'
    STAT_BaoZhongGANG = 'BaoZhongGang'
    STAT_CaiGANG = 'CaiGang'
    STAT_GANG = 'gang'
    STAT_ZUIDAFAN = 'zuiDaFan'
    STAT_BANKER = 'banker'
    STAT_JIAOPAI = 'jiaopai'
    STAT_MOZI = 'mozi'  # 摸子积分
    STAT_PINGNA = 'pingna'  # 平拿积分
    STAT_QINGNA = 'qingna'  # 清水拿分
    STAT_DANJUZUIJIA = 'danJuZuiJia'
    STAT_GENZHUANG = "genzhuang"  # 跟庄
    STAT_SANYUANPAI = "sanyuanpai" #三元牌
    STAT_FENGQUAN = "fengquan" #风圈
    STAT_FENGWEI = "fengwei" #风刻
    
    # winMode
    WIN_MODE_OBSERVERS = -99  # 观察者 不输不赢
    WIN_MODE_HUJIAOZHUANYI = -7  # 呼叫转移  杠上炮的一种
    WIN_MODE_HAIDIPAO = -6  # 海底炮    
    WIN_MODE_YIPAODUOXIANG = -5  # 一炮多响
    WIN_MODE_GANGSHANGPAO = -4  # 杠上炮
    WIN_MODE_DIANPAO_BAOZHUANG = -3  # 包庄
    WIN_MODE_LOSS = -2  # 输家
    WIN_MODE_DIANPAO = -1  # 点炮
    WIN_MODE_ZIMO = 0  # 自摸
    WIN_MODE_PINGHU = 1  # 胡
    WIN_MODE_GANGKAI = 2  # 杠上开花
    WIN_MODE_QIANGGANGHU = 3  # 抢杠胡
    WIN_MODE_WUDUIHU = 4  # 五对胡
    WIN_MODE_TIANHU = 5  # 天胡
    WIN_MODE_LOUHU = 6  # 漏胡
    WIN_MODE_baozhongbao = 7  # 宝中宝
    WIN_MODE_guadafeng = 8  # 刮大风
    WIN_MODE_hongzhongbao = 9  # 红中宝
    WIN_MODE_mobao = 10  # 摸宝
    WIN_MODE_GENZHUANG = 11  # 跟庄
    WIN_MODE_DIHU = 12  # 地胡
    WIN_MODE_HAIDILAOYUE = 13  # 海底捞月
    WIN_MODE_GANGKAI_HAIDI = 14  # 杠上开花 海底捞月


    def __init__(self, tilePatternChecker, playerCount):
        super(MOneResult, self).__init__()
        self.__tile_pattern_checker = tilePatternChecker
        # 玩家个数
        self.__player_count = playerCount
        self.__result_type = None
        # 玩法
        self.__play_mode = None
        # 庄家座位号
        self.__banker_seat_id = None
        """
        1）自摸 self.__win_seat_id == self.__last_seat_id
        2）点炮 self.__win_seat_id != self.__last_seat_id
        """
        # 获胜一方的桌子号
        self.__win_seat_id = None
        # 获胜的桌子号
        self.__win_seats = None
        # 失败的桌子号
        self.__loose_seats = None
        # 观察的桌子号
        self.__observer_seats = None
        # 上一轮的桌子号
        self.__last_seat_id = None
        
        """通过__table_tile_mgr获取__win_tile是否是宝牌，是否是宝中宝"""
        # 获胜牌
        self.__win_tile = None
        # 牌桌手牌管理器
        self.__table_tile_mgr = None
        # 获胜时的actionID
        self.__action_id = 0
        # 扎鸟的个数
        self.__zha_niao_count = None
        """
        1）通过获胜手牌与获胜手牌组合判断是否是夹牌
        2）通过获胜手牌组合判断是否是大扣等
        """
        # 获胜的手牌组合
        self.__win_pattern = None
        # 仅由获胜牌组合定义的番型，比如九莲宝灯，金钩和，七对等
        self.__win_pattern_type = None
        # style
        self.__style = 0
        # 结果
        self.__results = {}
        # 听牌详情
        self.__win_nodes = None
        # 报警详情
        self.__alarm_nodes = None
        # 杠开
        self.__gang_kai = False
        self.__gang_kai_last_seatId = -1
        self.__gang_kai_seatId = -1
        # 花呲
        self.__hua_ci = False
        # 宝中宝 上听后手里的刻牌为宝牌的情况
        self.__bao_zhong_bao = False
        # 听牌之后是宝牌时直接和牌
        self.__magic_after_ting = False
        # 宝牌
        self.__magics = None
        # 天胡(鸡西)
        self.__tian_hu = False
        # 无对胡(鸡西)
        self.__wu_dui_hu = False
        # 抢杠
        self.__qiang_gang = False
        # 牌桌配置
        self.__table_config = None
        # 门清状态
        self.__men_state = None
        # 听牌状态 'tingState': [0, 0, 0, 0]
        self.__ting_state = None
        # 明牌状态
        self.__ming_state = None
        # 花色状态 demo 'colorState': [1, 3, 3, 3]
        self.__color_state = None
        # 字牌状态 [[0,4,1,2,3,1,2],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]
        # 4个玩家手上的字牌,数字代表31到37七张牌的张数
        self.__zi_state = None
        # 大风
        self.__da_feng = None
        # 大扣
        self.__da_kou = None
        self.__win_fan_pattern = []
        # 所有玩家的所有牌，按手牌格式的数组
        self.__player_all_tiles = []
        # 所有玩家的所有牌，合到一个数组
        self.__player_all_tiles_arr = []
        # 所有玩家手牌
        self.__player_hand_tiles = []
        # 所有玩家杠牌情况
        self.__player_gang_tiles = []
        # 飘处理器
        self.__piao_processor = None
        # 交牌积分规则
        self.__jiaopai_conf = None
        # 番型积分规则
        self.__fan_rule_conf = None
        # 玩家当前积分
        self.__cur_player_score = []
        # 玩家是否加倍
        self.__double_points = []
        # 当前局数
        self.__round_index = 0
        # 当前quan数
        self.__quan_index = 0
        # 花猪大叫id集合
        self.__huaZhuDaJiaoId = []
        # 是否为大胡
        self.__da_hu_result = False
        # 延时时间，玩法自定义延时时间
        self.__delay_time = 0

        self.__stat_type = {
            self.STAT_WIN: {"name":"胡牌"},
            self.STAT_ZIMO: {"name":"自摸"},
            self.STAT_MOBAO: {"name":"摸宝"},
            self.STAT_DIANPAO: {"name":"点炮"},
            self.STAT_MINGGANG: {"name": "明杠"},
            self.STAT_ANGANG: {"name": "暗杠"},
            self.STAT_BaoZhongGANG: {"name": "宝中杠"},
            self.STAT_CaiGANG: {"name": "彩杠"},
            self.STAT_GANG: {"name": "杠牌"},
            self.STAT_ZUIDAFAN: {"name": "最大倍数"},
            self.STAT_BANKER: {"name": "坐庄"},
            self.STAT_JIAOPAI: {"name": "交牌计分"},
            self.STAT_MOZI: {"name": "摸子积分"},
            self.STAT_PINGNA: {"name": "平拿积分"},
            self.STAT_QINGNA: {"name": "清水拿分"},
            self.STAT_DANJUZUIJIA: {"name", "单局最佳"},
            self.STAT_GENZHUANG: {"name", "跟庄"}
        }
        
        # 倍数
        self.__multiple = 1
        # 杠牌上家的座位号,－1表示上家没杠牌
        self.__latest_gang_seatId = -1
        # 是否出牌胡,曲靖特殊胡,此时获胜牌型显示的是打出的牌
        self.__drop_hu_flag = 0
        # 抽奖用的牌(根据配置，多张)
        self.__award_tiles = []
        # 赢规则管理器
        self.__win_rule_mgr = None
        # 金币分
        # 保存本局所有的杠分，在退税时候结算
        self.__gang_detaile = []
        # 保存当局玩家
        self.__players = [ None for _ in range(self.playerCount)]
           
        self.__baopeiSeatId = -1
        self.__table_type = MTDefine.TABLE_TYPE_NORMAL
        # 保存上一个的OneResult，点杠开包庄，呼叫转移 退税等使用
        self.__latestOneResult = None

    @property
    def latestOneResult(self):
        return self.__latestOneResult

    def setLatestOneResult(self, latestResult):
        self.__latestOneResult = latestResult

    @property
    def delayTime(self):
        return self.__delay_time
    
    def setDealyTime(self, time):
        self.__delay_time = time

    @property
    def tilePatternChecker(self):
        return self.__tile_pattern_checker
    
    def setTilePatternChecker(self, checker):
        self.__tile_pattern_checker = checker
    
    @property
    def huaZhuDaJiaoId(self):
        return self.__huaZhuDaJiaoId
    
    @property
    def isDaHuResult(self):
        return self.__da_hu_result

    def setDaHuResult(self):
        '''
        默认值为False
        True 表示大胡结算，扣除服务费使用
        '''
        self.__da_hu_result = True

    @property
    def players(self): 
        return self.__players
    
    def setPlayers(self, players):
        self.__players = players
        
    @property
    def tableType(self):
        return self.__table_type
    
    def setTableType(self, tableType):
        ftlog.debug('MOneResult.setTableType:', tableType)
        self.__table_type = tableType
        
    @property
    def roundIndex(self):
        return self.__round_index
    
    def setRoundIndex(self, roundIndex):
        self.__round_index = roundIndex

    @property
    def quanIndex(self):
        return self.__quan_index

    def setQuanIndex(self, quanIndex):
        self.__quan_index = quanIndex
    
    @property
    def baopeiSeatId(self):
        return self.__baopeiSeatId
    
    @property
    def doublePoints(self):
        return self.__double_points
    
    def setDoublePoints(self, points):
        self.__double_points = points

    @property
    def piaoProcessor(self):
        return self.__piao_processor
    
    def setPiaoProcessor(self, piaoProcessor):
        self.__piao_processor = piaoProcessor
        
    def isResultOK(self):
        return (self.KEY_TYPE in self.results) and (self.KEY_SCORE in self.results)
    
    @property
    def awardTiles(self):
        return self.__award_tiles
    
    def setAwardTiles(self, awardTiles):
        self.__award_tiles = awardTiles
    
    def isGameOver(self):
        return True
    
    @property
    def dropHuFlag(self):
        return self.__drop_hu_flag
    
    def setDropHuFlag(self, flag):
        self.__drop_hu_flag = flag
    
    @property
    def latestGangSeatId(self):
        return self.__latest_gang_seatId
    
    def setLatestGangSeatId(self, seatId=-1):
        '''
        设置杠的seatId，如果有则为杠上炮、杠上花
        :param seatId:默认为-1
        '''
        # ftlog.debug('MOneResult.setLatestGangSeatId oldSeatId:', self.latestGangSeatId, 'newSeatId:', seatId)
        self.__latest_gang_seatId = seatId
        
    @property
    def multiple(self):
        return self.__multiple
    
    def setMultiple(self, playerMultiple):
        self.__multiple = playerMultiple
            
    @property
    def statType(self):
        return self.__stat_type
    
    @property
    def winFanPattern(self):
        return self.__win_fan_pattern
        
    def clearWinFanPattern(self):
        self.__win_fan_pattern = []
        
    def addWinFanPattern(self, name, index):
        self.__win_fan_pattern.append([name.strip(), str(index) + "番"])

    @property
    def winRuleMgr(self):
        return self.__win_rule_mgr

    def setWinRuleMgr(self, winRuleMgr):
        self.__win_rule_mgr = winRuleMgr

    def serialize(self):
        """序列化"""
        obj = {}
        if self.playMode:
            obj['playMode'] = self.playMode
        if self.bankerSeatId:
            obj['bankerSeatId'] = self.bankerSeatId
        if self.winSeatId:
            obj['winSeatId'] = self.winSeatId
        if self.winSeats:
            obj['winSeats'] = self.winSeats
        if self.lastSeatId:
            obj['lastSeatId'] = self.lastSeatId
        if self.winTile:
            obj['winTile'] = self.winTile
        if self.actionID:
            obj['actionID'] = self.actionID
        if self.zhaNiaoCount:
            obj['zhaNiaoCount'] = self.zhaNiaoCount
        if self.winPattern:
            obj['winPattern'] = self.winPattern
        if self.winPatternType:
            obj['winPatternType'] = self.winPatternType
        if self.playerCount:
            obj['playCount'] = self.playerCount
        if self.style:
            obj['style'] = self.style
        if self.winNodes:
            obj['winNodes'] = self.winNodes
        if self.huaCi:
            obj['huaCi'] = self.huaCi
        if self.gangKai:
            obj['gangKai'] = self.gangKai
        if self.baoZhongBao:
            obj['baoZhongBao'] = self.baoZhongBao
        if self.qiangGang:
            obj['qiangGang'] = self.qiangGang
        if self.tableConfig:
            obj['tableConfig'] = self.tableConfig
        if self.menState:
            obj['menState'] = self.menState
        if self.tingState:
            obj['tingState'] = self.tingState
        if self.colorState:
            obj['colorState'] = self.colorState
        if self.daFeng:
            obj['daFeng'] = self.daFeng
        if self.daKou:
            obj['daKou'] = self.daKou
        if self.magics:
            obj['magics'] = self.magics
        if self.alarmNodes:
            obj['alarmNodes'] = self.alarmNodes
        if self.jiaoPaiConf:
            obj['jiaoPaiConf'] = self.jiaoPaiConf
        if self.fanRuleConf:
            obj['fanRuleConf'] = self.fanRuleConf
        if self.playerCurScore:
            obj['playerCurScore'] = self.playerCurScore
        if self.playerAllTiles:
            obj['playerAllTiles'] = self.playerAllTiles
        if self.tableTileMgr:
            obj['tableTileMgr_absenceColors'] = self.tableTileMgr.absenceColors
        if self.gangKai:
            obj['gangKai'] = self.gangKai
        if self.qiangGang:
            obj['qiangGang'] = self.qiangGang
        
        ftlog.debug('MOneResult.serialize: ', obj)
        
    def unSerialize(self, obj):
        """反序列化"""
        ftlog.debug('MOneResult.unSerialize: ', obj)
        self.__play_mode = obj.get('playMode', None)
        self.__banker_seat_id = obj.get('bankerSeatId', None)
        self.__win_seat_id = obj.get('winSeatId', None)
        self.__last_seat_id = obj.get('lastSeatId', None)
        self.__win_tile = obj.get('winTile', 0)
        self.__action_id = obj.get('actionID', 0)
        self.__zha_niao_count = obj.get('zhaNiaoCount', 0)
        self.__win_pattern = obj.get('winPattern', [])
        self.__win_pattern_type = obj.get('winPatternType', 0)
        self.__player_count = obj.get('playCount', 4)
        self.__style = obj.get('style', 0)
        self.__win_nodes = obj.get('winNodes', None)
        self.__alarm_nodes = obj.get('alarmNodes', None)
        self.__jiaopai_conf = obj.get('jiaoPaiConf', None)
        self.__fan_rule_conf = obj.get('fanRuleConf', None)
        self.__hua_ci = obj.get('huaCi', False)
        self.__gang_kai = obj.get('gangKai', False)
        self.__gang_kai_last_seatId = obj.get('gangKaiLastSeatId', -1)
        self.__gang_kai_seatId = obj.get('gangKaiSeatId', -1)
        self.__bao_zhong_bao = obj.get('baoZhongBao', False)
        self.__magic_after_ting = obj.get('magicAfertTing', False)
        self.__magics = obj.get('magics', None)
        self.__tian_hu = obj.get('tianHu', False)
        self.__wu_dui_hu = obj.get('wuDuiHu', False)
        self.__qiang_gang = obj.get('qiangGang', False)
        self.__table_config = obj.get('tableConfig', None)
        self.__men_state = obj.get('menState', None)
        self.__ting_state = obj.get('tingState', None)
        self.__color_state = obj.get('colorState', None)
        self.__da_feng = obj.get('daFeng', False)
        self.__da_Kou = obj.get('daKou', False)
        self.__cur_player_score = obj.get('playerCurScore', [])
        self.__double_points = obj.get('doublePoints', [])

    @property
    def playerCount(self):
        return self.__player_count
    
    def setPlayerCount(self, count):
        self.__player_count = count
    
    @property
    def daFeng(self):
        return self.__da_feng
    
    def setDaFeng(self, daFeng):
        self.__da_feng = daFeng
        
    @property
    def daKou(self):
        return self.__da_feng
    
    def setDaKou(self, daKou):
        self.__da_kou = daKou
        
    @property
    def colorState(self):
        return self.__color_state
    
    def setColorState(self, color):
        self.__color_state = color
        
    @property
    def tingState(self):
        return self.__ting_state
    
    def setTingState(self, ting):
        self.__ting_state = ting
    
    @property
    def ziState(self):
        return self.__zi_state
    
    def setZiState(self, zi):
        self.__zi_state = zi    
    @property
    def menState(self):
        return self.__men_state
        
    def setMenState(self, men):
        self.__men_state = men

    @property
    def mingState(self):
        return self.__ming_state
        
    def setMingState(self, ming):
        self.__ming_state = ming

    
    @property
    def playerAllTiles(self):
        return self.__player_all_tiles
        
    def setPlayerAllTiles(self, playerAllTiles):
        self.__player_all_tiles = playerAllTiles
    
    @property
    def playerGangTiles(self):
        return self.__player_gang_tiles
        
    def setPlayerGangTiles(self, playerGangTiles):
        self.__player_gang_tiles = playerGangTiles

    @property
    def tableConfig(self):
        return self.__table_config
    
    def setTableConfig(self, config):
        self.__table_config = config

    @property
    def huaCi(self):
        return self.__hua_ci

    def setHuaCi(self, huaCi):
        self.__hua_ci = huaCi

    @property
    def gangKai(self):
        return self.__gang_kai
    
    def setGangKai(self, gangKai):
        self.__gang_kai = gangKai
        
    @property
    def gangKaiLastSeatId(self):
        return self.__gang_kai_last_seatId
    
    def setGangKaiLastSeatId(self, gangKaiLastSeatId):
        self.__gang_kai_last_seatId = gangKaiLastSeatId
        
    @property
    def gangKaiSeatId(self):
        return self.__gang_kai_seatId
    
    def setGangKaiSeatId(self, gangKaiSeatId):
        self.__gang_kai_seatId = gangKaiSeatId
        
    @property
    def baoZhongBao(self):
        return self.__bao_zhong_bao
    
    def setBaoZhongBao(self, baoZhongBao):
        self.__bao_zhong_bao = baoZhongBao 
        
    @property
    def magicAfertTing(self):
        return self.__magic_after_ting
    
    def setMagicAfertTing(self, magicAfertTing):
        self.__magic_after_ting = magicAfertTing
        
    @property
    def magics(self):
        return self.__magics
    
    def setMagics(self, magics):
        self.__magics = magics
        
    @property
    def tianHu(self):
        return self.__tian_hu
    
    def setTianHu(self, tianHu):
        self.__tian_hu = tianHu
        
    @property
    def wuDuiHu(self):
        return self.__wu_dui_hu
    
    def setWuDuiHu(self, wuDuiHu):
        self.__wu_dui_hu = wuDuiHu
        
    @property
    def qiangGang(self):
        return self.__qiang_gang
    
    def setQiangGang(self, qiangGang):
        self.__qiang_gang = qiangGang

    @property
    def winNodes(self):
        return self.__win_nodes
    
    def setWinNodes(self, wNodes):
        self.__win_nodes = wNodes

    @property
    def alarmNodes(self):
        return self.__alarm_nodes

    def setAlarmNodes(self, wNodes):
        self.__alarm_nodes = wNodes

    @property
    def jiaoPaiConf(self):
        return self.__jiaopai_conf

    def setJiaoPaiConf(self, ruleConf):
        self.__jiaopai_conf = ruleConf

    @property
    def fanRuleConf(self):
        return self.__fan_rule_conf

    def setFanRuleConf(self, ruleConf):
        self.__fan_rule_conf = ruleConf

    @property
    def playerCurScore(self):
        return self.__cur_player_score

    def setPlayerCurScore(self, score):
        self.__cur_player_score = score

    @property
    def results(self):
        return self.__results
    
    def setStyle(self, style):
        self.__style = style
        
    @property
    def style(self):
        return self.__style 
    
    def setZhaNiaoCount(self, count):
        """设置扎鸟的个数"""
        self.__zha_niao_count = count
        
    @property
    def zhaNiaoCount(self):
        return self.__zha_niao_count
        
    def setResultType(self, rType):
        """设置结算类型"""
        self.__result_type = rType
        
    @property
    def resultType(self):
        return self.__result_type
        
    def setActionID(self, actionId):
        """设置操作号"""
        self.__action_id = actionId
    
    @property    
    def actionID(self):
        return self.__action_id
        
    def setBankerSeatId(self, seatId):
        """设置庄家座位号"""
        self.__banker_seat_id = seatId
        
    @property
    def bankerSeatId(self):
        return self.__banker_seat_id
        
    def setPlayMode(self, mode):
        """设置玩法"""
        self.__play_mode = mode
        
    @property
    def playMode(self):
        return self.__play_mode
        
    def setWinSeatId(self, seatId):
        """赢家座位号"""
        self.__win_seat_id = seatId
        
    @property
    def winSeatId(self):
        return self.__win_seat_id

    def setWinSeats(self, seats):
        """赢家座位号"""
        self.__win_seats = seats
        
    @property
    def winSeats(self):
        return self.__win_seats
    
    @property
    def looseSeats(self):
        return self.__loose_seats
    
    def setLooseSeats(self, seats):
        self.__loose_seats = seats
        
    @property
    def observerSeats(self):
        return self.__observer_seats
    
    def setObserverSeats(self, seats):
        self.__observer_seats = seats
        
    def setLastSeatId(self, seatId):
        """上家座位号"""
        self.__last_seat_id = seatId
        
    @property
    def lastSeatId(self):
        return self.__last_seat_id
        
    def setWinTile(self, wTile):
        """设置获胜手牌"""
        self.__win_tile = wTile
        
    @property
    def winTile(self):
        return self.__win_tile
     
    def setTableTileMgr(self, tableTileMgr):
        """设置手牌管理器"""
        self.__table_tile_mgr = tableTileMgr
     
    @property   
    def tableTileMgr(self):
        return self.__table_tile_mgr 
        
    def setWinPattern(self, pattern):
        """设置赢牌手牌组合"""
        self.__win_pattern = pattern

    @property
    def winPattern(self):
        return self.__win_pattern
        
    def setWinPatternType(self, wType):
        """原始番型"""
        self.__win_pattern_type = wType
        
    @property
    def winPatternType(self):
        return self.__win_pattern_type

    def calcGang(self):
        """计算杠的输赢"""
        
        # 明杠暗杠统计
        resultStat = [[] for _ in range(self.playerCount)]
        
        self.__results[self.KEY_TYPE] = MOneResult.KEY_TYPE_NAME_GANG
        base = self.tableConfig.get(MTDefine.GANG_BASE, 0)
        if self.style == MPlayerTileGang.AN_GANG:
            self.__results[self.KEY_NAME] = "暗杠"
            base *= 2
            resultStat[self.winSeatId].append({MOneResult.STAT_ANGANG:1})
        else:
            self.__results[self.KEY_NAME] = "明杠"
            resultStat[self.winSeatId].append({MOneResult.STAT_MINGGANG:1})
        resultStat[self.winSeatId].append({MOneResult.STAT_GANG:1})
         
        if self.lastSeatId != self.winSeatId:  # 放杠
            scores = [0 for _ in range(self.playerCount)]
            scores[self.lastSeatId] = -base
            scores[self.winSeatId] = base
        else:
            scores = [-base for _ in range(self.playerCount)]
            scores[self.winSeatId] = (self.playerCount - 1) * base
        
        ftlog.debug('MOneResult.calcGang gangType:', self.__results[self.KEY_NAME], ' scores', scores)
        self.__results[self.KEY_SCORE] = scores
        self.__results[self.KEY_STAT] = resultStat
    
    def calcWin(self):
        """计算和牌的输赢"""
        '''
        由于金币桌金币结算需要根据玩家的自身金币数量有关，所以金币桌的score数组形式与自建桌不一样。
        比如自建桌score如果是[3，-1，-1，-1]
        '''
        pass

    def calcGenzhuang(self):
        """计算跟庄的分数"""
        pass

        
    def calcScore(self):
        """计算输赢数值"""
        pass
    
    def getBaseChip(self):
        ftlog.debug('MSiChuanOneResult.getBaseChip tableType:', self.tableType, 'base_chip:', self.tableConfig.get(MTDefine.BASE_CHIP, 1))
        if self.tableType == MTDefine.TABLE_TYPE_CREATE:
            return 1
        
        if self.tableType == MTDefine.TABLE_TYPE_NORMAL:
            return self.tableConfig.get(MTDefine.BASE_CHIP, 1)
        # todo, match
        return 1
    
    def isGangShangHua(self, winId):
        '''
        根据latestGangSeatId来判断
        1) latestGangSeatId为-1，则上一个动作没有杠
        2) latestGangSeatId、winId 相等，为杠上花
        3) latestGangSeatId、lastSeatId相等，为杠上炮
        '''
        ftlog.debug('MOneResult.isGangShangHua winId:', winId
                        , 'latestGangSeatId:', self.latestGangSeatId)
        if self.latestGangSeatId != -1 and self.latestGangSeatId == winId:
            ftlog.debug('MOneResult.isGangShangHua True')
            return True
        else:
            ftlog.debug('MOneResult.isGangShangHua False')
            return False
        
    def isGangShangPao(self, winId):
        ftlog.debug('MOneResult.isGangShangHua winId:', winId
                        , 'latestGangSeatId:', self.latestGangSeatId)
        if self.latestGangSeatId != -1  \
                and self.latestGangSeatId == self.lastSeatId \
                and self.lastSeatId != winId:
            ftlog.debug('MOneResult.isGangShangPao True')
            return True
        else:
            ftlog.debug('MOneResult.isGangShangPao False')
            return False

