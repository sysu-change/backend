import pymysql
from DBUtils.PooledDB import PooledDB
import sys
from functools import wraps
import io
import sys
from flask import current_app, session

from api import *
from .utils import *


# 创建问卷
# used in /module/user/create_questionnaire
def create_questionnaire_model(account):
    sid = account.get('sid', None)
    title = account.get('title', None)
    description = account.get('description', None)
    edit_status = account.get('edit_status', None)
    reward = account.get('reward', None)
    quantity = account.get('quantity', None)
    pub_time = account.get('pub_time', None)
    content = account.get('content', None)
    msg = ""
    if sid == None or title == None or description== None or edit_status == None or pub_time==None\
        or reward == None or quantity == None or content== None or (not isinstance(edit_status, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not session['sid'] == sid:
        msg += "publisher_must_be_your_own"
        return 400, msg
    if not isinstance(quantity, int):
        msg += "quantity_must_be_int"
        return 400, msg
    if not isinstance(reward , float):
        msg += "quantity_must_be_float"
        return 400, msg
    if edit_status == 1:
        cost = reward * quantity
        if cost > session['balance']:
            msg += "Insufficient_account_balance"
            return 400, msg
    sql = """INSERT INTO questiontable(sid, title, description, edit_status, quantity, reward, pub_time, content)
                                                VALUES ("%s", "%s", "%s", %d ,%d, %f,"%s","%s");""" % (
        sid, title, description, edit_status, quantity, reward, pub_time, content)
    tools.modifyOpt(sql)
    if edit_status == 1:
        reduce_balance_by_sid(session['sid'], cost)
        session['balance'] = session['balance'] - cost
    msg += "successful"
    return 200, msg


# 编辑问卷
# used in /module/user/edit_questionnaire
def edit_questionnaire_model(account):
    qid = account.get('qid', None)
    sid = account.get('sid', None)
    title = account.get('title', None)
    description = account.get('description', None)
    edit_status = account.get('edit_status', None)
    reward = account.get('reward', None)
    quantity = account.get('quantity', None)
    pub_time = account.get('pub_time', None)
    content = account.get('content', None)
    msg = ""
    if sid == None or title == None or description== None or edit_status == None or pub_time==None\
        or reward == None or quantity == None or content== None or (not isinstance(edit_status, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not session['sid'] == sid:
        msg += "publisher_must_be_your_own"
        return 400, msg
    if not isinstance(quantity, int):
        msg += "quantity_must_be_int"
        return 400, msg
    if not isinstance(reward, float):
        msg += "quantity_must_be_float"
        return 400, msg
    if not select_questionnaire_by_qid(qid):
        msg += "maybe_error_qid"
        return 400, msg
    if select_questionnaire_status_by_qid(qid) == 1:
        msg += "questionnaire_in_release_cannot_be_modified"
        return 400, msg
    if edit_status == 1:
        cost = reward * quantity
        if cost > session['balance']:
            msg += "Insufficient_account_balance"
            return 400, msg
    sql = """UPDATE questiontable SET title ="%s",description = "%s", edit_status=%d,
            reward=%f, quantity=%d, pub_time="%s", content="%s"WHERE qid= "%s";""" % (
        title, description, edit_status, reward, quantity, pub_time, content, qid)
    tools.modifyOpt(sql)
    if edit_status == 1:
        reduce_balance_by_sid(session['sid'], cost)
        session['balance'] = session['balance'] - cost
    msg += "successful"
    return 200, msg

