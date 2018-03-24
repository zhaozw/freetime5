#! -*- coding:utf-8 -*-
# Author:   qianyong
# Created:  2017/3/10

# 怀宁麻将中使用的牌常量

from majiang2.tile.tile import MTile

# 东风，中发白是花
FLOWERS = (MTile.TILE_DONG_FENG, MTile.TILE_HONG_ZHONG, MTile.TILE_FA_CAI, MTile.TILE_BAI_BAN)

# 南西北
NAN_XI_BEI = (MTile.TILE_NAN_FENG, MTile.TILE_XI_FENG, MTile.TILE_BEI_FENG)

# 风牌
FENGS = (MTile.TILE_DONG_FENG, MTile.TILE_NAN_FENG, MTile.TILE_XI_FENG, MTile.TILE_BEI_FENG,
         MTile.TILE_HONG_ZHONG, MTile.TILE_FA_CAI, MTile.TILE_BAI_BAN)

# 非风牌的orders
COLORS_EXCLUDE_FENG = (MTile.TILE_WAN, MTile.TILE_TONG, MTile.TILE_TIAO)

# 花牌在手牌中的索引, 东，中，发，白
FLOWERS_HANDS_INDEXES = (0, 4, 5, 6)
