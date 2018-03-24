# -*- coding=utf-8 -*-
"""
@file  : assetkind
@date  : 2016-09-22
@author: GongXiaobo
"""

from tuyoo5.core.typlugin import pluginCross
from tuyoo5.core.tyrpchall import ChipNotEnoughOpMode
from tuyoo5.core.tyrpchall import UserKeys
from tuyoo5.plugins.item import items


class TYAssetKindChip(items.TYAssetKind):

    TYPE_ID = 'common.chip'

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, param01='', param02=''):
        '''
        @return: finalCount
        '''
        assert (count >= 0)
        _trueDelta, final = pluginCross.halldata.incrChip(userAssets.userId,
                                                          gameId,
                                                          count,
                                                          ChipNotEnoughOpMode.NOOP,
                                                          eventId,
                                                          intEventParam,
                                                          param01=param01, 
                                                          param02=param02)
        return final

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        trueDelta, final = pluginCross.halldata.incrChip(userAssets.userId,
                                                         gameId,
                                                         -count,
                                                         ChipNotEnoughOpMode.NOOP,
                                                         eventId,
                                                         intEventParam)
        return -trueDelta, final

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        trueDelta, final = pluginCross.halldata.incrChip(userAssets.userId,
                                                         gameId,
                                                         -count,
                                                         ChipNotEnoughOpMode.CLEAR_ZERO,
                                                         eventId,
                                                         intEventParam)
        return -trueDelta, final

    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pluginCross.halldata.getUserDataList(userAssets.userId, UserKeys.ATT_CHIP)


class TYAssetKindCoupon(items.TYAssetKind):

    TYPE_ID = 'common.coupon'

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, param01='', param02=''):
        '''
        @return: finalCount
        '''
        assert (count >= 0)
        _trueDelta, final = pluginCross.halldata.incrCoupon(userAssets.userId,
                                                            gameId,
                                                            count,
                                                            ChipNotEnoughOpMode.NOOP,
                                                            eventId,
                                                            intEventParam,
                                                            param01=param01, 
                                                            param02=param02)
        return final

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        trueDelta, final = pluginCross.halldata.incrCoupon(userAssets.userId,
                                                           gameId,
                                                           -count,
                                                           ChipNotEnoughOpMode.NOOP,
                                                           eventId,
                                                           intEventParam)
        return -trueDelta, final

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        trueDelta, final = pluginCross.halldata.incrCoupon(userAssets.userId,
                                                           gameId,
                                                           -count,
                                                           ChipNotEnoughOpMode.CLEAR_ZERO,
                                                           eventId,
                                                           intEventParam)
        return -trueDelta, final

    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pluginCross.halldata.getUserDataList(userAssets.userId, UserKeys.ATT_COUPON)


class TYAssetKindExp(items.TYAssetKind):

    TYPE_ID = 'common.exp'

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, param01='', param02=''):
        '''
        @return: finalCount
        '''
        assert (count >= 0)
        final = pluginCross.halldata.incrExp(userAssets.userId, count)
        return final

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        final = pluginCross.halldata.incrExp(userAssets.userId, -count)
        return count, final

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        final = pluginCross.halldata.incrExp(userAssets.userId, -count)
        return count, final

    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pluginCross.halldata.getUserDataList(userAssets.userId, UserKeys.ATT_EXP)


class TYAssetKindCharm(items.TYAssetKind):

    TYPE_ID = 'common.charm'

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, param01='', param02=''):
        '''
        @return: finalCount
        '''
        assert (count >= 0)
        final = pluginCross.halldata.incrCharm(userAssets.userId, count)
        return final

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        final = pluginCross.halldata.incrCharm(userAssets.userId, -count)
        return -count, final

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        final = pluginCross.halldata.incrCharm(userAssets.userId, -count)
        return -count, final

    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pluginCross.halldata.getUserDataList(userAssets.userId, UserKeys.ATT_CHARM)


class TYAssetKindDiamond(items.TYAssetKind):

    TYPE_ID = 'common.diamond'

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, param01='', param02=''):
        '''
        @return: finalCount
        '''
        assert (count >= 0)
        _trueDelta, final = pluginCross.halldata.incrDiamond(userAssets.userId,
                                                             gameId,
                                                             count,
                                                             ChipNotEnoughOpMode.NOOP,
                                                             eventId,
                                                             intEventParam,
                                                             None,
                                                             param01=param01,
                                                             param02=param02)
        return final

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        trueDelta, final = pluginCross.halldata.incrDiamond(userAssets.userId,
                                                            gameId,
                                                            -count,
                                                            ChipNotEnoughOpMode.NOOP,
                                                            eventId,
                                                            intEventParam,
                                                            None)
        return -trueDelta, final

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        trueDelta, final = pluginCross.halldata.incrDiamond(userAssets.userId,
                                                            gameId,
                                                            -count,
                                                            ChipNotEnoughOpMode.CLEAR_ZERO,
                                                            eventId,
                                                            intEventParam,
                                                            None)
        return -trueDelta, final

    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return pluginCross.halldata.getUserDataList(userAssets.userId, UserKeys.ATT_DIAMOND)


class TYAssetKindEntity(items.TYAssetKind):
    TYPE_ID = 'common.entity'

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, param01='', param02=''):
        assert (count >= 0)
        return 1

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        assert (count >= 0)
        return 0, 0

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        assert (count >= 0)
        return 0, 0

    def balance(self, userAssets, timestamp):
        return 0


class TYAssetKindCash(TYAssetKindEntity):
    TYPE_ID = 'common.cash'

    def buildContentForDelivery(self, count):
        intCount = int(count)
        intFmt = '%s：%s%s'
        floatFmt = '%s：%.2f%s'
        fmt = intFmt if intCount == count else floatFmt
        return fmt % (self.displayName, count, self.units)

    def buildContent(self, count, needUnits=True):
        if needUnits:
            intCount = int(count)
            intFmt = '%s%s%s'
            floatFmt = '%.2f%s%s'
            fmt = intFmt if intCount == count else floatFmt
            return fmt % (count, self.units, self.displayName)
        return '%s%s' % (count, self.displayName)


class TYAssetKindSubMember(items.TYAssetKind):

    TYPE_ID = 'common.subMember'

    def buildContentForDelivery(self, count):
        return self.displayName

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, param01='', param02=''):
        '''
        @return: finalCount
        '''
        assert (count >= 0)
        isSub = pluginCross.hallsubmember.subscribeMember(gameId,
                                                          userAssets.userId,
                                                          timestamp,
                                                          eventId,
                                                          intEventParam,
                                                          param01=param01, 
                                                          param02=param02)
        return 1 if isSub else 0

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        return 0, self.balance(userAssets, timestamp)

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        assert (count >= 0)
        return 0, self.balance(userAssets, timestamp)

    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return 1 if pluginCross.hallsubmember.isSubmember(userAssets.userId) else 0


class HallAssetKindItem(items.TYAssetKindItem):
    """
    特殊的TYAssetKind类,包装所有物品,不需要注册到AssetKindRegister
    """

    def add(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam, param01='', param02=''):
        '''
        @return: finalCount
        '''
        userBag = userAssets.getUserBag()
        items = userBag.addItemUnitsByKind(gameId,
                                           self.itemKind,
                                           count,
                                           timestamp,
                                           0,
                                           eventId,
                                           intEventParam,
                                           param01=param01,
                                           param02=param02)
        for item in items:
            item.itemKind.processWhenAdded(item,
                                           userAssets,
                                           gameId,
                                           timestamp)
        return userBag.calcTotalUnitsCount(self.itemKind)

    def consume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount, finalCount
        '''
        userBag = userAssets.getUserBag()
        consumeCount = userBag.consumeUnitsCountByKind(gameId,
                                                       self.itemKind,
                                                       count,
                                                       timestamp,
                                                       eventId,
                                                       intEventParam)
        return consumeCount, userBag.calcTotalUnitsCount(self.itemKind)

    def forceConsume(self, gameId, userAssets, kindId, count, timestamp, eventId, intEventParam):
        '''
        @return: consumeCount
        '''
        userBag = userAssets.getUserBag()
        consumeCount = userBag.forceConsumeUnitsCountByKind(gameId,
                                                            self.itemKind,
                                                            count,
                                                            timestamp,
                                                            eventId,
                                                            intEventParam)
        return consumeCount, userBag.calcTotalUnitsCount(self.itemKind)

    def balance(self, userAssets, timestamp):
        '''
        @return: balance
        '''
        return userAssets.getUserBag().calcTotalUnitsCount(self.itemKind, timestamp)
