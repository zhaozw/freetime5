# -*- coding:utf-8 -*-
'''
Created on 2017年10月13日

比赛统计上报

@author: zhaol

'''
from freetime5.util import ftlog


class PokerMatchReport(object):

    def __init__(self):
        pass

    @classmethod
    def reportMatchEvent(cls, eventId, userId, gameId, matchId, tableId, roundId, score,cardList=None):
        try:
            # if TYPlayer.isRobot(userId):
            #     return
            pass
            # finalTableChip = 0
            # finalUserChip = userchip.getChip(userId)
            # clientId = sessiondata.getClientId(userId)
            # cardList = cardList if cardList is not None else []
            # bireport.reportGameEvent(eventId, userId, gameId, matchId, tableId, roundId, score,
            #                          0, 0, cardList, clientId, finalTableChip, finalUserChip)
            # ftlog.debug('PokerMatchReport.eventId=', eventId
            #             , ' userId=', userId
            #             , ' gameId=', gameId
            #             , ' matchId=', matchId
            #             , ' tableId=', tableId
            #             , ' roundId=', roundId
            #             , ' detalChip=', score
            #             )
        except:
            ftlog.error('PokerMatchReport.reportMatchEvent exception eventId=', eventId
                        , 'userId=', userId
                        , 'gameId=', gameId)


if __name__ == "__main__":
    pass