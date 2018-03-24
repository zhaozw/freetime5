# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
import random
from freetime5.util import ftlog
import json

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
class Dealer(object):
    def __init__(self):
        """初始化
            子类在自己的初始化方法里，初始化麻将牌池范围，准备发牌
        """
        super(Dealer, self).__init__()
        self.__tiles = []
        self.__wan_tiles = []
        self.__tiao_tiles = []
        self.__tong_tiles = []
        # 本玩法包含的牌
        self.__card_tiles = []
        
    def reset(self):
        """重置"""
        self.__tiles = []
        
    @property    
    def tiles(self):
        return self.__tiles
        
    def setTiles(self, tiles):
        self.__tiles = tiles
        
    def addTiles(self, tiles):
        self.__tiles.extend(tiles)
        
    def setCardTiles(self, cardTiles):
        self.__card_tiles = cardTiles
        
    @property
    def cardTiles(self):
        return self.__card_tiles
    
    """洗牌/发牌
        子类必须实现
    """
    def shuffle(self, goodPointCount, cardCountPerHand):
        """参数说明
            goodPointCount : 好牌点的个数
            cardCountPerHand ： 每手牌的麻将牌张数
        """
        return None
    
    def initTiles(self, handTiles, poolTiles):
        """根据摆牌结果初始化手牌"""
        ftlog.debug('MDealer.initTiles handTiles:', handTiles
                    , ' handTilesCount:', len(handTiles)
                    , ' poolTiles:', poolTiles
                    , ' poolTilesCount:', len(poolTiles)
                    , ' cardTiles:', self.cardTiles
                    , ' cardTilesCount:', len(self.cardTiles))
        cards = []
        for tiles in self.cardTiles:
            cards.extend(tiles)
        ftlog.debug('Dealer.initTiles cards:', cards)

        for hand in handTiles:
            for tile in hand:
                if tile not in cards:
                    ftlog.error('Dealer.initTiles handTile:', tile, ' not in cards')
                    return False
        
                cards.remove(tile)
                
        for tile in poolTiles:
            if tile not in cards:
                ftlog.error('Dealer.initTiles poolTile:', tile, ' not in cards...')
                return False
            cards.remove(tile)
            
        random.shuffle(cards)
        self.__tiles = []
        ftlog.debug('Dealer.initTiles, now cards:', cards)
        
        ftlog.debug('Dealer.initTiles handTiles:', handTiles)
        for index in range(len(handTiles)):
            self.__tiles.extend(handTiles[index])
            ftlog.debug('Dealer.initTiles self.tiles after extend handTiles:', self.__tiles)
            for _ in range(len(handTiles[index]), 13):
                self.__tiles.append(cards.pop(0))
            ftlog.debug('Dealer.initTiles self.__tiles after merge cards to make whole handTiles:', self.tiles)
        
        self.__tiles.extend(poolTiles)
        self.__tiles.extend(cards)
           
        return True
    
    def removeCards(self, cards, delTiles, errInfo):
        '''
        del delTiles from cards
        '''
        for tile in delTiles:
            if tile not in cards:
                print 'Error, ', errInfo, ' tile:', tile, ' not in cards....'
                return False
            cards.remove(tile)
            
        return True
    
    def generateTiles(self, extendInfo):
        """
        根据输入信息生成摆牌器
            extendInfo = {
                "seat1": [],
                "seat2": [],
                "seat3": [],
                "seat4": [],
                "pool": [],
                "magics": [],
                "jing": [],
                "laizi": []
            }
        """
        cards = []
        for tiles in self.cardTiles:
            cards.extend(tiles)
        ftlog.debug('Dealer.initTiles cards:', cards)
        
        magics = extendInfo.get('magics', [])
        if not self.removeCards(cards, magics, 'magics'):
            return
            
        horses = extendInfo.get('horses', {})
        seat1Horse = horses.get('seat1', [])
        if not self.removeCards(cards, seat1Horse, 'seat1Horse'):
            return
        
        seat2Horse = horses.get('seat2', [])
        if not self.removeCards(cards, seat2Horse, 'seat2Horse'):
            return
        
        seat3Horse = horses.get('seat3', [])
        if not self.removeCards(cards, seat3Horse, 'seat3Horse'):
            return
        
        seat4Horse = horses.get('seat4', [])
        if not self.removeCards(cards, seat4Horse, 'seat4Horse'):
            return
            
        seat1 = extendInfo.get('seat1', [])
        if not self.removeCards(cards, seat1, 'seat1'):
            return
            
        seat2 = extendInfo.get('seat2', [])
        if not self.removeCards(cards, seat2, 'seat2'):
            return
        
        seat3 = extendInfo.get('seat3', [])
        if not self.removeCards(cards, seat3, 'seat3'):
            return

        seat4 = extendInfo.get('seat4', [])
        if not self.removeCards(cards, seat4, 'seat4'):
            return
            
        pool = extendInfo.get('pool', [])
        if not self.removeCards(cards, pool, 'pool'):
            return
        
        random.shuffle(cards)    
        while len(seat1) < 13:
            seat1.append(cards.pop(0))
            
        while len(seat2) < 13:
            seat2.append(cards.pop(0))
            
        while len(seat3) < 13:
            seat3.append(cards.pop(0))
            
        while len(seat4) < 13:
            seat4.append(cards.pop(0))
            
        for index in range(len(pool)):
            if pool[index] == 0:
                pool[index] = cards.pop(0)
        
        pool.extend(cards)
        pool.extend(seat4Horse)
        pool.extend(seat3Horse)
        pool.extend(seat2Horse)
        pool.extend(seat1Horse)
        pool.extend(magics)
        
        putCard = {}
        putCard['seat1'] = seat1
        putCard['seat2'] = seat2
        putCard['seat3'] = seat3
        putCard['seat4'] = seat4
        putCard['pool'] = pool
        
        print json.dumps(putCard)
        
        