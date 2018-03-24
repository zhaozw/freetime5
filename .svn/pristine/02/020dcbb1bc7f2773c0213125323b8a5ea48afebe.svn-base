# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh
'''
import re

from freetime5.util import ftlog
from tuyoo5.core import typlugin, tyglobal
from tuyoo5.core.typlugin import pluginCross

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class Mj2PluginSrvHttp(typlugin.TYPlugin):

    def __init__(self):
        super(Mj2PluginSrvHttp, self).__init__()

    def destoryPlugin(self):
        pass

    @typlugin.markPluginEntry(initBeforeConfig=[tyglobal.SRV_TYPE_GAME_HTTP])
    def initPluginBefore(self):
        pass

    def _passThis(self):
        """ 判断这个请求是否需要被屏蔽
        """
        # 不能在线上和仿真服使用
        if tyglobal.mode() not in [tyglobal.RUN_MODE_RICH_TEST, tyglobal.RUN_MODE_TINY_TEST]:
            return False
        return True

    def putTiles(self, request):
        if not self._passThis():
            return {'info': 'can not use this tool !', 'code': 1}

        play_mode = request.getParamStr('play_mode')
        seat1 = request.getParamStr('seat1', '')
        seat2 = request.getParamStr('seat2', '')
        seat3 = request.getParamStr('seat3', '')
        seat4 = request.getParamStr('seat4', '')
        jing = request.getParamStr('jing', '')
        laizi = request.getParamStr('laizi', '')
        pool = request.getParamStr('pool')
        ftlog.debug('play_mode =', play_mode, 'seat1 =', seat1, 'seat2 =', seat2, 'seat3 =', seat3,
                    'seat4 =', seat4, 'jing=', jing, 'laizi=', laizi, 'pool =', pool, caller=self)

        tile_info = {
            'seat1':       self._splitTiles(seat1),
            'seat2':       self._splitTiles(seat2),
            'seat3':       self._splitTiles(seat3),
            'seat4':       self._splitTiles(seat4),
            'jing':        self._splitTiles(jing),
            'pool':        self._splitTiles(pool),
            'laizi':       self._splitTiles(laizi)
        }
        pluginCross.mj2dao.setPutCard(play_mode, tile_info)
        return {'info': 'ok', 'code': 0}

    def _splitTiles(self, tiles_str):
        """ 解析牌
        """
        tiles = []
        tiles_list = re.split(',|;| |\\t', tiles_str)
        for tile in tiles_list:
            try:
                t = int(tile)
                if t > 48:
                    continue
                tiles.append(t)
            except:
                pass
        return tiles

    def cancelPutTiles(self, request):
        """ 撤销摆牌
        """
        if not self._passThis():
            return {'info': 'fuck you!', 'code': 1}

        play_mode = request.getParamStr('play_mode')
        pluginCross.mj2dao.delPutCard(play_mode)
        return {'info': 'ok', 'code': 0}
