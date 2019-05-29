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


# 通过sid和qid查找是否含有该答卷
def select_answer_by_sid_and_qid(qid, sid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT * FROM answertable WHERE qid ='%s' AND sid = '%s'" % (qid, sid)
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


# 查找qid对应的quantity
def get_quantity_by_qid(qid):
    sql = "SELECT * FROM questiontable WHERE qid ='%s'" % (qid)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['quantity']
    else:
        return 0


# 查找qid对应的reward
def get_reward_by_qid(qid):
    sql = "SELECT * FROM questiontable WHERE qid ='%s'" % (qid)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['reward']
    else:
        return 0.0


# 查找qid对应未审核的答卷
def get_no_verify_num_by_qid(qid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT count(*) FROM answertable WHERE qid ='%s' AND verify = 0" % (qid)
    rows = tools.selectOpt(sql)
    current_app.logger.info(rows[0])
    return rows[0]['count(*)']


# 查找qid对应已审核的答卷
def get_verify_num_by_qid(qid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT count(*) FROM answertable WHERE qid ='%s' AND verify = 1" % (qid)
    rows = tools.selectOpt(sql)
    current_app.logger.info(rows[0])
    return rows[0]['count(*)']


# 根据qid和sid判断答卷审核状态
def get_verify_state_by_id(qid, sid):
    sql = "SELECT * FROM answertable WHERE qid = %d AND sid = '%s'" % (qid, sid)
    rows = tools.selectOpt(sql)
    if rows:
        return rows[0]['verify']
    else:
        return 0


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


# 根据学号增加账户余额
def add_balance_by_sid(sid, money):
    sql = """UPDATE accounts SET balance = balance+"%s"WHERE sid = "%s";""" % (
        money, sid)
    tools.modifyOpt(sql)
