# -*- coding:utf-8 -*-
"""
Created on 2018年02月02日11:16:10

@author: yzx

测试用例，可以测试插件到数据存储,需要启动本地的docker.
"""

from biz import mock
from biz.mock import patch, MagicMock
from freetime5._tyserver._entity import ftglobal
from freetime5._tyserver._entity import tyinit
from freetime5.twisted import ftcore
from freetime5.util.ftmsg import MsgPack


def _initSafe(server_id, mn_port, conf_ip, conf_port, conf_dbid, namespace, mainPyFile, *argl, **argd):
    serverDefine = [{'agent': '172.16.4.15:8005', 'gameId': 9999, 'id': '9999000001', 'ip': '172.16.4.15',
                     'namespace': 'hall5',
                     'redis': ['forbidden', 'bi', 'rank', 'paydata', 'mix', 'keymap', 'replay', 'dizhu', 'online',
                               'table', 'geo', 'friend', 'user'], 'type': 'HU'}]
    dbDefine = {
        "config": {
            "dbid": 3,
            "ip": "172.16.4.15",
            "port": 8003
        },
        "mysql": {},
        "redis": {
            "bi": {
                "dbid": 4,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "dizhu": {
                "dbid": 15,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "forbidden": {
                "dbid": 13,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "friend": {
                "dbid": 2,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "geo": {
                "dbid": 6,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "keymap": {
                "dbid": 5,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "mix": {
                "dbid": 1,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "online": {
                "dbid": 6,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "paydata": {
                "dbid": 3,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "rank": {
                "dbid": 9,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "replay": {
                "dbid": 14,
                "ip": "172.16.4.15",
                "port": 8004
            },
            "table": [
                {
                    "dbid": 11,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 12,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 11,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 12,
                    "ip": "172.16.4.15",
                    "port": 8004
                }
            ],
            "user": [
                {
                    "dbid": 7,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 8,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 7,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 8,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 7,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 8,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 7,
                    "ip": "172.16.4.15",
                    "port": 8004
                },
                {
                    "dbid": 8,
                    "ip": "172.16.4.15",
                    "port": 8004
                }
            ]
        }
    }
    #模拟gdata
    getdata = mock.Mock()

    def side_effect(arg):
        if arg == "ft:servers:hall5":
            return serverDefine
        if arg == "ft:db":
            return dbDefine
        return None

    getdata.side_effect = side_effect

    #模拟sendToUser
    def send_to_user(user_id,msg):
        print user_id,msg

    patcher4 = patch('tuyoo5.core.tyrpcconn.sendToUser')
    MockClass4 = patcher4.start()
    MockClass4.side_effect = send_to_user
    # MockClass4.return_value = DEFAULT

    #模拟外部依赖的RPC
    # https://erikzaadi.com/2012/07/03/mocking-python-imports/
    # http://www.voidspace.org.uk/python/mock/examples.html#mocking-imports-with-patch-dict
    rcp_mock = MagicMock()
    rcp_mock._search_user_by_id.return_value = None
    rcp_mock._check_friend.return_value = 1
    rcp_mock.get_online_state.return_value = 1
    rcp_mock.get_user_last_time.return_value = 1,2
    modules = {
        'chat.entity.rpc_adapter': rcp_mock
    }

    module_patcher = patch.dict('sys.modules', modules)
    module_patcher.start()

    with mock.patch('freetime5._tyserver._config.ftconfig.getData', getdata):
        tyinit._initializeStatic(server_id, namespace)
        tyinit._initializeServer(["ft:servers:%s" % namespace], None)
        tyinit._initializeDataBase(["ft:db"], None)
        print "init ...."

def init():
    """
    启动模拟环境.
    """
    ftglobal.gameId = 9993
    # 初始化环境基础变量
    server_id, mn_port, conf_ip, conf_port, conf_dbid, namespace = "HU9999000001", 8400, "172.16.4.15", 8003, 3, \
                                                                   "hall5"
    ftcore.runOnce(_initSafe, server_id, mn_port, conf_ip, int(conf_port), int(conf_dbid), namespace, None)
    #延迟运行测试用例
    ftcore.runOnceDelay(5,testcase0)
    ftcore.mainloop()

def testcase3():

    from chat.plugins.srvutil.srvutil import ChatListSrv
    manager = ChatListSrv()
    manager.initPluginBefore()

    #
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('get_chat_record')
    msg.setParam('userId', 10000)
    msg.setParam('gameId', 9993)
    msg.setParam('targetUserIds', [10001,10002])
    # manager.get_chat_record(msg)

    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('get_chat_record')
    msg.setParam('userId', 10000)
    msg.setParam('gameId', 9993)
    msg.setParam('targetUserId', 10001)
    msg.setParam('messageIds', ["10000-10001-1520936376549", "10000-10001-1520936376563"])
    # manager.sync_chat_record(msg)

    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('get_chat_record')
    msg.setParam('userId', 10000)
    msg.setParam('gameId', 9993)
    msg.setParam('targetUserIds', [10001,10002])
    # msg.setParam('messageIds', ["10000-10001-1520936376549", "10000-10002-1520936395127"])
    msg.setParam('messageIds', ["10000-10002-1521080812354", "10000-10002-1521080812354"])
    manager.get_next_chat_record(msg)



def testcase2():
    from chat.plugins.srvgame.srvgame import ChatGameSrv
    manager = ChatGameSrv()
    manager.initPluginBefore()

    #再来一局
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('again_game')
    msg.setParam('userId', 10000)
    msg.setParam('gameId', 9993)
    msg.setParam('targetUserId', 10001)
    msg.setParam('miniGameId', 6033)
    manager.again_game(msg)

    #再来一局应答
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('answer_again_game')
    msg.setParam('userId', 10000)
    msg.setParam('gameId', 9993)
    msg.setParam('targetUserId', 10001)
    msg.setParam('msgId', "10000-10001-1520866806727")
    msg.setParam('code', "accept")
    # manager.answer_again_game(msg)

    # 换个游戏
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('change_game')
    msg.setParam('userId', 10000)
    msg.setParam('gameId', 9993)
    msg.setParam('targetUserId', 10001)
    # manager.change_game(msg)

    # 上传游戏结果
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('send_message')
    msg.setResult('userId_a', 10000)
    msg.setResult('userId_b', 10001)
    # msg.setResult('table_msgId', -1)
    msg.setResult('table_msgId', "10000-10001-1520866161801")
    msg.setResult('gameId', 6033)
    msg.setResult('winnerId', 10000)
    # manager.doReportGameResult(msg)


def testcase0():
    # check_friend=0后需要创建通道
    from chat.plugins.srvchat.srvchat import ChatSrv

    manager = ChatSrv()
    manager.initPluginBefore()
    # 创建通道
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('create_channel')
    msg.setParam('userId', 10000)
    msg.setParam('targetUserId', 10002)
    msg.setParam('gameId', 9993)
    manager.create_channel(msg)
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('create_channel')
    msg.setParam('userId', 10002)
    msg.setParam('targetUserId', 10000)
    msg.setParam('gameId', 9993)
    manager.create_channel(msg)


    # 聊天
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('send_message')
    msg.setParam('userId', 10000)
    msg.setParam('gameId', 9993)
    msg.setParam('msgType', 0)
    msg.setParam('targetUserId', 10002)
    msg.setParam('sn', 1)
    msg.setParam('content', '{"text":"hello"}')
    # manager.talk_message2(msg)

    # 游戏邀请
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('send_message')
    msg.setParam('userId', 10000)
    msg.setParam('targetUserId', 10002)
    msg.setParam('gameId', 9993)
    msg.setParam('msgType', 2)
    msg.setParam('sn', 2)
    msg.setParam('content', '{"miniGameId":"6033","code":"invite"}')
    # manager.talk_message(msg)

    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('send_message')
    msg.setParam('userId', 10000)
    msg.setParam('targetUserId', 10002)
    msg.setParam('gameId', 9993)
    msg.setParam('msgType', 2)
    msg.setParam('sn', 1)
    # msg.setParam('content', '{"msgId":"6033","code":"accept"}')
    msg.setParam('content', '{"msgId":"10000-10002-1521538955919","code":"refuse"}')
    manager.talk_message(msg)

    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('leave_channel')
    msg.setParam('userId', 10000)
    msg.setParam('targetUserId', 10002)
    msg.setParam('gameId', 9993)
    # manager.leave_channel(msg)





def testcase1():
    from chat.plugins.srvchat.srvchat import ChatSrv

    manager = ChatSrv()
    manager.initPluginBefore()
    #check_friend=0后需要创建通道
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('create_channel')
    msg.setParam('userId', 10000)
    msg.setParam('targetUserId', 10002)
    msg.setParam('gameId', 9993)
    manager.create_channel(msg)
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('create_channel')
    msg.setParam('userId', 10002)
    msg.setParam('targetUserId', 10000)
    msg.setParam('gameId', 9993)
    manager.create_channel(msg)


    # 聊天
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('send_message')
    msg.setParam('userId', 10000)
    msg.setParam('gameId', 9993)
    msg.setParam('msgType', 0)
    msg.setParam('targetUserId', 10002)
    msg.setParam('sn', 1)
    msg.setParam('content', '{"text":"hello"}')
    manager.talk_message(msg)

    # 游戏邀请消息
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('send_message')
    msg.setParam('userId', 10000)
    msg.setParam('targetUserId', 10002)
    msg.setParam('gameId', 9993)
    msg.setParam('msgType', 2)
    msg.setParam('sn', 1)
    msg.setParam('content', '{"miniGameId":"6033","code":"invite"}')
    # manager.talk_message(msg)

    # 应答游戏消息
    msg = MsgPack()
    msg.setCmd('chat')
    msg.setAction('send_message')
    msg.setParam('userId', 10000)
    msg.setParam('targetUserId', 10001)
    msg.setParam('gameId', 9993)
    msg.setParam('msgType', 3)
    msg.setParam('sn', 1)
    # msg.setParam('content', '{"msgId":"6033","code":"accept"}')
    msg.setParam('content', '{"msgId":"10000-10002-1521538908717","code":"refuse"}')
    manager.talk_message(msg)





if __name__ == '__main__':
    init()

