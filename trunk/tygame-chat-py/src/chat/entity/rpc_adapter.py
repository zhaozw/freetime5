# -*- coding: utf-8 -*-
"""
Created on 2018年02月05日11:10:06
对其它服务的依赖
@author: yzx
"""


from freetime5.util import ftlog
from tuyoo5.core import tyrpcsdk
from tuyoo5.core.typlugin import RPC_CALL_SAFE, pluginCross
from tuyoo5.core.typlugin import RPC_TARGET_MOD_ONE
from tuyoo5.core.typlugin import getRpcProxy
from tuyoo5.core.tyrpchall import UserKeys

from chat.entity.utils import format_author_time

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

_UserBaseAttrs = ','.join(
    [UserKeys.ATT_NAME, UserKeys.ATT_PURL, UserKeys.ATT_SEX, UserKeys.ATT_ADDRESS, UserKeys.ATT_CITY_CODE,
     UserKeys.ATT_LAST_AUTHOR_TIME,UserKeys.ATT_AUTHOT_TIME])

SNS_GAME_ID = 9992



def search_user(userId, phone=None):
    if userId:
        return _search_user_by_id(userId)
    if phone:
        return _search_user_by_phone(phone)
    return None


def _search_user_by_id(userId):
    user_info = tyrpcsdk.getUserDatas(userId, _UserBaseAttrs)
    debug("tyrpcsdk.getUserDatas ", userId, user_info)
    name = user_info.get('name', "")
    if name:
        user_info["userId"] = userId
        user_info["authorTime"] = format_author_time(user_info.get('authorTime', ""))
        user_info["lastAuthorTime"] = format_author_time(user_info.get('lastAuthorTime', ""))
        return user_info
    else:
        return None

def get_user_last_time(user_id):
    user_info = _search_user_by_id(user_id)
    if user_info:
        return user_info.get('authorTime', ""),user_info.get('lastAuthorTime', "")
    return 0,0


def get_online_state(user_id):
    return  pluginCross.onlinedata.getOnLineState(user_id)

def _search_user_by_phone(phone):
    tyrpcsdk.getUserDatas(phone, ["userId", "nickName"])
    return None

def push_game_message(user_id, target_user_id, msg_id, record):
    pluginCross.srvchat.game_result_message(user_id, target_user_id, msg_id, record.getDict())

def _check_friend(user_id,target_user_id):
    debug("SNSService _check_friend RPC ", user_id, target_user_id)
    rpcproxy = getRpcProxy(SNS_GAME_ID, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
    rfc = rpcproxy.srvhttp.verify_friend(user_id,target_user_id)
    ret = rfc.getResult()
    debug("SNSService _check_friend RPC ", ret)
    return ret

def _upload_vs_record(user_id,target_user_id,mini_game_id, win_user_id):
    debug("SNSService _upload_vs_record RPC ", user_id, target_user_id, mini_game_id, win_user_id)
    rpcproxy = getRpcProxy(SNS_GAME_ID, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
    rfc = rpcproxy.srvhttp.upload_vs_record(user_id,target_user_id, mini_game_id, win_user_id)
    ret = rfc.getResult()
    debug("SNSService _upload_vs_record RPC ", ret)
    return ret