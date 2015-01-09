"""Monkeys app exercise."""
import os
import logging
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.menu import Menu

import views


def create_app(name_handler, config_object):
    """Application factory."""

    app = Flask(name_handler)
    app.config.from_object(config_object)

    # Imports db and all models-related things
    from models import db

    db.init_app(app)
    Bootstrap(app)
    Menu(app)

    app.register_blueprint(views.bp_monkey)

    if os.environ.get('HEROKU') is not None:
        stream_handler = logging.StreamHandler()

        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

    return app
