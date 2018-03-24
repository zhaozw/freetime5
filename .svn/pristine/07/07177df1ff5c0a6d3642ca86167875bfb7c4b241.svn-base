# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
"""
出牌的操作处理
人数：
吃 - 一个人
碰 - 一个人
杠 - 一个人
胡 - 多个人。赛制上，有抢胡/一炮多响等2个玩法

情况：
一个人出牌，可能有人吃，有人碰，有人杠，有人胡
有的人同时可以吃/碰/杠/胡

流程：
1）是最高优先级且唯一，响应此操作，本轮状态重置，结束。
2）是最高优先级但不唯一，只可能是一炮多响，本人胡牌，继续等待其他人胡牌，取消其他状态。
3）不是最高优先级，非和，等待其他人响应结束。选取最高优先级执行。
"""
from freetime5.util import ftlog
from majiang2.ai.play_mode import MPlayMode
from majiang2.player.player import MPlayer
from majiang2.table.run_mode import MRunMode
from majiang2.table_state.state import MTableState
from majiang2.table_state_processor.extend_info import MTableStateExtendInfo
from majiang2.table_state_processor.processor import MProcessor
from majiang2.table_tile.table_tile_factory import MTableTileFactory


class MDropCardProcessor(MProcessor):
    """
    一个人出牌，其他人响应的状态处理
    每个人都可以吃/碰/杠/和
    根据优先级响应行为
    
    默认处理：
    超时，其他人的操作都视为放弃，
    """
    
    def __init__(self, count, playMode, tableConfig):
        super(MDropCardProcessor, self).__init__(tableConfig)
        self.__processors = [{"state": MTableState.TABLE_STATE_NEXT, "extendInfo": None, "response": 0} for _ in range(count)]
        self.__count = count
        self.__tile = 0
        self.__cur_seat_id = 0
        self.__play_mode = playMode
        
    @property
    def count(self):
        return self.__count

    def setCount(self, count):
        self.__count = count

    def getTile(self):
        """
        获取当前手牌
        """
        return self.__tile
    
    @property
    def curSeatId(self):
        """获取当前座位号"""
        return self.__cur_seat_id
    
    def setCurSeatId(self, seatId):
        self.__cur_seat_id = seatId
    
    def getSeatsBySchedule(self):
        """根据座位号，获取吃牌的座位号列表"""
        seats = []
        for index in range(self.__count - 1):
            seats.append((self.curSeatId + index + 1) % self.__count)
        return seats
    
    def getAutoDecideSeatsBySchedule(self, trustTee):
        """根据座位号，获取托管的座位号列表"""
        seats = []
        
        for index in range(self.__count - 1):
            nextSeat = (self.curSeatId + index + 1) % self.__count
            
            if self.isUserAutoDecided(nextSeat, trustTee, self.getStateBySeatId(nextSeat), self.getResponseBySeatId(nextSeat) == 0):
                seats.append(nextSeat)
        
        if len(seats) > 0:
            ftlog.debug('MDropCardProcessor.getAutoDecideSeatsBySchedule seats:', seats)  
                  
        return seats
    
    def getStateBySeatId(self, seatId):
        """根据seatId获取出牌状态"""
        return self.__processors[seatId]['state']
    
    def setStateBySeatId(self, seatId, state):
        """设置某人的状态"""
        self.__processors[seatId]['state'] = state
    
    def getResponseBySeatId(self, seatId):
        """根据seatId获取响应状态"""
        return self.__processors[seatId]['response']
    
    def getState(self):
        """获取本轮出牌状态"""
        state = 0
        for seat in range(self.__count):
            state = state | self.__processors[seat]['state']
        
        if state != MTableState.TABLE_STATE_NEXT:
            ftlog.info('MDropCardProcessor.getState return:', state)    
        return state
    
    @property
    def processors(self):
        return self.__processors
            
    def reset(self):
        """重置数据"""
        self.__processors = [{"state": 0, "extendInfo": None, "response": 0} for _ in range(self.__count)]
        self.__tile = 0
        self.__cur_seat_id = 0
        ftlog.debug('MDropCardProcessor.reset now processors:', self.__processors)
        
    def resetSeatId(self, seatId):
        """重置某个座位，用户放弃"""
        self.__processors[seatId] = {"state": 0, "extendInfo": None, "response": 0}
        if self.getState() == 0:
            # 加入此人的门前手牌当中
            ftlog.debug('MDropCardProcessor.resetSeatId, seatId:', seatId
                    , ' choose cancel, put tile to men tiles:', self.__tile
                    , ' oldSeatId:', self.__cur_seat_id)
            self.tableTileMgr.setMenTileInfo(self.__tile, self.__cur_seat_id)
            
        ftlog.debug('MDropCardProcessor.resetSeatId now processors:', self.__processors)
        return True
    
    def resetSeatIdExceptWin(self, seatId):
        """重置用户状态，除了胡牌"""
        if self.getStateBySeatId(seatId) & MTableState.TABLE_STATE_HU:
            self.setStateBySeatId(seatId, MTableState.TABLE_STATE_HU)
        else:
            self.resetSeatId(seatId)
        
    def initTile(self, tile, curSeat):
        """初始化本轮手牌，用做校验"""
        ftlog.debug('MDropCardProcessor.initTile:', tile)
        self.__tile = tile
        self.__cur_seat_id = curSeat
        
    @property
    def tile(self):
        return self.__tile
            
    def initProcessor(self, actionID, seatId, state, extendInfo=None, timeOut=9, response=False):
        """
        初始化处理器
        参数
            seatId - 座位号
            state - 状态集合，当前座位号可以做出的全部选择
        """
        ftlog.debug('MDropCardProcessor.initProcessor seatId:', seatId, ' state:', state, ' extentdInfo:', extendInfo)
        if state == MTableState.TABLE_STATE_NEXT:
            return

        self.setActionID(actionID)
        self.__processors[seatId]['state'] = state
        self.__processors[seatId]['extendInfo'] = extendInfo
        # 用户未做出选择
        self.__processors[seatId]['response'] = 1
        if response == True:
            self.__processors[seatId]['response'] = 0
        self.setTimeOut(timeOut)
        ftlog.debug('MDropCardProcessor.initProcessor end:', self.__processors)
    
    def getExtendResultBySeatId(self, seatId):
        """当前座位号是否杠听"""
        extendInfo = self.__processors[seatId]['extendInfo']
        return extendInfo
    
    def getAllCanWins(self):
        '''
        获取所有选择了胡牌的玩家
        '''
        seats = []
        for seat in range(self.count):
            if (self.getStateBySeatId(seat) & MTableState.TABLE_STATE_HU):
                seats.append(seat)
        return seats
    
    def updateDuoHu(self, actionId, seatIds, state):
        """更新多胡"""
        ftlog.debug('MDropCardProcessor.updateDuoHu actionId:', actionId
                    , ' seatIds:', seatIds
                    , ' state:', state)

        if actionId != self.actionID:
            ftlog.debug('MDropCardProcessor.updateDuoHu wrong actionId, do not process actionId:', actionId
                        , ' actionIdInProcessor:', self.actionID)
            return False

        if len(seatIds) <= 1:
            ftlog.debug('MDropCardProcessor.updateDuoHu, only one player win, no need consider duoHu...')
            return True

        for seat in seatIds:
            if self.getResponseBySeatId(seat) != 0:
                return False

        return True

    def updateProcessor(self, actionID, seatId, state, tile, pattern=None):
        """
        用户做出了选择，state为0，表示放弃
        用户的选择集合明确
        参数
            state - 最终做出的选择
            tile - 操作的手牌
            extendInfo - 扩展信息，吃的时候保存吃牌选择
            
        返回值：
            True - 最高优先级，执行操作
            False - 非最高优先级，等待其他人的选择
        """
        if actionID != self.actionID:
            # 不是本轮处理的牌
            ftlog.debug('timeout dropcard processor update')
            return False
        
        ftlog.debug('MDropCardProcessor.updateProcessor actionID:', actionID
            , ' seatId:', seatId
            , ' state:', state
            , ' tile:', tile
            , ' pattern:', pattern
            , ' processor:', self.__processors)
        
        userState = self.__processors[seatId]['state'] & state
        if userState == MTableState.TABLE_STATE_NEXT:
            return False
        
        userExtend = self.__processors[seatId]['extendInfo']
        userExtend.updateState(state, pattern)
        self.__processors[seatId]['state'] = state
        # 用户已做出选择
        self.__processors[seatId]['response'] = 0
        # 如果是最高优先级的，返回True，牌桌据此响应
        # 如果不是最高优先级的，继续等待用户做出选择
        # 所有用户都做出选择，选择最高优先级的响应
        
        ftlog.debug('MDropCardProcessor.updateProcessor end:', self.__processors)
        return self.isBiggestPriority(state, seatId)
    
    def isBiggestPriority(self, state, seatId):
        """
        是否是最高优先级
        """
        seats = self.getSeatsBySchedule()
        ftlog.debug('MDropCardProcessor.isBiggestPriority state:', state
                    , ' seatId:', seatId
                    , ' seats:', seats)
        # 漏胡，出牌的人自己漏胡，如果其他人不胡，则自己胡
        if (seatId == self.curSeatId):
            for seat in seats:
                if state < self.getStateBySeatId(seat):
                    ftlog.debug('MDropCardProcessor.isBiggestPriority check PASS_HU return False ...')
                    return False
            ftlog.debug('MDropCardProcessor.isBiggestPriority check PASS_HU return True ...')
            return True
        
        curIndex = seats.index(seatId)
        for index in range(len(seats)):
            seat = seats[index]
            if seat == seatId:
                continue

            comAction = self.__processors[seat]['state']
            if index < curIndex:
                # 如果index的优先级大于curIndex的，则非最大优先级
                if self.isBigger(comAction, state):
                    ftlog.debug('MDropCardProcessor.isBiggestPriority biggest1 curIndex :', curIndex
                                , ' state:', state
                                , ' index:', index
                                , ' state:', state)
                    return False
            else:
                # 如果curIndex的优先级小于index的，
                if not self.isBigger(state, comAction):
                    ftlog.debug('MDropCardProcessor.isBiggestPriority biggest2 curIndex :', curIndex
                                , ' state:', state
                                , ' index:', index
                                , ' state:', state)
                    return False

            if comAction & MTableState.TABLE_STATE_HU and state & MTableState.TABLE_STATE_HU and self.tableTileMgr.canDuoHu():
                return False

        ftlog.debug('MDropCardProcessor.isBiggestPriority biggest at last...')
        return True   
        
    def hasAutoDecideAction(self, curSeat, trustTeeSet):
        """是否有自动托管的行为
        
        算法详情：
        1）查看是否有托管的player
        2）对有托管的玩家使用AI策略
        3）留下托管玩家的最高优先级行为，如果是本轮状态的最高优先级，执行此操作
        4）如果不是本轮的最高优先级行为，等待非托管玩家做出选择
        """
        if self.getState() == MTableState.TABLE_STATE_NEXT:
            return []
        
        seats = self.getAutoDecideSeatsBySchedule(trustTeeSet)
        ftlog.debug('MDropCardProcessor.hasAutoDecideAction seats:', seats)
        if len(seats) == 0:
            return []
        
        winSeats = []
        for seat in seats:
            player = self.players[seat]
            if self.isUserAutoDecided(player.curSeatId
                    , trustTeeSet
                    , self.getStateBySeatId(player.curSeatId)
                    , self.getResponseBySeatId(player.curSeatId) == 0):
                winSeats.append(seat)
                
        ftlog.debug('MDropCardProcessor.hasAutoDecideAction seats:', seats
                    , ' curSeat:', curSeat
                    , ' processors:', self.processors
                    , ' winSeats:', winSeats)
                
        return winSeats
    
    def isBigger(self, p1, p2):
        """两个人的优先级比较，判断seat1的优先级是否比seat2大
        参数：
        seat1 座位1
        p1 座位1的行为
        
        seat2 座位2
        p2 座位2的行为
        
        seat2是seat1顺时针循环得到的玩家
        """
        ftlog.debug('MDropCardProcessor.isBigger p1:', p1
                    , ' p2:', p2
                    , ' canDuoHu:', self.tableTileMgr.canDuoHu())
        if (p1 & MTableState.TABLE_STATE_GRABTING) and (p2 & MTableState.TABLE_STATE_GRABTING):
            return True
        
        # 两家同时胡牌 上家也和那么优先级大于下家
        if (p1 & MTableState.TABLE_STATE_HU) and (p2 & MTableState.TABLE_STATE_HU):
            if self.tableTileMgr.canDuoHu():
                return False
            else:
                return True

        if p1 == p2:
            return True
        
        return p1 > p2
    
    def allResponsed(self):
        """本轮出牌，所有人都已经响应
        """
        response = 0
        for seat in range(self.__count):
            response += self.__processors[seat]['response']
        return 0 == response
    
def testDuoWinsProcessor():
    """
    测试一炮多响时，多个和牌的状态更新
    状态：
        0号位出牌，1号位2号位两个人可和牌，能一炮多响

    操作：
        2号位先和牌
        1号位再和牌

    预期：
        2号位胡牌结果先不确认
        1号位胡牌的和牌结果确认
        1/2号位同时胡牌
    """
    dp = MDropCardProcessor(4, MPlayMode.JIXI)
    player3 = MPlayer('3', 1, 10003, 0)
    player3.setSeatId(3)
    player2 = MPlayer('2', 1, 10002, 0)
    player2.setSeatId(2)
    player1 = MPlayer('1', 1, 10001, 0)
    player1.setSeatId(1)
    player0 = MPlayer('0', 1, 10000, 0)
    player0.setSeatId(0)

    dp.players.append(player0)
    dp.players.append(player1)
    dp.players.append(player2)
    dp.players.append(player3)
    dp.setCurSeatId(0)

    tableTileMgr = MTableTileFactory.getTableTileMgr(4, MPlayMode.PINGDU258, MRunMode.CONSOLE)
    dp.setTableTileMgr(tableTileMgr)

    exInfoWin1 = MTableStateExtendInfo()
    winInfo1 = {}
    winInfo1['tile'] = 9
    exInfoWin1.appendInfo(MTableState.TABLE_STATE_HU, winInfo1)
    dp.initProcessor(19, 1, MTableState.TABLE_STATE_HU, exInfoWin1, 9)

    exInfoWin2 = MTableStateExtendInfo()
    winInfo2 = {}
    winInfo2['tile'] = 9
    exInfoWin2.appendInfo(MTableState.TABLE_STATE_HU, winInfo2)
    dp.initProcessor(19, 2, MTableState.TABLE_STATE_HU, exInfoWin2, 9)

    result2 = dp.updateProcessor(19, 2, MTableState.TABLE_STATE_HU, 9, None)
    print 'result2:', result2
    print dp.processors

    autoSeatId = dp.hasAutoDecideAction(0, -1)
    print 'autoSeatId2:', autoSeatId

    result1 = dp.updateProcessor(19, 1, MTableState.TABLE_STATE_HU, 9, None)
    print 'result1:', result1

    autoSeatId = dp.hasAutoDecideAction(0, -1)
    print 'autoSeatId1:', autoSeatId


    wins = [1, 2]
    result3 = dp.updateDuoHu(19, wins, MTableState.TABLE_STATE_HU)
    print 'result3:', result3

    print dp.processors

def testWinsProcessor():
    """
    测试多个和牌的状态更新
    状态：
        0号位出牌，1号位2号位两个人可和牌，不能一炮多响
        
    操作：
        2号位先和牌
        1号位再和牌
        
    预期：
        2号位胡牌结果先不确认
        1号位胡牌的和牌结果确认
    """
    dp = MDropCardProcessor(4, MPlayMode.JIXI)
    player3 = MPlayer('3', 1, 10003, 0)
    player3.setSeatId(3)
    player2 = MPlayer('2', 1, 10002, 0)
    player2.setSeatId(2)
    player1 = MPlayer('1', 1, 10001, 0)
    player1.setSeatId(1)
    player0 = MPlayer('0', 1, 10000, 0)
    player0.setSeatId(0)
    
    dp.players.append(player0)
    dp.players.append(player1)
    dp.players.append(player2)
    dp.players.append(player3)
    dp.setCurSeatId(0)
    
    exInfoWin1 = MTableStateExtendInfo()
    winInfo1 = {}
    winInfo1['tile'] = 9
    exInfoWin1.appendInfo(MTableState.TABLE_STATE_HU, winInfo1)
    dp.initProcessor(19, 1, MTableState.TABLE_STATE_HU, exInfoWin1, 9)
    
    exInfoWin2 = MTableStateExtendInfo()
    winInfo2 = {}
    winInfo2['tile'] = 9
    exInfoWin2.appendInfo(MTableState.TABLE_STATE_HU, winInfo2)
    dp.initProcessor(19, 2, MTableState.TABLE_STATE_HU, exInfoWin2, 9)
    
    result2 = dp.updateProcessor(19, 2, MTableState.TABLE_STATE_HU, 9, None)
    print 'result2:', result2
    print dp.processors

    result1 = dp.updateProcessor(19, 1, MTableState.TABLE_STATE_HU, 9, None)  
    print 'result1:', result1
    print dp.processors
    
def testLouhuProcessor():
    """
    测试漏和牌的状态更新
    状态：
        0号位出牌，1号位漏胡2号位和牌
        
    操作：
        1号位漏和牌
        2号位和牌
        
    预期：
        1号位漏胡牌结果先不确认
        2号位胡牌的和牌结果确认
    """
    dp = MDropCardProcessor(4, MPlayMode.JIXI)
    player3 = MPlayer('3', 1, 10003, 0)
    player3.setSeatId(3)
    player2 = MPlayer('2', 1, 10002, 0)
    player2.setSeatId(2)
    player1 = MPlayer('1', 1, 10001, 0)
    player1.setSeatId(1)
    player0 = MPlayer('0', 1, 10000, 0)
    player0.setSeatId(0)
    
    dp.players.append(player0)
    dp.players.append(player1)
    dp.players.append(player2)
    dp.players.append(player3)
    dp.setCurSeatId(0)
    
    exInfoWin1 = MTableStateExtendInfo()
    winInfo1 = {}
    exInfoWin1.appendInfo(MTableState.TABLE_STATE_PASS_HU, winInfo1)
    dp.initProcessor(19, 1, MTableState.TABLE_STATE_PASS_HU, exInfoWin1, 9)
    
    exInfoWin2 = MTableStateExtendInfo()
    winInfo2 = {}
    winInfo2['tile'] = 9
    exInfoWin2.appendInfo(MTableState.TABLE_STATE_HU, winInfo2)
    dp.initProcessor(19, 2, MTableState.TABLE_STATE_HU, exInfoWin2, 9)
    
    result1 = dp.updateProcessor(19, 1, MTableState.TABLE_STATE_PASS_HU, 9, None)  
    print 'result1:', result1
    print dp.processors
    
    result2 = dp.updateProcessor(19, 2, MTableState.TABLE_STATE_HU, 9, None)
    print 'result2:', result2
    print dp.processors

    
def testChiTingWinsProcessor():
    """
    测试多个和牌的状态更新
    状态：
        0号位出牌，1号位2号位两个人可和牌，不能一炮多响
        
    操作：
        2号位先和牌
        1号位再和牌
        
    预期：
        2号位胡牌结果先不确认
        1号位胡牌的和牌结果确认
    """
    dp = MDropCardProcessor(4)
    player3 = MPlayer('3', 1, 10003, 0)
    player3.setSeatId(3)
    player2 = MPlayer('2', 1, 10002, 0)
    player2.setSeatId(2)
    player1 = MPlayer('1', 1, 10001, 0)
    player1.setSeatId(1)
    player0 = MPlayer('0', 1, 10000, 0)
    player0.setSeatId(0)
    
    dp.players.append(player0)
    dp.players.append(player1)
    dp.players.append(player2)
    dp.players.append(player3)
    dp.setCurSeatId(1)
    
    exInfoWin0 = MTableStateExtendInfo()
    exInfoWin0.appendInfo(MTableState.TABLE_STATE_CHI & MTableState.TABLE_STATE_GRABTING, {"tile":14, "pattern":[12, 13, 14], "ting":{}})
    dp.initProcessor(19, 0, MTableState.TABLE_STATE_CHI & MTableState.TABLE_STATE_GRABTING, exInfoWin0, 9)
    
    exInfoWin2 = MTableStateExtendInfo()
    exInfoWin2.appendInfo(MTableState.TABLE_STATE_HU, {"tile": 14})
    dp.initProcessor(19, 2, MTableState.TABLE_STATE_HU, exInfoWin2, 9)
    
    exInfoChi3 = MTableStateExtendInfo()
    exInfoChi3.appendInfo(MTableState.TABLE_STATE_CHI, {"tile":14, " pattern":[12, 13, 14]})
    dp.initProcessor(19, 3, MTableState.TABLE_STATE_CHI, exInfoChi3, 9)
    
    result3 = dp.updateProcessor(19, 2, MTableState.TABLE_STATE_CHI, 9, [12, 13, 14])
    print 'result3:', result3
    print dp.processors

    result0 = dp.updateProcessor(19, 0, MTableState.TABLE_STATE_CHI & MTableState.TABLE_STATE_GRABTING, 9, [12, 13, 14])  
    print 'result0:', result0
    
    dp.resetSeatId(2)
    print dp.processors
    
    print dp.hasAutoDecideAction(1, -1)
    
def testNormalUpdateProcessor():
    """
    测试吃碰杠的状态更新
    状态：
        同时可吃可碰
    操作：
        吃先同意
        碰后取消
    
    预期结果：
        自动响应吃
    
    """
    dp = MDropCardProcessor(4)
    player3 = MPlayer('3', 1, 10003, 0)
    player3.setSeatId(3)
    player2 = MPlayer('2', 1, 10002, 0)
    player2.setSeatId(2)
    player1 = MPlayer('1', 1, 10001, 0)
    player1.setSeatId(1)
    player0 = MPlayer('0', 1, 10000, 0)
    player0.setSeatId(0)
    
    dp.players.append(player0)
    dp.players.append(player1)
    dp.players.append(player2)
    dp.players.append(player3)
    dp.setCurSeatId(1)
    
    exInfoChi = MTableStateExtendInfo()
    exInfoChi.setExtend({"chi":[[1, 2, 3]]})
    dp.initProcessor(19, 2, MTableState.TABLE_STATE_CHI, exInfoChi, 9)
    
    exInfoPeng = MTableStateExtendInfo()
    exInfoPeng.setExtend({"peng": [[3, 3, 3]]})
    dp.initProcessor(19, 3, MTableState.TABLE_STATE_PENG, exInfoPeng, 9)
    
    dp.updateProcessor(19, 2, MTableState.TABLE_STATE_CHI, 3, [1, 2, 3])
    print dp.processors
    dp.resetSeatId(3)
    
    print dp.hasAutoDecideAction(1, -1)
    
def testBigger():
    s1 = 65536
    s2 = 4
    tableTileMgr = MTableTileFactory.getTableTileMgr(4, MPlayMode.PINGDU258, MRunMode.CONSOLE)
    dp = MDropCardProcessor(4, MPlayMode.PINGDU258)
    dp.setTableTileMgr(tableTileMgr)
    print dp.isBigger(s1, s2)
    
if __name__ == "__main__":
    # testNormalUpdateProcessor()
    # testWinsProcessor()
#     testBigger()
    # testChiTingWinsProcessor()
    # testLouhuProcessor()
    testDuoWinsProcessor()
