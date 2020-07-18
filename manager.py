from app import create_app
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from app import db
from eventlet import wsgi
import eventlet

app = create_app()
manager = Manager(app)
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':

    wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
    manager.run()
