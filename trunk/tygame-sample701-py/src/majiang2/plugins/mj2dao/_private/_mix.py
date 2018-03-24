# -*- coding: utf-8 -*-
"""
大厅的基础业务数据
"""


from freetime5.util import ftlog
from freetime5._tyserver._dao._dataattrs import DataAttrInt, DataAttrObjDict
from freetime5._tyserver._dao._dataschema_str import DataSchemaString


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class DaoMjMixRoundId(DataSchemaString):

    DBNAME = 'mix'
    MAINKEY = 'dummy-DaoMjMixRoundId'
    SUBVALDEF = DataAttrInt('dummy-DaoMjMixRoundId', 0)

    @classmethod
    def getMainKey(cls, _cIndex, _mainKeyExt=None):
        return _mainKeyExt

    @classmethod
    def incrMajiang2RoundId(cls):
        return cls.INCRBY(0, 1, 'majiang2_round_id')


class DaoMjMixPutCard(DataSchemaString):

    DBNAME = 'mix'
    MAINKEY = 'dummy-DaoMjMixPutCard'
    SUBVALDEF = DataAttrObjDict('dummy-DaoMjMixPutCard', {}, 4012)

    @classmethod
    def getMainKey(cls, _cIndex, _mainKeyExt=None):
        return _mainKeyExt

    @classmethod
    def setPutCard(cls, playMode, cards):
        return cls.SET(0, cards, 'put_card:' + playMode)

    @classmethod
    def getPutCard(cls, playMode):
        return cls.GET(0, 'put_card:' + playMode)

    @classmethod
    def delPutCard(cls, playMode):
        return cls.DEL(0, 'put_card:' + playMode)
