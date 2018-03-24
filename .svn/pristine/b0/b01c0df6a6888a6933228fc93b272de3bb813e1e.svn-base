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
from hall5.plugins.halltest._private import _checker
from tuyoo5.core import tychecker
from tuyoo5.core import tyglobal
from tuyoo5.core.typlugin import hallRpcOne
from tuyoo5.game import tysessiondata


class HallPluginTestStore(object):

    def __init__(self):
        self.checkStoreUser = tychecker.Checkers(
            tychecker.check_userId,
            hallchecker.check__checkUserData
        )
        self.checkStoreBuy = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_productId,
            _checker.check_buyType,
            _checker.check_count,
            hallchecker.check__checkUserData
        )
        self.checkStoreAction = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_productId,
            _checker.check_buyType,
            _checker.check_price,
            _checker.check_orderId,
            _checker.check_prodRmd,
            _checker.check_prodDiamond,
            _checker.check_count,
            hallchecker.check__checkUserData
        )
        self.checkStoreActionTerm = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_productId,
            _checker.check_orderId,
            hallchecker.check__checkUserData
        )
        self.checkStoreActionDel = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_orderId,
            hallchecker.check__checkUserData
        )

    def doStoreTest(self, request):
        action = request.getParamStr('action')
        if action == 'query':
            return self.doStoreQuery(request)
        if action == 'buy':
            return self.doStoreBuy(request)
        if action == 'success':
            return self.doStoreSuccess(request)
        if action == 'fail':
            return self.doStoreFail(request)
        if action == 'cancel':
            return self.doStoreCancel(request)
        if action == 'delete':
            return self.doStoreDelete(request)
        return 'params action error'

    def doStoreQuery(self, request):
        mo = MsgPack()
        mi = self.checkStoreUser.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            clientId = tysessiondata.getClientId(mi.userId)
            datas = hallRpcOne.hallstore._doStoreQueryUi(mi.userId, clientId).getResult()
            mo.updateResult(datas)
        return mo

    def doStoreBuy(self, request):
        mo = MsgPack()
        mi = self.checkStoreBuy.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            clientId = tysessiondata.getClientId(mi.userId)
            orderId = ftstr.uuid()
            params = {'appId': tyglobal.gameId(),
                      'realGameId': tyglobal.gameId(),
                      'clientId': clientId,
                      'userId': mi.userId,
                      'prodId': mi.productId,
                      'prodCount': mi.count,
                      'prodOrderId': orderId,
                      '_test_': 1,
                      }
            url = tyglobal.httpGame() + '/api/hall5/store/consume/transaction?' + ftstr.toHttpStr(params)
            _, ret = fthttp.queryHttp('GET', url, None, None, 5)
            if ret != 'ok':
                mo.setError(1, ret)
            else:
                mo.setResult('ok', 1)
        return mo

    def doStoreSuccess(self, request):
        mo = MsgPack()
        mi = self.checkStoreAction.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            clientId = tysessiondata.getClientId(mi.userId)
            if mi.buyType == '1':  # 钻石
                chargedRmbs = 0
                chargedDiamonds = 0
                consumeCoin = mi.price
            else:
                chargedRmbs = mi.price
                chargedDiamonds = mi.count * mi.prodDiamond
                consumeCoin = 0

            params = {'userId': mi.userId,
                      'appId': tyglobal.gameId(),
                      'realGameId': tyglobal.gameId(),
                      'clientId': clientId,
                      'prodOrderId': mi.orderId,
                      'prodId': mi.productId,
                      'prodCount': 1,
                      'chargeType': 'tester',
                      'chargedRmbs': chargedRmbs,
                      'chargedDiamonds': chargedDiamonds,
                      'consumeCoin': consumeCoin,
                      '_test_': 1,
                      }
            url = tyglobal.httpGame() + '/api/hall5/store/consume/delivery?' + ftstr.toHttpStr(params)
            _, ret = fthttp.queryHttp('GET', url, None, None, 5)
            if ret != 'success':
                mo.setError(1, ret)
            else:
                mo.setResult('ok', 1)

            if chargedRmbs > 0 or chargedDiamonds > 0:
                params = {'appId': tyglobal.gameId(),
                          'clientId': clientId,
                          'userId': mi.userId,
                          'realGameId': tyglobal.gameId(),
                          'prodId': mi.productId,
                          'chargedRmbs': chargedRmbs,
                          'chargedDiamonds': chargedDiamonds,
                          '_test_': 1,
                          }
                url = tyglobal.httpGame() + '/api/hall5/store/consume/notify?' + ftstr.toHttpStr(params)
                ret = fthttp.queryHttp('GET', url, None, None, 5)

        return mo

    def doStoreFail(self, request):
        mo = MsgPack()
        mi = self.checkStoreActionTerm.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            params = {'userId': mi.userId,
                      'appId': tyglobal.gameId(),
                      'realGameId': tyglobal.gameId(),
                      'errinfo': 'test error',
                      'prodOrderId': mi.orderId,
                      'prodId': mi.productId,
                      '_test_': 1,
                      }
            url = tyglobal.httpGame() + '/api/hall5/store/pay/fail?' + ftstr.toHttpStr(params)
            _, ret = fthttp.queryHttp('GET', url, None, None, 5)
            if ret != 'success':
                mo.setError(1, ret)
            else:
                mo.setResult('ok', 1)

        return mo

    def doStoreCancel(self, request):
        mo = MsgPack()
        mi = self.checkStoreActionTerm.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            params = {'userId': mi.userId,
                      'appId': tyglobal.gameId(),
                      'realGameId': tyglobal.gameId(),
                      'errinfo': 'test error',
                      'prodOrderId': mi.orderId,
                      'prodId': mi.productId,
                      '_test_': 1,
                      }
            url = tyglobal.httpGame() + '/api/hall5/store/pay/cancel?' + ftstr.toHttpStr(params)
            _, ret = fthttp.queryHttp('GET', url, None, None, 5)
            if ret != 'success':
                mo.setError(1, ret)
            else:
                mo.setResult('ok', 1)

        return mo

    def doStoreDelete(self, request):
        mo = MsgPack()
        mi = self.checkStoreActionDel.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            ret = hallRpcOne.hallstore._doDelete(mi.userId,
                                                 mi.orderId).getResult()
            if ret == 'ok':
                mo.setResult('ok', 1)
            else:
                mo.setError(1, ret)

        return mo
