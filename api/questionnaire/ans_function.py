import pymysql
from DBUtils.PooledDB import PooledDB
import sys
from functools import wraps
import io
import sys
from flask import current_app, session
import json

from api import *
from .utils import *


# 答卷提交
# used in /module/user/answer_put_forward
def answer_put_forward_model(account):
    # 解析json得到想要的参数
    qid = account.get('qid', None)
    sid = account.get('sid', None)
    ans_time = account.get('ans_time', None)
    verify = 0
    content = account.get('content', None)
    msg = ""
    # 判断各种异常情况
    # 对应参数为空的情况
    if sid is None or sid is None or ans_time is None or verify is None or content is None:
        msg += "refused because of Illegal_parameter"
        return 400, msg

    # 当前sid与登录sid不符
    if not session['sid'] == sid:
        msg += "refused because of login_in sid don't match!"
        return 400, msg

    # 数据库中查不到对应的问卷id, 即问卷不存在
    if not select_questionnaire_by_qid(qid):
        msg += "refused because of maybe_error_qid"
        return 400, msg

    # 判断是否答过题，重复提交答卷会让数据库崩掉，导致后端崩掉，屏蔽这种情况
    if select_answer_by_sid_and_qid(qid, sid):
        msg += "answer the same questionaire twice!"
        return 400, msg

    # 未发布的问卷不允许提交答卷
    if select_questionnaire_status_by_qid(qid) == 0:
        msg += "questionaire hasn't been published!"
        return 400, msg

    # 成功插入答卷表更新数据库
    sql = """INSERT INTO answertable(qid, sid, ans_time, verify, content)
                                                    VALUES ("%d", "%s", "%s", %d ,"%s");""" % (
        qid, sid, ans_time, verify, content)
    tools.modifyOpt(sql)
    msg += "successful"
    return 200, msg


# 答卷审核
# used in /module/user/answer_review
def answer_review_model(account):
    # 解析json得到想要的参数
    qid = account.get('qid', None)
    sid = account.get('sid', None)
    verify = account.get('verify', None)
    msg = ""
    # 判断各种异常情况
    # 对应参数为空的情况
    if qid == None or sid == None or verify == None :
        msg += "refused because of Illegal_parameter"
        return 400, msg
    # 数据库中查不到对应的问卷id, 即问卷不存在
    if not select_questionnaire_by_qid(qid):
        msg += "refused because of maybe_error_qid"
        return 400, msg
    # 原来已经审核成功
    if get_verify_state_by_id(qid, sid) == 1:
        msg += "already verify successful"
        return 200, msg
    # 审核成功更新数据库
    sql = """UPDATE answertable SET verify =%d WHERE qid= %d AND sid = "%s";""" % (
        verify, qid, sid)
    tools.modifyOpt(sql)

    # 现审核成功支付费用
    money = get_reward_by_qid(qid)
    if verify == 1:
        add_balance_by_sid(sid, money)
    msg += "successful"
    return 200, msg


# 获取所有答卷
# used in /module/user/answer_get
def answer_get_model(account):
    # 解析json得到想要的参数
    qid = account.get('qid', None)
    msg = ""
    content = []
    # 数据库中查不到对应的问卷id, 即问卷不存在
    if not select_questionnaire_by_qid(qid):
        msg += "refused because of maybe_error_qid"
        return 400, msg, 0, content
    sql = "SELECT * FROM answertable WHERE qid =%d" % (qid)
    rows = tools.selectOpt(sql)
    if rows:
        for i in range(len(rows)):
            temp = {}
            temp['sid'] = rows[i]['sid']
            temp['ans_time'] = rows[i]['ans_time']
            temp['verify'] = rows[i]['verify']
            content.append(temp)
        msg += "successful"
        number = len(rows)
        return 200, msg, number, content
    else:
        msg += "failed"
        number = 0
        return 400, msg, number, content


# 查看具体一份问卷
# used in /module/user/get_sid_answer
def get_sid_answer_model(account):
    # 解析json得到想要的参数
    qid = account.get('qid', None)
    sid = account.get('sid', None)
    msg = ""
    content = {}

    # 数据库中查不到对应的答卷id, 即答卷不存在
    if not select_answer_by_sid_and_qid(qid, sid):
        msg += "refused because of maybe_error_qid_and_sid"
        return 400, msg, content
    sql = "SELECT * FROM answertable WHERE qid =%d AND sid ='%s'" % (qid, sid)
    rows = tools.selectOpt(sql)
    if rows:
        content = rows[0]
        content['content'] = eval(content['content'])
        msg += "successful"
        return 200, msg, content
    else:
        msg += "failed"
        return 400, msg, content
