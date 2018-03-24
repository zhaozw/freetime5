# -*- coding=utf-8 -*-
'''
Created on 2017年7月19日

@author: zqh
'''
from tuyoo5.core import tyglobal


def check_chargeMap(msg, result, name):
    chargeMap = {}
    if result.chargedRmbs > 0:
        chargeMap['rmb'] = result.chargedRmbs
    else:
        chargeMap['rmb'] = 0
    if result.chargedDiamonds > 0:
        chargeMap['diamond'] = result.chargedDiamonds
    else:
        chargeMap['diamond'] = 0
    return chargeMap, None


def check_consumeMap(msg, result, name):
    consumeMap = {}
    if result.consumeCoin > 0:
        consumeMap['coin'] = result.consumeCoin
    return consumeMap, None


def check_realGameId(msg, result, name):
    val = msg.getParamInt(name, tyglobal.gameId())
    return val, None


def check_appId(msg, result, name):
    val = msg.getParamInt(name, 0)
    if val <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_prodOrderId(msg, result, name):
    val = msg.getParamStr(name, '')
    if val:
        return val, None
    return None, 'the param %s error' % (name)


def check_platformOrder(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_prodId(msg, result, name):
    val = msg.getParamStr(name, '')
    if val:
        return val, None
    return None, 'the param %s error' % (name)


def check_prodCount(msg, result, name):
    val = msg.getParamInt(name, '')
    if val <= 0:
        return None, 'the param %s error' % (name)
    return val, None


def check_is_monthly(msg, result, name):
    val = msg.getParamInt(name, 0)
    return val, None


def check_chargeType(msg, result, name):
    val = msg.getParamStr(name, '')
    return val, None


def check_chargedRmbs(msg, result, name):
    val = msg.getParamFloat(name, 0)
    return val, None


def check_chargedDiamonds(msg, result, name):
    val = msg.getParamInt(name, 0)
    return val, None


def check_consumeCoin(msg, result, name):
    val = msg.getParamInt(name, 0)
    return val, None
