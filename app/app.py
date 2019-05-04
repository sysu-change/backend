import datetime
import time
import json
import random
import logging
from flask import Flask, redirect, jsonify, render_template, request, session, abort, make_response
from flask_login import login_required, login_user, logout_user, LoginManager, current_user

from flask_cors import CORS
import redis
from dbTools import *
# 引入OS模块中的产生一个24位的随机字符串的函数
import os

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = '234rsdf34523rwsf'

# 项目中设置flask_login
login_manager = LoginManager()
login_manager.init_app(app)

# 解决跨域问题
def jsonResponse(dump_json):
    '''
    参数值为已格式化的json
    返回值为进行包装后的response
    '''
    res = make_response(dump_json)
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'POST,GET,PUT,DELETE,OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res


# 登录函数
@app.route('/module/login', methods=['POST'])
def login():
    user = request.json
    phone_num = user.get('phone_num', None)
    password = user.get('password', None)
    # phone_num = request.json['phone_num']
    # password = request.json['password']

    result = login_auth(phone_num, password)
    model = result[1]
    if result[0]['isAuth']:
        login_user(model)
        code = 200
        msg = "successful"
        # print(current_user.phone_num)  # 登录成功之后可以用current_user来取该用户的其他属性，这些属性都是sql语句查来并赋值给对象的。
        # dump_json = jsonify("login is success")
        # return jsonResponse(dump_json)
    elif phone_num==None or password==None:
        code = 400
        msg = "Illegal_parameter"
    else:
        code = 400
        msg = "error_account_or_password"
        # abort(400)
    return python_object_to_json(code, msg)


'''
load_user是一个flask_login的回调函数，在登录之后，每访问一个带Login_required装饰的视图函数就要执行一次，
该函数返回一个用户对象，通过id来用sql语句查到的用户数据，然后实例化一个对象，并返回。
'''
@login_manager.user_loader
def load_user(phone_num):
    return load_user_by_phone_num(phone_num)


# 注册函数
@app.route('/module/register', methods=['POST'])
def register():
    # if not session.get('logged_in'):
    #     abort(401)

    code, msg = register_account(request.json)
    return python_object_to_json(code, msg)
    # return "register successfully"


# 注销登录函数
@app.route('/module/logout', methods=['DELETE'])
@login_required
def logout():
    # session.pop('logged_in', None)
    logout_user()
    code = 200
    msg = "successful"
    return python_object_to_json(code, msg)
    # flash('You were logged out')


def python_object_to_json(code, msg):
    python2json = {}
    python2json["code"] = code
    python2json["msg"] = msg
    json_str = json.dumps(python2json)
    return json_str

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)

