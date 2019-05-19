#coding: utf8

# 从flask框架中导入Flask类
from flask import Flask, url_for, redirect

# 传入__name__初始化一个Flask实例
app = Flask(__name__)

# app.route装饰器映射URL和执行的函数。这个设置将根URL映射到了hello_world函数上
@app.route('/')
def hello_world():
  print(url_for('hello_worlssd'))
  return 'Hello World!'

@app.route('/fff')
def fdf():
    return 'Hello wwwww!'

@app.route('/fd')
def hello_worlssd():
    return redirect(url_for('fdf'))

@app.route('/article/<id>')
def article(id):
    return u'你请求的参数是：%s' % id

if __name__ == '__main__':
    # 运行本项目，host=0.0.0.0可以让其他电脑也能访问到该网站，port指定访问的端口。默认的host是127.0.0.1，port为5000
    app.run(host='127.0.0.1', port=9000)

