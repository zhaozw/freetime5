# -*- coding: utf-8 -*-
"""
Created on 2018年03月10日17:40:58

@author: yzx

对应GH进程, 基本上为 http api 入口
"""

from freetime5.util import ftlog, ftstr
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import typlugin, tyadapter
from tuyoo5.core.typlugin import gameRpcUtilOne

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

_ADAPTER_SNS = 'sns'

def querySNS(api, params, sign=False):
    code = 200
    try:
        if _DEBUG:
            debug('querySNS->', api, params)
        code, page = tyadapter.queryAdapter(_ADAPTER_SNS, params, {}, api)
        if _DEBUG:
            debug('querySNS->', api, code, page)
        return ftstr.loads(page)
    except:
        ftlog.error()
        return {'error': code}

def _check_friend(user_id,target_user_id):
        params = {
            'userId': user_id,
            'targetUserId': target_user_id,
        }
        info = querySNS('/api/sns/check_friend', params)
        return info.get('data', 0)

class ChatHttpTestcase(typlugin.TYPlugin):
    """
    http测试用例.
    """

    def __init__(self):
        super(ChatHttpTestcase, self).__init__()

    def destoryPlugin(self):
        super(ChatHttpTestcase, self).destoryPlugin()

    @typlugin.markPluginEntry(httppath='test_http_chat')
    def test_http_chat(self, request):
        debug("ChatHttp : test_http_chat : request = ", request)
        return {request.path: 'ok'}

    @typlugin.markPluginEntry(httppath='test_http_chat2')
    def test_http_chat2(self, request):
        debug("ChatHttp : test_http_chat2 : request = ", request)
        word = request.getParamStr('word', '')
        msg = MsgPack()
        msg.setCmd('chat')
        msg.setAction('send_message')
        msg.setParam('userId', 10000)
        msg.setParam('gameId', 9993)
        msg.setParam('msgType', 0)
        msg.setParam('targetUserId', 10002)
        msg.setParam('sn', 1)
        msg.setParam('content', '{"text":"'+word+'"}')
        gameRpcUtilOne.srvchat.http_test_talk_message(10000, msg.pack())


        return {request.path: 'ok'}

    @typlugin.markPluginEntry(httppath='test_http_chat3')
    def test_http_chat3(self, request):
        debug("ChatHttp : test_http_chat3 : request = ", request)
        # tyglobal.gameIns().chat_service.do_some_thing()
        return {request.path: 'ok'}

    @typlugin.markPluginEntry(httppath='test_http_chat4')
    def test_http_check_friend(self, request):
        debug("ChatHttp : test_http_chat3 : request = ", request)
        userId = request.getParamInt('userId')
        targetUserId = request.getParamInt('targetUserId')
        _check_friend(userId,targetUserId)
        return {request.path: 'ok'}
