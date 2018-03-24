# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
from freetime5.util import ftlog
from majiang2.poker2.entity import hallrpcutil
from majiang2.poker2.entity.game.tables.table_player import TYPlayer
from tuyoo5.game import tybireport

class MTableExpression(object):
    
    def __init__(self):
        super(MTableExpression, self).__init__()
        
    @classmethod
    def get_interactive_expression_config(self, base_chip, chat_chip):
        """
        获取互动表情的配置
        同一场次不同表情花费数额是相同的
        若chat_chip为-1，则以base_chip计算
        """
        ftlog.debug('MTableExpression get_interactive_expression_config base_chip:', base_chip, 'chat_chip:', chat_chip)
        chip_limit = int(base_chip * 1.1)
        chat_chip = base_chip if chat_chip == -1 else chat_chip
        cost = int(chat_chip)
        ret = {
                'chip_limit' : chip_limit,
                'cost': cost,
                'charm': cost,
                'tb_charm': cost
            }
        ftlog.debug('MTableExpression get_interactive_expression_config ret:', ret)
        return ret
#===============================================================================
#         return ret
#         chip_limit = int(base_chip * 1.1)
#         cost_1 = int(base_chip * 0.5)
#         cost_2 = int(base_chip)
#         ret = {
#             # 炸弹
#             '0': {'chip_limit': chip_limit
#                 , 'cost': cost_2
#                 , 'charm': int(cost_2/10)
#                 , 'ta_charm': -int(cost_2/10)
#             },
#             # 钻戒
#             '1': {'chip_limit': chip_limit
#                 , 'cost': cost_2
#                 , 'charm': int(cost_2/5)
#                 , 'ta_charm': int(cost_2/5)
#             },
#             # 鸡蛋
#             '2': {'chip_limit': chip_limit
#                 , 'cost': cost_1
#                 , 'charm': int(cost_1/10)
#                 , 'ta_charm': -int(cost_1/10)
#             },
#             # 鲜花
#             '3': {'chip_limit': chip_limit
#                 , 'cost': cost_1
#                 , 'charm': int(cost_1/5)
#                 , 'ta_charm': int(cost_1/5)
#             },
#            # 板砖
#             '4': {'chip_limit': 0
#                 , 'cost': 0
#                 , 'charm': 0
#                 , 'ta_charm': 0
#             },
#         }
# 
#         return ret
#===============================================================================
    
    @classmethod
    def process_interactive_expression(cls, userId, gameId, seatId, chat_msg, target_player_uid, base_chip, chat_chip):
        """
        处理消费金币的表情
        """
        config = cls.get_interactive_expression_config(base_chip, chat_chip)
        emoId = str(chat_msg.get('emoId', -1))
        if emoId == -1:
            ftlog.warn('MTableExpression chat msg illegal', chat_msg, config)
            return False
        
        info = config
        # 底分限制
        chip = hallrpcutil.getChip(userId)
        ftlog.debug('MTableExpression info:', info, 'chip:', chip, caller=cls)
        if chip >= info['chip_limit'] + info['cost'] \
                and TYPlayer.isHuman(userId):
            trueDelta, _ = hallrpcutil.incrChip(userId
                    , gameId
                    , -info['cost']
                    , 0
                    , "EMOTICON_CONSUME"
                    , chat_msg['emoId'])
            
            if trueDelta != -info['cost']:   # 失败
                ftlog.warn('MTableExpression coin not enougth: ', chip, info['chip_limit'], info['cost'])
                return False
            # 金币发生变化，通知前端
            hallrpcutil.sendDataChangeNotify(userId, gameId, 'udata')
            tybireport.gcoin('out.interactive_expression', gameId, info['cost'])
        else:
            ftlog.warn('MTableExpression insufficient', chip, info['chip_limit'], info['cost'])
            
        return True
