# -*- coding=utf-8
'''
Created on 2016年9月23日

上行行为处理

@author: zhaol
'''
from majiang2.ai.play_mode import MPlayMode
from majiang2.table.table_config_define import MTDefine
from majiang2.table_state.state import MTableState
from majiang2.table_state_processor.charge_processor import MChargeProcessor
from majiang2.win_rule.win_rule import MWinRule
import random
from majiang2.tile.tile import MTile
from freetime5.util import ftlog
from majiang2.poker2.entity import hallrpcutil


class ActionHandler(object):
    # 出
    ACTION_DROP = 1
    # 吃
    ACTION_CHI = 2
    # 碰
    ACTION_PENG = 3
    # 杠
    ACTION_GANG = 4
    # 听
    ACTION_TING = 5
    # 和
    ACTION_HU = 6
    # 锚/蛋
    ACTION_MAO = 7
    
    def __init__(self):
        super(ActionHandler, self).__init__()
        self.__table = None
        self.__actionId = 0
        
    @property
    def actionId(self):
        return self.__actionId
    
    def setActionId(self, aId):
        self.__actionId = aId
        
    @property
    def table(self):
        return self.__table
    
    def setTable(self, table):
        """设置牌桌"""
        self.__table = table
        
    def processAction(self, cmd):
        pass
    
    def updateTimeOut(self, delta):
        if self.table.addCardProcessor.getState() > 0:
            self.table.addCardProcessor.updateTimeOut(delta)
            
        if self.table.dropCardProcessor.getState() > 0:
            self.table.dropCardProcessor.updateTimeOut(delta)
            
        if self.table.piaoProcessor.getState() > 0:
            self.table.piaoProcessor.updateTimeOut(delta)
            
        if self.table.doubleProcessor.getState() > 0:
            self.table.doubleProcessor.updateTimeOut(delta)

        if self.table.zhisaiziProcessor.getState() > 0:
            self.table.zhisaiziProcessor.updateTimeOut(delta)
            
        if self.table.huanSanZhangProcessor.getState() > 0:
            self.table.huanSanZhangProcessor.updateTimeOut(delta)
            
        if self.table.absenceProcessor.getState() > 0:
            self.table.absenceProcessor.updateTimeOut(delta)
            
        if self.table.pauseProcessor.getState() > 0:
            self.table.pauseProcessor.updateTimeOut(delta)
            ids = self.table.pauseProcessor.updatePauseEvent(delta)
            self.table.processPauseEvents(ids)
            
        if self.table.chargeProcessor.getState() > 0:
            self.table.chargeProcessor.updateTimeOut(delta)
    
    def doAutoAction(self):
        """自动行为，关注当前牌局是否正在开始"""
        if not self.table.isPlaying():
            return

        if self.table.curState() == MTableState.TABLE_STATE_NEXT:
            ftlog.debug('ActionHandler.doAutoAction gameNext...')
            self.table.gameNext()
            return True
        
        if self.table.pauseProcessor.getState() != MTableState.TABLE_STATE_NEXT:
            ftlog.debug('ActionHandler.doAutoAction pause...')
            return True
            
        autoDeciodeSeats, listenSeats = self.table.chargeProcessor.getAutoDecideSeats()
        if len(autoDeciodeSeats) > 0 or len(listenSeats) > 0:
            if len(listenSeats) > 0:
                for seatId in listenSeats:
                    self.autoProcessListenCharge(seatId)
            
            if len(autoDeciodeSeats) > 0:
                for seatId in autoDeciodeSeats:
                    self.autoProcessCharge(seatId)
            return True
        
        if self.table.zhisaiziProcessor.updateProcessor(MTableState.TABLE_STATE_NEXT):
            self.table.autoDecideCrapShoot()
            return True

        if self.table.flowerProcessor.getState() == MTableState.TABLE_STATE_BUFLOWER:
            self.table.autoBuFlower()
            return True

        seats = self.table.absenceProcessor.getAutoDecideSeatsBySchedule()
        for seat in seats:
            self.autoProcessAbsence(seat)
        if len(seats) > 0:
            return True
        
        seats = self.table.huanSanZhangProcessor.getAutoDecideSeatsBySchedule()
        for seat in seats:
            self.autoProcessChangeTiles(seat)
        if len(seats) > 0:
            return True
        
        seats = self.table.piaoProcessor.getAutoDecideSeatsBySchedule()
        for seat in seats:
            self.table.autoDecidePiao(seat)
        if len(seats) > 0:
            return True
        
        seats = self.table.doubleProcessor.getAutoDecideSeatsBySchedule()
        for seat in seats:
            self.table.autoDecideDouble(seat)
        if len(seats) > 0:
            return True
        
        nPause = 0
        if self.actionId != self.table.actionID:
            self.setActionId(self.table.actionID)
            nPause = random.randint(2, 4)

        if MTDefine.INVALID_SEAT != self.table.addCardProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT]):
            ftlog.debug('ActionHandler.addCardProcessor.hasAutoDecideAction curSeat: ', self.table.curSeat
                         , ' trustTeeSet:', self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
            self.autoProcessAddCard(nPause)
            return True
            
        seatIds = self.table.dropCardProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if len(seatIds) > 0:
            ftlog.debug('ActionHandler.dropCardProcessor.hasAutoDecideAction seatIds:', seatIds)
            self.autoProcessDropCard(seatIds, nPause)
            return True
        
        seatId = self.table.louHuProcesssor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if seatId != MTDefine.INVALID_SEAT and \
            (not self.table.dropCardProcessor.getState() & MTableState.TABLE_STATE_HU):
            ftlog.debug('ActionHandler.louHuProcesssor.hasAutoDecideAction seatId:', seatId)
            self.autoProcessLouHu(seatId, nPause)
            return True
        
        seatId = self.table.daFengProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if seatId != MTDefine.INVALID_SEAT:
            self.autoProcessDaFeng(seatId, nPause)
            return True
        
        seatId = self.table.tianHuProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if seatId != MTDefine.INVALID_SEAT:
            self.autoProcessTianHu(seatId, nPause)
            return True
        
        seatId = self.table.shuffleHuProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if seatId != MTDefine.INVALID_SEAT:
            self.autoProcessShuffleHu(seatId, nPause)
            return True
        
        seatId = self.table.addCardHuProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if seatId != MTDefine.INVALID_SEAT:
            self.autoProcessAddCardHu(seatId, nPause)
            return True
        
        seatId = self.table.dropCardHuProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if seatId != MTDefine.INVALID_SEAT:
            self.autoProcessDropCardHu(seatId, nPause)
            return True
        
        seatIds = self.table.qiangGangHuProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if len(seatIds) > 0:
            ftlog.debug('ActionHandler.qiangGangHuProcessor.hasAutoDecideAction seatId:', seatIds)
            self.autoProcessQiangGangHu(seatIds, nPause)
            return True
        
        seatId = self.table.qiangExmaoPengProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if seatId != MTDefine.INVALID_SEAT:
            ftlog.debug('ActionHandler.qiangExmaoPengProcessor.hasAutoDecideAction seatId:', seatId)
            self.autoProcessQiangExmaoPeng(seatId, nPause)
            return True
        
        seatIds = self.table.qiangExmaoHuProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if len(seatIds) > 0:
            ftlog.debug('ActionHandler.qiangExmaoHuProcessor.hasAutoDecideAction seatId:', seatIds[0])
            self.autoProcessQiangExmaoHu(seatIds, nPause)
            return True
        
        seatId = self.table.tingBeforeAddCardProcessor.hasAutoDecideAction(self.table.curSeat, self.table.tableConfig[MTDefine.TRUSTTEE_TIMEOUT])
        if seatId != MTDefine.INVALID_SEAT:
            ftlog.debug('ActionHandler.tingBeforeAddCardProcessor.hasAutoDecideAction seatId:', seatId)
            self.autoProcessTingBeforeAddTile(seatId, nPause)
            return True

        return False
    
    def isRobotFoolish(self):
        '''
        机器人是否是傻瓜AI
        '''
        return (self.table.getTableConfig(MTDefine.ROBOT_LEVEL, MTDefine.ROBOT_LEVEL_NORMAL) == MTDefine.ROBOT_FOOLISH)
    
    def isHumanAutoDecideFoolish(self, player=None):
        '''
        普通人托管后是否是傻瓜AI
        '''
        ftlog.debug('ActionHandler.isHumanAutoDecideFoolish player name:', player.name
                            , 'autoLeave:', self.table.getTableConfig(MTDefine.AUTO_LEVEL, MTDefine.ROBOT_FOOLISH))
        if self.table.playMode == MPlayMode.XUELIUCHENGHE:
            if player and player.isWon():
                ftlog.debug('ActionHandler.isHumanAutoDecideFoolish isWon:', player.isWon())
                return False
        return (self.table.getTableConfig(MTDefine.AUTO_LEVEL, MTDefine.ROBOT_FOOLISH) == MTDefine.ROBOT_FOOLISH)
    
    def consumeSmartOperateCount(self, player):
        '''
        消耗智能操作的机会
        '''
        player.consumeSmartOperateCount()
    
    def autoProcessTingBeforeAddTile(self, seatId, nPause):
        '''
        自动处理摸牌前上听
        '''
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessTingBeforeAddTile player is null, something error!!!')
            return
        
        if (player.isRobot() and self.isRobotFoolish()) or \
            ((not player.isRobot()) and player.autoDecide and self.isHumanAutoDecideFoolish()):
            # 傻瓜级别AI，不抢杠和
            ftlog.debug('ActionHandler.autoProcessTingBeforeAddTile table.playerCancel')
            self.table.playerCancel(seatId)
            return
        
        if nPause != 0:
            self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
            return True
           
        self.consumeSmartOperateCount(player) 
        self.table.tingBeforeAddCard(seatId, self.table.actionID)

    def autoProcessQiangExmaoPeng(self, seatId, nPause):
        '''
        自动处理抢锚碰
        '''
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessQiangExmaoPeng player is null, something error!!!')
            return
        
        if (player.isRobot() and self.isRobotFoolish()) or \
            ((not player.isRobot()) and player.autoDecide and self.isHumanAutoDecideFoolish()):
            # 傻瓜级别AI，不抢杠和
            ftlog.debug('ActionHandler.autoProcessQiangExmaoPeng table.playerCancel')
            self.table.playerCancel(seatId)
            return
        
        if nPause != 0:
            self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
            return True
          
        self.consumeSmartOperateCount(player)  
        state = self.table.qiangExmaoPengProcessor.getState()
        if state & MTableState.TABLE_STATE_GANG:
            extend = self.table.qiangExmaoPengProcessor.exmaoExtend
            gang = extend.getChoosedInfo(MTableState.TABLE_STATE_GANG)
            self.table.gangTile(seatId, gang['pattern'][0], gang['pattern'], MTableState.TABLE_STATE_GANG)
        elif state & MTableState.TABLE_STATE_PENG:
            extend = self.table.qiangExmaoPengProcessor.exmaoExtend
            peng = extend.getChoosedInfo(MTableState.TABLE_STATE_PENG)
            self.table.pengTile(seatId, peng[0], peng, MTableState.TABLE_STATE_PENG)
            
    def autoProcessQiangExmaoHu(self, seatIds, nPause):
        '''
        自动处理抢锚胡
        '''
        for seatId in seatIds:
            player = self.table.player[seatId]
            if not player:
                ftlog.error('ActionHandler.autoProcessQiangExmaoHu player is null, something error!!!')
                return
            
            if (player.isRobot() and self.isRobotFoolish()) or \
                ((not player.isRobot()) and player.autoDecide and self.isHumanAutoDecideFoolish()):
                # 傻瓜级别AI，不抢杠和
                ftlog.debug('ActionHandler.autoProcessQiangExmaoHu table.playerCancel')
                self.table.playerCancel(seatId)
                
        if nPause != 0:
            self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
            return True
            
        if self.table.qiangExmaoHuProcessor.getState() != 0:
            for seatId in seatIds:
                player = self.table.player[seatId]
                self.consumeSmartOperateCount(player)
                if self.table.qiangExmaoHuProcessor.canHuNow(seatId):
                    self.table.gameWin(seatId, self.table.qiangExmaoHuProcessor.tile)
                

    def autoProcessQiangGangHu(self, seatIds, nPause):
        """
        自动处理抢杠和
        """
        humanSeatIds = []
        for seatId in seatIds:
            player = self.table.player[seatId]
            if not player:
                ftlog.error('ActionHandler.autoProcessQiangGangHu player is null, something error!!!')
                return
            
            if (player.isRobot() and self.isRobotFoolish()) or \
                ((not player.isRobot()) and player.autoDecide and self.isHumanAutoDecideFoolish(player)):
                if (self.table.getTableConfig(MTDefine.ROBOT_LEVEL, MTDefine.ROBOT_LEVEL_NORMAL) == MTDefine.ROBOT_FOOLISH):
                    # 傻瓜级别AI，不抢杠和
                    ftlog.debug('ActionHandler.autoProcessQiangGangHu table.playerCancel')
                    self.table.playerCancel(seatId)
                    continue
                
            if nPause != 0:
                self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
                return True
            
            humanSeatIds.append(seatId)
            self.consumeSmartOperateCount(player)

        if len(humanSeatIds) > 0:
            extend = self.table.qiangGangHuProcessor.getExtendResultBySeatId(humanSeatIds[0])
            choose = extend.getChoosedInfo(MTableState.TABLE_STATE_QIANGGANG)
            self.table.gameWin(humanSeatIds[0], choose['tile'], True)

    def autoProcessDropCard(self, seatIds, nPause):
        """托管出牌操作
        简单点儿：
        1）能和就和
        2）能杠就杠
        3）能碰就碰
        4）能吃就吃
        
        特殊说明：
            每次只处理一个人，这样流程是序列化的，排查问题比较简单
        """
        for seatId in seatIds:
            if self.table.dropCardProcessor.getState() == MTableState.TABLE_STATE_NEXT:
                return
            
            player = self.table.player[seatId]
            if not player:
                ftlog.error('ActionHandler.autoProcessDropCard player is null, something error!!!')
                continue
            
            if player.isObserver():
                # 傻瓜级别， 不吃不碰不杠不和
                self.table.playerCancel(seatId)
                ftlog.debug('ActionHandler.autoProcessDropCard table.playerCancel because seatId:', seatId, 'is observer')
                continue
            
            if (player.isRobot() and self.isRobotFoolish()) or \
                ((not player.isRobot()) and player.autoDecide and self.isHumanAutoDecideFoolish(player)):
                # 傻瓜级别， 不吃不碰不杠不和
                self.table.playerCancel(seatId)
                continue

            # 暂时取消，加快速度
            if (nPause != 0) and (not player.isWon()):
                # 胡牌之后，不在延时假装思考
                self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
                return True
             
            self.consumeSmartOperateCount(player)
            extendStrategyInfo = self.getExtendStrategyInfo(player)
            seatState = self.table.dropCardProcessor.getStateBySeatId(seatId)
            nowTile = self.table.dropCardProcessor.tile
            # 用户是否做出过选择
            seatResponse = True if self.table.dropCardProcessor.getResponseBySeatId(seatId) == 0 else False
            if seatState > 0:
                if (seatState & MTableState.TABLE_STATE_HU):
                    
                        
                    if player.isWon() or self.table.dropCardStrategy.isWin(player.copyTiles()
                                            , nowTile
                                            , MWinRule.WIN_BY_OTHERS
                                            , self.table.tableTileMgr.getTiles()
                                            , seatResponse
                                            , extendStrategyInfo):
                        self.table.gameWin(seatId, nowTile, False)
                        continue
                    
                extend = self.table.dropCardProcessor.getExtendResultBySeatId(seatId)
                
                if seatState & MTableState.TABLE_STATE_GANG:
                    choose = extend.getChoosedInfo(MTableState.TABLE_STATE_GANG)
                    ftlog.debug('ActionHandler.autoProcessDropCard gang choose:', choose)
                    special_tile = self.getPiguTile()
                    # AI自动选择杠听
                    if seatState & MTableState.TABLE_STATE_GRABTING:
                        self.table.gangTile(seatId
                            , nowTile
                            , choose['pattern']
                            , choose['style']
                            , MTableState.TABLE_STATE_GANG | MTableState.TABLE_STATE_GRABTING
                            , special_tile)
                        continue
                    else:
                        if player.isWon() or self.table.dropCardStrategy.isGang(player.copyTiles()
                                        , nowTile
                                        , choose
                                        , self.table.tableTileMgr.getTiles()
                                        , player.tingResult
                                        , seatResponse
                                        , extendStrategyInfo
                                        ):
                            self.table.gangTile(seatId
                                , nowTile
                                , choose['pattern']
                                , choose['style']
                                , MTableState.TABLE_STATE_GANG
                                , special_tile)
                            continue
                    
                if seatState & MTableState.TABLE_STATE_PENG:
                    choose = extend.getChoosedInfo(MTableState.TABLE_STATE_PENG)
                    ftlog.debug('ActionHandler.autoProcessDropCard peng choose:', choose)
                    # AI自动选择碰听
                    ftlog.debug('seatId:', seatId, ' nowTile:', nowTile, ' extend:', extend)
                    if seatState & MTableState.TABLE_STATE_GRABTING:
                        self.table.pengTile(seatId, nowTile, choose['pattern'], MTableState.TABLE_STATE_PENG | MTableState.TABLE_STATE_GRABTING)
                        continue
                    else:
                        if self.table.dropCardStrategy.isPeng(player.copyTiles()
                                , nowTile
                                , choose
                                , self.table.tableTileMgr.getTiles()
                                , player.tingResult
                                , seatResponse
                                , extendStrategyInfo):
                            self.table.pengTile(seatId, nowTile, choose, MTableState.TABLE_STATE_PENG)
                            continue
                    
                if seatState & MTableState.TABLE_STATE_CHI:
                    choose = extend.getChoosedInfo(MTableState.TABLE_STATE_CHI)
                    ftlog.debug('ActionHandler.autoProcessDropCard chi choose:', choose)
                    # 这里的准确逻辑是，如果吃的牌在吃听里，继续转听。如果吃的牌不在听牌里，按普通的吃处理
                    if seatState & MTableState.TABLE_STATE_GRABTING:
                        self.table.chiTile(seatId
                                , nowTile
                                , choose['pattern']
                                , MTableState.TABLE_STATE_CHI | MTableState.TABLE_STATE_GRABTING)
                        continue
                    else:
                        if self.table.dropCardStrategy.isChi(player.copyTiles()
                                , nowTile
                                , choose
                                , self.table.tableTileMgr.getTiles()
                                , player.tingResult
                                , seatResponse
                                , extendStrategyInfo):
                            self.table.chiTile(seatId, nowTile, choose, MTableState.TABLE_STATE_CHI)
                            continue
                    
                # 未处理的状态，自动取消
                self.table.playerCancel(seatId)  
                
    def autoProcessLouHu(self, seatId, nPause):
        '''
        自动处理漏胡
        '''
        if self.table.louHuProcesssor.actionID != self.table.actionID:
            ftlog.error('ActionHandler.autoProcessLouHu actionID is wrong, something error!!!')
            return
        
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessLouHu player is null, something error!!!')
            return
        
        if (player.isRobot() and self.isRobotFoolish()) or \
            ((not player.isRobot()) and player.autoDecide and self.isHumanAutoDecideFoolish()):
            self.table.playerCancel(seatId)
            return
        
        if nPause != 0:
            self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
            return True
        
        self.consumeSmartOperateCount(player)
        self.table.gameWin(seatId, self.table.louHuProcesssor.tile)
        
    def autoProcessDaFeng(self, seatId, nPause):
        '''
        自动处理刮大风
        '''
        if self.table.daFengProcessor.actionID != self.table.actionID:
            ftlog.error('ActionHandler.autoProcessDaFeng actionID is wrong, something error!!!')
            return
        
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessDaFeng player is null, something error!!!')
            return
        
        if (player.isRobot() and self.isRobotFoolish()) or \
            ((not player.isRobot()) and player.autoDecide and self.isHumanAutoDecideFoolish()):
            self.table.playerCancel(seatId)
            return
        
        if nPause != 0:
            self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
            return True
            
        self.consumeSmartOperateCount(player)
        self.table.gameWin(seatId, self.table.daFengProcessor.tile)
        
    def autoProcessTianHu(self, seatId, nPause):
        '''
        自动处理天胡
        '''
        if self.table.tianHuProcessor.actionID != self.table.actionID:
            ftlog.error('ActionHandler.autoProcessTianHu actionID is wrong, something error!!!')
            return
        
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessTianHu player not valid...')
            return
        
        if nPause != 0:
            self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
            return True
          
        self.consumeSmartOperateCount(player)
        self.table.gameWin(seatId, self.table.tianHuProcessor.tile)
        
    def autoProcessShuffleHu(self, seatId, nPause):
        '''
        自动处理发牌胡
        '''
        if self.table.shuffleHuProcessor.actionID != self.table.actionID:
            return
        
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessShuffleHu player not valid...')
            return
        
        if nPause != 0:
            self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
            return True
            
        self.consumeSmartOperateCount(player)
        self.table.gameWin(seatId, self.table.shuffleHuProcessor.tile)
        
    def autoProcessAddCardHu(self, seatId, nPause):
        '''
        自动处理摸牌胡
        '''
        if self.table.addCardHuProcessor.actionID != self.table.actionID:
            ftlog.error('ActionHandler.autoProcessAddCardHu actionID is wrong, something error!!!')
            return
        
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessAddCardHu player not valid...')
            return
        
        if nPause != 0:
            self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
            return True
            
        self.consumeSmartOperateCount(player)
        self.table.gameWin(seatId, self.table.addCardHuProcessor.tile)
        
    def autoProcessDropCardHu(self, seatId, nPause):
        '''
        自动处理出牌胡
        '''
        if self.table.dropCardHuProcessor.actionID != self.table.actionID:
            ftlog.error('ActionHandler.autoProcessDropCardHu actionID is wrong, something error!!!')
            return
        
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessAddCardHu player not valid...')
            return
        
        if nPause != 0:
            self.table.pauseProcessor.addPauseEvent(nPause * 0.5)
            return True
            
        self.consumeSmartOperateCount(player)
        self.table.gameWin(seatId, self.table.dropCardHuProcessor.tile)
    
    def autoProcessListenCharge(self, seatId):
        '''
        监听用户充值是否成功
        '''
        uChip = hallrpcutil.getChip(self.table.player[seatId].userId)
        # 判断用户现在的金币是否大于buyIn
        buyIn = self.table.roomConfig.get(MTDefine.BUYIN_CHIP, 0)
        # 用户外面的金币大于的话，则充值成功
        if uChip >= buyIn:
            self.table.processCharge(seatId, MChargeProcessor.ASK_CHARGE_OK)
    
    def autoProcessCharge(self, seatId):
        '''
        自动处理充值
        '''
        ftlog.debug("ActionHandler.autoProcessCharge Charge.actionId:", self.table.chargeProcessor.actionID, 'table.actionId:', self.table.actionID)
        if self.table.chargeProcessor.actionID != self.table.actionID:
            ftlog.error('ActionHandler.autoProcessCharge actionID is wrong, something error!!!')
            return
        
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessAddCardHu player not valid...')
            return
        
        self.consumeSmartOperateCount(player)
        # 默认不充值
        self.table.processCharge(seatId, MChargeProcessor.ASK_CHARGE_NO)
        
    def autoProcessAbsence(self, seatId):
        '''
        自动处理定缺
        '''
        ftlog.debug('ActionHandler.autoProcessAbsence seatId:', seatId)
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessAbsence player not valid...')
            return
        
        self.consumeSmartOperateCount(player)
        self.table.processAbsence(seatId)
        
    def autoProcessChangeTiles(self, seatId):
        '''
        自动处理换三张
        '''
        ftlog.debug('ActionHandler.autoProcessChangeTiles seatId:', seatId)
        player = self.table.player[seatId]
        if not player:
            ftlog.error('ActionHandler.autoProcessChangeTiles player not valid...')
            return
        
        self.consumeSmartOperateCount(player)
        self.table.processChangeTiles(seatId)
                
    def autoProcessAddCard(self, nPause):
        '''
        自动处理摸牌
        '''
        player = self.table.addCardProcessor.getPlayer()
        nowTile = self.table.addCardProcessor.getTile()
        extendStrategyInfo = self.getExtendStrategyInfo(player)

        # 海底且不出牌时，gameNext
        if self.table.tableTileMgr.isHaidilao() \
            and (not self.table.tableTileMgr.canDropWhenHaidiLao()) \
            and (not self.table.addCardProcessor.getState() & MTableState.TABLE_STATE_HU):
            self.table.addCardProcessor.reset()
            self.table.gameNext()
            return

        if (player.isRobot() and self.isRobotFoolish()) or \
            ((not player.isRobot()) and player.autoDecide and self.isHumanAutoDecideFoolish(player)):
            '''
            AI是傻瓜级别，抓什么打什么
            如果有缺牌，则自动打出缺牌
                如果nowTile是缺牌，则优先打出nowTile
                
            如果没有缺牌并且nowTile也不是缺牌，则打出nowTile
            
            '''
            if self.table.checkTableState(MTableState.TABLE_STATE_ABSENCE):
                abColor = self.table.getAbsenceColor(player.curSeatId)
                hands = player.copyHandTiles()
                abTiles = MTile.filterTiles(hands, abColor)
                if (len(abTiles) > 0) and (nowTile not in abTiles):
                    nowTile = abTiles[0]

            # 剔除赖子
            hands = player.copyHandTiles()
            mts = self.table.tableTileMgr.getMagicTiles()
            afterTiles = MTile.filterMagicTiles(hands, mts)
            ftlog.debug('autoProcessAddCard:', nowTile,hands,afterTiles)
            if nowTile not in afterTiles:
                if (len(afterTiles) > 0):
                    nowTile = afterTiles[-1]

            self.table.dropTile(player.curSeatId, nowTile)
            return
        
        self.consumeSmartOperateCount(player)
        
        exInfo = self.table.addCardProcessor.extendInfo
        winScore = 0
        if self.table.addCardProcessor.getState() & MTableState.TABLE_STATE_HU:
            winScore = player.getTingResultScore(MWinRule.WIN_BY_MYSELF)
            
        tingScore = 0
        tingInfo = None
        # 添加判断条件玩家是否胡牌，胡牌后，不走听
        if (self.table.addCardProcessor.getState() & MTableState.TABLE_STATE_TING) and not player.isWon():
            tingInfo = exInfo.getChoosedInfo(MTableState.TABLE_STATE_TING)
            ftlog.debug('ActionHandler.autoProcessAddCard tingInfo:', tingInfo)
            tingScore = tingInfo.get('value', 0)
        
        if (self.table.addCardProcessor.getState() & MTableState.TABLE_STATE_HU) and (winScore >= tingScore):
            self.table.gameWin(player.curSeatId, nowTile)
            return
        
        if (self.table.addCardProcessor.getState() & MTableState.TABLE_STATE_TING) and (not player.isWon()):
            if self.table.addCardProcessor.getState() & MTableState.TABLE_STATE_GANG:
                gangs = exInfo.getChiPengGangResult(MTableState.TABLE_STATE_GANG)
                allDropTilesInTing = exInfo.getAllDropTilesInTing()
                for gangInfo in gangs:
                    if gangInfo['pattern'][0] in allDropTilesInTing:
                        style = gangInfo['style']
                        pattern = gangInfo['pattern']
                        special_tile = self.getPiguTile()
                        self.table.gangTile(player.curSeatId, gangInfo['pattern'][0], pattern, style, MTableState.TABLE_STATE_GANG, special_tile)
                        return
            
            # 选择打掉的牌，用剩下的牌听，自动选择可胡牌数最多的解，默认不扣任何牌
            if tingInfo and self.table.dropCardStrategy.isTing(player.copyTiles()
                                    , tingInfo['dropTile']
                                    , self.table.tableTileMgr.getTiles()
                                    , False
                                    , extendStrategyInfo
                                    ):
                self.table.tingAfterDropCard(player.curSeatId, tingInfo['dropTile'], True, [], self.table.addCardProcessor.extendInfo)
                return
        
        ftlog.debug('ActionHandler.autoProcessAddCard player.copyTiles:', player.copyTiles(), 'isStateFixeder:', player.isStateFixeder())
        minTile, minValue = self.table.dropCardStrategy.getBestDropTile(player.copyTiles()
            , self.table.tableTileMgr.getTiles()
            , nowTile
            , player.isStateFixeder()
            , self.table.tableTileMgr.getMagicTiles(player.isTing())
            , extendStrategyInfo)
        ftlog.debug('ActionHandler.getBestDropTile minTile:', minTile, ' minValue:', minValue)

        if self.table.addCardProcessor.getState() & MTableState.TABLE_STATE_GANG:
            gangInfo = exInfo.getChoosedInfo(MTableState.TABLE_STATE_GANG)
            # 第一种情况，当前策略允许杠
            if self.table.dropCardStrategy.isGang(player.copyTiles()
                        , nowTile
                        , gangInfo
                        , self.table.tableTileMgr.getTiles()
                        , player.tingResult
                        , False
                        , extendStrategyInfo):
                exInfo.updateState(MTableState.TABLE_STATE_GANG, gangInfo)
                ftlog.debug('ActionHandler.autoProcessAddCard gangInfo:', gangInfo
                            , ' strategy decide gang')
                style = gangInfo['style']
                pattern = gangInfo['pattern']
                special_tile = self.getPiguTile()
                self.table.gangTile(player.curSeatId, nowTile, pattern, style, MTableState.TABLE_STATE_GANG, special_tile)
                return
            
            # 第二种情况，当前的最佳出牌是杠牌
            gangs = exInfo.getChiPengGangResult(MTableState.TABLE_STATE_GANG)
            for gangInfo in gangs:
                gangTile = gangInfo['pattern'][0]
                if gangTile != minTile:
                    continue
                
                exInfo.updateState(MTableState.TABLE_STATE_GANG, gangInfo)
                ftlog.debug('ActionHandler.autoProcessAddCard gangInfo:', gangInfo
                            , ' gangTile:', gangTile
                            , ' minTile:', minTile
                            , ' gangTile same with minTile, gang!!!')
                style = gangInfo['style']
                pattern = gangInfo['pattern']
                special_tile = self.getPiguTile()
                self.table.gangTile(player.curSeatId, nowTile, pattern, style, MTableState.TABLE_STATE_GANG, special_tile)
                return
        
        # 最后，出价值最小的牌
        self.table.tingAfterDropCard(player.curSeatId, minTile, player.isTing(), [], exInfo)
        
    def getPiguTile(self):
        """获取翻屁股"""
        if self.table.checkTableState(MTableState.TABLE_STATE_FANPIGU):
            pigus = self.table.tableTileMgr.getPigus()
            if pigus and len(pigus) > 0:
                return pigus[0]
        return None
    
    def getExtendStrategyInfo(self, player):
        '''
        获取AI策略的扩展参数
        '''
        extendStrategyInfo = {'tingRule':self.table.tingRule, 'seatId': player.curSeatId}
        if self.table.tableStater.states & MTableState.TABLE_STATE_ABSENCE:
            extendStrategyInfo['absenceColor'] = self.table.absenceProcessor.absenceColor
        return extendStrategyInfo