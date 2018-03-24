# -*- coding: utf-8 -*-
"""
Created on 2018年02月03日17:08:55

@author: yzx
"""
from chat.entity.msg_validation_if import ChatMsgValidation
from freetime5.util import ftlog
from tuyoo5.core.typlugin import RPC_CALL_SAFE
from tuyoo5.core.typlugin import RPC_TARGET_MOD_ONE
from tuyoo5.core.typlugin import getRpcProxy

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class FriendValidation(ChatMsgValidation):

    def __init__(self):
        super(FriendValidation, self).__init__()

    @property
    def SNSProxy(self):
        return getRpcProxy(8888, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)

    def do_verify(self, msg):
        userId = msg.getParam('userId')
        targetId = msg.getParam('targetId')
        pass
        # rfc = self.SNSProxy.srvhttp.verify(userId,targetId)
        # result = rfc.getResult()
        # if result == 0:
        #     raise StrangerException()
