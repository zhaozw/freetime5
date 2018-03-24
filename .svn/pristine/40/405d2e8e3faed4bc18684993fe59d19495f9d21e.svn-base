# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from majiang2.ai.play_mode import MPlayMode
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
from majiang2.win_rule.win_rule import MWinRule
from majiang2.win_rule.win_rule_factory import MWinRuleFactory
from freetime5.util import ftlog

"""
结果样例：
[{'dropTile': 11, 'winNodes': [{'winTile': 1, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [1, 2, 3]]}, {'winTile': 2, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [3, 4, 5], [2, 2]]}, {'winTile': 4, 'winTileCount': 3, 'pattern': [[6, 6], [5, 6, 7], [4, 5, 6], [2, 3, 4]]}, {'winTile': 5, 'winTileCount': 2, 'pattern': [[6, 6, 6], [5, 6, 7], [5, 5], [2, 3, 4]]}, {'winTile': 7, 'winTileCount': 1, 'pattern': [[6, 6], [5, 6, 7], [5, 6, 7], [2, 3, 4]]}, {'winTile': 8, 'winTileCount': 1, 'pattern': [[6, 7, 8], [6, 6, 6], [5, 5], [2, 3, 4]]}]}]
"""
class MTing(object):
    """是否可以听牌
    如果可以听牌，可以和哪些牌
    判断流程：
    去掉一张手牌，加入一张牌，是否可以和
    如果可以和，去掉改手牌，进入听牌状态，和可以和的牌。可以和的牌会有多个
    
    对可以和的牌，提示剩余牌的张数
    """
    
    def __init__(self):
        super(MTing, self).__init__()
        
    @classmethod    
    def chooseBestTingSolution(cls, tingReArr):
        """选择最好的听牌方案"""
        chooseTile = 0
        maxCount = 0
        chooseWinNodes = []
        for tingSolution in tingReArr:
            dropTile = tingSolution['dropTile']
            winNodes = tingSolution['winNodes']
            count = 0
            for node in winNodes:
                winTileCount = node['winTileCount']
                count += winTileCount
            if count > maxCount:
                maxCount = count
                chooseTile = dropTile
                chooseWinNodes = winNodes
                
        return chooseTile, chooseWinNodes
    
    @classmethod
    def canTingBeforeAddTile(cls, tilePatternChecker, tableTileMgr, tiles, leftTiles, winRule, magicTiles=[], curSeatId=0, winSeatId=0):
        """判断在摸牌之前是否可以听
        """
        ftlog.debug('MTing.canTingBeforeAddTile', tiles)
        leftTileArr = MTile.changeTilesToValueArr(leftTiles)
        leftTileCount = len(leftTileArr)
        ftlog.debug('MTing.canTing leftTiles:', leftTiles
                     , ' leftTileArr:', leftTileArr
                     , ' leftTileCount:', leftTileCount)
        
        result = []
        resultNode,isHuAll = cls.canWinAddOneTile(tilePatternChecker, tableTileMgr, leftTileArr, leftTileCount, tiles, winRule, magicTiles, winSeatId)
        if len(resultNode) > 0:
            winNode = {}
            winNode['winNodes'] = resultNode
            result.append(winNode)
                
        return len(result) > 0, result
    
    @classmethod
    def canTing(cls, tilePatternChecker, tableTileMgr, tiles, leftTiles, winRule, tile, magicTiles=[], winSeatId=0):
        """
        判断是否可以听牌
        参数：
        1）tiles 手牌
        2）leftTiles 剩余未发的牌
        
        返回值：
        
        """
        ftlog.debug('MTile.changeTilesToValueArr', tiles[MHand.TYPE_HAND])
        handTileArr = MTile.changeTilesToValueArr(tiles[MHand.TYPE_HAND])
        
        leftTileArr = MTile.changeTilesToValueArr(leftTiles)
        leftTileCount = len(leftTileArr)
        ftlog.debug('MTing.canTing leftTiles:', leftTiles
                     , ' leftTileArr:', leftTileArr
                     , ' leftTileCount:', leftTileCount)
        
        result = []
        for tile in tableTileMgr.getAllTilesForTing():
            if handTileArr[tile] > 0:
                newTiles = MTile.cloneTiles(tiles)
                newTiles[MHand.TYPE_HAND].remove(tile)
                resultNode,istingAll = cls.canWinAddOneTile(tilePatternChecker, tableTileMgr, leftTileArr, leftTileCount, newTiles, winRule, magicTiles, winSeatId)
                if len(resultNode) > 0:
                    winNode = {}
                    winNode['dropTile'] = tile
                    winNode['winNodes'] = resultNode
                    winNode['isHuAll'] = istingAll
                    result.append(winNode)
                
        return len(result) > 0, result
    
    @classmethod
    def canWinAddOneTile(cls, tilePatternChecker, tableTileMgr, leftTileArr, leftTileCount, tiles, winRule, magicTiles=[], winSeatId=0):
        result = []
        #for tile in range(leftTileCount):
        ishuAll = True
        for tile in tableTileMgr.getAllTilesForTing():
            newTile = MTile.cloneTiles(tiles)
            newTile[MHand.TYPE_HAND].append(tile)
            '''
            # 添加tile牌，如果tile牌总数大于4，则不用判断
            if newTile[MHand.TYPE_HAND].count(tile) > 4:
                continue
            '''
            # 测试听牌时，默认听牌状态
            winResult, winPattern = winRule.isHu(newTile, tile, True, MWinRule.WIN_BY_MYSELF, magicTiles, [], winSeatId)
            if winResult:
                winNode = {}
                winNode['winTile'] = tile
                winNode['winTileCount'] = leftTileArr[tile]
                # getVisibleTileCount 返回值是已经有几张了 最多为4张，一炮多响胡牌会算多
                visibleTileCount = tableTileMgr.getVisibleTilesCount(tile, True, winSeatId)
                winNode['winTileCountUserCanSee'] = 4 - visibleTileCount
                tilePatternChecker.initChecker(newTile, tableTileMgr)
                winNode['winFan'] = tilePatternChecker.calcFanPatternTing()
                winNode['pattern'] = winPattern
                ftlog.debug('MTing.canWinAddOneTile winTile:', tile
                            , ' winTileCount:', winNode['winTileCount']
                            , ' winPattern:', winPattern
                            , ' winNode:', winNode)
                result.append(winNode)
            else:
                ishuAll = False

        return result,ishuAll
    
    @classmethod
    def calcTingResult(cls, winNodes, seatId, tableTileMgr):
        # 在玩家丢弃牌以后，需要更新winTileCountUserCanSee字段
        ftlog.debug('MTing.calcTingResult winNodes:', winNodes, 'seatId:', seatId)
        tings = []
        for winNode in winNodes:
            ting = []
            ting.append(winNode['winTile'])
            ting.append(winNode['winFan'])
            ting.append(4 - tableTileMgr.getVisibleTilesCount(winNode['winTile'], True, seatId))
            tings.append(ting)
        return tings

    @classmethod
    def updateTingResult(cls, player, dropTile, tableTileMgr, volatileFlag):
        '''
        更新用户的听牌信息，根据player中的tingResult成员
        True 更新成功，需要通知前端
        False 更新失败，不用通知前端
        '''
        if player and not player.tingResult:
            return False
        for _result in player.tingResult:
            if dropTile == _result[0]:
                if volatileFlag:
                    _result[2] = 4 - tableTileMgr.getVisibleTilesCount(dropTile, True, player.curSeatId)
                else:
                    _result[2] = 0 if _result[2] - 1 < 0 else _result[2] - 1
                return True
        return False
        
def test1():
    tiles = [[24, 25, 26, 13, 13, 13, 14, 15, 16, 17, 18, 18, 18, 1], [], [], [], [], []]
    leftTiles = [1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 7, 8, 9]
    winRule = MWinRuleFactory.getWinRule(MPlayMode.XUEZHANDAODI)
    MTing.canTing(tiles, leftTiles, winRule, 6)
    
def testTingBefore():
    tiles = [[31, 31, 31, 32, 32, 33, 33, 34, 34, 35, 36, 37], [], [], [], [], []]
    leftTiles = [37, 36]
    winRule = MWinRuleFactory.getWinRule(MPlayMode.YANTAI)
    winRule.setTableConfig({"only_jiang_258": 0})
    canTing, tings = MTing.canTingBeforeAddTile(tiles, leftTiles, winRule)
    ftlog.debug('testTingBefore canTing:', canTing
                , ' tings:', tings)
    
if __name__ == "__main__":
    testTingBefore()
