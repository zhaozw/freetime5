# -*- coding=utf-8
'''
Created on 2016年12月11日
牌型整理
@author: zhaol
'''
from __builtin__ import False
from freetime5.util import ftlog
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from majiang2.table.friend_table_define import MFTDefine
from majiang2.table.table_config_define import MTDefine
from majiang2.tile.tile import MTile
from majiang2.tile_pattern_checker.tile_pattern_checker import MTilePatternChecker
import copy


class MSichuanTilePatternChecker(MTilePatternChecker):
    """
    基础番型计算
    仅仅有手牌组成的番型计算，不考虑打牌时的具体情况，比如自摸，点炮，杠开，海底捞等。
    只考虑基本番型，比如七对，清一色，风一色，对对胡等等。
    
    算分时，结合胡牌的具体情况+番型，计算。比如清一色+杠开等
    只判断当前玩家的番型
    """
    
    # 和牌的番型
    PINGHU = 'PINGHU'
    DUIDUIHU = 'DUIDUIHU'
    QINGYISE = 'QINGYISE'
    QIDUI = 'QIDUI'
    QINGQIDUI = 'QINGQIDUI'
    LONGQIDUI = 'LONGQIDUI'
    QINGDUI = 'QINGDUI'
    QINGLONGQIDUI = 'QINGLONGQIDUI'
    QUANYAOJIU = 'QUANYAOJIU'
    QINGYAOJIU = 'QINGYAOJIU'
    JIANGDUI = 'JIANGDUI'
    JIANGQIDUI = 'JIANGQIDUI'
    LONGJIANGDUI = 'LONGJIANGDUI'
    JINGOUDIAO = 'JINGOUDIAO'
    QINGJINGOUDIAO = 'QINGJINGOUGOU'
    JIANGJINGOUDIAO = 'JIANGJINGOUGOU'
    SHIBALUOHAN = 'SHIBALUOHAN'
    QINGSHIBALUOHAN = 'QINGSHIBALUOHAN'
    DUANYAOJIU = 'DUANYAOJIU'
    MENQING = 'MENQING'
    
    def __init__(self):
        super(MSichuanTilePatternChecker, self).__init__()
        self.addFanXing(self.PINGHU, "平胡", 0)
        self.addFanXing(self.DUIDUIHU, '对对胡', 1)
        self.addFanXing(self.MENQING, '门清', 1)
        self.addFanXing(self.QINGYISE, '清一色', 2)
        self.addFanXing(self.QIDUI, '七对', 2)
        
        self.addFanXing(self.QINGQIDUI, '清七对', 4)
        self.addFanXing(self.LONGQIDUI, '龙七对', 3)
        self.addFanXing(self.QINGDUI, '清对', 3)
        self.addFanXing(self.QINGLONGQIDUI, '清龙七对', 5)
        self.addFanXing(self.QUANYAOJIU, '全幺九', 2)
        
        self.addFanXing(self.QINGYAOJIU, '清幺九', 4)
        self.addFanXing(self.JIANGDUI, '将对', 3)
        self.addFanXing(self.LONGJIANGDUI, '龙将对', 4)
        self.addFanXing(self.JINGOUDIAO, '金钩钓', 2)
        self.addFanXing(self.QINGJINGOUDIAO, '清金钩钓', 4)
        
        self.addFanXing(self.JIANGJINGOUDIAO, '将金钩钓', 4)
        self.addFanXing(self.JIANGQIDUI, '将七对', 4)
        self.addFanXing(self.SHIBALUOHAN, '十八罗汉', 6)
        self.addFanXing(self.QINGSHIBALUOHAN, '清十八罗汉', 8)
        self.addFanXing(self.DUANYAOJIU, '断幺九', 1)
        
        # 计算龙根 番型 龙七对 -1根 清龙七对 -1根 将七对 -1根 十八罗汉 -4根 清十八罗汉 -4根 
        self.__gen_xing = {
            self.LONGQIDUI : 1,
            self.QINGLONGQIDUI : 1,
            self.JIANGQIDUI : 1,
            self.SHIBALUOHAN : 4,
            self.QINGSHIBALUOHAN : 4
        }
     
    @property
    def genXing(self):   
        return self.__gen_xing
    
    def isQuanJiang(self):
        '''
        判断是否全将
        血流血战的独特番型，所有的牌都是2，5，8
        '''
        tiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        jiang258 = [2, 5, 8, 12, 15, 18, 22, 25, 28]
        ftlog.debug('MSiChuanOneResult.isQuanJiang tiles:', tiles)
        for tile in tiles:
            if tile not in jiang258:
                ftlog.debug('MSiChuanOneResult.isQuanJiang: False')
                return False
        ftlog.debug('MSiChuanOneResult.isQuanJiang: True')
        return True
    
    def isLongGen(self):
        '''
        龙根 和牌时 判断手牌中是否有龙根 4张为龙根
        '''
        tiles = copy.deepcopy(self.playerAllTiles[MHand.TYPE_HAND])
        tileArr = MTile.changeTilesToValueArr(tiles)
        ftlog.debug('MSiChuanTilePattern.isLongGen tiles: ', tiles, 'tileArr: ', tileArr)
        for tile in tileArr:
            if tile == 4:
                ftlog.debug('MSiChuanTilePattern.isLongGen: True tile: ', tile)
                return True
        ftlog.debug('MSiChuanTilePattern.isLongGen: False')  
        return False
    
    def isQuanYao(self, tableConfig):
        '''
        判断手牌是否为全幺 所有组成的顺子、刻子、将牌里都包含1或9
        '''
        # 房间配置为0，则没有全幺九
        if not tableConfig.get(MFTDefine.QUANYAOJIU_DOUBLE, 0):
            ftlog.debug('MSiChuanTilePattern.isQuanYao False because roomConfig')
            return False
        return MWin.isQuanYaoJiu(self.playerAllTiles)
    
    def isDuanYao(self, tableConfig):
        '''
        判断手牌是否为断幺
        '''
        # 房间配置为0，则没有全幺九
        if not tableConfig.get(MFTDefine.DUANYAOJIU_DOUBLE, 0):
            ftlog.debug('MSiChuanTilePattern.isDuanYao False because roomConfig')
            return False
        
        tiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        ftlog.debug('MSiChuanTilePattern.isDuanYao tiles:', tiles)
        for tile in tiles:
            tileValue = MTile.getValue(tile)
            if tileValue == 1 or tileValue == 9:
                ftlog.debug('MSiChuanTilePattern.isDuanYao : False')
                return False
        ftlog.debug('MSiChuanTilePattern.isDuanYao: True')
        return True
    
    def isJinGouDiao(self): 
        '''
        金钩钓 单吊一张
        '''
        return self.isShouzhuayi()
    
    def isMenQing(self):
        '''
        胡牌时没有碰过牌，没有明杠过
        '''
        # 判断房间配置中，是否有门清选项    
        if not self.tableTileMgr.tableConfig.get(MTDefine.MEN_CLEAR_DOUBLE, 0):
            ftlog.debug('MSiChuanTilePattern.isMenQing False because roomConfig')
            return False
        
        handTiles = self.playerAllTiles[MHand.TYPE_HAND]
        
        # 获取杠的牌
        allGangPattern = []
        for gangObj in self.playerAllTiles[MHand.TYPE_GANG]:
            gang = {}
            if gangObj.has_key('pattern'):
                gang['pattern'] = gangObj['pattern']
            if gangObj.has_key('style'):
                gang['style'] = gangObj['style']
            if gangObj.has_key('actionID'):
                gang['actionID'] = gangObj['actionID']
            if gangObj.has_key('styleScore'):
                gang['styleScore'] = gangObj['styleScore']
            allGangPattern.append(gang)
        
        _, an = MTile.calcGangCount(allGangPattern)
        
        ftlog.debug('MSichuanTilePattern.isMenQing handTiles:', handTiles
                            , 'allGang:', allGangPattern
                            , 'an:', an)
        if len(handTiles) == 14 - an * 3:
            return True
        else:
            return False
            
    # 根据玩家手牌获取 玩家可胡番型
    def getFanSymbolFromAllTiles(self):
        '''
        基本番型是 对对胡 金钩钓 七对 全幺九 断幺九
        '''
        fanSymbol = []
        isQingYiSeFlag = False
        if self.isQingyise():
            isQingYiSeFlag = True
            fanSymbol.append(self.QINGYISE)
            
        isQuanJiang = False
        if self.isQuanJiang():
            isQuanJiang = True
        
        isLong = False
        if self.isLongGen():
            isLong = True
        
        if self.isDuiDuiHu():
            ftlog.debug('MSiChuanTilePattern.isDuiDuiHu True')
            if isQingYiSeFlag:
                fanSymbol.append(self.QINGDUI)  
            elif isQuanJiang:
                if self.tableTileMgr.tableConfig.get(MFTDefine.JIANGDUI_DOUBLE, 0):
                    ftlog.debug('MSiChuanTilePattern.isQuanJiang True because roomConfig')
                    fanSymbol.append(self.JIANGDUI)             
            else:
                fanSymbol.append(self.DUIDUIHU)

        result, pattern = self.isQidui()
        if result:
            if isQingYiSeFlag and isLong:
                fanSymbol.append(self.QINGLONGQIDUI)
            elif isQingYiSeFlag:
                fanSymbol.append(self.QINGQIDUI)
            elif isLong:
                fanSymbol.append(self.LONGQIDUI)
            elif isQuanJiang:
                fanSymbol.append(self.JIANGQIDUI)
            else:
                fanSymbol.append(self.QIDUI)
        
        if self.isQuanYao(self.tableTileMgr.tableConfig):
            if isQingYiSeFlag:
                fanSymbol.append(self.QINGYAOJIU)
            else:
                fanSymbol.append(self.QUANYAOJIU)
        
        if self.isDuanYao(self.tableTileMgr.tableConfig):
            fanSymbol.append(self.DUANYAOJIU)
            
        if self.isJinGouDiao():
            if isQingYiSeFlag:
                fanSymbol.append(self.QINGJINGOUDIAO)   
            elif isQuanJiang:
                fanSymbol.append(self.JIANGJINGOUDIAO)
            else:
                fanSymbol.append(self.JINGOUDIAO)
                
        if self.isShiBaLuoHan():
            if isQingYiSeFlag:
                fanSymbol.append(self.QINGSHIBALUOHAN)  
            else:
                fanSymbol.append(self.SHIBALUOHAN)
        
        
        if self.isMenQing():
            fanSymbol.append(self.MENQING)
                
        fanSymbol.append(self.PINGHU)
        ftlog.debug('MSiChuanTilePattern.getFanSymbolFromAllTiles fanSymbol:', fanSymbol)
        return self.getMaxFanByResult(fanSymbol)
    
    # 从结果番型列表中获取最大
    def getMaxFanByResult(self, fanSymbol):
        maxIndex = 0
        maxFan = self.PINGHU
        for fan in fanSymbol:
            if self.fanXing[fan]['index'] > maxIndex:
                maxFan = fan 
                maxIndex = self.fanXing[fan]['index']
        ftlog.debug('MSiChuanTilePattern.getMaxFanByResult maxIndex:', maxIndex
                    , 'maxFan:', maxFan)
        return maxFan
    
    def getLongGenCount(self):
        '''
        获取玩家手牌根的个数 杠过的牌也算
        ''' 
        count = 0
        tiles = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        tileArr = MTile.changeTilesToValueArr(tiles)
        for tile in tileArr:
            if tile == 4:
                count += 1
        return count
    
    
    def calcFanPatternTing(self):
        '''
        计算倍数 番型＋根数
        '''
        fanSymbol = self.getFanSymbolFromAllTiles()
        fanNum = self.fanXing[fanSymbol]['index']
        gengNum = self.getLongGenCount()
        
        # 过滤一下不计的根数
        if self.genXing.has_key(fanSymbol):
            gengNum -= self.genXing[fanSymbol]
        
        result = pow(2, fanNum + gengNum)
        ftlog.debug('MSiChuanTilePattern.calcFanPatternTing result:', result, 'fanNum:', fanNum, 'gengNum:', gengNum)
        return result
    
    def calcFanPattern(self):
        '''计算番型数值'''
        # 手牌添加winTile，判断番型
        fanSymbol = self.getFanSymbolFromAllTiles()
        result = pow(2, self.fanXing[fanSymbol]['index'])
        ftlog.debug('MSiChuanTilePattern.calcFanPattern resultList:', result)
        return result
    
if __name__ == "__main__":
    checker = MSichuanTilePatternChecker()
    checker.setTableConfig({})
