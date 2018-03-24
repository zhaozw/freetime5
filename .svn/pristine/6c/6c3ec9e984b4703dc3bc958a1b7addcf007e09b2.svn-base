# -*- coding=utf-8
'''
Created on 2016年11月18日

@author: zqh
'''

from freetime5.util import ftlog
from tuyoo5.plugins.todotask import _todotask
from tuyoo5.plugins.todotask import _todotaskunit


_DEBUG = 0

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


class TodoTaskOrderShow(_todotask.TodoTask):
    '''
    显示购买弹窗 TodoTask模板
    '''

    def __init__(self, desc, note, price, detail, count=0, itemId=''):
        super(TodoTaskOrderShow, self).__init__('pop_order_info')
        self.setParam('allow_close', True)
        self.setParam('des', desc)
        self.setParam('note', note)
        self.setParam('price', price)
        self.setParam('detail', detail)
        self.setParam('count', count)
        self.setParam('itemId', itemId)

    @classmethod
    def makeByProduct(cls, desc, note, product, buyType='', count=0, itemId=''):
        params = _todotaskunit.TodoTaskPayOrder.getParamsByProduct(product)
        ret = TodoTaskOrderShow(desc, note, params['price'], params['tip'], count, itemId)
        payOrder = _todotaskunit.TodoTaskPayOrder().updateParams(params)
        if buyType:
            payOrder.setParam('buy_type', buyType)
        ret.setSubCmd(payOrder)
        return ret


class TodoTaskQuickStart(_todotask.TodoTask):
    '''
    发送快速开始 TodoTask模板
    '''

    def __init__(self, gameId=0, roomId=0, tableId=0, seatId=0):
        super(TodoTaskQuickStart, self).__init__('quick_start')
        # 老的参数，暂时保留，参数应该使用标准的驼峰命名，使用全小写的命名，前端原样儿转发，快开参数解析会失败。
        self.setParam('gameid', gameId)
        self.setParam('roomid', roomId)
        self.setParam('tableid', tableId)
        self.setParam('seatid', seatId)
        # 标准驼峰参数
        self.setParam('gameId', gameId)
        self.setParam('roomId', roomId)
        self.setParam('tableId', tableId)
        self.setParam('seatId', seatId)


class TodoTaskJumpToSecondHall(_todotask.TodoTask):
    '''
    通知前端返回二级子大厅
    '''

    def __init__(self, gameId, playMode):
        super(TodoTaskJumpToSecondHall, self).__init__('jump_to_second_hall')
        self.setParam('gameId', gameId)
        self.setParam('playMode', playMode)


class TodoTaskJumpToRoomList(_todotask.TodoTask):
    '''
    通知前端离开牌桌
    '''

    def __init__(self, gameId, playMode):
        super(TodoTaskJumpToRoomList, self).__init__('jump_to_room_list')
        self.setParam('gameId', gameId)
        self.setParam('playMode', playMode)


class TodoTaskPopTip(_todotask.TodoTask):
    def __init__(self, text=''):
        super(TodoTaskPopTip, self).__init__('pop_tip')
        self.setParam('text', text)
