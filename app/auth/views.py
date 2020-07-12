# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for
from flask import Blueprint
from flask_login import login_user, logout_user
from app.auth.forms import LoginForm, RegisterForm
from app.models import User
from app import db

auth = Blueprint('auth', __name__)


@auth.route("/")
def index():
    return render_template("index.html", title="caesar博客")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data, password=form.password.data).first()
        if user is not None:
            login_user(user)
            return redirect(url_for('auth.index'))

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
        return redirect(url_for('auth.login'))
    return render_template("register.html", title=u'注册', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
