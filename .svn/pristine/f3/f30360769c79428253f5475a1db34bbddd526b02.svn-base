# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from freetime5.util import ftlog

class MLocation(object):
    """
    描述两个座位号之间的位置关系
    """
    
    def __init__(self):
        super(MLocation, self).__init__()
        
    @classmethod
    def getLocInfo(cls, mySeatId, otherSeatId, playerCount):
        """
        是否可以吃
        吃牌的判断中，tile已经在tiles中
        参数：
            tiles - 手牌
            tile - 待吃的牌
        返回值：吃牌选择
            最多三种解
            
        例子：
            [[2, 3, 4], [3, 4, 5], [4, 5, 6
        """
        if mySeatId < 0 or mySeatId >= playerCount:
            return 'unKnown'
        if otherSeatId < 0 or otherSeatId >= playerCount:
            return 'unKnown'
        
        seatDelta = (otherSeatId + playerCount - mySeatId) % playerCount
        if playerCount == 2:
            # 对家
            # 本家
            if seatDelta == 1:
                return '对家'
            else:
                return '本家'
        if playerCount == 3:
            # 左    右
            #    我
            if seatDelta == 1:
                return '右家'
            elif seatDelta == 2:
                return '左家'
            else:
                return '本家'
        elif playerCount == 4:
            #     上
            # 左        右
            #     我
            if seatDelta == 1:
                return '右家'
            elif seatDelta == 2:
                return '对家'
            elif seatDelta == 3:
                return '左家'
            else:
                return '本家'
    
if __name__ == "__main__":
    result = MLocation.getLocInfo(0,2,4)
    ftlog.debug(result)