# -*- coding: utf-8 -*-
"""
Created on 2018年02月05日11:10:06

@author: yzx
"""

from freetime5.util import ftlog
from tuyoo5.core import tyrpcsdk
from tuyoo5.core.tyrpchall import UserKeys
from tuyoo5.core.typlugin import RPC_CALL_SAFE, pluginCross
from tuyoo5.core.typlugin import RPC_TARGET_MOD_ONE
from tuyoo5.core.typlugin import getRpcProxy
import time
from datetime import datetime

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

_UserBaseAttrs = ','.join(
    [UserKeys.ATT_NAME, UserKeys.ATT_PURL, UserKeys.ATT_SEX, UserKeys.ATT_ADDRESS, UserKeys.ATT_CITY_CODE,UserKeys.ATT_LAST_AUTHOR_TIME,UserKeys.ATT_AUTHOT_TIME])

CHAT_GAME_ID = 9993


def strtime_to_datetime(timestr):
    """将字符串格式的时间 (含毫秒) 转为 datetiem 格式
    :param timestr: {str}'2016-02-25 20:21:04.242'
    :return: {datetime}2016-02-25 20:21:04.242000
    """
    local_datetime = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")
    return local_datetime

def datetime_to_timestamp(datetime_obj):
    """将本地(local) datetime 格式的时间 (含毫秒) 转为毫秒时间戳
    :param datetime_obj: {datetime}2016-02-25 20:21:04.242000
    :return: 13 位的毫秒时间戳  1456402864242
    """
    local_timestamp = long(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)
    return local_timestamp

def format_author_time(time_str):
    if time_str:
        return datetime_to_timestamp(strtime_to_datetime(time_str))
    else:
        return 0

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


def _search_user_by_phone(phone):
    tyrpcsdk.getUserDatas(phone, ["userId", "nickName"])
    return None


def del_chat(user_id, target_user_id):
    debug("ChatService _del_chat RPC ", user_id, target_user_id)
    rpcproxy = getRpcProxy(CHAT_GAME_ID, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
    rfc = rpcproxy.srvutil.doDelChat(user_id,target_user_id)
    ret = rfc.getResult()
    debug("ChatService _del_chat RPC ", ret)
    return ret

def system_chat(user_id, target_user_id, code):
    debug("ChatService _system_chat RPC ", user_id, target_user_id,code)
    rpcproxy = getRpcProxy(CHAT_GAME_ID, RPC_CALL_SAFE, RPC_TARGET_MOD_ONE)
    rfc = rpcproxy.srvchat.sns_system_message(user_id,target_user_id,code)
    ret = rfc.getResult()
    debug("ChatService _system_chat RPC ", ret)
    return ret

def get_online_state(user_id):
    return  pluginCross.onlinedata.getOnLineState(user_id)