# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash
from flask import Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from app.auth.forms import LoginForm, RegisterForm, \
    ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm
from app.models import User
from app import db
from ..utils.email import send_email

auth = Blueprint('auth', __name__)


# (1) 用户已登录（current_user.is_authenticated 的值为 True）。
# (2) 用户的账户还未确认。
# (3) 请求的 URL 不在auth蓝本中，而且也不是对静态文件的请求
# 转发到未认证页面进行认证
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route("/")
def index():
    return render_template("index.html", title="caesar博客")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('auth.index'))
        else:
            flash("用户名或密码错误")

    return render_template('login.html',
                           title=u'登录',
                           form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(name=form.username.data,
                    password=form.password.data,
                    email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '账号认证',
                   'auth/email/confirm', user=user, token=token)
        return redirect(url_for('auth.login'))
    return render_template("register.html", title=u'注册', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
    else:
        flash('链接过期')
    return redirect(url_for('main.index'))


@auth.route('/password_change', methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('密码更新成功')
            return redirect(url_for('main.index'))
        else:
            flash('无效的密码')
    return render_template("auth/change_email.html", title="密码管理", form=form)


@auth.route('/resend_confirmation', methods=['GET'])
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '账号认证',
               'auth/email/confirm', user=current_user, token=token)
    return redirect(url_for('main.index'))


@auth.route('/reset', methods=['GET', 'POST'])
def passwd_reset():
    form = PasswordResetRequestForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重置密码',
                       'auth/email/reset_password',
                       user=user, token=token)
            flash("请登录邮箱重置密码")
            return redirect(url_for('auth.login'))
    return render_template("auth/reset_password.html", form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('密码重置成功')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
