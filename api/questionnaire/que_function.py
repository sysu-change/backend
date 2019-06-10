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
    sid = session.get('sid')
    title = account.get('title', None)
    description = account.get('description', None)
    edit_status = account.get('edit_status', None)
    reward = account.get('reward', None)
    quantity = account.get('quantity', None)
    pub_time = account.get('pub_time', None)
    content = account.get('content', None)
    msg = ""
    if sid is None or title is None or description is None or edit_status is None or \
            pub_time is None or reward is None or quantity is None or \
            content is None or (not isinstance(edit_status, int)):
        msg += "Illegal_parameter"
        return 400, msg
    #if not isinstance(quantity, int):
    #    msg += "quantity_must_be_int"
    #    return 400, msg
    if not isinstance(reward, float):
        msg += "reward_must_be_float"
        return 400, msg
    if edit_status == 1:
        cost = reward * quantity
        if cost > session['balance']:
            msg += "Insufficient_account_balance"
            return 400, msg
    sql = """INSERT INTO questiontable(sid, title, description, edit_status, quantity, reward, pub_time, content)
                    VALUES ("%s", "%s", "%s", %d ,%d, %f,"%s","%s");""" % (
                            sid, title, description, edit_status, quantity,
                            reward, pub_time, content)
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
    sid = session.get('sid')
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
    if not isinstance(quantity, int):
        msg += "quantity_must_be_int"
        return 400, msg
    #if not isinstance(reward, float):
    #    msg += "quantity_must_be_float"
    #    return 400, msg
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


# 删除问卷
# used in /module/user/delete_questionnaire
def delete_questionnaire_model(account):
    qid = account.get('qid', None)
    msg = ""
    # 对应参数为空的情况
    if qid == None:
        msg += "refused because of Illegal_parameter"
        return 400, msg
    # 数据库中查不到对应的问卷id, 即问卷不存在
    if not select_questionnaire_by_qid(qid):
        msg += "refused because of maybe_error_qid"
        return 400, msg
    # 查看该用户是否是该问卷创始人
    if not session['sid'] == get_sid_by_qid(qid):
        msg += "refused because no authority"
        return 400, msg
    # 查看是否还存在答卷未审核
    if get_no_verify_num_by_qid(qid) != 0:
        msg += "refused because there are still some answers no verify"
        return 400, msg
    # 判断是否需要退钱
    if select_questionnaire_status_by_qid(qid) == 1:
        # 返还剩下的钱
        verify_num = get_verify_num_by_qid(qid)
        quantity = get_quantity_by_qid(qid)
        reward = get_reward_by_qid(qid)
        return_monty = (quantity - verify_num) * reward
        add_balance_by_sid(session['sid'], return_monty)
        session['balance'] = session['balance'] + return_monty
    # 删除问卷
    sql = """DELETE FROM questiontable WHERE qid="%d";""" % \
          (qid)
    tools.modifyOpt(sql)

    msg += "successful"
    return 200, msg


# 获取用户创建的所有问卷
# used in /module/user/questionnaire_own
def questionnaire_own_model(account):
    sid = session.get('sid')
    msg = ""
    content = []
    # 对应参数为空的情况
    if sid is None:
        msg += "refused because of Illegal_parameter"
        return 400, msg, 0, content
    sql = "SELECT * FROM questiontable WHERE sid='%s'" % (sid)
    rows = tools.selectOpt(sql)
    if rows:
        for i in range(len(rows)):
            temp = {}
            temp['qid'] = rows[i]['qid']
            temp['title'] = rows[i]['title']
            temp['description'] = rows[i]['description']
            temp['edit_status'] = rows[i]['edit_status']
            temp['quantity'] = rows[i]['quantity']
            temp['reward'] = rows[i]['reward']
            content.append(temp)
        msg += "successful"
        number = len(rows)
        return 200, msg, number, content
    else:
        msg += "successful"
        number = 0
        return 200, msg, 0, content


# 请求具体问卷
# used in /module/user/questionnaire/{qid}
def questionnaire_spec_model(qid):
    qid = qid
    msg = ""
    # 对应参数为空的情况
    if qid == None:
        msg += "refused because of Illegal_parameter"
        return 400, msg, []
    # 数据库中查不到对应的问卷id, 即问卷不存在
    if not select_questionnaire_by_qid(qid):
        msg += "refused because of maybe_error_qid"
        return 400, msg, []

    sql = "SELECT * FROM questiontable WHERE qid='%d'" % (qid)
    rows = tools.selectOpt(sql)
    if rows:
        content = rows[0]
        content['content'] = eval(content['content'])
        msg += "successful"
        return 200, msg, content
    else:
        msg += "no record"
        content = None
        return 200, msg, content


# 问卷预览页面数据请求
# 从当前偏移量开始，获取接下去n个数据库问卷，用户已经填写的不传，未发布的问卷不传
# used in /module/user/questionnaire_pre
def questionnaire_pre_model(request):
    offset = request.args.get("offset")
    number = request.args.get("number")

    content = []
    msg = ""

    if offset is None or number is None or not (offset.isdigit() and number.isdigit()):
        msg += "invalid parameter"
        number = 0
        return 400, msg, number, content

    offset = int(offset)
    number = int(number)

    sql = "SELECT * FROM questiontable where edit_status = 1"
    rows = tools.selectOpt(sql)
    if rows:
        for i in range(offset, min(len(rows), offset+number)):
            temp = {}
            temp['qid'] = rows[i]['qid']
            temp['title'] = rows[i]['title']
            temp['description'] = rows[i]['description']
            temp['edit_status'] = rows[i]['edit_status']
            temp['quantity'] = rows[i]['quantity']
            temp['reward'] = rows[i]['reward']
            content.append(temp)
        msg += "successful"
        number = len(content)
        return 200, msg, number, content
    else:
        msg += "no record"
        number = 0
        return 200, msg, 0, content
