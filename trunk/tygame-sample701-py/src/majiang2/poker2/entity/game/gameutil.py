# -*- coding: utf-8 -*-
'''
Created on 2017年10月27日

@author: zqh
'''
from freetime5.util.ftmsg import MsgPack


def getClientId(msg):
    '''
    获取msgpack中的clientId值
    '''
    if isinstance(msg, MsgPack):
        clientId = msg.getKey('clientId')
        if clientId:
            return clientId
        return msg.getParam('clientId')
    return None
