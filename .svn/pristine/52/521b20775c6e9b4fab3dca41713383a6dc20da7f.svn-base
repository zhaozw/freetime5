#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/9

from majiang2.ai.play_mode import MPlayMode
from majiang2.peng_rule.peng_rule import MPengRule
from majiang2.peng_rule.peng_rule_huaining import MPengRuleHuaiNing
from majiang2.peng_rule.peng_rule_wuhu import MPengRuleWuHu
from majiang2.peng_rule.peng_rule_hanshan import MPengRuleHanShan
from majiang2.peng_rule.peng_rule_hexian import MPengRuleHeXian
from majiang2.peng_rule.peng_rule_panjin import MPengRulePanJin
from majiang2.peng_rule.peng_rule_sichuan import MPengRuleSiChuan

class MPengRuleFactory(object):
    def __init__(self):
        super(MPengRuleFactory, self).__init__()

    @classmethod
    def getPengRule(cls, playMode):
        """判碰规则获取工厂
        输入参数：
            playMode - 玩法

        返回值：
            对应玩法的判和规则
        """
        if playMode == MPlayMode.HUAINING:
            return MPengRuleHuaiNing()
        elif playMode == MPlayMode.WUHU or playMode == MPlayMode.WUWEI:
            return MPengRuleWuHu()
        elif playMode == MPlayMode.HANSHAN:
            return MPengRuleHanShan()
        elif playMode == MPlayMode.HEXIAN:
            return MPengRuleHeXian()
        elif playMode == MPlayMode.PANJIN:
            return MPengRulePanJin()
        elif playMode == MPlayMode.XUEZHANDAODI \
            or playMode == MPlayMode.XUELIUCHENGHE:
            return MPengRuleSiChuan()
        
        return MPengRule()
