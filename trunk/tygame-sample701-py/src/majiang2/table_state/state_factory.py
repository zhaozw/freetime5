# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.ai.play_mode import MPlayMode
from majiang2.table_state.state_haerbin import MTableStateHaerbin
from majiang2.table_state.state_mudanjiang import MTableStateMudanjiang
from majiang2.table_state.state_xuezhan import MTableStateXuezhan
from majiang2.table_state.state_jixi import MTableStateJixi
from majiang2.table_state.state_pingdu import MTableStatePingDu
from majiang2.table_state.state_baicheng import MTableStateBaicheng
from majiang2.table_state.state_weihai import MTableStateWeihai
from majiang2.table_state.state_jinan import MTableStateJinan
from majiang2.table_state.state_wuhu import MTableStateWuHu
from majiang2.table_state.state_huaining import MTableStateHuaiNing
from freetime5.util import ftlog
from majiang2.table_state.state_yantai import MTableStateYantai
from majiang2.table_state.state_chaohu import MTableStateChaoHu
from majiang2.table_state.state_hexian import MTableStateHeXian
from majiang2.table_state.state_wuwei import MTableStateWuWei
from majiang2.table_state.state_panjin import MTableStatePanjin
from majiang2.table_state.state_sanxian import MTableStateSanXian
from majiang2.table_state.state_dandong import MTableStateDandong
from majiang2.table_state.state_xueliu import MTableStateXueliu
from majiang2.table_state.state_jipinghu import MTableStateJiPingHu

class TableStateFactory(object):
    
    def __init__(self):
        super(TableStateFactory, self).__init__()
    
    @classmethod
    def getTableStates(cls, playMode):
        """发牌器获取工厂
        输入参数：
            playMode - 玩法
        
        返回值：
            对应玩法的牌桌状态
        """
        if playMode == MPlayMode.HAERBIN:
            return MTableStateHaerbin()
        elif playMode == MPlayMode.MUDANJIANG:
            return MTableStateMudanjiang()
        elif playMode == MPlayMode.XUEZHANDAODI:
            return MTableStateXuezhan()
        elif playMode == MPlayMode.XUELIUCHENGHE:
            return MTableStateXueliu()
        elif playMode == MPlayMode.JIXI:
            return MTableStateJixi()
        elif playMode == MPlayMode.PINGDU:
            return MTableStatePingDu()
        elif playMode == MPlayMode.PINGDU258:
            return MTableStatePingDu()
        elif playMode == MPlayMode.WEIHAI:
            return MTableStateWeihai()
        elif playMode == MPlayMode.BAICHENG:
            return MTableStateBaicheng()
        elif playMode == MPlayMode.PANJIN:
            return MTableStatePanjin()
        elif playMode == MPlayMode.DANDONG:
            return MTableStateDandong()
        elif playMode == MPlayMode.WUHU:
            return MTableStateWuHu()
        elif playMode == MPlayMode.HUAINING:
            return MTableStateHuaiNing()
        elif playMode == MPlayMode.YANTAI:
            return MTableStateYantai()
        elif playMode == MPlayMode.CHAOHU:
            return MTableStateChaoHu()
        elif playMode == MPlayMode.JINAN:
            return MTableStateJinan()
        elif playMode == MPlayMode.HEXIAN:
            return MTableStateHeXian()
        elif playMode == MPlayMode.WUWEI \
            or playMode == MPlayMode.HANSHAN:
            return MTableStateWuWei()
        elif playMode == MPlayMode.SANXIAN:
            return MTableStateSanXian()
        elif playMode == MPlayMode.JIPINGHU:
            return MTableStateJiPingHu()

        ftlog.error('TableStateFactory.getTableStates error, playMode:', playMode)
        return None
