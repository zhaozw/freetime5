# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''

class MUserLeaveReason(object):
    """
    用户离开牌桌的原因
    """
    
    # 自建桌房主离开
    FRIEND_TABLE_OWNER_LEAVE = 'friendTableOwnerLeave'
    
    # 自建桌玩家离开
    FRIEND_TABLE_PLAYER_LEAVE = 'friendTablePlayerLeave'
    
    # 自建桌准备时间超时
    READY_TIME_OUT = 'readyTimeOut'
    
    # 自建桌游戏结束
    GAME_OVER = 'gameOver'
    
    # 长时间无操作超时
    NO_OPTION_TIME_OUT = 'noOptionTimeOut'
    
    # 自建桌解散
    FRIEND_TABLE_DISSOLVE = 'friendTableDissolve'
    
    # 金币桌托管离开
    AUTO_DECIDE = 'autoDecide'
    
    # 金币不足
    CHIP_NOT_ENOUGH = 'chipNotEnough'
    
    # 金币超出
    CHIP_MORE_THAN_MAX = 'chipMoreThanMax'
    
    # 机器人
    IS_ROBOT = 'isRobot'
    
    # 认输
    IS_CONFIRM_LOOSE = 'isConfirmLoose'
    
    # 用户手点离开
    LEAVE = 'leave'
    
    # 金币场未准备超时踢出
    NORMAL_READY_TIME_OUT = 'normalReadyTimeOut'
    
    # 管理工具踢出
    TABLE_MANAGE = 'doTableManage'
    
    # 牌桌出现错误
    TABLE_CALL_ERROR = 'tableCallErr'
    
    # 金币桌牌桌结束
    COIN_TABLE_FINISH = 'coinTableFinish'

    # 停服准备
    SERVER_SHUTDOWN = 'serverShutdown'
    
    def __init__(self):
        super(MUserLeaveReason, self).__init__()
