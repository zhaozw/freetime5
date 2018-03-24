# coding:utf-8
from freetime5.util import ftlog
from tuyoo5.core.typlugin import pluginCross


class CreateTableData(object):
    """创建牌桌相关数据管理类 模块中redis script初始化在GT进程
    """
    @classmethod
    def initialize(cls, serverId):
        """初始化，加载lua脚本,清除serverId对应的数据
        """
        ftlog.debug('CreateTableData.initialize serverId:', serverId)
        pluginCross.mj2dao.clearCreateTableData(serverId)

    @classmethod
    def addCreateTableNo(cls, tableId, roomId, serverId, tableNoKey, initParams):
        """添加自建桌验证码数据 只在GT服调用
        """
        return pluginCross.mj2dao.addCreateTableNo(tableId, roomId, serverId, tableNoKey, initParams)

    @classmethod
    def removeCreateTableNo(cls, serverId, tableNoKey):
        """删除redis中自建桌验证码数据 只在GT服调用
        """
        return pluginCross.mj2dao.removeCreateTableNo(serverId, tableNoKey)

    @classmethod
    def getAllCreateTableNoList(cls):
        """获取所有的自建桌验证码列表
        """
        return pluginCross.mj2dao.getAllCreateTableNoList()

    @classmethod
    def getTableIdByCreateTableNo(cls, createTableNo):
        """通过自建桌验证码查找返回tableId
        """
        return pluginCross.mj2dao.getTableIdByCreateTableNo(createTableNo)

    @classmethod
    def getTableParamsByCreateTableNo(cls, createTableNo):
        """通过自建桌号查找返回建桌参数
        """
        return pluginCross.mj2dao.getTableParamsByCreateTableNo(createTableNo)

    @classmethod
    def getAllCreatedTableIdList(cls):
        """返回所有已创建的tableId列表
        """
        return pluginCross.mj2dao.getAllCreatedTableIdList()
