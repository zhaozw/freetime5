# -*- coding=utf-8 -*-
"""
Created on 2017年11月02日10:14:41

@author: yzx

TODO List
1) 添加好友消息过期
2）添加玩家时候查看玩家常玩的小游戏

"""
import random

from collections import deque

from freetime5.util import fttime, ftlog, ftstr
from sns.plugins.srvhttp._private._dao import DaoFollow, DaoFriend, DaoVSRecord
from sns.plugins.srvhttp._private._rpc_adapter import search_user,del_chat,system_chat,get_online_state

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

MINI_GAMES= [602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612]

class SNSService(object):
    ST_FOLLOW = 1  # 粉
    ST_EXPIRED = 2  # 过期
    ST_REFUSE = 3  # 拒绝
    ST_ACCEPT = 4  # 接受

    def __init__(self):
        super(SNSService, self).__init__()
        self.__follow_dao = DaoFollow()
        self.__friend_dao = DaoFriend()
        self.__vs_record_dao = DaoVSRecord()
        self.active_user_line = deque(maxlen=50)

    @property
    def follow_dao(self):
        return self.__follow_dao

    @follow_dao.setter
    def follow_dao(self, value):
        """
        The setter of the dao property
        """
        if isinstance(value, DaoFollow):
            self.__follow_dao = value

    @property
    def friend_dao(self):
        return self.__friend_dao

    @friend_dao.setter
    def friend_dao(self, value):
        """
        The setter of the dao property
        """
        if isinstance(value, DaoFriend):
            self.__friend_dao = value

    @property
    def vs_record_dao(self):
        return self.__vs_record_dao

    @vs_record_dao.setter
    def vs_record_dao(self, value):
        """
        The setter of the dao property
        """
        if isinstance(value, DaoVSRecord):
            self.__vs_record_dao = value

    def get_follow_detail(self, target_userId):
        #from sdk
        basic_user_info = search_user(target_userId, None)
        #from perference
        extend_info = self.get_preference_record(target_userId)
        if extend_info:
            basic_user_info.update(extend_info)
        return basic_user_info

    def search_user(self,user_id,phone):
        return self.get_follow_detail(user_id)

    def do_follow_launch(self, user_id, target_user_id, hello, origin=""):
        # userId|targetUserId|(hello,origin)
        now = fttime.getCurrentTimestamp()
        info = {
            "time": now,
            "hello": hello,
            "sponsor": user_id,
            "origin": origin,
            "status": self.ST_FOLLOW
        }
        # 存库 --> 判断目标用户是否在线 -->推送消息到目标用户 -->返回结果
        self.follow_dao.do_follow_launch(user_id, target_user_id, info)
        system_chat(user_id, target_user_id, 1)

    def do_follow_landfall(self, user_id, target_user_id, ret):
        # 通过 --> 更新消息 --> 更新双方好友列表
        # 拒绝 --> 更新消息
        debug("do_follow_landfall: ", user_id, target_user_id, ret)
        if ret == 1:
            # userId|targetUserId|ret=1
            # 生成好友.
            # 发送好友通过消息.
            code = self.follow_dao.do_follow_landfall(user_id, target_user_id, self.ST_ACCEPT)
            if code:
                self.create_friend(user_id, target_user_id)
        elif ret == 2:
            # userId|targetUserId|ret=2
            self.follow_dao.do_follow_landfall(user_id, target_user_id, self.ST_REFUSE)
        else:
            pass



    def create_friend(self, user_id, target_user_id):
        debug("create_friend: ", user_id, target_user_id)
        now = fttime.getCurrentTimestamp()
        info = {
            "time": now,
            "last_msg": "hi",
            "remark": ""
        }
        self.friend_dao.create_friend(user_id, target_user_id, ftstr.dumps(info))
        system_chat(user_id, target_user_id, 2)

    def get_follow_list(self, userId):
        follow_list = self.follow_dao.get_follow_list(userId)
        debug("get_follow_list: ", follow_list,type(follow_list))
        for k, v in follow_list.iteritems():
            user_info = self.get_follow_detail(k)
            if user_info:
                v.update(user_info)
        # TODO 批量查询信息
        return follow_list

    def get_friend_list(self, user_id, flag=0):
        friend_list = self.friend_dao.get_friend_list(user_id)
        debug("get_friend_list: ",friend_list,type(friend_list))
        if flag:
            # 从sdk批量获取用户信息
            for k, v in friend_list.iteritems():
                user_info = self.get_follow_detail(k)
                if user_info:
                    user_info["onlineState"] = get_online_state(k)
                    v.update(user_info)
        return friend_list

    def get_friend_detail(self, user_id, target_user_id):
        #TODO check friend
        user_info = self.get_follow_detail(target_user_id)
        return user_info

    def save_vs_record(self, user_id, target_user_id, mini_game_id, win_user_id):
        self.active_user_line.append(user_id)
        self.active_user_line.append(target_user_id)
        self._do_save_vs_record(user_id,target_user_id,mini_game_id,win_user_id)
        self._do_save_vs_record(target_user_id,user_id,mini_game_id,win_user_id)
        self._do_save_game_record(user_id,mini_game_id,win_user_id)
        self._do_save_game_record(target_user_id,mini_game_id,win_user_id)

    def _do_save_game_record(self, user_id, mini_game_id, win_user_id):
        # 只更新自己身上的游戏记录
        info = self.vs_record_dao.get_game_record(user_id, mini_game_id)
        # 0 输 1 赢 2 平
        if not info:
            info = [0, 0, 0]
        if win_user_id == -1:
            code = 2
        elif win_user_id == user_id:
            code = 1
        else:
            code = 0
        if code < len(info):
            info[code] = info[code] + 1
        debug("_do_save_game_record: ", info)
        self.vs_record_dao.save_game_record(user_id, mini_game_id, info)


    def _do_save_vs_record(self, user_id, target_user_id, mini_game_id, win_user_id):
        # 只更新自己身上的VS记录
        info = self.vs_record_dao.get_vs_record(user_id, target_user_id)
        # 0 输 1 赢 2 平
        if not info:
            info = {
                "total": [0, 0, 0],
                mini_game_id: [0, 0, 0]
            }
        if win_user_id == -1:
            code = 2
        elif win_user_id == user_id:
            code = 1
        else:
            code = 0
        debug("_do_save_vs_record: ", info, type(info))
        info["total"][code] = info["total"][code] + 1
        if str(mini_game_id) not in info:
            _ = [0, 0, 0]
            _[code] = _[code] + 1
            info[str(mini_game_id)] = _
        else:
            info[str(mini_game_id)][code] = info[str(mini_game_id)][code] + 1
        debug("_do_save_vs_record: ", info)
        self.vs_record_dao.save_vs_record(user_id, target_user_id, info)


    def get_vs_record_list(self, user_id):
        vs_record_list = self.vs_record_dao.get_vs_record_list(user_id)
        debug("get_vs_record_list: ", vs_record_list, type(vs_record_list))
        ret = []
        for uid, v in vs_record_list.iteritems():
            user_info = search_user(uid, None)
            if user_info:
                user_info["vsRecord"] = v["total"]
                user_info["onlineState"] = get_online_state(uid)
                ret.append(user_info)
        return ret

    def check_friend(self,user_id,target_user_id):
        return self.friend_dao.get_friend(user_id,target_user_id)

    def remark_friend(self, userId, targetUserId, remark):
        pass

    def del_friend(self, user_id, target_user_id):
        self.friend_dao.del_friend(user_id,target_user_id)
        del_chat(user_id, target_user_id)

    def setting_demand_record(self, user_id, info):
        self.vs_record_dao.setting_demand_record(user_id, info)

    def get_demand_record(self, user_id):
        return self.vs_record_dao.get_demand_record(user_id)

    def setting_preference_record(self, user_id, info):
        self.vs_record_dao.setting_preference_record(user_id, info)

    def get_preference_record(self, user_id):
        return self.vs_record_dao.get_preference_record(user_id)

    def get_favorite_game(self, user_id, size=3):
        game_record_list = self.vs_record_dao.get_game_record_list(user_id)
        debug("get_favorite_game: ", game_record_list, type(game_record_list))
        games = {}
        for (k, v) in game_record_list.items():
            games[k] = reduce(lambda x, y: x + y, v)
        games_sorted = sorted(zip(games.values(), games.keys()), reverse=True)
        # 默认有total数据
        if len(games_sorted) >= size + 1:
            ret = [int(x[1]) for x in games_sorted[1:1 + size]]
        else:
            _ = [int(x[1]) for x in games_sorted[1:]]
            _2 = random.sample(list(set(MINI_GAMES) - set(_)), size - len(games_sorted) + 1)
            ret = list(set(_).union(set(_2)))
        debug("get_favorite_game: ", ret)
        return ret

    def get_active_user(self, user_id, gender , size):
        if(len(self.active_user_line)) <= size:
            ret = [uid for uid in self.active_user_line]
        else:
            ret = random.sample([uid for uid in self.active_user_line], size)
        debug("get_active_user: ", ret)
        users = []
        for uid in ret:
            user_info = self.search_user(uid,None)
            users.append(user_info)
        debug("get_active_user: ", users)
        return users

