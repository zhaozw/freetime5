# -*- coding=utf-8
'''
Created on 2016年9月23日
麻将核心玩法中用到的玩家对象
@author: zhaol
'''
import copy

from freetime5.util import ftlog
from majiang2.ai.play_mode import MPlayMode
from majiang2.player.hand.hand import MHand
from majiang2.table.table_config_define import MTDefine
from majiang2.table_state.state import MTableState
from majiang2.table_tile.table_tile import MTableTile
from majiang2.tile.tile import MTile
from majiang2.win_rule.win_rule import MWinRule
from majiang2.poker2.entity import hallrpcutil
from tuyoo5.core import tyconfig


class MPlayerTileMao(object):
    """锚牌"""
    def __init__(self, pattern, actionId, maoDanType):
        super(MPlayerTileMao, self).__init__()
        self.__pattern = pattern
        self.__actionId = actionId
        self.__mao_type = maoDanType
        
    def copyData(self):
        data = {}
        data['pattern'] = self.pattern
        data['type'] = self.maoType
        data['action_id'] = self.actionId
        return data
    
    def extendTile(self, tile):
        self.pattern.append(tile)
        
    @property
    def actionId(self):
        return self.__actionId
    
    def setActionId(self, actionId):
        self.__actionId = actionId
        
    @property
    def pattern(self):
        return self.__pattern
    
    def setPattern(self, pattern):
        self.__pattern = pattern
        
    @property
    def maoType(self):
        return self.__mao_type
    
    def setMaoType(self, maoType):
        self.__mao_type = maoType
        
class MPlayerTileChi(object):
    """玩家手牌的吃牌"""
    def __init__(self, tile, pattern, actionId, fromSeat):
        super(MPlayerTileChi, self).__init__()
        self.__tile = tile
        self.__pattern = pattern 
        self.__actionId = actionId
        self.__from_seat = fromSeat
        
    @property
    def tile(self):
        return self.__tile
    
    @property
    def pattern(self):
        return self.__pattern
    
    @property
    def actionID(self):
        return self.__actionId
    
    @property
    def fromSeat(self):
        return self.__from_seat
    
    def setPattern(self, newPattern):
        """设置吃牌组"""
        self.__pattern = newPattern
        
class MPlayerTilePeng(object):
    """玩家手牌的吃牌"""
    def __init__(self, tile, pattern, actionId, fromSeat):
        super(MPlayerTilePeng, self).__init__()
        self.__tile = tile
        self.__pattern = pattern 
        self.__actionId = actionId
        self.__from_seat = fromSeat
        
    @property
    def tile(self):
        return self.__tile
    
    @property
    def pattern(self):
        return self.__pattern
    
    @property
    def actionID(self):
        return self.__actionId
    
    @property
    def fromSeat(self):
        return self.__from_seat

    def setPattern(self, newPattern):
        """设置牌组"""
        self.__pattern = newPattern
    

class MPlayerTileGang(object):
    MING_GANG = 1
    AN_GANG = 0
    ZFB_GANG = 2
    YAOJIU_GANG = 3
    EXMao_GANG = 4
    GEN_ZHUANG = 5
    CHAOTIANXIAO_MING = 6  # 明杠朝天笑
    CHAOTIANXIAO_AN = 7  # 暗杠朝天笑
    BaoZhong_MING_GANG = 8
    BaoZhong_AN_GANG = 9
    """玩家手牌的吃牌"""
    def __init__(self, tile, pattern, actionId, style, fromSeat):
        super(MPlayerTileGang, self).__init__()
        self.__tile = tile
        self.__pattern = pattern 
        self.__actionId = actionId
        self.__gang_style = style
        self.__gang_style_score = None
        self.__from_seat = fromSeat
     
    def isMingGang(self):
        """是否明杠"""
        return self.__gang_style == self.MING_GANG
        
    @property
    def tile(self):
        return self.__tile
    
    @property
    def pattern(self):
        return self.__pattern
    
    def setPattern(self, pattern):
        """设置碰牌组"""
        self.__pattern = pattern
    
    @property
    def actionID(self):
        return self.__actionId 
    
    @property
    def style(self):
        return self.__gang_style

    @property
    def styleScore(self):
        return self.__gang_style_score
    
    @property
    def fromSeat(self):
        return self.__from_seat

    def setStyleScore(self, score):
        """设置分数，这个是按照杠型计算的分数，与赔付关系无关"""
        self.__gang_style_score = score

class MPlayerTileAlarm(object):
    QINGORHUN_ALARM = 1  # 清一色或混一色报警
    DOUBLEEIGHT_ALARM = 2  # 双八支报警
    DOUBLEFOUR_ALARM = 3  # 双四核报警

    """
    玩家报警信息： 存储每个玩家报警的方式，可能由多个
    记录每个碰对应出牌人的id，碰影响结算，如果结算时没有1的报警，可忽略pattern
    """
    def __init__(self, tile, pattern, style):
        super(MPlayerTileAlarm, self).__init__()
        self.__tile = tile
        self.__pattern = pattern  # [{"pattern":[1,1,1],"seatId":1}]
        self.__alarm_style = style

    @property
    def tile(self):
        return self.__tile

    @property
    def pattern(self):
        return self.__pattern

    @property
    def style(self):
        return self.__alarm_style

    def setPattern(self, pattern):
        """设置碰牌组"""
        self.__pattern = pattern

class MPlayer(object):
    """
    麻将的玩家类
    本类主要描述一下几种信息
    1）玩家的个人信息，包括姓名，性别，userId，积分等等
    2）手牌，包括握在手里的牌，吃牌，碰牌，杠牌
    3）打牌行为的响应，是否吃牌，是否碰牌，是否杠牌，是否胡牌，是否过胡翻倍
    """
    
    """玩家游戏状态，只关心用户的游戏状态，用户的准备状态由继承框架TYTable的MajiangTable来处理
    """

    # 用户刚坐下，需要点击准备按钮
    PLAYER_STATE_NORMAL = 'sit'
    # 用户已准备
    PLAYER_STATE_READY = 'ready'
    # 用户在游戏中
    PLAYER_STATE_PLAYING = 'play'
    # 特殊的游戏状态，听牌状态
    PLAYER_STATE_TING = 'ting'
    # 特殊的游戏状态，明牌状态
    PLAYER_STATE_MING = 'ming'
    # 特殊的游戏状态，用户已经和牌
    PLAYER_STATE_WON = 'win'
    # 离开
    PLAYER_STATE_LEAVE = 'leave'
    # 认输
    PLAYER_STATE_CONFIRM_LOOSE = 'confirm_loose'
    # 前台
    FORE_GROUND = 1
    # 后台
    BACK_GROUND = 0

    
    def __init__(self, name, sex, userId, score, purl='', coin=0, tablecoin=0, clientId='', playMode='', pluginVer=5.01):
        super(MPlayer, self).__init__()
        ftlog.debug('MPlayer init name:', name, 'sex:', sex, 'userId:', userId, 'score:', score
                            , 'coin:', coin, 'tableCoin:', tablecoin, 'purl:', purl, 'clientId:', clientId, 'playMode:', playMode, 'pluginVer:', pluginVer)
        # 1 姓名
        self.__name = name
        # 2 性别
        self.__sex = sex
        self.__purl = purl
        self.__coin = coin
        self.__table_coin = tablecoin
        # 3 用户ID
        self.__userId = userId
        self.__clientId = clientId
        # 玩家插件版本号
        self.__plugin_ver = pluginVer
        # 5 手牌
        self.__hand_tiles = []
        # 6 吃牌
        self.__chi_tiles = []
        # 7 碰牌
        self.__peng_tiles = []
        # 8 杠牌
        self.__gang_tiles = []
        # 9 报警
        self.__alarm_info = []
        # 这个与上面的区别是存的是字典，包括打牌的人id，如果碰被杠了，不影响该数组{"pattern":[1,1,1],"seatId":1}
        self.__peng_tiles_for_alarm = []
        # 10 和牌，血流有多次胡牌的设计
        self.__hu_tiles = []
        # 胡牌的 牌的相关ID，与__hu_tiles 相对应
        self.__hu_tiles_seatId = []
        # 粘牌 鸡西玩法 粘之后存储在player中 下发协议时用来塞选手牌
        self.__zhan_tiles = []
        # 听牌同时亮牌，需要等待杠的牌，扣下来
        self.__kou_tiles = []
        # 听牌同时亮牌，亮牌列表
        self.__ting_liang_tiles = []
        # 放锚的牌
        self.__mao_tiles = []
        # 11 状态
        self.__state = self.PLAYER_STATE_NORMAL
        # 12 当前手牌
        self.__cur_tile = 0
        # 13 座位号
        self.__cur_seat_id = -1
        # 15 托管
        self.__auto_decide = False
        self.__time_out_count = 0
        # 听牌方案
        self.__win_nodes = []
        # 听牌同时亮牌，操作id
        self.__ting_liang_actionId = None
        # 听牌同时亮牌，要胡的牌，同时也是其他人不能打牌
        self.__ting_liang_winTiles = []
        # 用户离线状态
        self.__online_state = 1
        # 用户离开状态
        self.__back_fore_state = 1
        # 花牌
        self.__flowers = []
        # 花分
        self.__flower_scores = 0
        # 过碰的哪些牌，过碰期间的牌不可再碰
        self.__guo_peng_tiles = set()
        # 过胡分数，过胡期间需要出现分数更大的番才能胡
        self.__guo_hu_point = -1
        # 连杠次数
        self.__lian_gang_nums = set()  # 曾经的多次连杠次数
        self.__cur_lian_gang_num = -1  # 当前连杠次数
        # 能胡牌时，胡牌番型
        self.__winTypes = []
        # 能胡牌时，胡牌附加分类型
        self.__winExtendTypes = []
        # 能胡牌时，胡牌分数点集合
        self.__winPoints = []  # 怀宁：花，明杠，暗杠，连杠，明杠风，暗杠风，胡分数
        self.__totalWinPoint = 0  # 总的可胡牌分
        self.__penaltyPoints = []  # 胡牌时，额外的对恶意喂牌行为的惩罚分点。按座位id从0，1，2，3
        # 打出过的牌数
        self.__dropNum = 0
        # 听牌结果
        self.__ting_result = []
        self.__ishuAll = False
        # 玩法
        self.__play_mode = playMode
        # 是否托管过
        self.__is_have_time_out = False
        # 提示玩家缺牌的次数
        self.__show_tips_que_times = 0
        # 一炮多响牌保存，保存的是牌的玩家胡牌中的位置
        self.__multi_win_tiles = []
        # 智能提示次数
        self.__smart_operate_count = 0
        # 换牌
        self.__change_tiles = []
        # 换牌的方向
        self.__change_tiles_model = 0
        # 玩家的超时时间
        self.__ready_time_out = -1
        

    def reset(self):
        """重置
        """
        self.__hand_tiles = []
        self.__chi_tiles = []
        self.__peng_tiles = []
        self.__gang_tiles = []
        self.__alarm_info = []
        self.__hu_tiles = []
        self.__hu_tiles_seatId = []
        self.__zhan_tiles = []
        self.__kou_tiles = []
        self.__mao_tiles = []
        self.__state = self.PLAYER_STATE_NORMAL
        self.__auto_decide = False
        self.__time_out_count = 0
        self.__cur_tile = 0
        self.__win_nodes = []
        self.__ting_liang_tiles = []
        self.__ting_liang_actionId = None
        self.__ting_liang_winTiles = []
        self.__flowers = []
        self.__flower_scores = 0
        self.resetGuoPengTiles()
        self.resetGuoHuPoint()
        self.resetLianGangData()
        self.resetWinTypes()
        self.resetWinExtendTypes()
        self.resetWinPoints()
        self.resetTotalWinPoint()
        self.__penaltyPoints = []
        self.__peng_tiles_for_alarm = []
        self.__dropNum = 0
        self.__ting_result = []
        self.__ishuAll = False
        self.__liangMode = 1
        self.__is_have_time_out = False
        self.__show_tips_que_times = 0
        self.__multi_win_tiles = []
        self.__smart_operate_count = 0
        self.__change_tiles = []
        self.__change_tiles_model = 0
        self.__ready_time_out = -1
    
    @property
    def pluginVer(self):
        return self.__plugin_ver
    
    @property
    def readyTimeOut(self):
        return self.__ready_time_out
    
    def setReadyTimeOut(self, timeOut):
        self.__ready_time_out = timeOut
    
    @property
    def changeTiles(self):
        return self.__change_tiles
    
    def setChangeTiles(self, tiles):
        self.__change_tiles = tiles
    
    @property
    def changeTilesModel(self):
        return self.__change_tiles_model
    
    def setChangeTilesModel(self, model):
        self.__change_tiles_model = model
        
    
    @property
    def smartOperateCount(self):
        return self.__smart_operate_count
    
    def setSmartOperateCount(self, count):
        self.__smart_operate_count = count
        
    def incrSmartOperateCount(self):
        '''
        智能操作次数加1
        '''
        self.__smart_operate_count += 1
        ftlog.debug('MPlayer.incrSmartOperateCount now smartOperateCount:', self.__smart_operate_count)
        
    def consumeSmartOperateCount(self):
        '''
        消耗智能操作提示的机会
        '''
        self.__smart_operate_count -= 1
        if self.__smart_operate_count < 0:
            self.__smart_operate_count = 0
        ftlog.debug('MPlayer.consumeSmartOperateCount now smartOperateCount:', self.__smart_operate_count)
        
    @property
    def multiWinTiles(self):
        return self.__multi_win_tiles
    
    def setMultiWinTiles(self):
        '''
        保存玩家一炮多响牌在胡牌中的位置
        '''
        self.__multi_win_tiles.append(len(self.huTiles))
    
    @property
    def showTipsQueTimes(self):
        return self.__show_tips_que_times
    
    def incrShowTipsQueTimes(self):
        self.__show_tips_que_times += 1
        
    @property
    def playMode(self):
        return self.__play_mode
    
    @property
    def tingResult(self):
        return self.__ting_result

    def setTingResult(self, tingResult):
        self.__ting_result = tingResult

    @property
    def ishuAll(self):
        return self.__ishuAll

    def setishuAll(self, ishuAll):
        self.__ishuAll = ishuAll
        
    def getTingResultScore(self, winStyle):
        '''
        计算当前胡牌组合的价值
        
        点炮多加2张
        自摸多加1张
        
        [ tile, fan, count ]
        '''
        if len(self.tingResult):
            # 没有听牌预览的玩法，返回一个极大值
            return 999
        
        score = 0
        for ting in self.tingResult:
            if winStyle == MWinRule.WIN_BY_MYSELF:
                score += ting[1] * (ting[2] + 1)
            else:
                score += ting[1] * (ting[2] + 2)
        ftlog.debug('MPlayer.getTingResultScore tingResult:', self.tingResult
                    , ' scoer:', score)
        
        return score

    @property
    def name(self):
        """获取名称"""
        return self.__name
    
    @property
    def maoTiles(self):
        return self.__mao_tiles
    
    def setMaoTiles(self, maoTiles):
        self.__mao_tiles = maoTiles
    
    @property
    def clientId(self):
        return self.__clientId
    
    @property
    def winNodes(self):
        """获取听牌方案
        例子：
        [{'winTile': 1, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [1, 2, 3]]}
        """
        return self.__win_nodes
    
    def setWinNodes(self, winNodes):
        """设置听牌信息"""
        ftlog.debug('MPlayer.setWinNodes:', winNodes, 'userId:', self.userId, 'name:', self.name)
        self.__win_nodes = winNodes
    
    @property
    def sex(self):
        """获取用户性别"""
        return self.__sex
    
    @property
    def purl(self):
        """获取用户头像"""
        return self.__purl
    
    @property
    def coin(self):
        """获取用户金币"""
        return self.__coin
    
    def setCoin(self, coin):
        self.__coin = coin
        
    @property
    def tableCoin(self):
        """获取用户牌桌内金币"""
        return self.__table_coin
    
    def setTableCoin(self, coin):
        '''设置用户牌桌内金币'''
        ftlog.debug('MPlayer.setTableCoin:', self.__table_coin, 'UserId:', self.__userId)
        self.__table_coin = coin
        
    def getTableCoin(self, gameId, tableId):
        '''
        获取牌桌金币
        '''
        if self.isRobot():
            return self.__table_coin
        else:
            return hallrpcutil.getTableChip(self.userId, gameId, tableId)

    @property
    def curTile(self):
        """当前手牌"""
        return self.__cur_tile
    
    @property
    def curSeatId(self):
        """玩家当前座位号"""
        return self.__cur_seat_id
    
    @property
    def seatId(self):
        return self.__cur_seat_id
    
    def setSeatId(self, seat):
        """设置座位号"""
        self.__cur_seat_id = seat

    @property
    def onlineState(self):
        """玩家当前在线状态"""
        return self.__online_state
    
    @property
    def backForeState(self):
        '''
        玩家当前的离开状态
        '''
        return self.__back_fore_state
    
    def setBackForeState(self, state):
        '''
        设置玩家当前的离开状态
        '''
        self.__back_fore_state = state
    
    def setOffline(self):
        """设置用户离线"""
        self.__online_state = 0
    
    def setOnline(self):
        """设置用户在线"""
        self.__online_state = 1
    
    @property
    def userId(self):
        """获取用户ID"""
        return self.__userId
    
    @property
    def handTiles(self):
        """获取手牌"""
        return self.__hand_tiles
    
    @property
    def chiTiles(self):
        """获取吃牌"""
        return self.__chi_tiles

    @property
    def pengTiles(self):
        """获取听牌"""
        return self.__peng_tiles
    
    @property
    def gangTiles(self):
        """获取暗杠牌"""
        return self.__gang_tiles

    @property
    def pengTilesForAlarm(self):
        """获取碰牌杠牌"""
        return self.__peng_tiles_for_alarm

    @property
    def alarmInfo(self):
        """获取报警消息"""
        return self.__alarm_info

    @property
    def dropNum(self):
        return self.__dropNum

    def SetDropNum(self, value):
        self.__dropNum += value

    @property
    def huTiles(self):
        """胡牌"""
        return self.__hu_tiles
    
    @property
    def huTilesSeatId(self):
        return self.__hu_tiles_seatId

    @property
    def zhanTiles(self):
        """粘牌"""
        if self.__zhan_tiles:
            zhanTiles = []
            zhanTiles.append(self.__zhan_tiles)
            return zhanTiles
        else:
            return self.__zhan_tiles
    
    def setZhanTiles(self, zhanSolution):
        self.__zhan_tiles = zhanSolution

    @property
    def tingLiangTiles(self):
        """听牌亮牌的牌列表"""
        return self.__ting_liang_tiles

    @property
    def tingLiangTilesCurrent(self):
        """听牌亮牌的牌列表,舍掉扣牌"""
        tingLiangTilesCurrent = copy.deepcopy(self.tingLiangTiles)
        kouTiles = []
        for kouPattern in self.__kou_tiles:
            for kouTile in kouPattern:
                kouTiles.append(kouTile)
                break
        for gangObj in self.__gang_tiles:
            for gangTile in gangObj.pattern:
                if gangTile in kouTiles and gangTile in tingLiangTilesCurrent:
                    tingLiangTilesCurrent.remove(gangTile)
        return tingLiangTilesCurrent

    @property
    def tingLiangActionID(self):
        """听牌亮牌时的actionId，后面用来确认谁先亮牌"""
        return self.__ting_liang_actionId

    @property
    def tingLiangWinTiles(self):
        """听牌亮牌要胡的牌列表，也是对方禁止打的牌的列表"""
        return self.__ting_liang_winTiles

    @property
    def kouTiles(self):
        """听牌亮牌时候，需要扣掉的手牌，听牌的时候就可以杠牌了"""
        return self.__kou_tiles

    @property
    def state(self):
        """获取当前玩家状态"""
        return self.__state
    
    @property
    def autoDecide(self):
        """是否托管"""
        return self.__auto_decide

    @property
    def flowers(self):
        """花牌"""
        return self.__flowers

    def addFlowers(self, flower_tile):
        self.__flowers.append(flower_tile)

    @property
    def flowerScores(self):
        return  self.__flower_scores

    def addFlowerScores(self, score):
        self.__flower_scores += score

    @property
    def guoPengTiles(self):
        """过碰牌集合"""
        return self.__guo_peng_tiles

    def resetGuoPengTiles(self):
        """重置过碰牌集合，每次出牌要重置"""
        self.guoPengTiles.clear()

    @property
    def guoHuPoint(self):
        """过胡分数"""
        return self.__guo_hu_point

    @guoHuPoint.setter
    def guoHuPoint(self, value):
        """设置过胡分数"""
        self.__guo_hu_point = value

    def resetGuoHuPoint(self):
        """重置过胡分数，每次摸牌出牌要重置"""
        self.guoHuPoint = -1

    @property
    def curLianGangNum(self):
        """连杠次数"""
        return self.__cur_lian_gang_num

    @curLianGangNum.setter
    def curLianGangNum(self, value):
        """设置连杠次数"""
        self.__cur_lian_gang_num = value

    def maxLianGangNum(self):
        """本局里玩家的最大连杠次数"""
        num = self.__cur_lian_gang_num
        if len(self.__lian_gang_nums) > 0:
            num = max(num, max(self.__lian_gang_nums))

        return num if num >= 0 else 0

    def recordAndResetLianGangNum(self):
        """记录连杠次数，每次出牌要判断，记录并重置"""
        if self.curLianGangNum != -1:
            self.__lian_gang_nums.add(self.curLianGangNum)
            self.curLianGangNum = -1

    def resetLianGangData(self):
        """重置连杠数据，每次开局要重置"""
        self.__lian_gang_nums.clear()
        self.__cur_lian_gang_num = -1

    @property
    def winTypes(self):
        """胡牌番型列表"""
        return self.__winTypes

    @winTypes.setter
    def winTypes(self, value):
        self.__winTypes = value

    def resetWinTypes(self):
        del self.__winTypes[:]

    @property
    def winExtendTypes(self):
        """胡牌附加分类型列表"""
        return self.__winExtendTypes

    @winExtendTypes.setter
    def winExtendTypes(self, value):
        self.__winExtendTypes = value

    def resetWinExtendTypes(self):
        del self.__winExtendTypes[:]

    @property
    def winPoints(self):
        """胡牌分数集合：各种分相加，花牌分，杠分等等"""
        return self.__winPoints

    @winPoints.setter
    def winPoints(self, value):
        self.__winPoints = value

    def resetWinPoints(self):
        del self.__winPoints[:]

    @property
    def totalWinPoint(self):
        """胡牌总分"""
        return self.__totalWinPoint

    @totalWinPoint.setter
    def totalWinPoint(self, value):
        self.__totalWinPoint = value

    def resetTotalWinPoint(self):
        self.__totalWinPoint = 0

    @property
    def penaltyPoints(self):
        return self.__penaltyPoints

    @penaltyPoints.setter
    def penaltyPoints(self, value):
        self.__penaltyPoints = value
    
    @property
    def timeOutCount(self):
        return self.__time_out_count
    
    def resetTimeOutCount(self):
        self.__time_out_count = 0
        
    def addTimeOutCount(self):
        self.__time_out_count += 1
    
    def isHaveTimeOut(self):
        '''
        玩家是否超时托管过
        '''
        return self.__is_have_time_out
         
    def setAutoDecide(self, value):
        """设置是否托管
        参数
        1）value，托管设置
        True 托管
        False 不托管
        """
        ftlog.debug('MPlayer.setAutoDecide value:', value
                , ' player:', self.name
                , ' userId:', self.userId)
        self.__auto_decide = value
        self.resetTimeOutCount()
        # 玩家托管过，则设置标志位位True
        if value:
            self.__is_have_time_out = True
        
    def ready(self):
        """设置准备状态"""
        ftlog.debug('MPlayer changeState to ready, userId:', self.userId
                    , ' seatId:', self.curSeatId)
        self.__state = self.PLAYER_STATE_READY
        
    def leave(self):
        self.__state = self.PLAYER_STATE_LEAVE
        
    def confirmLoose(self):
        self.__state = self.PLAYER_STATE_CONFIRM_LOOSE
        
    def isReady(self):
        return self.__state == self.PLAYER_STATE_READY
        
    def play(self):
        """设置游戏状态"""
        ftlog.debug('MPlayer changeState to play, userId:', self.userId
                    , ' seatId:', self.curSeatId)
        self.__state = self.PLAYER_STATE_PLAYING
        
    def wait(self):
        """设置准备状态"""
        ftlog.debug('MPlayer changeState to wait, userId:', self.userId
                    , ' seatId:', self.curSeatId)
        self.__state = self.PLAYER_STATE_NORMAL
    
    def changeHandTiles(self, getTiles, removeTiles):
        '''修改用户手牌'''
        ftlog.debug('player seatid:', self.seatId, 'removeTiles:', removeTiles, 'getTiles:', getTiles)
        for tile in removeTiles:
            self.__hand_tiles.remove(tile)
        self.__hand_tiles.extend(getTiles)
       
    def isWon(self):
        """是否和牌"""
        return self.__state == self.PLAYER_STATE_WON
    
    def isLeave(self):
        return self.__state == self.PLAYER_STATE_LEAVE
    
    def isConfirmLoose(self):
        return self.__state == self.PLAYER_STATE_CONFIRM_LOOSE
    
    def isStateFixeder(self):
        '''
        玩家 手牌固定，听牌、和牌以后 不可切换听口
        '''
        if self.playMode == MPlayMode.XUELIUCHENGHE:
            # 血流没有听牌，和牌后不可切换听口
            return self.isWon()
        else:
            # 其他玩法 有听牌，听牌后不可切换听口
            return self.isTing()
    
    def isObserver(self):
        '''
        区分玩家状态，观察者，对牌局没有影响
        不关心吃碰杠听
        '''
        if self.playMode == MPlayMode.XUELIUCHENGHE:
            # 血流 可一直胡
            return self.isConfirmLoose() or self.isLeave()
        else:
            return self.isWon() or self.isLeave() or self.isConfirmLoose()
        
    def isIgnoreMessage(self):
        '''
        忽略长连接消息
        玩家认输状态会置为离开状态，在未离开的时候，还需要给玩家发送消息
        '''
        return self.isLeave() or self.isConfirmLoose()
    
    def isTing(self):
        """是否听牌"""
        return self.__state == self.PLAYER_STATE_TING

    def isTingLiang(self):
        """是否听牌同时亮牌"""
        if self.__ting_liang_tiles:
            return True
        else:
            return False
    
    def isMing(self):
        """是否明牌"""
        return self.__state == self.PLAYER_STATE_MING
        
    def isRobot(self):
        """是否是机器人"""
        if self.__userId < 10000:
            return True
        return False
    
    def canGang(self, gang, hasGang, _tiles, tile, winRuleMgr, magicTiles, tingRule, extendInfo={}):
        if not hasGang:
            return False
        
        # 判断牌池的牌数量，如果为0，则不可以杠牌，继续杠牌为相公
        if winRuleMgr.tableTileMgr.getTilesLeftCount() == 0:
            ftlog.debug("MPlayer.canGang getTilesLeftCount is 0 can't Gang")
            return False
        # 如果玩家没有听牌 胡牌，则可以直接杠
        if not self.isStateFixeder():
            return True
        
        tiles = copy.deepcopy(_tiles)
        tingGangMode = winRuleMgr.tableTileMgr.getTingGangMode()
        ftlog.debug('MPlayer.canGang gang:', gang
                    , ' hasGang:', hasGang
                    , ' tiles:', tiles
                    , ' tile:', tile
                    , ' magicTiles:', magicTiles
                    , ' extendInfo:', extendInfo
                    , ' tingGangMode:', tingGangMode)
    
        if tingGangMode & MTableTile.AFTER_TING_HU_NONE:
            return False
        elif tingGangMode & MTableTile.AFTER_TING_HU_KOU:
            ftlog.debug('MPlayer.canGang tingGangMode is kouGang')
            if [tile, tile, tile] in tiles[MHand.TYPE_PENG]:
                # 蓄杠在亮牌后，需要看是否有人胡这张牌，如果有，不能杠，否则是抢杠胡
                for player in winRuleMgr.tableTileMgr.players:
                    if player.curSeatId != self.curSeatId and tile in player.tingLiangWinTiles:
                        return False
                ftlog.debug('MPlayer.canGang xu gang', [tile, tile, tile])
                return True
            if self.kouTiles:
                # 扣牌是暗杠，不会抢杠胡，可以杠牌
                for kouPattern in self.kouTiles:
                    if tile in kouPattern:
                        return True
            return False
        elif tingGangMode & MTableTile.AFTER_TING_HU_XUGANG:
            if [tile, tile, tile] in tiles[MHand.TYPE_PENG]:
                ftlog.debug('MPlayer.canGang tingGangMode is xu gang', [tile, tile, tile])
                return True
            else:
                return False
        elif tingGangMode & MTableTile.AFTER_TING_HU_NO_CHANGE_TING:
            # 检查是否可以明杠 明杠里面要排除蓄杠问题
            if tingGangMode & MTableTile.AFTER_TING_HU_WITHOUT_MINGGANG \
                and gang['style'] == MPlayerTileGang.MING_GANG \
                and [tile, tile, tile] not in tiles[MHand.TYPE_PENG]:
                ftlog.debug('MPlayer.canGang tingGangMode with out minggang and gang is minggang')
                return False
            # 检查是否可以暗杠
            if tingGangMode & MTableTile.AFTER_TING_HU_WITHOUT_ANGANG \
                and gang['style'] == MPlayerTileGang.AN_GANG:
                ftlog.debug('MPlayer.canGang tingGangMode with out angang and gang is angang')
                return False
            
            if gang['style'] == MPlayerTileGang.AN_GANG:
                for tile in gang['pattern']:
                    tiles[MHand.TYPE_HAND].remove(tile)
               
            if gang['style'] == MPlayerTileGang.MING_GANG:
                if [tile, tile, tile] in tiles[MHand.TYPE_PENG]:
                    # 蓄杠，手牌仅清掉一张牌
                    tiles[MHand.TYPE_HAND].remove(tile)
                else:
                    for tile in gang['pattern']:
                        # 这里需要考虑3张牌在手上，最后一张明杠，清掉所有手上杠牌用掉的牌
                        if tile in tiles[MHand.TYPE_HAND]:
                            tiles[MHand.TYPE_HAND].remove(tile)
            
            tiles[MHand.TYPE_GANG].append(gang)
            ftlog.debug('MPlayer.canGang winNodes:', self.winNodes)
            if not self.winNodes:
                ftlog.debug('MPlayer.canGang return False because winNodes is None')
                return False
            _, newWinResult = tingRule.canTingBeforeAddTile(tiles, winRuleMgr.tableTileMgr.tiles, magicTiles, self.curSeatId)
            ftlog.debug('MPlayer.canGang gang newWinResult:', newWinResult)
            # 判断新的winNodes与旧的winNodes是否一致
            if newWinResult and newWinResult[0].has_key('winNodes'):
                newWinNodes = newWinResult[0]['winNodes']
            else:
                newWinNodes = []
            # 列表排序，判断是否相等
            tempOldWinNodes = copy.deepcopy(self.winNodes)
            tempOldWinNodes.sort(key=lambda node:node['winTile'])
            newWinNodes.sort(key=lambda node:node['winTile'])
            if len(tempOldWinNodes) != len(newWinNodes):
                ftlog.debug('Mplayer.canGang return False becase len not equal change WinNode oldWinNode:', tempOldWinNodes, 'newWinNodes:', newWinNodes)
                return False
            for index in range(len(tempOldWinNodes)):
                if newWinNodes[index]['winTile'] != tempOldWinNodes[index]['winTile']:
                    ftlog.debug('Mplayer.canGang return False becase change WinNode oldWinNode:', tempOldWinNodes, 'newWinNodes:', newWinNodes)
                    return False
            
            # 加入听口，如果都能和，不改变听口结果，继续杠牌；如果改变了听口，不能杠
            for node in self.winNodes:
                winTile = node['winTile']
                tiles[MHand.TYPE_HAND].append(winTile)
                # 判断是否影响听口，一律按照自摸情况预估
                result, _ = winRuleMgr.isHu(tiles, winTile, True, MWinRule.WIN_BY_MYSELF, magicTiles, [], self.curSeatId)
                if not result:
                    ftlog.debug('MPlayer.canGang gang:', gang, 'change ting result with result tiles:', tiles, 'winTile:', winTile)
                    return False
                tiles[MHand.TYPE_HAND].remove(winTile)
            # 所有听口都留下
            return True
        ftlog.debug('MPlayer.canGang  return False')
        return False

    def canAlarm(self, tiles, tile, winRuleMgr=None, magicTiles=[]):
        """是否可以报警：报警必须有碰or杠
            返回值： if True return style  else False
        """
        alarmStyle = 0

        gangTiles = []
        pengTiles = tiles[MHand.TYPE_PENG]

        for gang in tiles[MHand.TYPE_GANG]:
            gangTiles.append(gang['pattern'])

        ftlog.info('Player pengTilesForAlarm:', self.pengTilesForAlarm)

        if len(pengTiles) == 0 and len(gangTiles) == 0:
            return alarmStyle

        # 取出已有的报警类型，如果已经有了，不在判断
        allAlarm = []
        for alarm in self.alarmInfo:
            allAlarm.append(alarm.style)

        ftlog.info('Player allAlarm:', allAlarm)
        # 判断双八支 同色二杠 碰另一个色
        if MPlayerTileAlarm.DOUBLEEIGHT_ALARM not in allAlarm and len(pengTiles) >= 1 and len(gangTiles) >= 2:
            isDoubleEight = 0
            gangColors = -1  # 如果大于－1，就是同色二杠成立
            tileColors = []
            for gangTile in gangTiles:
                tileColor = MTile.getColor(gangTile[0])
                if tileColor not in tileColors:
                    tileColors.append(tileColor)
                else:
                    gangColors = tileColor

            for pengTile in pengTiles:
                tileColor = MTile.getColor(pengTile[0])
                if gangColors >= 0 and tileColor != gangColors:
                    isDoubleEight = 1
                    break

            if isDoubleEight:
                alarmStyle = MPlayerTileAlarm.DOUBLEEIGHT_ALARM
                tileAlarm = MPlayerTileAlarm(tile, [], alarmStyle)
                self.__alarm_info.append(tileAlarm)

        # 判断双四核 同色二连对or中间隔对
        if MPlayerTileAlarm.DOUBLEFOUR_ALARM not in allAlarm and len(pengTiles) >= 2:
            isLianDui = 0
            tempTileColors = {}
            pengPattern = []
            for pengTile in pengTiles:
                tempColor = MTile.getColor(pengTile[0])
                ftlog.info('Player tempTileColors:', tempTileColors, "tempColor:", tempColor)
                if tempColor in tempTileColors.values():
                    if tempTileColors.has_key(str(pengTile[0] + 1)) or tempTileColors.has_key(str(pengTile[0] - 1)) or \
                            tempTileColors.has_key(str(pengTile[0] + 2)) or tempTileColors.has_key(str(pengTile[0] - 2)):
                        isLianDui = 1
                        tempTileColors[str(pengTile[0])] = tempColor
                        for key in tempTileColors:
                            if tempTileColors[key] == tempColor and int(key) not in pengPattern:
                                pengPattern.append(int(key))
                else:
                    tempTileColors[str(pengTile[0])] = tempColor
            ftlog.info('Player pengPattern:', pengPattern)
            if isLianDui:
                alarmStyle = MPlayerTileAlarm.DOUBLEFOUR_ALARM
                tileAlarm = MPlayerTileAlarm(tile, pengPattern, alarmStyle)
                self.__alarm_info.append(tileAlarm)

        # 判断清或混
        if MPlayerTileAlarm.QINGORHUN_ALARM not in allAlarm and len(pengTiles) + len(gangTiles) >= 3:
            tileColors = []
            tempColor = -1
            for pengTile in pengTiles:
                tileColor = MTile.getColor(pengTile[0])
                tileColors.append(tileColor)

            for gangTile in gangTiles:
                tileColor = MTile.getColor(gangTile[0])
                tileColors.append(tileColor)

            # 找出关键的颜色
            arrTiles = MTile.changeTilesToValueArr(tileColors)
            for color in range(len(arrTiles)):
                if arrTiles[color] >= 2:
                    tempColor = color

            pengs = []
            for pengTile in pengTiles:
                tileColor = MTile.getColor(pengTile[0])
                if tileColor == tempColor or MTile.TILE_FENG == tileColor:
                    pengs.append(pengTile)

            for gangTile in gangTiles:
                tileColor = MTile.getColor(gangTile[0])
                if tileColor == tempColor or MTile.TILE_FENG == tileColor:
                    pengs.append(gangTile)

            if len(pengs) >= 3:
                pengPattern = []
                for pengTile in self.__peng_tiles_for_alarm:
                    tileColor = MTile.getColor(pengTile['pattern'][0])
                    if tileColor == tempColor or MTile.TILE_FENG == tileColor:
                        pengPattern.append(pengTile)

                ftlog.info('Player tileColors:', tileColors, "pengPattern:", pengPattern)
                alarmStyle = MPlayerTileAlarm.QINGORHUN_ALARM
                tileAlarm = MPlayerTileAlarm(tile, pengPattern, alarmStyle)
                self.__alarm_info.append(tileAlarm)

        return alarmStyle

    def copyHandTiles(self):
        """拷贝手牌
        返回值： 数组
        """
        return copy.deepcopy(self.__hand_tiles)
    
    def copyChiArray(self):
        """拷贝吃牌，二位数组"""
        allChi = []
        for chiObj in self.__chi_tiles:
            allChi.append(chiObj.pattern)
        return copy.deepcopy(allChi)
    
    @property
    def chiTilesFromSeat(self):
        chiSeats = []
        for chiObj in self.__chi_tiles:
            chiSeats.append({'tile': chiObj.tile, 'playerSeatId': chiObj.fromSeat})
        return chiSeats
    
    def copyChiDetails(self):
        '''
        拷贝吃牌的详细信息
        '''
        allChi = []
        for chiObj in self.__chi_tiles:
            chi = {}
            chi['tile'] = chiObj.tile
            chi['playerSeatId'] = chiObj.fromSeat
            chi['pattern'] = chiObj.pattern
            allChi.append(chi)
        return allChi

    def copyPengArray(self):
        """拷贝所有的碰牌"""
        allPeng = []
        for pengObj in self.__peng_tiles:
            allPeng.append(pengObj.pattern)
        return allPeng
    
    @property
    def pengTilesFromSeat(self):
        allPeng = []
        for pengObj in self.__peng_tiles:
            allPeng.append({'tile': pengObj.tile, 'playerSeatId': pengObj.fromSeat})
        return allPeng
    
    def copyPengDetails(self):
        """
        拷贝所有的碰牌的详细信息
        """
        allPeng = []
        for pengObj in self.__peng_tiles:
            peng = {}
            peng['tile'] = pengObj.tile
            peng['playerSeatId'] = pengObj.fromSeat
            peng['pattern'] = pengObj.pattern
            allPeng.append(peng)
        return allPeng

    def copyTingArray(self):
        """拷贝听牌数组"""
        return copy.deepcopy(self.tingResult)
    
    def copyGangArray(self):
        """拷贝杠牌"""
        allGangPattern = []
        for gangObj in self.__gang_tiles:
            gang = {}
            gang['pattern'] = gangObj.pattern
            gang['style'] = gangObj.style
            gang['actionID'] = gangObj.actionID
            if gangObj.styleScore:
                gang['styleScore'] = gangObj.styleScore
            allGangPattern.append(gang)
        return allGangPattern
    
    @property
    def gangTilesFromSeat(self):
        allGangPattern = []
        for gangObj in self.__gang_tiles:
            allGangPattern.append({'tile': gangObj.tile, 'playerSeatId':gangObj.fromSeat})
        return allGangPattern
    
    def copyGangDetails(self):
        """
        拷贝杠牌详细信息
        """
        allGangPattern = []
        for gangObj in self.__gang_tiles:
            gang = {}
            gang['tile'] = gangObj.tile
            gang['playerSeatId'] = gangObj.fromSeat
            gang['pattern'] = gangObj.pattern
            gang['style'] = gangObj.style
            gang['actionID'] = gangObj.actionID
            if gangObj.styleScore:
                gang['styleScore'] = gangObj.styleScore
            allGangPattern.append(gang)
        return allGangPattern

    def copyHuArray(self):
        """拷贝和牌"""
        return copy.deepcopy(self.__hu_tiles)
    
    def copyHuSeatIdArray(self):
        '''
        深拷贝胡牌seatId
        '''
        return copy.deepcopy(self.__hu_tiles_seatId)
        
    
    def copyMaoTile(self):
        """拷贝锚牌"""
        allMaos = []
        for maoObj in self.maoTiles:
            mao = maoObj.copyData()
            allMaos.append(mao)
        if len(allMaos) > 0:
            ftlog.debug('MPlayer.copyMaoTile allMaos:', allMaos)
        return allMaos

    def getMaoTypes(self):
        """获取已有的锚/蛋类型"""
        maoType = 0
        for maoObj in self.maoTiles:
            maoType = maoType | maoObj.maoType
        return maoType

    def getPengMaoTypes(self):
        """获取碰、杠区有的锚/蛋类型"""
        maoType = 0
        for pengobj in self.pengTiles:
            if MTile.isFeng(pengobj.pattern[0]):
                maoType = maoType | MTDefine.MAO_DAN_DNXB
            if MTile.isArrow(pengobj.pattern[0]):
                maoType = maoType | MTDefine.MAO_DAN_ZFB

        for gangobj in self.gangTiles:
            if MTile.isFeng(gangobj.pattern[0]):
                maoType = maoType | MTDefine.MAO_DAN_DNXB
            if MTile.isArrow(gangobj.pattern[0]):
                maoType = maoType | MTDefine.MAO_DAN_ZFB

        return maoType
    
    def printTiles(self):
        """打印玩家手牌"""
        ftlog.debug('MPayer.printTiles name:', self.name, ' seatId:', self.curSeatId)
        ftlog.debug('HandTiles:', self.copyHandTiles())
        ftlog.debug('ChiTiles:', self.copyChiArray())
        ftlog.debug('PengTiles:', self.copyPengArray())
        ftlog.debug('gangTiles::', self.copyGangArray())
        ftlog.debug('WinTiles:', self.copyHuArray())
    
    def copyTiles(self):
        """拷贝玩家所有的牌
        返回值，二维数组
        索引  说明    类型
        0    手牌    数组
        1    吃牌    数组
        2    碰牌    数组
        3    明杠牌  数组
        4    暗杠牌  数组
        """
        re = [[] for _ in range(MHand.TYPE_COUNT)]
        # 手牌
        handTiles = self.copyHandTiles()
        re[MHand.TYPE_HAND] = (handTiles)
        
        # 吃牌
        re[MHand.TYPE_CHI] = self.copyChiArray()
        
        # 碰牌
        re[MHand.TYPE_PENG] = self.copyPengArray()

        # 明杠牌
        re[MHand.TYPE_GANG] = self.copyGangArray()
        
        # mao牌
        re[MHand.TYPE_MAO] = self.copyMaoTile()
        
        # 和牌
        re[MHand.TYPE_HU] = self.copyHuArray()

        # 最新手牌
        newestTiles = [self.__cur_tile]
        re[MHand.TYPE_CUR] = newestTiles

        re[MHand.TYPE_SHOW_FLOWERS] = self.flowers[:]

        return re
    
    """
    以下是玩家打牌的行为
    开始
    摸牌
    出牌
    明牌
    吃
    碰
    杠
    和
    """
    def actionBegin(self, handTiles):
        """开始
        参数
            handTiles - 初始手牌
        """
        length = len(self.handTiles)
        if length > 0:
            for _ in range(length):
                self.handTiles.pop(0)
                
        self.handTiles.extend(handTiles)
        self.handTiles.sort()
        ftlog.info('Player ', self.name, ' Seat:', self.curSeatId, ' actionBegin:', self.__hand_tiles)
        
    def updateTile(self, tile, tableTileMgr):
        """更新吃牌/碰/杠牌中的宝牌"""
        magicTiles = tableTileMgr.getMagicTiles(False)
        if len(magicTiles) == 0:
            return False, None

        if tableTileMgr.canUseMagicTile(MTableState.TABLE_STATE_CHI):
            chiRe, chiData = self.updateChiTile(tile, magicTiles)
            if chiRe:
                return chiRe, chiData
            
        if tableTileMgr.canUseMagicTile(MTableState.TABLE_STATE_PENG):
            pengRe, pengData = self.updatePengTile(tile, magicTiles)
            if pengRe:
                return pengRe, pengData
            
        if tableTileMgr.canUseMagicTile(MTableState.TABLE_STATE_GANG):
            gangRe, gangData = self.updateMingGangTile(tile, magicTiles)
            if gangRe:
                return gangRe, gangData
            
        return False, None
    
    def updateChiTile(self, tile, magicTiles):
        """更新吃牌中的宝牌"""
        for chiObj in self.__chi_tiles:
            if tile in chiObj.pattern:
                continue
            
            bChanged = False
            oldPattern = copy.deepcopy(chiObj.pattern)
            newPattern = copy.deepcopy(oldPattern)
            oldTile = 0
            newTile = 0
            
            for index in range(3):
                if oldPattern[index] in magicTiles:
                    if index == 0:
                        if (oldPattern[index + 1] == (tile + 1)) or (oldPattern[index + 2] == (tile + 2)):
                            bChanged = True
                            oldTile = oldPattern[index]
                            newTile = tile
                            newPattern[index] = tile
                            break
                        
                    if index == 1:
                        if (oldPattern[index - 1] == (tile - 1)) or (oldPattern[index + 1] == (tile + 1)):
                            bChanged = True
                            oldTile = oldPattern[index]
                            newTile = tile
                            newPattern[index] = tile
                            break
                        
                    if index == 2:
                        if (oldPattern[index - 1] == (tile - 1)) or (oldPattern[index - 2] == (tile - 2)):
                            bChanged = True
                            oldTile = oldPattern[index]
                            newTile = tile
                            newPattern[index] = tile
                            break
            
            if bChanged:    
                chiObj.setPattern(newPattern)
                newData = {}
                newData['old'] = oldPattern
                newData['new'] = newPattern
                newData['type'] = 'chi'
                newData['oldTile'] = oldTile
                newData['newTile'] = newTile
                self.__hand_tiles.remove(tile)
                self.__hand_tiles.append(oldTile)
                
                return True, newData
        return False, None
            
    def updatePengTile(self, tile, magicTiles):
        """更新碰牌中的宝牌"""
        for pengObj in self.__peng_tiles:
            if tile not in pengObj.pattern:
                continue
            
            oldTile = 0
            newTile = 0
            
            newPattern = copy.deepcopy(pengObj.pattern)
            for index in range(len(newPattern)):
                if newPattern[index] in magicTiles:
                    oldTile = newPattern[index]
                    newTile = tile
                    newPattern[index] = tile
                    break
                
            ftlog.debug('MPlayer.updatePengTile newPattern:', newPattern)
            oldPattern = copy.deepcopy(pengObj.pattern)      
            pengObj.setPattern(newPattern)
            newData = {}
            newData['old'] = oldPattern
            newData['new'] = newPattern
            newData['type'] = 'peng'
            newData['newTile'] = newTile
            newData['oldTile'] = oldTile
            self.__hand_tiles.remove(tile)
            self.__hand_tiles.append(oldTile)
            return True, newData
                
        return False, None
    
    def updateMingGangTile(self, tile, magicTiles):
        """更新明杠牌中的宝牌"""
        for gangObj in self.__gang_tiles:
            if gangObj.isMingGang and (tile in gangObj.pattern):
                newPattern = copy.deepcopy(gangObj.pattern)
                oldPattern = copy.deepcopy(gangObj.pattern)
                
                oldTile = 0
                newTile = 0
                
                for index in range(4):
                    if oldPattern[index] in magicTiles:
                        newPattern[index] = tile
                        oldTile = oldPattern[index]
                        newTile = tile
                        break
                        
                gangObj.setPattern(newPattern)
                newData = {}
                
                old = {}
                old['pattern'] = oldPattern
                old['style'] = gangObj.style
                newData['old'] = old
                
                new = {}
                new['pattern'] = newPattern
                new['style'] = gangObj.style
                newData['new'] = new
                
                newData['type'] = 'gang'
                newData['oldTile'] = oldTile
                newData['newTile'] = newTile
                
                self.__hand_tiles.remove(tile)
                self.__hand_tiles.append(oldTile)
                return True, newData
                
        return False, None
        
    def actionAdd(self, tile):
        """摸牌
        加到最后，先不排序
        """
        self.__cur_tile = tile
        self.__hand_tiles.append(tile)
        self.__hand_tiles.sort()
        ftlog.debug('Player:', self.name
                    , ' HandTiles:', self.__hand_tiles
                    , ' Seat:', self.curSeatId
                    , ' actionAdd:', tile)
        
    def canDropTile(self, tile, playMode, magicTiles=[]):
        ftlog.debug('MPlayer.canDropTile tile:', tile
                    , ' playMode:', playMode
                    , ' handTiles:', self.handTiles
                    , ' count:', len(self.handTiles))
        if tile not in self.handTiles:
            return False, 'TILE NOT IN HAND!!'
        
        for maoObj in self.maoTiles:
            if maoObj.maoType == MTDefine.MAO_DAN_ZFB and playMode == MPlayMode.WEIHAI:
                if tile >= MTile.TILE_HONG_ZHONG and tile <= MTile.TILE_BAI_BAN:
                    return False, '您已经下箭锚，该张手牌只能补锚，请重新选择出牌'

            if maoObj.maoType == MTDefine.MAO_DAN_DNXB and playMode == MPlayMode.WEIHAI:
                if tile >= MTile.TILE_DONG_FENG and tile <= MTile.TILE_BEI_FENG:
                    return False, '您已经下风锚，该张手牌只能补锚，请重新选择出牌'

            if maoObj.maoType == MTDefine.MAO_DAN_DNXBZFB and playMode == MPlayMode.WEIHAI:
                if tile >= MTile.TILE_DONG_FENG and tile <= MTile.TILE_BAI_BAN:
                    return False, '您已经下乱锚，该张手牌只能补锚，请重新选择出牌'

        if len(magicTiles) > 0:
            if tile in magicTiles:
                return False, "您不能打出赖子牌"

        return True, 'OK'

    def actionDrop(self, tile):
        """出牌
        """
        if tile not in self.handTiles:
            ftlog.error('Player：', self.name
                        , ' Seat:', self.curSeatId
                        , ' actiondrap dropTile:', tile
                        , ' handTile:', self.handTiles
                        , ' BUT TILE NOT IN HANDTILES!!!')
            return False

        self.SetDropNum(1)
        self.handTiles.remove(tile)
        # 手牌排序
        self.handTiles.sort()
        ftlog.debug('Player:', self.name, ' Seat:', self.curSeatId, ' actionDrop:', tile)
        return True
    
    def actionMing(self):
        """明牌
        明牌后，别人可看到此人的手牌
        """
        ftlog.debug('MPlayer changeState to ming, userId:', self.userId
                    , ' seatId:', self.curSeatId)
        self.__state = self.PLAYER_STATE_MING
        ftlog.debug('Player:', self.name, ' Seat:', self.curSeatId, ' actionMing')
    
    def actionChi(self, handTiles, chiTile, actionId, targetSeat=None):
        """吃
        参数：
            handTiles - 自己的手牌，跟chiTile组成吃牌组
            chiTile - 被吃的牌，跟handTiles组成吃牌组
        """
        ftlog.debug('actionChi handTiles:', handTiles, ' chiTile:', chiTile)
        for tile in handTiles:
            if tile not in self.__hand_tiles:
                ftlog.debug('chi error tile:', tile)
                return False
            self.__hand_tiles.remove(tile)
        
        chiTileObj = MPlayerTileChi(chiTile, handTiles, actionId, targetSeat)    
        self.__chi_tiles.append(chiTileObj)

        self.__hand_tiles.sort()
        self.chiTilesFromSeat.append({'tile':chiTile, 'playerSeat':targetSeat})
        self.resetGuoHuPoint()
        ftlog.debug('Player:', self.name, ' Seat:', self.curSeatId, ' actionChi:', chiTile)
        return True
        
    def actionPeng(self, pengTile, pengPattern, actionId, lastSeatId=0):
        """碰别人
        """
        for _tile in pengPattern:
            self.__hand_tiles.remove(_tile)
        
        pengTileObj = MPlayerTilePeng(pengTile, pengPattern, actionId, lastSeatId)
        self.__peng_tiles.append(pengTileObj)
        
        self.__hand_tiles.sort()

        alarmPeng = {"pattern":pengPattern, "seatId":lastSeatId}
        self.pengTilesForAlarm.append(alarmPeng)
        self.pengTilesFromSeat.append({'tile':pengTile, 'playerSeat':lastSeatId})
        self.resetGuoHuPoint()
        ftlog.debug('Player:', self.name, ' Seat:', self.curSeatId, ' actionPeng:', pengTile, ' alarmPeng:', self.pengTilesForAlarm)
        return True
    
    def actionZhan(self, zhanTile, zhanPattern, actionId):
        """粘别人
        """
        for _tile in zhanPattern:
            self.__hand_tiles.remove(_tile)
            break
        
        self.__zhan_tiles = zhanPattern
        
        self.__hand_tiles.sort()
        ftlog.debug('Player:', self.name, ' Seat:', self.curSeatId, ' actionZhan:', zhanTile)
        return True

    def actionChaoTian(self, gangPattern, gangTile, actionId, style, fromSeat):
        if len(gangPattern) == 4:
            tmpTile = gangPattern.pop()
        handTiles = self.copyHandTiles()
        for _tile in gangPattern:
            if _tile not in handTiles:
                ftlog.debug('gang error gangTile =', gangTile, "handtiles=", handTiles)
                return False
            else:
                handTiles.remove(_tile)
        self.__hand_tiles = handTiles
        gangPattern.append(tmpTile)
        gangTileObj = MPlayerTileGang(gangTile, gangPattern, actionId, style, fromSeat)
        self.__gang_tiles.append(gangTileObj)

        ftlog.debug('Player:', self.name, ' Seat:', self.curSeatId, ' actionGangByDropCard:', gangTile)

    def actionGangByDropCard(self, gangTile, gangPattern, actionId, targetSeat=None):
        """明杠，通过出牌杠牌，牌先加到手牌里，再加到杠牌里
        参数：
            gangTile - 被杠的牌，跟handTiles组成杠牌组
        """
        handTiles = self.copyHandTiles()
        for _tile in gangPattern:
            if _tile not in handTiles:
                ftlog.debug('gang error gangTile =', gangTile, "handtiles=", handTiles)
                return False
            else:
                handTiles.remove(_tile)
        self.__hand_tiles = handTiles
        gangTileObj = MPlayerTileGang(gangTile, gangPattern, actionId, 1, targetSeat)
        self.__gang_tiles.append(gangTileObj)

        alarmPeng = {"pattern": gangPattern, "seatId": targetSeat}
        self.pengTilesForAlarm.append(alarmPeng)

        self.resetGuoHuPoint()
        ftlog.debug('Player:', self.name, ' Seat:', self.curSeatId, ' actionGangByDropCard:', gangTile)
        return True        
        
    def actionGangByAddCard(self, gangTile, gangPattern, style, actionId, magicTiles, fromSeat):
        """暗杠/明杠都有可能
        1）杠牌在手牌里，暗杠
        2）杠牌在碰牌里，明杠
        参数：
            gangTile - 杠牌
        返回值：
        0 - 出错，不合法
        1 - 明杠
        2 - 暗杠
        """
        ftlog.debug('MPlayer.actionGangByAddCard, gangPattern = ', gangPattern, 'gangTile=', magicTiles)
        self.resetGuoHuPoint()
        if style == MPlayerTileGang.MING_GANG:
            pengPattern = [gangPattern[0], gangPattern[1], gangPattern[2]]
            pengObj = None
            if gangTile not in self.__hand_tiles:
                ftlog.debug('MPlayer.actionGangByAddCard gang error, gangTile not in handTiles')
                return False
            
            realGangTile = None
            for _tile in self.__hand_tiles:
                if _tile in pengPattern:
                    realGangTile = _tile
                    break
                
            if not realGangTile and (len(magicTiles) > 0) and (gangTile in magicTiles):
                realGangTile = gangTile
                
            if not realGangTile:
                ftlog.debug('MPlayer.actionGangByAddCard an gang error, not gangTile in handTiles')
                return False 
            
        
            for _pengObj in self.__peng_tiles:
                if _pengObj.pattern == pengPattern:
                    pengObj = _pengObj
                    break
            ftlog.debug('MPlayer.actionGangByAddCard, gangPattern = ', gangPattern, 'gangTile=', gangTile)
            # 带赖子的补杠
            isLaiziBuGang = False
            laizi = None
            if len(magicTiles) > 0:
                ftlog.debug('MPlayer.actionGangByAddCard1,')
                for magicTile in magicTiles:
                    ftlog.debug('MPlayer.actionGangByAddCard2,')
                    newGangPattern = copy.deepcopy(gangPattern)
                    ftlog.debug('MPlayer.actionGangByAddCard3,')
                    if magicTile in newGangPattern:
                        ftlog.debug('MPlayer.actionGangByAddCard, newGangPattern = ', newGangPattern, 'magicTile=', magicTile)
                        newGangPattern.remove(magicTile)
                        newPengPattern = newGangPattern
                        ftlog.debug('MPlayer.actionGangByAddCard, newPengPattern = ', newPengPattern, 'gangTile=', gangTile)
                        for _pengObj in self.__peng_tiles:
                            if _pengObj.pattern == newPengPattern:
                                pengObj = _pengObj
                                isLaiziBuGang = True
                                laizi = magicTile
                                break
                        
            if pengObj:
                self.__peng_tiles.remove(pengObj)
                if isLaiziBuGang and laizi:
                    self.__hand_tiles.remove(laizi)
                else:
                    self.__hand_tiles.remove(realGangTile)
                gangTileObj = MPlayerTileGang(gangTile, gangPattern, actionId, style, self.curSeatId)
                self.__gang_tiles.append(gangTileObj)
            return True
        else:
            handTiles = self.copyHandTiles()
            for _tile in gangPattern:
                if _tile in handTiles:
                    handTiles.remove(_tile)
                else:
                    ftlog.debug('MPlayer.actionGangByAddCard an gang error, not 4 gangTiles in handTiles')
                    return False
            
            self.__hand_tiles = handTiles
            gangTileObj = MPlayerTileGang(gangTile, gangPattern, actionId, style, self.curSeatId)
            self.__gang_tiles.append(gangTileObj)
            return True

    def addGangScore(self, actionID, gangStyleScore):
        """将杠牌分数加到杠牌信息中"""
        ftlog.debug('MPlayer.addGangScore params actionID=', actionID, ',gangStyleScore=', gangStyleScore, ',copyGangArray=', self.copyGangArray())
        for gang in self.__gang_tiles:
            if gang.actionID == actionID:
                # 根据actionID，记录当前用户的杠牌分数
                ftlog.debug('MPlayer.addGangScore added Score', gangStyleScore)
                gang.setStyleScore(gangStyleScore)
    
    def actionTing(self, winNodes):
        """听
        """
        ftlog.info('MPlayer changeState to ting, userId:', self.userId
                    , ' seatId:', self.curSeatId)
        self.__state = self.PLAYER_STATE_TING
        self.setWinNodes(winNodes)
        ftlog.info('MPlayer:', self.name, ' Seat:', self.curSeatId, ' actionTing winNodes:', winNodes)

    def actionTingLiang(self, tableTileMgr, dropTile, actionId, kouTiles):
        """听牌同时亮牌
        """
        # 听牌同时亮牌，必须要先听牌
        if not self.isTing():
            return None

        self.__ting_liang_tiles = []
        self.__ting_liang_winTiles = []
        mode = tableTileMgr.getTingLiangMode()
        ftlog.info('actionTingLiang, mode:', mode, ' hand tiles:', self.__hand_tiles, ' drop tile:', dropTile)

        if mode == MTableTile.MODE_LIANG_NONE:
            # 当前不支持亮牌
            return None

        self.__kou_tiles = []
        if kouTiles:
            for kouTile in kouTiles:
                kouTilesPattern = [kouTile, kouTile, kouTile]
                self.__kou_tiles.append(kouTilesPattern)

            winNodesAfterKou = []
            for wn in self.__win_nodes:
                canDrop = True
                for kouTile in kouTiles:
                    if kouTile not in wn['canKouTiles']:
                        canDrop = False
                        break
                if canDrop:
                    winNodesAfterKou.append(wn)
            # 重新计算winNode
            self.__win_nodes = winNodesAfterKou

        for wn in self.__win_nodes:
            self.__ting_liang_winTiles.append(wn['winTile'])
            
        self.__ting_liang_actionId = actionId
        handTiles = copy.deepcopy(self.handTiles)

        
        if dropTile and dropTile in handTiles:
            handTiles.remove(dropTile)
        if mode == MTableTile.MODE_LIANG_HAND:
            # 亮全部手牌
            ftlog.info('actionTingLiang: in MTableTile.MODE_LIANG_HAND')
            # 此处一定要用deepcopy,否则会影响用户手牌
            self.__ting_liang_tiles = handTiles
        elif mode == MTableTile.MODE_LIANG_TING:
            # 亮全部听口的牌
            ftlog.info('actionTingLiang: in MTableTile.MODE_LIANG_TING')
            # 先找到最基本要亮的牌，就是winTile所在的所有pattern的牌的并集
            liangBasicTilesCount = [0 for _ in range(MTile.TILE_MAX_VALUE)]
            for wn in self.__win_nodes:
                liangBasicTilesCountTemp = [0 for _ in range(MTile.TILE_MAX_VALUE)]
                for p in wn['pattern']:
                    if wn['winTile'] in p:
                        # 只要要和牌出现在牌型中，这3张牌就是听口牌
                        for tile in p:
                            liangBasicTilesCountTemp[tile] += 1
                # 遍历过所有牌后，减去要胡的牌，剩下的是当前所有听口的牌
                liangBasicTilesCountTemp[wn['winTile']] -= 1
                # 汇总各种牌型中听口的牌
                for i in range(MTile.TILE_MAX_VALUE):
                    if liangBasicTilesCountTemp[i] > liangBasicTilesCount[i]:
                        liangBasicTilesCount[i] = liangBasicTilesCountTemp[i]
            # 把听口的牌整理出来
            tingLiangBasicTiles = []
            for i in range(MTile.TILE_MAX_VALUE):
                tingLiangBasicTiles.extend([i for _ in range(liangBasicTilesCount[i])])
            ftlog.info('actionTingLiang: tingLiangBasicTiles=', tingLiangBasicTiles)

            # 上面找到的最基本要亮的牌，可能拼不成一个真正要胡的牌型
            # 用户不能理解为什么胡这些牌，所以要把winNode中相关未亮的牌补全
            # 最后再求这些牌的并集
            liangTilesCount = [0 for _ in range(MTile.TILE_MAX_VALUE)]
            for wn in self.__win_nodes:
                liangTilesCountTemp = [0 for _ in range(MTile.TILE_MAX_VALUE)]
                for p in wn['pattern']:
                    # 只要那个pattern包含了基本要亮的牌，就要把整个pattern亮出来
                    # 这里可能会多亮一点牌，应该是取包含所有基本要亮的牌的最少的pattern
                    liangThisPattern = False
                    for tile in p:
                        if tile in tingLiangBasicTiles:
                            liangThisPattern = True
                            break
                    if liangThisPattern:
                        for tile in p:
                            liangTilesCountTemp[tile] += 1
                liangTilesCountTemp[wn['winTile']] -= 1
                # 汇总各种牌型中听口的牌
                for i in range(MTile.TILE_MAX_VALUE):
                    if liangTilesCountTemp[i] > liangTilesCount[i]:
                        liangTilesCount[i] = liangTilesCountTemp[i]
            # 把听口的牌整理出来
            for i in range(MTile.TILE_MAX_VALUE):
                self.__ting_liang_tiles.extend([i for _ in range(liangTilesCount[i])])

        ftlog.info('MPlayer.actionTingLiang playerName:', self.name
                   , ' Seat:', self.curSeatId
                   , ' actionTingLiang, mode:', mode
                   , ' tiles:', self.__ting_liang_tiles
                   , ' winTiles:', self.__ting_liang_winTiles
                   , ' kouTiles:', self.__kou_tiles)
    
    
    def actionHuFromOthers(self, tile, seatId):
        """吃和
        别分放炮
        """
        ftlog.debug('MPlayer changeState to actionHuFromOthers, userId:', self.userId
                    , ' seatId:', self.curSeatId
                    , ' tile:', tile)
        self.__state = self.PLAYER_STATE_WON
        self.__hu_tiles.append(tile)
        self.__hu_tiles_seatId.append(seatId)
        ftlog.debug('Player:', self.name, ' Seat:', self.curSeatId, ' actionHuFromOthers:', tile)
        
    def actionHuByMyself(self, tile, addRemove=True):
        """自摸和
        """
        ftlog.debug('MPlayer changeState to actionHuByMyself, userId:', self.userId
                    , ' seatId:', self.curSeatId
                    , ' name:', self.name
                    , ' tile:', tile)
        if not tile:
            # 血流天胡，取手牌的最后一张牌给别人看
            tile = self.handTiles[-1]
        self.__state = self.PLAYER_STATE_WON
        # 取最后一张牌放到和牌里
        if addRemove:
            self.__hu_tiles.append(tile)
            self.__hu_tiles_seatId.append(self.curSeatId)
            self.__hand_tiles.remove(tile)
    
    def actionHuByDrop(self, tile):
        """云南曲靖特殊玩法,自己出牌自己胡
        """
        ftlog.debug('MPlayer changeState to actionHuByDrop, userId:', self.userId
                    , ' seatId:', self.curSeatId)
        
        self.__state = self.PLAYER_STATE_WON
        # 取最后一张牌放到和牌里
        self.__hu_tiles.append(tile)
        self.__hu_tiles_seatId.append(self.curSeatId)
        ftlog.debug('Player:', self.name, ' Seat:', self.curSeatId, ' actionHuByDrop:', tile)
    
    def actionGrabGangHu(self, tile):
        '''
        抢杠胡 从玩家中手牌去掉
        :param tile:要胡的牌
        '''
        self.__hand_tiles.remove(tile)
        
    
    def actionBuFlower(self, tile):
        '''
        补花的牌
        :param tile:补花的牌
        '''
        self.__hand_tiles.remove(tile)
        self.__flowers.append(tile)
       
    def actionFangMao(self, pattern, maoType, actionId):
        """
        放锚/蛋
            将锚/蛋的牌从手牌中移除，加到锚牌区
        """
        for tile in pattern:
            if tile not in self.handTiles:
                return False
            self.handTiles.remove(tile)
        maoObj = MPlayerTileMao(pattern, actionId, maoType)
        self.__mao_tiles.append(maoObj)
        return True
    
    def actionExtendMao(self, tile, maoType):
        if tile not in self.handTiles:
            return False, None
        
        for maoObj in self.maoTiles:
            if maoObj.maoType == maoType:
                maoObj.pattern.append(tile)
                self.handTiles.remove(tile)
                mao = {}
                mao['tile'] = tile
                mao['type'] = maoObj.maoType
                mao['pattern'] = maoObj.pattern
                return True, mao
        return False, None
            
if __name__ == "__main__":
    pass
