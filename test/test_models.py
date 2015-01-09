from hamcrest import *

from models import Monkey as M


def create_monkeys(session):
    monkey_ginger = M(name='Ginger', age=10, email='ginger@hotmail.icann')
    monkey_john = M(name='John', age=2, email='john.doe@gmail.tt')
    monkey_melissa = M(name='Melissa', age=19, email='granny@yahoo.club')

    session.add(monkey_ginger)
    session.add(monkey_john)
    session.add(monkey_melissa)
    session.commit()

    return (monkey_ginger, monkey_john, monkey_melissa)


class TestMonkey:
    def test_monkey_model(self, session):
        monkey = M(name='test', age=14, email='q@q.ru')

        session.add(monkey)
        session.commit()

        assert_that(monkey, has_property('id', greater_than(0)))
        assert_that(monkey.name, isequal)

    def test_monkeys_friends(self, session):
        monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

        monkey_ginger.add_friend(monkey_john)
        session.commit()

        assert_that(
            M.query.get(monkey_ginger.id).friends,
            has_item(monkey_john)
        )

        monkey_ginger.add_friend(monkey_melissa)
        session.commit()

        assert_that(
            M.query.get(monkey_ginger.id).friends,
            has_item(monkey_melissa)
        )

        assert_that(
            monkey_ginger.friends_count,
            equal_to(2)
        )

        assert_that(
            monkey_john.friends_count,
            equal_to(1)
        )

        monkey_ginger.delete_friend(monkey_melissa)
        session.commit()

        assert_that(
            monkey_ginger.friends_count,
            equal_to(1)
        )

        assert_that(
            monkey_melissa.friends_count,
            equal_to(0)
        )

    def test_monkeys_best_friends(self, session):
        monkey_ginger, monkey_john, monkey_melissa = create_monkeys(session)

        monkey_ginger.set_best_friend(monkey_melissa)
        session.commit()

        assert_that(monkey_ginger.best_friend_id, equal_to(monkey_melissa.id))

        monkey_ginger.unset_best_friend()
        monkey_ginger.set_best_friend(monkey_john)

        assert_that(
            monkey_ginger.friends.all(),
            contains_inanyorder(monkey_john, monkey_melissa)
        )

        assert_that(monkey_ginger.best_friend, equal_to(monkey_john))
