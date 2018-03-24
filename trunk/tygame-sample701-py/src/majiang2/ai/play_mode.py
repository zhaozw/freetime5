# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''

class MPlayMode(object):
    # 最简单的麻将玩法
    SIMPLE = 'simple'
    # 1) 四川玩法，血战到底
    XUEZHANDAODI = 'xuezhan'
    # 四川麻将，血流成河
    XUELIUCHENGHE = 'xueliu'
    # 2) 国标玩法
    GUOBIAO = 'guobiao'
    # 3) 哈尔滨玩法
    HAERBIN = 'harbin'
    # 7) 鸡西麻将
    JIXI = "jixi"
    # 8) 牡丹江麻将
    MUDANJIANG = "mudanjiang"
    # 9) 青岛平度打八张麻将
    PINGDU = "pingdu"
    # 10) 青岛平度258将麻将
    PINGDU258 = "pingdu258"
    # 11) 吉林白城麻将
    BAICHENG = "baicheng"
    # 12) 威海麻将
    WEIHAI = "weihai"
    # 14) 安微芜湖
    WUHU = "wuhu"
    # 15）安徽怀宁麻将
    HUAINING = "huaining"
    # 16）安徽合肥巢湖八支带路
    CHAOHU = "chaohu"
    # 17) 山东烟台
    YANTAI = "yantai"
    # 18) 山东济南
    JINAN = "jinan"
    # 19) 安徽马鞍山市和县
    HEXIAN = "hexian"
    # 20) 安徽芜湖无为
    WUWEI = "wuwei"
    # 21) 盘锦
    PANJIN = "panjin"
    # 22) 安徽芜湖三县
    SANXIAN = "sanxian"
    # 23) 丹东
    DANDONG = "dandong"
    # 24) 安徽马鞍山含山
    HANSHAN = "hanshan"
    # 25）广东鸡平胡
    JIPINGHU = "jipinghu"

    def __init__(self):
        super(MPlayMode, self).__init__()
