from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, current_user
from flask_wtf.form import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Length, DataRequired, Optional
from teach.User_dal import user_dal

app = Flask(__name__)

# 项目中设置flask_login
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '234rsdf34523rwsf'


# flask_wtf表单
class LoginForm(FlaskForm):
    username = StringField('手机号：', validators=[DataRequired(), Length(1, 30)])
    password = PasswordField('密码：', validators=[DataRequired(), Length(1, 64)])
    remember_me = BooleanField('记住密码', validators=[Optional()])


'''
登录函数，首先实例化form对象
然后通过form对象验证post接收到的数据格式是否正确
然后通过login_auth函数，用username与password向数据库查询这个用户，并将状态码以及对象返回
判断状态码，如果正确则将对象传入login_user中，然后就可以跳转到正确页面了
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        result = user_dal.User_Dal.login_auth(username, password)
        model = result[1]
        if result[0]['isAuth']:
            login_user(model)
            print('登陆成功')
            print(current_user.username)  # 登录成功之后可以用current_user来取该用户的其他属性，这些属性都是sql语句查来并赋值给对象的。
            return redirect('/t')
        else:
            print('登陆失败')
            return render_template('login.html', formid='loginForm', action='/login', method='post', form=form)
    return render_template('login.html', formid='loginForm', action='/login', method='post', form=form)


'''
load_user是一个flask_login的回调函数，在登陆之后，每访问一个带Login_required装饰的视图函数就要执行一次，
该函数返回一个用户对象，通过id来用sql语句查到的用户数据，然后实例化一个对象，并返回。
'''
@login_manager.user_loader
def load_user(id):
    return user_dal.User_Dal.load_user_byid(id)


# 登陆成功跳转的视图函数
@app.route('/t')
@login_required
def hello_world():
    print('登录跳转')
    return 'Hello World!'


# 随便写的另一个视图函数
@app.route('/b')
@login_required
def hello():
    print('视图函数b')
    return 'Hello b!'




if __name__ == '__main__':
    app.run()
