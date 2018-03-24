# -*- coding=utf-8 -*-
"""
@file  : itemaction
@date  : 2016-09-22
@author: GongXiaobo
"""

from freetime5.util import ftstr
from hall5.plugins.hallitem._private._actions import _action
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.plugins.item import items


class TYItemActionSubMemberInfo(_action.HallItemAction):

    TYPE_ID = 'common.subMemberInfo'

    def __init__(self):
        super(TYItemActionSubMemberInfo, self).__init__()

    def _initWhenLoaded(self, itemKind, itemKindMap, assetKindMap):
        if not self.inputParams:
            self.inputParams = {
                'type': 'detail',
                'desc': ''
            }

    def canDo(self, gameId, clientId, userBag, item, timestamp):
        '''
        判断是否可以对item执行本动作
        '''
        status = pluginCross.hallsubmember.loadSubMemberStatus(userBag.userId)
        return status.isSub

    def getInputParams(self, gameId, userBag, item, timestamp):
        ret = ftstr.cloneData(self.inputParams)
        desc = ret.get('desc', '')
        status = pluginCross.hallsubmember.loadSubMemberStatus(userBag.userId)
        unsubDesc = status.unsubDesc or ''
        ret['desc'] = ftstr.replaceParams(desc, {'unsubDesc': unsubDesc})
        return ret

    def doAction(self, gameId, clientId, userAssets, item, timestamp, params):
        return items.ACT_RESULT_OK
