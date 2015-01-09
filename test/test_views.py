from hamcrest import *

from models import Monkey as M
from test_models import create_monkeys


def test_view_monkey(client, session):
    monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

    monkey_ginger.set_best_friend(monkey_melissa)
    session.commit()

    request = client.get('/monkey/{0}'.format(monkey_ginger.id))

    assert_that(
        request.data,
        contains_string('ginger@hotmail.icann')
    )

    assert_that(
        request.data,
        contains_string('Melissa')
    )


def test_add_monkey(client, session):
    request = client.get('/monkey/add')

    assert_that(
        request.data,
        contains_string('Add monkey')
    )

    data = dict(name='John', age=2, email='john.doe@gmail.tt')
    request = client.post('/monkey/add', data=data, follow_redirects=True)

    assert_that(request.status_code, equal_to(200))

    monkey = M.query.filter(M.email == 'john.doe@gmail.tt').one()

    assert_that(monkey.name, equal_to('John'))
    assert_that(monkey.email, equal_to('john.doe@gmail.tt'))
    assert_that(monkey.age, equal_to(2))

    data = dict(name='John', age='not_an_age', email='john.doe@gmail.tt')
    request = client.post('/monkey/add', data=data, follow_redirects=True)

    assert_that(request.status_code, equal_to(200))
    assert_that(request.data, contains_string('Not a valid integer value'))
