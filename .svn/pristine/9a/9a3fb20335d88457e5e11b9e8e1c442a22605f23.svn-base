# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from majiang2.table.table_config_define import MTDefine
from majiang2.tile.tile import MTile
from majiang2.win_rule.win_rule import MWinRule


class MWinRuleJiPingHu(MWinRule):
    
    """
    开局房主庄家
    需要传入缺牌的花色
    """
    def __init__(self):
        super(MWinRuleJiPingHu, self).__init__()
    
    def isHu(self, tiles, tile, isTing, getTileType, magicTiles=[], tingNodes=[], winSeatId=0):
        ftlog.debug('MWinRuleJiPingHu.isHu tiles:', tiles
                    , ' tile:', tile
                    , ' isTing:', isTing
                    , ' getTileType:', getTileType
                    , ' magicTiles:', magicTiles
                    , ' tingNodes:', tingNodes
                    , ' winSeatId:', winSeatId
                    )
 
        # 检查是否过胡状态
        if self.tableTileMgr.isPassHuTileBySeatId(winSeatId, tile):
            if self.msgProcessor:
                ftlog.debug('songsong MWinRuleJiPingHu.isHu isPassHuTileBySeatId:',winSeatId, 'tile:',tile)
                self.msgProcessor.table_call_show_tips(MTDefine.TIPS_NUM_10, self.tableTileMgr.players[winSeatId])
            return False, []
        
        huqidui = self.tableConfig.get(MTDefine.HUQIDUI, MTDefine.HUQIDUI_YES)
        if huqidui:
            resultQidui, qiduiPattern = MWin.isQiDui(tiles[MHand.TYPE_HAND], magicTiles)
            if resultQidui:
                ftlog.debug('MWinRuleJiPingHu.isQiDui True,', qiduiPattern)
                return True, qiduiPattern

        resultshisan = MWin.isShisanyao(tiles, magicTiles)
        if resultshisan:
            ftlog.debug('MWinRuleJiPingHu.isShisanyao True,')
            return True, []

        tileArr = MTile.changeTilesToValueArr(MHand.copyAllTilesToList(tiles))
        result, rePattern = MWin.isHu(tiles[MHand.TYPE_HAND], magicTiles)
        if result:
            ftlog.debug('MWinRuleJiPingHu.isHu True, ', rePattern)
            if getTileType == MWinRule.WIN_BY_OTHERS:
                jipinghu = False  # 【鸡胡】：X1，顺牌+刻牌+1对将. 鸡胡只能自摸/抢杠胡
                jipinghu = self.isJipinghu(rePattern, tiles, tileArr, magicTiles)
                if jipinghu:
                    if self.msgProcessor:
                        ftlog.debug('MWinRuleJiPingHu.isHu jipinghu buneng hu:')
                        self.msgProcessor.table_call_show_tips(MTDefine.TIPS_NUM_12,self.tableTileMgr.players[winSeatId])
                    return False, []
                else:
                    return True, rePattern
            else:
                return True, rePattern

        ftlog.debug('MWinRuleJiPingHu.isHu False, []')
        return False, []
    
    def getHuPattern(self, tiles, magicTiles=[]):
        return MWin.isHu(tiles[MHand.TYPE_HAND], magicTiles)
    
    def isPassHu(self):
        """是否有过胡规则"""
        return True

    def isJipinghu(self, pattern, tiles, tileArr, magicTiles):

        useforColor = tileArr
        if len(magicTiles) > 0:
            useforColor[magicTiles[0]] = 0

        hasfeng = 0
        for tile in MTile.traverseTile(MTile.TILE_FENG):
            if tileArr[tile]:
                hasfeng += 1
                break
        if MTile.getColorCount(useforColor) - hasfeng <= 1:
            return False

        kecount = 0
        shuncount = 0
        bothok = 0
        for p in pattern:
            if len(p) == 3:
                magiccount = 0
                for x in p:
                    if len(magicTiles) > 0 and x == magicTiles[0]:
                        magiccount += 1
                if magiccount >= 2:
                    bothok += 1
                else:
                    if p[0] == p[1] or p[0] == p[2] or p[1] == p[2]:
                        kecount += 1
                    else:
                        shuncount += 1

        kecount += len(tiles[MHand.TYPE_PENG])
        kecount += len(tiles[MHand.TYPE_GANG])

        ftlog.debug('MWinRuleJiPingHu.isJipinghu kecount:', kecount, 'shuncount:', shuncount, 'bothok:', bothok)

        # 排除掉碰碰胡
        if shuncount == 0:
            return False
        # 排除掉三元
        haszhong = 0
        for tile in [35, 36, 37]:
            if tileArr[tile] > 0:
                haszhong += 1
        if haszhong == 3:
            return False
        # 排除掉四喜
        hasfeng = 0
        for tile in [31, 32, 33, 34]:
            if tileArr[tile] > 0:
                hasfeng += 1
        if hasfeng == 4:
            return False

        if shuncount > 0 and kecount > 0:
            ftlog.debug('MWinRuleJiPingHu.isJipinghu True')
            return True

        return False
    
def testHu():
    '''
    测试胡牌
    '''
    tiles = [[8, 9, 12, 12, 13, 13, 13, 14, 14, 14, 16, 16, 16, 1], [], [], [], [], [], [7], []]
    rule = MWinRuleJiPingHu()
    isHu = rule.isHu(tiles, 1, True, 0, [9], [], 0)
    ftlog.debug('isHu:', isHu)
    
def testQiDui():
    '''
    测试七对
    '''
    tiles = [[1,1,4,4,4,37,7,7,15,15,18,18,36,36], [], [], [], [], [], [36], []]
    rule = MWinRuleJiPingHu()
    isHu = rule.isHu(tiles, 11, False, 0, [37], [], 0)
    ftlog.debug('isHu:', isHu)

if __name__ == "__main__":
    # testHu()
    testQiDui()