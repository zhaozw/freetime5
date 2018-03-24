# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: yawen
'''

from majiang2.tile.tile import MTile

class MFlowerRuleBase(object):
    """
    花牌判断
    """
    
    def __init__(self):
        super(MFlowerRuleBase, self).__init__()


    @classmethod
    def hasFlower(cls, tiles):
        flowers =[]
        for tile in tiles:
            if MTile.isFlower(tile):
                flowers.append(tile)

        return flowers
    
    @classmethod
    def getAllFlowers(cls, players):
        flowers = [None for _ in range(len(players))]
        for player in players:
            flowers[player.curSeatId] = cls.hasFlower(player.copyHandTiles())
        return flowers
    
    @classmethod
    def getFlowerCount(cls, flowers):
        count = 0
        for f in flowers:
            count += len(f)
        return count
