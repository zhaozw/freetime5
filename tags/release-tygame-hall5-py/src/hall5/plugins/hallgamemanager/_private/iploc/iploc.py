# -*- coding=utf-8
'''
Created on 2017年4月5日

@author: zqh
'''
from bisect import bisect

from freetime5.util import ftlog
from hall5.plugins.hallgamemanager._private.iploc.ipaddr import IPAddress

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


def getResourcePath(fileName):
    '''
    取得当前文件下某一个资源的绝对路径
    '''
    import os
    cpath = os.path.abspath(__file__)
    cpath = os.path.dirname(cpath)
    fpath = cpath + os.path.sep + fileName
    return fpath


class IPLoc(object):

    def __init__(self, ipfile):
        filename = getResourcePath('./' + ipfile)
        self._ip_list_start = []
        self._ip_list_end = []
        with open(filename, 'r') as f:
            for line in f:
                if len(line) == 0 or line == '\n':
                    continue
                start, end, locality = line[:-1].split(' ')
                self._ip_list_start.append(int(start))
                self._ip_list_end.append((int(end), locality))

    def _binary_search(self, x, lo=0, hi=None):
        if hi is None:
            hi = len(self._ip_list_start)
        pos = bisect(self._ip_list_start, x, lo, hi)
        if pos == 0:
            return -1
        return pos - 1

    def find(self, ipstr):
        ipInt = IPAddress(ipstr)._ip
        pos = self._binary_search(ipInt)
        ip_start = self._ip_list_start[pos]
        ip_end = self._ip_list_end[pos][0]
        if ipInt > ip_start and ipInt < ip_end:
            if self._ip_list_end[pos][1] >= 0:
                return self._ip_list_end[pos][1]
        return None


class IPLocKeyArea(object):

    def __init__(self, ipfile):
        filename = getResourcePath('./' + ipfile)
        self._ip_list_start = []
        self._ip_list_end = []
        with open(filename, 'r') as f:
            for line in f:
                if len(line) == 0 or line == '\n':
                    continue
                start, end, locality = line[:-1].split(' ')
                self._ip_list_start.append(int(start))
                self._ip_list_end.append((int(end), locality))

    def _binary_search(self, x, lo=0, hi=None):
        if hi is None:
            hi = len(self._ip_list_start)
        pos = bisect(self._ip_list_start, x, lo, hi)
        if pos == 0:
            return -1
        return pos - 1

    def find(self, ipstr):
        ipInt = IPAddress(ipstr)._ip
        pos = self._binary_search(ipInt)
        ip_start = self._ip_list_start[pos]
        ip_end = self._ip_list_end[pos][0]
        if ipInt > ip_start and ipInt < ip_end:
            if isinstance(self._ip_list_end[pos][1], (str, unicode)):
                if self._ip_list_end[pos][1].find("北京市") >= 0 or self._ip_list_end[pos][1].find("广州市") >= 0 or self._ip_list_end[pos][1].find("深圳市") >= 0:
                    return self._ip_list_end[pos][1]
        return None

# _IPLocBeiJing = None
#
#
# def isBeijingIp(ipstr):
#     try:
#         global _IPLocBeiJing
#         if _IPLocBeiJing is None:
#             _IPLocBeiJing = IPLoc('ip_locality_beijing.txt')
#         if _IPLocBeiJing.find(ipstr):
#             return 1
#         return 0
#     except:
#         ftlog.exception('find iploc->' + str(ipstr))
#     return 1  # 如果异常我们认为是北京的IP
#
_IPLocAll = None


def getIpLocation(ipstr):
    try:
        global _IPLocAll
        if _IPLocAll is None:
            _IPLocAll = IPLoc('ip_locality_all.txt')
        return _IPLocAll.find(ipstr)
    except:
        ftlog.exception('find iploc->' + str(ipstr))
    return None



class FilterUser(object):

    def __init__(self, filterUserfile):
        filename = getResourcePath('./' + filterUserfile)
        self._filter_users = []
        with open(filename, 'r') as f:
            for line in f:
                if len(line) == 0 or line == '\n':
                    continue
                user = line
                self._filter_users.append(int(user))

    def find(self, userId):
        if userId in self._filter_users:
            return 1
        return None


_IPLocBjSz = None
_filterUsers = None

def isBjSzIp(ipstr):
    try:
        global _IPLocBjSz
        if _IPLocBjSz is None:
            _IPLocBjSz = IPLocKeyArea('ip_locality_all.txt')
        if _IPLocBjSz.find(ipstr):
            return 1
        return 0
    except:
        ftlog.exception('find iploc->' + str(ipstr))
    return 1  # 如果异常我们认为是北京的IP

def isFilterUser(userId):
    try:
        global _filterUsers
        if _filterUsers is None:
            _filterUsers = FilterUser('filter_user_list.txt')
        if _filterUsers.find(userId):
            return 1
        return 0
    except:
        ftlog.exception('find users->' + userId)
    return 1    #满足条件,可以继续玩的玩家