# -*- coding=utf-8
'''
Created on 2016年9月23日
杠牌规则
@author: zhaol
'''
from majiang2.player.hand.hand import MHand
from majiang2.tile.tile import MTile
import copy
from majiang2.player.player import MPlayerTileGang
from freetime5.util import ftlog
from majiang2.table_state.state import MTableState
from majiang2.gang_rule.gang_rule import MGangRule

class MGangRulePanJin(MGangRule):
    """杠牌判断"""
    
    def __init__(self):
        super(MGangRulePanJin, self).__init__()
        
    def hasGang(self, tiles, curTile, state, extendInfo={}):
        """判断杠牌"""
        
        magicTiles = self.tableTileMgr.getMagicTiles()
        for magicTile in magicTiles:
            if magicTile==curTile:
                return []
                
        handTiles = tiles[MHand.TYPE_HAND]
        tileArr = MTile.changeTilesToValueArr(handTiles)
        magics = []
        if self.tableTileMgr.canUseMagicTile(MTableState.TABLE_STATE_GANG):           
            magics = self.tableTileMgr.getMagicTiles(False)
        tileArr, magicTiles = self.tableTileMgr.exculeMagicTiles(tileArr, magics)
        magicCount = len(magicTiles)
        magicGangMaxCount = self.tableTileMgr.magicGangMaxCount
        if magicGangMaxCount > 4 or magicGangMaxCount < 0:
            magicGangMaxCount = 4
 
        gangs = []
        if self.tableTileMgr.getTilesLeftCount() == 0 and (not self.tableTileMgr.canGangLastTile()):
            # 部分玩法牌桌牌抓完后，不能杠牌，因为杠完无法再摸牌了
            return gangs
 
        # 带有癞子的杠
        for tile in range(MTile.TILE_MAX_VALUE):
            if not self.tableTileMgr.canGangThisTile(tile):
                continue
            if tileArr[tile] == 4:
                pattern = [tile, tile, tile, tile]
                if (curTile in pattern) and (state & MTableState.TABLE_STATE_DROP):
                    gangs.append({"pattern":pattern, "style": MPlayerTileGang.MING_GANG, "tile":tile})
                else:
                    gangs.append({"pattern":pattern, "style": MPlayerTileGang.AN_GANG, "tile":tile})
            if tileArr[tile] >= 3 and magicCount >= 1:
                pattern = [tile, tile, tile, magicTiles[0]]
                pattern.sort()
                if (curTile in pattern) and (curTile not in magicTiles) and (state & MTableState.TABLE_STATE_DROP) and magicGangMaxCount >= 1:
                    gangs.append({"pattern":pattern, "style": MPlayerTileGang.MING_GANG, "tile":tile})
                else:
                    gangs.append({"pattern":pattern, "style": MPlayerTileGang.AN_GANG, "tile":tile})
            if tileArr[tile] >= 2 and magicCount >= 2:
                pattern = [tile, tile, magicTiles[0], magicTiles[1]]
                pattern.sort()
                if (curTile in pattern) and (curTile not in magicTiles) and (state & MTableState.TABLE_STATE_DROP) and magicGangMaxCount >= 2:
                    gangs.append({"pattern":pattern, "style": MPlayerTileGang.MING_GANG, "tile":tile})
                else:
                    gangs.append({"pattern":pattern, "style": MPlayerTileGang.AN_GANG, "tile":tile})
            if tileArr[tile] >= 1 and magicCount >= 3:
                pattern = [tile, magicTiles[0], magicTiles[1], magicTiles[2]]
                pattern.sort()
                if (curTile in pattern) and (curTile not in magicTiles) and (state & MTableState.TABLE_STATE_DROP) and magicGangMaxCount >= 3:
                    gangs.append({"pattern":pattern, "style": MPlayerTileGang.MING_GANG, "tile":tile})
                else:
                    gangs.append({"pattern":pattern, "style": MPlayerTileGang.AN_GANG, "tile":tile})
        
        # 赖子作为普通牌来杠,暂时不处理多类赖子的情况
        if magicCount >= 4 and len(magics) == 1:
            pattern = [magicTiles[0], magicTiles[1], magicTiles[2], magicTiles[3]]
            pattern.sort()
            if (curTile in pattern) and (state & MTableState.TABLE_STATE_DROP):
                gangs.append({"pattern":pattern, "style": MPlayerTileGang.MING_GANG, "tile":curTile})
            else:
                gangs.append({"pattern":pattern, "style": MPlayerTileGang.AN_GANG, "tile":magicTiles[0]})
                    
        # 补杠
        if not (state & MTableState.TABLE_STATE_DROP):
            for pengPattern in tiles[MHand.TYPE_PENG]:
                    for tile in pengPattern:
                        if not self.tableTileMgr.canGangThisTile(tile):
                            continue
                        # 可补杠的情况下，只要手上还有碰过的牌，就要提示杠牌
                        if tile not in magicTiles  \
                                and (tile in handTiles or tile == curTile):
                            gangPattern = copy.deepcopy(pengPattern)
                            gangPattern.append(tile)
                            gangs.append({"pattern":gangPattern, "style": MPlayerTileGang.MING_GANG, "tile":tile})
                            break
            # 用赖子补杠,目前只处理一个赖子补杠
            for pengPattern in tiles[MHand.TYPE_PENG]:
                ftlog.debug('MGangRule.hasGang:pengPattern', tiles[MHand.TYPE_PENG])
                if magicCount >= 1:
                    # 有赖子的杠,注意三个赖子碰补杠也在这里处理
                    gangPattern2 = copy.deepcopy(pengPattern)
                    tile2 = magicTiles[0]
                    gangPattern2.append(tile2) 
                    gangs.append({"pattern":gangPattern2, "style": MPlayerTileGang.MING_GANG, "tile":tile2})

        ftlog.debug('MGangRule.hasGang:', gangs)
        return gangs

    def hasChaoTianGang(self,tiles,tile):
        gang={}
        if tiles[MHand.TYPE_HAND].count(tile)==3:
            gang["tile"]=tile
            gang["pattern"]=[tile,tile,tile,tile]
        return gang

    def canGangThisTile(self, tile):
        """能否杠这张牌"""
        return True

if __name__ == "__main__":
    #testYunnan()
    pass