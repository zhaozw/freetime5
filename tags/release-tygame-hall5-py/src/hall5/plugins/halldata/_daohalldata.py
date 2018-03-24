# -*- coding: utf-8 -*-
"""
大厅的基础业务数据
"""

from freetime5.util import ftlog
from freetime5.util import fttime
from tuyoo5.core.tyconst import HALL_GAMEID
from tuyoo5.core.tydao import DataSchemaHashAttrs
from tuyoo5.core.tyrpchall import ChipNotEnoughOpMode
from tuyoo5.core.tyrpchall import HallKeys


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class DaoGameDataHall(DataSchemaHashAttrs):
    DBNAME = 'user'
    MAINKEY = 'gamedata:%s:%s' % (HALL_GAMEID, '%s')
    ATTS = HallKeys

    @classmethod
    def checkAndInit(cls, userId):
        '''
        若数据字段小于3项，认为没有数据或丢失，重新建立数据
        '''
        if cls.HLEN(userId) < 4:
            attDataDict = {}
            ct = fttime.formatTimeMs()
            attDataDict[HallKeys.ATT_CREATE_TIME] = ct
            attDataDict[HallKeys.ATT_AUTHOR_TIME] = ct
            attDataDict[HallKeys.ATT_OFFLINE_TIME] = ct
            attDataDict[HallKeys.ATT_ALIVE_TIME] = ct
            attDataDict[HallKeys.ATT_DATA_VERSION] = 5.1
            # attDataDict[HallKeys.ATT_FIRST_GAME_LIST5] = 0 # 缺省即为0，不必初始化
            # attDataDict[HallKeys.ATT_NEW_USER] = 1
            # attDataDict[HallKeys.ATT_USER_CHIP_MOVE_GAME] = 1  # 新用户，肯定不需要进行hall37的数据升级
            cls.HMSET(userId, attDataDict)
            return True
        return False


def incrDaShiFen(userId, detalDaShiFen):
    '''
    调整用户的大师分
    '''
    _, finalCount, _ = DaoGameDataHall.HINCRBY_LIMIT(userId, HallKeys.ATT_DASHIFEN, detalDaShiFen, 0, -1,
                                                     ChipNotEnoughOpMode.CLEAR_ZERO)
    return finalCount
