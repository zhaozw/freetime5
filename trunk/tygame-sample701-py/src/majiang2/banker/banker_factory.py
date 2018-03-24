# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from majiang2.ai.play_mode import MPlayMode
from majiang2.banker.banker_random_remain import MBankerRandomRemain
from majiang2.banker.bank_host_win import MBankerHostWin
from majiang2.banker.bank_host_next import MBankerHostNext
from majiang2.banker.banker_random_huangNext_multiPao import MBankerRandomHuangNextMuiltPao
from majiang2.banker.bank_host_win_huang_gang import MBankerHostWinHuangGang
from majiang2.banker.bank_host_next_huang_next import MBankerHostNextHuangNext
from majiang2.banker.bank_host_next_huang_gang import MBankerHostNextHuangGang
from majiang2.banker.banker_host_sichuan import MBankerHostSiChuan

class BankerFactory(object):
    # 初始随机 坐庄玩法
    RANDOM_REMAIN = 'random_remain'
    # 首局房主坐庄 赢家接庄
    HOST_WIN = 'host_win'
    # 首局房主坐庄 输了庄下家接庄
    HOST_NEXT = 'host_next'
    # 初始随机，黄庄下一个人，一炮多响放炮者坐庄
    RANDOM_NEXT_MULTIPAO = 'random_next_multi_pao'
    # 首局房主坐庄 赢家接庄 黄庄按杠坐庄
    HOST_WIN_HUANG_GANG = 'host_win_huang_gang'
    # 首局房主坐庄 下家接庄 黄庄下家坐庄
    HOST_NEXT_HUANG_NEXT = 'host_next_huang_next'
    # 首局房主坐庄 下家接庄 黄庄按杠坐庄
    HOST_NEXT_HUANG_GANG = 'host_next_huang_gang'
    # 四川玩法
    HOST_NEXT_SICHUAN = 'host_next_sichuan'
    def __init__(self):
        super(BankerFactory, self).__init__()
    
    @classmethod
    def getBankerAI(cls, playMode):
        """庄家规则获取工厂
        输入参数：
            playMode - 玩法
        
        返回值：
            对应玩法的庄家管理规则
        """
        bankerType = cls.getBankerTypeByPlayMode(playMode)
        if bankerType == cls.RANDOM_REMAIN:
            return MBankerRandomRemain()
        if bankerType == cls.RANDOM_NEXT_MULTIPAO:
            return MBankerRandomHuangNextMuiltPao()
        if bankerType == cls.HOST_WIN:
            return MBankerHostWin()
        if bankerType == cls.HOST_NEXT:
            return MBankerHostNext()
        if bankerType == cls.HOST_WIN_HUANG_GANG:
            return MBankerHostWinHuangGang()
        if bankerType == cls.HOST_NEXT_HUANG_NEXT:
            return MBankerHostNextHuangNext()
        if bankerType == cls.HOST_NEXT_HUANG_GANG:
            return MBankerHostNextHuangGang()
        if bankerType == cls.HOST_NEXT_SICHUAN:
            return MBankerHostSiChuan()
        return MBankerHostNext()
    
    @classmethod
    def getBankerTypeByPlayMode(cls, playMode):
        if playMode == MPlayMode.GUOBIAO:
            return cls.RANDOM_REMAIN
        elif playMode == MPlayMode.PINGDU:
            return cls.RANDOM_NEXT_MULTIPAO
        elif playMode == MPlayMode.PINGDU258:
            return cls.RANDOM_NEXT_MULTIPAO
        elif playMode == MPlayMode.JINAN:
            return cls.HOST_WIN
        elif playMode == MPlayMode.JIXI \
            or playMode == MPlayMode.HAERBIN \
            or playMode == MPlayMode.BAICHENG \
            or playMode == MPlayMode.MUDANJIANG \
            or playMode == MPlayMode.WEIHAI \
            or playMode == MPlayMode.CHAOHU \
            or playMode == MPlayMode.PANJIN \
            or playMode == MPlayMode.DANDONG \
            or playMode == MPlayMode.JIPINGHU :
            return cls.HOST_NEXT
        elif playMode == MPlayMode.HUAINING:
            return cls.HOST_WIN
        elif playMode == MPlayMode.YANTAI:
            return cls.HOST_WIN_HUANG_GANG
        elif playMode == MPlayMode.HEXIAN:
            return cls.HOST_WIN
        elif playMode == MPlayMode.WUHU \
            or playMode == MPlayMode.WUWEI :
            return cls.HOST_NEXT_HUANG_NEXT
        elif playMode == MPlayMode.SANXIAN \
            or playMode == MPlayMode.HANSHAN :
            return cls.HOST_NEXT_HUANG_GANG
        elif playMode == MPlayMode.XUEZHANDAODI \
            or playMode == MPlayMode.XUELIUCHENGHE:
            return cls.HOST_NEXT_SICHUAN
        return None
