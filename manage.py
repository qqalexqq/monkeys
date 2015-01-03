"""Application management utility script."""
import os
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

import models
from app import create_app
from models import db

app = create_app(
    __name__, os.environ.get('APP_SETTINGS', 'config.DevelopmentConfig')
)

migrate = Migrate(app, db)
manager = Manager(app)


@manager.command
def test():
    """Tests runner command."""
    import pytest

    return pytest.main(['test', '--verbose'])


def mk_context():
    """Creating a shell context."""
    return dict(app=app, db=db, models=models)

manager.add_command('shell', Shell(make_context=mk_context, use_ipython=True))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
