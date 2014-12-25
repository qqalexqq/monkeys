"""Monkeys app exercise."""
import os
from flask import Flask

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS', 'config.TestingConfig'))

# We run app only when it's really needed
if __name__ == '__main__':
    app.run()
