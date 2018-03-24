# -*- coding=utf-8 -*-
'''
Created on 2015年10月17日

@author: liaoxx
'''
import base64
import collections
import functools
import json

from freetime5.util import ftlog, ftstr
from majiang2.entity import majiang_conf
from tuyoo5.core import tyrpcconn
from tuyoo5.game import tysessiondata
from tuyoo5.core.typlugin import pluginCross, gameRpcRoomOne
from tuyoo5.core.tyconst import HALL_GAMEID
from freetime5.util.ftmsg import MsgPack


class Majiang2Util(object):
    @classmethod
    def dict2list(cls, d):
        l = []
        if isinstance(d, dict):
            for k, v in d.iteritems():
                l.append(k)
                l.append(v)
        return l
    
    @classmethod
    def dict_sort(cls, d, ol):
        """sort dict by ol
        """
        if len(ol) <= 0:
            return d

        if len(d.keys()) >= len(ol):
            s_list, l_list = ol, d.keys()
        else:
            s_list, l_list = d.keys(), ol

        diff_l = cls.list_diff(s_list, l_list)

        nol = ol[:]
        nol.extend(diff_l)
        if sorted(d.keys()) == sorted(nol):
            sd = collections.OrderedDict()
            for k in nol:
                sd[k] = d.get(k)
            return sd

        return d

    @classmethod
    def list2dict(cls, l):
        d = {}
        if isinstance(l, list):
            length = len(l)
            while length > 1:
                d[l[length - 2]] = l[length - 1]
                length -= 2
        return d

    @classmethod
    def list_merge(cls, l1, l2):
        l = []
        for i, j in zip(l1, l2):
            l.append(i)
            l.append(j)
        return l

    @classmethod
    def check_msg_result(cls, msg):
        if not msg._ht.has_key('result'):
            msg._ht['result'] = {}
            
    @classmethod
    def sendShowInfoTodoTask(cls, uid, gid, msg):
        pluginCross.mj2todotask.sendTodoTaskShowInfo(gid, uid, msg)

    @classmethod
    def getClientVerAndDeviceType(cls, clientId):
        infos = clientId.split('_')
        if len(infos) > 2:
            try:
                clientVer = float(infos[1])
                deviceType = infos[0].lower()
                return clientVer, deviceType
            except:
                pass
        return 0, ''            

    @classmethod
    def getClientId(self, uid):
        if uid < 10000:
            clientId = "robot_3.7_-hall6-robot"
        else:
            clientId = tysessiondata.getClientId(uid)
        return  clientId
    
    @classmethod
    def getClientIdVer(self, uid):
        if uid < 10000:
            clientId = 3.7
        else:
            clientId = tysessiondata.getClientIdVer(uid)
        return  clientId
    
    @classmethod
    def list_diff(cls, short_list, long_list):
        '''获取list差集
        '''
        l_list = ftstr.cloneData(long_list)
        for l in short_list:
            if l in l_list:
                l_list.remove(l)
        return l_list
    
    @classmethod
    def list_intersection(cls, a_list, b_list):
        '''获取list交集
        '''
        return [v for v in a_list if v in b_list]
    
    @classmethod
    def list_union(cls, a_list, b_list):
        '''不去重复元素的list并集
        '''
        return a_list + [v for v in b_list if v not in a_list]
        
def sendPrivateMessage(userId, msg):
    """ 发送个人消息
    """
#     if not isinstance(msg, unicode):
#         msg = unicode(msg)
#     message.sendPrivate(9999, userId, 0, msg)
    ftlog.warn('TODO, HALL51 not support user private message', userId, msg)

def safemethod(method):
    """ 方法装饰，被装饰函数不会将异常继续抛出去
    """
    @functools.wraps(method)
    def safetyCall(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except:
            ftlog.exception()
    return safetyCall


def sendPopTipMsg(userId, msg, duration=3):
    pluginCross.mj2todotask.sendTodoTaskPopTipMsg(HALL_GAMEID, userId, msg, duration)


def sendTableInviteShareTodoTask(userId, gameId, tableNo, playMode, cardCount, contentStr):
    '''牌桌上邀请处理
    '''
    ftlog.warn('TODO not implement !')
#     shareId = hallshare.getShareId('mj_invite_play_share', userId, gameId)
#     if shareId:
#         share = hallshare.findShare(shareId)
#         if not share:
#             return
# 
#         retDesc = ''
#         play_mode_dict = majiang_conf.get_room_other_config(gameId).get('playmode_desc_map', {})
# 
#         if gameId == 715 or gameId == 701:
#             retDesc = contentStr
#         else:
#             retDesc += play_mode_dict.get(playMode, '') if playMode else ''
#             retDesc += contentStr
#         ftlog.debug('sendTableInviteShareTodoTask last retDesc:', retDesc)
#         share.setDesc(retDesc)
# 
#         if gameId == 715:
#             title = play_mode_dict.get(playMode, '') if playMode else ''
#             title += ' - 房号:' + tableNo
#         elif gameId == 701:
#             title = play_mode_dict.get(playMode, '') if playMode else ''
#             ftlog.debug('sendTableInviteShareTodoTask playMode:', title)
#             title += '速来，房间号' + tableNo
#         else:
#             title = share.title.getValue(userId, gameId)
#             title = '房间号：' + tableNo + '，' + title
#         share.setTitle(title)
#         ftlog.debug('sendTableInviteShareTodoTask newTitle:', title)
# 
#         url = share.url.getValue(userId, gameId)
#         url += "?ftId=" + tableNo
#         url += "?from=magicWindow"
#         eParams = {}
#         eParams['action'] = 'hall_enter_friend_table_direct'
#         fParam = {}
#         fParam['ftId'] = tableNo
#         eParams['params'] = fParam
#         paramStr = json.dumps(eParams)
#         base64Str = base64.b64encode(paramStr)
#         from urllib import quote
#         url += "&enterParams=" + quote(base64Str)
#         share.setUrl(url)
#         ftlog.debug('sendTableInviteShareTodoTask newUrl:', url, ' ftId:', tableNo, ' paramStr:', paramStr, ' base64Str:', base64Str)
# 
#         todotask = share.buildTodotask(gameId, userId, 'mj_invite_play_share')
#         pluginCross.mj2todotask.sendTodoTask(gameId, userId, todotask)


def send_led(gameId, msg):
    '''系统led'''
#     hallled.sendLed(gameId, msg, 0)

def notifyChargeOk(userId, gameId, clientId):
    '''
    处理充值成功事件
    
    获取用户的loc，如果在gameId游戏中，则想改游戏的牌桌发送充值成功的消息
    '''
    truelocs, _onTableIds = pluginCross.onlinedata.checkUserLoc(userId, clientId, gameId)
    ftlog.debug('MajiangQuickStartCoin.onCmdQuickStart checkUserLoc:', truelocs)
    for loc in truelocs:
        lgameId, lroomId, ltableId, lseatId = loc.split('.')
        lgameId, lroomId, ltableId, lseatId = ftstr.parseInts(lgameId, lroomId, ltableId, lseatId)
        if lgameId != gameId:
            return
        
        if lroomId > 0 and ltableId > 0:
#             mo = MsgPack()
#             mo.setCmd('table_manage')
#             mo.setAction('charge_success')
#             mo.setParam('userId', userId)
#             mo.setParam('clientId', clientId)
#             mo.setParam('roomId', lroomId)
#             mo.setParam('tableId', ltableId)
            gameRpcRoomOne.srvroom.doUserChangeDone(lroomId, ltableId, userId, clientId, 0)
if __name__ == "__main__":
    di = {"wanFa": 1, "cardCount": 2}
    d2 = Majiang2Util.dict_sort(di, [])
    print d2
