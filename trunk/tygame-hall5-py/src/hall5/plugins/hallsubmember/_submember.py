# -*- coding=utf-8 -*-
"""
@file  : _tysubmember
@date  : 2016-09-22
@author: GongXiaobo
"""

from datetime import datetime
import time

from dateutil.relativedelta import relativedelta

from freetime5.util import ftlog
from freetime5.util import fttime
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import UserKeys, HallKeys
from tuyoo5.game import tygameitem


class SubMemberStatus(object):
    def __init__(self, isSub, subDT=None, deliveryDT=None, unsubDesc=None, expiresDT=None):
        self.isSub = isSub
        self.subDT = subDT
        self.deliveryDT = deliveryDT
        self.unsubDesc = unsubDesc
        self.expiresDT = expiresDT

    @classmethod
    def calcSubExpiresDT(self, subDT, nowDT):
        '''
        计算nowDT所在订阅周期的到期时间
        @param subDT: 订阅时间
        @param param: 当前时间
        @return: 到期时间
        '''
        years = nowDT.year - subDT.year
        months = nowDT.month - subDT.month
        ret = subDT + relativedelta(years=years, months=months)
        if nowDT.date() >= ret.date():
            ret = subDT + relativedelta(years=years, months=months + 1)
        return ret.replace(hour=0, minute=0, second=0, microsecond=0)

    def isSubExpires(self, nowDT):
        return not self.expiresDT or nowDT >= self.expiresDT

    def calcDeliveryDays(self, nowDT):
        '''
        计算需要发几天货
        '''
        if self.subDT and self.expiresDT:
            # 本次订阅周期到期时间
            if not self.deliveryDT or self.expiresDT > self.calcSubExpiresDT(self.subDT, self.deliveryDT):
                return max(0, (self.expiresDT.date() - nowDT.date()).days)
        return 0


def _decodeDT(timestamp):
    return datetime.fromtimestamp(timestamp) if timestamp >= 0 else None


def _loadSubMemberStatus(userId):
    try:
        d = pluginCross.halldata.getHallDataList(userId, HallKeys.ATT_SUBMEMBER)
        subDT = _decodeDT(d.get('subTime', -1))
        deliveryDT = _decodeDT(d.get('deliveryTime', -1))
        expiresDT = _decodeDT(d.get('expiresTime', -1))
        return SubMemberStatus(False, subDT, deliveryDT, None, expiresDT)
    except:
        ftlog.error()
        return SubMemberStatus(False, None, None, None, None)


def _adjustExpiresDT(status, nowDT):
    if status.subDT:
        # 本次订阅周期到期时间
        expiresDT = SubMemberStatus.calcSubExpiresDT(status.subDT, nowDT)
        if expiresDT != status.expiresDT:
            status.expiresDT = expiresDT
            return True
    return False


def loadSubMemberStatus(userId):
    isYouyifuVipUser, youyifuVipMsg = pluginCross.halldata.getUserDataList(userId, [UserKeys.ATT_YOUYIFU_VIP, UserKeys.ATT_YOUYIFU_MSG])
    isSub = isYouyifuVipUser == 1
    youyifuVipMsg = str(youyifuVipMsg) if youyifuVipMsg is not None else None
    nowDT = datetime.now()
    status = _loadSubMemberStatus(userId)
    status.isSub = isSub
    status.unsubDesc = youyifuVipMsg
    if status.isSub and not status.subDT:
        status.subDT = nowDT
    _adjustExpiresDT(status, nowDT)
    return status


def _saveSubMemberStatus(userId, status):
    d = {}
    if status.subDT:
        d['subTime'] = int(time.mktime(status.subDT.timetuple()))
    if status.deliveryDT:
        d['deliveryTime'] = int(time.mktime(status.deliveryDT.timetuple()))
    if status.expiresDT:
        d['expiresTime'] = int(time.mktime(status.expiresDT.timetuple()))
    pluginCross.halldata.set_submember(userId, d)


def checkSubMember(gameId, userId, eventId, intEventParam):
    status = loadSubMemberStatus(userId)
    _checkSubMember(gameId, userId, fttime.getCurrentTimestamp(), status, eventId, intEventParam)
    return status


def subscribeMember(gameId, userId, timestamp, eventId, intEventParam, param01='', param02=''):
    status = loadSubMemberStatus(userId)
    deliveryDays = _checkSubMember(gameId, userId, timestamp, status, eventId, intEventParam, param01=param01, param02=param02)
    if deliveryDays > 0:
        pluginCross.halldatanotify.sendDataChangeNotify(userId, gameId, ['promotion_loc'])
    return status


def unsubscribeMember(gameId, userId, isTempVipUser, timestamp, eventId, intEventParam):
    status = loadSubMemberStatus(userId)
    _checkSubMember(gameId, userId, timestamp, status, eventId, intEventParam)
    if status.subDT:
        subDT = status.subDT
        nowDT = datetime.fromtimestamp(timestamp)
        balance = pluginCross.hallitem.getAssets(userId, tygameitem.ASSET_ITEM_MEMBER_NEW_KIND_ID)
        removeDays = 0
        if isTempVipUser:
            # 用户首次购买72小时之内如果退订则扣除剩余会员天数
            removeDays = max(0, (status.expiresDT.date() - nowDT.date()).days)
            status.deliveryDT = None
            status.subDT = None
            status.expiresDT = None
#         # 退订会员权益不消失
#         else:
#             # 根据平台中心建议新增：用户退订后会员有效期最长维持到当月最后一天
#             limitDT = datetime.fromtimestamp(pktimestamp.getDeltaMonthStartTimestamp(timestamp, 1))
#             # 最多剩余多少天
#             maxKeep = max(0, (limitDT.date() - nowDT.date()).days)
#             status.subDT = None
#             status.deliveryDT = None
#             status.expiresDT = (nowDT + timedelta(days=maxKeep)).replace(hour=0, minute=0, second=0, microsecond=0)
#             removeDays = max(0, balance - maxKeep)

        _saveSubMemberStatus(userId, status)
        removeDays = min(balance, removeDays)
        if removeDays > 0:
            changed = []
            _, _consumeCount, final = pluginCross.hallitem.consumeAsset(userId, gameId, tygameitem.ASSET_ITEM_MEMBER_NEW_KIND_ID,
                                                                        removeDays, eventId, intEventParam)
            if final <= 0:
                changed.append('promotion_loc')
        ftlog.info('hallsubmember.unsubscribeMember gameId=', gameId,
                   'userId=', userId,
                   'isTempVipUser=', isTempVipUser,
                   'isSub=', status.isSub,
                   'unsubDesc=', status.unsubDesc,
                   'expiresDT=', status.expiresDT.strftime('%Y-%m-%d %H:%M:%S') if status.expiresDT else None,
                   'eventId=', eventId,
                   'intEventParam=', intEventParam,
                   'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                   'subTime=', subDT.strftime('%Y-%m-%d %H:%M:%S') if subDT else None,
                   'balance=', balance,
                   'removeDays=', removeDays)


def _checkSubMember(gameId, userId, timestamp, status, eventId, intEventParam, param01='', param02=''):
    nowDT = datetime.fromtimestamp(timestamp)
    prevDeliveryDT = status.deliveryDT
    deliveryDays = 0
    if status.isSub:
        deliveryDays = status.calcDeliveryDays(nowDT)
        if deliveryDays > 0:
            status.deliveryDT = nowDT
            _saveSubMemberStatus(userId, status)
            pluginCross.hallitem.addAsset(userId, gameId, tygameitem.ASSET_ITEM_MEMBER_NEW_KIND_ID,
                                          deliveryDays, eventId, intEventParam, param01=param01, param02=param02)
    ftlog.info('hallsubmember._checkSubMember gameId=', gameId,
               'userId=', userId,
               'isSub=', status.isSub,
               'unsubDesc=', status.unsubDesc,
               'deliveryDays=', deliveryDays,
               'expiresDT=', status.expiresDT.strftime('%Y-%m-%d %H:%M:%S') if status.expiresDT else None,
               'eventId=', eventId,
               'intEventParam=', intEventParam,
               'timestamp=', datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
               'subTime=', status.subDT.strftime('%Y-%m-%d %H:%M:%S') if status.subDT else None,
               'prevDeliveryTime=', prevDeliveryDT.strftime('%Y-%m-%d %H:%M:%S') if prevDeliveryDT else None)
    return deliveryDays
