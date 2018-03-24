# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from majiang2.ai.play_mode import MPlayMode
from majiang2.win_loose_result.table_results_stat_xuezhan import MTableResultsStatXuezhan
from majiang2.win_loose_result.table_results_stat_guangdong import MTableResultsStatGuangDong
from majiang2.win_loose_result.table_results_stat import MTableResultsStat

class MTableResultsStateFactory(object):
    def __init__(self):
        super(MTableResultsStateFactory, self).__init__()
    
    @classmethod
    def getStat(cls, playMode):
        """判和规则获取工厂
        输入参数：
            playMode - 玩法
        
        返回值：
            对应玩法的判和规则
        """
        if playMode == MPlayMode.XUELIUCHENGHE \
            or playMode == MPlayMode.XUEZHANDAODI:
            return MTableResultsStatXuezhan()
        elif playMode == MPlayMode.JIPINGHU:
            return MTableResultsStatGuangDong()
        
        return MTableResultsStat()
