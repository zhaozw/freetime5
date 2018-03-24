# -*- coding=utf-8 -*-
"""
@file  : _tasksubsys
@date  : 2016-11-28
@author: GongXiaobo
"""
from tuyoo5.plugins.task import tytask


class HappyBagTaskKindPool(tytask.TYTaskKindPool):

    TYPE_ID = 'happybag.task.pool'

    def __init__(self):
        super(HappyBagTaskKindPool, self).__init__()
