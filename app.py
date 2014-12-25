"""Monkeys app exercise."""
from flask import Flask

app = Flask(__name__)

# We run app only when it's really needed
if __name__ == '__main__':
    app.run()
