# -*- coding: utf-8 -*-
"""
Created on 2018年02月05日11:10:06
一些工具函数
@author: yzx
"""
import time
from datetime import datetime

# 毫秒级时间戳
from freetime5.util import fttime

current_milli_time = lambda: int(round(time.time() * 1000))

# 消息ID生成器 UID1-UID2-毫秒时间戳 （小号在前）
get_msg_id = lambda uid,tid,now: '%s-%s-%s' % (tid,uid,now) if uid > tid \
    else '%s-%s-%s' % (uid,tid,now)

# 临时会话通道 UID1-UID2 （小号在前）
def _get_channel_key(user_id, target_user_id):
    channel_key = "|".join(str(x) for x in sorted([user_id, target_user_id]))
    return channel_key

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