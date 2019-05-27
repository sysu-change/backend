import pymysql
from DBUtils.PooledDB import PooledDB
import sys
from functools import wraps
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from flask import current_app, session


from dbTools import *
from .utils import *

# 打开数据库连接
db = pymysql.connect(host=DB_HOST,
                     port=DB_PORT,
                     user=DB_USER,
                     password=DB_PASSWORD,
                     database=DB_DATABASE,
                     charset=DB_CHARSET)

# 使用cursor()方法获取操作游标
cursor = db.cursor()

cursor.execute('SHOW TABLES')
tables = []
for row in cursor.fetchall():
    tables.append(row)
for row in tables:
    cursor.execute('ALTER TABLE %s CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;' % (row[0]))
cursor.close()

# create tools
tools = dbTools()


# 登录函数
# used in /module/login
def login_auth(phone_num, password):
    # current_app.logger.info('login_auth')
    current_app.logger.info(dict(session))
    salt = select_salt_by_phone_num(phone_num)

    if salt == "":
        return False
    password = hash_password(password, salt)
    isAuth = False
    sql = "SELECT * FROM accounts WHERE phone_num ='%s' AND password = '%s'" % (
    phone_num, password)
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
        session['balance'] = rows_['balance']
    return isAuth


# 确认是否登录的函数
# used in all api needs login before
def login_required_mine(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get('phone_num'):
            code = 401
            msg = "not login"
            return python_object_to_json(code=code, msg=msg)
        return func(*args, **kwargs)

    return decorated_view


# 根据手机号查找是否拥有该用户
# serve for user_recharge_model
# serve for register_account
def select_user_by_phone_num(phone_num):
    # current_app.logger.info('select_user_by_phone_num')
    sql = "SELECT * FROM accounts WHERE phone_num ='%s'" % (phone_num)
    rows = tools.selectOpt(sql)
    if rows:
        return True
    else:
        return False


# 根据收据号获取盐值
# serve for login_auth
# serve for user_withdraw_model
def select_salt_by_phone_num(phone_num):
    # current_app.logger.info('select_user_by_phone_num')
    sql = "SELECT * FROM accounts WHERE phone_num ='%s'" % (phone_num)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['salt']
    else:
        return ""


# 根据手机号获取密码
def select_password_by_phone_num(phone_num):
    # current_app.logger.info('select_user_by_phone_num')
    sql = "SELECT * FROM accounts WHERE phone_num ='%s'" % (phone_num)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['password']
    else:
        return ""


# 查找是否拥有该用户id
def select_user_by_sid(sid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT * FROM accounts WHERE sid ='%s'" % (sid)
    rows = tools.selectOpt(sql)
    if rows:
        return True
    else:
        return False


# 查找是否含有该问卷id
def select_questionnaire_by_qid(qid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT * FROM questiontable WHERE qid ='%s'" % (qid)
    rows = tools.selectOpt(sql)
    if rows:
        return True
    else:
        return False


# 根据问卷id获取问卷状态
def select_questionnaire_status_by_qid(qid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT * FROM questiontable WHERE qid ='%s'" % (qid)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['edit_status']
    else:
        return 9999


# 根据学号增加账户余额
def add_balance_by_sid(sid,money):
    sql = """UPDATE accounts SET balance = balance+"%s"WHERE sid = "%s";""" % (
        money, sid)
    tools.modifyOpt(sql)


# 根据学号减少账户余额
def reduce_balance_by_sid(sid, money):
    sql = """UPDATE accounts SET balance = balance-"%s"WHERE sid = "%s";""" % (
        money, sid)
    tools.modifyOpt(sql)


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
    password = account.get('password', None)


    # 密码加密逻辑，生成26位字符串，对前端传来的密码进行盐值加密之后存进数据库
    salt = random_code(26)
    password = hash_password(password, salt)
    msg = ""
    if sid == None or name == None or age == None or grade == None or major == None\
            or phone_num==None or password==None or (not isinstance(age, int)):
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
        sql = """INSERT INTO accounts(sid, name, age, sex, grade, major, phone_num, password, balance,salt)
                                            VALUES ("%s", "%s", %d, "%s", "%s", "%s", "%s", "%s", "0","%s");""" % (
            sid, name, age, sex, grade, major, phone_num, password, salt)
        tools.modifyOpt(sql)
        msg += "successful"
        code = 200
    else:
        code = 400
    return code, msg


# 修改用户资料
# used in /module/user/userinfo--PUT
def edit_userinfo_model(sid, account):
    name = account.get('name', None)
    age = account.get('age', None)
    sex = account.get('sex', None)
    grade = account.get('grade', None)
    major = account.get('major', None)
    msg = ""
    if  name == None or age == None or grade == None or major == None or sex ==None \
             or (not isinstance(age, int)) or (not isinstance(sex, int)) or (not isinstance(grade, int)):
        msg += "Illegal_parameter"
        return 400, msg
    sql = """UPDATE accounts SET name ="%s",age = "%s", sex="%s",grade="%s",major="%s"WHERE sid= "%s";""" % (
                 name, age, sex, grade, major, sid)
    tools.modifyOpt(sql)
    msg += "successful"
    session['name'] = name
    session['age'] = age
    session['sex'] = sex_trans(sex)
    session['grade'] = grade_trans(grade)
    session['major'] = major
    return 200, msg


# 账户提现
# used in /user/withdraw
def user_recharge_model(account):
    phone_num = account.get('phone_num', None)
    money = account.get('money', None)
    msg = ""
    if phone_num == None or money == None or (not isinstance(money, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not match_phone(phone_num):
        msg += "error_phone"
        return 400, msg
    if not select_user_by_phone_num(phone_num):
        msg += "not_registered_phone_num"
        return 400, msg
    sql = """UPDATE accounts SET balance = balance+"%s"WHERE phone_num= "%s";""" % (
        money, phone_num)
    tools.modifyOpt(sql)
    msg += "successful"
    if phone_num == session['phone_num']:
        session['balance'] = session['balance'] + money
    return 200, msg


# 创建问卷
# used in /module/user/create_questionnaire
def user_withdraw_model(sid, account):
    pay_phone = account.get('pay_phone', None)
    password = account.get('password', None)
    money = account.get('money', None)
    msg = ""
    if pay_phone == None or password == None or (not isinstance(money, int)):
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
    sql = """UPDATE accounts SET balance = balance-"%s"WHERE phone_num= "%s";""" % (
        money, session['phone_num'])
    tools.modifyOpt(sql)
    msg += "successful"
    session['balance'] = session['balance'] - money
    return 200, msg


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
    msg =""
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
    msg =""
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


