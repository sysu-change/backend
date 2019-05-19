from teach.Model import User_model
from teach.User_dal import dal


class User_Dal:
    persist = None

    # 通过用户名及密码查询用户对象
    @classmethod
    def login_auth(cls, username, password):
        print('login_auth')
        result = {'isAuth': False}
        model = User_model.User_mod()  # 实例化一个对象，将查询结果逐一添加给对象的属性
        sql = "SELECT id,username,sample_count,task_count FROM User WHERE username ='%s' AND password = '%s'" % (username,password)
        rows = user_dal.User_Dal.query(sql)
        print('查询结果>>>', rows)
        if rows:
            result['isAuth'] = True
            model.id = rows[0]
            model.username = rows[1]
            model.sample_count = rows[2]
            model.task_count = rows[3]
        return result, model

    # flask_login回调函数执行的，需要通过用户唯一的id找到用户对象
    @classmethod
    def load_user_byid(cls, id):
        print('load_user_byid')
        sql = "SELECT id,username,sample_count,task_count FROM User WHERE id='%s'" % id
        model = User_model.User_mod()  # 实例化一个对象，将查询结果逐一添加给对象的属性
        rows = user_dal.User_Dal.query(sql)
        if rows:
            result = {'isAuth': False}
            result['isAuth'] = True
            model.id = rows[0]
            model.username = rows[1]
            model.sample_count = rows[2]
            model.task_count = rows[3]
        return model

    # 具体执行sql语句的函数
    @classmethod
    def query(cls, sql, params=None):
        result = dal.SQLHelper.fetch_one(sql, params)
        return result
