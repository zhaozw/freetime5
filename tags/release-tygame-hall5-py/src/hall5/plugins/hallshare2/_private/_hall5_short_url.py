# -*- coding:utf-8 -*-
'''
Created on 2017年11月28日

@author: zhaojiangang
'''

from freetime5.twisted import fthttp
from freetime5.util import ftstr
from freetime5.util import ftlog


_DEBUG, debug = ftlog.getDebugControl(__name__)

_SHORT_IP = 'shorturl.ywdier.com'


def longUrlToShort(longUrl):
    query = ftstr.toHttpStr({
        'longUrl': longUrl
    })
    url = 'http://%s/api/shorturl/make?%s' % (_SHORT_IP, query)
    _code, page = fthttp.queryHttp('GET', url, None, None, 5)
    datas = ftstr.loads(page, ignoreException=True, execptionValue={})
    status, short_url = datas.get('ok'), datas.get('url')
    if status != 1:
        ftlog.error('longUrlToShort', url, _code, page)
        return longUrl
    return short_url

