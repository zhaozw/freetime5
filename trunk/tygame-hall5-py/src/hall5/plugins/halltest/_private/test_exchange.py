# -*- coding=utf-8 -*-
"""
@file  : test
@date  : 2016-11-10
@author: GongXiaobo
"""

from freetime5.twisted import fthttp
from freetime5.util import ftstr
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.entity import hallconf
from hall5.plugins.halltest._private import _checker
from tuyoo5.core import tychecker
from tuyoo5.core import tyglobal
from tuyoo5.core.typlugin import hallRpcOne
from tuyoo5.game import tysessiondata


class HallPluginTestExchange(object):

    def __init__(self):
        self.checkExchange = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_exchangeId,
            _checker.check_itemId,
            hallchecker.check__checkUserData
        )

    def doExchangeTest(self, request):
        action = request.getParamStr('action')
        if action == 'query':
            return self.doExchangeQuery(request)
        if action == 'EXCHANGE':
            return self.doExchangeExchange(request)
        if action == 'jdaddress':
            return self.doExchangeAddrList(request)

        if action == 'AUDIT_ACCEPT':
            return self.doAudit(request, 3)
        if action == 'AUDIT_REJECT_FAIL':
            return self.doAudit(request, 1)
        if action == 'AUDIT_REJECT_RETURN_FAIL':
            return self.doAudit(request, 2)

        if action == 'SHIPPING_SUCC_FAIL':
            return self.doShipping(request, 0)
        if action == 'SHIPPING_ERR_FAIL':
            return self.doShipping(request, 4)
        if action == 'SHIPPING_ERR_FAIL_RETURN':
            return self.doShipping(request, 5)

        if action == 'delete':
            return self.doDelete(request)

        return 'params action error'

    def doExchangeQuery(self, request):
        mo = MsgPack()
        mi = self.checkExchange.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            clientId = tysessiondata.getClientId(mi.userId)
            datas = hallRpcOne.hallexchange._doExchangeQueryUi(mi.userId, clientId).getResult()
            mo.updateResult(datas)
        return mo

    def doExchangeAddrList(self, request):
        userId = request.getParamInt('userId')
        proviceId = request.getParamStr('proviceId')
        cityId = request.getParamStr('cityId')
        countyId = request.getParamStr('countyId')
        mo = MsgPack()
        try:
            address = hallRpcOne.hallexchange._doGetJdAddressList(userId,
                                                                  proviceId,
                                                                  cityId,
                                                                  countyId).getResult()
            mo.setResult('address', address)
        except Exception, e:
            mo.setError(1, str(e))
        return mo

    def doExchangeExchange(self, request):
        mo = MsgPack()
        mi = self.checkExchange.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            clientId = tysessiondata.getClientId(mi.userId)
            msg = MsgPack()
            msg.setKey('apiVersion', 5.0)
            msg.setCmdAction('exchange5', 'exchange')
            msg.setParam('phone', request.getParamStr('phone'))
            msg.setParam('uName', request.getParamStr('uName'))
            msg.setParam('uAddres', request.getParamStr('uAddres'))
            msg.setParam('gameId', tyglobal.gameId())
            msg.setParam('itemId', mi.itemId)
            msg.setParam('userId', mi.userId)
            msg.setParam('extabName', request.getParamStr('extabName'))
            msg.setParam('clientId', clientId)
            msg.setParam('wxappid', hallconf.getWeiXinAppId(mi.userId, clientId))
            msg.setParam('proviceId', request.getParamStr('proviceId'))
            msg.setParam('cityId', request.getParamStr('cityId'))
            msg.setParam('countyId', request.getParamStr('countyId'))
            msg.setParam('townId', request.getParamStr('townId'))
            msg.setParam('proviceName', request.getParamStr('proviceName'))
            msg.setParam('cityName', request.getParamStr('cityName'))
            msg.setParam('countyName', request.getParamStr('countyName'))
            msg.setParam('townName', request.getParamStr('townName'))
            msg = msg.getDict()
            try:
                ret = hallRpcOne.hallexchange.doExchangeRequest(mi.userId, msg)
                datas = ret.getResult()
                if datas:
                    exchangeId, errMsg = datas[0], datas[1]
                    if exchangeId:
                        mo.setResult('exchangeId', exchangeId)
                        mo.setResult('info', errMsg)
                    else:
                        mo.setError(1, errMsg)
                else:
                    mo.setError(1, 'doExchangeRequest return is None')
            except Exception, e:
                mo.setError(1, str(e))
        return mo

    def doAudit(self, request, result):
        mo = MsgPack()
        mi = self.checkExchange.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            params = {
                'userId': mi.userId,
                'result': result,
                'realGameId': tyglobal.gameId(),
                'exchangeId': mi.exchangeId,
                'extOrderId': 'dummy_jd_num_audit',
                '_test_': 1,
            }
            url = tyglobal.httpGame() + '/api/hall5/exchange/auditCallback?' + ftstr.toHttpStr(params)
            _, ret = fthttp.queryHttp('GET', url, None, None, 5)
            if ret and ret[0] == '{':
                mo.updateResult(ftstr.loads(ret))
            else:
                mo.setError(1, ret)
        return mo

    def doShipping(self, request, result):
        mo = MsgPack()
        mi = self.checkExchange.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            params = {
                'userId': mi.userId,
                'result': result,
                'realGameId': tyglobal.gameId(),
                'exchangeId': mi.exchangeId,
                'extOrderId': 'dummy_jd_num_shipping',
                '_test_': 1,
            }
            url = tyglobal.httpGame() + '/api/hall5/exchange/shippingCallback?' + ftstr.toHttpStr(params)
            _, ret = fthttp.queryHttp('GET', url, None, None, 5)
            if ret and ret[0] == '{':
                mo.updateResult(ftstr.loads(ret))
            else:
                mo.setError(1, ret)
        return mo

    def doDelete(self, request):
        mo = MsgPack()
        mi = self.checkExchange.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            try:
                hallRpcOne.hallexchange._doDelete(mi.userId, mi.exchangeId).getResult()
                mo.setResult('ok', 1)
            except Exception, e:
                mo.setError(1, str(e))
        return mo
