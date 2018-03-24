# -*- coding=utf-8 -*-
'''
Created on 2015年9月30日
麻将陌生人桌的牌桌
@author: zhaol
'''
import copy
import random

from freetime5.twisted import ftcore
from freetime5.twisted.ftlock import locked
from freetime5.util import ftlog
from freetime5.util import ftstr
from freetime5.util import fttime
from majiang2.action_handler.action_handler_factory import ActionHandlerFactory
from majiang2.ai.play_mode import MPlayMode
from majiang2.entity import majiang_conf, util
from majiang2.entity.create_table_record import MJCreateTableRecord
from majiang2.entity.majiang_timer import MajiangTableTimer
from majiang2.entity.util import sendPopTipMsg
from majiang2.player.player import MPlayer
from majiang2.poker2.entity import hallrpcutil
from majiang2.poker2.entity.game.tables.table import TYTable
from majiang2.poker2.entity.game.tables.table_player import TYPlayer
from majiang2.poker2.entity.game.tables.table_seat import TYSeat
from majiang2.table.friend_table_define import MFTDefine
from majiang2.table.run_mode import MRunMode
from majiang2.table.table_config_define import MTDefine
from majiang2.table.table_expression import MTableExpression
from majiang2.table.table_logic import MajiangTableLogic
from majiang2.table.user_leave_reason import MUserLeaveReason
from majiang2.table_state.state import MTableState
from majiang2.table_state_processor.charge_processor import MChargeProcessor
from tuyoo5.core import tyconfig
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.game import tysessiondata
from majiang2.poker2.entity.game.rooms.room import TYRoom


class MajiangQuickTable(TYTable):
    """
    1）负责框架桌子资源的管理，对接赛制/自建桌
    2）负责处理用户的上行消息处理
    3）麻将的具体逻辑，在逻辑类中处理
    4）负责联网玩法用户准备情况的管理，条件合适的时候开始游戏
    5）MajiangTable就是核心玩法里联网的action_handler
    
    机器人调度策略
    1）机器人每局自动站起，正常结算输赢
    2）托管的真人，每局自动站起
    3）桌子上有真人准备后【坐下准备/下一局准备】，开始定时召唤机器人。在定时内如果有玩家坐下，则不添加机器人
    4）机器人金币正常带入/带出，添加BI事件和INFO级别的日志统计机器人输赢
    """
    
    def __init__(self, tableId, room):
        super(MajiangQuickTable, self).__init__(room, tableId)
        self.__actionHandler = ActionHandlerFactory.getActionHandler(MRunMode.LONGNET)
        # 初始化seat
        for seat in range(self.maxSeatN):
            self.seats[seat] = TYSeat(self)
        # 牌桌配置
        self._roomConf = self.room.roomConf
        ftlog.debug('[MajiangQuickTable] roomConf=> ', self._roomConf)
        
        self._tableConf = copy.deepcopy(self._roomConf.get('tableConf', {}))
        self._tableConf[MFTDefine.IS_CREATE] = self.getRoomConfig(MFTDefine.IS_CREATE, 0)
        self._tableConf[MFTDefine.CREATE_ITEM] = self.getRoomConfig(MFTDefine.CREATE_ITEM, None)
        ftlog.debug('[MajiangQuickTable] tableConf=>', self._tableConf)
        
        # 创建逻辑配桌类
        self.__tableType = self.getRoomConfig('tableType', 'normal')
        self.__playMode = self.getRoomConfig('playMode', None)
        if not self.__playMode:
            ftlog.error('MajiangQuickTable.init, playMode parame inValid...')
            
        # 逻辑牌桌
        self.__table_observer = None
        self.logic_table = MajiangTableLogic(self.maxSeatN, self.playMode, MRunMode.LONGNET)
        self.logic_table.setGameInfo(self.gameId, self.bigRoomId, self.roomId, self.tableId)
        self.logic_table.setTableConfig(self._tableConf, self._roomConf)
        # 设置牌桌公共信息，tableId & roomId
        self.logic_table.msgProcessor.setInfo(self.gameId, self.roomId, self.tableId, self.playMode, self.tableType, self.maxSeatN)
        self.logic_table.setTableType(self.tableType)
        
        # 给action handler设置table
        self.__actionHandler.setTable(self.logic_table)
        
        # 初始化定时器，个数是座位数加1
        self.__timer = MajiangTableTimer(self.maxSeatN + 1, self)
        # 循环定时器，用于处理打牌时候的牌桌状态
        self.__looper_timer = None
                
        ftlog.debug('[MajiangQuickTable] ====create table success=====')
        # 用户操作超时
        self.__cur_seat = 0
        # 当前的无用户操作时间
        self.__cur_no_option_time_out = -1
        
        self._params_desc = None
        self._params_option_name = None
        self._params_play_desc = None
        # 血战玩法添加，桌布信息发生了变化
        self._params_option_info = None
        # 把用户设定的逻辑桌配置传递给 WinRule
        self.logic_table.winRuleMgr.setWinRuleTableConfig(self.logic_table.tableConfig)
        # 添加机器人的时间间隔
        self._add_robot_interval = -1
        
    def _checkReloadRunConfig(self):
        '''
        更新桌子内的配置信息
        '''
        ftlog.debug('MajiangQuickTable._checkReloadRunConfig before roomConf:', self.roomConf
                    , ' tableConf:', self.tableConf)
        
        if self.configChanged :
            self._roomConf = self.room.roomConf
            self._tableConf = copy.deepcopy(self._roomConf.get('tableConf', {}))
            self._tableConf[MFTDefine.IS_CREATE] = self.getRoomConfig(MFTDefine.IS_CREATE, 0)
            self._tableConf[MFTDefine.CREATE_ITEM] = self.getRoomConfig(MFTDefine.CREATE_ITEM, None)
            ftlog.debug('[MajiangQuickTable] tableConf=>', self._tableConf)
            self.logic_table.setTableConfig(self._tableConf, self._roomConf)

        ftlog.debug('MajiangQuickTable._checkReloadRunConfig after roomConf:', self.roomConf
                    , ' tableConf:', self.tableConf)
    
    @property
    def addRobotInterval(self):
        return self._add_robot_interval
    
    def setAddRobotInterval(self, time):
        self._add_robot_interval = time
    
    @property
    def paramsDesc(self):
        return self._params_desc
    
    @property
    def paramsOptionInfo(self):
        return self._params_option_info
    
    def setParamsOptionInfo(self, info):
        self._params_option_info = info
    
    @property
    def paramsOptionName(self):
        return self._params_option_name
    
    def setParamsOptionName(self, name):
        self._params_option_name = name
        
    @property
    def paramsPlayDesc(self):
        return self._params_play_desc
    
    @property
    def curSeat(self):
        return self.__cur_seat
    
    @property
    def curNoOptionTimeOut(self):
        """当前的无用户操作时间"""
        return self.__cur_no_option_time_out
    
    @property
    def tableObserver(self):
        return self.__table_observer 
    
    def setTableObserver(self, observer):
        """设置牌桌观察者"""
        self.__table_observer = observer
        self.logic_table.setTableObserver(self.tableObserver)
    
    @property
    def tableTimer(self):
        return self.__timer
    
    @property
    def tableLooperTimer(self):
        return self.__looper_timer
    
    @property
    def actionHander(self):
        """行为解析处理器"""
        return self.__actionHandler
        
    @property
    def playMode(self):
        """玩法"""
        return self.__playMode
    
    @property
    def tableType(self):
        """牌桌类型"""
        return self.__tableType
    
    def changeFrameSeatToMJSeatId(self, frameSeat):
        """将框架的seatId转化为麻将的座位号
        获取座位号时，框架返回的是1，2，3，内部存储的索引是0，1，2
        麻将的座位号是0，1，2
        """
        return frameSeat - 1
    
    def changeMJSeatToFrameSeat(self, mjSeat):
        """将麻将的座位号转化为框架的座位号"""
        return mjSeat + 1

    def getRoomConfig(self, name, defaultValue):
        """获取房间配置"""
        return self._roomConf.get(name, defaultValue)
    
    @property
    def roomConf(self):
        return self._roomConf
    
    @property
    def tableConf(self):
        return self._tableConf
    
    def getTableConfig(self, name, defaultValue):
        """获取table配置"""
        return self._tableConf.get(name, defaultValue)

    def get_select_quick_config_infos(self):
        '''
        传递给前端list 用户桌布显示
        return [[血战到底.换三张],[底分：800],[]]
        '''
        ret = ['' for _ in range(3)]
        
        playModeName = self.getRoomConfig('playModeName', None)
        if playModeName:
            ret[0] = playModeName
                    
        threeTiles = self.getTableConfig(MTDefine.THREE_TILE_CHANGE, 0)
        if threeTiles:
            ret[0] += ".换三张"
        
        baseChipVal = self.getTableConfig(MTDefine.BASE_CHIP, 1)
        if baseChipVal:
            ret[1] = '底分:' + str(baseChipVal)    
            
        ftlog.debug('get_select_quick_config_infos playmode_config ret:', ret)
        return ret


    def get_select_quick_config_items(self):
        """
        获取快速桌创建的选项描述
            
            返回值1，paramsDesc - 分享时的建桌参数，包含人数和局数
            返回值2，paramsPlayDesc - 在牌桌上显示的建桌参数，不包含人数和局数
            
        """
        paramsDesc = []
        paramsPlayDesc = []
#         paramsPlayDescPattern1 = []
#         
#         create_table_config = majiang_conf.getCreateTableTotalConfig(self.gameId)
#         playmode_config = {}
#         if create_table_config:
#             playmode_config = create_table_config.get(self.playMode,{})
#             prarmType = playmode_config['paramType']
#             for key in prarmType:
#                 if not (key == 'cardCount' or key=='wanFa' or key=='playerType'):
#                     paramsPlayDescPattern1.append(key)
#                     
#             '''    
#             wanFa = playmode_config['wanFa']
#             for wa in wanFa:
#                 paramsPlayDescPattern1.append(wa['id'])
#             '''
# 
#             ftlog.debug('paramsPlayDescPattern1:', paramsPlayDescPattern1)
#             #快速金币桌通过桌子配置文件设置数值
#             paramsPlayDescPattern = {}
#             for item in paramsPlayDescPattern1:
#                 if item=='winBase': 
#                     findTableConfigKey=MTDefine.WIN_BASE
#                 elif item=='shareFangka': 
#                     findTableConfigKey=MTDefine.SHARE_FANGKA
#                 elif item=='xixiangfeng': 
#                     findTableConfigKey=MTDefine.XIXIANGFENG
#                 elif item=='needzimo': 
#                     findTableConfigKey=MTDefine.WIN_BY_ZIMO
#                 elif item=='maiMa': 
#                     findTableConfigKey=MTDefine.MAI_MA
#                 
#                 value = self.getTableConfig(findTableConfigKey, 0)
#                 keyConfig = playmode_config[item]
#                 paramsPlayDescPattern[item] = 0
#                 for keyConfigItem in keyConfig:
#                     if 'value' in keyConfigItem:
#                         if keyConfigItem['value']==value:
#                             paramsPlayDescPattern[item] = keyConfigItem['id']
#                             continue
#                 
#             ftlog.debug('paramsPlayDescPattern:', paramsPlayDescPattern)
#         
#             #通过id直接获取自建桌配置的key数组
#             for key, value in paramsPlayDescPattern.iteritems():
#                 if (key not in playmode_config):
#                     continue
#                 
#                 items = playmode_config[key]
#                 for item in items:
#                     ftlog.debug('get_select_quick_config_items item:', item, ' value:', value)
#                     if item['id'] == value:
#                         paramsDesc.append(item['desc'])
#                         paramsPlayDesc.append(item['desc'])
#                         
#                         
#         ftlog.debug('get_select_quick_config_items paramsDesc:', paramsDesc
#                         , ' paramsPlayDesc:', paramsPlayDesc)
            
        return paramsDesc, paramsPlayDesc
    
    def CheckSeatId(self, seatId, userId=None):
        """
        校验座位号
        """
        seatValid = (seatId >= 0) and (seatId < self.maxSeatN)
        if not seatValid:
            return False
        
        if not userId:
            return seatValid
        
        if self.seats[seatId][TYSeat.INDEX_SEATE_USERID] != userId:
            return False
        
        return True
    
    @property
    def playersNum(self):
        '''
        重载table的属性
        '''
        x = 0
        for s in self.seats :
            if s and (s.userId > 0) and (TYPlayer.isHuman(s.userId)):
                x = x + 1
        return x
    
    @property
    def realPlayerNum(self):
        '''
        牌桌人数，包括机器人
        '''
        x = 0
        for s in self.seats :
            if s and (s.userId > 0):
                x = x + 1
        return x
    
    def doTableChat(self, userId, seatId, isFace, voiceIdx, chatMsg):
        """
        doTableChat非父类的接口，可以抽象至麻将的table基类中
        """
        ftlog.debug('MajiangQuickTable.doTableChat userId:', userId,
                ' seatId:', seatId,
                ' ifFace:', isFace if isFace else "1",
                ' voiceIdx:', voiceIdx if voiceIdx else "1",
                ' chatMsg:', chatMsg if chatMsg else "1")
        
        if 'type' in chatMsg and chatMsg['type'] == 2:
            # 表情
            if not self.process_interactive_expression(userId, seatId, chatMsg):
                return
        # 语音/文字
        self._doTableChat(userId, seatId, isFace, voiceIdx, chatMsg)

    def _doTableChat(self, userId, seatId, isFace, voiceIdx, chatMsg):
        """
        聊天的逻辑
        1）文字聊天
        {
            "cmd": "table_chat",
            "params": {
                "roomId": 7108021001,
                "tableId": 71080210010100,
                "seatId": 1,
                "isFace": 0,
                "msg": {
                    "seatId": 1,
                    "type": 0,
                    "content": "abc"
                },
                "gameId": 710,
                "userId": 10856,
                "clientId": "IOS_3.91_tuyoo.appStore,weixinPay,alipay.0-hall6.appStore.huanle"
            }
        }
        
        2）语音聊天
        {
            "cmd": "table_chat",
            "params": {
                "roomId": 7108021001,
                "tableId": 71080210010100,
                "seatId": 1,
                "isFace": 0,
                "msg": {
                    "seatId": 1,
                    "type": 2,
                    "emoId": 1,
                    "targetSeatId": 0
                },
                "gameId": 710,
                "userId": 10856,
                "clientId": "      IOS_3.91_tuyoo.appStore,weixinPay,alipay.0-hall6.appStore.huanle"
            }
        }
        """
        ftlog.debug('MajiangQuickTable._doTableChat chatMsg:', chatMsg)
        if not chatMsg:
            return
        
        if isFace == 0 and 'type' in chatMsg and chatMsg['type'] == 0:  # 麻将文字聊天消息
            content = chatMsg['content']
            filterContent = pluginCross.keywords.replace(content)
            chatMsg['content'] = filterContent
            
        if isFace == 0:
            self.logic_table.msgProcessor.table_chat_broadcast(userId, self.gameId, voiceIdx, chatMsg)
        else:
            for seat in self.maxSeatN:
                player = self.logic_table.getPlayer(seat)
                self.logic_table.msgProcessor.table_chat_to_face(userId, self.gameId, voiceIdx, chatMsg, player)

    def process_interactive_expression(self, uid, seatId, chat_msg):
        """
        处理消费金币的表情
        """
        targetSeatId = chat_msg.get('targetSeatId', -1)
        if not self.CheckSeatId(targetSeatId, None):
            return False
        
        target_player_uid = self.seats[targetSeatId][TYSeat.INDEX_SEATE_USERID]
        return MTableExpression.process_interactive_expression(uid
                , self.gameId
                , seatId
                , chat_msg
                , target_player_uid
                , self.getTableConfig(MTDefine.BASE_CHIP, 0)
                , self.getTableConfig(MTDefine.TABLE_CHAT_CHIP, -1))

    def _doSit(self, msg, userId, seatId, clientId): 
        '''
        玩家操作, 尝试再当前的某个座位上坐下
        '''
        ftlog.debug('MajiangQuickTable._doSit=msg=', msg, ' seatId:', seatId, 'tableId:', self.tableId)
        seatId = self.changeFrameSeatToMJSeatId(seatId)
        self.doSitDown(userId, seatId, msg, clientId)
        
    def playerReady(self, seatId, ready):
        '''
        用户准备 返回值为牌桌是否开始
        '''
        return self.logic_table.playerReady(seatId, ready)

    def doSitDown(self, userId, seatId, msg, clientId):
        """
        用户坐到某个桌子上，逻辑处理：如果是非重连用户，将用户坐下的消息广播给
        其它已经坐下的用户，然后将当前的桌子信息发送给新来用户
        继承自table类
        这是的seatId为游戏的座位号
        
        返回值：
        1）是否做下
        2）是否断线重连
        """
        ftlog.info('MajiangQuickTable.doSitDown seatId =', seatId, ', userId = ', userId, ' tableId:', self.tableId, 'msg:', msg)
        if (seatId != -1) and (userId != self.seats[seatId][TYSeat.INDEX_SEATE_USERID]):
            pluginCross.onlinedata.removeOnLineLoc(userId, self.roomId, self.tableId)
            ftlog.warn('reconnecting user id is not matched', 'seats =', self.seats, ' tableId:', self.tableId)
            return False
            
        pluginVersion = msg.getParam('version', 5.01) if msg else 5.01
        frameSeatId = self.findIdleSeat(userId)
        ftlog.info('MajiangQuickTable.doSitDown userId:', userId, ' findSeatId:', frameSeatId)
        
        sitRe = True
        if 0 == frameSeatId:
            ftlog.debug('MajiangQuickTable.doSitDown now seats:', self.seats)
            sendPopTipMsg(userId, '对不起,该房间已满员')
            self.logic_table.msgProcessor.quick_start_err(userId)
            sitRe = False
        elif 0 > frameSeatId:
            # 补发tableInfo
            seatId = self.getSeatIdByUserId(userId)
            ftlog.info('MajiangQuickTable.doSitDown try to reSend tableInfo userId:', userId
                    , ' seatId:', seatId
                    , ' loc:', pluginCross.onlinedata.getOnLineLocList(userId))
            if seatId < 0:
                pluginCross.onlinedata.removeOnLineLoc(userId, self.roomId, self.tableId)
            else:
                self.sendMsgTableInfo(msg, userId, seatId, True)
        elif frameSeatId > 0:
            isReady = self.getTableConfig(MTDefine.READY_AFTER_SIT, 0)
            gameSeatId = self.changeFrameSeatToMJSeatId(frameSeatId)
            # 设置座位的状态
            self.seats[gameSeatId][TYSeat.INDEX_SEATE_USERID] = userId
            # 快速桌用户坐下就是准备状态
            self.seats[gameSeatId][TYSeat.INDEX_SEATE_STATE] = TYSeat.SEAT_STATE_READY if isReady else TYSeat.SEAT_STATE_WAIT
            # 添加玩家
            tPlayer = TYPlayer(self, gameSeatId)
            self.players[gameSeatId] = tPlayer
            ftlog.debug('MajiangQuickTable.doSitDown user:', userId
                        , ' seat in:', gameSeatId
                        , ' now seats:', self.seats
                        , ' now realPlayerNum:', self.realPlayerNum
                        , ' isReady', isReady)
            
            
            # 玩家金币带入金币桌
            if TYPlayer.isHuman(userId):
                chip = hallrpcutil.getChip(userId)
                lastTableCoin, lastRoomId, lastLeaveTime = pluginCross.mj2dao.getQuickStartLastInfo(userId)
                buyIn = self.getRoomConfig(MTDefine.BUYIN_CHIP, 1000)
                nowTime = fttime.getCurrentTimestamp()
                ftlog.debug('MajiangQuickTable.doSitDown userChip:', chip
                            , ' buyIn:', buyIn
                            , ' lastRoomId:', lastRoomId
                            , ' nowRoomId:', tyconfig.getBigRoomId(self.roomId)
                            , ' lastLeaveTime:', lastLeaveTime
                            , ' nowTime:', nowTime
                            , ' lastTableCoin:', lastTableCoin)
                if (nowTime - lastLeaveTime < 600) and (tyconfig.getBigRoomId(self.roomId) == lastRoomId):
                    if buyIn < lastTableCoin:
                        buyIn = lastTableCoin

                if chip < buyIn:
                    buyIn = chip
                    
                ftlog.debug('MajiangQuickTable.doSitDown finally buyIn:', buyIn)
                    
                tfinal, final, delta = hallrpcutil.setTableChipToN(userId, self.gameId, buyIn, 'CHIP_TO_TABLE_TCHIP', 0, clientId, self.tableId
                                                                   )
                ftlog.debug('MajiangQuickTable.doSitDown setTableChipToN tfinal:', tfinal, 'final', final, 'delta', delta)
            
                locResult = pluginCross.onlinedata.addOnLineLoc(userId, self.roomId, self.tableId, frameSeatId)
                ftlog.info('MajiangQuickTable.doSitDown, add online loc userId:', userId
                           , ' roomId:', self.roomId
                           , ' tableId:', self.tableId
                           , ' frameSeatId:', frameSeatId
                           , ' locResult:', locResult)
                
                # _name, _purl, _sex, _coin = userdata.getAttrs(userId, ['name', 'purl', 'sex', 'coin'])
                _name, _purl, _sex = hallrpcutil.getUserBaseInfo(userId)
                _tablecoin = hallrpcutil.getTableChip(userId, self.gameId, self.tableId)
                ftlog.debug('MajiangQuickTable.doSitDown chip:', chip, 'tableCoin:', _tablecoin, 'userId:', userId)
                ftlog.info('Majiang2.logAnalyse userId:', userId, 'BuyinTableCoin:', _tablecoin, 'tableId:', self.tableId, 'SitDown')
                player = MPlayer(_name, _sex, userId, 0, _purl, chip - _tablecoin, _tablecoin, clientId, self.playMode, pluginVersion)
                # 通知前端金币发生变化
                hallrpcutil.sendDataChangeNotify(userId, self.gameId, 'udata')
                # 快速桌 默认坐下就是准备状态 默认非托管状态
                self.logic_table.addPlayer(player, gameSeatId, False)
                # 发送location消息
                self.logic_table.msgProcessor.send_location_message(gameSeatId, userId)
            else:
                from majiang2.resource import resource
                robot = resource.getRobotByUserId(userId)
                if robot:
                    robotCoin = self.getAutoCoin()
                    player = MPlayer(robot['name']
                                , robot['sex']
                                , userId
                                , 0
                                , robot['purl']
                                , 0
                                , robotCoin
                                , 'Android_3.361_tuyoo.weakChinaMobile.0-hall7.wangyi.tu'
                                , self.playMode, pluginVersion)
                    ftlog.info('Majiang2.logAnalyse userId:', userId, 'BuyinTableCoin:', robotCoin, 'tableId:', self.tableId, 'SitDown')
                    # 机器人默认准备 默认托管状态
                    self.logic_table.addPlayer(player, gameSeatId, True)
                    isReady = True

            # 座位号调整，框架返回时进行了加1的操作，调整还原
            ftlog.info('MajiangQuickTable.doSitDown, self.tableId:', self.tableId, 'getTableScore:', self.getTableScore(), 'playersNum:', self.playersNum, 'maxSeatN:', self.maxSeatN)
            self.room.updateTableScore(self.getTableScore(), self.tableId)
            self.sendMsgTableInfo(msg, userId, self.getSeatIdByUserId(userId), False)
            # seatId房主特殊处理
            if self.getSeatIdByUserId(userId) == 0:
                isReady = True
            self.playerReady(gameSeatId, isReady)
            # 通知其他人玩家信息
            self.logic_table.msgProcessor.sendTableEvent(self.realPlayerNum, userId, gameSeatId)
            # 启动牌桌未开始时的定时器
            self.startLoopTimer()
            
        return sitRe
    
    def getAutoCoin(self):
        '''
        机器人带入金币，带入[minCoin, maxCoin]范围内的随机值
        '''
        minCoin = self.getRoomConfig(MTDefine.MIN_COIN, 0)
        if minCoin <= 0:
            minCoin = 0
        maxCoin = self.getRoomConfig(MTDefine.MAX_COIN, 0)
        if maxCoin <= 0:
            maxCoin = 2 * minCoin
        buyIn = self.getRoomConfig(MTDefine.BUYIN_CHIP, 0)
        if maxCoin > buyIn * 2:
            maxCoin = buyIn * 2
        coin = random.randint(minCoin, maxCoin)
        return coin
    
    def sendMsgTableInfo(self, message, userId, seatId, isReconnect, isHost=False):
        """玩家坐下后，给玩家发送table_info，拉进游戏"""
        if not isReconnect and 0 == seatId:
            # 计算本局庄家位置
            self.logic_table.calcBeginBanker()
        
        if self.tableType == MTDefine.TABLE_TYPE_NORMAL:
            # 如果是快速桌，因为没有创建选项消息，所以要根据桌子配置文件填充玩法信息
            self._params_desc, self._params_play_desc = self.get_select_quick_config_items()  # 配置项对应的参数及值
            self._params_option_info = self.get_select_quick_config_infos()
            self.logic_table.tableConfig[MFTDefine.CREATE_TABLE_PLAY_DESCS] = self.paramsPlayDesc
            self.logic_table.tableConfig[MFTDefine.CREATE_TABLE_PLAY_INFO] = self.paramsOptionInfo
            
            # 金币桌根据桌子配置文件填充连胜信息
            self.logic_table.tableConfig[MTDefine.WIN_STREAK_TASKS_DESC] = self.getRoomConfig(MTDefine.WIN_STREAK_TASKS_DESC, None)
            ftlog.debug('MajiangQuickTable.getWinStreakTask desc:', self.logic_table.tableConfig[MTDefine.WIN_STREAK_TASKS_DESC])
        
        self.logic_table.sendMsgTableInfo(seatId, isReconnect)
        if isReconnect and self.logic_table.isPlaying():
            if self.logic_table.checkTableState(MTableState.TABLE_STATE_PIAO):
                self.logic_table.piaoProcessor.broadCastPiao(self.logic_table.msgProcessor)
            if self.logic_table.checkTableState(MTableState.TABLE_STATE_DOUBLE):
                self.logic_table.doubleProcessor.broadCastDoule()
            if self.logic_table.roundResult != None:
                # 发送对局流水信息
                self.logic_table.sendTurnoverResult(seatId)
                self.logic_table.sendWinerInfo(seatId)
            # 实时消息补发
            self.logic_table.msgProcessor.table_call_latest_msg(seatId)
            
            # 补发其他玩家定缺换三张的选择情况
            if self.logic_table.checkTableState(MTableState.TABLE_STATE_ABSENCE):
                self.logic_table.absenceProcessor.handlePlayerReconnect(userId, seatId)
            if self.logic_table.checkTableState(MTableState.TABLE_STATE_CHANGE_TILE):
                self.logic_table.huanSanZhangProcessor.handlePlayerReconnect(seatId, self.logic_table.msgProcessor)
            # 补发comb状态
            self.logic_table.processCombol(seatId)
            # 补发任务状态信息
            self.logic_table.sendTaskInfoToUser(userId)
            # 补发癞子的信息
            self.logic_table.sendLaiziInfo(True)
            
        self.logic_table.msgProcessor.broadcastUserSit(seatId, userId, isReconnect, isHost)
        
    def startLoopTimer(self):
        '''开启牌桌管理定时器'''
        if not self.__looper_timer:
            ftlog.debug('startLoopTimer tableId:', self.tableId)
            self.__looper_timer = ftcore.runLoopSync(MTDefine.TABLE_TIMER, self.handle_table_action)
            self.__looper_timer.start()
    
    @locked
    def handle_table_action(self):
        '''
        管理处理牌桌逻辑
        '''
        isTableBegin = self.logic_table.isPlaying()
        isGameOver = self.logic_table.isGameOver()
        if isTableBegin or isGameOver:
            self.handle_auto_decide_action()
        else:
            self.handler_table_manager_not_play()
            
    def _randRobotUserId(self):
        '''
        防止取到相同userID的机器人
        '''
        from majiang2.resource import resource
        userIdRange = range(1, 999)
        userIdList = random.sample(userIdRange, 4)
        for randId in userIdList:
            robotUserId = resource.getRobot(randId)['userId']
            isSameFlag = False
            for cp in self.logic_table.players:
                if cp and cp.userId == robotUserId:
                    isSameFlag = True
                    break
                
            if not isSameFlag:
                return randId
    
    def handler_table_manager_not_play(self):
        '''
        牌桌状态管理器，由于牌桌状态会实时变化，所以不能保存牌桌状态
        --> 没有真人，清空桌子，取消定时器
        --> 有真人
            --> 有人准备
                --> 人满，玩家超时踢出未准备的玩家 回到第一步
                --> 人不满 添加机器人 会到第一步
        '''
        ftlog.debug('MajiangQuickTable.handler_table_manager_not_play tableId:', self.tableId)
        
        ftlog.debug('MajiangQuickTable.handler_table_manager_not_play tableId:', self.tableId)
        # 桌子上没有真人，则清理桌子
        if ((self.realPlayerNum >= 0) and (self.playersNum == 0)) or (self.realPlayerNum == 0):
            ftlog.debug("MajiangQuickTable.handler_table_manager_not_play clearTable...")
            self.clearTable(True, MUserLeaveReason.IS_ROBOT)
            return 
        
        # 桌子上有人准备，根据情况添加机器人
        hasReady = False 
        for player in self.logic_table.players:
            if player and player.isReady():
                hasReady = True 
                break
        robotMode = self.getRoomConfig(MTDefine.HAS_ROBOT, 1)
        if hasReady:
            if self.realPlayerNum < self.maxSeatN and robotMode == 1:
                if self.addRobotInterval == -1:
                    # 初始化 随机时间
                    robot_interval = majiang_conf.getRobotInterval(self.gameId)
                    if robot_interval >= 3:
                        randTime = random.randint(0, 2) - 1
                        robot_interval += randTime
                    self.setAddRobotInterval(robot_interval)
                    
                if self.addRobotInterval == 0:
                    robotMode = self.getRoomConfig(MTDefine.HAS_ROBOT, 1)
                    if robotMode != 1:
                        return
                    
                    robotRandom = self._randRobotUserId()
                    ftlog.debug('MajiangQuickTable.handler_table_manager_not_play robotRandom:', robotRandom)
                    from majiang2.resource import resource
                    robot = resource.getRobot(robotRandom)
                    self.doSitDown(robot['userId'], -1, None, 'robot_3.7_-hall6-robot')
                    # 设置时间为默认值
                    self.setAddRobotInterval(-1)
                elif self.addRobotInterval > 0:
                    self.setAddRobotInterval(self.addRobotInterval - MTDefine.TABLE_TIMER)
                    ftlog.debug('MajiangQuickTable.handler_table_manager_not_play addRobotInterval:', self.addRobotInterval)
                
        # 判断超时未准备的玩家 
        for player in self.logic_table.players:
            if not player or player.isReady():
                # 玩家已准备，则不判断
                continue 
            
            ftlog.debug('MajiangQuickTable.handler_table_manager_not_play userLeave player:', player.userId, 'time:', player.readyTimeOut)
            if player.readyTimeOut == -1:
                # 初始化时间
                player.setReadyTimeOut(majiang_conf.getNormalTableReadyTimeOut(self.gameId))
            elif player.readyTimeOut == 0:
                # 超时时间到
                self.userLeave(player.userId, player.seatId, MUserLeaveReason.NORMAL_READY_TIME_OUT)
            else:
                # 递减时间
                player.setReadyTimeOut(player.readyTimeOut - MTDefine.TABLE_TIMER)
        
    def handle_auto_decide_action(self):
        """处理托管"""
        if self.logic_table.isGameOver():
            if not self.getRoomConfig(MTDefine.HAS_ROBOT, 0):
                self.saveRecordAfterTable()
            
            for player in self.logic_table.player:
                if not player:
                    continue
                
                if TYPlayer.isHuman(player.userId):
                    if self.room.runStatus != TYRoom.ROOM_STATUS_RUN:
                        # 服务器维护
                        self.userLeave(player.userId, player.seatId, MUserLeaveReason.SERVER_SHUTDOWN)

                    if self.logic_table.isUserChipNotEnough(player.curSeatId):
                        # 用户金币不足，离开
                        self.userLeave(player.userId, player.seatId, MUserLeaveReason.CHIP_NOT_ENOUGH)
                    elif self.logic_table.isUserChipMoreThanMax(player.curSeatId):
                        self.userLeave(player.userId, player.seatId, MUserLeaveReason.CHIP_MORE_THAN_MAX)
                    elif player.autoDecide:
                        # 用户托管，离开
                        self.userLeave(player.userId, player.seatId, MUserLeaveReason.AUTO_DECIDE)
                        # 房间配置 金币桌牌局结束后玩家离桌
                    elif majiang_conf.getNormalTableFinishUserLeave(self.gameId):
                        self.userLeave(player.userId, player.seatId, MUserLeaveReason.COIN_TABLE_FINISH)
                    
                if TYPlayer.isRobot(player.userId):
                    self.userLeave(player.userId, player.seatId, MUserLeaveReason.IS_ROBOT)
                    
            self.logic_table.nextRound()
            self.resetNoOptionTimeOut()
        else:
            # 处理金币桌托管
            for player in self.logic_table.player:
                if player:
                    if TYPlayer.isHuman(player.userId) and (not player.autoDecide):
                        if player.timeOutCount == 2 or (player.timeOutCount != 0 and player.isHaveTimeOut()):
                            player.setAutoDecide(True)
                            self.logic_table.msgProcessor.trusteeInfo(player.curSeatId, True, player.userId)
                            ftlog.debug('handle_auto_decide_action player.setAutoDecide(True) userid:', player.userId)
                    # 使认输的玩家离开        
                    if player.isConfirmLoose():
                        ftlog.debug('handle_auto_decide_action player leave becase isConfirmLoose')
                        self.userLeave(player.userId, player.seatId, MUserLeaveReason.IS_CONFIRM_LOOSE)
                    
        self.actionHander.updateTimeOut(-MTDefine.TABLE_TIMER)
        self.actionHander.doAutoAction()
        self.checkNoOptionTimeOut()

    def resetNoOptionTimeOut(self):
        """充值无操作超时参数"""
        if self.__cur_no_option_time_out != -1:
            self.__cur_no_option_time_out = -1
            self.__cur_seat = 0
        
    def checkNoOptionTimeOut(self):
        """检查无操作超时"""
        if not self.getRoomConfig(MTDefine.HAS_ROBOT, 0):
            """非练习场不检查"""
            return
        
        ftlog.debug('MajiangFriendTable.checkNoOptionTimeOut timeOut:', self.curNoOptionTimeOut
                , ' curSeat:', self.curSeat
                , ' tableId:', self.tableId)
        nowSeat = self.logic_table.curSeat
        if (self.curNoOptionTimeOut == -1) or (self.curSeat != nowSeat):
            self.__cur_no_option_time_out = self.logic_table.getTableConfig(MFTDefine.CLEAR_TABLE_NO_OPTION_TIMEOUT, 3600)
            self.__cur_seat = nowSeat
        elif self.curNoOptionTimeOut > 0:
            self.__cur_no_option_time_out -= 1
            if self.curNoOptionTimeOut <= 0:
                self.resetNoOptionTimeOut()
                self.clearTable(True, MUserLeaveReason.NO_OPTION_TIME_OUT)
            
    def _doTableCall(self, msg, userId, seatId, action, clientId):
        """继承父类，处理table_call消息
        """
        try:
            ftlog.info('MajiangQuickTable handle table_call message, tableId:', self.tableId
                       , ' seatId:', seatId
                       , ' action:', action
                       , ' userId:', userId
                       , ' message:', msg)
            
            if not self.CheckSeatId(seatId, userId):
                ftlog.warn("handle table_call, seatId is invalid,", action, seatId)
                return
            
            if action == 'play':
                # 出牌
                self.actionHander.handleTableCallPlay(userId, seatId, msg)
            elif action == 'chi':
                # 吃牌
                self.actionHander.handleTableCallChi(userId, seatId, msg)
            elif action == 'peng':
                # 碰牌
                self.actionHander.handleTableCallPeng(userId, seatId, msg)
            elif action == 'gang':
                # 杠牌
                self.actionHander.handleTableCallGang(userId, seatId, msg)
            elif action == 'grabTing':
                # 抢听
                self.actionHander.handleTableCallGrabTing(userId, seatId, msg)
            elif action == 'ting':
                # 听牌，明楼
                self.actionHander.handleTableCallTing(userId, seatId, msg)
            elif action == 'win':
                # 和牌
                self.actionHander.handleTableCallWin(userId, seatId, msg)
            elif action == 'pass':
                # 过牌
                self.actionHander.handleTableCallpass(userId, seatId, msg)
            elif action == 'grabHuGang':
                # 抢杠和
                self.actionHander.handleTableCallGrabHuGang(userId, seatId, msg)
            elif action == 'fanpigu':
                self.actionHander.handleTableCallFanpigu(userId, seatId, msg)
            elif action == 'remove_trustee':
                self.logic_table.setAutoDecideValue(seatId, False)
                self.logic_table.msgProcessor.trusteeInfo(seatId, False, userId)
            elif action == 'ask_piao':
                self.actionHander.handleTableCallAskPiao(userId, seatId, msg)
            elif action == 'accept_piao':
                self.actionHander.handleTableCallAcceptPiao(userId, seatId, msg)
            elif action == 'double':
                self.actionHander.handleTableCallDouble(userId, seatId, msg)
            elif action == 'noDouble':
                self.actionHander.handleTableCallNoDouble(userId, seatId, msg)
            elif action == 'ping':
                self.actionHander.handleTableCallPing(userId, seatId, msg)
            elif action == 'fang_mao':
                self.actionHander.handleTableCallFangMao(userId, seatId, msg)
            elif action == 'extend_mao':
                self.actionHander.handleTableCallExtendMao(userId, seatId, msg)
            elif action == 'bu_flower':
                self.actionHander.handleTableCallBuFlower(userId, seatId, msg)
            elif action == 'crapshoot':  # 掷骰子
                self.actionHander.handleTableCallCrapShoot(userId, seatId, msg)
            elif action == 'ding_absence':  # 定缺
                self.actionHander.handleTableCallDingAbsence(userId, seatId, msg)
            elif action == 'ask_huanPai':  # 换三张
                self.actionHander.handleTableCallConfirmSanZhang(userId, seatId, msg)
            elif action == 'leave':  # 离开
                userId = msg.getParam('userId')
                seatId = self.getSeatIdByUserId(userId)
                if seatId < 0:
                    return
                self.userLeave(userId, seatId, MUserLeaveReason.LEAVE)
            elif action == 'next_round':
                self.nextRound(msg, userId, seatId, action, clientId)
            elif action == 'charge':
                self.actionHander.handleTableCallCharge(userId, seatId, msg)
            elif action == 'smart_operate':
                self.actionHander.handleTableCallSmartOperate(userId, seatId, msg)
            else:
                ftlog.debug('MajiangQuickTable._doTableCall unprocessed message:', msg)
        except:
            ftlog.error("_doTableCall error clear table")
            self.clearTable(True, MUserLeaveReason.TABLE_CALL_ERROR)
            
    def nextRound(self, message, userId, seatId, action, clientId):
        '''
        继续下一局游戏
        '''
        if self.logic_table.isPlaying():
            return

        if self.room.runStatus != TYRoom.ROOM_STATUS_RUN:
            util.sendPopTipMsg(userId, "亲爱的玩家服务即将例行维护，请5分钟后继续打牌，给您带来的不便尽请谅解！")
            return
        
        self.logic_table.sendMsgTableInfo(seatId)
        self.playerReady(seatId, True)
        for player in self.logic_table.player:
            if not player:
                continue
            
            if player.isRobot() and (not player.isReady()):
                self.playerReady(player.curSeatId, True)
            
    def kickOffUser(self, userId, seatId, sendLeave, reason=''):
        """让一个玩家leave"""
        ftlog.info('MajiangQuickTable.kickOffUser userId:', userId, ' seatId:', seatId)
        
        if TYPlayer.isHuman(userId) and self.tableType == MTDefine.TABLE_TYPE_NORMAL:
            # 离开时，玩家牌桌上的金币数
            tableChip = hallrpcutil.getTableChip(userId, self.gameId, self.tableId)
            ftlog.info('Majiang2.logAnalyse userId:', userId, 'LeaveTableChip:', tableChip, 'tableId:', self.tableId, 'KickOffUser')  
            # 归还牌桌金币
            hallrpcutil.moveAllTableChipToChip(userId, self.gameId, 'TABLE_STANDUP_TCHIP_TO_CHIP', self.roomId, tysessiondata.getClientId(userId), self.tableId)
            hallrpcutil.delTableChips(userId, [self.tableId])

            # 记录玩家站起时的房间信息，金币信息，离开时间
            pluginCross.mj2dao.setQuickStartLastInfo(userId, tableChip,
                                                     tyconfig.getBigRoomId(self.roomId),
                                                     fttime.getCurrentTimestamp())

            # 牌局未结束且牌局开始以后 玩家离开时更新任务信息
            if self.logic_table.isPlaying() \
                and self.logic_table.roundResult:
                self.logic_table.updateTaskInfoProcess(seatId)
            
            player = self.logic_table.getPlayer(seatId)
            if player:
                player.setTableCoin(0)
            # 刷新金币
            hallrpcutil.sendDataChangeNotify(userId, self.gameId, 'udata')
        else:
            # todo，记录机器人的带出
            if self.logic_table.players[seatId]:
                tableChip = self.logic_table.players[seatId].tableCoin
                ftlog.info('Majiang2.logAnalyse userId:', userId, 'LeaveTableChip:', tableChip, 'tableId:', self.tableId, 'KickOffUser')  
        
        pluginCross.onlinedata.removeOnLineLoc(userId, self.roomId, self.tableId)
        self.logic_table.msgProcessor.table_leave(userId, seatId, reason)
        self.logic_table.removePlayer(seatId)
        self.seats[seatId] = TYSeat(self)
    
    def _doStandUp(self, msg, userId, seatId, reason, clientId=-1):
        '''
        玩家操作, 尝试离开当前的座位
        子类需要自行判定userId和seatId是否吻合
        快速麻将桌的站起比较简单
        牌局没开始，站起
        牌局已开始，不处理，超时托管
        '''
        ftlog.info('MajiangQuickTable._doStandUp userId:', userId
                   , ' roomId:', self.roomId
                   , ' tableId:', self.tableId
                   , ' seatId:', seatId
                   , ' reason:', reason)
        self.kickOffUser(userId, seatId, True, reason)
        self.room.updateTableScore(self.getTableScore(), self.tableId)
            
    def userLeave(self, userId, seatId, reason=''):
        if seatId < 0:
            return
        
        ftlog.info('MajiangQuickTable.userLeave user leave, userId:', userId
               , ' seatId:', seatId)
        self.logic_table.playerLeave(seatId) 
        
        isKick = False
        if not self.logic_table.isPlaying():
            isKick = True
            
        if (not isKick) and self.logic_table.player[seatId].isObserver():
            isKick = True
            
        if isKick:
            # 剔除玩家    
            self._doStandUp(None, userId, seatId, reason, -1)
        else:
            # 设置托管
            self.logic_table.setAutoDecideValue(seatId, True)
            # 后台leave导致的托管，要发送托管消息
            if reason == MUserLeaveReason.TABLE_MANAGE:
                self.logic_table.msgProcessor.trusteeInfo(seatId, True, userId)
            
    def _doTableManage(self, msg, action):
        '''桌子内部处理所有的table_manage命令'''
        result = {'isOK' : True}
        if action == 'leave' :
            userId = msg.getParam('userId')
            seatId = self.getSeatIdByUserId(userId)
            self.userLeave(userId, seatId, MUserLeaveReason.TABLE_MANAGE)
        elif action == 'clear_table':
            ftlog.info('MajiangQuickTable.doTableManage clearTable...')
            self.clearTable(True, MUserLeaveReason.TABLE_MANAGE)
        elif action == 'tableTiles':
            if self.logic_table.isPlaying():
                self.logic_table.printTableTiles()
        elif action == 'charge_success':
            if self.logic_table.isPlaying():
                userId = msg.getParam('userId')
                seatId = self.getSeatIdByUserId(userId)
                self.logic_table.processCharge(seatId, MChargeProcessor.ASK_CHARGE_OK)
        elif action == 'enter_background':
            userId = msg.getParam('userId')
            seatId = self.getSeatIdByUserId(userId)
            if seatId >= 0:
                ftlog.info('MajiangQuickTable.doTableManage user enterBackGround userId:', userId
                        , ' seatId:', seatId)
                self.logic_table.playerEnterBackGround(seatId)
                self.logic_table.sendPlayerLeaveMsg(seatId)
        elif action == 'resume_foreground':
            userId = msg.getParam('userId')
            seatId = self.getSeatIdByUserId(userId)
            if seatId >= 0:
                ftlog.debug('MajiangQuickTable.doTableManage user resumeForeGround userId:', userId
                        , ' seatId:', seatId)
                self.logic_table.playerResumeForeGround(seatId)
                self.logic_table.sendPlayerLeaveMsg(seatId)
                
        return result
        
    def getSeatIdByUserId(self, userId):
        """根据userId获取座位号"""
        for index in range(self.maxSeatN):
            if self.seats[index][TYSeat.INDEX_SEATE_USERID] == userId:
                return index
        return -1
        
    def clearTable(self, sendLeave, reason='clearTable'):
        """清理桌子"""
        ftlog.info('MajiangQuickTable.clearTable tableId:', self.tableId
                , ' now seats: ', self.seats)
        self.__timer.cancelTimerAll()
        if self.__looper_timer:
            self.__looper_timer.cancel()
            self.__looper_timer = None
        
        self.setAddRobotInterval(-1)
        
        # 清理用户座位
        for seatId in range(self.maxSeatN):
            if self.seats[seatId][TYSeat.INDEX_SEATE_USERID] != 0:
                self.kickOffUser(self.seats[seatId][TYSeat.INDEX_SEATE_USERID], seatId, sendLeave, reason)
        # 结束游戏
        self.logic_table.reset()
        # 释放桌子
        tableScore = self.getTableScore()
        ftlog.debug('MajiangQuickTable.clearTable tableScore:', tableScore)
        self.room.updateTableScore(tableScore, self.tableId)
        
    def getTableScore(self):
        '''
        取得当前桌子的快速开始的评分
        越是最适合进入的桌子, 评分越高, 座位已满评分为0
        '''
        if self.maxSeatN <= 0 :
            ftlog.info('MajiangQuickTable.getTableScore return 1')
            return 1
        
        if self.realPlayerNum == self.maxSeatN:
            return 0
        
        if self.realPlayerNum > 0 and self.logic_table.isPlaying():
            ftlog.info('MajiangQuickTable.getTableScore table isPlaying return 0')
            # 血战牌局中可以离开，如果当前牌桌正在打牌，禁止其他人加入
            return 0
        
        return (self.realPlayerNum + 1) * 100 / self.maxSeatN
        
    def saveRecordAfterTable(self):
        """
        {
                "recordTime": 1482236117,
                "tableRecordKey": "1482236094.437114",
                "createTableNo": "437114",
                "record_download_info": [
                    {
                        "url": "http://df.dl.shediao.com/cdn37/majiang/difang/record/record_7_1482236094.437114_1.zip",
                        "fileType": "zip",
                        "MD5": "276F48089FA744EC14CCBB16CFEB028B"
                    },
                    {
                        "url": "http://df.dl.shediao.com/cdn37/majiang/difang/record/record_7_1482236094.437114_2.zip",
                        "fileType": "zip",
                        "MD5": "F5C74E0A76D657B07BBA48542B596BD6"
                    }
                ],
                "deltaScore": -236,
                "playMode": "lichuan",
                "score":10000,
                "users": [
                    {
                        "score": -40,
                        "userId": 10093,
                        "name": "8681-M02",
                        "deltaScore": [
                            -40,
                            0
                        ]
                    },
                    {
                        "score": 316,
                        "userId": 10104,
                        "name": "博大精深",
                        "deltaScore": [
                            120,
                            196
                        ]
                    },
                    {
                        "score": -236,
                        "userId": 10101,
                        "name": "**-G5700",
                        "deltaScore": [
                            -40,
                            -196
                        ]
                    },
                    {
                        "score": -40,
                        "userId": 10100,
                        "name": "Redmi Note 4",
                        "deltaScore": [
                            -40,
                            0
                        ]
                    }
                ]
            }
        """
        tableRecordInfo = {}
        playerCount = self.logic_table.playerCount
        ftId = self.logic_table.getTableConfig(MFTDefine.FTID, '000000')
        userIds = []
        userRecordInfos = []
        # 整体分数处理
        allDeltaScore = [0 for _ in range(playerCount)]

        # 每局分数处理
        roundResults = self.logic_table.tableResult.results
        if len(roundResults) == 0:
            return
        
        allRoundDeltaScore = []
        for roundResult in roundResults:
            """
            #改为从oneresult中统计的方案
            roundDeltaScore = [0 for _ in range(playerCount)]
            for oneResult in roundResult.roundResults:
                if MOneResult.KEY_SCORE in oneResult.results:
                    oneResultScore = oneResult.results[MOneResult.KEY_SCORE]
                    for i in range(playerCount):
                        roundDeltaScore[i] = roundDeltaScore[i] + oneResultScore[i]
                        allDeltaScore[i] = allDeltaScore[i] + oneResultScore[i]
                    ftlog.debug('MajiangQuickTable.saveRecordAfterTable oneResultScore is:', oneResultScore)
                else:
                    ftlog.debug('MajiangQuickTable.saveRecordAfterTable oneResultScore is null')
            allRoundDeltaScore.append(roundDeltaScore)
            ftlog.debug('MajiangQuickTable.saveRecordAfterTable roundDeltaScore is:', roundDeltaScore, ' allDeltaScore is:', allDeltaScore)
            """
            
            if roundResult.score:
                roundDeltaScore = roundResult.score
                ftlog.debug('MajiangQuickTable.saveRecordAfterTable roundDeltaScore is:', roundDeltaScore)
                allRoundDeltaScore.append(roundDeltaScore)
                for i in range(playerCount):
                    allDeltaScore[i] = allDeltaScore[i] + roundDeltaScore[i]
            else:
                ftlog.debug('MajiangQuickTable.saveRecordAfterTable roundResult.score is null')
        
            
        for i in range(0, playerCount):
            cp = self.logic_table.player[i]
            if cp:
                playerRecordInfo = {}
                import time 
                playerRecordInfo['recordTime'] = int(time.time())
                playerRecordInfo['playMode'] = self.playMode
                playerRecordInfo['tableId'] = self.tableId
                playerRecordInfo['createTableNo'] = ftId
                playerRecordInfo['tableRecordKey'] = '%s.%s' % (playerRecordInfo['recordTime'], ftId)
                playerRecordInfo['deltaScore'] = allDeltaScore[i]
                _, playerRecordInfo['playDesc'] = self.get_select_quick_config_items()
                playerRecordInfo['paoUid'] = self.logic_table.tableResult.paoUid
                playerRecordInfo['hostUid'] = self.getTableConfig(MFTDefine.FTOWNER, 0)
                # 回放记录key
                recordDownloadInfos = []
                recordUrls = self.logic_table.recordUrl
                for recordUrl in recordUrls:
                    if recordUrl != None:
                        recordDownloadInfoObj = {}
                        recordDownloadInfoObj['url'] = recordUrl
                        recordDownloadInfoObj['fileType'] = 'zip'
                        recordDownloadInfoObj['MD5'] = ftstr.md5digest(recordDownloadInfoObj['url']).upper()
                        recordDownloadInfos.append(recordDownloadInfoObj)

                playerRecordInfo['record_download_info'] = recordDownloadInfos
                tableRecordInfo[cp.userId] = playerRecordInfo
                userIds.append(cp.userId)
                """
                {
                        "score": -40,
                        "userId": 10100,
                        "name": "Redmi Note 4",
                        "deltaScore": [
                            -40,
                            0
                        ]
                }
                """
                userRecordInfo = {}
                userRecordInfo['score'] = allDeltaScore[i]
                userRecordInfo['userId'] = cp.userId
                userRecordInfo['name'] = cp.name
                userRecordInfo['purl'] = cp.purl
                deltaScore = []
                for roundDeltaScore in allRoundDeltaScore:
                    deltaScore.append(roundDeltaScore[i])
                
                userRecordInfo['deltaScore'] = deltaScore
                userRecordInfos.append(userRecordInfo)
                
        for userId in userIds:
            tableRecordInfo[userId]['users'] = userRecordInfos
        ftlog.debug('MajiangQuickTable.saveRecordAfterTable content:', tableRecordInfo)   
        MJCreateTableRecord.saveTableRecord(tableRecordInfo, self.gameId)
