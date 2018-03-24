# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
import copy
from freetime5.util import ftlog


class MWin(object):
    """公共的判断和牌的AI
    """
    
    def __init__(self):
        super(MWin, self).__init__()
        
    @classmethod
    def isLuanFengyise(cls, tiles, colorCount):
        """
         风一色
        """
        ftlog.debug('MWin.isLuanFengyise tiles:', tiles
                    , ' colorCount:', colorCount)
        if colorCount > 1:
            return False, []
        
        for tile in tiles:
            if (not MTile.isFeng(tile)) and (not MTile.isArrow(tile)):
                return False, []
            
        ftlog.debug('MWin.isLuanFengyise ok, pattern:', tiles)
        return True, [tiles]
      
    @classmethod  
    def isQiDui(cls, tiles, baoTiles=[]):
        '''
        判断是否是七对
        现在加入宝牌处理判断
        
        特别注意，baoTiles不是癞子牌，是宝牌，穷和玩法特有的宝牌，上听后生效。
        上听后摸到一张就和牌
        baoTiles可以是癞子牌，但传进来的必须是手牌中的赖子数组，如手牌中有2个7是赖子 baoTiles=[7,7]
        '''
        
        allMagicTiles = []
        newTiles = []
        for tile in tiles:
            if tile in baoTiles:
                allMagicTiles.append(tile)
            else:
                newTiles.append(tile)
                
        # ftlog.debug('MWin.isQiDui newTiles:', newTiles, ' baoTiles:', baoTiles)
        tileArr = MTile.changeTilesToValueArr(newTiles)
        # ftlog.debug('MWin.isQiDui tileArr:', tileArr)
        resultArr = []
        duiCount = 0
        for tileIndex in range(0, len(tileArr)):
            if tileArr[tileIndex] == 0:
                continue
            
            # 单张情况
            elif tileArr[tileIndex] == 1:
                if len(allMagicTiles) >= 1:
                    duiCount += 1
                    resultArr.append([tileIndex, allMagicTiles.pop(0)])
            # 三张情况        
            elif tileArr[tileIndex] == 3:
                if len(allMagicTiles) >= 1:
                    duiCount += 2
                    resultArr.append([tileIndex, tileIndex])
                    resultArr.append([tileIndex, allMagicTiles.pop(0)])
            # 一对
            elif tileArr[tileIndex] == 2:
                resultArr.append([tileIndex, tileIndex])
                duiCount += 1
            # 两对    
            elif tileArr[tileIndex] == 4:
                resultArr.append([tileIndex, tileIndex])
                resultArr.append([tileIndex, tileIndex])
                duiCount += 2
                
        for index in range(len(allMagicTiles)):
            if ((index + 1) % 2) == 0:
                resultArr.append([allMagicTiles[index - 1], allMagicTiles[index]])
                duiCount += 1
        
        # ftlog.info('MWin.isQiDui, tiles:', tiles, ' baoTiles:', baoTiles, ' duiCount:', duiCount, ' resultArr',resultArr)
             
        if (duiCount == 7) and (len(tiles) == 14):
            return True, resultArr
        elif (duiCount == 6) and (len(tiles) == 12):
            return True, resultArr
        else:
            return False, []

    @classmethod
    def isQuanJiang(cls, tiles):
        '''
        判断是否全将
        '''
        jiang258 = [2, 5, 8, 12, 15, 18, 22, 25, 28]
        handTiles = tiles[MHand.TYPE_HAND]
        # chi: [[1,2,3]
        chiTiles = tiles[MHand.TYPE_CHI]
        # peng: [[4, 4, 4]]
        pengTiles = tiles[MHand.TYPE_PENG]
        # gang: [{'pattern': [31, 31, 31, 31], 'style': True, 'actionID': 11}]
        gangTiles = tiles[MHand.TYPE_GANG] 

        for tile in handTiles:
            if not tile in jiang258:
                return False, []
        if len(chiTiles) > 0:
                return False, []
        for tilePatten in pengTiles:
            if not tilePatten[0] in jiang258:
                return False, []
        for tile in gangTiles:
            if not tile['pattern'][0] in jiang258:
                return False, []

        return True, [handTiles]
    
    @classmethod
    def isQuanYaoJiu(cls, tiles):
        """
        判断是否是全幺九
        
        全幺九
        吃/碰/杠/将牌里都还有幺/九
        
        如果有非幺九的牌，一定在顺子里面。
        1）吃牌
        2）手牌中可以组成吃牌的牌
        """
        # 验证吃牌
        chiPatterns = tiles[MHand.TYPE_CHI]
        for chiPattern in chiPatterns:
            hasYaoJiu = False
            for tile in chiPattern:
                if MTile.isYaoJiu(tile):
                    hasYaoJiu = True
                    break
            if not hasYaoJiu:
                return False
        
        # 验证碰牌
        pengPatterns = tiles[MHand.TYPE_PENG]
        for pengPattern in pengPatterns:
            tile = pengPattern[0]
            if not MTile.isYaoJiu(tile):
                return False
            
        # 验证杠牌[{'pattern': [31, 31, 31, 31], 'style': True, 'actionID': 11}]
        gangs = tiles[MHand.TYPE_GANG]
        for gang in gangs:
            pattern = gang['pattern']
            tile = pattern[0]
            if not MTile.isYaoJiu(tile):
                return False
        
        # 提取手牌中的所有顺子
        handTiles = copy.deepcopy(tiles[MHand.TYPE_HAND])
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
        ftlog.debug('MWin.isQuanYaoJiu tiles:', tiles
                    , ' result:', result
                    , ' patterns:', patterns)
        return result

    @classmethod
    def isDadiaoche(self, tiles):
        """
        大吊车：胡牌时自己手上只有一张牌，且胡的是二五八
        """
        handTile = tiles[MHand.TYPE_HAND]
        huTile = tiles[MHand.TYPE_HU][0]
        handTile.extend(tiles[MHand.TYPE_HU])
        if len(handTile) == 2 and huTile < MTile.TILE_DONG_FENG and (MTile.getValue(huTile) == 2 or MTile.getValue(huTile) == 5 or MTile.getValue(huTile) == 8):
            return True, [handTile]

        return False, []

    @classmethod
    def isFlowerHu(self, tiles):
        """
        花胡：摸到花牌8张全
        """
        handTile = tiles[MHand.TYPE_HAND]
        flowerTile = tiles[MHand.TYPE_SHOW_FLOWERS]

        flower_count = 0
        for tile in handTile:
            if MTile.isFlower(tile):
                flower_count += 1
        if flower_count + len(flowerTile) == 8:
            return True, [handTile]

        return False, []

    @classmethod
    def is13BuKao(cls, handTiles):
        '''
        判断是否十三不靠
        '''

        # 有五张不同的风牌或箭牌
        fengTiles = []
        for index in range(0, len(handTiles)):
            if (MTile.isFeng(handTiles[index]) or MTile.isArrow(handTiles[index])):
                if (handTiles[index] not in fengTiles):
                    fengTiles.append(handTiles[index])
                else:
                    return False, []

        if len(fengTiles) > 0:
            for tile in fengTiles:
                handTiles.remove(tile)
        # 剩余9张牌
        if not (len(fengTiles) == 5 and len(handTiles) == 9):
            return False, []
        # 排序
        handTiles.sort()

        ftlog.debug("handTiles ===", handTiles)

        # 根据花色分组
        groups = [[] for _ in xrange(3)]
        for tile in handTiles:
            if ((tile % 10) == 0) or (tile >= 30):
                continue
                
            index = tile / 10
            groups[index].append(tile)

        ftlog.debug("groups ===", groups)

        # 每组3张牌
        types = [1, 2, 3]
        for grp in groups:
            if len(grp) != 3:
                return False, []
            
            v = grp[0] % 10
            if not (grp[1] % 10 == (v + 3) and grp[2] % 10 == (v + 6)):
                return False, []
            
            if v in types:
                types.remove(v)
            else:
                return False, []

        ftlog.debug("handTile ===", handTiles)

        handTiles.extend(fengTiles)

        return True, [handTiles]

    @classmethod
    def is13BuKaoWithOutLimit(cls, handTiles, handMagics=[], replaceMagics=[]):
        '''
        判断是否十三不靠 只要手牌没有靠着的就行 没有其他限制
        hanMagics是手牌中的赖子数组，如手牌中有2个7是赖子 baoTiles=[7,7]
        replaceMagic是手牌中的顶赖子数组 如2万是赖子，白板是顶赖子牌，白板可以当作2万，但白板的2万不是赖子
        '''
        if len(replaceMagics) > 2 and len(handMagics) > 0 and handMagics[0] != replaceMagics[0]:
            return False, []

        newHandTiles = copy.deepcopy(handTiles)
        # 排序
        newHandTiles.sort()
        for magic in handMagics:
            if magic in newHandTiles:
                newHandTiles.remove(magic)

        if len(replaceMagics) == 2 and len(handMagics) > 0 and handMagics[0] != replaceMagics[0]:
            newHandTiles.append(handMagics[0])
            newHandTiles.remove(replaceMagics[0])

        # 有五张不同的风牌或箭牌
        fengTiles = []
        for index in range(0, len(newHandTiles)):
            if (MTile.isFeng(newHandTiles[index]) or MTile.isArrow(newHandTiles[index])):
                if (newHandTiles[index] not in fengTiles):
                    fengTiles.append(newHandTiles[index])
                else:
                    return False, []

        if len(fengTiles) > 0:
            for tile in fengTiles:
                newHandTiles.remove(tile)

        # 根据花色分组
        groups = [[] for _ in xrange(3)]
        for tile in newHandTiles:
            if ((tile % 10) == 0) or (tile >= 30):
                continue

            index = tile / 10
            groups[index].append(tile)

        # 每组3张牌
        buKaoCount = 0
        for grp in groups:
            if len(grp) == 0:
                continue

            v = grp[0]
            ftlog.debug("grp ===", grp)
            if len(grp) == 2 and (v + 2) < grp[1]:
                buKaoCount += len(grp)
            elif len(grp) == 3 and ((v + 2) < grp[1] and (grp[1] + 2) < grp[2]):
                buKaoCount += len(grp)
            elif len(grp) == 1:
                buKaoCount += len(grp)

        ftlog.debug("buKaoCount ===", buKaoCount)
        ftlog.debug("handMagics ===", len(handMagics))
        ftlog.debug("fengTiles ===", len(fengTiles))
        if buKaoCount + len(handMagics) + len(fengTiles) != 14:
            return False, []

        return True, [handTiles]
    
    @classmethod
    def isHuWishSpecialJiang(cls, tiles, jiangPattern, magics=[]):
        """
        指定将牌类型判断是否胡牌
            暂时不考虑将牌
        """
        # 先移除将牌。无指定将牌，判和失败
        tileArr = MTile.changeTilesToValueArr(tiles)
        jiangTile = jiangPattern[0]
        if tileArr[jiangTile] < 2:
            return False, []
        # 移除将牌
        tileArr[jiangTile] -= 2
        
        # 计算剩下的结果
        resultArr = []
        resultArr.append(jiangPattern)
        tileTypes = [MTile.TILE_WAN, MTile.TILE_TONG, MTile.TILE_TIAO, MTile.TILE_FENG]
        winResult = False
        for tileType in tileTypes:
            winResult, _, _tArr, _rArr, _mArr = cls.isHuWithMagic(tileArr, resultArr, magics, True, tileType, False)
            if not winResult:
                return False, []
            else:
                tileArr = copy.deepcopy(_tArr)
                resultArr = copy.deepcopy(_rArr)
        
        return winResult, resultArr

    @classmethod
    def isShisanyao(cls, tiles, laizi=[]):
        """
        十三幺：13章（由东南西北中发白 + 一万、九万、一条、九条、一筒、九筒）+ 这13章中任意一种牌
        前提条件：无

        十三幺是门清
        只需要判断TYPE_HAND手牌

        其他称呼
        1）国士无双
        """
        if len(tiles[MHand.TYPE_HAND]) != 14:
            ftlog.debug('win.isShisanyao: false')
            return False

        ftlog.debug('win.isShisanyao, laizi:',laizi,
                    'tiles[MHand.TYPE_HAND]:',tiles[MHand.TYPE_HAND],
                    'len tiles[MHand.TYPE_HAND]:', len(tiles[MHand.TYPE_HAND])
                    )

        yao13Arr = [1, 9, 11, 19, 21, 29, 31, 32, 33, 34, 35, 36, 37]
        handTile = copy.deepcopy(tiles[MHand.TYPE_HAND])


        if len(laizi)==0:
            #没有赖子
            yaoJiuCount = 0
            for yao in yao13Arr:
                if yao in handTile:
                    yaoJiuCount += 1

            if yaoJiuCount==13:
                allYao = True
                for tile in handTile:
                    if tile not in yao13Arr:
                        allYao = False
                        break
                if allYao:
                    return True

            return False
        else:
            #有赖子
            #如果除去赖子全是幺九，并且数量>=T－1，就是十三幺
            laiziTile = laizi[0]
            handTile = filter(lambda x:(x != laiziTile), handTile)
            #如果有不是幺九的，直接返回false
            for tile in handTile:
                if tile not in yao13Arr:
                    return False
            #计算幺九数量
            yaojiuArray = []
            for tile in handTile:
                if tile not in yaojiuArray:
                    yaojiuArray.append(tile)
            if len(yaojiuArray) >= len(handTile)-1:
                return True
            else:
                return False


    '''
        @classmethod
    def isShisanyao(cls, tiles, laizi=[]):
        """
        十三幺：13章（由东南西北中发白 + 一万、九万、一条、九条、一筒、九筒）+ 这13章中任意一种牌
        前提条件：无

        十三幺是门清
        只需要判断TYPE_HAND手牌

        其他称呼
        1）国士无双
        """
        if len(tiles[MHand.TYPE_HAND]) != 14:
            ftlog.debug('MTilePatternChecker.isShisanyao: false')
            return False

        ftlog.debug('MTilePatternChecker.isShisanyao, laizi:',laizi,
                    'tiles[MHand.TYPE_HAND]:',tiles[MHand.TYPE_HAND],
                    'len tiles[MHand.TYPE_HAND]:', len(tiles[MHand.TYPE_HAND])
                    )

        laiziCount = 0
        if len(laizi) > 0:
            for x in tiles[MHand.TYPE_HAND]:
                if x == laizi[0]:
                    laiziCount += 1

        yao13Arr = [1, 9, 11, 19, 21, 29, 31, 32, 33, 34, 35, 36, 37]
        handTile = copy.deepcopy(tiles[MHand.TYPE_HAND])
        for yao in yao13Arr:
            if yao not in handTile:
                if len(laizi) > 0:
                    laiziCount -= 1
                    if laiziCount >= 0:
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


    @classmethod
    def isHu(cls, tiles, magicTiles=[], allowZFB=False):
        """胡牌判断，只判断手牌，杠牌，吃牌，碰牌不在内
           杠牌、吃牌、碰牌已成型，不用另外计算
           1）肯定包含将牌
           2）剩下的牌里不会有暗杠牌
           3）杠牌/吃牌/碰牌是已经成型的牌，按成型的样式计算积分，不再重新计算
        返回值：
            True - 和了
            False - 没和
            
        特别说明：
            这个API是判断是否胡牌，并未遍历所有的胡牌解
            依据返回的pattern去判断番型是有问题的。
            具体的番型要用具体的番型API去判断。
        """
        tileArr = MTile.changeTilesToValueArr(tiles)
        magicArr = []
        for magicTile in magicTiles:
            magicArr.extend([magicTile for _ in range(tileArr[magicTile])])
            tileArr[magicTile] = 0
            
        resultArr = []
        tileTypes = [MTile.TILE_WAN, MTile.TILE_TONG, MTile.TILE_TIAO, MTile.TILE_FENG]
        hasJiang = False
        winResult = False
        
        for tileType in tileTypes:
            winResult, hasJiang, _tArr, _rArr, _mArr = cls.isHuWithMagic(tileArr, resultArr, magicArr, hasJiang, tileType, allowZFB)
            if not winResult:
                return False, []
            else:
                tileArr = copy.deepcopy(_tArr)
                resultArr = copy.deepcopy(_rArr)
                magicArr = copy.deepcopy(_mArr)
        
        if winResult and len(magicArr) > 0:
            resultArr.append(magicArr)
            if not hasJiang and len(magicArr) == 2:
                hasJiang = True
        return hasJiang and winResult, resultArr

    @classmethod
    def isHuWithMagic(cls, tileArr, resultArr, magicArr, hasJiang, tileType, allowZFB):
        '''
        不能一次性把所有癞子都给过去，要一个一个的给，使用最少的癞子打成胡牌效果。
        用掉太多癞子，会导致漏和
        '''
        _hasJiang = hasJiang
        _tileArr = copy.deepcopy(tileArr)
        _resultArr = copy.deepcopy(resultArr)
        
        for magicLength in range(len(magicArr) + 1):
            newMagicArr = magicArr[0:magicLength]
            _newMagicArr = copy.deepcopy(newMagicArr)
            _resultType, _hasJiang = cls.isBu(_tileArr, _resultArr, newMagicArr, tileType, _hasJiang, allowZFB)
            # ftlog.debug('tileType:', tileType, ' resultType:', _resultType, ' hasJiang:', hasJiang)
            if not _resultType:
                continue
            else: 
                magicArr = magicArr[len(_newMagicArr):]
                magicArr.extend(newMagicArr)
                return _resultType, _hasJiang, _tileArr, _resultArr, magicArr
            
        return False, hasJiang, None, None, None
    
    @classmethod
    def isBu(cls, tileArr, resultArr, magicArr, tileType, hasJiang, allowZFB):
        """
        判断某个花色是否是三朴，缺的牌从癞子中获取，如果没有癞子牌了，也形不成三朴，和牌失败
        """
        if 0 == cls.getCardNumByType(tileArr, tileType):
            # 这个花色没有牌
            return True, hasJiang
        
        # ftlog.debug('check card:', MTile.traverseTile(tileType))
        for tileIndex in MTile.traverseTile(tileType):
            if tileArr[tileIndex] == 0:
                continue
            
            if tileArr[tileIndex] >= 3:
                # 刻，没有占用癞子
                tileArr[tileIndex] -= 3
                resultTmp, hasJiang = cls.isBu(tileArr, resultArr, magicArr, tileType, hasJiang, allowZFB)
                if resultTmp:
                    resultArr.append([tileIndex, tileIndex, tileIndex])
                    return True, hasJiang
                # 还原手牌，继续判断
                tileArr[tileIndex] += 3
                
            if (tileArr[tileIndex] == 2) and (len(magicArr) >= 1):
                # 对子，尝试加一张癞子组成刻
                tileArr[tileIndex] -= 2
                mTile = magicArr.pop(-1)
#                 ftlog.debug('[11M]magicArr pop:', mTile, ' after pop:', magicArr)
                resultTmp, hasJiang = cls.isBu(tileArr, resultArr, magicArr, tileType, hasJiang, allowZFB)
                if resultTmp:
                    resultArr.append([tileIndex, tileIndex, mTile])
                    return True, hasJiang
                    
                # 还原手牌，继续判断
                tileArr[tileIndex] += 2
                magicArr.append(mTile)
#                 ftlog.debug('[11M]magicArr push:', mTile, ' after push:', magicArr)
                
            if (tileArr[tileIndex] == 1) and (len(magicArr) >= 2):
                # 单张，尝试加两张癞子组成刻
                tileArr[tileIndex] -= 1
                mTile1 = magicArr.pop(-1)
                mTile2 = magicArr.pop(-1)
#                 ftlog.debug('[1MM] magicArr pop1:', mTile1, ' pop2:', mTile2, ' after pop:', magicArr)
                resultTmp, hasJiang = cls.isBu(tileArr, resultArr, magicArr, tileType, hasJiang, allowZFB)
                if resultTmp:
                    resultArr.append([tileIndex, mTile1, mTile2])
                    return True, hasJiang
                # 还原手牌，继续判断
                tileArr[tileIndex] += 1
                magicArr.append(mTile1)
                magicArr.append(mTile2)
#                 ftlog.debug('[1MM] magicArr push1:', mTile1, ' push2:', mTile2, ' after push:', magicArr)
                
            if not hasJiang and \
                tileArr[tileIndex] > 0 and \
                (tileArr[tileIndex] + len(magicArr) >= 2):
                tileArr[tileIndex] -= 1
                isMagicJiang = False
                jiangTile = tileIndex
                if tileArr[tileIndex] > 0:
                    tileArr[tileIndex] -= 1
                else:
                    isMagicJiang = True
                    jiangTile = magicArr.pop(-1)
#                     ftlog.debug('[1M] magicArr pop:', jiangTile, ' after pop:', magicArr)
                
                oldJiang = hasJiang
                resultTmp, hasJiang = cls.isBu(tileArr, resultArr, magicArr, tileType, True, allowZFB)
                if resultTmp:
                    resultArr.append([tileIndex, jiangTile])
                    hasJiang = True
                    return True, hasJiang
                else:
                    # 还原将牌标记
                    hasJiang = oldJiang
                     
                # 还原手牌
                tileArr[tileIndex] += 1
                if isMagicJiang:
                    magicArr.append(jiangTile)
#                     ftlog.debug('[1M] magicArr append:', jiangTile, ' after append:', magicArr)
                else:
                    tileArr[tileIndex] += 1
            
            # 是否允许中发白作为顺牌，暂时没有考虑赖子的情况，后续可以修改添加
            if not allowZFB:    
                if tileIndex >= MTile.TILE_DONG_FENG:
                    # 风箭牌不能组成顺
                    return False, hasJiang
            else:
                if tileIndex == MTile.TILE_HONG_ZHONG:
                    if tileArr[tileIndex] > 0 and tileArr[tileIndex + 1] > 0 and tileArr[tileIndex + 2] > 0:
                        pattern = [tileIndex, tileIndex + 1, tileIndex + 2]
                        tileArr[tileIndex] -= 1
                        tileArr[tileIndex + 1] -= 1
                        tileArr[tileIndex + 2] -= 1
                                  
                        resultTmp, hasJiang = cls.isBu(tileArr, resultArr, magicArr, tileType, hasJiang, allowZFB)
                        if resultTmp:
                            resultArr.append(pattern)
                            return True, hasJiang
                elif tileIndex >= MTile.TILE_DONG_FENG:
                    return False, hasJiang

            # 提取顺牌组合
            if tileArr[tileIndex] > 0 and tileType != MTile.TILE_FENG:
                # 测试顺子 0 1 2
                if MTile.getValue(tileIndex) <= 7:
                    tile0 = tileIndex
                    needMagic = 0
                    is1Magic = False
                    is2Magic = False
                    if tileArr[tileIndex + 1] == 0:
                        needMagic += 1
                        is1Magic = True
                    if tileArr[tileIndex + 2] == 0:
                        needMagic += 1
                        is2Magic = True
                     
                    if needMagic <= len(magicArr):    
                        pattern = [tile0, None, None]
                        tileArr[tileIndex] -= 1
                        
                        if is1Magic:
                            pattern[1] = (magicArr.pop(-1))
                        else:
                            pattern[1] = (tileIndex + 1)
                            tileArr[tileIndex + 1] -= 1
                            
                        if is2Magic:
                            pattern[2] = (magicArr.pop(-1))
                        else:
                            pattern[2] = (tileIndex + 2)
                            tileArr[tileIndex + 2] -= 1
                            
#                         if is1Magic and is2Magic:
#                             ftlog.debug('[1MM] magicArr pop1:', pattern[1], ' pop2:', pattern[2], ' after pop:', magicArr)
#                         elif is1Magic:
#                             ftlog.debug('[1M3] magicArr pop1:', pattern[1], ' after pop:', magicArr)
#                         elif is2Magic:
#                             ftlog.debug('[12M] magicArr pop2:', pattern[2], ' after pop:', magicArr)
                            
                        resultTmp, hasJiang = cls.isBu(tileArr, resultArr, magicArr, tileType, hasJiang, allowZFB)
                        if resultTmp:
                            resultArr.append(pattern)
                            return True, hasJiang
                        
                        # 还原手牌
                        tileArr[tileIndex] += 1
                        if is1Magic:
                            magicArr.append(pattern[1])
                        else:
                            tileArr[tileIndex + 1] += 1
                        
                        if is2Magic:
                            magicArr.append(pattern[2])
                        else:
                            tileArr[tileIndex + 2] += 1
                        
#                         if is1Magic and is2Magic:
#                             ftlog.debug('[1MM] magicArr append1:', pattern[1], ' append2:', pattern[2], ' after append:', magicArr)
#                         elif is1Magic:
#                             ftlog.debug('[1M3] magicArr append1:', pattern[1], ' after append:', magicArr)
#                         elif is2Magic:
#                             ftlog.debug('[12M] magicArr append2:', pattern[2], ' after append:', magicArr)
                    
                # 测试顺子 -1 0 1
                if MTile.getValue(tileIndex) <= 8 and MTile.getValue(tileIndex) >= 2:
                    tile1 = tileIndex
                    needMagic = 0
                    is0Magic = False
                    is2Magic = False
                    if tileArr[tileIndex - 1] == 0:
                        needMagic += 1
                        is0Magic = True
                    if tileArr[tileIndex + 1] == 0:
                        needMagic += 1
                        is2Magic = True
                        
                    if needMagic <= len(magicArr):    
                        pattern = [None, tile1, None]
                        tileArr[tileIndex] -= 1
                        
                        if is0Magic:
                            pattern[0] = (magicArr.pop(-1))
                        else:
                            pattern[0] = (tileIndex - 1)
                            tileArr[tileIndex - 1] -= 1
                            
                        if is2Magic:
                            pattern[2] = (magicArr.pop(-1))
                        else:
                            pattern[2] = (tileIndex + 1)
                            tileArr[tileIndex + 1] -= 1
                            
#                         if is0Magic and is2Magic:
#                             ftlog.debug('[M1M] magicArr pop0:', pattern[0], ' pop2:', pattern[2], ' after pop:', magicArr)
#                         elif is0Magic:
#                             ftlog.debug('[M23] magicArr pop1:', pattern[0], ' after pop:', magicArr)
#                         elif is2Magic:
#                             ftlog.debug('[12M] magicArr pop2:', pattern[2], ' after pop:', magicArr)
                            
                        resultTmp, hasJiang = cls.isBu(tileArr, resultArr, magicArr, tileType, hasJiang, allowZFB)
                        if resultTmp:
                            resultArr.append(pattern)
                            return True, hasJiang
                        
                        # 还原手牌
                        tileArr[tileIndex] += 1
                        if is0Magic:
                            magicArr.append(pattern[0])
                        else:
                            tileArr[tileIndex - 1] += 1
                        
                        if is2Magic:
                            magicArr.append(pattern[2])
                        else:
                            tileArr[tileIndex + 1] += 1
                            
#                         if is0Magic and is2Magic:
#                             ftlog.debug('[M1M] magicArr append0:', pattern[0], ' append2:', pattern[2], ' after append:', magicArr)
#                         elif is0Magic:
#                             ftlog.debug('[M23] magicArr append0:', pattern[0], ' after append:', magicArr)
#                         elif is2Magic:
#                             ftlog.debug('[12M] magicArr append2:', pattern[2], ' after append:', magicArr)  
                
                # 测试顺子 -2 -1 0
                if MTile.getValue(tileIndex) >= 3:
                    tile2 = tileIndex
                    needMagic = 0
                    is0Magic = False
                    is1Magic = False
                    if tileArr[tileIndex - 2] == 0:
                        needMagic += 1
                        is0Magic = True
                    if tileArr[tileIndex - 1] == 0:
                        needMagic += 1
                        is1Magic = True
                     
                    if needMagic <= len(magicArr):    
                        pattern = [None, None, tile2]
                        tileArr[tileIndex] -= 1
                        
                        if is0Magic:
                            pattern[0] = (magicArr.pop(-1))
                        else:
                            pattern[0] = (tileIndex - 2)
                            tileArr[tileIndex - 2] -= 1
                            
                        if is1Magic:
                            pattern[1] = (magicArr.pop(-1))
                        else:
                            pattern[1] = (tileIndex - 1)
                            tileArr[tileIndex - 1] -= 1
                            
#                         if is0Magic and is1Magic:
#                             ftlog.debug('[MM3] magicArr pop0:', pattern[0], ' pop1:', pattern[1], ' after pop:', magicArr)
#                         elif is0Magic:
#                             ftlog.debug('[M23] magicArr pop0:', pattern[0], ' after pop:', magicArr)
#                         elif is1Magic:
#                             ftlog.debug('[1M3] magicArr pop1:', pattern[1], ' after pop:', magicArr)
                            
                        resultTmp, hasJiang = cls.isBu(tileArr, resultArr, magicArr, tileType, hasJiang, allowZFB)
                        if resultTmp:
                            resultArr.append(pattern)
                            return True, hasJiang
                    
                        # 还原手牌
                        tileArr[tileIndex] += 1
                        if is0Magic:
                            magicArr.append(pattern[0])
                        else:
                            tileArr[tileIndex - 2] += 1
                        
                        if is1Magic:
                            magicArr.append(pattern[1])
                        else:
                            tileArr[tileIndex - 1] += 1
                            
#                         if is0Magic and is1Magic:
#                             ftlog.debug('[MM3] magicArr append0:', pattern[0], ' append1:', pattern[1], ' after append:', magicArr)
#                         elif is0Magic:
#                             ftlog.debug('[M23] magicArr append0:', pattern[0], ' after append:', magicArr)
#                         elif is1Magic:
#                             ftlog.debug('[1M3] magicArr append1:', pattern[1], ' after append:', magicArr)
        
        # 无和牌可能
        return False, hasJiang
        
    @classmethod
    def isHuBySearchAllTiles(cls, _tileArr, hasJiang, resultArr):
        """
        判断是否和牌
        目的是判断胡牌，未判断所有的胡牌情况
        这是第一版本的判胡，未按花色分组，未考虑癞子
        
        参数
            tileArr：      整理好的手牌
            hasJiang：     是否有将牌
            resultArr：    结果牌
        
            带判断数组中没有剩余牌了，和了
        """
        tileArr = copy.deepcopy(_tileArr)
        _num = cls.getCardNum(tileArr)
        
        if 0 == _num:
            # 一定有将牌
            return hasJiang
        
        for tile in range(40):
            # 3张组合，刻
            if tileArr[tile] >= 3:
                # 去掉这三张牌
                tileArr[tile] -= 3
                # 判断剩下的牌
                if cls.isHuBySearchAllTiles(tileArr, hasJiang, resultArr):
                    # 存储结果
                    pattern = [tile, tile, tile]
                    resultArr.append(pattern)
                    return True
                # 还原，继续判断
                tileArr[tile] += 3
                
            # 2张组合，对
            if tileArr[tile] >= 2 and not hasJiang:
                hasJiang = True
                tileArr[tile] -= 2
                if cls.isHuBySearchAllTiles(tileArr, hasJiang, resultArr):
                    # 保存结果
                    pattern = [tile, tile]
                    resultArr.append(pattern)
                    return True
                # 还原
                hasJiang = False
                tileArr[tile] += 2
             
            # 风牌不会组成顺，不和
            if tile > 30 and hasJiang:
                """已经有将牌，只考虑顺"""
                return False
            
            # 提取顺牌组合
            if (tile % 10) <= 7 \
                and tileArr[tile] > 0 \
                and tileArr[tile + 1] > 0 \
                and tileArr[tile + 2] > 0:
                tileArr[tile] -= 1
                tileArr[tile + 1] -= 1
                tileArr[tile + 2] -= 1
                
                if cls.isHuBySearchAllTiles(tileArr, hasJiang, resultArr):
                    # 保存结果
                    pattern = [tile, tile + 1, tile + 2]
                    resultArr.append(pattern)
                    return True
                # 还原
                tileArr[tile] += 1
                tileArr[tile + 1] += 1
                tileArr[tile + 2] += 1
        
        # 无法和牌
        return  False

    @classmethod
    def isHuWithAllSolution(cls, tileArr, hasJiang, resultArr, allResults):
        """
        获取所有的胡牌解
        比如，输入是：
        [2,2,2,3,3,3,4,4,4,5,5]
        
        输出是：
        [[[2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5]], [[2, 2], [2, 3, 4], [3, 4, 5], [3, 4, 5]], [[2, 3, 4], [2, 3, 4], [2, 3, 4], [5, 5]]]
        
        第一步，先完成所有胡牌结果的遍历
        第二步，优化算法，按花色分组
        第三步，支持癞子
        
        目前完成第一步，使用是请看说明
        """
        num = cls.getCardNum(tileArr)
        if 0 == num:
            # 一定有将牌
            if hasJiang:
#                 print resultArr
                resultArr.sort()
                if resultArr not in allResults:
                    allResults.append(resultArr)
                return
        
        oldTileArr = copy.deepcopy(tileArr)
        oldResultArr = copy.deepcopy(resultArr)
        for tile in range(40):
            # 3张组合，刻
            if tileArr[tile] >= 3:
                # 去掉这三张牌
                tileArr[tile] -= 3
                # 判断剩下的牌
                if cls.isHuBySearchAllTiles(tileArr, hasJiang, []):
                    # 存储结果
                    pattern = [tile, tile, tile]
                    resultArr.append(pattern)
                    cls.isHuWithAllSolution(tileArr, hasJiang, resultArr, allResults)
                
            # 还原，继续判断
            tileArr = copy.deepcopy(oldTileArr)
            resultArr = copy.deepcopy(oldResultArr)
            
            # 2张组合，对
            if tileArr[tile] >= 2 and not hasJiang:
                hasJiang = True
                tileArr[tile] -= 2
                if cls.isHuBySearchAllTiles(tileArr, hasJiang, []):
                    # 保存结果
                    pattern = [tile, tile]
                    resultArr.append(pattern)
                    cls.isHuWithAllSolution(tileArr, hasJiang, resultArr, allResults)
                # 还原
                hasJiang = False
            
            tileArr = copy.deepcopy(oldTileArr)
            resultArr = copy.deepcopy(oldResultArr)
            # 提取顺牌组合
            if tile < 30:
                if (tile % 10) <= 7 \
                    and tileArr[tile] > 0 \
                    and tileArr[tile + 1] > 0 \
                    and tileArr[tile + 2] > 0:
                    tileArr[tile] -= 1
                    tileArr[tile + 1] -= 1
                    tileArr[tile + 2] -= 1
                    
                    if cls.isHuBySearchAllTiles(tileArr, hasJiang, []):
                        # 保存结果
                        pattern = [tile, tile + 1, tile + 2]
                        resultArr.append(pattern)
                        cls.isHuWithAllSolution(tileArr, hasJiang, resultArr, allResults)
        
    
    @classmethod
    def getCardNumByType(cls, tileArr, tileType):
        """
        获取某一个花色的张数
        """
        num = 0    
        for tile in MTile.traverseTile(tileType):
            num += tileArr[tile]
        return num
    
    @classmethod
    def getCardNum(cls, tileArr):
        """
        获取所有的麻将牌张数
        """
        num = 0
        for tile in tileArr:
            num += tile
        return num
    
def test1():
    tiles = [3, 3]
    return MWin.isHu(tiles, [21])

def test2():
    tiles = [5, 6, 6, 13, 14, 15, 21, 21]
    return MWin.isHu(tiles, [21])
    
def testqidui():
    tiles = [5, 5, 6, 6, 7, 7, 8, 8, 13, 13, 15, 15, 21, 22]
    return MWin.isQiDui(tiles, 22, False, [22])

def testqidui1():
    tiles = [5, 5, 6, 6, 7, 7, 8, 8, 13, 13, 15, 15, 21, 22]
    return MWin.isQiDui(tiles, 22, False, [21, 23])

def testqidui2():
    tiles = [5, 5, 6, 6, 7, 7, 8, 8, 13, 13, 14, 15, 21, 22]
    return MWin.isQiDui(tiles, 22, False, [14, 15])

def testqidui3():
    tiles = [5, 5, 6, 6, 7, 7, 8, 8, 13, 13, 14, 15, 21, 22]
    return MWin.isQiDui(tiles, 22, False, [14, 15, 21, 22])

def testqidui4():
    tiles = [5, 5, 6, 6, 7, 7, 8, 8, 13, 13, 14, 15, 21, 22]
    return MWin.isQiDui(tiles, 22, False, [14, 24, 25, 26])

def testqidui5():
    tiles = [5, 5, 6, 6, 7, 7, 8, 8, 13, 13]
    return MWin.isQiDui(tiles, 13, False, [13, 13, 8, 8])

def testQiDui6():
    tiles = [12, 12, 14, 14, 17, 17, 17, 22, 22, 23, 29, 29]
    return MWin.isQiDui(tiles, [17])

def test13bukao():
    tiles = [[4, 7, 12, 15, 18, 23, 26, 29, 31, 32, 33, 33, 34, 35], [], [], [], []]
    return MWin.is13BuKao(tiles[MHand.TYPE_HAND])

def testQuanjiang():
    tiles = [[2, 2, 5, 2, 5, 8, 22, 12, 5, 25, 28, 18, 18, 18], [], [], [], []]
    return MWin.isQuanJiang(tiles)

def testDadiaoche():
    tiles = [[2], [], [], [], [], [2]]
    return MWin.isDadiaoche(tiles)

def testFlowerHu():
    tiles = [[2, 3, 23, 12, 43, 41, 23, 44, 32, 35, 26, 28, 19], [], [], [], [], [], [], [42, 45, 46, 47, 48]]
    return MWin.isFlowerHu(tiles)

def testZFB():
    tiles = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 35, 36, 37]
    return MWin.isHu(tiles)

def testMagci():
    tiles = [12, 12, 13, 14, 14, 25, 25, 25, 26, 27, 28, 28, 28, 1]
    magics = [1]
    return MWin.isHu(tiles, magics)

def testQuanYaojiu():
    tiles = [[7, 7, 8, 8, 9, 9, 9, 9], [[1, 2, 3]], [[21, 21, 21]], [], [], [], [], []]
    return MWin.isQuanYaoJiu(tiles)

if __name__ == "__main__":
    # result, pattern = test1()
    # ftlog.debug('result:', result, ' pattern:', pattern)
# 
#     result, pattern = testqidui1()
#     ftlog.debug('result:', result)
#     
#     result, pattern = testqidui2()
#     ftlog.debug('result:', result)
#     
#     result, pattern = testqidui3()
#     ftlog.debug('result:', result)
#     
#     result, pattern = testqidui4()
#     ftlog.debug('result:', result)
#     
#     result, pattern = testqidui5()
#     ftlog.debug('result:', result)
#     result, pattern = testQiDui6()
#     ftlog.debug('result:', result
#                 , ' pattern:', pattern)
#     result, pattern = testFlowerHu()
#     ftlog.debug('result:', result , pattern )
    
#     result, pattern = test13bukao()
#     ftlog.debug('result:', result , pattern )

#     tiles = [[5,5,5,5,6,7,8,9,32,32,33], [], [[31,31,31]], [], [], [], [33], []]
#     result, pattern = MWin.isHu(tiles[MHand.TYPE_HAND], [33])
#     ftlog.debug('result:', result , pattern )

#     tiles = [5,5,5,7,8,9,32,32]
#     tileArr = MTile.changeTilesToValueArr(tiles)
#     result = MWin.isHuBySearchAllTiles(tileArr, False, [])
#     ftlog.debug('result:', result )
    
#     tiles = [[2,2,2,3,4,5,6,7,8,11,12,13,13,13], [], [], [], [], [], [2], []]
#     result, pattern = MWin.isHu(tiles[MHand.TYPE_HAND], [2])
#     ftlog.debug('result:', result , pattern )
    
#     tiles = [2,2,2,3,3,3,4,4,4,5,5]
#     tileArr = MTile.changeTilesToValueArr(tiles)
#     allResults = []
#     MWin.isHuWithAllSolution(tileArr, False, [], allResults)
#     print 'allResult:', allResults
    testQuanYaojiu()
