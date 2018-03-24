# -*- coding=utf-8 -*-
'''
Created on 2015年9月28日

@author: liaoxx
'''


import time
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tyrpcconn
from majiang2.entity import room_list


class HallTcpHandler(object):

    def __init__(self):
        pass

    def doRoomList(self, userId, gameId, msg):
        message = MsgPack()
        message.setCmd('room_list')
        message.setResult('gameId', gameId)
        message.setResult('baseUrl', 'http://www.tuyoo.com/')
        playMode = msg.getParam('play_mode', None)
        if not playMode:
            message.setError(1, 'no param play_mode!!!')
            tyrpcconn.sendToUser(userId, message)
            return

        message.setResult('play_mode', playMode)
        # 金币卓
        room_infos = room_list.fetchAllRoomInfos(userId, gameId, playMode)
        message.setResult('rooms', room_infos)
        # 朋友桌
        message.setResult('friend', [])
        # 比赛
        match_infos = room_list.fetchAllMatchInfos(userId, gameId, playMode)
        message.setResult('match', match_infos)
        tyrpcconn.sendToUser(userId, message)

    def curTimestemp(self, gameId, userId):
        msg = MsgPack()
        msg.setCmd('user')
        msg.setResult('action', 'mj_timestamp')
        msg.setResult('gameId', gameId)
        msg.setResult('userId', userId)
        current_ts = int(time.time())
        msg.setResult('current_ts', current_ts)
        tyrpcconn.sendToUser(userId, msg)

    def getVipTableList(self, userId, clientId):
        """ 客户端获取 <vip桌子列表>
        """
        pass

    def getVipTableListUpdate(self, userId, clientId):
        """ 客户端获取 <vip桌子列表变化信息>
        """
        pass

    def getUserInfoSimple(self, userId, gameId, roomId0, tableId0, clientId):
        """ 客户端获取vip桌子上，玩家简单个人信息
        """
        pass

    def getRichManList(self, userId, gameId, clientId):
        """ 客户端请求 <土豪列表>
        """
        pass

    def getConponExchangeInfos(self, userId, gameId, clientId):
        """ 麻将大厅主界面 <实物兑换>
        """
        pass

    def getSaleChargeInfos(self, userId, gameId, clientId):
        """ 麻将大厅主界面 <特惠充值>
        """
        pass

    def getCumulateChargeInfos(self, gameId, userId, clientId):
        """ 麻将大厅主界面 <累计充值>
        """
        pass

    def openCumulateChargeBox(self, gameId, userId, clientId):
        """ 客户端打开累计充值宝箱
        """
        pass
