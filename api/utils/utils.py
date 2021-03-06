import json
from functools import wraps
from flask import current_app, session, request
from api import *
import smtplib


# 将key:value参数转成json形式
# used in every response
def python_object_to_json(**kwargs):
    python2json = {}
    for i in kwargs.items():
        python2json[i[0]] = i[1]
    json_str = json.dumps(python2json)
    return json_str


# 确认是否登录的函数
# used in all api needs login before
def login_required_mine(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get('phone_num'):
            code = 401
            msg = "not login"
            return python_object_to_json(code=code, msg=msg)
        return func(*args, **kwargs)

    return decorated_view


"""
邮箱函数
"""
# eg1：给用户发送问卷审核成功的信息
# sent_email_answer_message('1415629749@qq.com', 26, 1)
# eg2：给任务发布者发布任务状态的信息
# sent_email_to_task_publisher('1415629749@qq.com', 26, 3)
# eg2：给任务接受者发布任务信息
# sent_email_to_task_receiver('1415629749@qq.com', 26, 3)


# 这个方法只跟问卷有关
# 答卷审核发送邮件
def sent_email_answer_message(to, qid, verify):
    # 163邮件
    # 1> 配置邮箱SMTP服务器的主机地址，将来使用这个服务器收发邮件。
    host = 'smtp.163.com'
    # # 2> 配置服务的端口，默认的邮件端口是25.
    port = '25'
    # # 3> 指定发件人和收件人。
    from_email = 'xifen321@163.com'
    # # 4> 邮件标题
    subject = '闲钱宝 问卷审核信息'
    # # 5> 邮件内容
    content = ''
    # # 创建邮件发送对象
    # # 普通的邮件发送形式
    # # 数据在传输过程中会被加密。
    # # qq邮箱则需要加密 采用465端口
    # # stmp_obj = smtplib.SMTP_SSL(host=host)
    # # stmp_obj = smtplib.SMTP_SSL()
    stmp_obj = smtplib.SMTP()

    # # 需要进行发件人的认证，授权。
    # # stmp_obj就是一个第三方客户端对象
    stmp_obj.connect(host=host, port=port)

    # # 如果使用第三方客户端登录，要求使用授权码，不能使用真实密码，防止密码泄露。
    res = stmp_obj.login(user=from_email, password='qq1415629749')
    if not res:
        return False
    if verify == 1:
        content = '恭喜您，您在闲钱宝关于问卷编号为'+ str(qid) + '的回答已经通过审核，问卷赏金已经存进您的账户'
    if verify == 0:
        content = '非常遗憾，您在闲钱宝关于问卷编号为' + str(qid) + '的回答未能通过审核，请注意规范答题！'
    msg = '\n'.join(['From: {}'.format(from_email), 'To: {}'.format(to+','+from_email), 'Subject: {}'.format(subject), '', content ])
    stmp_obj.sendmail(from_addr=from_email, to_addrs=[to, from_email], msg=msg.encode('utf-8'))
    return True


# 这个方法是发给任务发布者，非问卷逻辑采用这个方法发送，需要添加内容就改一下content
# 接受任务给任务发布者发邮件
# to 表示收件方邮件地址 可以是qq邮箱 163邮箱 126邮箱 等等各类邮箱
# qid 表示任务的内容的编号
# content_num 表示要发给用户的内容的选择
def sent_email_to_task_publisher(to, tid, content_num):
    # 163邮件
    # 1> 配置邮箱SMTP服务器的主机地址，将来使用这个服务器收发邮件。
    host = 'smtp.163.com'
    # # 2> 配置服务的端口，默认的邮件端口是25.
    port = '25'
    # # 3> 指定发件人和收件人。
    from_email = 'xifen321@163.com'
    # # 4> 邮件标题
    subject = '闲钱宝 任务信息提醒'
    # # 5> 邮件内容
    content = ''
    # # 创建邮件发送对象
    # # 普通的邮件发送形式
    # # 数据在传输过程中会被加密。
    # # stmp_obj = smtplib.SMTP_SSL(host=host)
    stmp_obj = smtplib.SMTP()

    # # 需要进行发件人的认证，授权。
    # # stmp_obj就是一个第三方客户端对象
    stmp_obj.connect(host=host, port=port)
    # # 如果使用第三方客户端登录，要求使用授权码，不能使用真实密码，防止密码泄露。
    res = stmp_obj.login(user=from_email, password='qq1415629749')

    if not res:
        return False

    # content_num == 1 ,提示任务发布者已经有人接受任务
    if content_num == 1:
        content = '任务状态提醒：您在闲钱宝关于任务ID为' + str(tid) + '的任务已经有人接受任务，对方将第一时间联系您，请注意！详细情况登陆闲钱宝查看'
    # content_num == 2 ,提示任务发布者已经有人完成任务，注意审核
    if content_num == 2:
        content = '任务状态提醒：您在闲钱宝关于任务ID为' + str(tid) + '的任务已经完成任务，请注意登陆系统进行任务审核！详细情况登陆闲钱宝查看'
    # content_num == 3 ,提示任务发布者对方取消任务，注意任务状态
    if content_num == 3:
        content = '任务状态提醒：您在闲钱宝关于任务ID为' + str(tid) + '的任务对方已经取消了任务，您的任务状态重新变更为发布中，请注意！详细情况登陆闲钱宝查看'
    # content_num == 4 ,注册时发送邮箱验证码
    if content_num == 4:
        content = '验证码提醒：您在闲钱宝的4位注册验证码为 ' + str(tid) + ' 请填写正确的验证码以验证邮箱！详细情况登陆闲钱宝查看！'
    # 接下去有什么要回复的内容记得在这里添加

    msg = '\n'.join(['From: {}'.format(from_email), 'To: {}'.format(to+','+from_email), 'Subject: {}'.format(subject), '', content])
    stmp_obj.sendmail(from_addr=from_email, to_addrs=[to, from_email], msg=msg.encode('utf-8'))
    return True


# 这个方法是发给任务接受者，非问卷逻辑采用这个方法发送，需要添加内容就改一下content
# 接受任务给任务发布者发邮件
# to 表示收件方邮件地址 可以是qq邮箱 163邮箱 126邮箱 等等各类邮箱
# qid 表示任务的内容的编号
# content_num 表示要发给用户的内容的选择
def sent_email_to_task_receiver(to, tid, content_num):
    # 163邮件
    # 1> 配置邮箱SMTP服务器的主机地址，将来使用这个服务器收发邮件。
    host = 'smtp.163.com'
    # # 2> 配置服务的端口，默认的邮件端口是25.
    port = '25'
    # # 3> 指定发件人和收件人。
    from_email = 'xifen321@163.com'
    # # 4> 邮件标题
    subject = '闲钱宝 任务信息提醒'
    # # 5> 邮件内容
    content = ''
    # # 创建邮件发送对象
    # # 普通的邮件发送形式
    # # 数据在传输过程中会被加密。
    # # stmp_obj = smtplib.SMTP_SSL(host=host)
    stmp_obj = smtplib.SMTP()

    # # 需要进行发件人的认证，授权。
    # # stmp_obj就是一个第三方客户端对象
    stmp_obj.connect(host=host, port=port)

    # # 如果使用第三方客户端登录，要求使用授权码，不能使用真实密码，防止密码泄露。
    res = stmp_obj.login(user=from_email, password='qq1415629749')
    if not res:
        return False

    # content_num == 1 ,提示任务接受者接受任务记得完成
    if content_num == 1:
        content = '任务提醒！您在闲钱宝上接受了任务编号为：' + str(tid) + '的任务，请注意第一时间联系任务发布者完成任务！详细情况登陆闲钱宝查看'
    # content_num == 2 ,提示任务接受者任务审核成功，赏金到账
    if content_num == 2:
        content = '恭喜您！在闲钱宝关于任务ID为' + str(tid) + '的任务审核通过，赏金已经发布到您的账户，请注意查收！详细情况登陆闲钱宝查看'
    # content_num == 3 ,提示任务接受者任务失败，没有赏金
    if content_num == 3:
        content = '非常抱歉！您在闲钱宝关于任务ID为' + str(tid) + '的任务未能通过审核，可以联系任务发布者解释原因，有其他不满可以进行投诉！详细情况登陆闲钱宝查看'
    # 接下去有什么要回复的内容记得在这里添加

    msg = '\n'.join(['From: {}'.format(from_email), 'To: {}'.format(to+','+from_email), 'Subject: {}'.format(subject), '', content])
    stmp_obj.sendmail(from_addr=from_email, to_addrs=[to, from_email], msg=msg.encode('utf-8'))
    return True


# 这个方法是投诉相关逻辑，投诉以及超级管理员审核都用这一个方法，需要添加内容就改一下content
# 投诉受理给投诉发起人发消息，投诉成功给投诉人和被投诉人发消息，投诉失败给投诉人发消息
# to 表示收件方邮件地址 可以是qq邮箱 163邮箱 126邮箱 等等各类邮箱
# qid 表示任务的内容的编号
# content_num 表示要发给用户的内容的选择
def sent_email_about_compliant(to, tid, sid, content_num):
    # 163邮件
    # 1> 配置邮箱SMTP服务器的主机地址，将来使用这个服务器收发邮件。
    host = 'smtp.163.com'
    # # 2> 配置服务的端口，默认的邮件端口是25.
    port = '25'
    # # 3> 指定发件人和收件人。
    from_email = 'xifen321@163.com'
    # # 4> 邮件标题
    subject = '闲钱宝 任务信息提醒'
    # # 5> 邮件内容
    content = ''
    # # 创建邮件发送对象
    # # 普通的邮件发送形式
    # # 数据在传输过程中会被加密。
    # # stmp_obj = smtplib.SMTP_SSL(host=host)
    stmp_obj = smtplib.SMTP()

    # # 需要进行发件人的认证，授权。
    # # stmp_obj就是一个第三方客户端对象
    stmp_obj.connect(host=host, port=port)
    # # 如果使用第三方客户端登录，要求使用授权码，不能使用真实密码，防止密码泄露。
    res = stmp_obj.login(user=from_email, password='qq1415629749')
    if not res:
        return False

    # content_num == 1 ,提示投诉已经受理
    if content_num == 1:
        content = '投诉受理！您在闲钱宝上关于任务ID为' + str(tid) + '的任务发起了对' + str(sid) + '的投诉，投诉已经受理，我们会在24小时内完成审核，敬请留意相关消息！'
    # content_num == 2 ,投诉成功
    if content_num == 2:
        content = '投诉成功！您在闲钱宝上关于任务ID为' + str(tid) + '的任务发起了对' + str(sid) + '的投诉，投诉审核成功，系统对被投诉者做出了扣除12点信誉积分的惩罚！'
    # content_num == 3 ,投诉失败
    if content_num == 3:
        content = '投诉失败！您在闲钱宝上关于任务ID为' + str(tid) + '的任务发起了对' + str(sid) + '的投诉，投诉缺乏相关证据，审核不予以通过，请提交更多的相关信息！'
    # content_num == 4 ,被投诉成功
    if content_num == 4:
        content = '投诉告知！您在闲钱宝上关于任务ID为' + str(tid) + '的任务受到了' + str(sid) + '的投诉，投诉审核通过，对您做出了扣除12点信誉积分的处罚！请注意任务规范！'
    # 接下去有什么要回复的内容记得在这里添加

    msg = '\n'.join(['From: {}'.format(from_email), 'To: {}'.format(to+','+from_email), 'Subject: {}'.format(subject), '', content])
    stmp_obj.sendmail(from_addr=from_email, to_addrs=[to, from_email], msg=msg.encode('utf-8'))
    return True
