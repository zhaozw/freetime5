# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh

对应GH进程, 基本上为 http api 入口
'''

from freetime5.util import ftlog
from tuyoo5.core import typlugin, tyglobal
from freetime5.util import ftlog

from tuyoo5.core.typlugin import hallRpcOne
from tuyoo5.core.tyrpchall import ChipNotEnoughOpMode

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class PopStarHttp(typlugin.TYPlugin):

    def __init__(self):
        super(PopStarHttp, self).__init__()

    def destoryPlugin(self):
        super(PopStarHttp, self).destoryPlugin()

    # @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_HTTP])
    # def initPluginBefore(self):
    #     super(SingleGameSrv, self).initPluginBefore()

    @typlugin.markPluginEntry(httppath='consumechip')
    def do_consume_chip(self, request):
        if _DEBUG:
            ftlog.info("_PopStarHttp : do_consume_chip : request = ", request)
        userId = int(request.getParamStr('userId'))
        dec_chip = abs(int(request.getParamStr('chipNum')))

        #dec user chip
        hallRpcOne.halldata.incrChip(userId, tyglobal.gameId(), -dec_chip, ChipNotEnoughOpMode.NOOP, 'POPSTAR_GAME_CONSUME_CHIP', 0)

        return {request.path: 'ok'}

    # @typlugin.markPluginEntry(httppath='/api5/xuezhan/admin/cancel_put_tiles')
    # def cancelPutTiles(self, request):
    #     return super(Mj2XueZhanPluginSrvHttp, self).cancelPutTiles(request)

