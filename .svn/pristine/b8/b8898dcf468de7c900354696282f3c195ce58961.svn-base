# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from majiang2.win_rule.win_rule import MWinRule
from majiang2.ai.win import MWin
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
from freetime5.util import ftlog
from majiang2.table.table_config_define import MTDefine
import copy

class MWinRuleJixi(MWinRule):
    """
    鸡西玩法的和牌规则
    1）没听牌 不和
    2）和牌不可以过
    3）和牌完全从听中去和牌番型
    """
    def __init__(self):
        super(MWinRuleJixi, self).__init__()
    
    def isHu(self, tiles, tile, isTing, getTileType, magicTiles = [], tingNodes = [], winSeatId = 0):
        if not isTing:
            # 没听牌 不和
            return False, []
        
        
        # 鸡西打宝炮(先不支持 之后通过配置项目支持) 玩家上听后没有听牌的玩家打出宝牌 则听牌玩家和牌
        # 听牌之后自摸到宝牌 自动和牌
        if isTing and getTileType == MWinRule.WIN_BY_MYSELF:
            if (tile in magicTiles):
                # 听牌并且是宝牌，和牌
                return True, []
        
        ftlog.debug('win_rule_jixi.isHu tiles:', tiles
                    , ' magicTiles:', magicTiles
                    , ' tile:', tile)
        
        # 这里的鸡西七对判断胡牌，不用宝牌，判断原始牌。宝牌在上面的逻辑里会判断胡牌
        resultQiDui, patternQiDui = MWin.isQiDui(tiles[MHand.TYPE_HAND])
        if resultQiDui:
            return True, patternQiDui
        
        result, pattern = MWin.isHu(tiles[MHand.TYPE_HAND])
        if not result:
            return False, []
        
        #从tingNode中判断，如果是听规则中的才算胡
        if len(tingNodes) > 0:
            hasTile = False
            pattern = []
            #[{'winTile': 16, 'winTileCount': 0, 'pattern': [[16, 17, 18], [12, 12]]}, {'winTile': 19, 'winTileCount': 0, 'pattern': [[17, 18, 19], [12, 12]]}] 
            for tingNode in tingNodes:
                if tingNode['winTile'] == tile:
                    hasTile = True
                    pattern = tingNode['pattern']
                    break
            if hasTile:
                #鸡西只有特大夹番型才能抢杠和
                if getTileType == MWinRule.WIN_BY_QIANGGANGHU:
                    if self.isTeDaJia(pattern, tingNodes, tiles, tile, winSeatId):
                        return True, pattern
                    else:
                        return False, []
                
                return True, pattern
            else:
                return False, []
        
        return True, pattern
    
    def isTeDaJia(self, winPattern, tingNodes, tiles, currWintile, curSeatId):
        winCount = 0
        isJiaCount = 0
        bianMulti = self.tableConfig.get(MTDefine.BIAN_MULTI, 0)
        for wn in tingNodes:
            winTile = wn['winTile']
            winCount = winCount + 1
            patterns = wn['pattern']
            ftlog.debug('MWinRuleJixi.isTaDaJia winTile:', winTile, ' winPatterns:', patterns)
            for p in patterns:
                if len(p) == 2:
                    continue
                    
                if p[0] == p[1]:
                    continue
                    
                # 夹牌
                if (wn['winTile'] in p) and len(p) == 3 and p[0] != p[1]:
                    if (p[1] == winTile) or (bianMulti and (MTile.getValue(winTile) == 3 or MTile.getValue(winTile) == 7)):
                        isJiaCount = isJiaCount + 1
                        
        #只能是夹牌 并且不能作为他用    
        if winCount > 1 or isJiaCount <= 0:
            ftlog.debug('MWinRuleJixi.isTaDaJia winTile:', winTile, 'winCount:', winCount, 'isJiaCount:', isJiaCount)
            return False
        
        # 他人的碰牌
        isInOtherPeng = False
        
        for (seatId, playerTiles) in self.allPlayerTiles.items():
            if seatId != curSeatId:
                playerPengTiles = playerTiles[MHand.TYPE_PENG]
                for pattern in playerPengTiles:
                    if pattern[0] == currWintile:
                        isInOtherPeng = True
                        break;
        
        isInSelfKe = False
        playerPengTiles = tiles[MHand.TYPE_PENG]
        for pattern in playerPengTiles:
            if pattern[0] == currWintile:
                isInSelfKe = True
                break
            
        #自己的手牌
        if not isInSelfKe:
            playerHandTiles = tiles[MHand.TYPE_HAND]
            winTileInHandCount = 0
            for tile in playerHandTiles:
                if tile == currWintile:
                    winTileInHandCount = winTileInHandCount + 1
                    if winTileInHandCount == 3:
                        isInSelfKe = True
                        break
            
        if not (isInSelfKe or isInOtherPeng):
            ftlog.debug('MWinRuleJixi.isTaDaJia winTile:', currWintile, 'isInSelfKe:', isInSelfKe, 'isInOtherPeng:', isInOtherPeng)
            return False
        
        return True
    
    def isMagicAfertTingHu(self, isTing, winNodes, magicTiles, extendInfo = {}):
        if len(magicTiles) == 0:
            #ftlog.debug('isMagicAfertTingHu magcicTile is zero')
            return False
        magicTile = magicTiles[0]
        if isTing:
            #[{'winTile': 1, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [1, 2, 3]]}
            for winNode in winNodes:
                if winNode['winTile'] == magicTile:
                    ftlog.debug('isMagicAfertTingHu success magcicTile is', magicTile)
                    return True
        return False
    
    # 三人麻将无对胡，按照逆时针顺序判断
    def isShuffleWin(self, allTiles, winTile, curSeatId, playerCount):
        if playerCount >= 4:
            return False
        
        playerTiles = allTiles
        handTiles = copy.deepcopy(playerTiles[MHand.TYPE_HAND])
        ftlog.debug('MWinRuleJixi.isWuDuiHu seatId:', curSeatId
                    , ' curSeatId:', curSeatId
                    , ' playerCount:', playerCount
                    , ' tilesCount:', len(handTiles)
                    , ' tiles:', handTiles)
            
        handTilesArr = MTile.changeTilesToValueArr(handTiles)
        hasPair = False
        for handTile in handTiles:
            if handTilesArr[handTile] >= 2:
                hasPair = True
                break
        if not hasPair:
            return True
        
        return False
        
    def canWinAfterChiPengGang(self, tiles):
        """吃完之后是否能和牌"""
        
        handTiles = tiles[MHand.TYPE_HAND]
        count = len(handTiles) - 2
        
        ftlog.debug( 'MTingHaerbinJixi.isPiaoHu canWinAfterChiPengGang:',count,'tiles:',handTiles )
        #飘可以手把一
        if count == 3:
            if len(tiles[MHand.TYPE_CHI])==0:
                ftlog.debug( 'MTingHaerbinJixi.isPiaoHu canWinAfterChiPengGang return true' )
                return True
            else:
                ftlog.debug( 'MTingHaerbinJixi.isPiaoHu canWinAfterChiPengGang return false' )
                return False
        
        if count < 4:
            ftlog.debug( 'MTingHaerbinJixi.isPiaoHu canWinAfterChiPengGang return false' )
            return False
        
        ftlog.debug( 'MTingHaerbinJixi.isPiaoHu canWinAfterChiPengGang return true' )
        return True
    
    def isTianHu(self, player, actionId, tile, tableTileMgr, tingRuleMgr):
        if actionId > 1:
            return False
        
        #用听牌规则判断 庄家可以听就直接胡牌
        isTing, tingArr = tingRuleMgr.canTing(player.copyTiles(), tableTileMgr.tiles, tile, [], player.curSeatId)
        if isTing:
            ftlog.debug('MTableLogic.checkBeginHu isTing:', isTing
                        , ' player all tiles:', player.copyTiles()
                        , ' tingArr:', tingArr)

            for tingInfo in tingArr:
                for winNode in tingInfo['winNodes']:
                    #打出去和胡的一样 说明可以直接和牌
                    if (tingInfo['dropTile'] == winNode['winTile']):
                        return True
        return False
    
if __name__ == "__main__":
    tiles = [[1,2,3,4,5,6,7,8,9,11,11], [[12,13,14]], [], [], [], []]
    rule = MWinRuleJixi()
    ftlog.debug(rule.isHu(tiles, 2, True, [3]))