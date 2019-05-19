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

    isAuth = False
    sql = "SELECT * FROM account WHERE phone_num ='%s' AND password = '%s'" % (
    phone_num, password)
    rows = tools.selectOpt(sql)
    # current_app.logger.info('查询结果>>>', rows)
    if rows:
        rows_ = rows[0]
        isAuth = True
        session['sid'] = rows_['sid']
        session['name'] = rows_['name']
        session['age'] = rows_['age']
        session['sex'] = rows_['sex']
        if session['sex'] == '0':
            session['sex'] = u'男'
        if session['sex'] == '1':
            session['sex'] = u'女'
        session['grade'] = rows_['grade']
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
    sql = "SELECT * FROM account WHERE phone_num ='%s'" % (phone_num)
    rows = tools.selectOpt(sql)
    if rows:
        return True
    else:
        return False


def select_user_by_sid(sid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT * FROM account WHERE sid ='%s'" % (sid)
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

    msg = ""
    if sid == None or name == None or age == None or grade == None or major == None\
            or phone_num==None or password==None or (not isinstance(age, int)):
        msg += "Illegal_parameter."
    if not match.match_phone(phone_num):
        msg += "error_phone."
    # if not match.match_password(password):
    #    msg += "error_password."
    if select_user_by_phone_num(phone_num):
        msg += "already_exists_phone."
    if select_user_by_sid(sid):
        msg += "already_exists_sid."
    if msg == "":
        sql = """INSERT INTO account(sid, name, age, sex, grade, major, phone_num, password, balance)
                                            VALUES ("%s", "%s", %d, "%s", "%s", "%s", "%s", "%s", "0");""" % (
            sid, name, age, sex, grade, major, phone_num, password)
        tools.modifyOpt(sql)
        msg += "successful"
        code = 200
    else:
        code = 400
    return code, msg


def python_object_to_json(**kwargs):
    python2json = {}
    for i in kwargs.items():
        python2json[i[0]] = i[1]
    json_str = json.dumps(python2json)
    return json_str

