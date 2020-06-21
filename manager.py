from app import create_app
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from app import db

app = create_app()
manager = Manager(app)
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    app.run(debug=True)
    manager.run()
