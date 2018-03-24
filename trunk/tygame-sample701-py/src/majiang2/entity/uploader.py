# -*- coding:utf-8 -*-
'''
Created on 2016年10月19日

@author: zhaojiangang
'''
import os

from freetime5.twisted import fthttp
from freetime5.util import ftlog
from freetime5.util.fthttp import MultipartForm


def uploadVideo(uploadUrl, token, uploadPath, videoData):
    try:
        filename = os.path.basename(uploadPath)
        formItems = []
        formItems.append(MultipartForm.FormItemData('token', token))
        formItems.append(MultipartForm.FormItemData('key', uploadPath))
        formItems.append(MultipartForm.FormItemFile('file', videoData, filename))
        #formItems.append(FormItemFile('fileBinaryData', videoData, filename))

        headers, uploadData = MultipartForm.encodeFormItems(formItems)
        retrydata = {'max': 3}
        code, res = fthttp.queryHttp(method='POST',
                                     url=uploadUrl,
                                     header=headers,
                                     body=uploadData,
                                     connect_timeout=5,
                                     retrydata=retrydata)
        if ftlog.is_debug():
            ftlog.debug('uploader.uploadVideo uploadUrl=', uploadUrl,
                        'uploadPath=', uploadPath,
                        'token=', token,
                        'ret=', (code, res))

        if code == 200 or code == 406:  # 406 文件已经存在
            return 0, '上传成功'

        ftlog.info('uploader.uploadVideo Res uploadUrl=', uploadUrl,
                   'uploadPath=', uploadPath,
                   'token=', token,
                   'ret=', code)
        return -1, '上传失败'
    except:
        return -2, '上传失败'
