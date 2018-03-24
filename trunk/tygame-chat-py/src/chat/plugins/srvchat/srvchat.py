# -*- coding: utf-8 -*-
"""
Created on 2018年03月10日17:39:53

@author: yzx

运行于GU进程,处理聊天对话.
1. 上行 chat#send_message
userId,targetUserId,msgType,content,cid
文本 0 {"text":"hello"}
表情 1 {"emoticon":"hello"}
游戏邀请 2 {"miniGameId":601,"code":"invite"}
游戏应答 2 {"msgId":601,"code":"accept/refuse/leave/result"}
语音 4 {"voice":"abcd","second":3}
文件 5 {"file":"abcd"}
小视频 6 {"video":"abcd","second":2,"pic":"aaa"}
系统消息 7 {"code":"sns","status":"invite|accept"}

2. 上行应答 chat#send_message
{"msgId":"","cid":"","time":"","status":"ok|error|notFriend"}

3. 下行 chat#receive_message
fromUserId,msgType,content
游戏消息
status:[0默认1通过3拒绝]
{"msgId":"","miniGameId":601,"time":"",status:""}
3.1 游戏结果下推result
{"msgId":"","miniGameId":601,"time":"",status:"","result":0|1|2}

## 游戏结果

"""

import uuid

import chat.entity.chat_dao as _dao
from chat.entity.chat_dao import DaoChatRecordRedis
from chat.entity.chat_service import ChatService
from chat.entity.dirtyword_filter import DirtyWordFilter
from chat.entity.exceptions import StrangerException
from chat.entity.friend_validation import FriendValidation
from chat.entity.models import ChatMessage, GameChatMessage, SystemChatMessage
from chat.entity.rpc_adapter import _check_friend, get_online_state, get_user_last_time
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

#游戏邀请的生命周期，默认1分钟
LIFE_CYCLE=1

class ChatSrv(typlugin.TYPlugin):
    """
    聊天服务插件，专注点对点的消息.
    """

    def __init__(self):
        super(ChatSrv, self).__init__()
        self.cache = []
        self.cache_size = 2000
        self.channels = {}
        self.tmp_channels = {}
        self.verifiers = []
        self.service = None
        self.init_service()


    def destoryPlugin(self):
        super(ChatSrv, self).destoryPlugin()
        _dao.DaoUserChatRecordZSet.finalize()
        _dao.DaoChatRecordHash.finalize()
        # _dao.DaoUserChatListHash.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_UTIL])
    def initPluginBefore(self):
        debug("ChatSrv initPluginBefore")
        _dao.DaoUserChatRecordZSet.initialize()
        _dao.DaoChatRecordHash.initialize()
        # _dao.DaoUserChatListHash.initialize()


    def init_service(self):
        debug("ChatSrv init")
        dirty_word = DirtyWordFilter()
        friend = FriendValidation()
        self.verifiers.append(dirty_word)
        #TODO 每条消息都验证是否好友可能不合理（创建一个好友对话通道，有通道不验证，无通道才做验证,通道带生命周期）
        self.verifiers.append(friend)
        self.service = ChatService()
        self.service.record_dao = DaoChatRecordRedis()
        ftcore.runLoopSync(0.1, self.send_talk_message)

    def verify_0(self, msg):
        content = msg.getParamStr("content")
        #TODO 脏话
        time = current_milli_time()
        msg_id = self.get_message_id(msg,time)
        return msg_id,content,time

    def verify_normal(self, msg):
        content = msg.getParamStr("content")
        time = current_milli_time()
        msg_id = self.get_message_id(msg,time)
        return msg_id, content, time

    def verify_2(self, msg):
        content = msg.getParamStr("content")
        obj = ftstr.loads(content)
        message_id = obj.get("msgId","")
        if message_id:
            code = obj.get("code", "refuse")
            info = self.service.get_record(message_id)
            if info:
                time = info.get("time")
                content = info.get("content")
                mini_game_id = ftstr.loads(content).get("miniGameId")
                info = {"miniGameId": mini_game_id, "code": code}
                content = ftstr.dumps(info)
            else:
                raise StrangerException()
        else:
            # TODO 校验minigameID及code
            time = current_milli_time()
            message_id = self.get_message_id(msg,time)
        return message_id, content, time

    def verify_4(self, msg):
        content = msg.getParamStr("content")
        time = current_milli_time()
        msg_id = self.get_message_id(msg,time)
        return msg_id, content, time

    def do_verify(self, msg):
        # for verifier in self.verifiers:
        #     verifier.do_verify(msg)
        method_name = 'verify_' + str(msg.getParamInt('msgType'))
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, self.verify_normal)
        # Call the method as we return it
        return method(msg)

    def get_message_id(self,msg,time):
        msg_id = msg.getParamStr("msgId")
        if not msg_id:
            # msgId = str(uuid.uuid1())
            user_id = msg.getParamInt('userId')
            target_user_id = msg.getParamInt('targetUserId')
            msg_id = get_msg_id(user_id,target_user_id,time)
        return msg_id

    # def get_time(self,msg):
    #     return current_milli_time()

    def write(self, user_id, target_user_id, message_id, content):
        self.cache.append((user_id, target_user_id,message_id, content))

    @typlugin.markPluginEntry(cmd='chat', act="create_channel", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def create_channel(self, msg):
        """
        创建临时会话.(双方各发一条，创建临时会话，防止骚扰)
        :param msg:
        :return:
        """
        debug("ChatSrv create_channel", msg)
        user_id = msg.getParamInt('userId')
        target_user_id = msg.getParamInt('targetUserId')
        is_friend = _check_friend(user_id, target_user_id)
        channel_key = _get_channel_key(user_id,target_user_id)
        #重用快速创建的通道
        if channel_key not in self.channels:
            if channel_key in self.tmp_channels:
                _ = self.tmp_channels[channel_key][0]
                if _ == user_id :
                    del self.tmp_channels[channel_key]
                    channel_uuid  = str(uuid.uuid1())
                    self.channels[channel_key] = channel_uuid
                    debug("ChatSrv create_channel", user_id, target_user_id, channel_uuid)
                else:
                    debug("ChatSrv create_channel again", user_id, target_user_id,self.tmp_channels[channel_key])
                    self.tmp_channels[channel_key] = [target_user_id]
            else:
                self.tmp_channels[channel_key] = [target_user_id]
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'create_channel')
        try:
            online_state = get_online_state(target_user_id)
            author_time,last_time = get_user_last_time(target_user_id)
            resp.setResult('userId', user_id)
            resp.setResult('targetUserId', target_user_id)
            resp.setResult('onlineState', online_state)
            resp.setResult('authorTime', author_time)
            resp.setResult('lastTime', last_time)
            resp.setResult('isFriend', is_friend)
            resp.setResult('status', "ok")
        except TYBizException, e:
            resp.setResult('status', "error")
            resp.setError(e.errorCode, e.message)
        tyrpcconn.sendToUser(user_id, resp)


    @typlugin.markPluginEntry(cmd='chat', act="leave_channel", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def leave_channel(self, msg):
        """
        离开临时会话.(一方退出即终结临时会话)
        :param msg:
        :return:
        """
        debug("ChatSrv leave_channel", msg)
        user_id = msg.getParamInt('userId')
        target_user_id = msg.getParamInt('targetUserId')
        channel_key = _get_channel_key(user_id, target_user_id)
        if channel_key in self.channels:
            del self.channels[channel_key]
            debug("ChatSrv clean channel", channel_key)
            is_friend = _check_friend(user_id, target_user_id)
            if not is_friend:
                now = current_milli_time()
                msg_id = get_msg_id(user_id, target_user_id, now)
                content = ftstr.dumps({"code": "chat", "status": "leave_channel"})
                system_message = ChatMessage(user_id, target_user_id, 7, now, content)
                self.service.save_record(user_id, target_user_id, msg_id, system_message)
                # 回应对方离线
                self.write(target_user_id, user_id, msg_id, system_message)
                # TODO 清理临时聊天消息
            ftcore.runOnceDelay(0.1, self.__do_leave_game_message,user_id, target_user_id)
        if channel_key in self.tmp_channels:
            del self.tmp_channels[channel_key]
            debug("ChatSrv clean temp channel", channel_key)

    def __do_leave_game_message(self, user_id, target_user_id):
        """
        清理多余的游戏邀请.
        """
        now = current_milli_time()
        before = now - LIFE_CYCLE*60*1000
        message_ids = self.service.do_leave_chat_record(user_id,target_user_id,before)
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'leave_game_message')
        resp.setResult('uid1', user_id)
        resp.setResult('uid2', target_user_id)
        resp.setResult('messageIds', message_ids)
        debug("ChatSrv __do_leave_game_message", user_id, target_user_id,resp)
        tyrpcconn.sendToUser(user_id, resp)
        tyrpcconn.sendToUser(target_user_id, resp)



    @typlugin.markPluginEntry(cmd='chat', act="check_channel", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def check_channel(self, msg):
        """
        检查通道是否存在.
        :param msg:
        :return:
        """
        user_id = msg.getParamInt('userId')
        target_user_id = msg.getParamInt('targetUserId')
        channel_key = _get_channel_key(user_id, target_user_id)
        debug("ChatSrv check_channel", user_id, target_user_id)
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'check_channel')
        if channel_key in self.channels:
            resp.setResult('ok', 1)
        else:
            resp.setResult('ok', 0)
        tyrpcconn.sendToUser(user_id, resp)

    @typlugin.markPluginEntry(cmd='chat', act="send_message", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def talk_message1(self, msg):
        """
        聊天消息.
        :param msg: userId,targetUserId,msgType,content,cid
        :return: msgId,ok
        """
        debug("ChatSrv talk_message", msg)
        user_id = msg.getParamInt('userId')
        target_user_id = msg.getParamInt('targetUserId')
        msg_type = msg.getParamInt('msgType')
        content = msg.getParamStr('content')
        #客户端消息序号
        sn = msg.getParamStr('sn')
        is_friend = _check_friend(user_id,target_user_id)
        debug("ChatSrv talk_message", user_id, target_user_id, msg_type, content, sn, is_friend)
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'send_message')
        try:
            msg_id, content, now = self.do_verify(msg)
            channel_key = _get_channel_key(user_id, target_user_id)
            if not is_friend and channel_key not in self.channels  :
                # 临时会话已关闭，不允许发送消息
                resp.setResult("status", "notFriend")
            else:
                obj = ftstr.loads(content)
                game_code = obj.get("code", "")
                if game_code == "" or game_code == "invite":
                    info = {
                        "time": now,
                        "userId": user_id,
                        "targetUserId": target_user_id,
                        "msgType": msg_type,
                        "content": content
                    }
                else:
                    # 游戏更新不更改初始来源
                    info = {
                        "time": now,
                        "userId": target_user_id,
                        "targetUserId": user_id,
                        "msgType": msg_type,
                        "content": content
                    }
                self.write(user_id,target_user_id,msg_id,info)
                self.service.save_record(user_id, target_user_id, msg_id, info)
                resp.setResult('sn', sn)
                resp.setResult('time', now)
                resp.setResult('msgId', msg_id)
                resp.setResult('status', "ok")
        except TYBizException, e:
            resp.setResult("status", "error")
            resp.setError(e.errorCode, e.message)
        tyrpcconn.sendToUser(user_id, resp)
        #msgId{"userId":1001,"targetUserId":1002,"msgType":1,"content":"hello"}(Hash)
        #userId{"msgId","20180223111415"}(SortedSet)

    @typlugin.markPluginEntry(cmd='chat', act="send_message2", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    def talk_message(self, msg):
        """
        聊天消息.
        :param msg: userId,targetUserId,msgType,content,cid
        :return: msgId,ok
        """
        debug("ChatSrv talk_message", msg)
        user_id = msg.getParamInt('userId')
        target_user_id = msg.getParamInt('targetUserId')
        msg_type = msg.getParamInt('msgType')
        content = msg.getParamStr('content')
        # 客户端消息序号
        sn = msg.getParamStr('sn')
        is_friend = _check_friend(user_id, target_user_id)
        debug("ChatSrv talk_message", user_id, target_user_id, msg_type, content, sn, is_friend)
        resp = MsgPack()
        resp.setCmd('chat')
        resp.setResult('action', 'send_message')
        try:
            channel_key = _get_channel_key(user_id, target_user_id)
            if not is_friend and channel_key not in self.channels:
                # 临时会话已关闭，不允许发送消息
                resp.setResult("status", "notFriend")
            else:
                game_obj = ftstr.loads(content)
                message_id = game_obj.get("msgId", "")
                if message_id:
                    # 游戏应答
                    code = game_obj.get("code", "refuse")
                    info = self.service.get_record(message_id)
                    if info:
                        chat_message = GameChatMessage.load_info(info)
                        chat_message.code = code
                    else:
                        raise StrangerException()
                else:
                    time = current_milli_time()
                    message_id = get_msg_id(user_id,target_user_id,time)
                    chat_message = ChatMessage(user_id,target_user_id,msg_type,time,content)
                self.write(user_id, target_user_id, message_id, chat_message)
                self.service.save_record(user_id, target_user_id, message_id, chat_message)
                resp.setResult('sn', sn)
                # resp.setResult('time', time)
                resp.setResult('msgId', message_id)
                resp.setResult('status', "ok")
        except TYBizException, e:
            resp.setResult("status", "error")
            resp.setError(e.errorCode, e.message)
        tyrpcconn.sendToUser(user_id, resp)
        # msgId{"userId":1001,"targetUserId":1002,"msgType":1,"content":"hello"}(Hash)
        # userId{"msgId","20180223111415"}(SortedSet)


    # @typlugin.markPluginEntry(cmd='chat', act="game_message", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    # def game_message(self, msg):
    #     """
    #     接受游戏对战消息.
    #     :param msg: userId,targetUserId,miniGameId
    #     :return: msgId,ok
    #     """
    #     user_id = msg.getParamInt('userId')
    #     target_user_id = msg.getParamInt('targetUserId')
    #     mini_game_id = msg.getParamInt('miniGameId')
    #     is_friend = _check_friend(user_id, target_user_id)
    #     debug("ChatSrv receive_game_message", user_id, target_user_id, mini_game_id)
    #
    #     resp = MsgPack()
    #     resp.setCmd('chat')
    #     resp.setResult('action', 'game_message')
    #     now = fttime.getCurrentTimestamp()
    #     try:
    #         msg_id = str(uuid.uuid1())
    #         if is_friend:
    #             info = {
    #                 "time": now,
    #                 "userId": user_id,
    #                 "targetUserId": target_user_id,
    #                 "msgType": 1,
    #                 "miniGameId": mini_game_id,
    #                 "status":0
    #             }
    #             self.service.save_record(user_id, target_user_id, msg_id, info)
    #             ftcore.runOnceDelay(0.1, self.__do_game_message, msg, msg_id)
    #             resp.setResult('msgId', msg_id)
    #             resp.setResult('ok', 1)
    #         else:
    #             channel_key = _get_channel_key(user_id, target_user_id)
    #             if channel_key in self.channels :
    #                 info = {
    #                     "time": now,
    #                     "userId": user_id,
    #                     "targetUserId": target_user_id,
    #                     "msgType": 1,
    #                     "miniGameId": mini_game_id,
    #                     "status": 0
    #                 }
    #                 self.service.save_record(user_id, target_user_id, msg_id, info)
    #                 ftcore.runOnceDelay(0.1, self.__do_game_message, msg, msg_id)
    #                 resp.setResult('msgId', msg_id)
    #                 resp.setResult('ok', 1)
    #             else:
    #                 #临时会话已关闭，不允许发送消息
    #                 resp.setResult('ok', 2)
    #     except TYBizException, e:
    #         resp.setResult('ok', 0)
    #         resp.setError(e.errorCode, e.message)
    #     tyrpcconn.sendToUser(user_id, resp)
    #
    #
    # def __do_game_message(self, msg, msg_id):
    #     target_user_id = msg.getParamInt('targetUserId')
    #     mini_game_id = msg.getParamInt('miniGameId')
    #     user_id = msg.getParamInt('userId')
    #     resp = MsgPack()
    #     resp.setCmd('chat')
    #     resp.setResult('action', 'receive_game_message')
    #     resp.setResult('fromUserId', user_id)
    #     resp.setResult('miniGameId', mini_game_id)
    #     resp.setResult('msgId', msg_id)
    #     tyrpcconn.sendToUser(target_user_id, resp)
    #
    # def __do_answer_message(self, msg, msg_id):
    #     target_user_id = msg.getParamInt('targetUserId')
    #     code = msg.getParamInt('code')
    #     user_id = msg.getParamInt('userId')
    #     resp = MsgPack()
    #     resp.setCmd('chat')
    #     resp.setResult('action', 'receive_answer_message')
    #     resp.setResult('fromUserId', user_id)
    #     resp.setResult('code', code)
    #     resp.setResult('msgId', msg_id)
    #     tyrpcconn.sendToUser(target_user_id, resp)
    #

    # @typlugin.markPluginEntry(cmd='chat', act="answer_game_message", srvType=tyglobal.SRV_TYPE_GAME_UTIL)
    # def answer_game_message(self, msg):
    #     """
    #     响应游戏对战消息.
    #     :param msg: userId,targetUserId,msgId,code
    #     :return: ok
    #     """
    #     debug("ChatSrv answer_game_message", msg)
    #     user_id = msg.getParamInt('userId')
    #     target_user_id = msg.getParamInt('targetUserId')
    #     msg_id = msg.getParamStr('msgId')
    #     code = msg.getParamStr('code')
    #     # sn = msg.getParamStr('sn')
    #     debug("ChatSrv answer_game_message", user_id, target_user_id, msg_id, code)
    #     resp = MsgPack()
    #     resp.setCmd('chat')
    #     resp.setResult('action', 'answer_game_message')
    #     try:
    #             is_friend = _check_friend(user_id, target_user_id)
    #             info = self.service.get_record(msg_id)
    #             time = info.get("time")
    #             content = info.get("content")
    #             msg_type = info.get("msgType")
    #             mini_game_id = ftstr.loads(content).get("miniGameId")
    #             info = {"miniGameId": mini_game_id, "code": code}
    #             channel_key = _get_channel_key(user_id, target_user_id)
    #             if not is_friend and channel_key not in self.channels:
    #                 # 临时会话已关闭，不允许发送消息
    #                 resp.setResult("status", "notFriend")
    #             else:
    #                 info = {
    #                     "time": time,
    #                     "userId": user_id,
    #                     "targetUserId": target_user_id,
    #                     "msgType": msg_type,
    #                     "content": ftstr.dumps(info)
    #                 }
    #                 self.write(user_id, target_user_id, msg_id, info)
    #                 self.service.save_record(user_id, target_user_id, msg_id, info)
    #                 # resp.setResult('sn', sn)
    #                 resp.setResult('time', time)
    #                 resp.setResult('msgId', msg_id)
    #                 resp.setResult('status', "ok")
    #     except TYBizException, e:
    #         resp.setResult("status", "error")
    #         resp.setError(e.errorCode, e.message)
    #     tyrpcconn.sendToUser(user_id, resp)


    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def sns_system_message(self, user_id, target_user_id, code):
        """
        收到添加好友邀请/添加好友邀请被通过.
        :param user_id:
        :param target_user_id:
        :param code:
        :return:
        """
        debug("ChatSrv sns_system_message", user_id, target_user_id, code)
        # resp = MsgPack()
        # resp.setCmd('chat')
        #1 xxx,请求添加你为好友(不存储/打招呼的语言-以上是打招呼的内容)
        #2 你的添加好友请求已被xxx通过(生成一条你们刚刚成为好友/你已经添加xxx，现在可以开始聊天了。)
        #3 对方已离开聊天，添加好友继续聊天
        #4 xxx(你),撤回了一条消息
        #5 你的消息不能够送达(被删除、屏蔽)
        #6 游戏结果
        now = current_milli_time()
        code_status = ["invite", "accept"][code-1]
        content = ftstr.dumps({"code": "sns", "status": code_status})
        system_message = ChatMessage(user_id, target_user_id, 7, now, content)
        msg_id = get_msg_id(user_id,target_user_id,now)
        # 申请不计入聊天消息
        if code == 1:
            self.service.save_record(user_id, target_user_id, msg_id, system_message)
        # 各回应一条
        self.write(user_id, target_user_id, msg_id, system_message)
        self.write(target_user_id, user_id, msg_id, system_message)
        return 1


    @typlugin.markPluginEntry(export=1)
    def game_result_message(self, user_id, target_user_id, msg_id,info):
        debug("ChatSrv game_result_message", user_id, target_user_id, msg_id,info)
        self.write(user_id, target_user_id, msg_id, info)
        self.write(target_user_id, user_id, msg_id, info)


    def send_talk_message(self):
        """
        聊天消息发送循环.
        """
        while len(self.cache) > 0:
            _ = self.cache.pop()
            user_id = _[0]
            target_user_id = _[1]
            message_id = _[2]
            content = _[3]
            resp = MsgPack()
            resp.setCmd('chat')
            resp.setResult('action', 'receive_message')
            # resp.setResult('userId', target_user_id)
            # resp.setResult('fromUserId', user_id)
            resp.setResult('msgId', message_id)
            if isinstance(content, ChatMessage):
                resp.setResult('content', content.getDict())
            else:
                resp.setResult('content', content)
            debug("ChatSrv send_talk_message loop", target_user_id, resp)
            tyrpcconn.sendToUser(target_user_id, resp)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_UTIL)
    def http_test_talk_message(self, user_id, msg):
        debug("ChatSrv http_test_talk_message", user_id, msg)
        resp = MsgPack()
        resp.unpack(msg)
        self.talk_message(resp)
        return 1