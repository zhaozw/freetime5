# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.mao_rule.mao_base import MMaoRuleBase
from majiang2.ai.mao import MMao
from majiang2.table.table_config_define import MTDefine

class MMaoRuleBaicheng(MMaoRuleBase):
    
    def __init__(self):
        super(MMaoRuleBaicheng, self).__init__()
        
    def hasMao(self, tiles, maoDanSetting, alreadyHave = 0,isFirstAddtile=False, extendInfo = {}):
        maos = MMao.hasMao(tiles, maoDanSetting, alreadyHave)
        # todo 根据自己的玩法过滤结果
        returnMaos = []
        for mao in maos:
            if mao['type'] == MTDefine.MAO_DAN_ZFB:
                returnMaos.append(mao)
            elif (mao['type'] == MTDefine.MAO_DAN_YAO or mao['type'] == MTDefine.MAO_DAN_JIU) and isFirstAddtile:
                returnMaos.append(mao)
        
        return returnMaos
    
