# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.poker2.entity import hallrpcutil
from tuyoo5.game import tysessiondata
"""
牌桌充值状态处理器

充值的逻辑：
1）首先尝试从uChip补充金币，补充[minChip, uChip/buyin]中的最大值。
2）如果uChip不足minChip，推荐购买，购买走大厅。
游戏GT监听购买成功事件，自动给GT发送补充金币的table_manage action，补充[minChip, uChip/buyin]中的最大值
3）超时后，用户认输
"""
from freetime5.util import ftlog
from majiang2.entity.util import Majiang2Util
from majiang2.table.table_config_define import MTDefine
from majiang2.table_state.state import MTableState
from majiang2.table_state_processor.processor import MProcessor


class MChargeProcessor(MProcessor):
    CHARGE_NONEED = 2  # 没必要充值
    CHARGE_ING = 1  # 正在充值
    CHARGE_OK = 0  # 充值成功
    CHARGE_TIMEOUT = -1  # 充值超时
    CHARGE_FAIL = -2  # 充值失败
    
    ASK_CHARGE_OK = 1
    ASK_CHARGE_NO = -1
    
    # 充值金币
    CHARGE_TYPE_COIN = 1 
    # 充值金钱或者钻石
    CHARGE_TYPE_BUY = 2
    
    def __init__(self, playerCount, tableConfig):
        super(MChargeProcessor, self).__init__(tableConfig)
        self.__state = MTableState.TABLE_STATE_NEXT
        self.__playerCount = playerCount
        self.__charge_states = [self.CHARGE_NONEED] * self.playerCount
        self.__charge_chip = [0] * self.playerCount
        self.__gang_info = None
        self.__charge_type = [0 for _ in range(self.playerCount)]
        
    def reset(self):
        """重置数据"""
        self.__state = MTableState.TABLE_STATE_NEXT
        self.__charge_states = [self.CHARGE_NONEED] * self.playerCount
        self.__charge_chip = [0] * self.playerCount
        self.__charge_type = [0 for _ in range(self.playerCount)]
    @property
    def chargeType(self): 
        return self.__charge_type
    
    def setChargeType(self, typeList):
        self.__charge_type = typeList
       
    @property
    def gangInfo(self):
        return self.__gang_info
    
    def setGangInfo(self, info):
        self.__gang_info = info
        
    @property
    def chargeState(self):
        return self.__charge_states
    
    @property
    def chargeChip(self):
        return self.__charge_chip
    
    def setChargeChip(self, chip):
        self.__charge_chip = chip
        
    @property
    def playerCount(self):
        return self.__playerCount
    
    def setPlayerCount(self, count):
        self.__playerCount = count
        
    @property
    def state(self):
        """获取本轮出牌状态"""
        return self.__state
    
    def getState(self):
        return self.state
    
    def setState(self, state):
        self.__state = state
        
    def isAllCharged(self):
        for seatId in range(self.playerCount):
            if self.chargeState[seatId] == self.CHARGE_ING:
                return False
        ftlog.debug('MChargeProcessor isAllCharged True') 
        return True
    
    def addUser(self, seatId):
        '''
        刮风下雨或者一炮多响时，会有多个玩家需要充值
        
        当前玩家状态变为充值中
        '''
        ftlog.debug('MChargeProcessor addUser seatId:', seatId)
        self.chargeState[seatId] = self.CHARGE_ING
    
    def initProcessor(self, actionId, timeOut, pauseProcessor):
        '''
        初始化处理器，开始发送消息，引导玩家付费
        '''
        ftlog.debug('MChargeProcessor.initProcessor actionId:', actionId
                    , ' timeOut:', timeOut
                    , ' chargeState:', self.chargeState)
        
        self.setActionID(actionId)
        self.setTimeOut(timeOut)
        self.setState(MTableState.TABLE_STATE_CHARGE)
        for seatId in range(self.playerCount):
            if self.chargeState[seatId] == self.CHARGE_ING:
                # 广播此人的正在充值状态
                self.msgProcessor.table_call_broadcast_charging(seatId, actionId, timeOut)
                # 计算充值方案
                minChip = self.roomConfig.get(MTDefine.MIN_COIN, 0)
                if minChip < 0:
                    minChip = 0
                
                userId = self.players[seatId].userId
                uChip = userchip.getChip(userId)
                tableCoin = userchip.getTableChip(userId, self.gameId, self.tableId)
                buyIn = self.roomConfig.get(MTDefine.BUYIN_CHIP, 0)
                ftlog.debug('MChargeProcessor.initProcessor minChip:', minChip
                    , ' uChip:', uChip
                    , ' buyIn:', buyIn
                    , ' roomConfig:', self.roomConfig
                    , ' pluginVer:', self.players[seatId].pluginVer)
                
                clientId = Majiang2Util.getClientId(userId)
                if minChip > uChip + tableCoin:
                    # 类型为充值
                    self.chargeType[seatId] = self.CHARGE_TYPE_BUY
                    # 准入金币大于玩家所有的金币总和
                    self.chargeChip[seatId] = buyIn
                    # 根据玩家插件版本号弹相应的商品
                    if self.players[seatId].pluginVer > 5.01:
                        dis = "由于您的金币不足，请补充后继续游戏"
                        luckBuyOrLessBuyChip = hallpopwnd.makeTodoTaskDiamondToCoin(self.gameId
                                    , userId
                                    , clientId
                                    , buyIn
                                    , dis
                                    , self.timeOut
                                    , False
                                    , 2)  
                        
                        if not luckBuyOrLessBuyChip:
                            luckBuyOrLessBuyChip = hallpopwnd.makeTodoTaskBuyTableChip(self.gameId
                                    , userId
                                    , clientId
                                    , buyIn
                                    , dis
                                    , self.timeOut
                                    , False
                                    , 2)  
                    else:
                        # 5.01版本弹这个商品
                        luckBuyOrLessBuyChip = hallpopwnd.makeTodoTaskLuckBuy(self.gameId, userId, clientId, self.roomId)
                        if not luckBuyOrLessBuyChip:
                            luckBuyOrLessBuyChip = hallpopwnd.makeTodoTaskLessbuyChip(self.gameId, userId, clientId, self.roomId)
                        
                    if luckBuyOrLessBuyChip:
                        TodoTaskHelper.sendTodoTask(self.gameId, userId, luckBuyOrLessBuyChip)
                    else:
                        ftlog.info('MChargeProcessor.initProcessor no product to recommend...')
                else:
                    self.chargeType[seatId] = self.CHARGE_TYPE_COIN
                    if uChip > buyIn:
                        self.chargeChip[seatId] = buyIn
                    else:
                        self.chargeChip[seatId] = uChip
                    
                    # 询问此人充值方案
                    dis = '由于您的金币不足，请补充后继续打牌'
                    content = '带入' + str(self.chargeChip[seatId]) + '金币'
                    promote = '背包剩余金币：' + str(userchip.getChip(userId))
                    message = self.msgProcessor.table_call_ask_charge(seatId, actionId, timeOut, self.chargeChip[seatId], dis, content, promote)
                    # 延时两秒发送
                    pauseProcessor.addDelayTask(2, self.players[seatId].userId, message, self.msgProcessor)
        
        ftlog.debug('MChargeProcessor.initProcessor actionId:', actionId
                    , ' state:', self.state
                    , ' chargeState:', self.chargeState
                    , ' chargeCoin:', self.chargeChip)
        
    def isUserChipNotEnough(self, seatId):
        '''
        用户身上的金币是否不够
        '''
        # 判断该用户是否为None
        if not self.players[seatId]:
            return True
        
        userId = self.players[seatId].userId
        uChip = userchip.getChip(userId)
        tableCoin = self.players[seatId].getTableCoin(self.gameId, self.tableId)
        baseChip = self.tableConfig.get(MTDefine.BASE_CHIP, 0)
        clientId = Majiang2Util.getClientId(userId)
        _, clientVer, _ = strutil.parseClientId(clientId)
        ftlog.debug('MChargeProcessor.isUserChipNotEnough clientVer:', clientVer)
        # 5.0 不弹充值
        if clientVer > 5.0:
            if baseChip > tableCoin:
                return True
            else:
                return False
        if baseChip > (uChip + tableCoin):
            luckBuyOrLessBuyChip = hallpopwnd.makeTodoTaskLuckBuy(self.gameId
                    , userId
                    , clientId
                    , self.roomId)
            
            if not luckBuyOrLessBuyChip:
                luckBuyOrLessBuyChip = hallpopwnd.makeTodoTaskLessbuyChip(self.gameId
                        , userId
                        , clientId
                        , self.roomId)
                
            if luckBuyOrLessBuyChip:
                TodoTaskHelper.sendTodoTask(self.gameId, userId, luckBuyOrLessBuyChip)
            else:
                ftlog.info('MChargeProcessor.initProcessor no product to recommend...')
            return True
        
        return False
        
    def autoChargeCoin(self, seatId):
        '''
        继续下一局时的自动带入金币
        '''
        if self.players[seatId].isRobot():
            return 
        
        # 免费场 不提示充值引导
        if self.roomConfig.get('level', MTDefine.FREE) == MTDefine.FREE:
            return 
        
        baseChip = self.tableConfig.get(MTDefine.BASE_CHIP, 0)
        if baseChip < 0:
            baseChip = 0
        
        userId = self.players[seatId].userId
        uChip = userchip.getChip(userId)
        uDiamond = userchip.getDiamond(userId)
        tableCoin = userchip.getTableChip(userId, self.gameId, self.tableId)
        if tableCoin != self.players[seatId].getTableCoin(self.gameId, self.tableId):
            self.players[seatId].setTableCoin(tableCoin)
            
        buyIn = self.roomConfig.get(MTDefine.BUYIN_CHIP, 0)
        ftlog.debug('MChargeProcessor.autoChargeCoin baseChip:', baseChip
            , ' tableCoin:', self.players[seatId].getTableCoin(self.gameId, self.tableId)
            , ' uChip:', uChip
            , ' buyIn:', buyIn
            , ' roomConfig:', self.roomConfig)
        
        clientId = Majiang2Util.getClientId(userId)
        # 第一次带入的时候，要么buyIn==tableCoin 要么uChip为0
        if buyIn > tableCoin and uChip != 0 :
            changeChip = uChip
            # 大于一倍 则让玩家牌桌金币为buyIn 否则全部带入
            if uChip + tableCoin > buyIn:
                changeChip = buyIn - tableCoin
            
            tfinal, final, delta = hallrpcutil.setTableChipToN(userId
                    , self.gameId
                    , changeChip + self.players[seatId].getTableCoin(self.gameId, self.tableId)
                    , 'CHIP_TO_TABLE_TCHIP'
                    , 0
                    , clientId
                    , self.tableId
            )
            ftlog.info('Majiang2.logAnalyse userId:', userId
                            , 'tableCoin:', self.players[seatId].getTableCoin(self.gameId, self.tableId)
                            , 'ChargeChip:', changeChip
                            , 'tableId:', self.tableId
                            , 'ChargeChip')
            self.players[seatId].setCoin(hallrpcutil.getChip(userId))
            tableCoin = hallrpcutil.getTableChip(userId, self.gameId, self.tableId)
            self.players[seatId].setTableCoin(tableCoin)
            # 通知前端金币发生变化
            datachangenotify.sendDataChangeNotify(self.gameId, userId, 'udata')
            ftlog.debug('MChargeProcessor.autoChargeCoin setTableChipToN, tfinal:', tfinal
                        , ' final:', final
                        , ' delta:', delta
                        , ' uChip:', self.players[seatId].coin
                        , ' tableChip:', self.players[seatId].getTableCoin(self.gameId, self.tableId)
                        , ' userId:', userId
                        , ' gameId:', self.gameId
                        , ' seatId:', seatId)    
            # 通知前端积分变化
            allCoin = [0 for _ in range(self.playerCount)]
            allTableCoin = [0 for _ in range(self.playerCount)]
            for i in range(self.playerCount):
                if self.players[i]:
                    allCoin[i] = userchip.getChip(self.players[i].userId)
                    allTableCoin[i] = userchip.getTableChip(self.players[i].userId, self.gameId, self.tableId)
            currentScore = [0 for _ in range(self.playerCount)]
            delta = [0 for _ in range(self.playerCount)]
            self.msgProcessor.table_call_score(allCoin
                                               , allTableCoin
                                               , currentScore
                                               , delta
                                               , False)
            
            self.msgProcessor.table_call_coin_detail(seatId, changeChip, final, uDiamond)
        
    def updateProcessor(self, actionId, seatId, chargeResult, dis=''):
        '''
        更新某个玩家的购买结果
        '''
        if self.getState() != MTableState.TABLE_STATE_CHARGE:
            return False
        
        if chargeResult == self.ASK_CHARGE_NO:
            self.chargeState[seatId] = self.CHARGE_FAIL
            ftlog.debug('MChargeProcessor.updateProcessor player name:', self.players[seatId].name, 'confirmLoose')
            self.players[seatId].confirmLoose()
        else:
            self.chargeState[seatId] = self.CHARGE_OK
            # 带入金币
            userId = self.players[seatId].userId
            # 钻石数量
            uDiamond = userchip.getDiamond(userId)
            tfinal, final, delta = userchip.setTableChipToN(userId
                    , self.gameId
                    , self.chargeChip[seatId] + self.players[seatId].getTableCoin(self.gameId, self.tableId)
                    , 'CHIP_TO_TABLE_TCHIP'
                    , 0
                    , tysessiondata.getClientId(userId)
                    , self.tableId
            )
            dis += '已为您带入' + str(self.chargeChip[seatId]) + '金币，还有' + str(tfinal) + '金币，继续游戏...'
            ftlog.info('Majiang2.logAnalyse userId:', userId
                            , 'tableCoin:', self.players[seatId].getTableCoin(self.gameId, self.tableId)
                            , 'ChargeChip:', self.chargeChip[seatId]
                            , 'tableId:', self.tableId
                            , 'ChargeChip')
            self.players[seatId].setCoin(hallrpcutil.getChip(userId))
            tableCoin = hallrpcutil.getTableChip(userId, self.gameId, self.tableId)
            self.players[seatId].setTableCoin(tableCoin)
            # 通知前端背包金币发生变化
            datachangenotify.sendDataChangeNotify(self.gameId, userId, 'udata')
            ftlog.debug('MChargeProcessor.updateProcessor setTableChipToN, tfinal:', tfinal
                        , ' final:', final
                        , ' delta:', delta
                        , ' uChip:', self.players[seatId].coin
                        , ' tableChip:', self.players[seatId].getTableCoin(self.gameId, self.tableId)
                        , ' userId:', userId
                        , ' gameId:', self.gameId
                        , ' seatId:', seatId)
            self.msgProcessor.table_call_coin_detail(seatId, self.chargeChip[seatId], final, uDiamond)
        self.msgProcessor.table_call_charged(seatId, actionId, self.chargeState[seatId], dis)
        if self.isAllCharged():
            self.reset()
        return True
            
    def getAutoDecideSeats(self):
        """根据座位号，获取托管的座位号列表"""
        autoDecideSeats = []
        listenSeats = []
        if self.state == MTableState.TABLE_STATE_NEXT:
            return autoDecideSeats, listenSeats
   
        for index in range(self.playerCount):
            if self.chargeState[index] != self.CHARGE_ING:
                continue
            if self.players[index].isRobot():
                autoDecideSeats.append(index)
            
            if (self.timeOut <= 0) and (not self.isNeverAutoDecide()) and (index not in autoDecideSeats):
                autoDecideSeats.append(index)
            
            if (self.chargeType[index] == self.CHARGE_TYPE_BUY) and (index not in listenSeats) and (index not in autoDecideSeats):
                listenSeats.append(index)
                
        if len(autoDecideSeats) > 0 or len(listenSeats) > 0:
            ftlog.debug('MChargeProcessor.getAutoDecideSeatsBySchedule autoDecideSeats:', autoDecideSeats, 'listenSeats:', listenSeats)
                    
        return autoDecideSeats, listenSeats
