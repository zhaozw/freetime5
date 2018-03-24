# -*- coding=utf-8 -*-
"""
@file  : test
@date  : 2016-11-10
@author: GongXiaobo
"""

from datetime import datetime

from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tychecker
from tuyoo5.core import tyglobal
from tuyoo5.core import tyrpcsdk
from tuyoo5.core.typlugin import hallRpcOne
from tuyoo5.core.tyrpchall import ChipNotEnoughOpMode
from tuyoo5.core.tyrpchall import HallKeys
from tuyoo5.core.tyrpchall import UserKeys
from tuyoo5.game import tysessiondata


class HallPluginTestGameData(object):

    def __init__(self):
        self.checkUser = tychecker.Checkers(
            tychecker.check_userId
        )

    def doGameDataTest(self, request):
        action = request.getParamStr('action')
        if action == 'query':
            return self.doGameDataQuery(request)
        if action == 'update':
            return self.doGameDataUpdate(request)
        return 'params action error'

    def doGameDataQuery(self, request):
        mo = MsgPack()
        mi = self.checkUser.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            attrs = [HallKeys.ATT_CREATE_TIME,
                     HallKeys.ATT_AUTHOR_TIME,
                     HallKeys.ATT_LOGIN_DAYS,
                     HallKeys.ATT_LOGIN_SUM,
                     HallKeys.ATT_SET_NAME_SUM,
                     HallKeys.ATT_VIP_EXP,
                     ]
            values = hallRpcOne.halldata.getHallDataList(mi.userId, attrs).getResult()

            sdkattrs = [UserKeys.ATT_DIAMOND,
                        UserKeys.ATT_CHARGE_TOTAL,
                        UserKeys.ATT_PAY_COUNT,
                        UserKeys.ATT_CHIP,
                        UserKeys.ATT_COUPON,
                        UserKeys.ATT_CHARM,
                        ]
            sdkdatas = hallRpcOne.halldata.getUserDataDict(mi.userId, sdkattrs).getResult()

            datas = {}
            for x in xrange(len(attrs)):
                if attrs[x] == HallKeys.ATT_VIP_EXP:
                    datas['vip_exp'] = values[x]
                else:
                    datas[attrs[x]] = values[x]

            datas.update(sdkdatas)

            mo.setResult('datas', datas)
        return mo

    def doGameDataUpdate(self, request):
        mo = MsgPack()
        mi = self.checkUser.check(request)
        if mi.error:
            mo.setError(1, mi.error)
        else:
            try:
                field = request.getParamStr('field')
                value = request.getParamStr('value')

                if field == UserKeys.ATT_DIAMOND:
                    clientId = tysessiondata.getClientId(mi.userId)
                    newVal = int(value.strip())
                    oldVal = hallRpcOne.halldata.getUserDataList(mi.userId, UserKeys.ATT_DIAMOND).getResult()
                    hallRpcOne.halldata.incrDiamond(mi.userId,
                                                    tyglobal.gameId(),
                                                    newVal - oldVal,
                                                    ChipNotEnoughOpMode.CLEAR_ZERO,
                                                    'TEST_ADJUST',
                                                    0,
                                                    clientId)
                    pass

                if field == UserKeys.ATT_CHARGE_TOTAL:
                    newVal = float(value.strip())
                    tyrpcsdk.setUserInfo(mi.userId, chargeTotal=newVal)
                    pass

                if field == UserKeys.ATT_PAY_COUNT:
                    newVal = int(value.strip())
                    tyrpcsdk.setUserInfo(mi.userId, payCount=newVal)
                    pass

                if field == HallKeys.ATT_CREATE_TIME:
                    newVal = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
                    newVal = newVal.strftime('%Y-%m-%d %H:%M:%S.%f')
                    hallRpcOne.halldata._setDataValue(mi.userId, HallKeys.ATT_CREATE_TIME, newVal)
                    pass

                if field == HallKeys.ATT_AUTHOR_TIME:
                    newVal = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
                    newVal = newVal.strftime('%Y-%m-%d %H:%M:%S.%f')
                    hallRpcOne.halldata._setDataValue(mi.userId, HallKeys.ATT_AUTHOR_TIME, newVal)
                    pass

                if field == HallKeys.ATT_LOGIN_DAYS:
                    newVal = int(value.strip())
                    oldVal = hallRpcOne.halldata.getHallDataList(mi.userId, HallKeys.ATT_LOGIN_DAYS).getResult()
                    hallRpcOne.halldata.incrLoginDays(mi.userId, newVal - oldVal)
                    pass

                if field == HallKeys.ATT_LOGIN_SUM:
                    newVal = int(value.strip())
                    oldVal = hallRpcOne.halldata.getHallDataList(mi.userId, HallKeys.ATT_LOGIN_SUM).getResult()
                    hallRpcOne.halldata.incrLoginSum(mi.userId, newVal - oldVal)
                    pass

                if field == HallKeys.ATT_SET_NAME_SUM:
                    newVal = int(value.strip())
                    oldVal = hallRpcOne.halldata.getHallDataList(mi.userId, HallKeys.ATT_SET_NAME_SUM).getResult()
                    hallRpcOne.halldata.incrSetNameSum(mi.userId, newVal - oldVal)
                    pass

                if field == UserKeys.ATT_CHIP:
                    newVal = int(value.strip())
                    oldVal = hallRpcOne.halldata.getUserDataList(mi.userId, UserKeys.ATT_CHIP).getResult()
                    hallRpcOne.halldata.incrChip(mi.userId,
                                                 tyglobal.gameId(),
                                                 newVal - oldVal,
                                                 ChipNotEnoughOpMode.CLEAR_ZERO,
                                                 'TEST_ADJUST',
                                                 0)
                    pass

                if field == UserKeys.ATT_COUPON:
                    newVal = int(value.strip())
                    oldVal = hallRpcOne.halldata.getUserDataList(mi.userId, UserKeys.ATT_COUPON).getResult()
                    hallRpcOne.halldata.incrCoupon(mi.userId,
                                                   tyglobal.gameId(),
                                                   newVal - oldVal,
                                                   ChipNotEnoughOpMode.CLEAR_ZERO,
                                                   'TEST_ADJUST',
                                                   0)
                    pass

                if field == UserKeys.ATT_CHARM:
                    newVal = int(value.strip())
                    oldVal = hallRpcOne.halldata.getUserDataList(mi.userId, UserKeys.ATT_CHARM).getResult()
                    hallRpcOne.halldata.incrCharm(mi.userId, newVal - oldVal)
                    pass

                if field == 'vip_exp':
                    newVal = int(value.strip())
                    oldVal = hallRpcOne.halldata.getHallDataList(mi.userId, HallKeys.ATT_VIP_EXP).getResult()
                    hallRpcOne.halldata.incrVipExp(mi.userId, newVal - oldVal)
                    pass

                mo.setResult('ok', 1)
            except Exception, e:
                mo.setError(1, str(e))
        return mo
