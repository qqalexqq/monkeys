from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, abort
)
from flask.ext import menu
from sqlalchemy.orm import aliased
from sqlalchemy.orm.strategy_options import Load

from models import *
from forms import *

bp_monkey = Blueprint('monkey', __name__)


# '/monkey' route goes first because 'menu' module takes last route's url
@bp_monkey.route('/monkey')
@bp_monkey.route('/')
@menu.register_menu(bp_monkey, '.view_monkey_list', 'Monkeys list', order=0)
def view_monkey_list():
    return render_template('view_monkey_list.html')


@bp_monkey.route('/monkey/<int:id>')
def view_monkey(id):
    best_friend = aliased(Monkey)
    monkey = Monkey.query.outerjoin(best_friend, Monkey.best_friend).options(
        Load(Monkey).load_only(Monkey.name, Monkey.age, Monkey.email)
        .contains_eager(Monkey.best_friend, alias=best_friend)
        .load_only(best_friend.name)
    ).filter(Monkey.id == id).first()

    if monkey is None:
        abort(404)

    return render_template('view_monkey.html', monkey=monkey)


@menu.register_menu(bp_monkey, '.add_monkey', 'Add monkey', order=1)
@bp_monkey.route('/monkey/add', methods=['GET', 'POST'])
def add_monkey():
    monkey_form = MonkeyForm()

    if request.method == 'POST':
        if monkey_form.validate():
            data = dict(monkey_form.data.items())

            del data['id']
            del data['submit_button']

            monkey = Monkey(**data)

            db.session.add(monkey)
            db.session.commit()

            flash('Monkey was succesfully created.')

            return redirect(url_for('.view_monkey', id=monkey.id))
        else:
            monkey_form.validate_on_submit()

    return render_template('add_monkey.html', monkey_form=monkey_form)


@bp_monkey.route('/monkey/<int:id>/edit', methods=['GET', 'POST'])
def edit_monkey(id):
    monkey = Monkey.query.options(
        Load(Monkey).load_only(Monkey.name, Monkey.age, Monkey.email)
    ).filter(Monkey.id == id).first()

    if monkey is None:
        abort(404)

    if request.method == 'POST':
        monkey_form = MonkeyForm()

        if monkey_form.validate():
            data = dict(monkey_form.data.items())

            del data['id']
            del data['submit_button']

            monkey = Monkey(**data)

            db.session.add(monkey)
            db.session.commit()

            flash('Monkey was succesfully edited.')

            return redirect(url_for('.view_monkey', id=monkey.id))
        else:
            monkey_form.validate_on_submit()
    else:
        monkey_form = MonkeyForm(**monkey.__dict__)

    return render_template(
        'edit_monkey.html', monkey=monkey, monkey_form=monkey_form
    )


@bp_monkey.route('/monkey/<int:id>/delete')
def delete_monkey(id):
    monkey = Monkey.query.options(
        Load(Monkey).load_only(Monkey.name, Monkey.age, Monkey.email)
    ).filter(Monkey.id == id).first()

    if monkey is None:
        abort(404)

    return render_template('delete_monkey.html', monkey=monkey)


@bp_monkey.route('/monkey/<int:id>/delete/confirm')
def delete_monkey_confirm(id):
    monkey = Monkey.query.get(id)

    if monkey is None:
        abort(404)

    db.session.delete(monkey)
    db.session.commit()

    flash('Monkey {0} was succesfully deleted.'.format(monkey.name))

    return redirect(url_for('.view_monkey_list'))
