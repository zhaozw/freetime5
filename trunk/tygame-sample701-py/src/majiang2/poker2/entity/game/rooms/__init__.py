# coding=UTF-8
from freetime5.util import ftclass


tyRoomConst = ftclass.BaseConst()

tyRoomConst.ROOM_TYPE_NAME_NORMAL = 'normal'  # 普通非队列房间
tyRoomConst.ROOM_TYPE_NAME_QUEUE = 'queue'  # 队列房间
tyRoomConst.ROOM_TYPE_NAME_VIP = 'vip'  # 贵宾室房间
tyRoomConst.ROOM_TYPE_NAME_LTS = 'lts'  # 限时积分赛房间
tyRoomConst.ROOM_TYPE_NAME_SNG = 'sng'  # S&G 比赛房间
tyRoomConst.ROOM_TYPE_NAME_MTT = 'mtt'  # MTT 比赛房间
tyRoomConst.ROOM_TYPE_NAME_HUNDREDS = 'hundreds'  # 百人房间
tyRoomConst.ROOM_TYPE_NAME_DTG = 'dtg'  # 打通关房间
tyRoomConst.ROOM_TYPE_NAME_CUSTOM = 'custom'  # 自建房间
tyRoomConst.ROOM_TYPE_NAME_SCORE_MATCH = 'score_match'  # 积分赛房间
tyRoomConst.ROOM_TYPE_NAME_BIG_MATCH = 'big_match'  # 大比赛房间
tyRoomConst.ROOM_TYPE_NAME_ARENA_MATCH = 'arena_match'
tyRoomConst.ROOM_TYPE_NAME_GROUP_MATCH = 'group_match'
tyRoomConst.ROOM_TYPE_NAME_ERDAYI_MATCH = 'erdayi_match'
tyRoomConst.ROOM_TYPE_NAME_PK = 'pk'  # 好友pk
tyRoomConst.ROOM_TYPE_NAME_CHIP_NORMAL = 'chip_normal'
'''
休闲赛(一天内某个时间段，任意打N局, minN<=N<=maxN)，且遇到过的玩家当天本比赛内将不能再组局,
比赛过程中，每局胜利或者和局，会得到配置的积分N-(chip.base)
排名规则：可由自己游戏实现
'''
tyRoomConst.ROOM_TYPE_NAME_RELAXATION_MATCH = 'relaxation_match'
