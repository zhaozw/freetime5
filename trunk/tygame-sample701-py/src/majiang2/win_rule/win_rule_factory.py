# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from majiang2.ai.play_mode import MPlayMode
from majiang2.win_rule.win_rule_haerbin import MWinRuleHaerbin
from majiang2.win_rule.win_rule_sichuan import MWinRuleSichuan
from majiang2.win_rule.win_rule_simple import MWinRuleSimple
from majiang2.win_rule.win_rule_jixi import MWinRuleJixi
from majiang2.win_rule.win_rule_mudanjiang import MWinRuleMudanjiang
from majiang2.win_rule.win_rule_pingdu import MWinRulePingDu
from majiang2.win_rule.win_rule_baicheng import MWinRuleBaicheng
from majiang2.win_rule.win_rule_pingdu258 import MWinRulePingDu258
from majiang2.win_rule.win_rule_weihai import MWinRuleWeihai
from majiang2.win_rule.win_rule_yantai import MWinRuleYantai
from majiang2.win_rule.win_rule_panjin import MWinRulePanjin
from majiang2.win_rule.win_rule_jinan import MWinRuleJinan
from majiang2.win_rule.win_rule_dandong import MWinRuleDandong
from majiang2.win_rule.win_rule_jipinghu import MWinRuleJiPingHu

class MWinRuleFactory(object):
    def __init__(self):
        super(MWinRuleFactory, self).__init__()
    
    @classmethod
    def getWinRule(cls, playMode):
        """判和规则获取工厂
        输入参数：
            playMode - 玩法
        
        返回值：
            对应玩法的判和规则
        """
        if playMode == MPlayMode.HAERBIN:
            return MWinRuleHaerbin()
        elif playMode == MPlayMode.MUDANJIANG:
            return MWinRuleMudanjiang()
        elif playMode == MPlayMode.XUEZHANDAODI \
            or playMode == MPlayMode.XUELIUCHENGHE:
            return MWinRuleSichuan()
        elif playMode == MPlayMode.JIPINGHU:
            return MWinRuleJiPingHu()
        elif playMode == MPlayMode.JIXI:
            return MWinRuleJixi()
        elif playMode == MPlayMode.PINGDU:
            return MWinRulePingDu()
        elif playMode == MPlayMode.PINGDU258:
            return MWinRulePingDu258()
        elif playMode == MPlayMode.WEIHAI:
            return MWinRuleWeihai()
        elif playMode == MPlayMode.BAICHENG:
            return MWinRuleBaicheng()
        elif playMode == MPlayMode.PANJIN:
            return MWinRulePanjin()
        elif playMode == MPlayMode.DANDONG:
            return MWinRuleDandong()
        elif playMode == MPlayMode.YANTAI:
            return MWinRuleYantai()
        elif playMode == MPlayMode.JINAN:
            return MWinRuleJinan()
        else:
            return MWinRuleSimple()
