import pymysql
from DBUtils.PooledDB import PooledDB
import sys
from functools import wraps
import io
import sys
from flask import current_app, session

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

    # ***
    # todo：修改这一步的报错信息，传来的sid是答卷人，不需要判断发布者是答卷人
    # ****

    # 当前sid与登录sid不符
    #if not session['sid'] == sid:
    #    msg += "refused because of publisher_must_be_your_own"
    #    return 400, msg

    # ***
    # todo：判断是否答过题，重复提交答卷会让数据库崩掉，导致后端崩掉，屏蔽这种情况
    # ****

    # ***
    # todo：未发布的问卷不允许提交答卷，虽然前端应该不会这么做，
    # todo：但是如果发来了，后端得做屏蔽处理，不然数据库会乱
    # ****

    # 数据库中查不到对应的问卷id, 即问卷不存在
    if not select_questionnaire_by_qid(qid):
        msg += "refused because of maybe_error_qid"
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

    # ***
    # todo：正常输入。但是程序会崩溃，修复逻辑bug
    # ***

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
    # 审核成功更新数据库

    # ***
    # %d 是传入数据一类，不需要加双引号的，加了双引号变成了str，数据库会崩
    # 应该传入三个参数，括号只给了两个参数，对应不上
    # ***

    sql = """UPDATE answertable SET verify ="%d" WHERE qid= "%d" AND sid= "%s";""" % \
          (qid, sid)
    tools.modifyOpt(sql)
    msg += "successful"
    return 200, msg


# 获取所有答卷
# used in /module/user/answer_get
def answer_get_model(account):

    # ***
    # todo：正常输入。但是程序会崩溃，修复逻辑bug
    # ***

    # 解析json得到想要的参数
    qid = account.get('qid', None)
    msg = ""
    content = []
    # 数据库中查不到对应的问卷id, 即问卷不存在
    if not select_questionnaire_by_qid(qid):
        msg += "refused because of maybe_error_qid"
        return 400, msg, content
    sql = "SELECT * FROM answertable WHERE qid ='%d'" % (qid)
    rows = tools.selectOpt(sql)
    if rows:
        for i in range(len(rows)):
            temp = Answer_obj()
            temp.sid = rows[i]['sid']
            temp.ans_time = rows[i]['ans_time']
            temp.verify = rows[i]['verify']
            content.append(temp)
        msg += "successful"
        return 200, msg, content
    else:
        msg += "failed"
        return 400, msg, content


# 定义答卷类对象在获取所有答卷api时返回该对象的数组
class Answer_obj():
    def __init__(self):
        self.sid = ""
        self.ans_time = ""
        self.verify = 0


# 查看具体一份问卷
# used in /module/user/get_sid_answer
def get_sid_answer_model(account):

    # ***
    # todo：正常输入。但是程序会崩溃，修复逻辑bug
    # ***

    # 解析json得到想要的参数
    qid = account.get('qid', None)
    sid = account.get('sid', None)
    msg = ""
    content = {}

    # ***
    # todo：奶牛端登陆，可以查看任意答题人的问卷，此时这两个sid是不相等的
    # ****

    # 当前sid与登录sid不符
    #if not session['sid'] == sid:
    #    msg += "refused because of publisher_must_be_your_own"
    #    return 400, msg, content
    # 数据库中查不到对应的问卷id, 即问卷不存在
    if not select_questionnaire_by_qid(qid):
        msg += "refused because of maybe_error_qid"
        return 400, msg, content
    sql = "SELECT * FROM answertable WHERE qid ='%d' AND sid ='%s" % (qid, sid)
    rows = tools.selectOpt(sql)
    if rows:
        content = rows[0]
        msg += "successful"
        return 200, msg, content
    else:
        msg += "failed"
        return 400, msg, content
