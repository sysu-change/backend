import pymysql
from DBUtils.PooledDB import PooledDB
import sys
from functools import wraps
import io
import sys
from flask import current_app, session
import json

from api import *
from .utils import *


# 奶牛端创建发布任务(后端做的时候添加status, int类型，0：初始值刚发布未完成 1：已完成)
# used in module/user/create_task
def create_task_model(account):
    # 蔡湘国
    sid = session.get('sid')
    type = account.get('type', None)
    description = account.get('description', None)
    detail = account.get('detail', None)
    deadline = account.get('deadline', None)
    phone_num = account.get('phone_num', None)
    wechat = account.get('wechat', None)
    quantity = account.get('quantity', None)
    reward = account.get('reward', None)
    status = 0
    msg = ""
    if sid is None or type is None or description is None or detail is None or \
            deadline is None or phone_num is None or wechat is None or \
            quantity is None or reward is None or (not isinstance(type, int)):
        msg += "Illegal_parameter"
        return 400, msg
    if not isinstance(quantity, int):
        msg += "quantity_must_be_int"
        return 400, msg
    if not isinstance(reward, float):
        msg += "reward_must_be_float"
        return 400, msg
    cost = reward * quantity
    if cost > session['balance']:
        msg += "Insufficient_account_balance"
        return 400, msg
    sql = """INSERT INTO task(sid, type, description, detail, deadline, phone_num, wechat, quantity, reward, status)
                        VALUES ("%s", %d, "%s", "%s", "%s", "%s", "%s", %d, %f, %d);""" % (
        sid, type, description, detail, deadline, phone_num, wechat, quantity, reward, status)
    tools.modifyOpt(sql)
    reduce_balance_by_sid(session['sid'], cost)
    session['balance'] = session['balance'] - cost
    msg += "successful"
    return 200, msg


# 学生端申请任务（需求量从数据库调用减1，发送邮件给发起者和接收者，申请接单接单状态accept_status=0）
# used in module/user/apply
def apply_model(account):
    # 陈笑儒
    tid = account.get('tid', None)
    sid = session.get('sid')

    msg = ""
    if tid is None:
        msg += "Illegal_parameter"
        return 400, msg
    if not isinstance(tid, int):
        msg += "tid_must_be_int"
        return 400, msg

    sql = "SELECT * FROM task WHERE tid ='%d'" % (tid)
    rows = tools.selectOpt(sql)
    if rows and rows[0]['quantity'] <= 0:
        msg += "the applier of this task is full"
        return 400, msg
    if not rows:
        msg += "no this task"
        return 400, msg
    p_sid = rows[0]['sid']
    if p_sid == sid:
        msg += "you can't apply task you created"
        return 400, msg

    sql = "SELECT * FROM task_order WHERE tid='%d' and sid='%s'" % (tid, sid)
    rows = tools.selectOpt(sql)
    if rows:
        msg += "you have already applied this task"
        return 400, msg

    sql = """UPDATE task SET quantity = quantity-1 WHERE tid="%d";""" % (tid)
    tools.modifyOpt(sql)
    sql = """INSERT INTO task_order(tid, sid, accept_status, verify, reward_status)
                            VALUES ("%d", %s, "%d", "%d", "%d");""" % (tid, sid, 0, 0, 0)
    tools.modifyOpt(sql)

    # email_publisher = select_email_by_sid(p_sid)
    # email_receiver = select_email_by_sid(sid)
    # sent_email_to_task_publisher(email_publisher, tid, 1)
    # sent_email_to_task_receiver(email_receiver, tid, 1)

    msg += "successful"
    return 200, msg


# 学生端完成任务（更新接单状态accept_status=1，邮件通知任务发起者，提醒审核）
# used in module/user/task_finish
def task_finish_model(account):
    # 陈笑儒
    tid = account.get('tid', None)
    sid = session.get('sid')

    msg = ""
    if tid is None:
        msg += "Illegal_parameter"
        return 400, msg
    if not isinstance(tid, int):
        msg += "tid_must_be_int"
        return 400, msg

    if not select_task_by_tid(tid):
        msg += "no this task"
        return 400, msg

    sql = "SELECT * FROM task_order WHERE tid='%d' and sid='%s'" % (tid, sid)
    rows = tools.selectOpt(sql)
    if not rows:
        msg += "you haven't applied this task"
        return 400, msg
    elif rows[0]['accept_status'] == 1:
        msg += "you have already finished this task"
        return 400, msg

    sql = """UPDATE task_order SET accept_status = 1 WHERE tid='%d' and sid='%s';""" % (tid, sid)
    tools.modifyOpt(sql)

    # email_publisher = select_email_by_sid(p_sid)
    # sent_email_to_task_publisher(email_publisher, tid, 2)

    msg += "successful"
    return 200, msg


# 奶牛端查看已完成的任务（注意是学生端标记任务完成，而不是奶牛端整个任务结束，奶牛端在学生标记任务完成之后还要进行审核）
# used in module/user/provider_task_done
def provider_task_done_model():
    # 蔡湘国
    sid = session.get('sid')
    content = []
    msg = ""
    sql = "(SELECT * FROM task t1,task_order t2 where " \
          "t1.tid=t2.tid and t1.sid='%s' and accept_status=1)" % (sid)
    rows = tools.selectOpt(sql)
    if rows:
        for i in range(len(rows)):
            temp = {}
            temp['tid'] = rows[i]['tid']
            temp['type'] = rows[i]['type']
            temp['reward'] = rows[i]['reward']
            temp['sid'] = rows[i]['sid']
            temp['accept_status'] = rows[i]['accept_status']
            temp['verify'] = rows[i]['verify']
            content.append(temp)
        msg += "successful"
        number = len(content)
        return 200, msg, number, content
    else:
        msg += "no record"
        return 200, msg, 0, content
    pass


# 奶牛端查看正在进行中的任务（包括已接单但未完成，和发布中未被接单的任务）
# used in module/user/provider_task_in_progress
def provider_task_in_progress_model():
    # ************
    #  todo： 一项任务 审批成功的人数 ==需求人数为任务完成  其他都是未完成  这里返还信息出错
    # ************

    # 蔡湘国
    sid = session.get('sid')
    content = []
    msg = ""
    # 已接单未完成
    sql = "(SELECT * FROM task t1,task_order t2 where " \
          "t1.tid=t2.tid and t1.sid='%s' and accept_status=0)" % (sid)
    rows = tools.selectOpt(sql)
    if rows:
        for i in range(len(rows)):
            temp = {}
            temp['tid'] = rows[i]['tid']
            temp['type'] = rows[i]['type']
            temp['deadline'] = rows[i]['deadline']
            temp['reward'] = rows[i]['reward']
            temp['quantity'] = rows[i]['quantity']
            acc_num = compute_accept_num(rows[i]['tid'])
            temp['accept_num'] = acc_num
            content.append(temp)
    # 已发布未被接单
    sql2 = "(SELECT * FROM task t1 where (SELECT COUNT(1) FROM task_order t2 where t1.tid=t2.tid)=0 AND t1.sid='%s')" % (sid)
    rows = tools.selectOpt(sql2)
    if rows:
        for i in range(len(rows)):
            temp = {}
            temp['tid'] = rows[i]['tid']
            temp['type'] = rows[i]['type']
            temp['deadline'] = rows[i]['deadline']
            temp['reward'] = rows[i]['reward']
            temp['quantity'] = rows[i]['quantity']
            acc_num = compute_accept_num(rows[i]['tid'])
            temp['accept_num'] = acc_num
            content.append(temp)
    if len(content) == 0:
        msg += "no record"
        return 200, msg, 0, content
    else:
        msg += "successful"
        number = len(content)
        return 200, msg, number, content


# 奶牛端和学生端查看具体任务详情
# used in module/user/task/<int:id>
def task_model(id):
    # 蔡湘国
    tid = id
    msg = ""
    # 对应参数为空的情况
    if id == None:
        msg += "id can't be empty"
        return 400, msg, []
    # 数据库中查不到对应的任务tid, 即任务不存在
    if not select_task_by_tid(tid):
        msg += "refused because of maybe_error_tid"
        return 400, msg, []

    sql = "SELECT * FROM task WHERE tid='%d'" % (tid)
    rows = tools.selectOpt(sql)
    if rows:
        content = {}
        content['tid'] = rows[0]['tid']
        content['type'] = rows[0]['type']
        content['description'] = rows[0]['description']
        content['detail'] = rows[0]['detail']
        content['deadline'] = rows[0]['deadline']
        content['phone_num'] = rows[0]['phone_num']
        content['wechat'] = rows[0]['wechat']
        msg += "successful"
        return 200, msg, content
    else:
        msg += "no record"
        content = None
        return 200, msg, content


# 学生端查看已完成的任务（注意是学生端标记任务完成，而不是奶牛端整个任务结束，奶牛端在学生标记任务完成之后还要进行审核）
# used in module/user/student_task_done
def student_task_done_model(account):
    # 陈笑儒
    sid = session.get('sid')
    content = []
    msg = ""

    sql = "(SELECT * FROM task t1,task_order t2 where " \
          "t1.tid=t2.tid and t2.sid='%s' and accept_status=1)" % (sid)
    rows = tools.selectOpt(sql)
    if rows:
        for i in range(len(rows)):
            temp = {}
            temp['tid'] = rows[i]['tid']
            temp['type'] = rows[i]['type']
            temp['sid'] = rows[i]['sid']
            temp['deadline'] = rows[i]['deadline']
            temp['reward'] = rows[i]['reward']
            temp['reward_status'] = rows[i]['reward_status']
            content.append(temp)
        msg += "successful"
        number = len(content)
        return 200, msg, number, content
    else:
        msg += "no record"
        return 200, msg, 0, content


# 学生端查看正在进行中的任务
# used in module/user/student_task_in_progress
def student_task_in_progress_model(account):
    # 陈笑儒
    sid = session.get('sid')
    content = []
    msg = ""

    sql = "(SELECT * FROM task t1,task_order t2 where " \
          "t1.tid=t2.tid and t2.sid='%s' and accept_status=0)" % (sid)
    rows = tools.selectOpt(sql)
    if rows:
        for i in range(len(rows)):
            temp = {}
            temp['tid'] = rows[i]['tid']
            temp['type'] = rows[i]['type']
            temp['sid'] = rows[i]['sid']
            temp['deadline'] = rows[i]['deadline']
            temp['reward'] = rows[i]['reward']
            temp['reward_status'] = rows[i]['reward_status']
            content.append(temp)
        msg += "successful"
        number = len(content)
        return 200, msg, number, content
    else:
        msg += "no record"
        return 200, msg, 0, content


# 学生端挑选任务，查看到目前系统所有的其他类型任务（要做分页）
# used in module/user/select_task?offset={value}&number={value}
def select_task_model(account):
    # 陈笑儒
    offset = request.args.get("offset")
    number = request.args.get("number")
    sid = session.get('sid')

    content = []
    msg = ""

    if offset is None or number is None or not (offset.isdigit() and number.isdigit()):
        msg += "invalid parameter"
        number = 0
        return 400, msg, number, content

    offset = int(offset)
    number = int(number)

    sql = "SELECT * FROM task where tid not in" \
          "(SELECT tid FROM task_order where sid = '%s')" % (sid)
    rows = tools.selectOpt(sql)
    if rows:
        for i in range(offset, min(len(rows), offset + number)):
            temp = {}
            temp['tid'] = rows[i]['tid']
            temp['type'] = rows[i]['type']
            temp['description'] = rows[i]['description']
            temp['quantity'] = rows[i]['quantity']
            temp['reward'] = rows[i]['reward']
            content.append(temp)
        msg += "successful"
        number = len(content)
        return 200, msg, number, content
    else:
        msg += "no record"
        return 200, msg, 0, content


# 审核投诉单
# used in module/user/complaint_handle
def complaint_handle_model(account):
    # todo
    # 唐育涛
    pass


# 查看投诉单
# used in module/user/get_complaint/<int:cid>
def get_complaint_model(cid):
    # todo
    # 唐育涛
    pass


# 奶牛端和学生端投诉（发送邮件告知被投诉者）
# used in module/user/complaint
def complaint_model(account):
    # todo
    # 唐育涛
    pass


# 学生端放弃任务（需求量回退一步,邮件告知任务发起者 ）
# used in module/user/task_give_up
def task_give_up_model(account):
    # 陈笑儒
    tid = account.get('tid', None)
    sid = session.get('sid')

    msg = ""
    if tid is None:
        msg += "Illegal_parameter"
        return 400, msg
    if not isinstance(tid, int):
        msg += "tid_must_be_int"
        return 400, msg

    if not select_task_by_tid(tid):
        msg += "no this task"
        return 400, msg

    sql = "SELECT * FROM task_order WHERE tid='%d' and sid='%s'" % (tid, sid)
    rows = tools.selectOpt(sql)
    if not rows:
        msg += "you haven't applied this task"
        return 400, msg
    elif rows[0]['accept_status'] == 1:
        msg += "you have already finished this task"
        return 400, msg

    sql = """UPDATE task SET quantity = quantity+1 WHERE tid="%d";""" % (tid)
    tools.modifyOpt(sql)
    sql = """DELETE FROM task_order WHERE tid="%d" and sid="%s";""" % (tid, sid)
    tools.modifyOpt(sql)

    # email_publisher = select_email_by_sid(p_sid)
    # sent_email_to_task_publisher(email_publisher, tid, 3)

    msg += "successful"
    return 200, msg


# 奶牛端删除任务
# used in module/user/delete_task
def delete_task_model(account):
    # 蔡湘国
    tid = account.get('tid', None)
    msg = ""
    # 对应参数为空的情况
    if tid == None:
        msg += "tid can't be empty"
        return 400, msg
    # 数据库中查不到对应的任务tid, 即任务不存在
    if not select_task_by_tid(tid):
        msg += "refused because of maybe_error_tid"
        return 400, msg
    # 查看该用户是否是该任务创始人
    if not session['sid'] == get_sid_by_tid(tid):
        msg += "refused because no authority"
        return 400, msg
    # 查看是否还存在任务未审核
    if get_no_verify_num_by_tid(tid) != 0:
        msg += "refused because there are still some task no verify"
        return 400, msg

    # 返还剩下的钱
    verify_num = get_verify_num_by_tid(tid)
    quantity = get_quantity_by_tid(tid)
    reward = get_reward_by_tid(tid)
    return_monty = (quantity - verify_num) * reward
    add_balance_by_sid(session['sid'], return_monty)
    session['balance'] = session['balance'] + return_monty
    # 删除任务
    sql = """DELETE FROM task_order WHERE tid="%d";""" % (tid)
    tools.modifyOpt(sql)
    sql2 = """DELETE FROM task WHERE tid="%d";""" % (tid)
    tools.modifyOpt(sql2)

    msg += "successful"
    return 200, msg


# 奶牛端审核任务(审核成功与否都将通过邮箱告知任务接受者)
# used in module/user/task_verify
def task_verify_model(account):
    # 蔡湘国
    # 需要学生端接受问卷，所以未测试
    # 解析json得到想要的参数
    tid = account.get('tid', None)
    sid = account.get('sid', None)
    verify = account.get('verify', None)
    email = select_email_by_sid(sid)
    msg = ""

    # 判断各种异常情况
    # 对应参数为空的情况
    if tid == None or sid == None or verify == None:
        msg += "refused because of Illegal_parameter"
        return 400, msg
    # 数据库中查不到对应的任务id, 即任务不存在
    if not select_task_by_tid(tid):
        msg += "refused because of maybe_error_tid"
        return 400, msg
    # 接单表查不到对应任务
    if not get_task_by_id(tid, sid):
        msg += "can't find task in task_order"
        return 400, msg
    # 原来已经审核成功
    if get_verify_state_by_id(tid, sid) == 1:
        msg += "already verify successful"
        return 200, msg
    # 审核成功更新数据库
    sql = """UPDATE task_order SET verify=%d WHERE tid=%d AND sid="%s";""" % (
        verify, tid, sid)
    tools.modifyOpt(sql)
    # sent_email_to_task_receiver(email, tid, verify+1)
    # 现审核成功支付费用
    money = get_reward_by_tid(tid)
    if verify == 1:
        add_balance_by_sid(sid, money)
        sql = """UPDATE task_order SET reward_status=%d WHERE tid=%d AND sid="%s";""" % (
            1, tid, sid)
        tools.modifyOpt(sql)
    # 审核不通过 quantity + 1回退
    if verify == 2:
        increase_quantity_by_tid(tid)
    msg += "successful"
    return 200, msg


# 奶牛端联系接单者（获取接单者部分用户信息）
# used in module/user/contact_receiver/<int:sid>
def contact_receiver_model(sid):
    # 蔡湘国
    content = {}
    msg = ""
    sql = "SELECT * FROM accounts WHERE sid='%s'" % (sid)
    rows = tools.selectOpt(sql)
    if rows:
        row = rows[0]
        content['name'] = row['name']
        content['sid'] = row['sid']
        content['phone_num'] = row['phone_num']
        content['email'] = row['email']
        code = 200
        msg += "successful"
        return code, msg, content
    else:
        code = 400
        msg += "sid hasn't registered!"
        return code, msg, content

