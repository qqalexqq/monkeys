"""Application management utility script."""
import os
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

import models
from app import create_app
from models import db

app = create_app(
    __name__, os.environ.get('APP_SETTINGS', 'config.DevelopmentConfig')
)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
