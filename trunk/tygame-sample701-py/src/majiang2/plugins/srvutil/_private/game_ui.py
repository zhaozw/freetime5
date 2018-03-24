# -*- coding=utf-8 -*-
'''
Created on 2015年9月28日

@author: liaoxx
'''


from freetime5.util.ftmsg import MsgPack
from majiang2.entity import room_list
from tuyoo5.core import tyrpcconn


def doRoomList(userId, gameId, playMode):
    # 金币卓
    room_infos = room_list.fetchAllRoomInfos(userId, gameId, playMode)
    # 比赛
    match_infos = room_list.fetchAllMatchInfos(userId, gameId, playMode)

    mo = MsgPack()
    mo.setCmd('room_list')
    mo.setResult('gameId', gameId)
    mo.setResult('baseUrl', 'http://www.tuyoo.com/')
    mo.setResult('play_mode', playMode)
    mo.setResult('rooms', room_infos)
    mo.setResult('match', match_infos)
    mo.setResult('friend', [])
    tyrpcconn.sendToUser(userId, mo)
