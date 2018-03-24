# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from majiang2.ai.play_mode import MPlayMode
from majiang2.win_loose_result.baicheng_one_result import MBaichengOneResult
from majiang2.win_loose_result.dandong_one_result import MDandongOneResult
from majiang2.win_loose_result.haerbin_one_result import MHaerbinOneResult
from majiang2.win_loose_result.jinan_one_result import MJinanOneResult
from majiang2.win_loose_result.jipinghu_one_result import MJiPingHuOneResult
from majiang2.win_loose_result.jixi_one_result import MJixiOneResult
from majiang2.win_loose_result.mudanjiang_one_result import MMudanjiangOneResult
from majiang2.win_loose_result.one_result import MOneResult
from majiang2.win_loose_result.panjin_one_result import MPanjinOneResult
from majiang2.win_loose_result.pingdu_one_result import MPingDuOneResult
from majiang2.win_loose_result.sichuan_one_result import MSiChuanOneResult
from majiang2.win_loose_result.weihai_one_result import MWeihaiOneResult
from majiang2.win_loose_result.yantai_one_result import MYantaiOneResult


class MOneResultFactory(object):
    def __init__(self):
        super(MOneResultFactory, self).__init__()
    
    @classmethod
    def getOneResult(cls, playMode, tilePatternChecker, playerCount):
        """判和规则获取工厂
        输入参数：
            playMode - 玩法
        
        返回值：
            对应玩法的判和规则
        """
        if playMode == MPlayMode.HAERBIN:
            return MHaerbinOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.MUDANJIANG:
            return MMudanjiangOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.JIXI:
            return MJixiOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.PINGDU:
            return MPingDuOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.PINGDU258:
            return MPingDuOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.WEIHAI:
            return MWeihaiOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.BAICHENG:
            return MBaichengOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.PANJIN:
            return MPanjinOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.DANDONG:
            return MDandongOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.YANTAI:
            return MYantaiOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.JINAN:
            return MJinanOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.XUELIUCHENGHE \
            or playMode == MPlayMode.XUEZHANDAODI:
            return MSiChuanOneResult(tilePatternChecker, playerCount)
        elif playMode == MPlayMode.JIPINGHU:
            return MJiPingHuOneResult(tilePatternChecker, playerCount)

        return MOneResult(tilePatternChecker, playerCount)
