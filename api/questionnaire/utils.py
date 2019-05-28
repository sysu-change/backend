from api import *


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

# 查找qid对应的创建者
def get_sid_by_qid(qid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT * FROM questiontable WHERE qid ='%s'" % (qid)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['sid']
    else:
        return None


# 查找qid对应未审核的答卷
def get_no_verify_num_by_qid(qid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT count(*) FROM answertable WHERE qid ='%s' AND verify = 0" % (qid)
    rows = tools.selectOpt(sql)
    return int(rows[0])


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