'''
Created on 2017年10月27日

@author: zqh
'''
from tuyoo5.core.typlugin import hallRpcOne
from tuyoo5.core import tyrpcsdk
from tuyoo5.core.tyrpchall import UserKeys


def getAssets(userId, assetKindId):
    count = hallRpcOne.hallitem.getAssets(userId, assetKindId).getResult()
    return count


def consumeAsset(userId, gameId, assetKindId, count, eventId, intEventParam):
    kindId, consumeCount, final = hallRpcOne.hallitem.consumeAsset(userId,
                                                                   gameId,
                                                                   assetKindId,
                                                                   count,
                                                                   eventId,
                                                                   intEventParam).getResult()
    return kindId, consumeCount, final


def addAsset(userId, gameId, assetKindId,  count, eventId, roomId):
    kindId, addCount, final = hallRpcOne.hallitem.addAsset(userId,
                                                           gameId,
                                                           assetKindId,
                                                           count,
                                                           eventId,
                                                           roomId).getResult()
    return kindId, addCount, final


def addAssets(userId, gameId, contentItems, eventId, intEventParam):
    aslist = hallRpcOne.hallitem.addAssets(userId,
                                           gameId,
                                           contentItems,
                                           eventId,
                                           intEventParam).getResult()
    return aslist


def getTableChip(userId, gameId, tableId):
    chip = hallRpcOne.halldata.getTableChip(userId, gameId, tableId).getResult()
    return chip


def getChip(userId):
    chip = hallRpcOne.halldata.getUserChip(userId).getResult()
    return chip


def incrChip(userId, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam):
    chip = hallRpcOne.halldata.incrChip(userId,
                                        gameid,
                                        deltaCount,
                                        chipNotEnoughOpMode,
                                        eventId,
                                        intEventParam).getResult()
    return chip


def incrTableChip(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId, tableId):
    trueDelta, finalCount = hallRpcOne.halldata.incrTableChip(uid,
                                                              gameid,
                                                              deltaCount,
                                                              chipNotEnoughOpMode,
                                                              eventId,
                                                              intEventParam,
                                                              clientId,
                                                              tableId).getResult()
    return trueDelta, finalCount


def setTableChipToN(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId):
    tfinal, final, delta = hallRpcOne.halldata.setTableChipToN(uid,
                                                               gameid,
                                                               tablechip,
                                                               eventId,
                                                               intEventParam,
                                                               clientId,
                                                               tableId).getResult()
    return tfinal, final, delta


def moveAllTableChipToChip(uid, gameid, eventId, intEventParam, clientId, tableId):
    tfinal, final, delta = hallRpcOne.halldata.moveAllTableChipToChip(uid,
                                                                      gameid,
                                                                      eventId,
                                                                      intEventParam,
                                                                      clientId,
                                                                      tableId).getResult()
    return tfinal, final, delta


def delTableChips(uid, tableIdList):
    ret = hallRpcOne.halldata.delTableChips(uid, tableIdList).getResult()
    return ret


_UserBaseAttrs = ','.join([UserKeys.ATT_NAME, UserKeys.ATT_PURL, UserKeys.ATT_SEX])


def getUserBaseInfo(userId):
    datas = tyrpcsdk.getUserDatas(userId, _UserBaseAttrs)
    name = datas.get(UserKeys.ATT_NAME, 'error name')
    purl = datas.get(UserKeys.ATT_PURL, '')
    sex = datas.get(UserKeys.ATT_SEX, 0)
    return name, purl, sex


def sendDataChangeNotify(userId, gameId, changedList):
    hallRpcOne.halldatanotify.sendDataChangeNotify(userId, gameId, changedList)
