# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache

redis_cache = Cache()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)

    Bootstrap(app)

    app.config.from_pyfile('config')
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///data.sqlite'
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    db.init_app(app)
    redis_cache.init_app(app)
    login_manager.init_app(app)
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

