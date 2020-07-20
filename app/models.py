# -*- coding: utf-8 -*-
from datetime import datetime
from . import db
from . import login_manager
from flask_login import UserMixin
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class Permission:
    """
    权限制，高权限肯定拥有低权限。比如WRITE，肯定拥有COMMENT
    """
    COMMENT = 1
    WRITE = 2
    MODERATE = 4
    ADMIN = 18


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_role():
        roles = {
            'User': [Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator':[Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = "User"
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role= Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def remvove_permisson(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def has_permission(self, perm):
        # 因为权限为2的次幂，叠加，值为2的n-1次方
        # 任何2的n-1次方内的值，与其位运算得本身
        return self.permissions & perm == perm

    def reset_permission(self):
        self.permissions = 0

    def __str__(self):
        return '<Role> %r' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    about_me = db.Column(db.Text())
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=1)
    articles = db.relationship('Article', backref='user')
    comments = db.relationship('Comment', backref='user')
    reply = db.relationship('Reply', backref='user')

    @staticmethod
    def on_created(target, value, oldvalue, initiator):
        target.role = Role.query.filter_by(name='Guests').first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
            print(data)
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        print("passwd:%s" % new_password)
        db.session.add(user)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.role.has_permission(Permission.ADMIN)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    hit_numers = db.Column(db.Integer, nullable=False, default=0)
    comment_numbers = db.Column(db.Integer, nullable=False, default=0)
    body_html = db.Column(db.String)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # 每篇文章都有一个作者，一一对应关系,在jinja模板中可以使用article.user.name获取用户名
    auther_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 每篇文章可以有n条评论，一对多关系
    comments = db.relationship('Comment', backref='article')

    @staticmethod
    def on_body_changed(target, value, oldvalue, initiator):
        if value is None or (value is ''):
            target.body_html = ''
        else:
            target.body_html = markdown(value)


db.event.listen(Article.body, 'set', Article.on_body_changed)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    auther_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Reply', backref='comment')


class Reply(db.Model):
    __tablename__ = 'reply'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    auther_id = db.Column(db.Integer, db.ForeignKey('user.id'))
