# -*- coding: utf-8 -*-
"""
Created on 2018年02月03日17:08:55

@author: yzx
"""


class ChatMsgValidation(object):

    def __init__(self):
        super(ChatMsgValidation, self).__init__()

    def do_verify(self, msg):
        """
        验证消息
        """
        raise NotImplementedError
