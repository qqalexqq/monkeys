"""Models for the case application."""
from sqlalchemy.orm.collections import attribute_mapped_collection

from app import db

friends_relationships = db.Table(
    'friends',
    db.Column('monkey_id', db.ForeignKey('monkeys.id', ondelete='CASCADE')),
    db.Column('friend_id', db.ForeignKey('monkeys.id', ondelete='CASCADE')),
    db.PrimaryKeyConstraint('monkey_id', 'friend_id')
)


class Monkey(db.Model):
    __tablename__ = 'monkeys'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(), nullable=False)
    friends = db.relationship(
        'Monkey',
        secondary=friends_relationships,
        primaryjoin=(friends_relationships.c.monkey_id == id),
        secondaryjoin=(friends_relationships.c.friend_id == id),
        lazy='dynamic',
        cascade='all',
        collection_class=attribute_mapped_collection('name')
    )
    best_friend_id = db.Column(db.Integer, db.ForeignKey('monkeys.id'))
    best_friend = db.relationship('Monkey', uselist=False, remote_side=[id])

    # TODO: rewrite using database triggers
    @property
    def friends_count(self):
        return self.friends.count()

    def set_best_friend(self, monkey):
        if not self.is_best_friend(monkey):
            self.add_friend(monkey)
            self.best_friend_id = monkey.id

        return self

    def unset_bestfriend(self):
        self.best_friend_id = None

        return self

    def is_best_friend(self, monkey):
        return self.best_friend_id == monkey.id

    def add_friend(self, monkey):
        if self != monkey:
            if not self.is_friend(monkey):
                self.friends.append(monkey)

            if not monkey.is_friend(self):
                monkey.friends.append(self)

        return self

    def delete_friend(self, monkey):
        if self.is_friend(monkey):
            self.friends.remove(monkey)

        if monkey.is_friend(self):
            monkey.friends.remove(self)

        return self

    def is_friend(self, monkey):
        return self.friends\
            .filter(friends_relationships.c.friend_id == monkey.id).count() > 0

    def __eq__(self, monkey):
        return self.id == monkey.id

    def __repr__(self):
        return '<Monkey #{0}>'.format(self.id)
