# -*- coding: utf-8 -*-
"""
Created on 2017年10月23日10:31:44

@author: yzx
"""
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from hall5.plugins.hallmatch._private import _dao
from tuyoo5.core import tyrpcconn



_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass

def _sendMatchDataResponse(userId, gameId, intClientId, apiVersion):
    """
    仅发送match_data命令, USER的我的比赛数据至客户端
    """
    mo = MsgPack()
    mo.setCmd('match_data5')
    mo.setResult('action', 'list')
    mo.setKey('apiVersion', apiVersion)
    mo.setResult('intClientId', intClientId)
    mo.setResult('gameId', gameId)
    mo.setResult('userId', userId)
    match_history_list = _dao.loadHistoryRecord(userId)
    match_sigin_list = _dao.loadSiginRecord(userId)
    if _DEBUG:
        if len(match_history_list) == 0 :
            match_history_list = [
                {
                    "gameId": 6,
                    "roomList": [6666, 6888]
                },
                {
                    "gameId": 701,
                    "roomList": [701230,701250]
                }
            ]
        debug('_sendMatchDataResponse OUT match_history_list=', match_history_list, 'match_sigin_list=',
              match_sigin_list)
    mock_match_list = {
        "historyList": match_history_list,
        "signinList": match_sigin_list
    }
    mo.setResult('matchData', mock_match_list)
    if _DEBUG:
        debug('_sendMatchDataResponse OUT userId=', userId, 'Msg=', mo)

    tyrpcconn.sendToUser(userId, mo)
