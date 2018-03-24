# -*- coding: utf-8 -*-
'''
Created on 2016年5月1日

@author: zqh
'''
from freetime5.util import ftlog
from freetime5.util import ftstr
from freetime5.util import fttime
from tuyoo5.core import tychecker
from tuyoo5.core import tyconfig
from tuyoo5.core import tyglobal
from tuyoo5.core import tyrpcsdk


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


def isCurrentUserHallUt(userId):
    return tyglobal.isCurrentUserServer(userId, tyglobal.SRV_TYPE_HALL_UTIL)


CHECK_BASE = tychecker.Checkers(
    tychecker.check_userId,
    tychecker.check_apiVersion,
    tychecker.check_gameId,
    tychecker.check_clientId
)


def check__checkUserData(msg, result, name):
    if tyrpcsdk.checkUserData(result.userId):
        return 1, None
    else:
        return None, 'check__checkUserData error [%s]!!' % (result.userId)


def check__gdssSingCode(request, result, name):
    if tyglobal.enableTestHtml():
        return 0, None
    code = ''
    datas = request.getDict()
    if 'code' in datas:
        code = datas['code']
        del datas['code']
    keys = sorted(datas.keys())
    checkstr = ''
    for k in keys:
        checkstr += k + '=' + datas[k] + '&'
    checkstr = checkstr[:-1]

    apikey = 'www.tuyoo.com-api-6dfa879490a249be9fbc92e97e4d898d-www.tuyoo.com'
    checkstr += apikey
    if code != ftstr.md5digest(checkstr):
        return -1, 'check_gdssSingCode code error'

    acttime = int(datas.get('time', 0))
    if abs(fttime.getCurrentTimestamp() - acttime) > 10:
        return -1, 'check_gdssSingCode time error'
    return 0, None


def check__sdkSignCode(request, result, name):
    if tyglobal.enableTestHtml() and '_test_' in request.args:
        return 0, None

    public_conf = tyconfig.getCacheGameTcData('public', tyglobal.gameId())
    appKey = public_conf.get('appkeys', '')

    args = request.args
    rparam = {}
    for k, v in args.iteritems():
        rparam[k] = v[0]
    code = rparam.pop('code')

    sk = rparam.keys()
    sk.sort()
    ret = ""
    for k in sk:
        ret = ret + str(k) + '=' + str(rparam[k]) + '&'
    signStr = ret[:-1]

    md5code = ftstr.md5digest(str(appKey) + signStr + str(appKey))
    if md5code == code:
        return 1, None
    return None, 'check_sdkSignCode error !'
