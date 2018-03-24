# -*- coding: utf-8 -*-
'''
Created on 2015-5-12
@author: zqh
每个配置项必须是JSON格式
'''
from freetime5.util import fttime
from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import HallKeys

def getWeiXinAppId(userId=None, clientId=None):
    return 'wxb01a635a437adb75'


def filterNoticeStartStopTime(defIds, cachedConfig, scKey):
    showIds = []
    ct = fttime.formatTimeSecond()
    confAll = cachedConfig.getScConfig().get(scKey, {})
    for nid in defIds:
        # 开始截止日期判定
        conf = confAll.get(nid)
        if not conf:
            continue
        startTime = conf['startTime']
        endTime = conf['endTime']
        ntype = conf['notice_type']
        if ct < startTime or ct > endTime or ntype == 1:
            continue
        else:
            showIds.append(nid)
    return showIds

def filterStartStopTime(defIds, cachedConfig, scKey):
    showIds = []
    ct = fttime.formatTimeSecond()
    confAll = cachedConfig.getScConfig().get(scKey, {})
    for nid in defIds:
        # 开始截止日期判定
        conf = confAll.get(nid)
        if not conf:
            continue
        startTime = conf['startTime']
        endTime = conf['endTime']
        if ct < startTime or ct > endTime:
            continue
        else:
            showIds.append(nid)
    return showIds

def filterNewPlayerTimeLimit(defIds, cachedConfig, scKey, userId):
    now_time = fttime.getCurrentTimestamp()
    notice_add_showIds = []
    confAll = cachedConfig.getScConfig().get(scKey, {})
    for nid in defIds:
        # 开始日期判定
        conf = confAll.get(nid)
        if not conf:
            continue
        ntype = conf['notice_type']
        if ntype == 1:
            limit_day = int(conf['limit_day'])
            #time_str = hallRpcOne.halldata.getCreateTimeInfo(userId)
            time_str = pluginCross.halldata.getHallDataList(userId, HallKeys.ATT_CREATE_TIME)
            timestamp = fttime.timestrToTimestamp(time_str, '%Y-%m-%d %H:%M:%S.%f')
            valid_time_max = timestamp + limit_day*24*60*60
            #print "======= test craete timestamp : ", timestamp, "   valid_time is : ", valid_time_max, " nid is : ", nid
            if valid_time_max > 0 and valid_time_max > now_time:
                notice_add_showIds.append(nid)

    return notice_add_showIds

def checkStartStopTime(conf):
    ct = fttime.formatTimeSecond()
    startTime = conf['startTime']
    endTime = conf['endTime']
    if ct < startTime or ct > endTime:
        return 0
    return 1


def checkStartStopTimeList(confs):
    ct = fttime.formatTimeSecond()
    newConfs = []
    for conf in confs:
        startTime = conf['startTime']
        endTime = conf['endTime']
        if ct < startTime or ct > endTime:
            continue
        else:
            newConfs.append(conf)
    return newConfs
