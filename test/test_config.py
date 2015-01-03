import os
from hamcrest import *

from app import create_app


def test_production_config():
    app = create_app(__name__, 'config.ProductionConfig')

    assert_that(app.config['DEBUG'], is_(False))
    assert_that(app.config['TESTING'], is_(False))
    assert_that(
        app.config['SQLALCHEMY_DATABASE_URI'],
        equal_to(os.environ['DATABASE_URL'])
    )
    assert_that(app.config['SQLALCHEMY_ECHO'], is_(False))
