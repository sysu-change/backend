import pymysql
from DBUtils.PooledDB import PooledDB
# The information of database
DB_HOST = "cdb-5vkcog4l.gz.tencentcdb.com"
DB_PORT = 10122
DB_DATABASE = "make_money"
DB_USER = "root"
DB_PASSWORD = "xifen123"
DB_CHARSET = "utf8"
# The information of database connection pool
# mincached : The number of idle connections opened at startup
DB_MIN_CACHED = 3
# maxcached : The maximum number of idle connections allowed in the connection pool
DB_MAX_CACHED = 3
# maxshared : The maximum number of shared connections allowed. If the maximum number is reached, the connection requested to be shared will be shared.
DB_MAX_SHARED = 10
# maxconnecyions : The maximum number of connection pools created.
DB_MAX_CONNECYIONS = 20
# blocking : Set the behavior when the connection pool reaches its maximum number.
DB_BLOCKING = True
# maxusage : The maximum number of allowed multiplexing for a single connection. When the maximum number is reached, the connection will automatically reconnect (close and reopen)
DB_MAX_USAGE = 0
# setsession : An optional list of SQL commands is used to prepare each session.
DB_SET_SESSION = None

# 打开数据库连接
db = pymysql.connect(host=DB_HOST,
                     port=DB_PORT,
                     user=DB_USER,
                     password=DB_PASSWORD,
                     database=DB_DATABASE,
                     charset=DB_CHARSET,
                     cursorclass=pymysql.cursors.DictCursor)
                     # cursorclass=pymysql.cursors.Cursor)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 使用 execute() 方法执行 SQL 查询
# cursor.execute("SELECT VERSION()")
# 使用 fetchone() 方法获取单条数据.
# data = cursor.fetchone()
# print(type(db))
# print(type(cursor))
# print(type(cursor.execute("SELECT VERSION()")))
# print(cursor.execute("SELECT VERSION()"))
# print(type(data))
# print("Database version : %s " % data)

# # SQL 插入语句
# sql = """INSERT INTO account(sid, name, age, sex, grade, major, phone_num, password)
#          VALUES ('%s', '%s', %s, '%s', '%s', '%s', '%s', '%s')""" % \
#        ('15331038', '陈笑儒', 22, '男', '大三', '软件工程', '13981153619', '123456')
#
# try:
#    # 执行sql语句
#    cursor.execute(sql)
#    # 提交到数据库执行
#    db.commit()
# except:
#    # 如果发生错误则回滚
#    db.rollback()

# SQL 查询语句
sql = "SELECT * FROM account \
       WHERE name = '%s'" % '陈笑儒'

# for Cursor
# # 执行SQL语句
# cursor.execute(sql)
# # 获取所有记录列表
# results = cursor.fetchall()
# # print(type(results))
# try:
#     # 执行SQL语句
#     cursor.execute(sql)
#     # 获取所有记录列表
#     results = cursor.fetchall()
#     # print(type(results))
#     for row in results:
#         sid = row[0]
#         name = row[1]
#         # print(type(lname))
#         age = row[2]
#         # print(type(age))
#         sex = row[3]
#         grade = row[4]
#         # 打印结果
#         print("sid = %s, name = %s, age = %s, sex = %s, grade = %s" % \
#              (sid, name, age, sex, grade))
# except:
#     print("Error: unable to fetch data")

# for DictCursor
# # 执行SQL语句
# cursor.execute(sql)
# # 获取所有记录列表
# results = cursor.fetchall()
# # print(type(results))
# try:
#     # 执行SQL语句
#     cursor.execute(sql)
#     # 获取所有记录列表
#     results = cursor.fetchall()
#     # print(type(results))
#     for row in results:
#         print(row)
# except:
#     print("Error: unable to fetch data")


# sql = "SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%S');"
# cursor.execute(sql)
# data = cursor.fetchone()
# print(data)

sql = "SHOW COLUMNS FROM %s" % 'account'
cursor.execute(sql)
data = cursor.fetchall()
print(data)
# 关闭数据库连接
db.close()

# print(pymysql.cursors.DictCursor)