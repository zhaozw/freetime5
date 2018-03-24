# -*- coding: utf-8 -*-
"""
Created on 2018年03月16日11:04:10
@author: yzx
"""
import json

from freetime5.util import fttime, ftstr

import time
from datetime import datetime

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

def test2():
    tstring = "2018-03-16 14:36:43.636448"
    print tstring
    td = fttime.parseTimeMs(tstring)
    print td
    print fttime.datetime2TimestampFloat(td)
    print fttime.getCurrentTimestamp()

    print datetime_to_timestamp(strtime_to_datetime(tstring))

def test1():
    from chat.entity.models import ChatMessage

    msg = ChatMessage(10000,10001,0,123,'{"text":"hello"}')
    print msg
    print msg.pack()

    from chat.entity.models import GameChatMessage
    msg2 = GameChatMessage(10000, 10001, 0, 123, '{"miniGameId":601,"code":"invite"}')
    print msg2
    print msg2.pack()
    info = {
        "time": 111,
        "userId": 10000,
        "targetUserId": 10001,
        "msgType": 2,
        "content": '{"miniGameId":"6033","code":"invite"}'
    }
    msg3 = GameChatMessage.load_info(info)
    print msg3.pack()
    msg3.code = "accept"
    print msg3.code
    print msg3.pack()
    if isinstance(msg3, dict):
        print "msg3 is dict"
    rec = msg3.pack()
    print rec
    msg4 = GameChatMessage.load_info(json.loads(rec))
    msg4 = GameChatMessage.load_info(ftstr.loads(rec))
    print msg4.pack()


if __name__ == '__main__':
    test1()