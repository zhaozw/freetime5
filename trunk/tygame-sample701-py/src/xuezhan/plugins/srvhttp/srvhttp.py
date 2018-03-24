# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh

对应GH进程, 基本上为 http api 入口
'''

from freetime5.util import ftlog
from majiang2.plugins.srvhttp.srvhttp import Mj2PluginSrvHttp
from tuyoo5.core import typlugin, tyglobal


_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2XueZhanPluginSrvHttp(Mj2PluginSrvHttp):

    def __init__(self):
        super(Mj2XueZhanPluginSrvHttp, self).__init__()

    def destoryPlugin(self):
        super(Mj2XueZhanPluginSrvHttp, self).destoryPlugin()

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_HTTP])
    def initPluginBefore(self):
        super(Mj2XueZhanPluginSrvHttp, self).initPluginBefore()

    @typlugin.markPluginEntry(httppath='/api5/xuezhan/admin/put_tiles')
    def putTiles(self, request):
        return super(Mj2XueZhanPluginSrvHttp, self).putTiles(request)

    @typlugin.markPluginEntry(httppath='/api5/xuezhan/admin/cancel_put_tiles')
    def cancelPutTiles(self, request):
        return super(Mj2XueZhanPluginSrvHttp, self).cancelPutTiles(request)

#     @typlugin.markPluginEntry(httppath='/api5/xuezhan/clear_table')
#     def clearTable(self, request):
#         roomId = request.getParamInt('roomId')
#         tableId = request.getParamInt('tableId')
#         ftlog.debug('MJAdmin.clearTable roomId:', roomId, ' tableId:', tableId)
# 
#         mo = MsgPack()
#         mo.setCmd('table_manage')
#         mo.setAction('clear_table')
#         mo.setParam('roomId', roomId)
#         mo.setParam('tableId', tableId)
#         router.sendTableServer(mo, roomId)
#         return {'info': 'ok', 'code': 0}
# 
#     @typlugin.markPluginEntry(httppath='/api5/xuezhan/kick_user')
#     def kickUser(self, request):
#         roomId = request.getParamInt('roomId')
#         tableId = request.getParamInt('tableId')
#         userId = request.getParamInt('userId')
#         ftlog.debug('MJAdmin.kickUser roomId:', roomId, ' tableId:', tableId, ' userId:', userId)
# 
#         mo = MsgPack()
#         mo.setCmd('table_manage')
#         mo.setAction('leave')
#         mo.setParam('roomId', roomId)
#         mo.setParam('tableId', tableId)
#         mo.setParam('userId', userId)
#         router.sendTableServer(mo, roomId)
#         return {'info': 'ok', 'code': 0}
# 
#     @typlugin.markPluginEntry(httppath='/api5/xuezhan/power_test')
#     def powerTest(self, request):
#         userId = request.getParamInt('userId')
#         ftlog.debug('MJAdmin.powerTest userId:', userId)
#         roomId, checkResult = MajiangCreateTable._chooseCreateRoom(userId, GAMEID, 'xuezhan', 4)
#         ftlog.debug('MajiangCreateTable._chooseCreateRoom roomId:', roomId, ' checkResult:', checkResult)
#         msg = MsgPack()
#         msg.setCmdAction("room", "create_table")
#         msg.setParam("roomId", roomId)
#         msg.setParam("gameId", GAMEID)
#         msg.setParam("userId", userId)
#         msg.setParam("itemParams", {"sanQiBian": 1, "playerType": 3, "cardCount": 1, "chunJia": 0, "guaDaFeng": 0, "hongZhongBao": 0})
#         msg.setParam('needFangka', 0)
#         ftlog.debug('MajiangCreateTable._chooseCreateRoom send message to room:', msg)
# 
#         router.sendRoomServer(msg, roomId)
#         return {'info': 'ok', 'code': 0}
# 
#     @typlugin.markPluginEntry(httppath='/api5/xuezhan/check_table_tiles')
#     def checkTableTiles(self, request):
#         roomId = request.getParamInt('roomId')
#         tableId = request.getParamInt('tableId')
#         ftlog.debug('MJAdmin.checkTableTiles roomId:', roomId, ' tableId:', tableId)
# 
#         mo = MsgPack()
#         mo.setCmd('table_manage')
#         mo.setAction('tableTiles')
#         mo.setParam('roomId', roomId)
#         mo.setParam('tableId', tableId)
#         router.sendTableServer(mo, roomId)
#         return {'info': 'ok', 'code': 0}
