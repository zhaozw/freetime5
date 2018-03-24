# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from majiang2.ai.play_mode import MPlayMode
from majiang2.ting_rule.ting_rule_haerbin import MTingHaerbinRule
from majiang2.ting_rule.ting_rule_mudanjiang import MTingMudanjiangRule
from majiang2.ting_rule.ting_rule_jixi import MTingJixiRule
from majiang2.ting_rule.ting_rule_sichuan import MTingSichuanRule
from majiang2.ting_rule.ting_rule_simple import MTingSimpleRule
from freetime5.util import ftlog
from majiang2.win_rule.win_rule_factory import MWinRuleFactory
from majiang2.ting_rule.ting_rule_pingdu import MTingPingDuRule
from majiang2.ting_rule.ting_rule_jinan import MTingJiNanRule
from majiang2.ting_rule.ting_rule_baicheng import MTingBaichengRule
from majiang2.ting_rule.ting_rule_yantai import MTingYantaiRule
from majiang2.ting_rule.ting_rule_wuwei import MTingWuWeiRule
from majiang2.ting_rule.ting_rule_panjin import MTingPanjinRule
from majiang2.ting_rule.ting_rule_dandong import MTingDandong
from majiang2.ting_rule.ting_rule_hexian import MTingHeXianRule
from majiang2.ting_rule.ting_rule_jipinghu import MTingJiPingHuRule

class MTingRuleFactory(object):
    def __init__(self):
        super(MTingRuleFactory, self).__init__()
    
    @classmethod
    def getTingRule(cls, playMode):
        """判和规则获取工厂
        输入参数：
            playMode - 玩法
        
        返回值：
            对应玩法的判和规则
        """
        if playMode == MPlayMode.HAERBIN:
            return MTingHaerbinRule()
        elif playMode == MPlayMode.MUDANJIANG:
            return MTingMudanjiangRule()
        elif playMode == MPlayMode.JIXI:
            return MTingJixiRule()
        elif playMode == MPlayMode.XUEZHANDAODI \
            or playMode == MPlayMode.XUELIUCHENGHE:
            return MTingSichuanRule()
        elif playMode == MPlayMode.JIPINGHU:
            return MTingJiPingHuRule()
        elif playMode == MPlayMode.PINGDU:
            return MTingPingDuRule()
        elif playMode == MPlayMode.PINGDU258:
            return MTingPingDuRule()
        elif playMode == MPlayMode.WEIHAI:
            return MTingPingDuRule()
        elif playMode == MPlayMode.BAICHENG:
            return MTingBaichengRule()
        elif playMode == MPlayMode.PANJIN:
            return MTingPanjinRule()
        elif playMode == MPlayMode.DANDONG:
            return MTingDandong()
        elif playMode == MPlayMode.YANTAI:
            return MTingYantaiRule()
        elif playMode == MPlayMode.JINAN:
            return MTingJiNanRule()
        elif playMode == MPlayMode.WUWEI or playMode == MPlayMode.HANSHAN:
            return MTingWuWeiRule()
        elif playMode == MPlayMode.HEXIAN:
            return MTingHeXianRule()
        else:
            return MTingSimpleRule()
    
def tingHaerbin():
    tingRule = MTingRuleFactory.getTingRule(MPlayMode.HAERBIN)
    winRule = MWinRuleFactory.getWinRule(MPlayMode.HAERBIN)
    tingRule.setWinRuleMgr(winRule)
    tiles = [[4, 4, 4, 5 ,13, 14, 15, 29], [[23, 24, 25]], [[27, 27, 27]], [], [], []]
    leftTiles = [3, 4, 4, 4, 7, 8, 8, 9, 14, 14, 16, 17, 18, 19, 21, 21, 22, 23, 24, 24, 25, 27, 28, 29]
    result, resultDetail = tingRule.canTing(tiles, leftTiles, 7, [])
    ftlog.debug( result )
    if result:
        ftlog.debug(resultDetail)

if __name__ == "__main__":
    tingHaerbin()
