import pymysql
from DBUtils.PooledDB import PooledDB
import sys
from functools import wraps
import io
import sys
from flask import current_app, session

from api import *
from .utils import *


# 登录函数
# used in /module/login
def login_auth(account):
    phone_num = account.get('phone_num', None)
    password = account.get('password', None)

    salt = select_salt_by_phone_num(phone_num)

    if salt == "":
        code = 400
        msg = "fail"
        return code, msg
    password = hash_password(password, salt)
    isAuth = False
    sql = "SELECT * FROM accounts WHERE phone_num='%s' AND password='%s'" % \
          (phone_num, password)
    rows = tools.selectOpt(sql)
    # current_app.logger.info('查询结果>>>', rows)
    if rows:
        rows_ = rows[0]
        isAuth = True
        session['sid'] = rows_['sid']
        session['name'] = rows_['name']
        session['age'] = rows_['age']
        session['sex'] = sex_trans(rows_['sex'])
        session['grade'] = grade_trans(rows_['grade'])
        session['major'] = rows_['major']
        session['phone_num'] = rows_['phone_num']
        session['email'] = rows_['email']
        session['Credibility'] = rows_['Credibility']
        session['balance'] = rows_['balance']
    if isAuth:
        code = 200
        msg = "successful"
    elif phone_num == None or password == None:
        code = 400
        msg = "Illegal_parameter"
    else:
        code = 400
        msg = "error_password"
    return code, msg


# 注册用户
# used in /module/user/register
def register_account(account):
    sid = account.get('sid', None)
    name = account.get('name', None)
    age = account.get('age', None)
    sex = account.get('sex', None)
    grade = account.get('grade', None)
    major = account.get('major', None)
    phone_num = account.get('phone_num', None)
    email = account.get('email', None)
    Credibility = 100
    password = account.get('password', None)

    # 密码加密逻辑，生成26位字符串，对前端传来的密码进行盐值加密之后存进数据库
    salt = random_code(26)
    password = hash_password(password, salt)
    msg = ""
    if sid is None or name is None or age is None or grade is None or major is None\
            or phone_num is None or email is None or password is None or (not isinstance(age, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not match_sid(sid):
        msg += "error_sid"
        return 400, msg
    if not match_phone(phone_num):
        msg += "error_phone"
        return 400, msg
    if select_user_by_phone_num(phone_num):
        msg += "already_exists_phone"
        return 400, msg
    if select_user_by_sid(sid):
        msg += "already_exists_sid"
        return 400, msg
    if msg == "":
        sql = """INSERT INTO accounts(sid, name, age, sex, grade, major, phone_num, email, Credibility, password, balance,salt)
                                            VALUES ("%s", "%s", %d, "%s", "%s", "%s", "%s","%s",%d, "%s", "0","%s");""" % (
            sid, name, age, sex, grade, major, phone_num, email, Credibility, password, salt)
        tools.modifyOpt(sql)
        msg += "successful"
        code = 200
    else:
        code = 400
    return code, msg


# 修改用户资料
# used in /module/user/userinfo--PUT
def edit_userinfo_model(account):
    sid = session.get('sid')
    name = account.get('name', None)
    age = account.get('age', None)
    sex = account.get('sex', None)
    grade = account.get('grade', None)
    major = account.get('major', None)
    email = account.get('email', None)
    msg = ""
    if name is None or age is None or grade is None or major is None or sex is None or email is None \
             or (not isinstance(age, int)) or (not isinstance(sex, int)) or (not isinstance(grade, int)):
        msg += "Illegal_parameter"
        return 400, msg
    sql = """UPDATE accounts SET name="%s",age="%s", sex="%s",grade="%s",major="%s", email="%s" WHERE sid="%s";""" % (
                 name, age, sex, grade, major, email, sid)
    tools.modifyOpt(sql)
    msg += "successful"
    session['name'] = name
    session['age'] = age
    session['sex'] = sex_trans(sex)
    session['grade'] = grade_trans(grade)
    session['major'] = major
    session['email'] = email
    return 200, msg


# 账户充值
# used in /user/recharge
def user_recharge_model(account):
    phone_num = account.get('phone_num', None)
    money = account.get('money', None)
    msg = ""
    if phone_num is None or money is None or (not isinstance(money, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not match_phone(phone_num):
        msg += "error_phone"
        return 400, msg
    if not select_user_by_phone_num(phone_num):
        msg += "not_registered_phone_num"
        return 400, msg
    sql = """UPDATE accounts SET balance = balance+"%s" WHERE phone_num="%s";""" % (
        money, phone_num)
    tools.modifyOpt(sql)
    msg += "successful"
    if phone_num == session['phone_num']:
        session['balance'] = session['balance'] + money
    return 200, msg


# 账户提现
# used in /user/withdraw
def user_withdraw_model(account):
    sid = session.get('sid')
    pay_phone = account.get('pay_phone', None)
    password = account.get('password', None)
    money = account.get('money', None)
    msg = ""
    if pay_phone is None or password is None or (not isinstance(money, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not match_phone(pay_phone):
        msg += "error_phone"
        return 400, msg
    if money > session['balance']:
        msg += "not_enough_account_balance"
        return 400, msg
    salt = select_salt_by_phone_num(session['phone_num'])
    password = hash_password(password, salt)
    right_pass = select_password_by_phone_num(session['phone_num'])
    if not password == right_pass:
        msg += "error_password"
        return 400, msg
    sql = """UPDATE accounts SET balance = balance-"%s"WHERE phone_num="%s";""" % (
        money, session['phone_num'])
    tools.modifyOpt(sql)
    msg += "successful"
    session['balance'] = session['balance'] - money
    return 200, msg


# 用户邮箱验证
# used in /module/user/sent_verify
def user_sent_verify_model(account):
    email = account.get('email', None)
    msg = ""

    if email is None :
        msg += "Illegal_parameter"
        return 400, msg, ""
    code = random_code(4)
    sent_email_to_task_publisher(email, code, 4)
    msg += "successful"
    return 200, msg, code
