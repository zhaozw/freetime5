# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.dealer.dealer_sanmen_nofeng import SanMenNoFengDealer
from majiang2.ai.play_mode import MPlayMode
from majiang2.dealer.dealer_all_color import AllColorDealer
from majiang2.dealer.dealer_all_flower import AllFlowerDealer
from majiang2.dealer.dealer_sanmen_zhong import SanMenWithZhonggDealer
from majiang2.dealer.dealer_tongtiao_zfb import TongTiaoWithZFBDealer
from majiang2.dealer.dealer_tongtiao_zhong import TongTiaoWithZhonggDealer
from majiang2.dealer.dealer_sanmen_zfb import SanMenWithZFBDealer
from majiang2.dealer.dealer_sanmen_fa import SanMenWithFaDealer
from freetime5.util import ftlog

class DealerFactory(object):
    # 只发万筒条，没有风
    DEALER_SANMEN_WUFENG = 'sanmen_wufeng'
    # 包含所有的牌
    DEALER_ALL_COLORS = 'all_colors'
    # 万/筒/条+红中
    DEALER_SANMENG_ZHONG = 'sanmen_zhong'
    # 筒/条+红中
    DEALER_TONGTIAO_ZHONG = 'tongtiao_zhong'
    # 筒/条+中发白
    DEALER_TONGTIAO_ZFB = 'tongtiao_zfb'
    # 万/筒/条+中发白
    DEALER_SANMENG_ZFB = 'sanmen_zfb'
    # 万/筒/条+发
    DEALER_SANMENG_FA = 'sanmen_fa'
    # 万筒条／风牌／箭牌／花牌 春夏秋冬梅兰竹菊
    DEALER_ALL_FLOWERS = 'all_flowers'


    
    def __init__(self):
        super(DealerFactory, self).__init__()
    
    @classmethod
    def getDealer(cls, playMode, playerCount = -1):
        """发牌器获取工厂
        输入参数：
            playMode - 玩法
        
        返回值：
            对应玩法的发牌算法
        """
        dType = cls.getDealerTypeByPlayMode(playMode, playerCount)
        ftlog.debug('[DealerFactory] playMode=', playMode, ' playerCount=', playerCount,'dType=',dType)
        
        if dType == cls.DEALER_SANMEN_WUFENG:
            return SanMenNoFengDealer()
        elif dType == cls.DEALER_ALL_COLORS:
            return AllColorDealer()
        elif dType == cls.DEALER_SANMENG_ZHONG:
            return SanMenWithZhonggDealer()
        elif dType == cls.DEALER_TONGTIAO_ZFB:
            return TongTiaoWithZFBDealer()
        elif dType == cls.DEALER_SANMENG_ZFB:
            return SanMenWithZFBDealer()
        elif dType == cls.DEALER_TONGTIAO_ZHONG:
            return TongTiaoWithZhonggDealer()
        elif dType == cls.DEALER_SANMENG_FA:
            return SanMenWithFaDealer()
        elif dType == cls.DEALER_ALL_FLOWERS:
            return AllFlowerDealer()
        
        return None
    
    @classmethod
    def getDealerTypeByPlayMode(cls, playMode, playerCount):
        """根据玩法返回发牌类型
            后续可作为配置
        """

        if playMode == MPlayMode.XUEZHANDAODI \
            or playMode == MPlayMode.XUELIUCHENGHE:
            return cls.DEALER_SANMEN_WUFENG
        elif playMode == MPlayMode.GUOBIAO \
                or playMode == MPlayMode.PINGDU \
                or playMode == MPlayMode.PINGDU258 \
                or playMode == MPlayMode.WEIHAI \
                or playMode == MPlayMode.HUAINING \
                or playMode == MPlayMode.YANTAI \
                or playMode == MPlayMode.HEXIAN \
                or playMode == MPlayMode.SANXIAN \
                or playMode == MPlayMode.HANSHAN \
                or playMode == MPlayMode.DANDONG \
                or playMode == MPlayMode.PANJIN \
                or playMode == MPlayMode.JIPINGHU:
            return cls.DEALER_ALL_COLORS
        elif playMode == MPlayMode.HAERBIN \
                or playMode == MPlayMode.WUHU \
                or playMode == MPlayMode.MUDANJIANG \
                or playMode == MPlayMode.WUWEI:
            return cls.DEALER_SANMENG_ZHONG
        elif playMode == MPlayMode.JIXI:
            if playerCount == 3 or playerCount ==2:
                return cls.DEALER_TONGTIAO_ZHONG
            else:
                return cls.DEALER_SANMENG_ZHONG
        elif playMode == MPlayMode.BAICHENG:
            return cls.DEALER_SANMENG_ZFB
        elif playMode == MPlayMode.CHAOHU:
            return cls.DEALER_SANMENG_FA
        elif playMode == MPlayMode.JINAN:
            return cls.DEALER_ALL_FLOWERS
        return None
