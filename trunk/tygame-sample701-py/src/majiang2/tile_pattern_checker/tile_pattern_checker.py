# -*- coding=utf-8
'''
Created on 2016年12月11日
牌型整理
@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from majiang2.player.player import MPlayerTileGang
from majiang2.tile.tile import MTile
import copy


class MTilePatternChecker(object):
    """
    基础番型计算
    仅仅有手牌组成的番型计算，不考虑打牌时的具体情况，比如自摸，点炮，杠开，海底捞等。
    只考虑基本番型，比如七对，清一色，风一色，对对胡等等。
    
    算分时，结合胡牌的具体情况+番型，计算。比如清一色+杠开等
    只判断当前玩家的番型
    """
    def __init__(self):
        super(MTilePatternChecker, self).__init__()
        # 牌桌手牌管理器
        self.__table_tile_mgr = None
        '''当前玩家的所有牌，按手牌格式的数组 
        初始化时，即将胡牌或赢的牌添加到handTile中，
        由于有的玩法可以胡多张，且此模块需计算听牌番数
        '''
        self.__player_all_tiles = []
        self.__fan_xing = {}
        
    @property
    def fanXing(self):
        return self.__fan_xing
    
    def setfanXing(self, fanXing):
        self.__fan_xing = fanXing
        
    def addFanXing(self, fanXing, name, index):
        if fanXing in self.fanXing:
            return
        
        self.fanXing[fanXing] = {"name":name, "index":index}

    def setTableTileMgr(self, tableTileMgr):
        """设置手牌管理器"""
        self.__table_tile_mgr = tableTileMgr
     
    @property   
    def tableTileMgr(self):
        return self.__table_tile_mgr 

    @property
    def playerAllTiles(self):
        return self.__player_all_tiles

    def setPlayerAllTiles(self, tiles):
        # 仅用于测试
        self.__player_all_tiles = tiles

    def initChecker(self, playersAllTiles, tableTileMgr):
        self.setTableTileMgr(tableTileMgr)
        self.__player_all_tiles = copy.deepcopy(playersAllTiles)
        ftlog.info('MTilePatternChecker.calcScore __player_all_tiles=', self.__player_all_tiles)

    def isQingyise(self):
        """
        清一色：由同一门花色（筒子或条子）组成的和牌牌型
        
        前提：胡牌
        """
        handTiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        magictiles = self.tableTileMgr.getMagicTiles()
        if len(magictiles) > 0:
            # 过滤赖子
            handTiles = filter(lambda x: (x != magictiles[0]), handTiles)
        tileArr = MTile.changeTilesToValueArr(handTiles)
        colorCount = MTile.getColorCount(tileArr)
        ftlog.debug('MTilePatternChecker.isQingyise colorCount:', colorCount)
        if colorCount != 1:
            return False
        
        tile = handTiles[0]
        return MTile.isWan(tile) or MTile.isTong(tile) or MTile.isTiao(tile)
    
    def isHunYiSe(self):
        '''
        混一色
        
        前提：胡牌
        '''
        handTiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        magictiles = self.tableTileMgr.getMagicTiles()
        if len(magictiles) > 0:
            # 过滤赖子
            handTiles = filter(lambda x: (x != magictiles[0]), handTiles)
        allCount = len(handTiles)
        # 过滤风
        handTiles = filter(lambda x:((not MTile.isFeng(x)) and (not MTile.isArrow(x))), handTiles)
        filterCount = len(handTiles)
        tileArr = MTile.changeTilesToValueArr(handTiles)
        colorCount = MTile.getColorCount(tileArr)
        ftlog.debug('MTilePatternChecker.isHunYiSe colorCount:', colorCount)
        return (colorCount == 1) and (allCount != filterCount)

    def isZiyise(self):
        """
        字一色：由东南西北中发白组成的胡牌
        
        特殊说明：
        有的地方需首先满足胡牌条件，有的地方只要都是字牌就可以
        """
        handTiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)  # 手牌区+吃+碰+杠+锚+胡区
        magictiles = self.tableTileMgr.getMagicTiles()
        if len(magictiles) > 0:
            # 过滤赖子
            handTiles = filter(lambda x: (x != magictiles[0]), handTiles)

        handArr = MTile.changeTilesToValueArr(handTiles)
        colorCount = MTile.getColorCount(handArr)
        result, _ = MWin.isLuanFengyise(handTiles, colorCount)
        return result

    def isShouzhuayi(self):
        """
        1）手抓一：胡牌时自己手上只有一张牌，和牌手牌应该是一对
        也叫
        2）大吊车
        3）金钩钓
        
        前提条件：满足胡牌要求
        """ 
        handTile = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        if len(handTile) % 3 != 2:
            handTile.extend(self.playerAllTiles[MHand.TYPE_HU])
        return len(handTile) == 2
    
    def isDuiDuiHu(self):
        boolFlag, _ = self.isPengpenghu()
        return boolFlag

    def isPengpenghu(self , laizi=None):
        """
        碰碰胡：由四个刻子（杠）和一对组成的胡牌牌型 不需要二五八做将
        """
        chiTile = self.playerAllTiles[MHand.TYPE_CHI]  # 吃牌区
        if len(chiTile) > 0:
            ftlog.debug('MTilePatternChecker.isPengpenghu result: False')
            return False, []

        maoTile = self.playerAllTiles[MHand.TYPE_MAO]  # 锚牌区
        if len(maoTile) > 0:
            ftlog.debug('MTilePatternChecker.isPengpenghu result: False')
            return False, []

        handTiles = self.playerAllTiles[MHand.TYPE_HAND]
        htiles = copy.deepcopy(handTiles)

        laiziCount = 0
        # 移除赖子
        if laizi != None:
            for _ in range(4):
                if laizi in htiles:
                    htiles.remove(laizi)
                    laiziCount += 1

        hTileArr = MTile.changeTilesToValueArr(htiles)  # 手牌区符合 2+ 3*n
        duiCount = 0
        keCount = 0
        singleCount = 0
        for tileIndex in range(0, len(hTileArr)):
            if hTileArr[tileIndex] == 0:
                continue
            # 对子
            elif hTileArr[tileIndex] == 2:
                duiCount += 1
            # 刻子
            elif hTileArr[tileIndex] == 3:
                keCount += 1
            # 单个
            elif hTileArr[tileIndex] == 1:
                singleCount += 1
            elif hTileArr[tileIndex] == 4:
                ftlog.debug('MTilePatternChecker.isPengpenghu result: False')
                return False, []

        if laiziCount == 0 and keCount >= 0:
            if duiCount == 1 and (2 * duiCount + 3 * keCount) == len(htiles):
                return True , [handTiles]
            ftlog.debug('MTilePatternChecker.isPengpenghu result: False')
            return False, []
        # 1个赖子 只能  1 + 3*n 或者 2*2 + 3*n
        if laiziCount == 1 and keCount >= 0:
            if duiCount == 2 and (2 * duiCount + 3 * keCount) == len(htiles):
                return True, [handTiles]
            if singleCount == 1 and (singleCount + 3 * keCount) == len(htiles):
                return True, [handTiles]
            ftlog.debug('MTilePatternChecker.isPengpenghu result: False')
            return False, []
        # 2个赖子 只能  1 + 2*2 + 3*n 或者 3*2+3*n
        if laiziCount == 2 and keCount >= 0:
            if singleCount == 1 and duiCount == 1 and (singleCount + 2 * duiCount + 3 * keCount) == len(htiles):
                return True, [handTiles]
            if singleCount == 0 and duiCount == 3 and (2 * duiCount + 3 * keCount) == len(htiles):
                return True, [handTiles]
            ftlog.debug('MTilePatternChecker.isPengpenghu result: False')
            return False, []
        # 3个赖子 只能  2+3*n 2*4+3*n 2*2+1+3*n 1*2+3*n
        if laiziCount == 3 and keCount >= 0:
            if duiCount == 1 and (2 * duiCount + 3 * keCount) == len(htiles):
                return True, [handTiles]
            if duiCount == 4 and (2 * duiCount + 3 * keCount) == len(htiles):
                return True, [handTiles]
            if duiCount == 2 and singleCount == 1 and (2 * duiCount + singleCount + 3 * keCount) == len(htiles):
                return True, [handTiles]
            if singleCount == 2 and (singleCount + 3 * keCount) == len(htiles):
                return True, [handTiles]
            ftlog.debug('MTilePatternChecker.isPengpenghu result: False')
            return False, []
        ftlog.debug('MTilePatternChecker.isPengpenghu result: False')
        return False, []

    def isQidui(self, laizi=[]):
        """
        七对：手中有七个对子的胡牌牌型，碰出的牌不算
        
        前提条件，无，七对半身就是胡牌类型
        """
        if len(self.playerAllTiles[MHand.TYPE_HAND]) != 14:
            ftlog.debug('MTilePatternChecker.isQidui: false')
            return False, []

        result, pattern = MWin.isQiDui(self.playerAllTiles[MHand.TYPE_HAND], laizi)
        ftlog.debug('MTilePatternChecker.isQiDui result:', result,'pattern:',pattern)
        return result, pattern

    def isQiduiHao(self, laizi=[]):
        """
        豪华七对：有四个相同的牌当做两个对子使用
        
        前提条件：七对
        """
        res, pattern = self.isQidui(laizi)
        if not res:
            return False

        if len(laizi)>0:
            if [laizi[0],laizi[0]] in pattern:
                return True
            else:
                tiles = []
                for pa in pattern:
                    for tile in pa:
                        if tile != laizi[0]:
                            tiles.append(tile)
                tileCountArr = MTile.changeTilesToValueArr(tiles)
                for tileCount in tileCountArr:
                    if tileCount >= 3:
                        return True
                return False
        else:
            tileCountArr = MTile.changeTilesToValueArr(self.playerAllTiles[MHand.TYPE_HAND])
            fourCount = 0
            for tileCount in tileCountArr:
                if tileCount == 4:
                    fourCount += 1
            ftlog.debug('MTilePatternChecker.isQiduiHao result: False')
            return fourCount >= 1

    def isQiduiChaoHao(self, pattern):
        """
        超豪华七对：有两个四个相同的牌当做四个对子使用
        
        前提条件：七对
        """
        res, pattern = self.isQidui()
        if not res:
            return False
        
        tileCountArr = MTile.changeTilesToValueArr(self.playerAllTiles[MHand.TYPE_HAND])
        fourCount = 0
        for tileCount in tileCountArr:
            if tileCount == 4:
                fourCount += 1
        ftlog.debug('MTilePatternChecker.isQiduiHao result: False')
        return fourCount >= 2

    def isQiduiChaoChaoHao (self, pattern):
        """
        超超豪华七对：有三个四个相同的牌当做六个对子使用
        
        前提条件：七对
        """
        res, pattern = self.isQidui()
        if not res:
            return False
        
        tileCountArr = MTile.changeTilesToValueArr(self.playerAllTiles[MHand.TYPE_HAND])
        fourCount = 0
        for tileCount in tileCountArr:
            if tileCount == 4:
                fourCount += 1
        ftlog.debug('MTilePatternChecker.isQiduiHao result: False')
        return fourCount >= 3
    
    def isLianQiDui(self):
        '''
        连七对
        
        前提条件：七对
        '''
        res, pattern = self.isQidui()
        if not res:
            return False
        
        if not self.isQingyise():
            return False
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        handTiles.sort()
        first = handTiles[0]
        lianQi = [first, first + 1, first + 2, first + 3, first + 4, first + 5, first + 6]
        for tile in lianQi:
            if tile not in handTiles:
                return False
        return True
    
    def isLvYise(self):
        '''
        绿一色
        
        前提条件：胡牌
        '''
        lvs = [MTile.TILE_TWO_TIAO, MTile.TILE_THREE_TIAO, MTile.TILE_FOUR_TIAO, MTile.TILE_SIX_TIAO, MTile.TILE_EIGHT_TIAO, MTile.TILE_FA_CAI]
        allTile = MHand.copyAllTilesToList(self.playerAllTiles)
        lefts = filter(lambda x:(x not in lvs), allTile)
        return (len(lefts) == 0)

    def isXiaosanyuan (self):
        """
        小三元：胡牌时 如果牌面上有中、发、白中的任意2种（每种牌3张，碰杠都算），并且牌面中还有其余1对
        中发白胡牌时，只能时按照将，刻，杠，不可能按照顺子来胡牌，所以不用看胡牌牌型
        
        前提条件：满足普通的胡牌条件
        """
        allTile = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        tileCountArr = MTile.changeTilesToValueArr(allTile)
        kegangCount = 0
        jiangCount = 0    
        for tileCheck in [MTile.TILE_HONG_ZHONG, MTile.TILE_FA_CAI, MTile.TILE_BAI_BAN]:
            if tileCountArr[tileCheck] >= 3:
                kegangCount += 1
            elif tileCountArr[tileCheck] == 2:
                jiangCount += 1
        if kegangCount == 2 and jiangCount == 1:
            ftlog.debug('MTilePatternChecker.isXiaosanyuan result: True')
            return True
        ftlog.debug('MTilePatternChecker.isXiaosanyuan result: False')
        return False

    def isDasanyuan (self):
        """
        大三元：胡牌时 如果牌面上有中、发、白每种3张（碰杠都算），称为大三元
        
        前提条件：满足普通的胡牌条件
        """
        allTile = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        tileCountArr = MTile.changeTilesToValueArr(allTile)
        if tileCountArr[MTile.TILE_HONG_ZHONG] >= 3 and tileCountArr[MTile.TILE_FA_CAI] >= 3 and tileCountArr[MTile.TILE_BAI_BAN] >= 3:
            ftlog.debug('MTilePatternChecker.isDasanyuan result: True')
            return True
        ftlog.debug('MTilePatternChecker.isDasanyuan result: False')
        return False

    def isXiaosixi(self):
        """
        小四喜：胡牌时 如果牌面上有东南西北中的任意3种（每种牌3张，碰杠都算），并且牌面中还有其余1对
        东南西北胡牌时，只能时按照将，刻，杠，不可能按照顺子来胡牌，所以不用看胡牌牌型
        
        前提条件：满足普通的胡牌条件
        """
        allTile = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        tileCountArr = MTile.changeTilesToValueArr(allTile)
        kegangCount = 0
        jiangCount = 0
        for tileCheck in [MTile.TILE_DONG_FENG, MTile.TILE_NAN_FENG, MTile.TILE_XI_FENG, MTile.TILE_BEI_FENG]:
            if tileCountArr[tileCheck] >= 3:
                kegangCount += 1
            elif tileCountArr[tileCheck] == 2:
                jiangCount += 1
        if kegangCount == 3 and jiangCount == 1:
            ftlog.debug('MTilePatternChecker.isXiaosixi result: True')
            return True
        ftlog.debug('MTilePatternChecker.isXiaosixi result: False')
        return False

    def isDasixi (self):
        """
        大四喜：胡牌时 如果牌面上有东南西北每种3张（碰杠都算）
        
        前提条件：满足普通的胡牌条件
        """
        allTile = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        tileCountArr = MTile.changeTilesToValueArr(allTile)
        if tileCountArr[MTile.TILE_DONG_FENG] >= 3 and tileCountArr[MTile.TILE_NAN_FENG] >= 3 \
                and tileCountArr[MTile.TILE_XI_FENG] >= 3 and tileCountArr[MTile.TILE_BEI_FENG] >= 3:
            ftlog.debug('MTilePatternChecker.isDasixi result: True')
            return True
        ftlog.debug('MTilePatternChecker.isDasixi result: False')
        return False

    def isXiaosanyuanMagic(self, winPattern, magictile):
        """
        小三元：胡牌时 如果牌面上有中、发、白中的任意2种（每种牌3张，碰杠都算），并且牌面中还有其余1对
        中发白胡牌时，只能时按照将，刻，杠，不可能按照顺子来胡牌，所以不用看胡牌牌型

        前提条件：满足普通的胡牌条件
        """
        magicpeng = 0
        magicjiang = 0
        fengcount = 0
        jiangcount = 0
        for p in winPattern:
            if len(p) == 3:
                if p[0] == p[1] == p[2] == magictile:
                    magicpeng += 1
                p = filter(lambda x: x != magictile, p)
                if len(p) > 0:
                    if MTile.isArrow(p[0]):
                        fengcount += 1
            elif len(p) == 2:
                if p[0] == p[1] == magictile:
                    magicjiang += 1
                p = filter(lambda x: x != magictile, p)
                if len(p) > 0:
                    if MTile.isArrow(p[0]):
                        jiangcount += 1

        if jiangcount + magicjiang == 0:
            ftlog.debug('MTilePatternChecker.isXiaosanyuanMagic result: False')
            return False

        for p in self.playerAllTiles[MHand.TYPE_PENG]:
            if MTile.isArrow(p[0]):
                fengcount += 1
        for p in self.playerAllTiles[MHand.TYPE_GANG]:
            if MTile.isArrow(p['pattern'][0]):
                fengcount += 1
        ftlog.debug('MTilePatternChecker.isXiaosanyuanMagic fengcount:', fengcount, 'magicpeng', magicpeng)

        if fengcount == 2:
            ftlog.debug('MTilePatternChecker.isXiaosanyuanMagic result: True')
            return True
        elif fengcount == 1 and magicpeng == 1:
            ftlog.debug('MTilePatternChecker.isXiaosanyuanMagic result: True')
            return True
        else:
            ftlog.debug('MTilePatternChecker.isXiaosanyuanMagic result: False')
            return False

    def isDasanyuanMagic(self, winPattern, magictile):
        """
        大三元：胡牌时 如果牌面上有中、发、白每种3张（碰杠都算），称为大三元

        前提条件：满足普通的胡牌条件
        """
        magicpeng = 0
        fengcount = 0
        for p in winPattern:
            if len(p) == 3:
                if p[0] == p[1] == p[2] == magictile:
                    magicpeng += 1
                p = filter(lambda x: x != magictile, p)
                if len(p) > 0:
                    if MTile.isArrow(p[0]):
                        fengcount += 1

        for p in self.playerAllTiles[MHand.TYPE_PENG]:
            if MTile.isArrow(p[0]):
                fengcount += 1
        for p in self.playerAllTiles[MHand.TYPE_GANG]:
            if MTile.isArrow(p['pattern'][0]):
                fengcount += 1
        ftlog.debug('MTilePatternChecker.isDasanyuanMagic fengcount:', fengcount, 'magicpeng', magicpeng)

        if fengcount == 3:
            ftlog.debug('MTilePatternChecker.isDasanyuanMagic result: True')
            return True
        elif fengcount == 2 and magicpeng == 1:
            ftlog.debug('MTilePatternChecker.isDasanyuanMagic result: True')
            return True
        else:
            ftlog.debug('MTilePatternChecker.isDasanyuanMagic result: False')
            return False

    def isXiaosixiMagic(self, winPattern, magictile):
        """
        小四喜：胡牌时 如果牌面上有东南西北中的任意3种（每种牌3张，碰杠都算），并且牌面中还有其余1对
        东南西北胡牌时，只能时按照将，刻，杠，不可能按照顺子来胡牌，所以不用看胡牌牌型

        前提条件：满足普通的胡牌条件
        """
        magicpeng = 0
        magicjiang = 0
        fengcount = 0
        jiangcount = 0
        for p in winPattern:
            if len(p) == 3:
                if p[0] == p[1] == p[2] == magictile:
                    magicpeng += 1
                p = filter(lambda x:x != magictile, p)
                if len(p) > 0:
                    if MTile.isFeng(p[0]):
                        fengcount += 1
            elif len(p) == 2:
                if p[0] == p[1] == magictile:
                    magicjiang += 1
                p = filter(lambda x: x != magictile, p)
                if len(p) > 0:
                    if MTile.isFeng(p[0]):
                        jiangcount += 1

        if jiangcount + magicjiang == 0:
            ftlog.debug('MTilePatternChecker.isXiaosixiMagic result: False')
            return False

        for p in self.playerAllTiles[MHand.TYPE_PENG]:
            if MTile.isFeng(p[0]):
                fengcount += 1
        for p in self.playerAllTiles[MHand.TYPE_GANG]:
            if MTile.isFeng(p['pattern'][0]):
                fengcount += 1
        ftlog.debug('MTilePatternChecker.isXiaosixiMagic fengcount:', fengcount, 'magicpeng', magicpeng)

        if fengcount == 3:
            ftlog.debug('MTilePatternChecker.isXiaosixiMagic result: True')
            return True
        elif fengcount == 2 and magicpeng == 1:
            ftlog.debug('MTilePatternChecker.isXiaosixiMagic result: True')
            return True
        else:
            ftlog.debug('MTilePatternChecker.isXiaosixiMagic result: False')
            return False

    def isDasixiMagic(self, winPattern, magictile):
        """
        大四喜：胡牌时 如果牌面上有东南西北每种3张（碰杠都算）

        前提条件：满足普通的胡牌条件
        """
        magicpeng = 0
        fengcount = 0
        for p in winPattern:
            if len(p) == 3:
                if p[0] == p[1] == p[2] == magictile:
                    magicpeng += 1
                p = filter(lambda x:x != magictile, p)
                if len(p) > 0:
                    if MTile.isFeng(p[0]):
                        fengcount += 1

        for p in self.playerAllTiles[MHand.TYPE_PENG]:
            if MTile.isFeng(p[0]):
                fengcount += 1
        for p in self.playerAllTiles[MHand.TYPE_GANG]:
            if MTile.isFeng(p['pattern'][0]):
                fengcount += 1
        ftlog.debug('MTilePatternChecker.isDasixiMagic fengcount:', fengcount, 'magicpeng', magicpeng)

        if fengcount == 4:
            ftlog.debug('MTilePatternChecker.isDasixiMagic result: True')
            return True
        elif fengcount == 3 and magicpeng == 1:
            ftlog.debug('MTilePatternChecker.isDasixiMagic result: True')
            return True
        else:
            ftlog.debug('MTilePatternChecker.isDasixiMagic result: False')
            return False


    def isSifangDaFa(self):
        '''
        四方大发：大四喜+青发对
        '''
        if not self.isDasixi():
            return False
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        jiangTiles = filter(lambda x:(not MTile.isFeng(x)), handTiles)
        return jiangTiles == [MTile.TILE_FA_CAI, MTile.TILE_FA_CAI]

    def isQingyaojiu(self, laizi=[]):
        """
        清幺九：全部是1、9牌组成的胡牌番型
        
        前提条件：满足普通的胡牌条件
        
        其他称呼
        1）全幺九
        """
        handTile = MHand.copyAllTilesToListButHu(self.playerAllTiles)  # 手牌区+吃+碰+杠+锚+胡区
        if len(laizi) > 0:
            handTile = filter(lambda x: (x != laizi[0]), handTile)
        for tile in handTile:
            if not MTile.isYaoJiu(tile):
                return False
        return True

    def isHunyaojiu(self, laizi=[]):
        '''
        混幺九
        前提条件：满足普通的胡牌条件
        '''
        handTiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        allCount = len(handTiles)
        # 过滤风
        handTiles = filter(lambda x:((not MTile.isFeng(x)) and (not MTile.isArrow(x))), handTiles)
        if len(laizi) > 0:
            handTiles = filter(lambda x: (x != laizi[0]), handTiles)
        filterCount = len(handTiles)
        if filterCount == 0:
            return False

        isAllYaojiu = True
        for tile in handTiles:
            if not MTile.isYaoJiu(tile):
                isAllYaojiu = False
                break
        return isAllYaojiu and (allCount != filterCount)
    
    def isQuanYaoJiu(self):
        """
        判断是否是全幺九
        
        全幺九
        吃/碰/杠/将牌里都还有幺/九
        
        如果有非幺九的牌，一定在顺子里面。
        1）吃牌
        2）手牌中可以组成吃牌的牌
        """
        # 验证吃牌
        chiPatterns = self.playerAllTiles[MHand.TYPE_CHI]
        for chiPattern in chiPatterns:
            hasYaoJiu = False
            for tile in chiPattern:
                if MTile.isYaoJiu(tile):
                    hasYaoJiu = True
                    break
            if not hasYaoJiu:
                return False
        
        # 验证碰牌
        pengPatterns = self.playerAllTiles[MHand.TYPE_PENG]
        for pengPattern in pengPatterns:
            tile = pengPattern[0]
            if not MTile.isYaoJiu(tile):
                return False
            
        # 验证杠牌[{'pattern': [31, 31, 31, 31], 'style': True, 'actionID': 11}]
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            pattern = gang['pattern']
            tile = pattern[0]
            if not MTile.isYaoJiu(tile):
                return False
        
        # 提取手牌中的所有顺子
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        YAOS = [MTile.TILE_ONE_WAN, MTile.TILE_ONE_TONG, MTile.TILE_ONE_TIAO]
        JIUS = [MTile.TILE_NINE_WAN, MTile.TILE_NINE_TONG, MTile.TILE_NINE_TIAO]
        for yao in YAOS:
            while (yao in handTiles) and ((yao + 1) in handTiles) and ((yao + 2) in handTiles):
                handTiles.remove(yao)
                handTiles.remove(yao + 1)
                handTiles.remove(yao + 2)
        for jiu in JIUS:
            while (jiu in handTiles) and ((jiu - 1) in handTiles) and ((jiu - 2) in handTiles):
                handTiles.remove(jiu)
                handTiles.remove(jiu - 1)
                handTiles.remove(jiu - 2)
                
        # 剩下的牌都是幺九
        for tile in handTiles:
            if not MTile.isYaoJiu(tile):
                return False
        
        result, patterns = MWin.isHu(handTiles)
        ftlog.debug('MWin.isQuanYaoJiu tiles:', self.playerAllTiles
                    , ' result:', result
                    , ' patterns:', patterns)
        return result
    
    def isDuanYaoJiu(self):
        '''
        断幺九
        所有的牌里没有幺九
        '''
        tiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        for tile in tiles:
            if MTile.isYaoJiu(tile):
                return False
        return True

    def isShisanyao(self, laizi=[]):
        """
        十三幺：13章（由东南西北中发白 + 一万、九万、一条、九条、一筒、九筒）+ 这13章中任意一种牌
        前提条件：无

        十三幺是门清
        只需要判断TYPE_HAND手牌

        其他称呼
        1）国士无双
        """
        if len(self.playerAllTiles[MHand.TYPE_HAND]) != 14:
            ftlog.debug('MTilePatternChecker.isShisanyao: false')
            return False

        ftlog.debug('MTilePatternChecker.isShisanyao, laizi:', laizi,
                    'tiles[MHand.TYPE_HAND]:', self.playerAllTiles[MHand.TYPE_HAND],
                    'len tiles[MHand.TYPE_HAND]:', len(self.playerAllTiles[MHand.TYPE_HAND])
                    )

        yao13Arr = [1, 9, 11, 19, 21, 29, 31, 32, 33, 34, 35, 36, 37]
        handTile = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])

        if len(laizi) == 0:
            # 没有赖子
            yaoJiuCount = 0
            for yao in yao13Arr:
                if yao in handTile:
                    yaoJiuCount += 1

            if yaoJiuCount == 13:
                allYao = True
                for tile in handTile:
                    if tile not in yao13Arr:
                        allYao = False
                        break
                if allYao:
                    return True

            return False
        else:
            # 有赖子
            # 如果除去赖子全是幺九，并且数量>=T－1，就是十三幺
            laiziTile = laizi[0]
            handTile = filter(lambda x: (x != laiziTile), handTile)
            # 如果有不是幺九的，直接返回false
            for tile in handTile:
                if tile not in yao13Arr:
                    return False
            # 计算幺九数量
            yaojiuArray = []
            for tile in handTile:
                if tile not in yaojiuArray:
                    yaojiuArray.append(tile)
            if len(yaojiuArray) >= len(handTile) - 1:
                return True
            else:
                return False

        '''
        def isShisanyao(self, laizi=[]):
        """
        十三幺：13章（由东南西北中发白 + 一万、九万、一条、九条、一筒、九筒）+ 这13章中任意一种牌
        前提条件：无

        十三幺是门清
        只需要判断TYPE_HAND手牌

        其他称呼
        1）国士无双
        """
        if len(self.playerAllTiles[MHand.TYPE_HAND]) != 14:
            ftlog.debug('MTilePatternChecker.isShisanyao: false')
            return False

        laiziCountInHand = 0
        if len(laizi) > 0:
            for x in self.playerAllTiles[MHand.TYPE_HAND]:
                if x == laizi[0]:
                    laiziCountInHand += 1

        yao13Arr = [1, 9, 11, 19, 21, 29, 31, 32, 33, 34, 35, 36, 37]
        handTile = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        for yao in yao13Arr:
            if yao not in handTile:
                if len(laizi) > 0 and laiziCountInHand>0:
                    laiziCountInHand -= 1
                    if laizi[0] in handTile:
                        handTile.remove(laizi[0])
                    continue
                ftlog.debug('MTilePatternChecker.isShisanyao: false')
                return False
            handTile.remove(yao)

        okpass = False
        if len(laizi) > 0:
            if handTile[0] == laizi[0]:
                okpass = True
        res = (len(handTile) == 1) and ((handTile[0] in yao13Arr) or okpass)
        ftlog.debug('MTilePatternChecker.isShisanyao: res', res)
        return res
        '''

    def isJiuLianBaoDeng(self):
        '''
        九莲宝灯
        1）清一色
        2）特殊牌型
        '''
        if not self.isQingyise():
            return False
        
        baoDengs = [1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9]
        newHand = []
        for tile in self.playerAllTiles[MHand.TYPE_HAND]:
            newHand.append(MTile.getValue(tile))
        
        for baoTile in baoDengs:
            if baoTile not in newHand:
                return False
            newHand.remove(baoTile)
            
        return True
    
    def isShiBaLuoHan(self):
        '''
        十八罗汉  4*4 + 2
        
        也叫
        1）四杠
        '''
        tiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        ftlog.debug('MTilePatternChecker.isShiBaLuoHan tiles:', tiles)
        if len(tiles) == 18 and len(self.playerAllTiles[MHand.TYPE_GANG]) == 4:
            ftlog.debug('MTilePatternChecker.isShiBaLuoHan: True')
            return True
        else:
            ftlog.debug('MTilePatternChecker.isShiBaLuoHan: False')
            return False
        
    def isSanGang(self):
        '''
        三杠
        
        前提：胡牌
        '''
        return len(self.playerAllTiles[MHand.TYPE_GANG]) == 3
        
    def isYiSeShuangLongHui(self):
        '''
        一色双龙会
        前提条件：清一色
        123 123 789 789 55
        '''
        if not self.isQingyise():
            return False
        
        allTiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        allTiles.sort()
        newAll = []
        
        for tile in allTiles:
            newAll.append(MTile.getValue(tile))
        
        return newAll == [1, 1, 2, 2, 3, 3, 5, 5, 7, 7, 8, 8, 9, 9]
    
    def isSiAnKe(self):
        '''
        四暗刻
        四个暗刻或者暗杠+一对将
        前提条件：
        1）自摸，在自摸的情况下判断你是否是四暗刻
        
        '''
        keTiles = []
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            if gang['stype'] == MPlayerTileGang.AN_GANG:
                keTiles.append(gang['pattern'][0])
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tilesArr = MTile.changeTilesToValueArr(handTiles)
        for tile in handTiles:
            if (tilesArr[tile] == 3) and (tile not in keTiles):
                keTiles.append(tile)
        
        leftTiles = filter(lambda x:(x not in keTiles), handTiles)
        ftlog.debug('MTilePatternChecker.isSiAnKe tiles:', self.playerAllTiles
                    , ' keTiles:', keTiles
                    , ' leftTiles:', leftTiles)
        return (len(keTiles) == 4) and (len(leftTiles) == 2) and (leftTiles[0] == leftTiles[1])
    
    def isSanAnKe(self):
        '''
        三暗刻
        三个暗刻或者暗杠
        
        前提条件：胡牌
        '''
        keTiles = []
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            if gang['stype'] == MPlayerTileGang.AN_GANG:
                keTiles.append(gang['pattern'][0])
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tilesArr = MTile.changeTilesToValueArr(handTiles)
        removes = []
        for tile in handTiles:
            if (tilesArr[tile] >= 3) and (tile not in keTiles):
                keTiles.append(tile)
                removes.extend([tile, tile, tile])
        
        if len(keTiles) != 3:
            return False
        
        for tile in removes:
            handTiles.remove(tile)
            
        return MWin.isHu(handTiles)
    
    def isSanFengKe(self):
        '''
        三暗刻
        三个暗刻或者暗杠
        
        前提条件：胡牌
        '''
        keTiles = []
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            tile = gang['pattern'][0]
            keTiles.append(tile)
            
        pengs = self.playerAllTiles[MHand.TYPE_PENG]
        for peng in pengs:
            keTiles.append(peng[0])
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tilesArr = MTile.changeTilesToValueArr(handTiles)
        removes = []
        for tile in handTiles:
            if (tilesArr[tile] >= 3) and (tile not in keTiles):
                keTiles.append(tile)
                removes.extend([tile, tile, tile])
        
        if len(keTiles) != 3:
            return False
        
        for tile in keTiles:
            if tile < MTile.TILE_DONG_FENG or tile > MTile.TILE_BAI_BAN:
                return False
        
        return True
        
    def isSanTongKe(self):
        '''
        三同刻
        三种值一样的刻
        
        前期条件：胡牌
        '''
        keTiles = []
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            keTiles.append(gang['pattern'][0])
            
        pengs = self.playerAllTiles[MHand.TYPE_PENG]
        for peng in pengs:
            keTiles.append(peng[0])
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tilesArr = MTile.changeTilesToValueArr(handTiles)
        removes = []
        for tile in handTiles:
            if (tilesArr[tile] >= 3) and (tile not in keTiles):
                keTiles.append(tile)
                removes.extend([tile, tile, tile])
        
        if len(keTiles) < 3:
            return False
        
        keValues = []
        for tile in keTiles:
            keValues.append(MTile.getValue(tile))
        keValues.sort()
        
        hasSanTongKe = False
        if (keValues[0] == keValues[1]) and (keValues[1] == keValues[2]):
            hasSanTongKe = True
            
        if (keValues[1] == keValues[2]) and (keValues[2] == keValues[3]):
            hasSanTongKe = True
            
        if not hasSanTongKe:
            return False
        
        for tile in removes:
            handTiles.remove(tile)
            
        return MWin.isHu(handTiles)
        
    
    def isYiSeSiJieGao(self):
        '''
        一色四节高
        前提条件，无，牌型保证可以胡牌
        '''
        keTiles = []
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            keTiles.append(gang['pattern'][0])
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tilesArr = MTile.changeTilesToValueArr(handTiles)
        for tile in handTiles:
            if (tilesArr[tile] == 3) and (tile not in keTiles):
                keTiles.append(tile)
        
        keTiles.sort()
        leftTiles = filter(lambda x:(x not in keTiles), handTiles)
        ftlog.debug('MTilePatternChecker.isYiSeSiJieGao tiles:', self.playerAllTiles
                    , ' keTiles:', keTiles
                    , ' leftTiles:', leftTiles)
        return (len(keTiles) == 4) \
                and (len(leftTiles) == 2) \
                and (leftTiles[0] == leftTiles[1]) \
                and (keTiles[1] == (keTiles[0] + 1)) \
                and (keTiles[2] == (keTiles[0] + 2)) \
                and (keTiles[3] == (keTiles[0] + 3))
                
    def isYiSeSanJieGao(self):
        '''
        一色三节高
        
        前提条件：无，去掉三节高后，剩下的牌可以胡
        '''
        # 有吃，不算三节高
        chis = self.playerAllTiles[MHand.TYPE_CHI]
        if len(chis) > 0:
            return False
        
        keTiles = []
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            keTiles.append(gang['pattern'][0])
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tilesArr = MTile.changeTilesToValueArr(handTiles)
        for tile in handTiles:
            if (tilesArr[tile] == 3) and (tile not in keTiles):
                keTiles.append(tile)
        
        keTiles.sort()
        kes = []
        if len(keTiles) == 3:
            kes.append(keTiles)
            if (keTiles[1] != keTiles[0] + 1) or (keTiles[2] != keTiles[0] + 2):
                return False
            
        if len(keTiles) == 4:
            kes.append(keTiles[:3])
            kes.append(keTiles[-3:])
        
        for ke in kes:
            if (ke[1] != ke[0] + 1) or (ke[2] != ke[0] + 2):
                continue
            
            leftTiles = filter(lambda x:(x not in ke), handTiles)
            ftlog.debug('MTilePatternChecker.isYiSeSanJieGao tiles:', self.playerAllTiles
                        , ' ke:', ke
                        , ' leftTiles:', leftTiles)
            if MWin.isHu(leftTiles):
                return True
            
        return False
    
    def isHunSiJieGao(self):
        '''
        混四节
        前提条件，胡牌，不是一色四节高
        '''
        keTiles = []
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            keTiles.append(gang['pattern'][0])
            
        pengs = self.playerAllTiles[MHand.TYPE_PENG]
        for peng in pengs:
            keTiles.append(peng[0])
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tilesArr = MTile.changeTilesToValueArr(handTiles)
        for tile in handTiles:
            if (tilesArr[tile] == 3) and (tile not in keTiles):
                keTiles.append(tile)
        
        keTiles.sort()
        colorCount = MTile.getColorCount(MTile.changeTilesToValueArr(keTiles))
        if colorCount == 1:
            return False
        
        vTiles = []
        for tile in keTiles:
            vTiles.append(MTile.getValue(tile))
        vTiles.sort()
            
        leftTiles = filter(lambda x:(x not in keTiles), handTiles)
        ftlog.debug('MTilePatternChecker.isHunSiJieGao tiles:', self.playerAllTiles
                    , ' keTiles:', keTiles
                    , ' vTiles:', vTiles
                    , ' leftTiles:', leftTiles)
        
        return (len(keTiles) == 4) \
                and (len(leftTiles) == 2) \
                and (leftTiles[0] == leftTiles[1]) \
                and (vTiles[1] == (vTiles[0] + 1)) \
                and (vTiles[2] == (vTiles[0] + 2)) \
                and (vTiles[3] == (vTiles[0] + 3))
                
    def isHunSanJieGao(self):
        '''
        混三节
        前提条件，胡牌，不是一色四节高
        '''
        keTiles = []
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            keTiles.append(gang['pattern'][0])
            
        pengs = self.playerAllTiles[MHand.TYPE_PENG]
        for peng in pengs:
            keTiles.append(peng[0])
        
        handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tilesArr = MTile.changeTilesToValueArr(handTiles)
        for tile in handTiles:
            if (tilesArr[tile] == 3) and (tile not in keTiles):
                keTiles.append(tile)
        
        keTiles.sort()
        colorCount = MTile.getColorCount(MTile.changeTilesToValueArr(keTiles))
        if colorCount == 1:
            return False
        
        vTiles = []
        for tile in keTiles:
            vTiles.append(MTile.getValue(tile))
        vTiles.sort()
            
        leftTiles = filter(lambda x:(x not in keTiles), handTiles)
        ftlog.debug('MTilePatternChecker.isHunSiJieGao tiles:', self.playerAllTiles
                    , ' keTiles:', keTiles
                    , ' vTiles:', vTiles
                    , ' leftTiles:', leftTiles)
        
        if not MWin.isHu(leftTiles):
            return False
        
        return (len(keTiles) == 3) \
                and (vTiles[1] == (vTiles[0] + 1)) \
                and (vTiles[2] == (vTiles[0] + 2))
    
    def isSanSeSanJieGao(self):
        '''
        三色三节高
        
        前提条件：胡牌，去掉三节高后，剩下的牌可以胡
        '''
        sans = [
            [0],
            [1, 11, 21],
            [2, 12, 22],
            [3, 13, 23],
            [4, 14, 24],
            [5, 15, 25],
            [6, 16, 26],
            [7, 17, 27],
            [8, 18, 28],
            [9, 19, 29]
        ]
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            tile = gang['pattern'][0]
            sans[MTile.getValue(tile)].remove(tile)
         
        pengs = self.playerAllTiles[MHand.TYPE_PENG]   
        for peng in pengs:
            tile = peng[0]
            sans[MTile.getValue(tile)].remove(tile)

        for san in sans:
            if san[0] == 0:
                continue
            
            hasGao = True
            handTiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            for tile in san:
                if not hasGao:
                    break
                
                tArr = [tile, tile, tile]
                for _tile in tArr:
                    if _tile not in handTiles:
                        hasGao = False
                        break
            
            if hasGao and MWin.isHu(handTiles):
                return True
        
        return False
                
    def isYiSeSiTongShun(self):
        '''
        一色四同顺
        前提条件，无。牌型保证可以胡牌
        
        拷贝手牌和吃牌，组成四通顺牌型
        '''
        rTiles = MHand.copyTiles(self.playerAllTiles, [MHand.TYPE_HAND, MHand.TYPE_CHI, MHand.TYPE_HU])
        if len(rTiles) != 14:
            return False
        
        tileArr = MTile.changeTilesToValueArr(rTiles)
        sTiles = []
        for tile in rTiles:
            if tileArr[tile] == 4 and tile not in sTiles:
                sTiles.append(tile)
        sTiles.sort()
        leftTiles = filter(lambda x:(x not in sTiles), rTiles)
        ftlog.debug('MTilePatternChecker.isYiSeSiTongShun tiles:', rTiles
                    , ' sTiles:', sTiles
                    , ' leftTiels:', leftTiles)
        return len(sTiles) == 3 \
                and (sTiles[1] == (sTiles[0] + 1)) \
                and (sTiles[2] == (sTiles[0] + 2)) \
                and len(leftTiles) == 2 \
                and leftTiles[0] == leftTiles[1]
                
    def isYiSeSanTongShun(self):
        '''
        一色三同顺
        前提条件，无。牌型保证可以胡牌
        
        拷贝手牌和吃牌，组成三同顺牌型
        '''
        chis = self.playerAllTiles[MHand.TYPE_CHI]
        if len(chis) == 0:
            return False
        
        rTiles = MHand.copyTiles(self.playerAllTiles, [MHand.TYPE_HAND, MHand.TYPE_CHI, MHand.TYPE_HU])
        tileArr = MTile.changeTilesToValueArr(rTiles)
        sTiles = []
        for tile in rTiles:
            if tileArr[tile] >= 3 and tile not in sTiles:
                sTiles.append(tile)
        sTiles.sort()
        
        ss = []
        if len(sTiles) == 3:
            ss.append(sTiles)
            
        if len(sTiles) == 4:
            ss.append(sTiles[:3])
            ss.append(sTiles[-3:])
        
        for s in ss:
            if (s[1] != s[0] + 1) or (s[2] != s[0] + 2):
                continue
            
            rsTiles = [s[0], s[0], s[0], s[1], s[1], s[1], s[2], s[2], s[2]]
            leftTiles = copy.deepcopy(rTiles)
            for rt in rsTiles:
                leftTiles.remove(rt)
                
            ftlog.debug('MTilePatternChecker.isYiSeSanTongShun tiles:', rTiles
                        , ' s:', s
                        , ' leftTiels:', leftTiles)
            
            if MWin.isHu(leftTiles):
                return True
            
        return False
    
    def isSanSeSanTongShun(self):
        '''
        三色三同顺
        前提条件，胡牌
        
        拷贝手牌和吃牌，组成三同顺牌型
        '''
        sans = [
            [[0]]
            , [[1, 2, 3], [11, 12, 13], [21, 22, 23]]
            , [[12, 13, 14], [22, 23, 24], [2, 3, 4]]
            , [[3, 4, 5], [13, 14, 15], [23, 24, 25]]
            , [[4, 5, 6], [14, 15, 16], [24, 25, 26]]
            , [[5, 6, 7], [15, 16, 17], [25, 26, 27]]
            , [[6, 7, 8], [16, 17, 18], [26, 27, 28]]
            , [[7, 8, 9], [17, 18, 19], [27, 28, 29]]
        ]
        chis = self.playerAllTiles[MHand.TYPE_CHI]
        for chi in chis:
            chi.sort()
            if chi in sans[MTile.getValue(chi[0])]:
                sans[MTile.getValue(chi[0])].remove(chi)
            
        for san in sans:
            hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            hasShun = True
            for chi in san:
                if not hasShun:
                    break
                
                for tile in chi:
                    if tile in hands:
                        hands.remove(tile)
                    else:
                        hasShun = False
                        break
            if MWin.isHu(hands):
                return True
        return False
                
    def isYiSeSiBuGao(self):
        '''
        一色四步高
        123 345 567 789
        密码：
        112121211 + 将
        [1,2,3,3,4,5,5,6,7,7,8,9]
        
        123 234 345 456
        [1,2,2,3,3,3,4,4,4,5,5,6]
        [2,3,3,4,4,4,5,5,5,6,6,7]
        [3,4,4,5,5,5,6,6,6,7,7,8]
        [4,5,5,6,6,6,7,7,7,8,8,9]
        密码：
        123321 + 将
        '''
        rTiles = MHand.copyTiles(self.playerAllTiles, [MHand.TYPE_HAND, MHand.TYPE_CHI, MHand.TYPE_HU])
        if len(rTiles) != 14:
            return False
        
        specialsWan = [
            [1, 2, 3, 3, 4, 5, 5, 6, 7, 7, 8, 9],
            [1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6],
            [2, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7],
            [3, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 8],
            [4, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 9]
        ]
        
        specials = []
        for code1Wan in specialsWan:
            specials.append(code1Wan)
            
            code1Tong = copy.deepcopy(code1Wan)
            for code in code1Tong:
                code += 10
            specials.append(code1Tong)
            
            code1Tiao = copy.deepcopy(code1Wan)
            for code in code1Tiao:
                code += 20
            specials.append(code1Tiao)
            
        for special in specials:
            ts = copy.deepcopy(rTiles)
            for tile in special:
                if tile not in ts:
                    continue
                else:
                    ts.remove(tile)
            if (len(ts) == 2) and (ts[0] == ts[1]):
                return True
            
        return False
    
    def isYiSeSanBuGao(self):
        '''
        一色三步高
        123 345 567
        234 456 678
        357 567 789
        
        密码：
        1121211
        211 + 将
        [1,2,3,3,4,5,5,6,7,7,8,9]
        
        123 234 345
        567 678 789
        [1,2,2,3,3,3,4,4,5]
        
        密码：
        12321
        '''
        rTiles = MHand.copyTiles(self.playerAllTiles, [MHand.TYPE_HAND, MHand.TYPE_CHI, MHand.TYPE_HU])
        if len(rTiles) != 14:
            return False
        
        specialsWan = [
            [1, 2, 3, 3, 4, 5, 5, 6, 7],
            [1 + 1, 2 + 1, 3 + 1, 3 + 1, 4 + 1, 5 + 1, 5 + 1, 6 + 1, 7 + 1],
            [1 + 2, 2 + 2, 3 + 2, 3 + 2, 4 + 2, 5 + 2, 5 + 2, 6 + 2, 7 + 2],
            [1, 2, 2, 3, 3, 3, 4, 4, 5],
            [1 + 1, 2 + 1, 2 + 1, 3 + 1, 3 + 1, 3 + 1, 4 + 1, 4 + 1, 5 + 1],
            [1 + 2, 2 + 2, 2 + 2, 3 + 2, 3 + 2, 3 + 2, 4 + 2, 4 + 2, 5 + 2],
            [1 + 3, 2 + 3, 2 + 3, 3 + 3, 3 + 3, 3 + 3, 4 + 3, 4 + 3, 5 + 3],
            [1 + 4, 2 + 4, 2 + 4, 3 + 4, 3 + 4, 3 + 4, 4 + 4, 4 + 4, 5 + 4]
        ]
        
        specials = []
        for code1Wan in specialsWan:
            specials.append(code1Wan)
            
            code1Tong = copy.deepcopy(code1Wan)
            for code in code1Tong:
                code += 10
            specials.append(code1Tong)
            
            code1Tiao = copy.deepcopy(code1Wan)
            for code in code1Tiao:
                code += 20
            specials.append(code1Tiao)
            
        for special in specials:
            ts = copy.deepcopy(rTiles)
            isOK = True
            for tile in special:
                if tile not in ts:
                    break
                
                ts.remove(tile)
            if not isOK:
                continue
            
            if MWin.isHu(ts):
                return True
            
        return False
    
    def isSanSeSanBuGao(self):
        '''
        三色三步高
        123 121314 232425
        567 678 789
        [1,2,2,3,3,3,4,4,5]
        
        密码：
        12321
        '''
        specials = [
            [[1, 2, 3], [12, 13, 14], [23, 24, 25]],
            [[1, 2, 3], [22, 23, 24], [13, 14, 15]],
            [[11, 12, 13], [2, 3, 4], [23, 24, 25]],
            [[11, 12, 13], [22, 23, 24], [3, 4, 5]],
            [[21, 22, 23], [2, 3, 4], [13, 14, 15]],
            [[21, 22, 23], [12, 13, 14], [3, 4, 5]],
            
            [[2, 3, 4], [13, 14, 15], [24, 25, 26]],
            [[2, 3, 4], [23, 24, 25], [14, 15, 16]],
            [[12, 13, 14], [23, 24, 25], [4, 5, 6]],
            [[12, 13, 14], [3, 4, 5], [24, 25, 26]],
            [[22, 23, 24], [23, 24, 25], [4, 5, 6]],
            [[22, 23, 24], [3, 4, 5], [14, 15, 16]],
            
            [[3, 4, 5], [14, 15, 16], [25, 26, 27]],
            [[3, 4, 5], [24, 25, 26], [15, 16, 17]],
            [[13, 14, 15], [24, 25, 26], [5, 6, 7]],
            [[13, 14, 15], [4, 5, 6], [25, 26, 27]],
            [[23, 24, 25], [14, 15, 16], [5, 6, 7]],
            [[23, 24, 25], [4, 5, 6], [15, 16, 17]],
            
            [[4, 5, 6], [15, 16, 17], [26, 27, 28]],
            [[4, 5, 6], [25, 26, 27], [16, 17, 18]],
            [[14, 15, 16], [25, 26, 27], [6, 7, 8]],
            [[14, 15, 16], [5, 6, 7], [26, 27, 28]],
            [[24, 25, 26], [15, 16, 17], [6, 7, 8]],
            [[24, 25, 26], [5, 6, 7], [16, 17, 18]],
            
            [[5, 6, 7], [16, 17, 18], [27, 28, 29]],
            [[5, 6, 7], [26, 27, 28], [17, 18, 19]],
            [[15, 16, 17], [26, 27, 28], [7, 8, 9]],
            [[15, 16, 17], [6, 7, 8], [27, 28, 29]],
            [[25, 26, 27], [16, 17, 18], [7, 8, 9]],
            [[25, 26, 27], [6, 7, 8], [17, 18, 19]]
        ]
        
        chis = self.playerAllTiles[MHand.TYPE_CHI]
        for chi in chis: 
            chi.sort()
            for special in specials:
                if chi in special:
                    special.remove(chi)
        
        for special in specials:
            hasShun = True
            hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            for chi in special:
                for tile in chi:
                    if tile not in hands:
                        hasShun = False
                        break
            if hasShun and MWin.isHu(hands):
                return True
            
        return False
    
    def isHunSiBuGao(self):
        '''
        混四步
        都变成万字牌，是一色四不高
        '''
        hands = self.playerAllTiles[MHand.TYPE_HAND]
        rArr = MTile.changeTilesToValueArr(hands)
        jiangs = []
        for tile in hands:
            if (rArr[tile] >= 2) and (tile not in jiangs):
                jiangs.append(tile)
                tiles = copy.deepcopy(self.playerAllTiles)
                tiles[MHand.TYPE_HAND].remove(tile)
                tiles[MHand.TYPE_HAND].remove(tile)
                
                rTiles = MHand.copyTiles(tiles, [MHand.TYPE_HAND, MHand.TYPE_CHI, MHand.TYPE_HU])
                if len(rTiles) != 12:
                    continue
                            
    
                wanTiles = []
                for tile in rTiles:
                    wanTiles.append(MTile.getValue(tile))
                wanTiles.sort()
                
                specialsWan = [
                    [1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6],
                    [2, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7],
                    [3, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 8],
                    [4, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 9]
                ]
    
                specials = specialsWan
                for special in specials:
                    if special == wanTiles:
                        return True
        return False
    
    def isShiSanBuKao(self):
        '''
        十三不靠
        [3,6,9,12,15,18,21,24,27,31,32,33,34,35,36,37]
        十六张牌中的十四张，即可成胡
        
        前提：无
        '''
        specials = [
            [3, 6, 9, 12, 15, 18, 21, 24, 27, 31, 32, 33, 34, 35, 36, 37],
            [3, 6, 9, 22, 25, 28, 11, 14, 17, 31, 32, 33, 34, 35, 36, 37],
            [2, 5, 8, 11, 14, 17, 23, 26, 29, 31, 32, 33, 34, 35, 36, 37],
            [2, 5, 8, 21, 24, 27, 13, 16, 19, 31, 32, 33, 34, 35, 36, 37],
            [1, 4, 7, 12, 15, 18, 23, 26, 29, 31, 32, 33, 34, 35, 36, 37],
            [1, 4, 7, 22, 25, 28, 13, 16, 19, 31, 32, 33, 34, 35, 36, 37]
        ]
        
        for special in specials:
            hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            for tile in special:
                if tile in hands:
                    hands.remove(tile)
            if len(hands) == 0:
                return True
            
        return False
                
    def isQiXingBuKao(self):
        '''
        七星不靠
        十三不靠中，风牌箭牌七张牌集齐
        
        前提：十三不靠
        '''
        if not self.isShiSanBuKao():
            return False
        
        mustTiles = [31, 32, 33, 34, 35, 36, 37]
        hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        for mt in mustTiles:
            if mt not in hands:
                return False
        
        return True
    
    def isQuanShuangKe(self):
        '''
        全双刻
        
        前提：碰碰胡
        '''
        if not self.isPengpenghu():
            return False
        
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        for tile in tiles:
            if tile >= MTile.TILE_DONG_FENG:
                return False
            
            if tile % 2 > 0:
                return False
        
        return True
    
    def isQuanDa(self):
        '''
        全大
        
        前提条件：胡牌
        '''
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        for tile in tiles:
            if tile >= MTile.TILE_DONG_FENG:
                return False
            
            if MTile.getValue(tile) not in [7, 8, 9]:
                return False
        
        return True
    
    def isQuanZhong(self):
        '''
        全中
        
        前提：胡牌
        '''
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        for tile in tiles:
            if tile >= MTile.TILE_DONG_FENG:
                return False
            
            if MTile.getValue(tile) not in [4, 5, 6]:
                return False
        
        return True
    
    def isQuanXiao(self):
        '''
        全小
        
        前提：胡牌
        '''
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        for tile in tiles:
            if tile >= MTile.TILE_DONG_FENG:
                return False
            
            if MTile.getValue(tile) not in [1, 2, 3]:
                return False
        
        return True
    
    def isQingLong(self):
        '''
        青龙
        
        也叫：一条龙
        
        前提条件：无
        '''
        longShuns = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [11, 12, 13],
            [14, 15, 16],
            [17, 18, 19],
            [21, 22, 23],
            [24, 25, 26],
            [27, 28, 29]   
        ]
        
        hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        chis = self.playerAllTiles[MHand.TYPE_CHI]
        for chi in chis:
            if chi in longShuns:
                hands.extend(chi)
        
        ftlog.debug('MTilePatternChecker.isQingLong hands:', hands)
        
        longs = [
             [1, 2, 3, 4, 5, 6, 7, 8, 9],
             [11, 12, 13, 14, 15, 16, 17, 18, 19],
             [21, 22, 23, 24, 25, 26, 27, 28, 29]  
        ]
        
        for _long in longs:
            nHands = copy.deepcopy(hands)
            hasLong = True
            for tile in _long:
                if tile not in nHands:
                    hasLong = False
                    break
                
                nHands.remove(tile)
                
            if hasLong and MWin.isHu(nHands):
                return True
            
        return False
    
    def isHuaLong(self):
        '''
        花龙
        
        由三张牌的123 456 789组成
        '''
        longShuns = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [11, 12, 13],
            [14, 15, 16],
            [17, 18, 19],
            [21, 22, 23],
            [24, 25, 26],
            [27, 28, 29]   
        ]
        
        hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        chis = self.playerAllTiles[MHand.TYPE_CHI]
        for chi in chis:
            if chi in longShuns:
                hands.extend(chi)
        
        ftlog.debug('MTilePatternChecker.isQingLong hands:', hands)
        
        longs = [
            [1, 2, 3, 14, 15, 16, 27, 28, 29],
            [1, 2, 3, 24, 25, 26, 17, 18, 19],
             
            [4, 5, 6, 11, 12, 13, 27, 28, 29],
            [4, 5, 6, 21, 22, 23, 17, 18, 19],
             
            [7, 8, 9, 14, 15, 16, 21, 22, 23],
            [7, 8, 9, 11, 12, 13, 24, 25, 26]  
        ]
        
        for _long in longs:
            nHands = copy.deepcopy(hands)
            hasLong = True
            for tile in _long:
                if tile not in nHands:
                    hasLong = False
                    break
                
                nHands.remove(tile)
                
            if hasLong and MWin.isHu(nHands):
                return True
            
        return False
    
    def isQuanDaiFive(self):
        '''
        全带五
        
        前提：无，判断方法保证是可以胡牌的
        '''
        chis = self.playerAllTiles[MHand.TYPE_CHI]
        for chi in chis:
            hasFive = False
            for tile in chi:
                if MTile.getValue(tile) == 5:
                    hasFive = True
                    break
            
            if not hasFive:
                return False
            
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs:
            if MTile.getValue(gang['pattern'][0] != 5):
                return False
            
        hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        fives = [MTile.TILE_FIVE_WAN, MTile.TILE_FIVE_TONG, MTile.TILE_FIVE_TIAO]
        for five in fives:
            if five not in hands:
                continue
            
            while ((five - 2) in hands) and ((five - 1) in hands) and (five in hands):
                hands.remove(five - 2)
                hands.remove(five - 1)
                hands.remove(five)
            
            while ((five + 2) in hands) and ((five + 1) in hands) and (five in hands):
                hands.remove(five)
                hands.remove(five + 1)
                hands.remove(five + 2)
                
            while ((five - 1) in hands) and (five in hands) and ((five + 1) in hands):
                hands.remove(five)
                hands.remove(five - 1)
                hands.remove(five + 1)
                
        # 剩下的牌都是5，而且可以胡
        for tile in hands:
            if MTile.getValue(tile) != 5:
                return False
            
        return MWin.isHu(hands)
    
    def isSanSeShuangLongHui(self):
        '''
        三色双龙会
        
        两种花色的123 789两顺，配另外一个花色的对5
        '''
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        wans = MTile.filterTiles(tiles, MTile.TILE_WAN)
        tongs = MTile.filterTiles(tiles, MTile.TILE_TONG)
        tiaos = MTile.filterTiles(tiles, MTile.TILE_TIAO)
        wanLength = len(wans)
        if wanLength != 6 or wanLength != 2:
            return False

        if wanLength == 6:
            wans.sort()
            if wans != [MTile.TILE_ONE_WAN, MTile.TILE_TWO_WAN, MTile.TILE_THREE_WAN, MTile.TILE_SEVEN_WAN, MTile.TILE_EIGHT_WAN, MTile.TILE_NINE_WAN]:
                return False
        
        if wanLength == 2:
            if wans[0] != MTile.TILE_FIVE_WAN or wans[1] != MTile.TILE_FIVE_WAN:
                return False
            
        tongLength = len(tongs)
        if tongLength != 6 or tongLength != 2:
            return False
        
        if tongLength == 6:
            tongs.sort()
            if tongs != [MTile.TILE_ONE_TONG, MTile.TILE_TWO_TONG, MTile.TILE_THREE_TONG, MTile.TILE_SEVEN_TONG, MTile.TILE_EIGHT_TONG, MTile.TILE_NINE_TONG]:
                return False
        
        if tongLength == 2:
            if tongs[0] != MTile.TILE_FIVE_TONG or tongs[1] != MTile.TILE_FIVE_TONG:
                return False
            
        tiaoLength = len(tiaos)
        if tiaoLength != 6 or tiaoLength != 2:
            return False
        
        if tiaoLength == 6:
            tiaos.sort()
            if tiaos != [MTile.TILE_ONE_TIAO, MTile.TILE_TWO_TIAO, MTile.TILE_THREE_TIAO, MTile.TILE_SEVEN_TIAO, MTile.TILE_EIGHT_TIAO, MTile.TILE_NINE_TIAO]:
                return False
        
        if tiaoLength == 2:
            if tiaos[0] != MTile.TILE_FIVE_TONG or tiaos[1] != MTile.TILE_FIVE_TONG:
                return False
            
        return True
    
    def isZuHeLong(self):
        '''
        组合龙
        '''
        specials = [
            [3, 6, 9, 12, 15, 18, 21, 24, 27],
            [3, 6, 9, 22, 25, 28, 11, 14, 17],
            [2, 5, 8, 11, 14, 17, 23, 26, 29],
            [2, 5, 8, 21, 24, 27, 13, 16, 19],
            [1, 4, 7, 12, 15, 18, 23, 26, 29],
            [1, 4, 7, 22, 25, 28, 13, 16, 19]
        ]
        
        for special in specials:
            tiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            isNotOK = False
            for tile in special:
                if tile not in tiles:
                    isNotOK = True
                    break
                tiles.remove(tile)
                
            if isNotOK:
                continue
                
            if len(tiles) != 2 and len(tiles) != 5:
                continue
            
            if MWin.isHu(tiles):
                return True
            
        return False
    
    def isBiggerThanFive(self):
        '''
        大于五
        
        前提条件：胡牌
        '''
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        for tile in tiles:
            if tile > MTile.TILE_DONG_FENG:
                return False
            
            if MTile.getValue(tile) <= 5:
                return False
            
        return True
    
    def isSmallerThanFive(self):
        '''
        小于五
        '''
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        for tile in tiles:
            if tile > MTile.TILE_DONG_FENG:
                return False
            
            if MTile.getValue(tile) >= 5:
                return False
        return True
    
    def isTuiBuDao(self):
        '''
        推不倒
        
        前提：胡牌
        '''
        samples = [MTile.TILE_TWO_TIAO
            , MTile.TILE_FOUR_TIAO
            , MTile.TILE_FIVE_TIAO
            , MTile.TILE_SIX_TIAO
            , MTile.TILE_EIGHT_TIAO
            , MTile.TILE_NINE_TIAO
            
            , MTile.TILE_ONE_TONG
            , MTile.TILE_TWO_TONG
            , MTile.TILE_THREE_TONG
            , MTile.TILE_FOUR_TONG
            , MTile.TILE_FIVE_TONG
            , MTile.TILE_EIGHT_TONG
            , MTile.TILE_NINE_TONG
            
            , MTile.TILE_BAI_BAN
        ]
        
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        for tile in tiles:
            if tile not in samples:
                return False
        return True
    
    def isWuMenQi(self):
        '''
        五门齐
        
        前提：胡牌
        '''
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        tilesWan = MTile.filterTiles(tiles, MTile.TILE_WAN)
        if len(tilesWan) <= 0:
            return False
        
        tilesTong = MTile.filterTiles(tiles, MTile.TILE_TONG)
        if len(tilesTong) <= 0:
            return False
        
        tilesTiao = MTile.filterTiles(tiles, MTile.TILE_TIAO)
        if len(tilesTiao) <= 0:
            return False
        
        tilesFeng = MTile.filterTiles(tiles, MTile.TILE_FENG)
        if len(tilesFeng) <= 0:
            return False
        
        tilesArrow = []
        for tile in tilesFeng:
            if MTile.isArrow(tile):
                tilesArrow.append(tile)
        if len(tilesArrow) <= 0:
            return False
        
        if len(tilesFeng) == len(tilesArrow):
            return False
        
        return True
    
    def isShuangAnGang(self):
        '''
        双暗杠
        
        前提条件：胡牌
        '''
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        anGang = 0
        for gang in gangs:
            if gang['style'] == MPlayerTileGang.AN_GANG:
                anGang += 1
        return anGang == 2
    
    def isShuangMingGang(self):
        '''
        双明杠
        
        前提条件：胡牌
        '''
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        anGang = 0
        for gang in gangs:
            if gang['style'] == MPlayerTileGang.MING_GANG:
                anGang += 1
        return anGang == 2
    
    def isShuangJianKe(self):
        '''
        双箭刻
        
        前提条件：胡牌
        '''
        tiles = MHand.copyTiles(self.playerAllTiles, [MHand.TYPE_HAND, MHand.TYPE_PENG, MHand.TYPE_GANG])
        tileArr = MTile.changeTilesToValueArr(tiles)
        arrCount = 0
        if tileArr[MTile.TILE_HONG_ZHONG] >= 3:
            arrCount += 1
            
        if tileArr[MTile.TILE_FA_CAI] >= 3:
            arrCount += 1
            
        if tileArr[MTile.TILE_BAI_BAN] >= 3:
            arrCount += 1
            
        return (arrCount == 2)
    
    def isPingHu(self, winPattern, laizi=[]):
        '''
        平胡
        
        四副顺子+一对将
        
        前提条件：无
        '''
        keCount = len(self.playerAllTiles[MHand.TYPE_PENG]) + len(self.playerAllTiles[MHand.TYPE_GANG])
        if keCount > 0:
            ftlog.debug('MTilePatternChecker.isPingHu result: False')
            return False

        if len(laizi) > 0:
            #有赖子的情况下，如果两张一样且＝＝赖子，不返回false
            for p in winPattern:
                if len(p) == 3:
                    if p[0] == p[1] !=laizi[0] \
                            or p[0] == p[2] !=laizi[0] \
                            or p[1] == p[2] !=laizi[0] :
                        ftlog.debug('MTilePatternChecker.isPingHu result: False')
                        return False
        else:
            for p in winPattern:
                if len(p) == 3:
                    if p[0] == p[1] or p[0] == p[2] or p[1] == p[2]:
                        ftlog.debug('MTilePatternChecker.isPingHu result: False')
                        return False

        ftlog.debug('MTilePatternChecker.isPingHu result: True')
        return True
    
    def isSiGuiYi(self):
        '''
        四归一
        包含四张相同的牌，但不能是杠牌
        
        前提：胡牌
        '''
        tiles = MHand.copyTiles(self.playerAllTiles, [MHand.TYPE_HAND, MHand.TYPE_CHI, MHand.TYPE_HU])
        tileArr = MTile.changeTilesToValueArr(tiles)
        for tile in tiles:
            if tileArr[tile] == 4:
                return True
        return False
    
    def is258Jiang(self):
        '''
        258将
        
        前提条件：
        无
        '''
        jiangPatterns = [
            [MTile.TILE_TWO_WAN, MTile.TILE_TWO_WAN]
            , [MTile.TILE_FIVE_WAN, MTile.TILE_FIVE_WAN]
            , [MTile.TILE_EIGHT_WAN, MTile.TILE_EIGHT_WAN]
            , [MTile.TILE_TWO_TONG, MTile.TILE_TWO_TONG]
            , [MTile.TILE_FIVE_TONG, MTile.TILE_FIVE_TONG]
            , [MTile.TILE_EIGHT_TONG, MTile.TILE_EIGHT_TONG]
            , [MTile.TILE_TWO_TIAO, MTile.TILE_TWO_TIAO]
            , [MTile.TILE_FIVE_TIAO, MTile.TILE_FIVE_TIAO]
            , [MTile.TILE_EIGHT_TIAO, MTile.TILE_EIGHT_TIAO]
        ]
        
        for jiangPat in jiangPatterns:
            hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            result, _ = MWin.isHuWishSpecialJiang(hands, jiangPat)
            if result:
                return True
        return False
    
    def is19Jiang(self):
        '''
        幺九头
        
        前提条件：无
        '''
        jiangPatterns = [
            [MTile.TILE_ONE_WAN, MTile.TILE_ONE_WAN]
            , [MTile.TILE_NINE_WAN, MTile.TILE_NINE_WAN]
            , [MTile.TILE_ONE_TONG, MTile.TILE_ONE_TONG]
            , [MTile.TILE_NINE_TONG, MTile.TILE_NINE_TONG]
            , [MTile.TILE_ONE_TIAO, MTile.TILE_ONE_TIAO]
            , [MTile.TILE_NINE_TIAO, MTile.TILE_NINE_TIAO]
        ]
        
        for jiangPat in jiangPatterns:
            hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            result, _ = MWin.isHuWishSpecialJiang(hands, jiangPat)
            if result:
                return True
        return False
    
    def isBian(self):
        '''
        边张
        12和3，89胡7
        
        也叫：
        三七边
        
        前提条件：无
        '''
        huTile = self.playerAllTiles[MHand.TYPE_HU]
        if huTile >= MTile.TILE_DONG_FENG:
            return False
        
        if MTile.getValue(huTile) == 7:
            hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            if huTile in hands and (huTile + 1) in hands and (huTile + 2) in hands:
                hands.remove(huTile)
                hands.remove(huTile + 1)
                hands.remove(huTile + 2)
                if MWin.isHu(hands):
                    return True
                
        if MTile.getValue(huTile) == 3:
            hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            if huTile in hands and (huTile - 1) in hands and (huTile - 2) in hands:
                hands.remove(huTile)
                hands.remove(huTile - 1)
                hands.remove(huTile - 2)
                if MWin.isHu(hands):
                    return True
        
        return False
    
    def isKan(self):
        '''
        坎张
        也叫
        1)嵌张
        
        前提条件：无
        '''
        huTile = self.playerAllTiles[MHand.TYPE_HU]
        if huTile >= MTile.TILE_DONG_FENG:
            return False
        
        hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        if huTile in hands and (huTile + 1) in hands and (huTile - 1) in hands:
            hands.remove(huTile)
            hands.remove(huTile - 1)
            hands.remove(huTile + 1)
            if MWin.isHu(hands):
                return True
        
        return False
    
    def isDanDiao(self):
        '''
        单调
        
        前提条件：胡牌
        '''
        huTile = self.playerAllTiles[MHand.TYPE_HU]
        hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        result, _ = MWin.isHuWishSpecialJiang(hands, [huTile, huTile])
        if result:
            return True
        return False
    
    def hasMingGang(self):
        '''
        明杠
        
        前提条件：胡牌
        '''
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs: 
            if gang['stype'] == MPlayerTileGang.MING_GANG:
                return True
            
        return False
    
    def hasAnGang(self):
        '''
        暗杠
        
        前提条件：胡牌
        '''
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs: 
            if gang['stype'] == MPlayerTileGang.AN_GANG:
                return True
            
        return False
    
    def isWuZi(self):
        '''
        无字
        
        前提条件：胡牌
        '''
        tiles = MHand.copyAllTilesToList(self.playerAllTiles)
        for tile in tiles:
            if MTile.isFeng(tile) or MTile.isArrow(tile):
                return False
            
        return True
    
    def hasYaoJiuKe(self):
        '''
        幺九刻
        有幺/九组成的刻字
        '''
        gangs = self.playerAllTiles[MHand.TYPE_GANG]
        for gang in gangs: 
            tile = gang['pattern']
            if ((MTile.getValue(tile) == 1) or (MTile.getValue(tile) == 9)) and tile < MTile.TILE_DONG_FENG:
                return True
          
        pengs = self.playerAllTiles[MHand.TYPE_PENG]  
        for peng in pengs:
            tile = peng[0]
            if ((MTile.getValue(tile) == 1) or (MTile.getValue(tile) == 9)) and tile < MTile.TILE_DONG_FENG:
                return True
            
        yaoJiuKes = [
            [1, 1, 1]
            , [9, 9, 9] 
            , [11, 11, 11]
            , [19, 19, 19]
            , [21, 21, 21]
            , [29, 29, 29]    
        ]
        for ke in yaoJiuKes:
            hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
            hasKe = True
            for tile in ke:
                if tile not in hands:
                    hasKe = False
                    break
            if hasKe and MWin.isHu(hands):
                return True
            
        return False
    
    def isQueYiMen(self):
        '''
        缺一门
        万桶条有两个花色，缺少一个花色
        '''
        tiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        tilesArr = MTile.changeTilesToValueArr(tiles)
        color = MTile.getColorCountArr(tilesArr)
        return ((color[MTile.TILE_WAN] + color[MTile.TILE_TONG] + color[MTile.TILE_TIAO]) == 2)
        
             
    def hasKe(self):
        pengCount = len(self.playerAllTiles[MHand.TYPE_PENG]) + len(self.playerAllTiles[MHand.TYPE_GANG])
        if pengCount > 0:
            return True
        hands = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tilesArr = MTile.changeTilesToValueArr(hands)
        for tile in hands:
            if tilesArr[tile] >= 3:
                return True
        return False

    def hasKeTile(self, ketile):
        handTile = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        tilesArr = MTile.changeTilesToValueArr(handTile)
        if tilesArr[ketile] >= 3:
            return True
        return False
    
    def calcFanPatternTing(self):
        '''
        计算听牌时的基本番型
        '''
        return 1
    
    def calcFanPattern(self):
        '''
        计算基本番型的数值
        '''
        return 1

def testSiBuGao():
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[15, 15, 1, 2, 3, 4, 5, 6], [[2, 3, 4], [3, 4, 5]], [], [], [], []])
    result = checker.isYiSeSiBuGao()
    print 'result:', result
    
def testSanJieGao():
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[15, 15, 2, 2, 2, 3, 3, 3, 4, 4, 4], [[7, 8, 9]], [], [], [], []])
    result = checker.isYiSeSanJieGao()
    print 'result:', result
    
def testZuHeLong():
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[1, 4, 7, 12, 15, 18, 23, 26, 29, 4, 4], [[7, 8, 9]], [], [], [], []])
    result = checker.isZuHeLong()
    print 'result:', result
    
def testSanSeSanJieGao():
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[4, 4, 4, 14, 14, 14, 5, 5], [[7, 8, 9]], [[24, 24, 24]], [], [], []])
    result = checker.isSanSeSanJieGao()
    print 'result:', result
    
def testSanSeSanBuGao():
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[15, 15, 1, 2, 3], [[12, 13, 14], [23, 24, 25]], [], [], [], []])
    result = checker.isSanSeSanBuGao()
    print 'result:', result
    
def testHunSiBuGao():
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[15, 15, 1, 2, 3], [[12, 13, 14], [23, 24, 25], [4, 5, 6]], [], [], [], []])
    result = checker.isHunSiBuGao()
    print 'result:', result
    
def testPingHu():
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[15, 15, 1, 2, 3, 1, 2, 3], [[1, 2, 3], [23, 24, 25]], [], [], [], []])
    result = checker.isPingHu()
    print 'result:', result
    
def test258Jiang():
    '''ok'''
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[15, 15, 1, 2, 3, 1, 2, 3], [[1, 2, 3], [23, 24, 25]], [], [], [], []])
    result = checker.is258Jiang()
    print 'result:', result
    
def test19Jiang():
    '''ok'''
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[21, 21, 1, 2, 3, 1, 2, 3], [[1, 2, 3], [23, 24, 25]], [], [], [], []])
    result = checker.is19Jiang()
    print 'result:', result
    
def test19Ke():
    '''ok'''
    checker = MTilePatternChecker()
    checker.setPlayerAllTiles([[21, 21, 21, 2, 2, 1, 2, 3], [[1, 2, 3], [23, 24, 25]], [], [], [], []])
    result = checker.hasYaoJiuKe()
    print 'result:', result
    
if __name__ == "__main__":
    # testSiBuGao()
    # testSanJieGao()
    # testZuHeLong()
    # testSanSeSanJieGao()
    # testSanSeSanBuGao()
    # testHunSiBuGao()
    # testPingHu()
    # test258Jiang()
    # test19Jiang()
    test19Ke()
