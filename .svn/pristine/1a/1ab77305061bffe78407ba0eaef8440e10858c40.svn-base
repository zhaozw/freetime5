# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.mao_rule.mao_base import MMaoRuleBase
from majiang2.tile.tile import MTile
from majiang2.table.table_config_define import MTDefine
from freetime5.util import ftlog

class MMaoRuleWeihai(MMaoRuleBase):
    
    def __init__(self):
        super(MMaoRuleWeihai, self).__init__()
        
    def hasMao(self, tiles, maoDanSetting, alreadyHave = 0,isFirstAddtile=False,extendInfo={}):
        hasPengMao = extendInfo.get('maoType', 0)
        #tiles手牌
        #alreadyHave 已经有锚牌的类型： 0 没有 1 箭牌 2 风牌
        #isFirstAddtile 还没出过牌
        maos = []

        if (maoDanSetting & MTDefine.MAO_DAN_DNXBZFB) and (not (alreadyHave & MTDefine.MAO_DAN_DNXBZFB)) and \
             (not (hasPengMao )) and isFirstAddtile:
            pattern = []
            values = []
            for tile in tiles:
                if MTile.isFeng(tile) or MTile.isArrow(tile):
                    pattern.append(tile)
                    # if tile not in values: 乱锚取消相同牌检查
                    values.append(tile)

            if len(values) >= 3:
                luanMao = {}
                luanMao['type'] = MTDefine.MAO_DAN_DNXBZFB
                luanMao['pattern'] = values
                luanMao['name'] = MTDefine.MAO_DAN_DNXBZFB_NAME
                maos.append(luanMao)

        if (maoDanSetting & MTDefine.MAO_DAN_DNXB) and \
                (not (alreadyHave & MTDefine.MAO_DAN_DNXB) and \
                         (not (maoDanSetting & MTDefine.MAO_DAN_DNXBZFB)) and \
                         (not (hasPengMao & MTDefine.MAO_DAN_DNXB )) and  isFirstAddtile):

            pattern = []
            values = []
            for tile in tiles:
                if MTile.isFeng(tile):
                    pattern.append(tile)
                    if tile not in values:
                        values.append(tile)

            if len(values) >= 3:
                fengMao = {}
                fengMao['type'] = MTDefine.MAO_DAN_DNXB
                fengMao['pattern'] = values
                fengMao['name'] = MTDefine.MAO_DAN_DNXB_NAME
                maos.append(fengMao)

        if (maoDanSetting & MTDefine.MAO_DAN_ZFB) and \
                (not (alreadyHave & MTDefine.MAO_DAN_ZFB)) and \
                (not (maoDanSetting & MTDefine.MAO_DAN_DNXBZFB)) and \
                (not (hasPengMao & MTDefine.MAO_DAN_ZFB)) and isFirstAddtile:
            pattern = []
            values = []
            for tile in tiles:
                if MTile.isArrow(tile):
                    pattern.append(tile)
                    if tile not in values:
                        values.append(tile)

            if len(values) >= 3:
                arrowMao = {}
                arrowMao['type'] = MTDefine.MAO_DAN_ZFB
                arrowMao['pattern'] = values
                arrowMao['name'] = MTDefine.MAO_DAN_ZFB_NAME
                maos.append(arrowMao)

        ftlog.debug('MMao.hasMao tiles:', tiles
                    , ' maoDanSetting:', maoDanSetting
                    , ' maos:', maos ,'alreadyHave:',alreadyHave
                    , 'isFirstAddtile:', isFirstAddtile)
        return maos




