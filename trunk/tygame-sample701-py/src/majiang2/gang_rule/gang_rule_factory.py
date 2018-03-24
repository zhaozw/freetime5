#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/10

from majiang2.ai.play_mode import MPlayMode
from majiang2.gang_rule.gang_rule import MGangRule
from majiang2.gang_rule.gang_rule_huaining import MGangRuleHuaiNing
from majiang2.gang_rule.gang_rule_mudanjiang import MGangRuleMudanjiang
from majiang2.gang_rule.gang_rule_hanshan import MGangRuleHanShan
from majiang2.gang_rule.gang_rule_hexian import MGangRuleHeXian
from majiang2.gang_rule.gang_rule_panjin import MGangRulePanJin
from majiang2.gang_rule.gang_rule_sichuan import MGangRuleSiChuan

class MGangRuleFactory(object):
    def __init__(self):
        super(MGangRuleFactory, self).__init__()

    @classmethod
    def getGangRule(cls, playMode):
        """判杠规则获取工厂
        输入参数：
            playMode - 玩法

        返回值：
            对应玩法的判和规则
        """
        if playMode == MPlayMode.HUAINING:
            return MGangRuleHuaiNing()
        elif playMode == MPlayMode.MUDANJIANG:
            return MGangRuleMudanjiang()
        elif playMode == MPlayMode.HANSHAN:
            return MGangRuleHanShan()
        elif playMode == MPlayMode.HEXIAN:
            return MGangRuleHeXian()
        elif playMode == MPlayMode.PANJIN:
            return MGangRulePanJin()
        elif playMode == MPlayMode.XUELIUCHENGHE \
                or playMode == MPlayMode.XUEZHANDAODI:
            return MGangRuleSiChuan()

        return MGangRule()
