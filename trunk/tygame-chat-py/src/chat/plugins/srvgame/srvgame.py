# -*- coding: utf-8 -*-
"""
Created on 2018年03月10日17:39:53

@author: yzx

运行于GU进程,处理游戏结果界面对战消息互传。
"""

import chat.entity.chat_dao as _dao
from chat.entity.chat_dao import DaoChatRecordRedis
from chat.entity.chat_service import ChatService
from chat.entity.exceptions import StrangerException
from chat.entity.models import GameChatMessage
from chat.entity.rpc_adapter import _upload_vs_record, push_game_message
from chat.entity.utils import current_milli_time, get_msg_id, _get_channel_key
from freetime5.twisted import ftcore
from freetime5.util import ftlog, ftstr
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import typlugin, tyrpcconn, tyglobal
from tuyoo5.core.tyconfig import TYBizException

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class ChatGameSrv(typlugin.TYPlugin):
    """
    聊天游戏服务插件，专注对战结果界面的对战邀请消息.
    """

    def __init__(self):
        super(ChatGameSrv, self).__init__()
        self.service = ChatService()
        self.service.record_dao = DaoChatRecordRedis()
        self.tmp_channels = {}


    def destoryPlugin(self):
        super(ChatGameSrv, self).destoryPlugin()
        _dao.DaoUserChatRecordZSet.finalize()
        _dao.DaoChatRecordHash.finalize()
        # _dao.DaoUserChatListHash.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginBefore(self):
        debug("ChatGameSrv initPluginBefore")
        _dao.DaoUserChatRecordZSet.initialize()
        _dao.DaoChatRecordHash.initialize()
        # _dao.DaoUserChatListHash.initialize()

    def check_channel(self, user_id, target_user_id):
        """
        创建临时会话.(双方各发一条，创建临时会话，防止骚扰)
        :return:
        """
        channel_key = _get_channel_key(user_id,target_user_id)
        debug("ChatGameSrv check_channel", channel_key, self.tmp_channels)
        if channel_key in self.tmp_channels:
            _ = self.tmp_channels[channel_key][0]
            if _ == user_id:
                now = self.tmp_channels[channel_key][1]
                msg_id = self.tmp_channels[channel_key][2]
                del self.tmp_channels[channel_key]
                debug("ChatGameSrv end_channel", user_id, target_user_id,now,msg_id)
                return True,now,msg_id
        now = current_milli_time()
        msg_id = get_msg_id(user_id, target_user_id, now)
        self.tmp_channels[channel_key] = [target_user_id,now,msg_id]
        debug("ChatGameSrv create_channel", user_id, target_user_id, now, msg_id)
        return False,now,msg_id

    def clean_channel(self, user_id, target_user_id):
        """
        创建临时会话.(双方各发一条，创建临时会话，防止骚扰)
        :return:
        """
        debug("ChatGameSrv do clean_channel", user_id, target_user_id)
        channel_key = _get_channel_key(user_id,target_user_id)
        if channel_key in self.tmp_channels:
            del self.tmp_channels[channel_key]
            debug("ChatSrv clean_channel", user_id, target_user_id)


    @typlugin.markPluginEntry(cmd='chat', act="again_game", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    # @lockargname('hall5.item', 'userId')
    def again_game(self, msg):
        """
        再来一局.
        TODO 并发
        :param msg: userId,targetUserId,miniGameId
        :return: msgId,ok
        """
        debug("ChatGameSrv again_game", msg)
        user_id = msg.getParamInt('userId')
        target_user_id = msg.getParamInt('targetUserId')
        mini_game_id = msg.getParamInt('miniGameId')
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'again_game')
        try:
            double_again,now,msg_id = self.check_channel(user_id,target_user_id)
            if double_again:
                info = self.service.get_record(msg_id)
                if info:
                    game_message = GameChatMessage.load_info(info)
                    game_message.code = "accept"
                    self.service.save_record(user_id, target_user_id, msg_id, game_message)
                    ftcore.runOnceDelay(0.1, self.__do_answer_again_game_message, user_id, target_user_id, "accept",
                                        msg_id)
                    push_game_message(user_id, target_user_id, msg_id, game_message)
                    resp.setResult('status', 'error')
                else:
                    raise StrangerException()
            else:
                content = ftstr.dumps({'miniGameId': mini_game_id, 'code': 'invite'})
                game_message = GameChatMessage(user_id, target_user_id, 2, now, content)
                self.service.save_record(user_id, target_user_id, msg_id, game_message)
                ftcore.runOnceDelay(0.1, self.__do_again_game_message,user_id,target_user_id,msg_id)
                push_game_message(user_id, target_user_id, msg_id, game_message)
                debug("ChatGameSrv again_game", msg_id)
                resp.setResult('msgId', msg_id)
                resp.setResult('userId', user_id)
                resp.setResult('targetUserId', target_user_id)
                resp.setResult('status', 'ok')
        except TYBizException, e:
            resp.setResult('status', 'error')
            resp.setError(e.errorCode, e.message)
        tyrpcconn.sendToUser(user_id, resp)

    def __do_again_game_message(self, user_id, target_user_id, message_id):
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'again_game_push')
        resp.setResult('userId', user_id)
        resp.setResult('targetUserId', target_user_id)
        resp.setResult('msgId', message_id)
        tyrpcconn.sendToUser(target_user_id, resp)


    @typlugin.markPluginEntry(cmd='chat', act="answer_again_game", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def answer_again_game(self, msg):
        """
        再来一局应答.
        :param msg: userId,targetUserId,miniGameId
        :return: msgId,ok
        """
        debug("ChatGameSrv answer_again_game", msg)
        user_id = msg.getParamInt('userId')
        target_user_id = msg.getParamInt('targetUserId')
        msg_id = msg.getParamStr('msgId')
        code = msg.getParamStr('code')
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'answer_again_game')
        try:
            self.clean_channel(user_id,target_user_id)
            info = self.service.get_record(msg_id)
            if info:
                game_message = GameChatMessage.load_info(info)
                game_message.code = code
                self.service.save_record(user_id, target_user_id, msg_id, game_message)
                ftcore.runOnceDelay(0.1, self.__do_answer_again_game_message, user_id, target_user_id, code, msg_id)
                push_game_message(user_id, target_user_id, msg_id, game_message)
                resp.setResult('msgId', msg_id)
                resp.setResult('userId', user_id)
                resp.setResult('targetUserId', target_user_id)
                resp.setResult('status', 'ok')
            else:
                resp.setResult('status', 'error msgId')
        except TYBizException, e:
            resp.setResult('status', 'error')
            resp.setError(e.errorCode, e.message)
        tyrpcconn.sendToUser(user_id, resp)

    def __do_answer_again_game_message(self, user_id, target_user_id, code, message_id):
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'answer_again_game_push')
        resp.setResult('userId', user_id)
        resp.setResult('targetUserId', target_user_id)
        resp.setResult('code', code)
        resp.setResult('msgId', message_id)
        tyrpcconn.sendToUser(target_user_id, resp)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def doReportGameResult(self, userId, mini_game_id, msg):
        """
        小游戏比赛服上报游戏结果.
        mo.setResult('winnerId', self.winnerId)
        mo.setResult('userId_a', self.userId_a)
        mo.setResult('userId_b', self.userId_b)
        mo.setResult('table_msgId', self.table_msgId)
        """
        debug("ChatGameSrv : report_game_result : msg = ",userId,mini_game_id, msg, type(msg))
        msg = ftstr.loads(msg)
        user_id = msg.get('userId_a')
        target_user_id = msg.get('userId_b')
        win_user_id = msg.get('winnerId')
        if isinstance(user_id, int) and user_id > 0 and isinstance(target_user_id, int) and target_user_id > 0 and \
                isinstance(win_user_id, int):
            msg_id = msg.get('table_msgId')
            if not msg_id or msg_id == -1:
                now = current_milli_time()
                msg_id = get_msg_id(user_id, target_user_id, now)
                content = ftstr.dumps({'miniGameId': mini_game_id, 'code': 'result'})
                game_message = GameChatMessage(user_id, target_user_id, 2, now, content)
                self.service.save_record(user_id, target_user_id, msg_id, game_message)

            debug("ChatGameSrv report_game_result", user_id, target_user_id, msg_id, win_user_id)
            self.service.save_record_result(user_id, target_user_id, msg_id, win_user_id)
            record = self.service.get_record(msg_id)
            if record:
                # 结果推送给双方
                game_message = GameChatMessage.load_info(record)
                push_game_message(user_id, target_user_id, msg_id, game_message)
                # 所有的对战消息都在sns中存储为对战记录
                _upload_vs_record(user_id, target_user_id, mini_game_id, win_user_id)
                return 1
        return 0

    @typlugin.markPluginEntry(cmd='chat', act="change_game", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def change_game(self, msg):
        """
        换个游戏.
        :param msg: userId,targetUserId,messageId
        :return: msgId,ok
        """
        debug("ChatGameSrv change_game", msg)
        user_id = msg.getParamInt('userId')
        target_user_id = msg.getParamInt('targetUserId')
        self.clean_channel(user_id, target_user_id)
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'change_game')
        resp.setResult('userId', user_id)
        resp.setResult('targetUserId', target_user_id)
        tyrpcconn.sendToUser(target_user_id, resp)



