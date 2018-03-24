# -*- coding: utf-8 -*-
"""
Created on 2018年02月02日11:16:10

@author: yzx

对应GH进程, 基本上为 http api 入口
"""
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from sns.plugins.srvhttp._private import _dao
from sns.plugins.srvhttp._private._dao import DaoFollowRedis, DaoFriendRedis, DaoUserVSRecordRedis, DaoVSRecordRedis
from sns.plugins.srvhttp._private._service import SNSService
from tuyoo5.core import typlugin, tyglobal, tychecker
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


def check_phone(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) < 11:
        return None, 'the param %s error' % (name)
    return val, None


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

def check_code(msg, result, name):
    val = msg.getParamInt(name)
    if val > 0:
        return val, None
    return None, 'the %s must large than zero !' % (name)


def check_remark(msg, result, name):
    val = msg.getParamStr(name, '')
    if len(val) > 10 or len(val) == 0:
        return None, 'the param %s error' % (name)
    return val, None

class SNSHttpAction(typlugin.TYPlugin):
    """
    SNS.
    """

    def __init__(self):
        super(SNSHttpAction, self).__init__()
        self.checkBase = tychecker.Checkers(
            check_userId,
            check_targetUserId,
        )
        self.phone_checker = tychecker.Checkers(
            check_phone,
        )
        self.user_checker = tychecker.Checkers(
            check_userId,
        )
        self.target_checker = tychecker.Checkers(
            check_targetUserId,
        )
        self.remark_checker = tychecker.Checkers(
            check_remark,
        )
        self.flag_checker = tychecker.Checkers(
            check_flag,
        )
        self.code_checker = tychecker.Checkers(
            check_code,
        )
        self.service = SNSService()
        debug("SNSHttpAction init")

    def destoryPlugin(self):
        super(SNSHttpAction, self).destoryPlugin()
        _dao.DaoUserFollowRedis.finalize()
        _dao.DaoUserFriendRedis.finalize()
        _dao.DaoUserVSRecordRedis.finalize()
        _dao.DaoUserVSDemandHash.finalize()
        _dao.DaoUserPreferenceHash.finalize()
        _dao.DaoUserGameRecordRedis.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_HTTP])
    def initPluginBefore(self):
        debug("SNSHttpAction initPluginBefore")
        _dao.DaoUserFollowRedis.initialize()
        _dao.DaoUserFriendRedis.initialize()
        _dao.DaoUserVSRecordRedis.initialize()
        _dao.DaoUserVSDemandHash.initialize()
        _dao.DaoUserPreferenceHash.initialize()
        _dao.DaoUserGameRecordRedis.initialize()
        self.service.follow_dao = DaoFollowRedis()
        self.service.friend_dao = DaoFriendRedis()
        self.service.vs_record_dao = DaoVSRecordRedis()

    @typlugin.markPluginEntry(httppath='search_user')
    def do_search_user(self, request):
        """
        检索好友.
        :param request:
        :return:
        """
        # 通过id或者电话号码检索
        user_id = request.getParamInt('userId')
        phone = request.getParamStr('phone')
        debug("SNSHttpAction do_search_user ", user_id, phone)
        user = self.service.search_user(user_id, phone)
        mo = MsgPack()
        if user:
            mo.setResult('ok', 1)
            mo.setResult("data", user)
        else:
            mo.setResult('ok', 0)
            mo.setError(1, "not found user")
        return mo

    @typlugin.markPluginEntry(httppath='follow_launch')
    def do_follow_launch(self, request):
        """
        添加好友.
        :param request:
        :return:
        """
        # 源用户ID->目标用户ID,问候语,来源渠道(检索，群, 游戏...)
        user_id = request.getParamInt('userId')
        target_user_id = request.getParamInt('targetUserId')
        debug("SNSHttpAction do_follow_launch ", user_id, target_user_id)
        mi = self.checkBase.check(request)
        mo = MsgPack()
        if mi.error :
            ftlog.warn('do_follow_launch error', user_id, target_user_id, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error )
        else:
            # 问候语
            hello = request.getParamStr('hello')
            # 搜索添加、游戏互动添加，用于数据分析
            origin = request.getParamStr('origin')
            self.service.do_follow_launch(user_id, target_user_id, hello, origin)
            mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='follow_landfall')
    def do_follow_landfall(self, request):
        """
        处理添加好友请求.
        :param request:
        :return:
        """
        # 消息ID及处理结果(通过/拒绝)
        user_id = request.getParamInt('userId')
        target_user_id = request.getParamInt('targetUserId')
        code = request.getParamInt('code')
        debug("SNSHttpAction do_follow_landfall ", user_id, target_user_id,code)
        mi = self.checkBase.check(request)
        m2 = self.code_checker.check(request)
        mo = MsgPack()
        if mi.error or m2.error:
            ftlog.warn('do_follow_landfall error', request, mi.error, m2.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error if mi.error else m2.error)
        else:
            self.service.do_follow_landfall(user_id, target_user_id, code)
            mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='get_follow_list')
    def get_follow_list(self, request):
        """
        待加好友消息列表.
        :param request:
        :return:
        """
        user_id = request.getParamInt('userId')
        debug("SNSHttpAction get_follow_list ", user_id)
        mi = self.user_checker.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('get_follow_detail error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            follow_list = self.service.get_follow_list(user_id)
            mo = MsgPack()
            mo.setResult('ok', 1)
            mo.setResult("data", follow_list)
        return mo

    @typlugin.markPluginEntry(httppath='get_follow')
    def get_follow_detail(self, request):
        """
        查看某个好友信息.
        :return:
        """
        user_id = request.getParamInt('userId')
        target_user_id = request.getParamInt('targetUserId')
        debug("SNSHttpAction get_follow_detail ", user_id, target_user_id)
        mi = self.checkBase.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('get_follow_detail error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            info = self.service.get_follow_detail(target_user_id)
            mo.setResult('ok', 1)
            mo.setResult("data", info)
        return mo

    @typlugin.markPluginEntry(httppath='get_friend_list')
    def get_friend_list(self, request):
        """
        获取用户好友列表.
        :param request:
        :return:
        """
        debug("get_friends :  request = ", request)
        user_id = request.getParamInt('userId')
        flag = request.getParamInt('flag')
        debug("SNSHttpAction get_friend_list ", user_id, flag)
        mi = self.user_checker.check(request)
        m2 = self.flag_checker.check(request)
        mo = MsgPack()
        if mi.error or m2.error:
            ftlog.warn('get_friend_list error', request, mi.error, m2.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error if mi.error else m2.error)
        else:
            friend_list = self.service.get_friend_list(user_id, flag)
            mo = MsgPack()
            mo.setResult('ok', 1)
            mo.setResult("data", friend_list)
        return mo

    @typlugin.markPluginEntry(httppath='get_friend')
    def get_friend_detail(self, request):
        """
        查看某个好友信息.
        :return:
        """
        user_id = request.getParamInt('userId')
        target_user_id = request.getParamInt('targetUserId')
        debug("SNSHttpAction get_friend_detail ", user_id, target_user_id)
        mi = self.checkBase.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('get_follow_detail error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            info = self.service.get_friend_detail(user_id, target_user_id)
            mo.setResult("data", info)
            mo.setResult('ok', 1)
        return mo


    @typlugin.markPluginEntry(httppath='remark_friend')
    def remark_friend(self, request):
        """
        备注某个好友.
        :return:
        """
        user_id = request.getParamInt('userId')
        target_user_id = request.getParamInt('targetUserId')
        debug("SNSHttpAction get_friend_detail ", user_id, target_user_id)
        remark = request.getParamString('remark')
        mi = self.checkBase.check(request)
        m2 = self.remark_checker.check(request)
        mo = MsgPack()
        if mi.error or m2.error:
            ftlog.warn('get_follow_detail error', request, mi.error,m2.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error if mi.error else m2.error)
        else:
            self.service.remark_friend(user_id, target_user_id, remark)
            mo.setResult('ok', 1)
        return mo


    # @typlugin.markPluginEntry(httppath='save_vs_record')
    # def save_vs_record(self, request):
    #     """
    #     上传匹配的游戏结果。
    #     :param userId:
    #     :param targetId:
    #     :return:
    #     """
    #     # id,昵称，头像，在线状态，性别，对战成绩
    #     user_id = request.getParamInt('userId')
    #     target_user_id = request.getParamInt('targetUserId')
    #     code = request.getParamInt('code')
    #     debug("SNSHttpAction save_vs_record ", user_id, target_user_id, code)
    #     self.service.save_vs_record(user_id, target_user_id, code)
    #     return 1

    @typlugin.markPluginEntry(httppath='get_vs_record_list')
    def get_vs_record_list(self, request):
        """
        获取用户的最近匹配过的人。
        :param userId:
        :param targetId:
        :return:
        """
        # id,昵称，头像，在线状态，性别，对战成绩
        user_id = request.getParamInt('userId')
        debug("SNSHttpAction get_vs_record_list userId:", user_id)
        mi = self.user_checker.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('get_vs_record_list error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            ret = self.service.get_vs_record_list(user_id)
            debug("SNSHttpAction get_vs_record_list userId:", user_id, ret)
            mo.setResult('data', ret)
            mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='check_friend')
    def check_friend(self, request):
        """
        检查2个人是否好友。
        :param userId:
        :param targetId:
        :return:
        """
        user_id = request.getParamInt('userId')
        target_user_id = request.getParamInt('targetUserId')
        debug("SNSHttpAction check_friend ", user_id, target_user_id)
        mi = self.checkBase.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('check_friend error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            ret = self.service.check_friend(user_id,target_user_id)
            if ret:
                ret = 1
            else:
                ret = 0
            mo.setResult("data", ret)
            mo.setResult('ok', 1)
        return mo


    @typlugin.markPluginEntry(httppath='del_friend')
    def do_delete_friend(self, request):
        """
        删除好友.
        :param request:
        :return:
        """
        user_id = request.getParamInt('userId')
        target_user_id = request.getParamInt('targetUserId')
        debug("SNSHttpAction : do_delete_friend : ", user_id, target_user_id)
        mi = self.checkBase.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('do_delete_friend error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            self.service.del_friend(user_id, target_user_id)
            mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='setting_vs_demand')
    def setting_vs_demand(self, request):
        """
        设置匹配偏好.
        TODO 将额外信息统一存储
        :param request:
        :return:
        """
        user_id = request.getParamInt('userId')
        gender = request.getParamStr('gender')
        age = request.getParamStr('age')
        debug("SNSHttpAction : setting_vs_demand : ", user_id, gender, age)
        mi = self.user_checker.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('setting_vs_demand error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            self.service.setting_demand_record(user_id, [gender,age])
            mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='get_vs_demand')
    def get_vs_demand(self, request):
        """
        获取用户的匹配喜好。
        :param request:
        :return:
        """
        # id,昵称，头像，在线状态，性别，对战成绩
        user_id = request.getParamInt('userId')
        debug("SNSHttpAction doGetUserBigGameDemandInfo ", user_id)
        ret = self.service.get_demand_record(user_id)
        debug("SNSHttpAction doGetUserBigGameDemandInfo ", ret)
        return ret

    @typlugin.markPluginEntry(httppath='setting_user_preference')
    def setting_user_preference(self, request):
        """
        玩家额外信息.
        :param request:
        :return:
        """
        debug("setting_user_preference :  request = ", request)
        user_id = request.getParamInt('userId')
        preferences = request.getParamStr('preferences')
        age = request.getParamStr('age')
        motto = request.getParamStr('motto')
        debug("SNSHttpAction : setting_user_preference : ", user_id, preferences, age, motto)
        mi = self.user_checker.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('setting_user_preference error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            # self.service.setting_preference_record(user_id, preferences)
            preferences = {
                "age": age,
                "motto": motto
            }
            self.service.setting_preference_record(user_id, preferences)
            mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='get_favorite_game')
    def get_favorite_game(self, request):
        """
        获取用户常玩的游戏。
        :param request:
        :return:
        """
        # id,昵称，头像，在线状态，性别，对战成绩
        user_id = request.getParamInt('userId')
        size = request.getParamInt('size')
        debug("SNSHttpAction get_favorite_game ", user_id, size)
        mi = self.user_checker.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('get_favorite_game error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            ret = self.service.get_favorite_game(user_id, size)
            mo.setResult("data", ret)
            mo.setResult('ok', 1)
        return mo

    @typlugin.markPluginEntry(httppath='get_active_user')
    def get_active_user(self, request):
        """
        获取活跃的用户。
        :param request:
        :return:
        """
        # id,昵称，头像，在线状态，性别，对战成绩
        user_id = request.getParamInt('userId')
        # 用户性别 0- 女 1-男
        gender = request.getParamInt('gender')
        # size 数量
        size = request.getParamInt('size')
        debug("SNSHttpAction get_active_user ", user_id, gender)
        mi = self.user_checker.check(request)
        mo = MsgPack()
        if mi.error:
            ftlog.warn('get_active_user error', request, mi.error)
            mo.setResult('ok', 0)
            mo.setError(1, mi.error)
        else:
            ret = self.service.get_active_user(user_id, gender, size)
            mo.setResult("data", ret)
            mo.setResult('ok', 1)
        return mo


################################################################

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_HTTP)
    def verify_friend(self, user_id, target_user_id):
        """
        验证2个用户是否好友关系,提供给聊天服务RPC调用。
        :param user_id:
        :param target_user_id:
        :return: 1 是好友 0 不是好友
        """
        debug("SNSHttpAction verify_friend:", user_id, target_user_id)
        if isinstance(user_id, int) and user_id > 0 and isinstance(target_user_id, int) and target_user_id > 0:
            ret = self.service.check_friend(user_id, target_user_id)
            if ret:
                return 1
            else:
                return 0
        else:
            ftlog.warn("SNSHttpAction verify_friend error param", user_id, target_user_id)
            return 0

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_HTTP)
    def upload_vs_record(self, user_id, target_user_id, mini_game_id, win_user_id):
        """
        上传匹配的游戏结果,提供给聊天服务RPC调用。
        :param user_id: 用户1
        :param target_user_id: 用户2
        :param mini_game_id: 游戏ID
        :param win_user_id: 获胜者
        :return: 成功1 失败0
        """
        # id,昵称，头像，在线状态，性别，对战成绩
        debug("SNSHttpAction upload_vs_record ", user_id, target_user_id, mini_game_id, win_user_id)
        if isinstance(user_id, int) and user_id > 0 and isinstance(target_user_id, int) and target_user_id > 0 and \
                isinstance(win_user_id, int):
            self.service.save_vs_record(user_id, target_user_id, mini_game_id,  win_user_id)
            return 1
        else:
            ftlog.warn("SNSHttpAction verify_friend error param", user_id, target_user_id, mini_game_id, win_user_id)
            return 0


    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_GAME_HTTP)
    def doGetUserBigGameDemandInfo(self, user_id):
        """
        获取用户的匹配喜好,由对战匹配服调用。
        :param user_id:
        :return:
        """
        # id,昵称，头像，在线状态，性别，对战成绩
        debug("SNSHttpAction doGetUserBigGameDemandInfo ", user_id)
        ret = self.service.get_demand_record(user_id)
        debug("SNSHttpAction doGetUserBigGameDemandInfo ", ret)
        if not ret:
            # 默认随机
            ret =["rand","rand"]
        return ret

################################################################

    @typlugin.markPluginEntry(httppath='ban')
    def do_ban(self, request):
        """
        屏蔽某用户.
        :param request:
        :return:
        """
        debug("SNSHttpAction : do_ban : request = ", request)
        pass



    @typlugin.markPluginEntry(httppath='test_chat')
    def test_chat(self, request):
        """
        测试聊天.
        :param request:
        :return:
        """
        return 'chat send ok'

    @typlugin.markPluginEntry(httppath='test_chat2')
    def test_chat2(self, request):
        """
        测试聊天.
        :param request:
        :return:
        """
        rpcproxy = getRpcProxy(9993, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
        rfc = rpcproxy.srvutil.doSomething(10001, "hello,by test_http_chat2")
        result = rfc.getResult()
        debug("test_chat2", result)
        return 'chat send ok2'

    @typlugin.markPluginEntry(httppath='test_upload_vs_record')
    def test_upload_vs_record(self, request):
        """
        测试聊天.
        :param request:
        :return:
        """
        debug("SNSHttpAction test_upload_vs_record ", request)
        user_id = request.getParamInt('userId')
        target_user_id = request.getParamInt('targetUserId')
        mini_game_id = request.getParamInt('miniGameId')
        win_user_id = request.getParamInt('winUserId')
        self.upload_vs_record(user_id, target_user_id, mini_game_id, win_user_id)
        return 'chat send ok'
