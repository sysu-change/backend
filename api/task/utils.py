from api import *


# 通过tid查找是否存在对应任务
def select_task_by_tid(tid):
    sql = "SELECT * FROM task WHERE tid ='%s'" % (tid)
    rows = tools.selectOpt(sql)
    if rows:
        return True
    else:
        return False


# 通过tid查找对应创建者sid
def get_sid_by_tid(tid):
    sql = "SELECT * FROM task WHERE tid ='%s'" % (tid)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['sid']
    else:
        return None


# 查找tid对应未审核的任务数目
def get_no_verify_num_by_tid(tid):
    sql = "SELECT count(*) FROM task_order WHERE tid ='%s' AND verify = 0" % (tid)
    rows = tools.selectOpt(sql)
    current_app.logger.info(rows[0])
    return rows[0]['count(*)']


# 查找tid对应已审核的任务数目
def get_verify_num_by_tid(tid):
    # current_app.logger.info('select_user_by_sid')
    sql = "SELECT count(*) FROM task_order WHERE tid ='%s' AND verify = 1" % (tid)
    rows = tools.selectOpt(sql)
    current_app.logger.info(rows[0])
    return rows[0]['count(*)']


# 查找tid对应的quantity
def get_quantity_by_tid(tid):
    sql = "SELECT * FROM task WHERE tid ='%s'" % (tid)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['quantity']
    else:
        return 0


# 查找tid对应的reward
def get_reward_by_tid(tid):
    sql = "SELECT * FROM task WHERE tid ='%s'" % (tid)
    rows = tools.selectOpt(sql)
    if rows:
        rows_ = rows[0]
        return rows_['reward']
    else:
        return 0.0


# 根据tid和sid判断任务审核状态
def get_verify_state_by_id(tid, sid):
    sql = "SELECT * FROM task_order WHERE tid = %d AND sid = '%s'" % (tid, sid)
    rows = tools.selectOpt(sql)
    if rows:
        return rows[0]['verify']
    else:
        return 0