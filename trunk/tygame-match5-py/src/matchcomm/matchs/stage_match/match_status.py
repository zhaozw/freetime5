# -*- coding:utf-8 -*-
"""
Created on 2017年8月14日

@author: zhaojiangang
"""
import json

import matchcomm.matchs.dao as basedao
from freetime5.util import ftlog


class StageMatchStatus(object):
    def __init__(self, matchId, seq=None, startTime=None):
        # 赛事ID
        self.matchId = matchId
        # 当前比赛序号
        self.seq = seq
        # 开赛时间，如果为None表示人满开赛
        self.startTime = startTime

    @property
    def instId(self):
        return '%s.%s' % (self.matchId, self.seq)


class StageMatchStatusDao(object):
    def load(self, gameId, matchId):
        """
        加载赛事状态
        """
        pass

    def save(self, gameId, status):
        """
        保存赛事状态
        """
        pass


class StageMatchStatusDaoRedis(StageMatchStatusDao):
    def load(self, gameId, matchId):
        """
        加载赛事状态
        """
        jstr = basedao.getMatchStatus(gameId, matchId)
        if jstr:
            d = json.loads(jstr)
            return StageMatchStatus(matchId, d['seq'], d['startTime'])
        return None

    def save(self, gameId, status):
        """
        保存赛事状态
        """
        try:
            d = {'seq': status.seq, 'startTime': status.startTime}
            jstr = json.dumps(d)
            basedao.saveMatchStatus(gameId, status.matchId, jstr)
        except:
            ftlog.error('StageMatchStatusDaoRedis.save',
                        'matchId=', status.matchId,
                        'seq=', status.seq,
                        'startTime=', status.startTime)
