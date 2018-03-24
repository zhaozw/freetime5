# -*- coding: utf-8 -*-
'''
Created on 2016年5月1日

@author: zqh
'''

from freetime5.twisted import ftcore
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tyrpcconn


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

_NOTIFY_MAP = {
    'diamond': ['udata'],
    'udata': ['udata'],
    'item': ['item'],
    'chip': ['gdata'],
    'coupon': ['gdata'],
    'gdata': ['gdata'],
    'vip': ['gdata'],
    'charm': ['gdata'],
    'redpoint5': ['redpoint5'],
}

_NOTIFYS = {}  # userId<->{gameId<->{changeName1,changeName2,...}}


def _flushDataChangeNotify():
    global _NOTIFYS
    notifys = _NOTIFYS
    _NOTIFYS = {}
    if _DEBUG:
        debug('_flushDataChangeNotify size=', len(notifys))

    count = 0
    msg = MsgPack()
    msg.setCmd('update_notify5')
    for userId, datas in notifys.iteritems():
        count += 1
        if count % 20 == 0:  # 每20个休息一次，避免长时间占据CPU
            ftcore.sleep(0.01)
        msg.setResult('userId', userId)
        for gameId, changes in datas.iteritems():
            msg.setResult('gameId', gameId)
            msg.setResult('changes', list(changes))
            tyrpcconn.sendToUser(userId, msg)


def _sendDataChangeNotify(userId, gameId, changedList):
    """
    此方法记录变化的信息，合并至缓存
    后续由持续心跳方法（当前2秒一次）发送缓存内容
    """
    if _DEBUG:
        debug('_sendDataChangeNotify gameId=', gameId, 'userId=', userId, 'changedList=', changedList)

    if not isinstance(gameId, int) or gameId <= 0:
        return

    if not isinstance(userId, int) or userId <= 0:
        return

    if isinstance(changedList, (str, unicode)) and len(changedList) > 0:
        changedList = [changedList]
    elif isinstance(changedList, (list, tuple, set)) and len(changedList) > 0:
        pass
    else:
        return

    udatas = _NOTIFYS.get(userId)
    if udatas is None:
        udatas = {}
        _NOTIFYS[userId] = udatas

    gdatas = udatas.get(gameId)
    if gdatas is None:
        gdatas = set()
        udatas[gameId] = gdatas

    for name in changedList:
        if name in _NOTIFY_MAP:
            gdatas.update(_NOTIFY_MAP[name])
        else:
            gdatas.add(name)
