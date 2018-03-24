# -*- coding=utf-8 -*-
"""
@file  : _dao
@date  : 2016-12-02
@author: GongXiaobo
"""
from freetime5.util import ftlog
from tuyoo5.core import tyrpcgdss


def getJdAddress(proviceId, cityId, countyId):
    try:
        if proviceId:
            resp = tyrpcgdss.getJdCity(proviceId)
        elif cityId:
            resp = tyrpcgdss.getJdCounty(cityId)
        elif countyId:
            resp = tyrpcgdss.getJdTown(countyId)
        else:
            resp = tyrpcgdss.getJdProvice()
        return resp
    except:
        ftlog.error('getJdAddress', proviceId, cityId, countyId)
        return {}


def checkJdAddress(proviceId, cityId, countyId, townId):
    try:
        ftlog.debug('checkJdAddress->', proviceId, cityId, countyId, townId)
        return tyrpcgdss.checkJdAddress(proviceId, cityId, countyId, townId)
    except:
        ftlog.error('checkJdAddress', proviceId, cityId, countyId, townId)
        return 0
