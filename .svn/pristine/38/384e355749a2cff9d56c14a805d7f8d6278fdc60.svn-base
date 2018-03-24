# -*- coding=utf-8 -*-
'''
Created on 2017年7月13日

@author: zqh
'''

from hall5.plugins.hallitem._private._actions.exchange import TYItemActionExchange
from tuyoo5.plugins.item.itemexceptions import TYItemConfException


class TYItemActionWeixinRedEnvelopOpen(TYItemActionExchange):

    TYPE_ID = 'common.weixin.redEnvelop.open'

    def __init__(self):
        super(TYItemActionWeixinRedEnvelopOpen, self).__init__()
        self.auditParams = None

    def _decodeFromDictImpl(self, d):
        amount = d.get('amount')
        if not isinstance(amount, int) or amount <= 0:
            raise TYItemConfException(d, 'TYItemActionWeixinRedEnvelopOpen.amount must be int > 0')
        self.auditParams = {
            "count": amount,
            "desc": "微信红包",
            "type": 5
        }
        if not self.message:
            self.message = "您的兑换申请已发送，请耐心等待，审核通过后将为您兑换。"
        return self
