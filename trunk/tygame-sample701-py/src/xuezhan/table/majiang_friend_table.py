# -*- coding=utf-8 -*-
'''
Created on 2015年9月30日
麻将好友桌的牌桌，负责好友桌号的管理和好友桌赛制的调度。
@author: 赵良
'''
from majiang2.table.majiang_friend_table import MajiangFriendTable
from xuezhan.table.majiang_table_observer import XueZhanTableObserver

class XueZhanMajiangFriendTable(MajiangFriendTable):

    def __init__(self, tableId, room):
        super(XueZhanMajiangFriendTable, self).__init__(tableId, room)
        observer = XueZhanTableObserver(self.gameId, self.roomId, self.tableId)
        observer.setBigRoomId(self.bigRoomId)
        self.setTableObserver(observer)
