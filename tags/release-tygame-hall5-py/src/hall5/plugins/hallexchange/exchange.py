# -*- coding=utf-8 -*-

from datetime import datetime

from freetime5.twisted import ftcore
from freetime5.util import ftlog
from freetime5.util import fttime
from freetime5.util.ftmsg import MsgPack
from hall5.entity import hallchecker
from hall5.plugins.hallexchange._private import _addr, _counts
from hall5.plugins.hallexchange._private import _conf
from hall5.plugins.hallexchange._private import _dao
from hall5.plugins.hallexchange._private import _exchange
from tuyoo5.core import tychecker
from tuyoo5.core import tyglobal
from tuyoo5.core import typlugin
from tuyoo5.core import tyrpcconn
from tuyoo5.core.typlugin import hallRpcOne


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginExchange(typlugin.TYPlugin):

    def __init__(self):
        super(HallPluginExchange, self).__init__()
        self._trimLedTimer = None
        self.checkUi = hallchecker.CHECK_BASE.clone()
        self.checkUi.addCheckFun(_exchange.check_tabName)
        self.checkUi.addCheckFun(_exchange.check_pageNum)
        self.checkJdAddr = hallchecker.CHECK_BASE.clone()
        self.checkJdAddr.addCheckFun(_exchange.check_proviceId)
        self.checkJdAddr.addCheckFun(_exchange.check_cityId)
        self.checkJdAddr.addCheckFun(_exchange.check_countyId)
        self.checkJdAddr.addCheckFun(_exchange.check_townId)
        self.checkGdssAudit = tychecker.Checkers(
            tychecker.check_userId,
            _exchange.check_exchangeId,
            _exchange.check_result,
            _exchange.check_extOrderId,
            _exchange.check_extCardId,
            _exchange.check_extCardPwd,
        )
        self.checkExchange = hallchecker.CHECK_BASE.clone()
        self.checkExchange.addCheckFun(_exchange.check_extabName)
        self.checkExchange.addCheckFun(_exchange.check_itemId)
        self.checkExchange.addCheckFun(_exchange.check_proviceId)
        self.checkExchange.addCheckFun(_exchange.check_cityId)
        self.checkExchange.addCheckFun(_exchange.check_countyId)
        self.checkExchange.addCheckFun(_exchange.check_townId)
        self.checkExchange.addCheckFun(_exchange.check_proviceName)
        self.checkExchange.addCheckFun(_exchange.check_cityName)
        self.checkExchange.addCheckFun(_exchange.check_countyName)
        self.checkExchange.addCheckFun(_exchange.check_townName)
        self.checkExchange.addCheckFun(_exchange.check_phone)
        self.checkExchange.addCheckFun(_exchange.check_uName)
        self.checkExchange.addCheckFun(_exchange.check_uAddres)
        self.checkExchange.addCheckFun(_exchange.check_wxappid)
        self.checkExchange.addCheckFun(_exchange.check__relation_)

    def destoryPlugin(self):
        _dao.DaoExchangeCount.finalize()
        _dao.DaoExchangeId.finalize()
        _dao.DaoExchangeRecord.finalize()
        _dao.DaoExchangeLed.finalize()
        if not self._trimLedTimer is None:
            self._trimLedTimer.cancel()
            self._trimLedTimer = None

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_HALL_UTIL])
    def initPluginBefore(self):
        _dao.DaoExchangeCount.initialize()
        _dao.DaoExchangeId.initialize()
        _dao.DaoExchangeRecord.initialize()
        _dao.DaoExchangeLed.initialize()
        self._trimLedTimer = ftcore.runOnceDelay(600, _dao.trimLedItem)  # 每10分钟trim一次

    @typlugin.markPluginEntry(confKeys=['game5:{}:exchange'.format(tyglobal.gameId()),
                                        'game5:{}:exchange_chip'.format(tyglobal.gameId()),
                                        'game5:{}:exchange_czcard'.format(tyglobal.gameId()),
                                        'game5:{}:exchange_electric'.format(tyglobal.gameId()),
                                        'game5:{}:exchange_jdcard'.format(tyglobal.gameId()),
                                        'game5:{}:exchange_rice'.format(tyglobal.gameId()),
                                        'game5:{}:exchange_supplies'.format(tyglobal.gameId())],
                              srvType=[tyglobal.SRV_TYPE_HALL_UTIL])
    def onConfChanged(self, confKeys, changedKeys):
        _conf.reloadConfig()

    @typlugin.markPluginEntry(cmd='exchange5', act='led', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doExchangeLedCmd(self, msg):
        mo = MsgPack()
        mo.setCmd('exchange5')
        mo.setResult('action', 'led')
        mi = hallchecker.CHECK_BASE.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            leds = _dao.loadLedList()
            mo.setResult('leds', leds)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _doExchangeQueryUi(self, userId, clientId):
        items = []
        _bannerIds, tabIds = _conf.getExchangeQueryUiTabs(clientId)
        msc = _conf.MAINCONF.getScConfig()
        for tabId in tabIds:
            tname = msc['extabs'][tabId]['name']
            itemIds = []
            page = 0
            ids = 1
            while ids:
                ids = _conf.getExchangeQueryUiItems(tname, page, clientId)
                page += 1
                if ids:
                    itemIds.extend(ids)
            subconf = _conf.SUBCONFS[tname]
            for itemId in itemIds:
                itemConf = subconf.getScConfig().get('exitems', {}).get(itemId)
                items.append({'tab': tname,
                              'id': itemId,
                              'title': itemConf['title'],
                              'price': itemConf['price'],
                              'count': itemConf['count'],
                              'showtext': itemConf['showtext'],
                              })
        orders = []
        exchangeIds = _dao.getReordKeys(userId)
        exchangeIds.sort(reverse=True)
        for exchangeId in exchangeIds:
            order = _dao.loadRecord(userId, exchangeId)
            orders.append({
                'time': fttime.formatTimeSecond(datetime.fromtimestamp(order.createTime)),  # 兑换时间
                'exchangeId': exchangeId,  # 兑换ID
                'state': order.state,  # 兑换状态
                'type': order.params['type'],  # 兑换类型 0-手机充值卡 3-京东卡 6-京东实物 99-金币
                'displayName': order.params['displayName'],  # 兑换物品名称
                'uName': order.params['uName'],  # 昵称
                'phone': order.params['phone'],  # 电话
                'itemId': order.params['itemId'],
                'coupon': order.params['coupon'],
                'count': order.params['count'],
                'addr': order.params.get('jdAddres', []),  # 京东收货地址数组 [1级，2级，3级，4级，输入地址]
                'extOrderId': order.extOrderId,  # 京东实物交易单号
            })
        return {'items': items, 'orders': orders}

    @typlugin.markPluginEntry(cmd='exchange5', act='ui_tabs', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doExchangeQueryUiTabs(self, msg):
        mo = MsgPack()
        mo.setCmd('exchange5')
        mo.setResult('action', 'ui_tabs')
        mi = hallchecker.CHECK_BASE.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            bannerIds, tabIds = _conf.getExchangeQueryUiTabs(mi.clientId)
            mo.setResult('banners', bannerIds)
            mo.setResult('tabs', tabIds)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd='exchange5', act='ui_items', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doExchangeQueryUiItems(self, msg):
        mo = MsgPack()
        mo.setCmd('exchange5')
        mo.setResult('action', 'ui_items')
        mi = self.checkUi.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            items = _conf.getExchangeQueryUiItems(mi.tabName, mi.pageNum, mi.clientId)
            counts = _counts.getItemCounts(items)
            mo.setResult('tabName', mi.tabName)
            mo.setResult('pageNum', mi.pageNum)
            mo.setResult('items', items)
            mo.setResult('counts', counts)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _doGetJdAddressList(self, userId, proviceId, cityId, countyId):
        address = _addr.getJdAddress(proviceId, cityId, countyId)
        return address

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def _doDelete(self, userId, exchangeId):
        _dao.removeExchange(userId, exchangeId)
        return 1

    @typlugin.markPluginEntry(cmd='exchange5', act='jdaddress', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doGetJdAddressInfo(self, msg):
        mo = MsgPack()
        mo.setCmd('exchange5')
        mo.setResult('action', 'jdaddress')
        mi = self.checkJdAddr.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            address = _addr.getJdAddress(mi.proviceId, mi.cityId, mi.countyId)
            mo.setResult('proviceId', mi.proviceId)
            mo.setResult('cityId', mi.cityId)
            mo.setResult('countyId', mi.countyId)
            mo.setResult('address', address)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd='exchange5', act='checkjdaddress', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doCheckJdAddressInfo(self, msg):
        mo = MsgPack()
        mo.setCmd('exchange5')
        mo.setResult('action', 'checkjdaddress')
        mi = self.checkJdAddr.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            isOk = _addr.checkJdAddress(mi.proviceId, mi.cityId, mi.countyId, mi.townId)
            if isOk:
                mo.setResult('ok', 1)
            else:
                mo.setError(1, 'check false')
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(cmd='exchange5', act='exchange', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def doExchangeRequestCmd(self, msg):
        mo = MsgPack()
        mo.setCmd('exchange5')
        mo.setResult('action', 'exchange')
        mi = self.checkExchange.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            exchangeId, errMsg = _exchange.doExchangeRequest(mi.userId, mi)
            mo.setResult('exchangeId', exchangeId)
            if errMsg:
                mo.setError(1, errMsg)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(export=1, rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def doExchangeRequest(self, userId, msg):
        '''
        给道具系统的接口
        '''
        if isinstance(msg, dict):
            msg = MsgPack(msg)
        mi = self.checkExchange.check(msg)
        if mi.error:
            return None, mi.error
        else:
            return _exchange.doExchangeRequest(mi.userId, mi)

    @typlugin.markPluginEntry(cmd='exchange5', act='history', srvType=tyglobal.SRV_TYPE_HALL_UTIL)
    def getExchangeHistory(self, msg):
        mo = MsgPack()
        mo.setCmd('exchange5')
        mo.setResult('action', 'history')
        mi = hallchecker.CHECK_BASE.check(msg)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            orders = []
            exchangeIds = _dao.getReordKeys(mi.userId)
            exchangeIds.sort(reverse=True)
            for exchangeId in exchangeIds:
                order = _dao.loadRecord(mi.userId, exchangeId)
                orders.append([
                    exchangeId,  # 兑换ID
                    fttime.formatTimeSecond(datetime.fromtimestamp(order.createTime)),  # 兑换时间
                    order.state,  # 兑换状态
                    order.params['type'],  # 兑换类型 0-手机充值卡 1-手工兑换 2-比赛等线下邀请函、门票等 3-京东卡 4-未使用 5-微信红包 6-京东实物 99-金币
                    order.params['displayName'],  # 兑换物品名称
                    order.params['uName'],  # 昵称
                    order.params['phone'],  # 电话
                    order.params.get('jdAddres', []),  # 京东收货地址数组 [1级，2级，3级，4级，输入地址]
                    order.extOrderId,  # 京东实物交易单号
                    order.extCardId,  # 京东卡卡号
                    order.extCardPwd,  # 京东卡卡密
                ])
            mo.setResult('userId', mi.userId)
            mo.setResult('orders', orders)
        tyrpcconn.sendToUser(mi.userId, mo)
        return 1

    @typlugin.markPluginEntry(httppath='exchange/auditCallback')
    def doExchangeAuditHttp(self, request):
        """
        gdss通知兑换申请审核结果
        """
        mo = MsgPack()
        mo.setCmd('exchange')
        mo.setParam('action', 'audit')
        mi = self.checkGdssAudit.check(request)
        if mi.error:
            mo.setResult('0', mi.error)
        else:
            try:
                rfc = hallRpcOne.hallexchange.doExchangeAudit(mi.userId,
                                                              mi.exchangeId,
                                                              mi.result,
                                                              mi.extOrderId,
                                                              mi.extCardId,
                                                              mi.extCardPwd)
                ret = rfc.getResult()
                mo.setResult('0', ret)
            except Exception, e:
                ftlog.error()
                mo.setResult('0', str(e))
        return mo

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def doExchangeAudit(self, userId, exchangeId, result, extOrderId, extCardId, extCardPwd):
        """
        gdss通知兑换申请审核结果
        """
        return _exchange.doExchangeGdssCallBack(userId,
                                                exchangeId,
                                                result,
                                                extOrderId,
                                                extCardId,
                                                extCardPwd)

    @typlugin.markPluginEntry(httppath='exchange/shippingCallback')
    def doExchangeShippingHttp(self, request):
        """
        gdss通知兑换投递结果
        """
        mo = MsgPack()
        mo.setCmd('exchange')
        mo.setParam('action', 'shipping')
        mi = self.checkGdssAudit.check(request)
        if mi.error:
            mo.setResult('0', mi.error)
        else:
            try:
                rfc = hallRpcOne.hallexchange.doExchangeShipping(mi.userId,
                                                                 mi.exchangeId,
                                                                 mi.result,
                                                                 mi.extOrderId,
                                                                 mi.extCardId,
                                                                 mi.extCardPwd)
                ret = rfc.getResult()
                mo.setResult('0', ret)
            except Exception, e:
                ftlog.error()
                mo.setResult('0', str(e))
        return mo

    @typlugin.markPluginEntry(rpc=tyglobal.SRV_TYPE_HALL_UTIL)
    def doExchangeShipping(self, userId, exchangeId, result, extOrderId, extCardId, extCardPwd):
        """
        gdss通知兑换投递结果
        """
        return _exchange.doExchangeGdssCallBack(userId,
                                                exchangeId,
                                                result,
                                                extOrderId,
                                                extCardId,
                                                extCardPwd)
