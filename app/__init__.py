# -*- coding: utf-8 -*-
import os

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    app.config.from_pyfile('config')
    register_errors(app)
    db.init_app(app)
    login_manager.init_app(app)
    app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
    mail.init_app(app)
    from app.auth.views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    from app.main.views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.template_test('current_link')
    def is_current_link(link):
        return link == request.path

    @app.template_filter('strftime')
    def datetime_format(date):
        return date.strftime("%Y-%m-%d %H:%M:%S")

    return app


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500