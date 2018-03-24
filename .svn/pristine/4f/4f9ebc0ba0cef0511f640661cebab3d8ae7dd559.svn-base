# -*- coding=utf-8
'''
Created on 2016年9月24日

@author: zhaol
'''
from majiang2.dealer.dealer import Dealer
import random
from majiang2.tile.tile import MTile
from freetime5.util import ftlog

"""
麻将手牌编码
万 1-9
筒 11-19
条 21-29
东 31
南 32
西 33
北 34
中 35
发 36
白 37
"""
class SanMenNoFengDealer(Dealer):
    def __init__(self):
        """初始化
            子类在自己的初始化方法里，初始化麻将牌池范围，准备发牌
            四川玩法，只有三门，没有风
        """
        super(SanMenNoFengDealer, self).__init__()
        # 本玩法包含的花色
        self.__card_colors = [MTile.TILE_WAN, MTile.TILE_TONG, MTile.TILE_TIAO]
        # 花色数量
        self.__card_count = len(self.__card_colors)
        # 初始化本玩法包含的牌
        self.setCardTiles(MTile.getTiles(self.__card_colors))
        ftlog.debug( self.cardTiles )
        
    """洗牌/发牌
        子类必须实现
    """
    def shuffle(self, goodPointCount, cardCountPerHand):
        """参数说明
            goodPointCount : 好牌点的人数
            cardCountPerHand ： 每手牌的麻将牌张数
        """
        for color in self.__card_colors:
            random.shuffle(self.cardTiles[color])
        
        tiles=[]
        for color in self.__card_colors:
            tiles.extend(self.cardTiles[color])

        # 对剩余的牌洗牌
        random.shuffle(tiles)
        self.addTiles(tiles)
        return self.tiles
    
    def getGoodCard(self, cardCountPerHand):
        """发一个人的好牌
        """
        count = self.getGoodCardCount(cardCountPerHand)
        
        color = random.randint(0, self.__card_count -1)
        cards = []
        cLen = len(self.cardTiles[color])
        if count > cLen:
            count = cLen
            
        # 发好牌
        for _ in range(count):
            cards.append(self.cardTiles[color].pop(0))
        # 发第二门
        count1 = (cardCountPerHand - count) / 2
        color = (color + 1) % self.__card_count
        for _ in range(count1):
            cards.append(self.cardTiles[color].pop(0))
        
        # 发最后一门
        left = cardCountPerHand - count - count1
        color = (color + 1) % self.__card_count
        for _ in range(left):
            cards.append(self.cardTiles[color].pop(0))
        return cards
        
    def getGoodCardCount(self, count):
        """好牌一门的数量
        """
        middle = count / 2
        choice = random.randint(0, 99)
        if choice > 90:
            middle += 2;
        elif choice > 60:
            middle += 1;
        
        return middle
    
if __name__ == "__main__":
    dealer = SanMenNoFengDealer()
    # 川麻
#     dealer.generateTiles({
#                         "seat1": [21,21,21,22,23,24,24,24,25,25,25,26,26],
#                         "seat2": [1,1,1,2,2,2,3,3,3,4,27,27,27],
#                         "seat3": [11,11,11,12,12,12,13,13,13,14,28,28,28],
#                         "seat4": [5,5,5,6,6,6,7,7,7,8,29,29,29],
#                         "pool": [],
#                         "magics": []
#                         })
    
    # 测试杠牌
#     dealer.generateTiles({
#                         "seat1": [1,1,1,2,2,2,3,3,3],
#                         "seat2": [11,11,11,12,12,12,13,13,13],
#                         "seat3": [21,21,21,22,22,22,23,23,23],
#                         "seat4": [],
#                         "pool": [1,2,3,11,12,13,21,22,23],
#                         "magics": []
#                         })

    # 测试血流三杀
    dealer.generateTiles({
                "seat1": [1,2,3,4,5,6,7,8,9,21,22,23,24],
                "seat2": [11,12,13,14,15,16,17,18,19,21,22,23,24],
                "seat3": [11,12,13,14,15,16,17,18,19,21,22,23,24],
                "seat4": [11,12,13,14,15,16,17,18,19,21,22,23,24],
                "pool": []
    })
