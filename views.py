from collections import OrderedDict
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, abort
)
from flask.ext import menu
from sqlalchemy.orm import aliased
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.sql.expression import select

from models import *
from forms import *

# 5 for easier testing purposes
monkeys_per_page = 5

bp_monkey = Blueprint('monkey', __name__)


# '/monkey' route goes first because 'menu' module takes last route's url
@bp_monkey.route('/monkey')
@bp_monkey.route('/')
@menu.register_menu(bp_monkey, '.view_monkey_list', 'Monkeys list', order=0)
def view_monkey_list():
    global monkeys_per_page

    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_asc_str = request.args.get('sort_asc', None, type=str)
    page = request.args.get('page', 1, type=int)

    fields_order = OrderedDict([
        ('name', True),
        ('best_friend.name', True),
        ('friends_count', False)
    ])

    sort_asc = None if sort_asc_str is None else sort_asc_str == 'True'

    if sort_by not in fields_order or sort_asc is None:
        sort_by = 'name'
        sort_asc = fields_order[sort_by]

    fields_order[sort_by] = not sort_asc

    best_friend = aliased(Monkey)
    # Hack. Can be fixed by denormalization
    if sort_by != 'best_friend.name':
        monkeys_order_by = getattr(Monkey, sort_by)
    else:
        monkeys_order_by = getattr(best_friend, 'name')

    paginate = Monkey.query.outerjoin(best_friend, Monkey.best_friend).options(
        Load(Monkey).load_only(Monkey.name, Monkey.friends_count)
        .contains_eager(Monkey.best_friend, alias=best_friend)
        .load_only(best_friend.name)
    ).order_by(
        getattr(monkeys_order_by, 'asc' if sort_asc else 'desc')()
    ).paginate(
        page, per_page=monkeys_per_page, error_out=False
    )

    if not paginate.items and paginate.total > 0:
        new_page = paginate.pages

        return redirect(url_for(
            '.view_monkey_list', sort_by=sort_by, sort_asc=sort_asc,
            page=new_page
        ))

    return render_template(
        'view_monkey_list.html',
        fields_order=fields_order,
        sort_by=sort_by,
        sort_asc=sort_asc,
        paginate=paginate
    )


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


@bp_monkey.route('/friend/<int:monkey_id>/add')
def view_add_friend(monkey_id):
    global monkeys_per_page

    best_friend = aliased(Monkey)
    monkey = Monkey.query.outerjoin(best_friend, Monkey.best_friend).options(
        Load(Monkey).load_only(Monkey.name)
        .contains_eager(Monkey.best_friend, alias=best_friend)
        .load_only(best_friend.name)
    ).filter(Monkey.id == monkey_id).first()

    if monkey is None:
        abort(404)

    page = request.args.get('page', 1, type=int)

    paginate = Monkey.query.filter(~(Monkey.id.in_(select(
        [friends_relationships.c.friend_id],
        friends_relationships.c.monkey_id == monkey_id
    ))), Monkey.id != monkey_id).options(
        Load(Monkey).load_only(Monkey.name, Monkey.age, Monkey.email)
    ).order_by(
        Monkey.name.asc()
    ).paginate(
        page, per_page=monkeys_per_page, error_out=False
    )

    if not paginate.items and paginate.total > 0:
        new_page = paginate.pages

        return redirect(url_for(
            '.view_add_friend', monkey_id=monkey_id, page=new_page
        ))

    return render_template(
        'view_add_friend.html',
        monkey=monkey,
        paginate=paginate
    )


@bp_monkey.route('/friend/<int:monkey_id>/add/<int:friend_id>')
def add_friend(monkey_id, friend_id):
    page_was = request.args.get('page_was', 1, type=int)

    monkey = Monkey.query.options(
        Load(Monkey).load_only(Monkey.name)
    ).filter(Monkey.id == monkey_id).first()

    if monkey is None:
        abort(404)

    friend = Monkey.query.options(
        Load(Monkey).load_only(Monkey.name)
    ).filter(Monkey.id == friend_id).first()

    if friend is None:
        abort(404)

    monkey.add_friend(friend)
    db.session.commit()

    flash(
        'Friend {0} added to monkey {1} friends.'
        .format(friend.name, monkey.name)
    )

    return redirect(url_for(
        '.view_add_friend', monkey_id=monkey_id, page=page_was
    ))
