# -*- coding: utf-8 -*-
"""
Created on 2018年02月03日17:08:55

@author: yzx
"""
import sys

from chat.entity.msg_validation_if import ChatMsgValidation
from freetime5.util import ftlog

_DEBUG = 1

if _DEBUG:
    def debug(*argl, **argd):
        ftlog.debug(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass


def getResourcePath(fileName):
    '''
    取得当前文件下某一个资源的绝对路径
    '''
    import os
    cpath = os.path.abspath(__file__)
    cpath = os.path.dirname(cpath)
    fpath = cpath + os.path.sep + fileName
    return fpath


class DirtyWordFilter(ChatMsgValidation):
    """
    脏话过滤器.
    """

    def __init__(self):
        super(DirtyWordFilter, self).__init__()
        self.__dirty = []
        self.init_dirty_word()

    def init_dirty_word(self):
        filename = getResourcePath('./dirtyword.txt')
        with open(filename, 'r') as f:
            for line in f:
                if len(line) == 0 or line == '\n':
                    continue
                word = line.strip('\n')
                self.__dirty.append(word)
        debug("init dirty word!", self.__dirty)

    def do_verify(self, msg):
        # TODO 脏话过滤后要返回
        clean_content = msg.getParam('content')
        debug("clean_content:", clean_content)
        for word in self.__dirty:
            clean_content = clean_content.replace(word, '呵呵')
        msg.setParam('content', clean_content)


if __name__ == '__main__':
    reload(sys)  # reload 才能调用 setdefaultencoding 方法
    sys.setdefaultencoding('utf-8')  # 设置 'utf-8'
    test = DirtyWordFilter()
    s = u'中国'
    print s
    s_gb = s.encode('gb2312')
    print s_gb
    s_utf8 = s.encode('UTF-8')
    print s_utf8
