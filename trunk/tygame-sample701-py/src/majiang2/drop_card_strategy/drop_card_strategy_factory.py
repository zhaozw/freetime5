#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/10

from majiang2.ai.play_mode import MPlayMode
from majiang2.drop_card_strategy.drop_card_strategy_xuezhan_high import MDropCardStrategyXuezhanHigh
from majiang2.drop_card_strategy.drop_card_strategy import MDropCardStrategy
from majiang2.table.table_config_define import MTDefine
from freetime5.util import ftlog
from majiang2.drop_card_strategy.drop_card_strategy_xuezhan_normal import MDropCardStrategyXuezhanNormal
from majiang2.drop_card_strategy.drop_card_strategy_jipinghu_high import MDropCardStrategyJiPingHuHigh
from majiang2.drop_card_strategy.drop_card_strategy_jipinghu_normal import MDropCardStrategyJiPingHuNormal

class MDropCardStrategyFactory(object):
    def __init__(self):
        super(MDropCardStrategyFactory, self).__init__()

    @classmethod
    def getDropCardStrategy(cls, playMode, robotLevel=MTDefine.ROBOT_LEVEL_HIGH):
        """判吃规则获取工厂
        输入参数：
            playMode - 玩法

        返回值：
            对应玩法的判和规则
        """
        ftlog.debug('playMode:', playMode
                    , ' robotLevel:', robotLevel)
        
        if playMode == MPlayMode.XUELIUCHENGHE:
            if robotLevel == MTDefine.ROBOT_LEVEL_HIGH:
                return MDropCardStrategyXuezhanHigh()
            elif robotLevel == MTDefine.ROBOT_LEVEL_NORMAL:
                return MDropCardStrategyXuezhanNormal()
        elif playMode == MPlayMode.XUEZHANDAODI:
            if robotLevel == MTDefine.ROBOT_LEVEL_HIGH:
                return MDropCardStrategyXuezhanHigh()
            elif robotLevel == MTDefine.ROBOT_LEVEL_NORMAL:
                return MDropCardStrategy()
        elif playMode == MPlayMode.JIPINGHU:
            if robotLevel == MTDefine.ROBOT_LEVEL_HIGH:
                return MDropCardStrategyJiPingHuHigh()
            elif robotLevel == MTDefine.ROBOT_LEVEL_NORMAL:
                return MDropCardStrategyJiPingHuNormal()

        return MDropCardStrategy()
