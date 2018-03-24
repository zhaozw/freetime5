'''
Created on 2018年2月7日

@author: lixi
'''
from tuyoo5.core.typlugin import hallRpcOne
from tuyoo5.core import tyrpcsdk
from tuyoo5.core.tyrpchall import UserKeys


_UserBaseAttrs = ','.join([UserKeys.ATT_NAME, UserKeys.ATT_PURL, UserKeys.ATT_SEX, UserKeys.ATT_ADDRESS, UserKeys.ATT_CITY_CODE])


def getUserSexInfo(userId):
    datas = tyrpcsdk.getUserDatas(userId, _UserBaseAttrs)
    sex = datas.get(UserKeys.ATT_SEX, 0)
    return sex

def getUserBaseInfo(userId):
    datas = tyrpcsdk.getUserDatas(userId, _UserBaseAttrs)
    name = datas.get(UserKeys.ATT_NAME, 'error name')
    purl = datas.get(UserKeys.ATT_PURL, '')
    sex = datas.get(UserKeys.ATT_SEX, 0)
    address = datas.get(UserKeys.ATT_ADDRESS, '')
    citycode = datas.get(UserKeys.ATT_CITY_CODE, '')
    return name, purl, sex, address, citycode