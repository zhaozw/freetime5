# -*- coding=utf-8 -*-

'''
玩家调起三方支付有两种情况
1. 只购买钻石
   /api/hall5/store/consume/transaction
   /api/hall5/store/charge/notify
2. 购买钻石后兑换商品(含金币)
    /api/hall5/store/consume/transaction
    /api/hall5/store/consume/delivery
    /api/hall5/store/charge/notify

玩家购买商品有两种情况
1. 直接通过钻石兑换商品(含金币)
   /api/hall5/store/consume/transaction
   /api/hall5/store/consume/delivery
2. 先购买钻石在兑换商品(含金币)
   /api/hall5/store/consume/transaction
   /api/hall5/store/consume/delivery
   /api/hall5/store/charge/notify

玩家购买商品流程
1. 钻石足够时可以直接兑换商品或强制先购买钻石在兑换(可选)
2. 先购买钻石,支付成功够更改钻石数量和兑换商品
3. hall5.1新增了一个接口当钻石不够时直接返回错误信息，不调支付
'''

from freetime5.twisted.ftlock import lockargname
from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.plugins.hallstore._private import _checker
from hall5.plugins.hallstore._private import _dao
from hall5.plugins.hallstore._private import _store
from tuyoo5.core import tychecker
from tuyoo5.core import tygame
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpcconn
from tuyoo5.core.typlugin import hallRpcOne
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.plugins.store import storeimpl
from tuyoo5.plugins.store.store import TYPluginStore
from tuyoo5.plugins.store.storeimpl import TYProductBuyType


_DEBUG = 0

if _DEBUG:

    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)

else:

    def debug(*argl, **argd):
        pass


class HallPluginStore(TYPluginStore):

    def __init__(self):
        super(HallPluginStore, self).__init__()
        self.checkTransactionStart = tychecker.Checkers(
            hallchecker.check__sdkSignCode,
            tychecker.check_userId,
            tychecker.check_clientId,
            _checker.check_appId,
            _checker.check_realGameId,
            _checker.check_prodOrderId,
            _checker.check_prodId,
            _checker.check_prodCount,
            hallchecker.check__checkUserData,
        )
        self.checkDelivery = tychecker.Checkers(
            hallchecker.check__sdkSignCode,
            tychecker.check_userId,
            tychecker.check_clientId,
            _checker.check_appId,
            _checker.check_realGameId,
            _checker.check_prodOrderId,
            _checker.check_prodId,
            _checker.check_prodCount,
            _checker.check_is_monthly,
            _checker.check_chargeType,
            _checker.check_chargedRmbs,
            _checker.check_chargedDiamonds,
            _checker.check_consumeCoin,
            _checker.check_chargeMap,
            _checker.check_consumeMap,
            _checker.check_platformOrder,
            hallchecker.check__checkUserData,
        )
        self.checkNotify = tychecker.Checkers(
            hallchecker.check__sdkSignCode,
            tychecker.check_userId,
            tychecker.check_clientId,
            _checker.check_appId,
            _checker.check_realGameId,
            _checker.check_prodId,
            _checker.check_chargedRmbs,
            _checker.check_chargedDiamonds,
            hallchecker.check__checkUserData,
        )
        self.checkTerminate = tychecker.Checkers(
            tychecker.check_userId,
            _checker.check_appId,
            _checker.check_realGameId,
            _checker.check_prodOrderId,
            _checker.check_prodId,
            hallchecker.check__checkUserData,
        )

    def destoryPlugin(self):
        _dao.DaoGameOrder.finalize()
        _dao.DaoUserOrderList.finalize()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        _dao.DaoGameOrder.initialize()
        _dao.DaoUserOrderList.initialize()
        self.storeSystem = _store.HallStoreSystem(_dao.TYOrderDao())
        storeimpl.storeSystem = self.storeSystem

    @typlugin.markPluginEntry(confKeys=['game5:{}:store:sc'.format(tyglobal.gameId()),
                                        'game5:{}:products:sc'.format(tyglobal.gameId()),
                                        'game5:{}:store:0'.format(tyglobal.gameId())],
                              srvType=[tyglobal.SRV_TYPE_HALL_UTIL])
    def onConfChanged(self, confKeys, changedKeys):
        super(HallPluginStore, self).onConfChanged(changedKeys, changedKeys)

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _doStoreQueryUi(self, userId, clientId):
        orders = self.storeSystem.getUserOrderList(userId)
        filteredList = self.storeSystem.getShelvesListByClientId(clientId)
        products = []
        for shelf in filteredList:
            for productId in shelf.productIdList:
                product = self.storeSystem.findProduct(productId)
                datas = {
                    'shelfName': shelf.name,
                    'productId': productId,
                    'buyType': product.buyType,
                    'displayName': product.displayName,
                    'price': product.price,
                    'priceDiamond': product.priceDiamond,
                    'diamondExchangeRate': product.diamondExchangeRate,
                }
                products.append(datas)
        for order in orders:
            productId = order[1]
            orderId = order[-1]
            product = self.storeSystem.findProduct(productId)
            if product:
                order.append(product.price)
                order.append(product.priceDiamond)
            orderData = self.storeSystem._loadOrder(orderId)
            if orderData:
                order.append(orderData.count)

        return {'products': products, 'orders': orders}

    @typlugin.markPluginEntry(cmd='store5', act='ui', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doStoreQueryUi(self, msg):
        '''
        查询商城界面列表配置信息
        '''
        mo = MsgPack()
        mo.setCmd('store5')
        mo.setResult('action', 'ui')

        mi = hallchecker.CHECK_BASE.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            filteredList = self.storeSystem.getShelvesListByClientId(mi.clientId)
            tabs = []
            for shelf in filteredList:
                tabs.append({
                    'name': shelf.name,
                    'displayName': shelf.displayName,
                    'items': shelf.productIdList
                })
            mo.setResult('tabs', tabs)

        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd='store5', act='history', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doStoreQueryUserHistory(self, msg):
        '''
        查询个人的商城充值、金币兑换记录
        '''
        mo = MsgPack()
        mo.setCmd('store5')
        mo.setResult('action', 'history')

        mi = hallchecker.CHECK_BASE.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            orders = self.storeSystem.getUserOrderList(mi.userId)
            mo.setResult('orders', orders)

        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(httppath='store/consume/transaction')
    def doConsumeTransactionHttp(self, request):
        """
        购买流程之一：client请求sdk,sdk调用游戏服,游戏服检查商品有效性并存储订单信息
        成功返回：标准MsgPack，需要result中有相同的prodOrderId
        """
        ftlog.info('doConsumeTransactionHttp IN->', request.getDict())

        mo = MsgPack()
        mo.setCmd('buy_prod5')

        mi = self.checkTransactionStart.check(request)
        if mi.error:
            mo.setError(1, str(mi.error))
        else:
            try:
                rfc = hallRpcOne.hallstore.doConsumeTransaction(mi.userId,
                                                                mi.appId,
                                                                mi.realGameId,
                                                                mi.clientId,
                                                                mi.prodOrderId,
                                                                mi.prodId,
                                                                mi.prodCount)
                if rfc.getException():
                    mo.setError(2, str(rfc.getException()))
                else:
                    result = rfc.getResult()
                    if result != 'ok':
                        mo.setError(3, str(result))
                    else:
                        mo.setResult('appId', mi.appId)
                        mo.setResult('userId', mi.userId)
                        mo.setResult('prodId', mi.prodId)
                        mo.setResult('prodCount', mi.prodCount)
                        mo.setResult('prodOrderId', mi.prodOrderId)
            except Exception, e:
                ftlog.error()
                mo.setError(4, str(e))

        ftlog.info('doConsumeTransactionHttp OUT->', mo)
        return mo

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.store', 'userId')
    def doConsumeTransaction(self, userId, gameId, realGameId, clientId, orderId, productId, count):
        ftlog.info('doConsumeTransaction IN->', userId, gameId, realGameId, clientId, orderId, productId, count)
        _, errmsg = self.storeSystem.buyProduct(gameId,
                                                realGameId,
                                                userId,
                                                clientId,
                                                orderId,
                                                productId,
                                                count)
        ftlog.info('doConsumeTransaction OUT->', errmsg)
        return errmsg

    @typlugin.markPluginEntry(httppath='store/consume/delivery')
    def doConsumDeliveryHttp(self, request):
        """
        购买流程之二：购买成功，sdk调用游戏服, 游戏服发物品
        成功返回: success
        """
        ftlog.info('doConsumDeliveryHttp IN->', request.getDict())

        mi = self.checkDelivery.check(request)
        if mi.error:
            ret = 'error,' + str(mi.error)
        elif mi.is_monthly:
            ret = 'error,we not support is_monthly'
        else:
            try:
                rfc = hallRpcOne.hallstore.doConsumDelivery(mi.userId,
                                                            mi.appId,
                                                            mi.realGameId,
                                                            mi.clientId,
                                                            mi.prodOrderId,
                                                            mi.prodId,
                                                            mi.prodCount,
                                                            mi.chargeType,
                                                            mi.chargeMap,
                                                            mi.consumeMap,
                                                            mi.platformOrder)
                if rfc.getException():
                    ret = 'error,' + str(rfc.getException())
                else:
                    result = rfc.getResult()
                    if result.get('error'):
                        ret = 'error,' + str(result.get('error').get('info'))
                    else:
                        ret = 'success'
            except Exception, e:
                ftlog.error()
                ret = 'error,' + str(e)
        ftlog.info('doConsumDeliveryHttp OUT->', ret)
        return ret

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.store', 'userId')
    def doConsumDelivery(self, userId, gameId, realGameId, clientId, prodOrderId, prodId, prodCount, chargeType, chargeMap, consumeMap, platformOrder):
        ftlog.info('doConsumDelivery IN->', userId, gameId, realGameId, clientId, prodOrderId, prodId, chargeType, chargeMap, consumeMap, platformOrder)
        mo = MsgPack()
        mo.setCmd('prod_delivery5')  # 兑换或直冲金币或直冲钻石
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('realGameId', realGameId)
        mo.setResult('prodId', prodId)
        mo.setResult('orderId', prodOrderId)

        product = self.storeSystem.findProduct(prodId)
        if not product:
            ftlog.info('ERROR doConsumDelivery product not found !', prodId)
            mo.setError(1, '没有找到要发货的商品')
        else:
            mo.setResult('buyType', product.buyType)
            mo.setResult('pic', product.pic)

        # 自动补单处理
        if not mo.isError() and not self.storeSystem.isOrderExits(prodOrderId):
            ftlog.info('doConsumDelivery compensate fix->', gameId, realGameId, userId, clientId, prodOrderId, prodId, prodCount)
            _, errmsg = self.storeSystem.buyProduct(gameId,
                                                    realGameId,
                                                    userId,
                                                    clientId,
                                                    prodOrderId,
                                                    prodId,
                                                    prodCount)
            if errmsg != 'ok':
                ftlog.info('ERROR doConsumDelivery compensate fix !!', gameId, userId, prodOrderId, prodId, errmsg)
                mo.setError(1, errmsg)

        if not mo.isError():
            try:
                cinfo = _store.TYChargeInfo(chargeType, chargeMap, consumeMap)
                orderDeliveryResult, errmsg = self.storeSystem.deliveryOrder(userId,
                                                                             realGameId,
                                                                             prodOrderId,
                                                                             prodId,
                                                                             cinfo,
                                                                             platformOrder)
                if not orderDeliveryResult or errmsg != 'ok':
                    mo.setError(-1, errmsg)
                else:
                    # 发送全局充值事件
                    evt = tygame.GlobalChargeEvent(userId,
                                                   gameId,
                                                   realGameId,
                                                   chargeMap['rmb'],
                                                   chargeMap['diamond'],
                                                   prodId, 
                                                   clientId,
                                                   prodOrderId,
                                                   platformOrder)
                    typlugin.asyncTrigerGlobalEvent(evt)

                    if product.buyType == TYProductBuyType.BUY_TYPE_CHARGE:  # 购买砖石，contents 和 assetItems 为空
                        assetItems = [['common.diamond', orderDeliveryResult.order.product.priceDiamond, 0]]
                        mo.setResult('assetItems', assetItems)
                    else:
                        mo.setResult('assetItems', orderDeliveryResult.assetItems)
            except:
                ftlog.error()
                mo.setError(1, '很抱歉，添加物品失败啦！')

        # 通知客户端刷新钻石和金币
        pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, ['diamond', 'chip'])

        tyrpcconn.sendToUser(userId, mo)
        ftlog.info('doConsumDelivery OUT->', mo)
        return mo

    @typlugin.markPluginEntry(httppath='store/pay/cancel')
    def doChargeCancelHttp(self, request):
        '''
        购买流程之三：客户端支付取消或失败
        成功返回: success
        '''
        ftlog.info('doChargeCancel IN->', request.getDict())
        mi = self.checkTerminate.check(request)
        if mi.error:
            ret = 'error,' + str(mi.error)
        else:
            try:
                rfc = hallRpcOne.hallstore.doChargeTerminate(mi.userId,
                                                             mi.appId,
                                                             mi.realGameId,
                                                             mi.prodOrderId,
                                                             mi.prodId,
                                                             _store.TYOrder.STATE_PAY_CANCEL)
                if rfc.getException():
                    ret = 'error, ' + str(rfc.getException())
                else:
                    if rfc.getResult() == 'ok':
                        ret = 'success'
                    else:
                        ret = 'error, ' + str(rfc.getResult())
            except Exception, e:
                ftlog.error()
                ret = 'error, ' + str(e)
        ftlog.info('doChargeCancel OUT->', ret)
        return ret

    @typlugin.markPluginEntry(httppath='store/pay/fail')
    def doChargeFailHttp(self, request):
        '''
        购买流程之三：服务端第三方通知支付失败
        成功返回: success
        '''
        ftlog.info('doChargeFail IN->', request.getDict())
        mi = self.checkTerminate.check(request)
        if mi.error:
            ret = 'error,' + str(mi.error)
        else:
            try:
                rfc = hallRpcOne.hallstore.doChargeTerminate(mi.userId,
                                                             mi.appId,
                                                             mi.realGameId,
                                                             mi.prodOrderId,
                                                             mi.prodId,
                                                             _store.TYOrder.STATE_PAY_FAIL)
                if rfc.getException():
                    ret = 'error, ' + str(rfc.getException())
                else:
                    if rfc.getResult() == 'ok':
                        ret = 'success'
                    else:
                        ret = 'error, ' + str(rfc.getResult())
            except Exception, e:
                ftlog.error()
                ret = 'error, ' + str(e)
        ftlog.info('doChargeFail OUT->', ret)
        return ret

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.store', 'userId')
    def doChargeTerminate(self, userId, gameId, realGameId, prodOrderId, prodId, finishState):
        ftlog.info('doChargeTerminate IN->', userId, prodOrderId)
        ret = self.storeSystem.finishOrder(prodOrderId, userId, finishState)

        # 通知客户端，支付取消或失败
        mo = MsgPack()
        mo.setCmd('prod_payerror5')
        mo.setResult('userId', userId)
        mo.setResult('gameId', gameId)
        mo.setResult('realGameId', realGameId)
        mo.setResult('prodId', prodId)
        mo.setResult('orderId', prodOrderId)
        mo.setResult('state', finishState)
        product = self.storeSystem.findProduct(prodId)
        if product:
            mo.setResult('buyType', product.buyType)
            mo.setResult('pic', product.pic)

        tyrpcconn.sendToUser(userId, mo)

        ftlog.info('doChargeTerminate OUT ->', ret)
        return ret

    @typlugin.markPluginEntry(httppath='store/charge/notify')
    def doChargeNotifyHttp(self, request):
        '''
        仅仅是一个钻石增加的通知，即表明：用户实际花了多少人民币,和购买事物无关
        '''
        ftlog.info('doChargeNotifyHttp IN->', request.getDict())
        mi = self.checkNotify.check(request)
        if mi.error:
            ret = 'error, ' + str(mi.error)
        else:
            try:
                rfc = hallRpcOne.hallstore.doChargeNotify(mi.userId,
                                                          mi.appId,
                                                          mi.realGameId,
                                                          mi.prodId,
                                                          mi.chargedRmbs,
                                                          mi.chargedDiamonds,
                                                          mi.clientId)
                if rfc.getException():
                    ret = 'error, ' + str(rfc.getException())
                else:
                    if rfc.getResult() == 'ok':
                        ret = 'success'
                    else:
                        ret = 'error, ' + str(rfc.getResult())
            except Exception, e:
                ftlog.error()
                ret = 'error, ' + str(e)
        ftlog.info('doChargeNotifyHttp OUT->', ret)
        return ret

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.store', 'userId')
    def doChargeNotify(self, userId, gameId, realGameId, prodId, chargedRmbs, chargedDiamonds, clientId):
        ftlog.info('doChargeNotify IN->', userId, gameId, prodId, chargedRmbs, chargedDiamonds, clientId)

        evt = tygame.ChargeNotifyEvent(userId, gameId, realGameId, chargedRmbs, chargedDiamonds, prodId, clientId)
        typlugin.asyncTrigerEvent(evt)

        evt = tygame.GlobalChargeEvent(userId, gameId, realGameId, chargedRmbs, chargedDiamonds, prodId, clientId, '', '')
        typlugin.asyncTrigerGlobalEvent(evt)

        ftlog.info('doChargeNotify OUT')
        return 'ok'

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    @lockargname('hall5.store', 'userId')
    def _doDelete(self, userId, orderId):
        ftlog.info('_doDelete IN->', userId, orderId)
        self.storeSystem._orderDao.removeOrder(userId, orderId)
        ftlog.info('_doDelete OUT')
        return 'ok'
