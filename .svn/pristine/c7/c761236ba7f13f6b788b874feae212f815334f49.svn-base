# coding:utf-8
import json

from freetime5.util import ftlog
from freetime5.util.ftmsg import MsgPack
from tuyoo5.core import tyrpcconn
from tuyoo5.core.typlugin import pluginCross


class MJCreateTableRecord(object):
    """自建桌战绩
    """
    _user_record_count = 20  # 一个用户最多存储的数据

    @classmethod
    def initialize(cls):
        return

    @classmethod
    def saveTableRecord(cls, tableRecordInfo, gameId):
        # add by taoxc
        ftlog.debug('createTableRecord.saveTableRecord tableRecordInfo:', tableRecordInfo, 'gameId:', gameId)
        # 保存用户数据
        for userId, playerRecordInfo in tableRecordInfo.items():
            # 通过recordKey获取当前玩家的战绩记录数据，如果超过最大存储则进行删除处理(同时删除对应的内容)
            userRecordKeys = pluginCross.mj2dao.getRecordKeyList(userId)

            if len(userRecordKeys) >= cls._user_record_count:
                # 删除最早的记录(附带删除内容)
                lastestKey = userRecordKeys.pop(0)
                pluginCross.mj2dao.removeReplayRecord(lastestKey)
                ftlog.debug('createTableRecord.saveTableRecord recordKey len > ', cls._user_record_count, ' delete key:', lastestKey)

            # 保存内容
            recordContentKey = pluginCross.mj2dao.setReplayRecord(userId, playerRecordInfo)
            # 保存KEY
            userRecordKeys.append(recordContentKey)
            pluginCross.mj2dao.setRecordKeyList(userId, userRecordKeys)
            ftlog.debug('createTableRecord.saveTableRecord save keys:', userRecordKeys, ' save content:', playerRecordInfo)

    @classmethod
    def sendAllRecordToUser(cls, userId, gameId, startRecordIndex, endRecordIndex):
        # 全量下发 带分页参数
        cls._sendAllRecordToUser(userId, gameId, startRecordIndex, endRecordIndex)

    @classmethod
    def _sendAllRecordToUser(cls
                             , userId
                             , gameId
                             , startRecordIndex
                             , endRecordIndex
                             , playMode=None
                             , targetUserId=None
                             , targetTableNo=None
                             ):
        """全量下发 带分页参数
        """
        # 获取keys
        if targetUserId is None:
            targetUserId = userId
        if startRecordIndex < 0:
            startRecordIndex = 0
        if endRecordIndex < startRecordIndex:
            endRecordIndex = startRecordIndex

        userRecordKeys = pluginCross.mj2dao.getRecordKeyList(targetUserId)
        rLength = len(userRecordKeys)
        urKeys = []
        for index in range(startRecordIndex, endRecordIndex + 1):
            newIndex = rLength - index - 1
            if newIndex >= 0:
                urKeys.append(userRecordKeys[rLength - index - 1])
        ftlog.debug('createTableRecord.sendAllRecordToUser2 urKeys:', urKeys)

        msg = MsgPack()
        msg.setCmd('create_table')
        msg.setResult('action', 'record')
        msg.setResult('type', 'update')
        msg.setResult('gameId', gameId)
        playerRecordList = []
        for userRecordKey in urKeys:
            playerRecordInfo = pluginCross.mj2dao.getReplayRecord(userRecordKey)
            if not playerRecordInfo:
                ftlog.warn('createTableRecord.sendAllRecordToUser2 key:', userRecordKey, ' is null')
            else:
                playerRecordDist = json.loads(playerRecordInfo)

                # playMode过滤
                if playMode and playMode != playerRecordDist.get('playMode'):
                    continue
                # 房间号过滤
                if targetTableNo and targetTableNo != playerRecordDist.get('tableNo'):
                    continue

                playerRecordList.append(playerRecordDist)
                ftlog.debug('createTableRecord.sendAllRecordToUser2 key:', userRecordKey, ' content:', playerRecordDist)
        msg.setResult('list', playerRecordList)
        tyrpcconn.sendToUser(userId, msg)

    @classmethod
    def sendAllRecordToUserForCustomer(cls
                                       , userId
                                       , gameId
                                       , playMode
                                       , targetUserId
                                       , targetTableNo
                                       , startRecordIndex
                                       , endRecordIndex):
        """查询他人的牌局记录，内部使用
        """
        cls._sendAllRecordToUser(userId
                                 , gameId
                                 , startRecordIndex
                                 , endRecordIndex
                                 , playMode
                                 , targetUserId
                                 , targetTableNo)
