# -*- coding=utf-8
'''
Created on 2016年9月23日

@author: zhaol
'''
"""
牌桌暂停的处理器
有暂停任务是，牌桌状态为TABLE_STATE_PAUSE
无暂停任务时，牌桌状态为TABLE_STATE_NEXT

本模块维护一个延时任务队列
[
    {
        "time": 2,
        "userId": 10001,
        "msg": {}
    },
    ...
]

参数说明
time - 延时时间
msgs - 延时时间到了之后发送的消息

每次状态处理器初始化时，添加所有的延时消息
所有的延时消息处理完毕，状态重置

"""
from freetime5.util import ftlog
from majiang2.table_state.state import MTableState
from majiang2.table_state_processor.processor import MProcessor


class MPauseProcessor(MProcessor):
    def __init__(self, tableConfig):
        super(MPauseProcessor, self).__init__(tableConfig)
        self.__state = MTableState.TABLE_STATE_NEXT
        self.__tasks = []
        self.__events = []
        
    def reset(self):
        """重置数据"""
        self.__state = MTableState.TABLE_STATE_NEXT
        self.__tasks = []
        self.__events = []
        
    @property
    def state(self):
        """获取本轮出牌状态"""
        return self.__state
    
    def getState(self):
        if len(self.tasks) > 0:
            return MTableState.TABLE_STATE_PAUSE
        if len(self.events) > 0:
            return MTableState.TABLE_STATE_PAUSE
        
        return MTableState.TABLE_STATE_NEXT
    
    @property
    def tasks(self):
        return self.__tasks
    
    @property
    def events(self):
        return self.__events
    
    def addDelayTask(self, time, userId, msg, msgProcessor):
        '''
        添加延时任务
        参数数目
        time - 延时时间
        userId - 待发送消息的用户ID
        msg - 待延时发送的消息
        msgProcessor - 消息处理器

        '''
        task = {}
        task['time'] = time
        task['userId'] = userId
        task['msg'] = msg
        self.tasks.append(task)
        self.setMsgProcessor(msgProcessor)
        
    def addPauseEvent(self, time, eventId=None, data=None):
        """
        添加暂停事件
        """
        ftlog.debug('addPauseEvent, time:', time
                    , ' eventId:', eventId)
        event = {}
        event['time'] = time
        event['id'] = eventId
        event['data'] = data
        self.events.append(event)
        
    def updateTimeOut(self, deta):
        """
        更新超时
        """
        for task in self.tasks:
            task['time'] += deta
            if task['time'] <= 0 and task['msg']:
                ftlog.debug('MPauseProcessor.updateTimeOut process task:', task)
                self.msgProcessor.send_message(task['msg'], task['userId'])
                # 在发送完消息后，在保存到最近消息
                self.msgProcessor.addMsgRecord(task['msg'], task['userId'])
                
        # 重新刷新整理任务列表
        if len(self.tasks) > 0:
            self.__tasks = filter(lambda x:x['time'] > 0, self.__tasks)
            ftlog.debug('MPauseProcessor.updateTimeOut left tasks:', self.tasks)
    
    def updatePauseEvent(self, deta):
        '''
        更新超时
        '''
        ids = []
        for event in self.events:
            event['time'] += deta
            if (event['time'] <= 0) and (event['id'] != None):
                ids.append(event)
                
        # 更新延迟事件
        if len(self.events) > 0:
            self.__events = filter(lambda x:x['time'] > 0, self.__events)
            ftlog.debug('MPauseProcessor.updateTimeOut left events:', self.events)
            
        return ids
