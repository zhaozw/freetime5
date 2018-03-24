# -*- coding=utf-8
'''
Created on 2016年9月23日
听牌规则
@author: zhaol
'''
from majiang2.ai.ting import MTing
from majiang2.tile.tile import MTile
from majiang2.player.hand.hand import MHand
from majiang2.ting_rule.ting_rule import MTingRule
from freetime5.util import ftlog
from majiang2.table.table_config_define import MTDefine
from majiang2.win_rule.win_rule_haerbin import MWinRuleHaerbin
import copy

class MTingHaerbinRule(MTingRule):
    """听牌规则
    1）听牌时，牌中必须带至少一个“幺”或“九”。
    2）听牌时，牌中必须带至少一组刻牌（即三张一样的牌，一对红中一般可以代替）。特例：没有刻牌，可以和对倒。和牌时必须至少有一组顺牌（例123或789）
    3）红中就可代替这个“幺九牌条件”。
    4）必需先开门（非“门清”状态）才能听牌，即必须吃、碰一组牌后才可听牌。
    5）特殊玩法：吃听。当手牌吃一次就可以上听时，别人打出一张要吃的牌，不管是不是上家都可以吃。吃后自动报听(注:只有在听牌状态下才可胡牌)
    6）配置了夹起步选项时只能和夹和3，7
    """
    def __init__(self):
        super(MTingHaerbinRule, self).__init__()
    
    def getKeCount(self, patterns):
        """
        patterns当中有几个刻
        [[6, 6], [5, 6, 7], [4, 5, 6], [1, 2, 3]]
        """
        count = 0
        for pattern in patterns:
            if (len(pattern) == 2) and (pattern[0] == MTile.TILE_HONG_ZHONG):
                count += 1
            
            if (len(pattern) == 3) and (pattern[0] == pattern[1]) and (pattern[1] == pattern[2]):
                count += 1
        return count
    
    def getShunCount(self, patterns):
        """获取顺子的数量"""
        count = 0
        for p in patterns:
            if len(p) != 3:
                continue
            
            if (p[0] + 2 == p[2]) and (p[1] + 1 == p[2]):
                count += 1
        
        return count

    def canTing(self, tiles, leftTiles, tile, magicTiles = [], winSeatId = 0):
        """子类必须实现
        参数：
        1）tiles 该玩家的手牌
        2）leftTiles 剩余手牌
        返回值：
        是否可以听牌，听牌详情
        """
        handCount = len(tiles[MHand.TYPE_HAND])
        if handCount < 5:
            return False, []

        isTing, tingResults = MTing.canTing(self.tilePatternChecker, self.tableTileMgr, MTile.cloneTiles(tiles), leftTiles, self.winRuleMgr, tile, magicTiles, winSeatId)
        ftlog.debug( 'MTingHaerbinRule.MTing.canTing isTing:', isTing, ' tingResults:', tingResults )
#         [{'dropTile': 11, 'winNodes': [{'winTile': 1, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [1, 2, 3]]}, {'winTile': 2, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [3, 4, 5], [2, 2]]}, {'winTile': 4, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [2, 3, 4]]}, {'winTile': 5, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [5, 5], [2, 3, 4]]}, {'winTile': 7, 'winTileCount': 1, 'pattern': [[6, 6], [5, 6, 7], [5, 6, 7], [2, 3, 4]]}, {'winTile': 8, 'winTileCount': 1, 'pattern': [[6, 7, 8], [6, 6, 6], [5, 5], [2, 3, 4]]}]}]

        if not isTing:
            return False, []
        
        chiCount = len(tiles[MHand.TYPE_CHI])
        pengCount = len(tiles[MHand.TYPE_PENG])
        gangCount = len(tiles[MHand.TYPE_GANG])
        
        mingGangCount = 0 
        anGangCount = 0
        #计算明杠个数，因为暗杠不算开门
        if gangCount!=0:
            mingGangCount,anGangCount = MTile.calcGangCount(tiles[MHand.TYPE_GANG])
        ftlog.debug( 'MTingHaerbinRule.gang tiles:', tiles[MHand.TYPE_GANG],' mingGangCount=',mingGangCount,' anGangCount=',anGangCount)
        
        if (chiCount + pengCount + mingGangCount) == 0:
            return False, []
                
        # 检查刻，刻的来源，碰牌/明杠牌/手牌
        keCount = pengCount + mingGangCount + anGangCount
        # 必须有顺牌
        shunCount = chiCount
            
        newTingResults = []
        for tingResult in tingResults:
            newWinNodes = []
            winNodes = tingResult['winNodes']
            for winNode in winNodes:
                newTiles = MTile.cloneTiles(tiles)
                newTiles[MHand.TYPE_HAND].remove(tingResult['dropTile'])
                newTiles[MHand.TYPE_HAND].append(winNode['winTile'])
                tileArr = MTile.changeTilesToValueArr(MHand.copyAllTilesToList(newTiles))
        #       ftlog.debug( 'MTingHaerbinRule.canTing tileArr:', tileArr )
                
                # 清一色不可以听牌/和牌
                if self.getTableConfig(MTDefine.YISE_CAN_TING, 0) != 1:
                    newTileArr = copy.deepcopy(tileArr)
                    newTileArr[MTile.TILE_HONG_ZHONG] = 0
                    colorCount = MTile.getColorCount(newTileArr)
                    if colorCount == 1:
                        # 清一色不能和牌
                        ftlog.debug('MTingHaerbinRule.canTing colorCount:', colorCount, ' can not win, continue....')
                        continue
                
                # 检查牌中的幺/九   
                # 1软 听牌可以没有19，只要胡牌带19就可以
                # 2硬 听牌时就要有19 
                RuanYaoJiuConfig = self.getTableConfig(MTDefine.RUAN_YAO_JIU, 1)
                if RuanYaoJiuConfig==0:
                    #硬幺九 ：听牌必须有19
                    #tileArr 减去 winNode['winTile'] 后判断
                    tileArr[winNode['winTile']] -= 1
                    yaoCount = tileArr[MTile.TILE_ONE_WAN] + tileArr[MTile.TILE_ONE_TONG] + tileArr[MTile.TILE_ONE_TIAO]
                    jiuCount = tileArr[MTile.TILE_NINE_WAN] + tileArr[MTile.TILE_NINE_TONG] + tileArr[MTile.TILE_NINE_TIAO]
                    zhongCount = tileArr[MTile.TILE_HONG_ZHONG]
                    ftlog.debug('MTingJixiRule.canTing : YING yaoCount:',yaoCount,'jiuCount',jiuCount,'zhongCount',zhongCount)
                    if (yaoCount + jiuCount + zhongCount) <= 0:
                        continue     
                else:
                    #软幺九 :只要胡牌有19就行
                    yaoCount = tileArr[MTile.TILE_ONE_WAN] + tileArr[MTile.TILE_ONE_TONG] + tileArr[MTile.TILE_ONE_TIAO]
                    jiuCount = tileArr[MTile.TILE_NINE_WAN] + tileArr[MTile.TILE_NINE_TONG] + tileArr[MTile.TILE_NINE_TIAO]
                    zhongCount = tileArr[MTile.TILE_HONG_ZHONG]
                    ftlog.debug('MTingJixiRule.canTing : RUAN yaoCount:',yaoCount,'jiuCount',jiuCount,'zhongCount',zhongCount)
                    if (yaoCount + jiuCount + zhongCount) == 0:
                        continue
                        
                
                
                patterns = winNode['pattern']
                #夹起步(顺牌只能和夹和3，7) 除单吊
                chunJiaConfig = self.getTableConfig(MTDefine.MIN_MULTI, 0)
                if chunJiaConfig:
                    bianMulti = self.tableConfig.get(MTDefine.BIAN_MULTI, 0)
                    danDiaoJia = self.tableConfig.get(MTDefine.DAN_DIAO_JIA, 1)
                    hasJia = False
                    for pattern in patterns:
                        if winNode['winTile'] in pattern:
                            if len(pattern) == 3 and pattern[0] != pattern[1]:
                                if pattern.index(winNode['winTile']) == 2:
                                    if bianMulti:
                                        if MTile.getValue(winNode['winTile']) == 3:
                                            hasJia = True
                                            break
                                if pattern.index(winNode['winTile']) == 0:
                                    if bianMulti:
                                        if MTile.getValue(winNode['winTile']) == 7:
                                            hasJia = True
                                            break
                                        
                                if pattern.index(winNode['winTile']) == 1:
                                    hasJia = True
                                    break
                                        
                                    
                            #单吊
                            if len(pattern) == 2 and pattern[0] == pattern[1] and danDiaoJia:
                                hasJia = True
                                break    
                                    
                    if not hasJia:
                        ftlog.debug('MTingHaerbinRule.canTing :, can not win tile:', winNode['winTile'], ', not has jia continue....')
                        continue
                
                
                patterns = winNode['pattern']
                checkKeCount = keCount + self.getKeCount(patterns)
                checkShunCount = shunCount + self.getShunCount(patterns)
                ftlog.debug('MTingHaerbinRule.canTing keCount:', keCount, ' shunCount:', shunCount)
                
                if checkKeCount and checkShunCount:
                    newWinNodes.append(winNode)
                    
            if len(newWinNodes) > 0:
                newTingResult = {}
                newTingResult['dropTile'] = tingResult['dropTile']
                newTingResult['winNodes'] = newWinNodes
                newTingResults.append(newTingResult)
                
        return len(newTingResults) > 0, newTingResults
    
if __name__ == "__main__":
    tiles = [[3,4,15,5,5,6,9,9], [[26,27,28]], [[8,8,8]], [], [], []]
    rule = MTingHaerbinRule()
    rule.setWinRuleMgr(MWinRuleHaerbin())
    ftlog.debug(rule.canTing(tiles, [], 4, []))
