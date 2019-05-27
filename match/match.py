import re
import random
import hashlib


# 匹配手机号 ：用来匹配手机号是否符合格式
def match_phone(phone_num):
    ret = re.match(r"^1(?:3\d{3}|5[^4\D]\d{2}|8\d{3}|7(?:[35678]\d{2}|4(?:0\d|1[0-2]|9\d))|9[189]\d{2}|66\d{2})\d{6}$", phone_num)
    if ret:
        return True
    else:
        return False


# 匹配密码 ：用于匹配前端传来的密码是否符合格式
def match_password(password):
    ret = re.match(r"^[A-F0-9]{128}$", password)
    if ret:
        return True
    else:
        return False


def match_sid(sid):
    ret = re.match(r"^[0-9]{8}$", sid)
    if ret:
        return True
    else:
        return False

# 为每个用户生成26位随机盐值，盐值用于密码加密
# 每个用户创建时调用这个函数，并将盐值存于后端数据库
def random_code(num):
    h = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    salt = ''
    for i in range(num):
        salt += random.choice(h)

    return salt


# 密码盐值加密
# 暂定的加密逻辑为password = tolower(sha512(password))，这部分由前端负责
# password = sha512(password+salt)，这部分由后端负责 将加密后的密码存进数据库
def hash_password(password,salt):
    if salt == "":
        salt = random_code(26)
    h = hashlib.sha512()
    h.update(bytes(password + salt, encoding='utf-8'))
    pawd_result = h.hexdigest()
    return pawd_result


''' 
def main():
    password = "12345678911234567891123456789112345678911234567891123456789112345678911234567891123456789112345678911234567891123456789112345678"
    if not match_password(password):
        print("密码类型错误")

    salt = random_code(26)
    phone = "13128284774"
    if not match_phone(phone):
        print("手机号错误")

    password1 = hash_password(password, "xbiLcSDI1G5FvFOpvDknkP8ZO4")
    print("加密前的密码：" + password)
    print("用于加密的盐值：" + "xbiLcSDI1G5FvFOpvDknkP8ZO4")
    print("加密后的密码：" + password1)
    print("结果应该为：" + "8a57d06e7c951429878ea49ca3b24a9d8568542e2449814034e8c75d546b809aeaed4bacd0c71cb711d0a56e8c4addd92c060abac9175f9ccc912e7327a73245")

    password1 = hash_password(password, salt)
    print("加密前的密码"+password)
    print("用于加密的盐值" + salt)
    print("加密后的密码"+password1)


if __name__ == '__main__':
    main()
'''