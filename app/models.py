# -*- coding: utf-8 -*-
from datetime import datetime
from . import db
from . import login_manager
from flask_login import UserMixin
from markdown import markdown
from sqlalchemy.dialects.mysql import DATETIME

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    users = db.relationship('User', backref='role')

    @staticmethod
    def seed():
        db.session.add_all(map(lambda r: Role(name=r), ['Guests', 'Administrators']))
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    articles = db.relationship('Article', backref='user')
    comments = db.relationship('Comment', backref='user')
    reply = db.relationship('Reply', backref='user')

    @staticmethod
    def on_created(target, value, oldvalue, initiator):
        target.role = Role.query.filter_by(name='Guests').first()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    body_html = db.Column(db.String)
    created = db.Column(DATETIME(fsp=6), index=True, default=datetime.utcnow)
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
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    auther_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Reply', backref='comment')


class Reply(db.Model):
    __tablename__ = 'reply'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    auther_id = db.Column(db.Integer, db.ForeignKey('user.id'))
