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
    # todo
    pass


# 学生端申请任务（需求量从数据库调用减1，发送邮件给发起者和接收者，申请接单接单状态accept_status=0）
# used in module/user/apply
def apply_model(account):
    # todo
    pass


# 奶牛端查看已完成的任务（注意是学生端标记任务完成，而不是奶牛端整个任务结束，奶牛端在学生标记任务完成之后还要进行审核）
# used in module/user/provider_task_done
def provider_task_done_model(account):
    # todo
    pass


# 奶牛端查看正在进行中的任务（包括已接单但未完成，和发布中未被接单的任务）
# used in module/user/provider_task_in_progress
def provider_task_in_progress_model(account):
    # todo
    pass


# 奶牛端和学生端查看具体任务详情
# used in module/user/task/<int:id>
def task_model(id):
    # todo
    pass


# 学生端查看已完成的任务（注意是学生端标记任务完成，而不是奶牛端整个任务结束，奶牛端在学生标记任务完成之后还要进行审核）
# used in module/user/student_task_done
def student_task_done_model(account):
    # todo
    pass


# 学生端挑选任务，查看到目前系统所有的其他类型任务（要做分页）
# used in module/user/select_task?offset={value}&number={value}
def select_task_model(account):
    # todo
    pass


# 审核投诉单
# used in module/user/complaint_handle
def complaint_handle_model(account):
    # todo
    pass


# 查看投诉单
# used in module/user/get_complaint/<int:cid>
def get_complaint_model(cid):
    # todo
    pass


# 奶牛端和学生端投诉（发送邮件告知被投诉者）
# used in module/user/complaint
def complaint_model(account):
    # todo
    pass


# 学生端放弃任务（需求量回退一步,邮件告知任务发起者 ）
# used in module/user/task_give_up
def task_give_up_model(account):
    # todo
    pass


# 奶牛端删除任务
# used in module/user/delete_task
def delete_task_model(account):
    # todo
    pass


# 奶牛端审核任务(审核成功与否都将通过邮箱告知任务接受者)
# used in module/user/task_verify
def task_verify_model(account):
    # todo
    pass


# 奶牛端联系接单者（获取接单者部分用户信息）
# used in module/user/contact_receiver/<int:sid>
def contact_receiver_model(sid):
    # todo
    pass
