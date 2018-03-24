# -*- coding=utf-8
'''
Created on 2016年12月11日
牌型整理
@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.tile_pattern_checker.tile_pattern_checker import MTilePatternChecker
from majiang2.player.hand.hand import MHand
from majiang2.ai.win import MWin
from majiang2.ai.play_mode import MPlayMode
from majiang2.table_tile.table_tile_factory import MTableTileFactory
from majiang2.table.table_config_define import MTDefine

class MJiPingHuTilePatternChecker(MTilePatternChecker):
    """
    基础番型计算
    仅仅有手牌组成的番型计算，不考虑打牌时的具体情况，比如自摸，点炮，杠开，海底捞等。
    只考虑基本番型，比如七对，清一色，风一色，对对胡等等。
    
    算分时，结合胡牌的具体情况+番型，计算。比如清一色+杠开等
    只判断当前玩家的番型
    """
    
    '''
    和牌的番型
    '''
    
    # 鸡胡
    JIHU = 'JIHU'
    # 平胡
    PINGHU = 'PINGHU'
    # 对对胡
    PENGPENGHU = 'PENGPENGHU'
    # 混一色
    HUNYISE = 'HUNYISE'
    # 清一色
    QINGYISE = 'QINGYISE'
    # 清碰
    QINGPENG = 'QINGPENG'
    # 混碰
    HUNPENG = 'HUNPENG'
    # 七对
    QIDUI = 'QIDUI'
    # 豪华七小对
    HAOHUAQIDUI = 'HAOHUAQIDUI'
    # 混幺九
    HUNYAOJIU = 'HUNYAOJIU'
    # 清幺九
    QINGYAOJIU = 'QINGYAOJIU'
    # 小三元
    XIAOSANYUAN = 'XIAOSANYUAN'
    # 大三元
    DASANYUAN = 'DASANYUAN'
    # 小四喜
    XIAOSIXI = 'XIAOSIXI'
    # 大四喜
    DASIXI = 'DASIXI'
    # 字一色
    ZIYISE = 'ZIYISE'
    # 九莲宝灯
    JIULIANBAODENG = 'JIULIANBAODENG'
    # 十三幺
    SHISANYAO = 'SHISANYAO'
    
    def __init__(self):
        super(MJiPingHuTilePatternChecker, self).__init__()

        self.addFanXing(self.JIHU, "鸡胡", 1)
        self.addFanXing(self.PINGHU, '平胡', 2)
        self.addFanXing(self.PENGPENGHU, '碰碰胡', 8)
        self.addFanXing(self.HUNYISE, '混一色', 8)
        self.addFanXing(self.QINGYISE, '清一色', 16)

        self.addFanXing(self.QINGPENG, '清碰', 32)
        self.addFanXing(self.HUNPENG, '混碰', 16)
        self.addFanXing(self.QIDUI, '七对', 16)
        self.addFanXing(self.HAOHUAQIDUI, '豪华七对', 32)
        self.addFanXing(self.HUNYAOJIU, '混幺九', 32)
        self.addFanXing(self.QINGYAOJIU, '清幺九', 64)

        self.addFanXing(self.XIAOSANYUAN, '小三元', 32)
        self.addFanXing(self.DASANYUAN, '大三元', 64)
        self.addFanXing(self.XIAOSIXI, '小四喜', 32)
        self.addFanXing(self.DASIXI, '大四喜', 64)

        self.addFanXing(self.ZIYISE, '字一色', 64)
        self.addFanXing(self.JIULIANBAODENG, '九莲宝灯', 64)
        self.addFanXing(self.SHISANYAO, '十三幺', 64)

    # 根据玩家手牌获取 玩家可胡番型
    def getWinFanList(self):

        fanlist=[]
        baohu=False

        allTile = MHand.copyAllTilesToListButHu(self.playerAllTiles)
        ftlog.debug('MJiPingHuTilePattern.getWinFanList,,allTile:', allTile
                    ,' self.playerAllTiles',self.playerAllTiles)

        '''64'''
        if self.isShisanyao():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.SHISANYAO)
            fanlist.append(self.SHISANYAO)
            return fanlist,False

        if self.isJiuLianBaoDeng():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.JIULIANBAODENG)
            fanlist.append(self.JIULIANBAODENG)
            return fanlist, False

        isqingyise = False
        ishunyise = False
        isziyise = self.isZiyise()
        if not isziyise:
            isqingyise = self.isQingyise()
            if not isqingyise:
                ishunyise = self.isHunYiSe()

        '''64'''
        if self.isDasixi():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.DASIXI)
            fanlist.append(self.DASIXI)
        elif self.isDasanyuan():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.DASANYUAN)
            fanlist.append(self.DASANYUAN)
        elif self.isQingyaojiu():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.QINGYAOJIU)
            fanlist.append(self.QINGYAOJIU)
        if fanlist!=[]:
            if isziyise:
                fanlist.append(self.ZIYISE)
            elif isqingyise:
                fanlist.append(self.QINGYISE)
            elif ishunyise:
                fanlist.append(self.HUNYISE)
        if fanlist != []:
            return fanlist, False


        '''32'''
        if self.isXiaosixi():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.XIAOSIXI)
            fanlist.append(self.XIAOSIXI)
        elif self.isXiaosanyuan():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.XIAOSANYUAN)
            fanlist.append(self.XIAOSANYUAN)
        elif self.isHunyaojiu():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.HUNYAOJIU)
            fanlist.append(self.HUNYAOJIU)
        elif self.isQiduiHao():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.HAOHUAQIDUI)
            fanlist.append(self.HAOHUAQIDUI)
        else:
            result, pattern = self.isQidui()
            if result:
                ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.QIDUI)
                fanlist.append(self.QIDUI)
        if fanlist!=[]:
            if isziyise:
                fanlist.append(self.ZIYISE)
            elif isqingyise:
                fanlist.append(self.QINGYISE)
            elif ishunyise:
                fanlist.append(self.HUNYISE)
        if fanlist != []:
            return fanlist, False

        #如果是字一色，也不用判断碰碰胡了
        if isziyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.ZIYISE)
            fanlist.append(self.ZIYISE)
            return fanlist, False

        ispenghu,x = self.isPengpenghu()
        if ispenghu and isqingyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.QINGPENG)
            fanlist.append(self.QINGPENG)
        elif ispenghu and ishunyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.HUNPENG)
            fanlist.append(self.HUNPENG)
        elif ispenghu:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.PENGPENGHU)
            fanlist.append(self.PENGPENGHU)
        elif isqingyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.QINGYISE)
            fanlist.append(self.QINGYISE)
        elif ishunyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.HUNYISE)
            fanlist.append(self.HUNYISE)
        if fanlist != []:
            return fanlist, False

        result, rePattern = MWin.isHu(self.playerAllTiles[MHand.TYPE_HAND])
        if self.isPingHu(rePattern):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.PINGHU)
            fanlist.append(self.PINGHU)
            return fanlist, True
        else:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.JIHU)
            fanlist.append(self.JIHU)
            return fanlist,True

    def getWinFanWithMagic(self):

        fanlist=[]
        baohu=False

        result, rePattern = MWin.isHu(self.playerAllTiles[MHand.TYPE_HAND], self.tableTileMgr.getMagicTiles())
        ftlog.debug('MJiPingHuTilePattern.getWinFanWithMagic: result',result,'rePattern',rePattern)
        #if not result:
        #   return fanlist, False

        magictiles = self.tableTileMgr.getMagicTiles()
        if len(magictiles)==0:
            ftlog.debug('MJiPingHuTilePattern.getWinFanWithMagic:len(magictiles)==0')
            return fanlist, False

        ftlog.debug('MJiPingHuTilePattern.getWinFanWithMagic:', rePattern)

        '''64'''
        if self.isShisanyao(magictiles):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.SHISANYAO)
            fanlist.append(self.SHISANYAO)
            return fanlist,False

        if self.isJiuLianBaoDeng():
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.JIULIANBAODENG)
            fanlist.append(self.JIULIANBAODENG)
            return fanlist, False

        isqingyise = False
        ishunyise = False
        isziyise = self.isZiyise()
        if not isziyise:
            isqingyise = self.isQingyise()
            if not isqingyise:
                ishunyise = self.isHunYiSe()

        '''64'''
        if self.isDasixiMagic(rePattern,magictiles[0]):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.DASIXI)
            fanlist.append(self.DASIXI)
        elif self.isDasanyuanMagic(rePattern,magictiles[0]):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.DASANYUAN)
            fanlist.append(self.DASANYUAN)
        elif self.isQingyaojiu(magictiles):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.QINGYAOJIU)
            fanlist.append(self.QINGYAOJIU)
        if fanlist!=[]:
            if isziyise:
                fanlist.append(self.ZIYISE)
            elif isqingyise:
                fanlist.append(self.QINGYISE)
            elif ishunyise:
                fanlist.append(self.HUNYISE)
        if fanlist != []:
            return fanlist, False


        '''32'''
        if self.isXiaosixiMagic(rePattern,magictiles[0]):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.XIAOSIXI)
            fanlist.append(self.XIAOSIXI)
        elif self.isXiaosanyuanMagic(rePattern,magictiles[0]):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.XIAOSANYUAN)
            fanlist.append(self.XIAOSANYUAN)
        elif self.isHunyaojiu(magictiles):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.HUNYAOJIU)
            fanlist.append(self.HUNYAOJIU)
        elif self.isQiduiHao(magictiles):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.HAOHUAQIDUI)
            fanlist.append(self.HAOHUAQIDUI)
        else:
            result,pattern = self.isQidui(magictiles)
            if result:
                ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.QIDUI)
                fanlist.append(self.QIDUI)
        if fanlist!=[]:
            if isziyise:
                fanlist.append(self.ZIYISE)
            elif isqingyise:
                fanlist.append(self.QINGYISE)
            elif ishunyise:
                fanlist.append(self.HUNYISE)
        if fanlist != []:
            return fanlist, False

        #如果是字一色，也不用判断碰碰胡了
        if isziyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.ZIYISE)
            fanlist.append(self.ZIYISE)
            return fanlist, False

        ispenghu,x = self.isPengpenghu(magictiles[0])
        if ispenghu and isqingyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.QINGPENG)
            fanlist.append(self.QINGPENG)
        elif ispenghu and ishunyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.HUNPENG)
            fanlist.append(self.HUNPENG)
        elif ispenghu:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.PENGPENGHU)
            fanlist.append(self.PENGPENGHU)
        elif isqingyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.QINGYISE)
            fanlist.append(self.QINGYISE)
        elif ishunyise:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.HUNYISE)
            fanlist.append(self.HUNYISE)
        if fanlist != []:
            return fanlist, False


        if self.isPingHu(rePattern,magictiles):
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.PINGHU)
            fanlist.append(self.PINGHU)
            return fanlist, True
        else:
            ftlog.debug('MJiPingHuTilePattern.getFanSymbolFromAllTiles:', self.JIHU)
            fanlist.append(self.JIHU)
            return fanlist,True

    def calcFanPatternTing(self):
        '''
        计算倍数 番型＋根数
        '''
        if self.tableTileMgr.tableConfig.get(MTDefine.LAIZI, 0):
            fanSymbol, _ = self.getWinFanWithMagic()
        else:
            fanSymbol, _ = self.getWinFanList()

        resultBeishu = 0
        for fan in fanSymbol:
            fanNum = self.fanXing[fan]['index']
            resultBeishu += fanNum

        ftlog.debug('MJiPingHuTilePattern.calcFanPatternTing resultBeishu:', resultBeishu,'fanSymbol:',fanSymbol)
        return resultBeishu

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

    
if __name__ == "__main__":
    checker = MJiPingHuTilePatternChecker()
    mgr = MTableTileFactory.getTableTileMgr(4, MPlayMode.JIPINGHU, 0)
    mgr.addMagicTile(18)
    checker.setTableTileMgr(mgr)
    #checker.setPlayerAllTiles([[31,31,31,32,32,32,33,33,33,34,34,34,35,35],[],[],[],[],[],[],[]])

    #checker.setPlayerAllTiles([[8, 36, 35, 3, 3, 3, 4, 4, 4, 35, 35], [], [[37, 37, 37]], [], [], [], [], []])
    #碰碰胡
    #checker.setPlayerAllTiles([[22, 8, 22, 23, 23, 23, 24, 8, 24, 35, 35, 35, 36, 36], [], [], [], [], [], [], []])
    #平胡
    #checker.setPlayerAllTiles([[1,2,3,18,7,18,21,22,23,11,12,13, 36, 36], [], [], [], [], [], [], []])

    checker.setPlayerAllTiles([[2, 2, 2, 23, 23, 23, 24, 24, 24, 35,35, 35, 36, 36], [], [], [], [], [], [], []])

    fanlist = checker.getWinFanList()
    #fanlist = checker.getWinFanWithMagic()
    ftlog.debug('checker.getWinFanWithMagic:', fanlist)
