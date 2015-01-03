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


@pytest.yield_fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
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
    db.session.begin_nested()

    yield db.session

    db.session.rollback()
