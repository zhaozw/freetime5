# -*- coding:utf-8 -*-
from tuyoo5.core.tyconfig import TYBizException


class StrangerException(TYBizException):
    def __init__(self, ec, message):
        super(StrangerException, self).__init__(ec, message)
