# -*- coding: utf-8 -*-
'''
Created on 2016年11月26日

@author: zqh
'''
from freetime5.util import ftlog, ftstr
from tuyoo5.core import typlugin, tyconfig
from tuyoo5.core.typlugin import pluginCross


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class HallPluginOnline(typlugin.TYPlugin):

    @typlugin.markPluginEntry(export=1)
    def doBindUser(self, userId, gameId, intClientId):
        '''
        用户TCP连接建立，绑定用户，检查loc状态，返回是否需要断线重连以及重连的loc信息
        '''
        truelocs, onTableIds = pluginCross.onlinedata.checkUserLoc(userId, intClientId, 0)
        deltaChips = self.recoverUserTableChips(userId, onTableIds, intClientId)
        return truelocs, deltaChips

    def recoverUserTableChips(self, userId, onTableIds, intClientId):
        deltaChips = 0
        try:
            tableChips = pluginCross.halldata.getTableChipDict(userId)
            ftlog.debug('recoverUserTableChips->tableChips=', tableChips, 'onTableIds=', onTableIds)
            delTablesIds = []
            for tableId, tchip in tableChips.iteritems():
                tableId, tchip = ftstr.parseInts(tableId, tchip)
                if tableId in onTableIds:
                    # the user is on the table, do not clear
                    pass
                else:
                    if tchip > 0:
                        troomId = tableId / tyconfig.MAX_TABLE_ID
                        gameId = troomId / tyconfig.MAX_ROOM_ID / tyconfig.MAX_ROOM_ID / tyconfig.MAX_CONFIG_ID
                        ftlog.info('recoverUserTableChips->userId=', userId, 'gameId=', gameId, 'troomId=', troomId, 'tableId=', tableId, 'tchip=', tchip)
                        _, _, delta = pluginCross.halldata.moveAllTableChipToChip(userId, gameId, 'TABLE_TCHIP_TO_CHIP', troomId, intClientId, tableId)
                        deltaChips += delta
                    delTablesIds.append(tableId)

            if delTablesIds:
                ftlog.info('recoverUserTableChips->delTableChips=', userId, 'delTablesIds=', delTablesIds)
                pluginCross.halldata.delTableChips(userId, delTablesIds)
        except:
            ftlog.error()
        return deltaChips
