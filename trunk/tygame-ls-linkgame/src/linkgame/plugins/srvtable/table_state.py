# -*- coding: utf-8 -*-
'''
Created on 2015年7月7日

@author: zqh
'''
from freetime5.util import ftstr

class TYTableState(object):
    '''
    为了兼容老版Table（_stat是list类型）， TYTableState需要实现list的部分函数, 即可以按list的方式进行数据的操作
    Note： 如果直接继承list的话，在redis化时，没有覆写的函数会出现致数据不一致的问题， 所以不推荐。
    table.state一旦建立, 其数据存储为list形式(便于redis化), 基本上其数据的个数将不再发生变化
    注意约定: 此列表中第0个字段为桌子的int值状态
    '''

    INDEX_TABLE_STATE = 0  # 第0个字段固定为桌子的状态

    TABLE_STATE_IDEL = 10  # 当前桌子为空闲状态


    def __init__(self, table):
        self.table = table
        self._list = [self.TABLE_STATE_IDEL]


    def __getitem__(self, index):
        return self._list[index]

    
    def __setitem__(self, index, value):  
        self._list[index] = value


    def __len__(self):
        return len(self._list)


    def __str__(self):
        return self._list.__str__()

    
    def __repr__(self):
        return self._list.__repr__()

    
    def getDatas(self):
        return self._list


    def update(self, stateList):
        '''
        将stateList (list类型) 数据更新到TYTableState类属性
        TYTableState子类可以通过覆写此函数来扩展属性,
        此方法通常再初始化桌子状态时调用
        '''
        assert(isinstance(stateList, list))
        self._list = ftstr.cloneData(stateList)


    @property
    def state(self):
        return self._list[self.INDEX_TABLE_STATE]


    @state.setter
    def state(self, state):
        self._list[self.INDEX_TABLE_STATE] = state


    