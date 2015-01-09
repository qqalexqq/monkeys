from hamcrest import *

from models import Monkey as M
from test_models import create_monkeys


def test_view_monkey_list(client, session):
    monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

    monkey_john.add_friend(monkey_melissa)
    session.commit()

    request = client.get('/')

    assert_that(request.status_code, equal_to(200))

    for monkey in (monkey_ginger, monkey_john, monkey_melissa):
        assert_that(request.data, contains_string(monkey.name))
        assert_that(request.data, contains_string(str(monkey.friends_count)))

    request = client.get('/?page={0}'.format(100), follow_redirects=True)

    assert_that(request.status_code, equal_to(200))

    for monkey in (monkey_ginger, monkey_john, monkey_melissa):
        assert_that(request.data, contains_string(monkey.name))
        assert_that(request.data, contains_string(str(monkey.friends_count)))


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


def test_edit_monkey(client, session):
    data = dict(name='Melissa', age=19, email='granny@yahoo.club')

    monkey = M(**data)
    session.add(monkey)
    session.commit()

    request = client.get('/monkey/{0}/edit'.format(monkey.id))

    assert_that(
        request.data,
        contains_string('Edit monkey')
    )

    assert_that(
        request.data,
        contains_string('granny@yahoo.club')
    )

    data['age'] = 20
    request = client.post(
        '/monkey/{0}/edit'.format(monkey.id),
        data=data, follow_redirects=True
    )

    assert_that(request.status_code, equal_to(200))
    assert_that(request.data, contains_string('Melissa'))
    assert_that(request.data, contains_string('granny@yahoo.club'))
    assert_that(request.data, contains_string('20'))

    data['email'] = 123
    request = client.post(
        '/monkey/{0}/edit'.format(monkey.id),
        data=data, follow_redirects=True
    )

    assert_that(request.status_code, equal_to(200))
    assert_that(request.data, contains_string('Invalid email address'))


def test_delete_monkey(client, session):
    monkey = M(name='John', age=2, email='john.doe@gmail.tt')

    session.add(monkey)
    session.commit()

    request = client.get('/monkey/{0}/delete'.format(monkey.id))

    assert_that(
        request.data,
        contains_string('Monkey to be deleted:')
    )

    assert_that(
        request.data,
        contains_string('john.doe@gmail.tt')
    )


def test_delete_monkey_confirm(client, session):
    monkey = M(name='Melissa', age=19, email='granny@yahoo.club')

    session.add(monkey)
    session.commit()

    request = client.get(
        '/monkey/{0}/delete/confirm'.format(monkey.id), follow_redirects=True
    )

    assert_that(request.status_code, equal_to(200))
    assert_that(
        request.data,
        contains_string('{0} was succesfully deleted.'.format(monkey.name))
    )

    request = client.get(
        '/monkey/{0}/delete/confirm'.format(-1), follow_redirects=True
    )

    assert_that(request.status_code, equal_to(404))


def test_view_friend_list(client, session):
    monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

    monkey_john.add_friend(monkey_melissa)
    session.commit()

    request = client.get('/friend/{0}'.format(monkey_john.id))

    assert_that(request.status_code, equal_to(200))
    assert_that(request.data, contains_string(monkey_melissa.name))
    assert_that(request.data, contains_string(str(monkey_melissa.age)))
    assert_that(request.data, contains_string(monkey_melissa.email))

    request = client.get(
        '/friend/{0}?page={1}'.format(monkey_john.id, 100),
        follow_redirects=True
    )

    assert_that(request.status_code, equal_to(200))
    assert_that(request.data, contains_string(monkey_melissa.name))
    assert_that(request.data, contains_string(str(monkey_melissa.age)))
    assert_that(request.data, contains_string(monkey_melissa.email))


def test_view_add_friend(client, session):
    monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

    request = client.get('/friend/{0}/add'.format(monkey_melissa.id))

    assert_that(request.status_code, equal_to(200))

    for monkey in (monkey_ginger, monkey_john):
        assert_that(request.data, contains_string(monkey.name))
        assert_that(request.data, contains_string(str(monkey.age)))
        assert_that(request.data, contains_string(monkey.email))

    request = client.get(
        '/friend/{0}/add?page={0}'.format(monkey_melissa.id, 100),
        follow_redirects=True
    )

    assert_that(request.status_code, equal_to(200))

    for monkey in (monkey_ginger, monkey_john):
        assert_that(request.data, contains_string(monkey.name))
        assert_that(request.data, contains_string(str(monkey.age)))
        assert_that(request.data, contains_string(monkey.email))


def test_add_friend(client, session):
    monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

    request = client.get(
        '/friend/{0}/add/{1}'.format(monkey_melissa.id, monkey_john.id),
        follow_redirects=True
    )

    assert_that(request.status_code, equal_to(200))
    assert_that(request.data, contains_string(
        '{0} added to monkey {1} friends.'
        .format(monkey_john.name, monkey_melissa.name)
    ))


def test_delete_friend(client, session):
    monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

    monkey_ginger.add_friend(monkey_melissa)
    session.commit()

    request = client.get(
        '/friend/{0}/delete/{1}'.format(monkey_ginger.id, monkey_melissa.id),
        follow_redirects=True
    )

    assert_that(request.status_code, equal_to(200))
    assert_that(request.data, contains_string(
        '{0} deleted from monkey {1} friends.'
        .format(monkey_melissa.name, monkey_ginger.name)
    ))


def test_set_best_friend(client, session):
    monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

    request = client.get(
        '/best_friend/{0}/set/{1}'.format(monkey_melissa.id, monkey_john.id),
        follow_redirects=True
    )

    assert_that(request.status_code, equal_to(200))
    assert_that(request.data, contains_string(
        'Best friend {0} set for monkey {1}.'
        .format(monkey_john.name, monkey_melissa.name)
    ))


def test_unset_best_friend(client, session):
    monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

    monkey_melissa.set_best_friend(monkey_john)
    session.commit()

    request = client.get(
        '/best_friend/{0}/unset/{1}'.format(monkey_melissa.id, monkey_john.id),
        follow_redirects=True
    )

    assert_that(request.status_code, equal_to(200))
    assert_that(request.data, contains_string(
        'Best friend {0} unset for monkey {1}.'
        .format(monkey_john.name, monkey_melissa.name)
    ))
