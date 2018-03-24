# -*- coding: utf-8 -*-
'''
Created on 2016年7月19日

@author: zqh
'''
from tuyoo5.core.tydao import DataAttrDateTime
from tuyoo5.core.tydao import DataAttrFloat
from tuyoo5.core.tydao import DataAttrInt
from tuyoo5.core.tydao import DataAttrObjDict
from tuyoo5.core.tydao import attrsDefinedClass


@attrsDefinedClass
class MajangKeys(object):

    BIG_PATTERN_HISTORY = {u'天胡': 0, u'地胡': 0, u'清龙七对': 0,
                           u'龙七对': 0, u'七对': 0, u'清七对': 0,
                           u'将对': 0, u'清对': 0, u'对对胡': 0,
                           u'清幺九': 0, u'全幺九': 0, u'清一色': 0}

    ATT_CREATE_TIME = DataAttrDateTime('createTime', '', DataAttrDateTime.DFL_YMDHMSF)  # 当前数据库建立时间
    ATT_AUTHOR_TIME = DataAttrDateTime('authorTime', '', DataAttrDateTime.DFL_YMDHMSF)  # 当前游戏的登录时间
    ATT_OFFLINE_TIME = DataAttrDateTime('offlineTime', '', DataAttrDateTime.DFL_YMDHMSF)  # 当前游戏的退出时间
    ATT_ALIVE_TIME = DataAttrDateTime('aliveTime', '', DataAttrDateTime.DFL_YMDHMSF)  # 用户在线存活时间
    ATT_DATA_VERSION = DataAttrFloat('version', 0.0)  # 数据版本标记

    ATT_LAST_LOGIN = DataAttrInt('lastlogin', 0)
    ATT_LOGIN_SUM = DataAttrInt('loginsum', 0)
    ATT_NS_LOGIN = DataAttrInt('nslogin', 0)
    ATT_EXP = DataAttrInt('exp', 0)
    ATT_LEVEL = DataAttrInt('level', 1)
    ATT_PLAY_GAME_COUNT = DataAttrInt('play_game_count', 0)
    ATT_WIN_GAME_COUNT = DataAttrInt('win_game_count', 0)
    ATT_DRAW_GAME_COUNT = DataAttrInt('draw_game_count', 0)
    ATT_LOSE_GAME_COUNT = DataAttrInt('lose_game_count', 0)
    ATT_BANG_COUNT = DataAttrInt('bang_count', 0)
    ATT_HIGHEST_LOSE_CHIP = DataAttrInt('highest_lose_chip', 0)
    ATT_HIGHEST_WIN_CHIP = DataAttrInt('highest_win_chip', 0)
    ATT_HIGHEST_CHIP_RECORD = DataAttrInt('highest_chip_record', 0)
    ATT_DAY_WIN_GAME_COUNT = DataAttrInt('day_win_game_count', 0)
    ATT_DAY_WIN_SEQUENCE_COUNT = DataAttrInt('day_win_sequence_count', 0)
    ATT_DAY_MAX_WIN_SEQUENCE_COUNT = DataAttrInt('day_max_win_sequence_count', 0)
    ATT_BIG_PATTERN_HISTORY = DataAttrObjDict('big_pattern_history', BIG_PATTERN_HISTORY, 512)
    ATT_BEST_PATTERN = DataAttrObjDict('best_pattern', {'degree': 0, 'description': ''}, 512)
    ATT_ONLINE_RECORDS = DataAttrObjDict('online_records', {}, 512)
    ATT_WIN_SEQUENCE_COUNT = DataAttrInt('win_sequence_count', 0)
    ATT_MAX_WIN_SEQUENCE_COUNT = DataAttrInt('max_win_sequence_count', 0)
    ATT_GUOBIAO_BEST_PATTERN = DataAttrObjDict('guobiao_best_pattern', {'degree': 0, 'description': ''}, 512)
    ATT_GUOBIAO_ONLINE_RECORDS = DataAttrObjDict('guobiao_online_records', {}, 512)
    ATT_MASTER_POINT = DataAttrInt('master_point', 0)
    ATT_WEEK_MASTER_POINT = DataAttrInt('week_master_point', 0)
    ATT_WEEK_MASTER_POINT_TS = DataAttrInt('week_master_point_ts', 0)
    ATT_DAY_PLAY_GAME_COUNT = DataAttrInt('day_play_game_count', 0)
    ATT_NEW_WIN_SEQUENCE_COUNT = DataAttrInt('new_win_sequence_count', 0)
    ATT_INVITE_STATE = DataAttrInt('invite_state', 0)
    ATT_NANCHANG_BEST_PATTERN = DataAttrObjDict('nanchang_best_pattern', {'degree': 0, 'description': ''}, 512)
    ATT_NANCHANG_ONLINE_RECORDS = DataAttrObjDict('nanchang_online_records', {}, 512)
    ATT_HISTORY_WIN_STREAK = DataAttrInt('history_win_streak', 0)
    ATT_QUICK_START_COIN_TIMESTAMP = DataAttrInt('quickStartCoinTimeStamp', 0)

    ATT_LAST_TABLE_COIN = DataAttrInt('lastTableCoin', 0)  # 上一局的牌桌金币
    ATT_LAST_ROOM_ID = DataAttrInt('lastRoomId', 0)  # 上一局的roomId
    ATT_LAST_LEAVE_TIME = DataAttrInt('lastLeaveTime', 0)  # 上一局站起的时间
    ATT_HAS_GET_COUPON = DataAttrInt('WinStreakGetCoupon', 0)
