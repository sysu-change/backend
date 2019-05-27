import datetime
import time
import json
import random
import logging
from flask import Flask, redirect, jsonify, render_template, request, session, abort, make_response
from flask_login import login_required, login_user, logout_user, LoginManager, current_user
from flask import current_app
from flask_cors import CORS
import redis
import os

from api import *

app = Flask(__name__, instance_relative_config=True)
# app.config['SECRET_KEY'] = '234rsdf34523rwsf'
app.config['SECRET_KEY'] = os.urandom(24)  # 设置随机字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间

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


"""
用户信息接口
"""


# 登录函数
@app.route('/module/login', methods=['POST'])
def login():
    # current_app.logger.info('123')
    # current_app.logger.info(request.json)

    user = request.json
    phone_num = user.get('phone_num', None)
    password = user.get('password', None)

    isAuth = login_auth(phone_num, password)
    if isAuth:
        code = 200
        msg = "successful"
    elif phone_num == None or password == None:
        code = 400
        msg = "Illegal_parameter"
    else:
        code = 400
        msg = "error_password"
    # current_app.logger.info(dict(session))
    return python_object_to_json(code=code, msg=msg)


# 注册用户
@app.route('/module/register', methods=['POST'])
def register():
    # if not session.get('logged_in'):
    #     abort(401)

    code, msg = register_account(request.json)
    return python_object_to_json(code=code, msg=msg)
    # return "register successfully"


# 注销登录函数
@app.route('/module/logout', methods=['DELETE'])
@login_required_mine
def logout():
    # session.pop('logged_in', None)
    session.pop('sid')
    session.pop('name')
    session.pop('age')
    session.pop('sex')
    session.pop('grade')
    session.pop('major')
    session.pop('phone_num')
    session.pop('balance')

    code = 200
    msg = "successful"
    # current_app.logger.info(dict(session))
    return python_object_to_json(code=code, msg=msg)
    # flash('You were logged out')


# 获取用户资料
@app.route('/module/user/userinfo', methods=['GET'])
@login_required_mine
def userinfo():
    name = session.get('name')
    sid = session.get('sid')
    age = session.get('age')
    major = session.get('major')
    grade = session.get('grade')
    sex = session.get('sex')
    phone_num = session.get('phone_num')
    balance = session.get('balance')
    return python_object_to_json(name=name, sid=sid, age=age, major=major, grade=grade,
                                 sex=sex, phone_num=phone_num, balance=balance)


# 修改用户资料
@app.route('/module/user/userinfo', methods=['PUT'])
@login_required_mine
def edit_userinfo():
    sid = session.get('sid')
    code, msg = edit_userinfo_model(sid, request.json)
    return python_object_to_json(code=code, msg=msg)


# 账户充值
@app.route('/user/recharge', methods=['POST'])
#@login_required_mine
def user_recharge():
    sid = session.get('sid')
    # current_app.logger.info(sid)
    code, msg = user_recharge_model(request.json)
    return python_object_to_json(code=code, msg=msg)


# 账户提现
@app.route('/user/withdraw', methods=['POST'])
@login_required_mine
def user_withdraw():
    sid = session.get('sid')
    code, msg = user_withdraw_model(sid, request.json)
    return python_object_to_json(code=code, msg=msg)


"""
问卷接口
"""

# 创建问卷
@app.route('/module/user/create_questionnaire', methods=['POST'])
@login_required_mine
def create_questionnaire():
    code, msg = create_questionnaire_model(request.json)
    return python_object_to_json(code=code, msg=msg)


# 修改编辑问卷
@app.route('/module/user/edit_questionnaire', methods=['PUT'])
@login_required_mine
def edit_questionnaire():
    code, msg = edit_questionnaire_model(request.json)
    return python_object_to_json(code=code, msg=msg)


# 删除问卷
@app.route('/module/user/delete_questionnaire', methods=['DELETE'])
@login_required_mine
def delete_questionnaire():
    pass


# 获取用户创建的所有问卷
@app.route('/module/user/questionnaire_own', methods=['GET'])
@login_required_mine
def questionnaire_own():
    pass


# 请求具体问卷
@app.route('/module/user/wenjuan/{wenjuan_id}', methods=['GET'])
@login_required_mine
def wenjuan():
    pass


# 问卷预览页面数据请求
# 从当前偏移量开始，获取接下去n个数据库问卷，用户已经填写的不传，未发布的问卷不传
@app.route('/module/user/questionnaire_pre', methods=['GET'])
@login_required_mine
def questionnaire_pre():
    pass


"""
答卷接口
"""


#  答卷提交
@app.route('/module/user/answer_put_forward', methods=['POST'])
@login_required_mine
def answer_put_forward():
    pass


# 答卷审核
@app.route('/module/user/answer_review', methods=['PUT'])
@login_required_mine
def answer_review():
    pass


# 获取所有答卷
@app.route('/module/user/answer_get', methods=['GET'])
@login_required_mine
def answer_get():
    pass


# 查看一份具体的答卷
@app.route('/module/user/get_sid_answer', methods=['GET'])
@login_required_mine
def get_sid_answer():
    pass


if __name__ == '__main__':
    CORS(app, supports_credentials=True)
    app.run(host='localhost', port=8082, debug=True)
