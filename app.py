"""Monkeys app exercise."""
import os
from flask import Flask


def create_app(name_handler, config_object):
    """Application factory."""

    app = Flask(name_handler)
    app.config.from_object(config_object)

    # Imports db and all models-related things
    from models import db

    db.init_app(app)

    return app


# We run app when this script is executed directly
if __name__ == '__main__':
    app = create_app(
        __name__, os.environ.get('APP_SETTINGS', 'config.DevelopmentConfig')
    )

    app.run()
