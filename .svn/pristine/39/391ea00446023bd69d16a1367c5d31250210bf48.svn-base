# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from majiang2.banker.banker import MBanker
from freetime5.util import ftlog


class MBankerHostSiChuan(MBanker):
    """
    开局房主庄家
    1）赢牌 有一炮多响 -> 放炮者坐庄
           无一炮多响 -> 先胡者坐庄
    2）流局 有查大叫／查花猪-> 庄家位置开始先查大叫／查花猪者坐庄
           无查大叫／查花猪-> 上一轮庄家坐庄
    """
    def __init__(self):
        super(MBankerHostSiChuan, self).__init__()
        self.__huaZhuDaJiaoId = -1

    @property
    def huaZhuDaJiaoId(self):
        return self.__huaZhuDaJiaoId
    
    def setHuaZhuDaJiaoId(self, seatId):
        self.__huaZhuDaJiaoId = seatId
    
    def getBanker(self, playerCount, isFirst, winLoose, winSeatId, extendInfo={}):
        """子类必须实现
        参数：
        1）isFirst 是否第一句
        2）winLoose 上局的结果 1分出了胜负 0流局
        3）winSeatId 赢家的座位号，如果第二个参数为0，则本参数为上一局的庄家
        4）四川无法根据winLoose来判断是否流局，可以胡多次，则从extenInfo中获取
        """
        if isFirst:
            # 初始化房主
            self.banker = 0
            self.no_result_count = 0
            self.remain_count = 0
        else:
            isGameFlow = extendInfo.get('isGameFlow', False)
            if isGameFlow:
                # 流局
                if self.huaZhuDaJiaoId != -1:
                    winSeatId = self.huaZhuDaJiaoId
                else:
                    winSeatId = self.banker
            else:
                # 赢局
                if self.multiPaoId != -1:
                    winSeatId = self.multiPaoId
                elif extendInfo.get('firstHuId', -1) != -1:
                    winSeatId = extendInfo.get('firstHuId', -1)
                else:
                    winSeatId = self.banker
            
            ftlog.debug('MBankerSiChuan.getbankerId:', winSeatId
                            , 'oldBankerId:', self.banker
                            , 'extendInfo:', extendInfo
                            , 'huaZhuDaJiaoId:', self.huaZhuDaJiaoId
                            , 'MultiPaoId:', self.multiPaoId)
            
            if winSeatId == self.banker:
                # 第一次胡的玩家 是庄家
                self.remain_count += 1
                self.no_result_count = 0
            else:
                # 赢得是闲家
                self.banker = winSeatId
                self.remain_count = 0
                self.no_result_count = 0
                
        # 重置相关参数
        self.__multiPaoId = -1
        self.__huaZhuDaJiaoId = -1
        
        ftlog.info('MBankerSiChuan.getBanker playerCount:', playerCount
                   , ' isFirst:', isFirst
                   , ' winLoose:', winLoose
                   , ' winSeatId:', winSeatId
                   , ' banker:', self.banker
                   , ' remainCount:', self.remain_count
                   , ' noResultCount:', self.no_result_count)        
        return self.banker, self.remain_count, self.no_result_count

    def calcNextBanker(self, playerCount, winLoose, winSeatId, extendInfo={}):
        """ 计算下一个庄家
            只是计算，不是真的设置庄家
            设置庄家请继续使用getBanker接口
        """

        isGameFlow = extendInfo.get('isGameFlow', False)
        if isGameFlow:
            # 流局
            if self.huaZhuDaJiaoId != -1:
                winSeatId = self.huaZhuDaJiaoId
            else:
                winSeatId = self.banker
        else:
            # 赢局
            if self.multiPaoId != -1:
                winSeatId = self.multiPaoId
            elif extendInfo.get('firstHuId', -1) != -1:
                winSeatId = extendInfo.get('firstHuId', -1)
            else:
                winSeatId = self.banker
            
        ftlog.debug('MBankerSiChuan.getbankerId:', winSeatId
                            , 'oldBankerId:', self.banker
                            , 'extendInfo:', extendInfo
                            , 'huaZhuDaJiaoId:', self.huaZhuDaJiaoId
                            , 'MultiPaoId:', self.multiPaoId)
            
        return winSeatId  
