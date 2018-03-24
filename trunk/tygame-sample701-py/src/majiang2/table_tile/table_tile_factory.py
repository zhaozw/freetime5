# -*- coding=utf-8
'''
Created on 2016年9月23日
庄家规则
@author: zhaol
'''
from majiang2.ai.play_mode import MPlayMode
from majiang2.table_tile.table_tile_haerbin import MTableTileHaerbin
from majiang2.table_tile.table_tile_mudanjiang import MTableTileMudanjiang
from majiang2.table_tile.table_tile_jixi import MTableTileJixi
from majiang2.table.run_mode import MRunMode
from majiang2.tile.tile import MTile
from majiang2.table_tile.table_tile import MTableTile
from majiang2.table_tile.table_tile_pingdu import MTableTilePingdu
from majiang2.table_tile.table_tile_baicheng import MTableTileBaicheng
from majiang2.table_tile.table_tile_wuhu import MTableTileWuHu
from majiang2.table_tile.table_tile_huaining import MTableTileHuaiNing
from majiang2.table_tile.table_tile_weihai import MTableTileWeihai
from majiang2.table_tile.table_tile_jinan import MTableTileJinan
from majiang2.table_tile.table_tile_chaohu import MTableTileChaoHu
from majiang2.table_tile.table_tile_hexian import MTableTileHeXian
from majiang2.table_tile.table_tile_wuwei import MTableTileWuWei
from majiang2.table_tile.table_tile_panjin import MTableTilePanjin
from majiang2.table_tile.table_tile_sanxian import MTableTileSanXian
from majiang2.table_tile.table_tile_dandong import MTableTileDandong
from majiang2.table_tile.table_tile_hanshan import MTableTileHanShan
from majiang2.table_tile.table_tile_yantai import MTableTileYantai
from majiang2.table_tile.table_tile_sichuan import MTableTileSiChuan
from majiang2.table_tile.table_tile_jipinghu import MTableTileJiPingHu

class MTableTileFactory(object):
    def __init__(self):
        super(MTableTileFactory, self).__init__()
    
    @classmethod
    def getTableTileMgr(cls, playerCount, playMode, runMode):
        """牌桌手牌管理器获取工厂
        输入参数：
            playMode - 玩法      
        返回值：
            对应玩法手牌管理器
        """
        if playMode == MPlayMode.HAERBIN:
            return MTableTileHaerbin(playerCount, playMode, runMode)
        if playMode == MPlayMode.MUDANJIANG:
            return MTableTileMudanjiang(playerCount, playMode, runMode)
        elif playMode == MPlayMode.JIXI:
            return MTableTileJixi(playerCount, playMode, runMode)     
        elif playMode == MPlayMode.PINGDU:
            return MTableTilePingdu(playerCount, playMode, runMode)
        elif playMode == MPlayMode.PINGDU258:
            return MTableTilePingdu(playerCount, playMode, runMode)
        elif playMode == MPlayMode.WEIHAI:
            return MTableTileWeihai(playerCount, playMode, runMode)
        elif playMode == MPlayMode.JINAN:
            return MTableTileJinan(playerCount, playMode, runMode)
        elif playMode == MPlayMode.BAICHENG:
            return MTableTileBaicheng(playerCount, playMode, runMode)
        elif playMode == MPlayMode.PANJIN:
            return MTableTilePanjin(playerCount, playMode, runMode)
        elif playMode == MPlayMode.DANDONG:
            return MTableTileDandong(playerCount, playMode, runMode)
        elif playMode == MPlayMode.WUHU :
            return MTableTileWuHu(playerCount, playMode, runMode)
        elif playMode == MPlayMode.HUAINING:
            return MTableTileHuaiNing(playerCount, playMode, runMode)
        elif playMode == MPlayMode.YANTAI:
            return MTableTileYantai(playerCount, playMode, runMode)
        elif playMode == MPlayMode.CHAOHU:
            return MTableTileChaoHu(playerCount, playMode, runMode)
        elif playMode == MPlayMode.HEXIAN:
            return MTableTileHeXian(playerCount, playMode, runMode)
        elif playMode == MPlayMode.WUWEI:
            return MTableTileWuWei(playerCount, playMode, runMode)
        elif playMode == MPlayMode.SANXIAN:
            return MTableTileSanXian(playerCount, playMode, runMode)
        elif playMode == MPlayMode.HANSHAN:
            return MTableTileHanShan(playerCount, playMode, runMode)
        elif playMode == MPlayMode.XUELIUCHENGHE \
                or playMode == MPlayMode.XUEZHANDAODI:
            return MTableTileSiChuan(playerCount, playMode, runMode)
        elif playMode == MPlayMode.JIPINGHU:
            return MTableTileJiPingHu(playerCount, playMode, runMode)

        return MTableTile(playerCount, playMode, runMode)

if __name__ == "__main__":
    tableTileMgr = MTableTileFactory.getTableTileMgr(4, MPlayMode.HAERBIN, MRunMode.CONSOLE)
    tableTileMgr.tileTestMgr.setHandTiles([[5, 5, 5, 5], [6, 6, 6, 6], [7, 7, 7, 7], [8, 8, 8, 8]])
    tableTileMgr.tileTestMgr.setTiles([9, 9, 9, 9])
    tableTileMgr.shuffle(0, 13)
    tiles = tableTileMgr.tiles
    print tiles
    
    tileArr = MTile.changeTilesToValueArr(tiles)
    print tileArr
