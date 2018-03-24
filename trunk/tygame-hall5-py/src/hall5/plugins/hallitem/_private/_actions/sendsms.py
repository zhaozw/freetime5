# -*- coding=utf-8 -*-
"""
@file  : itemaction
@date  : 2016-09-22
@author: GongXiaobo
"""

from hall5.plugins.hallitem._private._actions import _action
from hall5.plugins.hallitem._private.itemdao import DaoMixExCodeList
from tuyoo5.core import tyrpcsdk
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import UserKeys
from tuyoo5.plugins.item import items


class TYItemActionSendMsg(_action.HallItemAction):

    TYPE_ID = 'common.sendMsg'

    def __init__(self):
        super(TYItemActionSendMsg, self).__init__()

    def canDo(self, gameId, clientId, userBag, item, timestamp):
        return not item.isDied(timestamp)

    def doAction(self, gameId, clientId, userAssets, item, timestamp, params):

        if item.isDied(timestamp):
            return items.TYItemActionResult(None, None, -30, '道具已经过期', None)

        # 手机号码的处理
        useBindPhone = params.get('bindPhone', 0)
        if not useBindPhone:
            # 如果没有bindPhone，则需要检查phoneNumber
            phoneNumber = params.get('phoneNumber')
            if not phoneNumber:
                return items.TYItemActionResult(None, None, -31, '请输入手机号码', None)
        else:
            # 获取绑定的手机号
            phoneNumber = pluginCross.halldata.getUserDataList(userAssets.userId, UserKeys.ATT_BIND_MOBILE)
            if not phoneNumber:
                return items.TYItemActionResult(None, None, -32, '您绑定的手机号状态有误，请联系客服电话4008098000', None)

        # 获取库存
        exCode = DaoMixExCodeList.getFreeExCode(userAssets.userId, item.kindId, phoneNumber, timestamp)
        if not exCode:
            return items.TYItemActionResult(None, None, -33, '非常抱歉的通知您，兑换码已无库存，请联系客服电话4008098000', None)

        # 短信发送
        replaceParams = {'item': item.itemKind.displayName}
        mail, message, _ = _action._buildMailAndMessageAndChanged(gameId, userAssets, self, None, replaceParams)
        content = mail + exCode + message
        code = tyrpcsdk.sendSmsToUser(userAssets.userId, content, phoneNumber)
        if code == 0:
            # 消耗item
            userBag = userAssets.getUserBag()
            userBag.removeItem(gameId, item, timestamp, 'ITEM_USE', 0)
            return items.ACT_RESULT_OK
        else:
            # 将消息下发到用户的消息列表中
            # pluginCross.hallmessage.sendMessageSystem(userAssets.userId, gameId, sendToMsg, None, None)
            return items.TYItemActionResult(None, None, -34, '非常抱歉，短信发送失败，请联系客服电话4008098000', None)
