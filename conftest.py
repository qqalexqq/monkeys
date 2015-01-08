import pytest
from app import create_app
from models import db as _db


@pytest.yield_fixture(scope='session')
def app(request):
    """Session-wide test application."""
    _app = create_app(__name__, 'config.TestingConfig')

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app

    # Teardown
    ctx.pop()


# Function-wide because 'bind' parameter doesn't work in F-SQLA
# https://github.com/mitsuhiko/flask-sqlalchemy/blob/2.0
# /flask_sqlalchemy/__init__.py#L160
@pytest.yield_fixture(scope='function')
def db(app, request):
    """Function-wide test database."""
    _db.create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True
    )
    _db.drop_all()
    _db.create_all()

    yield _db

    # Teardown
    _db.drop_all()


@pytest.yield_fixture(scope='function')
def session(db, request):
    """Function-wide test database session"""
    yield db.session

    # Teardown
    db.session.close()
