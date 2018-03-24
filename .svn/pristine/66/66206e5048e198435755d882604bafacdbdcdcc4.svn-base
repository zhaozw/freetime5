# -*- coding: utf-8 -*-
"""
Created on 2018年02月02日11:16:10

@author: yzx

对应GU进程, 基本为长连接入口.
"""
import chat.entity.chat_dao as _dao
from chat.entity.chat_dao import DaoChatRecordRedis
from chat.entity.chat_service import ChatService
from chat.entity.utils import current_milli_time
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import typlugin, tyglobal, tyrpcconn, tychecker
from tuyoo5.core.tyconfig import TYBizException

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

def check_targetUserId(msg, result, name):
    val = msg.getParamInt(name)
    if val > 0:
        return val, None
    return None, 'the %s must large than zero !' % (name)


def check_userId(msg, result, name):
    val = msg.getParamInt(name)
    if val > 0:
        return val, None
    return None, 'the %s must large than zero !' % (name)

def check_flag(msg, result, name):
    val = msg.getParamInt(name)
    if val > 0:
        return val, None
    return None, 'the %s must large than zero !' % (name)



class ChatListSrv(typlugin.TYPlugin):
    """
    聊天服务，聊天列表，历史消息等.
    """

    def __init__(self):
        super(ChatListSrv, self).__init__()
        debug("ChatListSrv init")
        self.service = ChatService()
        self.service.record_dao = DaoChatRecordRedis()
        self.checkBase = tychecker.Checkers(
            check_userId,
            check_targetUserId,
        )
        self.user_checker = tychecker.Checkers(
            check_userId,
        )
        self.flag_checker = tychecker.Checkers(
            check_flag,
        )

    def destoryPlugin(self):
        super(ChatListSrv, self).destoryPlugin()
        _dao.DaoUserChatRecordZSet.finalize()
        _dao.DaoChatRecordHash.finalize()
        # _dao.DaoUserChatListHash.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginBefore(self):
        debug("ChatListSrv initPluginBefore")
        _dao.DaoUserChatRecordZSet.initialize()
        _dao.DaoChatRecordHash.initialize()
        # _dao.DaoUserChatListHash.initialize()

    @typlugin.markPluginEntry(initAfterConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginAfter(self):
        debug("ChatListSrv initPluginAfter")

    @typlugin.markPluginEntry(cmd='chat', act="get_chat_record", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def get_chat_record(self, msg):
        """
        获取所有的聊天记录.
        """
        debug("ChatListSrv : get_chat_record : msg = ", msg)
        user_id = msg.getParamInt('userId')
        target_user_ids = msg.getParam('targetUserIds')
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'chat_record')
        mi = self.user_checker.check(msg)
        if mi.error:
            ftlog.warn('get_chat_record param error', user_id, target_user_ids, mi.error)
            resp.setResult('status', "error")
            resp.setError(1, mi.error)
        else:
            try:
                records = self.service.batch_record_list(user_id, target_user_ids)
                debug("ChatListSrv get_chat_record", records)
                resp.setResult('records', records)
                resp.setResult('status', "ok")
            except TYBizException, e:
                resp.setResult('status', "error")
                resp.setError(e.errorCode, e.message)
        tyrpcconn.sendToUser(user_id, resp)

    @typlugin.markPluginEntry(cmd='chat', act="get_next_chat_record", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def get_next_chat_record(self, msg):
        """
        获取某条消息以后的聊天记录.
        """
        debug("ChatListSrv : get_next_chat_record : msg = ", msg)
        user_id = msg.getParamInt('userId')
        target_user_ids = msg.getParam('targetUserIds')
        message_ids = msg.getParam('messageIds')
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'chat_record')
        mi = self.user_checker.check(msg)
        if mi.error:
            ftlog.warn('get_next_chat_record param error', user_id, target_user_ids, mi.error)
            resp.setResult('status', "error")
            resp.setError(1, mi.error)
        else:
            try:
                records = self.service.batch_next_record_list(user_id, target_user_ids, message_ids)
                debug("ChatListSrv get_next_chat_record", records)
                resp.setResult('records', records)
                resp.setResult('status', "ok")
            except TYBizException, e:
                resp.setResult('status', "error")
                resp.setError(e.errorCode, e.message)
        tyrpcconn.sendToUser(user_id, resp)

    @typlugin.markPluginEntry(cmd='chat', act="sync_chat_record", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def sync_chat_record(self, msg):
        """
        同步某些指定messageID的消息.
        """
        debug("ChatListSrv : sync_chat_record : msg = ", msg)
        user_id = msg.getParamInt('userId')
        target_user_id = msg.getParam('targetUserId')
        message_ids = msg.getParam('messageIds')
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'chat_record')
        mi = self.user_checker.check(msg)
        if mi.error:
            ftlog.warn('sync_chat_record param error', user_id, target_user_id, mi.error)
            resp.setResult('status', "error")
            resp.setError(1, mi.error)
        else:
            try:
                records = self.service.sync_chat_record(user_id, target_user_id, message_ids)
                debug("ChatListSrv sync_chat_record", records)
                resp.setResult('records', records)
                resp.setResult('status', "ok")
            except TYBizException, e:
                resp.setResult('status', "error")
                resp.setError(e.errorCode, e.message)
        tyrpcconn.sendToUser(user_id, resp)

    @typlugin.markPluginEntry(cmd='chat', act="sync_server_time", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def sync_server_time(self, msg):
        """
        同步某些指定messageID的消息.
        """
        debug("ChatListSrv : sync_server_time : msg = ", msg)
        user_id = msg.getParamInt('userId')
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'sync_server_time')
        #TODO 切换到redis时间
        now = current_milli_time()
        resp.setResult('serverTime', now)
        resp.setResult('status', "ok")
        tyrpcconn.sendToUser(user_id, resp)


    # @typlugin.markPluginEntry(cmd='chat', act="get_chat_list", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    # def get_chat_list(self, msg):
    #     """
    #     获取聊天会话列表.
    #     """
    #     user_id = msg.getParamInt('userId')
    #     flag = msg.getParamInt('flag')
    #     debug("ChatListSrv : get_chat_list", user_id, flag)
    #     resp = MsgPack()
    #     resp.setCmd('chat')
    #     resp.setResult('action', 'get_chat_list')
    #     mi = self.user_checker.check(msg)
    #     mi2 = self.flag_checker.check(msg)
    #     if mi.error or mi2:
    #         ftlog.warn('get_chat_record param error', user_id, flag, mi.error, mi2.error)
    #         resp.setResult('ok', 0)
    #         resp.setError(1, mi.error if mi.error else mi2.error)
    #     try:
    #         chat_list = self.service.get_chat_list(user_id, flag)
    #         resp.setResult('chatList', chat_list)
    #         resp.setResult('ok', 1)
    #     except TYBizException, e:
    #         resp.setResult('ok', 0)
    #         resp.setError(e.errorCode, e.message)
    #     tyrpcconn.sendToUser(user_id, resp)

    # @typlugin.markPluginEntry(cmd='chat', act="del_chat", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    # def del_chat(self, msg):
    #     """
    #     删除聊天会话.
    #     """
    #     user_id = msg.getParamInt('userId')
    #     target_user_id = msg.getParamInt('targetUserId')
    #     debug("ChatListSrv : del_chat  ", user_id, target_user_id)
    #     resp = MsgPack()
    #     resp.setCmd('chat')
    #     resp.setResult('action', 'del_chat')
    #     mi = self.checkBase.check(msg)
    #     if mi.error:
    #         ftlog.warn('del_chat param error', user_id, target_user_id, mi.error)
    #         resp.setResult('ok', 0)
    #         resp.setError(1, mi.error)
    #     else:
    #         try:
    #             self.service.del_chat(user_id, target_user_id)
    #             resp.setResult('ok', 1)
    #         except TYBizException, e:
    #             resp.setResult('ok', 0)
    #             resp.setError(e.errorCode, e.message)
    #     tyrpcconn.sendToUser(user_id, resp)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def doDelChat(self, user_id, target_user_id):
        """
        开放SNS删除好友后的删除会话.
        :param user_id: 发送方的userId
        :param target_user_id: 要删除的玩家ID
        :return:
        """
        debug("ChatListSrv doDelChat:", user_id, target_user_id)
        if isinstance(user_id, int) and user_id > 0 and isinstance(target_user_id, int) and target_user_id > 0:
            self.service.del_chat(user_id, target_user_id)
            # 告知对方
            resp = MsgPack()
            resp.setCmd('sns')
            resp.setResult('action', 'friend_change')
            resp.setResult('user_id', user_id)
            resp.setResult('target_user_id', target_user_id)
            tyrpcconn.sendToUser(target_user_id, resp)
            return 1
        else:
            ftlog.warn('doDelChat param error', user_id, target_user_id)
            return 0

    ##############################################

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def doSomething(self, userId, msg):
        """
        开放给外部应用的消息发送RPC接口示例.
        :param message: 消息内容
        :return:
        """
        debug("doSomething:", userId, msg)
        return 1