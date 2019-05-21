import pymysql
from DBUtils.PooledDB import PooledDB
import sys
sys.path.append('../match/')
import match
from functools import wraps
from .tools import *
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from .dbConfig import *
from flask import current_app, session

# 打开数据库连接
db = pymysql.connect(host=DB_HOST,
                     port=DB_PORT,
                     user=DB_USER,
                     password=DB_PASSWORD,
                     database=DB_DATABASE,
                     charset=DB_CHARSET)

# convert character
cursor = db.cursor()

cursor.execute('SHOW TABLES')
tables = []
for row in cursor.fetchall():
    tables.append(row)
for row in tables:
    cursor.execute('ALTER TABLE %s CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;' % (row[0]))
cursor.close()

# create tools
tools = Tools()


# 创建一个类，用来通过sql语句查询结果实例化对象用
class User_mod():
    def __init__(self):
        self.phone_num = None

    def todict(self):
        return self.__dict__

    # 下面这4个方法是flask_login需要的4个验证方式
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.phone_num


def login_auth(phone_num, password):
    # current_app.logger.info('login_auth')
    current_app.logger.info(dict(session))
    salt = select_salt_by_phone_num(phone_num)

    if salt =="":
        return False
    password = match.hash_password(password,salt)
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
        session['sex'] = match.sex_trans(rows_['sex'])
        session['grade'] = match.grade_trans(rows_['grade'])
        session['major'] = rows_['major']
        session['phone_num'] = rows_['phone_num']
        session['balance'] = rows_['balance']
    return isAuth


def login_required_mine(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get('phone_num'):
            code = 401
            msg = "not login"
            return python_object_to_json(code=code, msg=msg)
        return func(*args, **kwargs)

    return decorated_view


def select_user_by_phone_num(phone_num):
    # current_app.logger.info('select_user_by_phone_num')
    sql = "SELECT * FROM accounts WHERE phone_num ='%s'" % (phone_num)
    rows = tools.selectOpt(sql)
    if rows:
        return True
    else:
        return False


def select_salt_by_phone_num(phone_num):
    # current_app.logger.info('select_user_by_phone_num')
    sql = "SELECT * FROM accounts WHERE phone_num ='%s'" % (phone_num)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['salt']
    else:
        return ""


def select_password_by_phone_num(phone_num):
    # current_app.logger.info('select_user_by_phone_num')
    sql = "SELECT * FROM accounts WHERE phone_num ='%s'" % (phone_num)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['password']
    else:
        return ""


def select_user_by_sid(sid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT * FROM accounts WHERE sid ='%s'" % (sid)
    rows = tools.selectOpt(sql)
    if rows:
        return True
    else:
        return False


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
    salt = match.random_code(26)
    password = match.hash_password(password,salt)
    msg = ""
    if sid == None or name == None or age == None or grade == None or major == None\
            or phone_num==None or password==None or (not isinstance(age, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not match.match_sid(sid):
        msg += "error_sid"
        return 400, msg
    if not match.match_phone(phone_num):
        msg += "error_phone"
        return 400, msg
    if not match.match_password(password):
        msg += "error_password."
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


def edit_userinfo_model(sid,account):
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
    session['sex'] = match.sex_trans(sex)
    session['grade'] = match.grade_trans(grade)
    session['major'] = major
    return 200, msg


def user_recharge_model(account):
    phone_num = account.get('phone_num', None)
    money = account.get('money', None)
    msg = ""
    if phone_num == None or money == None or (not isinstance(money, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not match.match_phone(phone_num):
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


def user_withdraw_model(sid, account):
    pay_phone = account.get('pay_phone',None)
    password = account.get('password', None)
    money = account.get('money', None)
    msg = ""
    if pay_phone == None or password == None or (not isinstance(money, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not match.match_phone(pay_phone):
        msg += "error_phone"
        return 400, msg
    if not match.match_password(password):
        msg += "error_password"
        return 400, msg
    if money > session['balance']:
        msg += "not_enough_account_balance"
        return 400, msg
    salt = select_salt_by_phone_num(session['phone_num'])
    password = match.hash_password(password, salt)
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



def python_object_to_json(**kwargs):
    python2json = {}
    for i in kwargs.items():
        python2json[i[0]] = i[1]
    json_str = json.dumps(python2json)
    return json_str

