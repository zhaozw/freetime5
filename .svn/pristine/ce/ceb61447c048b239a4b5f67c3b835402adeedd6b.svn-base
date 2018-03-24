# -*- coding=utf-8 -*-
"""
Created on 2017年11月02日10:14:41

@author: yzx

TODO List
1) 添加好友消息过期
2）添加玩家时候查看玩家常玩的小游戏

"""
from chat.entity.chat_dao import DaoChatRecord
from chat.entity.models import ChatMessage
from chat.entity.rpc_adapter import _search_user_by_id
from freetime5.util import ftlog, ftstr
from tuyoo5.core.typlugin import pluginCross

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass



class ChatService(object):
    ST_FOLLOW = 1  # 粉
    ST_EXPIRED = 2  # 过期
    ST_REFUSE = 3  # 拒绝
    ST_ACCEPT = 4  # 接受

    def __init__(self):
        super(ChatService, self).__init__()
        self.__record_dao = DaoChatRecord()

    @property
    def record_dao(self):
        return self.__record_dao

    @record_dao.setter
    def record_dao(self, value):
        """
        The setter of the dao property
        """
        if isinstance(value, DaoChatRecord):
            self.__record_dao = value

    def save_record(self, user_id,target_user_id,message_id,info):
        message = self.record_dao.get_record_info(message_id)
        if not message:
            if isinstance(info, ChatMessage):
                self.record_dao.save_message_record(message_id, info.getDict())
                self.record_dao.save_user_record(user_id, target_user_id, message_id, info.time)
            else:
                self.record_dao.save_message_record(message_id, info)
                self.record_dao.save_user_record(user_id, target_user_id, message_id, info["time"])
        else:
            if isinstance(info, ChatMessage):
                self.record_dao.update_record(user_id, target_user_id, message_id, info.getDict())
            else:
                self.record_dao.update_record(user_id, target_user_id, message_id, info)

    def update_record(self, user_id, target_user_id, message_id, ret):
        #ret[发起，接受，拒绝，超时]
        # 0 输 1 赢 2 平
        self.record_dao.update_record(user_id, target_user_id, message_id, ret)
        info = self.record_dao.get_record_info(message_id)

    def save_record_result(self, user_id, target_user_id, message_id, win_user_id):
        # 0 输 1 赢 2 平
        self.record_dao.save_record_result(user_id, target_user_id, message_id, win_user_id)
        # info = self.record_dao.get_record_info(message_id)
        # self.record_dao.update_user_chat_list(user_id, target_user_id, info)

    def get_record(self,message_id):
        return self.record_dao.get_record_info(message_id)


    def get_record_list(self,user_id,target_user_id):
        #TODO翻页(根据时间戳取值)
        msg_list =  self.record_dao.get_record_list(user_id,target_user_id)
        debug("get_record_list",msg_list)
        res = []
        datas = len(msg_list) - 1
        i = 0
        while i < datas:
            msg = {
                "msgId":msg_list[i],
                "time": msg_list[i + 1]
            }
            info = self.record_dao.get_record_info(msg_list[i])
            msg.update(info)
            res.append(msg)
            i += 2
        debug("get_record_list",target_user_id, res)
        return res

    def get_next_record_list(self,user_id,target_user_id, message_id):
        debug("get_next_record_list", user_id,target_user_id, message_id)
        score = self.record_dao.get_user_chat_score(user_id,target_user_id,message_id)
        debug("get_next_record_list",score,type(score))
        res = []
        if score:
            # msg_list =  self.record_dao.get_next_record_list(user_id,target_user_id,score+1)
            msg_list =  self.record_dao.get_next_record_list(user_id,target_user_id,score)
            debug("get_next_record_list",msg_list)
            datas = len(msg_list) - 1
            i = 0
            while i < datas:
                msg = {
                    "msgId":msg_list[i],
                    "time": msg_list[i + 1]
                }
                info = self.get_record(msg_list[i])
                msg.update(info)
                res.append(msg)
                i += 2
        debug("get_record_list",target_user_id, res)
        return res

    def batch_record_list(self,user_id,target_user_ids):
        result = {}
        for target_user_id in target_user_ids:
            msg_list = self.get_record_list(user_id, target_user_id)
            result[target_user_id] = msg_list
        return result

    def batch_next_record_list(self,user_id,target_user_ids, message_ids):
        result = {}
        for idx, target_user_id in enumerate(target_user_ids):
            message_id = message_ids[idx]
            msg_list = self.get_next_record_list(user_id, target_user_id, message_id)
            result[target_user_id] = msg_list
        return result

    def sync_chat_record(self,user_id,target_user_id, message_ids):
        result = []
        for message_id in message_ids:
            msg = self.get_record(message_id)
            result.append(msg)
        return result

    # def get_chat_list(self, user_id, flag):
    #     if flag:
    #         chat_list =  self.record_dao.get_user_chat_list_detail(user_id)
    #         debug("get_chat_list", chat_list)
    #         ret = []
    #         for uid, v in chat_list.iteritems():
    #             user_info = _search_user_by_id(uid)
    #             if user_info:
    #                 user_info["lastMsg"] = v
    #                 user_info["onlineState"] = pluginCross.onlinedata.getOnLineState(uid)
    #                 ret.append(user_info)
    #         return ret
    #     else:
    #         chat_list = self.record_dao.get_record_list(user_id)
    #         debug("get_chat_list",chat_list)
    #         ret = []
    #         for uid in chat_list.iteritems():
    #             user_info ={
    #                 "userId":uid,
    #                 "onlineState":pluginCross.onlinedata.getOnLineState(uid)
    #             }
    #             ret.append(user_info)
    #         return ret

    def del_chat(self, user_id, target_user_id):
        #双方全删除
        self.record_dao.del_user_chat(user_id,target_user_id)
        self.record_dao.del_user_chat(target_user_id,user_id)
        #TODO 聊天记录也清除

    def do_leave_chat_record(self,user_id, target_user_id,score):
        msg_list = self.record_dao.get_next_record_list(user_id, target_user_id, score)
        debug("do_leave_chat_record", msg_list)
        datas = len(msg_list) - 1
        i = 0
        msg_ids=[]
        while i < datas:
            msg_id = msg_list[i]
            info = self.get_record(msg_list[i])
            time = info.get("time")
            msg_type = info.get("msgType")
            content = info.get("content")
            uid = info.get("userId")
            tid = info.get("targetUserId")
            content_obj = ftstr.loads(content)
            mini_game_id = content_obj.get("miniGameId")
            ex_code = content_obj.get("code")
            if ex_code == "invite":
                info = {"miniGameId": mini_game_id, "code": "leave"}
                content = ftstr.dumps(info)
                info = {
                    "time": time,
                    "userId": uid,
                    "targetUserId": tid,
                    "msgType": msg_type,
                    "content": content
                }
                self.save_record(user_id, target_user_id, msg_id, info)
            msg_ids.append(msg_id)
            i += 2
        return msg_ids


