# -*- coding=utf-8 -*-
'''
Created on 2017年7月10日

@author: zqh
'''
# import random
# 
# from freetime5.twisted import ftcore, fthttp
# from freetime5.util import ftstr, ftlog
# from tuyoo5.core import tyglobal
# 
# 
# def _fack_test_cover_params(mi):
#     mi._add_('displayName', 'HALL51测试，请勿操作！%s' % (mi.displayName))
#     if mi.type == 0:
#         mi._add_('count', 1)  # 充值卡，换位1元
#     if mi.type == 3:
#         mi._add_('count', 10)  # 京东卡
#     if mi.type == 6:
#         mi._add_('jd_product_id', '1798191')  # 京东实物
# 
# 
# def _fack_recover_ip(code, errmsg):
#     if errmsg.find('非法IP') >= 0:
#         return 1
#     return code
# 
# 
# def _fack_test_cover_result(userId, mi, exchangeId, errMsg):
#     if exchangeId and mi.type != 99:
#         # 10 秒钟后自动审核
#         ftcore.runOnceDelay(120, _fack_gdss_callback_audit, userId, exchangeId)
# 
# 
# def _fack_gdss_callback_audit(userId, exchangeId):
#     extOrederId = ftstr.toHttpStr(ftstr.uuid())
#     result = random.choice([1, 2, 3])
#     params = 'userId=%s&exchangeId=%s&result=%s&extOrederId=%s' % (userId, exchangeId, result, extOrederId)
#     url = tyglobal.httpGame() + '/api/hall5/exchange/auditCallback?' + params
#     ftlog.info('_fack_gdss_callback_audit->', url)
#     fthttp.queryHttp('GET', url, None, None, 5, None, None)
#     if result == 3:
#         # 10 秒钟后自动发货
#         ftcore.runOnceDelay(120, _fack_gdss_callback_shipping, userId, exchangeId, extOrederId)
# 
# 
# def _fack_gdss_callback_shipping(userId, exchangeId, extOrederId):
#     result = random.choice([0, 4, 5])
#     params = 'userId=%s&exchangeId=%s&result=%s&extOrederId=%s' % (userId, exchangeId, result, extOrederId)
#     url = tyglobal.httpGame() + '/api/hall5/exchange/shippingCallback?' + params
#     ftlog.info('_fack_gdss_callback_shipping->', url)
#     fthttp.queryHttp('GET', url, None, None, 5, None, None)
