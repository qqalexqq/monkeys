from flask import Blueprint, render_template
from flask.ext import menu

bp_monkey = Blueprint('monkey', __name__)


# '/monkey' route goes first because 'menu' module takes last route's url
@bp_monkey.route('/monkey')
@bp_monkey.route('/')
@menu.register_menu(bp_monkey, '.monkeys_list', 'Monkeys list', order=0)
def monkeys_list():
    return render_template('monkeys_list.html')


@bp_monkey.route('/monkey/add')
@menu.register_menu(bp_monkey, '.add_monkey', 'Add monkey', order=1)
def add_monkey():
    return render_template('monkeys_list.html')
