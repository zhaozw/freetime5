# -*- coding: utf-8 -*-
'''
Created on 2017年7月19日

@author: zqh
'''


def check_authorCode(msg, result, name):
    authorCode = msg.getParamStr(name)
    if len(authorCode) <= 0:
        return None, 'the param %s is empty' % (name)
    return authorCode, None


def check_sex(msg, result, name):
    sex = msg.getParamInt(name, -1)
    if sex not in (0, 1):
        return None, 'the param %s is error' % (name)
    return sex, None


def check_purl(msg, result, name):
    purl = msg.getParamStr(name)
    return purl, None


def check_realName(msg, result, name):
    realName = msg.getParamStr(name)
    if len(realName) <= 0:
        return None, 'the param %s is empty' % (name)
    return realName, None

def check_idCardNum(msg, result, name):
    idCardNum = msg.getParamStr(name)
    if len(idCardNum) <= 0:
        return None, 'the param %s is empty' % (name)
    return idCardNum, None