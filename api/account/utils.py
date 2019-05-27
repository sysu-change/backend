from api import *


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
