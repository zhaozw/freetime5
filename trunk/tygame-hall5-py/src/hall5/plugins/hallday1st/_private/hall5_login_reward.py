# -*- coding: utf-8 -*-
'''
Created on 2017-9-6
@author: lx
'''

from freetime5.util import ftlog
from tuyoo5.core import tyglobal
from tuyoo5.plugins.item import itemsys
from freetime5.util import fttime
from tuyoo5.core.typlugin import pluginCross

_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


def sendLoginReward(HallPluginDay1st, userId, gameId, clientId):
    # _DB_KEY_GAME_TEMPLATE_GCSC = 'game5:%s:%s:tc'  # 各个游戏的业务模板数据，由console进行自动生成
    # confKey = _DB_KEY_GAME_TEMPLATE_GCSC % (gameId, 'loginreward')
    # conf = _config3._getCacheGameData(confKey, None, None, None)
    conf = HallPluginDay1st.configLoginreward.getTcConfig()
    debug('hall_login_reward.sendLoginReward userId:', userId
        , ' gameId:', gameId
        , ' clientId:', clientId
        , ' conf : ', conf)
    supplement = conf.get('supplement', None)
    if supplement!=None:
        changed = []
        userAssets = itemsys.itemSystem.loadUserAssets(userId)
        items=supplement["items"]
        for item in items:
            maxCount=item["count"]
            itemId=item["itemId"]
            balance=userAssets.balance(itemId, fttime.getCurrentTimestamp())
            if (maxCount-balance)>0:

                assetKind, _addCount, _final = userAssets.addAsset(gameId, itemId, maxCount-balance, fttime.getCurrentTimestamp(),
                                                                       'LOGIN_REWARD', 0)
                if assetKind.keyForChangeNotify:
                    changed.append(assetKind.keyForChangeNotify)

        pluginCross.halldatanotify.sendDataChangeNotify(userId, tyglobal.gameId(), changed)
