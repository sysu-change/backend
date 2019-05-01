import pymysql
from DBUtils.PooledDB import PooledDB
from .tools import *
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from .dbConfig import *

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
    print('login_auth')
    result = {'isAuth': False}
    model = User_mod()  # 实例化一个对象，将查询结果逐一添加给对象的属性
    sql = "SELECT * FROM account WHERE phone_num ='%s' AND password = '%s'" % (
    phone_num, password)
    rows = tools.selectOpt(sql)
    print('查询结果>>>', rows)
    if rows:
        rows_ = rows[0]
        result['isAuth'] = True
        model.phone_num = rows_['phone_num']
    return result, model


def load_user_by_phone_num(phone_num):
    print('load_user_by_phone_num')
    sql = "SELECT * FROM account WHERE phone_num ='%s'" % (phone_num)
    model = User_mod()  # 实例化一个对象，将查询结果逐一添加给对象的属性
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        result = {'isAuth': False}
        result['isAuth'] = True
        model.phone_num = rows_['phone_num']
    return model

def register_account(account):
    sid = account['sid']
    name = account['name']
    age = account['age']
    sex = account['sex']
    grade = account['grade']
    major = account['major']
    phone_num = account['phone_num']
    password = account['password']
    sql = """INSERT INTO account(sid, name, age, sex, grade, major, phone_num, password)
                                    VALUES ("%s", "%s", %d, "%s", "%s", "%s", "%s", "%s");""" % (
    sid, name, age, sex, grade, major, phone_num, password)
    tools.modifyOpt(sql)