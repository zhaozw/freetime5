# coding=UTF-8
'''
'''
from freetime5.util.ftmsg import MsgPack
from freetime5.util import ftlog
from tuyoo5.core import tyrpcconn
from tuyoo5.core.typlugin import gameRpcRoomOne

__author__ = [
    'Zhaoqh'
    '"Zhouhao" <zhouhao@tuyoogame.com>',
]


class TYTableSender(object):
    '''
    桌子使用的发送消息的工具集合类
    '''

    def __init__(self, table):
        self.table = table  # 桌子对象

    def createMsgPackRes(self, cmd, action=None):
        mp = MsgPack()
        mp.setCmd(cmd)
        if action:
            mp.setResult('action', action)
        mp.setResult('gameId', self.table.gameId)
        mp.setResult('roomId', self.table.roomId)  # table/table_call等发给GT的协议必须使用shadowRommId进行路由
        mp.setResult('tableId', self.table.tableId)
        return mp

    def createMsgPackRequest(self, cmd, action=None):
        mp = MsgPack()
        mp.setCmd(cmd)
        if action:
            mp.setParam('action', action)
        mp.setParam('gameId', self.table.gameId)
        mp.setParam('roomId', self.table.roomId)
        mp.setParam('tableId', self.table.tableId)
        return mp

    def sendToAllTableUser(self, mo, exclude=None):
        if ftlog.is_debug():
            ftlog.debug('<< |tableId:', self.tableId,
                        '|len players=', self.table.playersNum,
                        'len observers=', self.table.observers,
                        'exclude=', exclude,
                        '|mo:', mo, caller=self)
        if isinstance(mo, MsgPack):
            mo = mo.pack()
        if exclude == None:
            exclude = []
        for p in self.table.players:
            if p.userId > 0 and not p.userId in exclude:
                tyrpcconn.sendToUser(p.userId, mo)
        for userId in self.table.observers:
            tyrpcconn.sendToUser(userId, mo)

    def sendQuickStartRes(self, userId, clientId, result):
        if ftlog.is_debug():
            ftlog.debug("<< |params", userId, clientId, result, caller=self)
        mpSitRes = self.createMsgPackRes("quick_start")
        mpSitRes.updateResult(result)
        tyrpcconn.sendToUser(userId, mpSitRes)

    @classmethod
    def sendNotifyMsg(cls, gameId, uid, showTime, content):
        """
        {
            "cmd": "notifyMsg",
            "result":
            {
                "showTime": 0.5,
                "content": [{
                    "color": "RRGGBB",
                    "text": "bababababa"
                }, {
                    "color": "RRGGBB",
                    "text": "bababababa"
                }]
            }
        }
        """

        msg_content = [dict(zip(("color", "text"), segment)) for segment in content]

        message = MsgPack()
        message.setCmd('notifyMsg')
        message.setResult("userId", uid)
        message.setResult("gameId", gameId)
        message.setResult("showTime", showTime)
        message.setResult("content", msg_content)

        tyrpcconn.sendToUser(uid, message)

    def sendRoomLeaveReq(self, userId, reason, needSendRes=True):
        gameRpcRoomOne.srvroom.doRoomLeave(self.table.room.ctrlRoomId,
                                           self.table.tableId,
                                           userId,
                                           reason,
                                           needSendRes,
                                           0)

    def sendRobotNotifyCallUp(self, params):
        hasrobot = self.table.runConfig.get("hasrobot", 0)
        if ftlog.is_debug():
            ftlog.debug("|hasrobot, params", hasrobot, params, caller=self)
        if hasrobot:
            ucount, uids = self.getSeatUserIds()
            gameRpcRoomOne.srvrobot.doRobotCallUp(self.table.roomId,
                                                  self.table.tableId,
                                                  ucount,
                                                  uids,
                                                  params,
                                                  0)

    def sendRobotNotifyShutDown(self, params):
        hasrobot = self.table.runConfig["hasrobot"]
        if ftlog.is_debug():
            ftlog.debug("|hasrobot, params", hasrobot, params, caller=self)
        if hasrobot:
            ucount, uids = self.getSeatUserIds()
            gameRpcRoomOne.srvrobot.doRobotShutDown(self.table.roomId,
                                                    self.table.tableId,
                                                    ucount,
                                                    uids,
                                                    params,
                                                    0)
