"""Models for the case application."""
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import event, DDL

db = SQLAlchemy()

friends_relationships = db.Table(
    'friends',
    db.Column('monkey_id', db.ForeignKey('monkeys.id', ondelete='CASCADE')),
    db.Column('friend_id', db.ForeignKey('monkeys.id', ondelete='CASCADE')),
    db.PrimaryKeyConstraint('monkey_id', 'friend_id')
)


class Monkey(db.Model):
    __tablename__ = 'monkeys'
    __table_args__ = (
        db.Index('ix_monkey_name_id', 'name', 'id', unique=True),
        db.Index('ix_monkey_fCount_id', 'friends_count', 'id', unique=True)
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(), nullable=False)
    friends = db.relationship(
        'Monkey',
        secondary=friends_relationships,
        primaryjoin=(friends_relationships.c.monkey_id == id),
        secondaryjoin=(friends_relationships.c.friend_id == id),
        lazy='dynamic',
        cascade='all'
    )
    friends_count = db.Column(
        db.Integer, default=0, server_onupdate=db.FetchedValue()
    )
    best_friend_id = db.Column(
        db.Integer, db.ForeignKey('monkeys.id'), index=True
    )
    best_friend = db.relationship('Monkey', uselist=False, remote_side=[id])

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

change_monkey_friends_count_trigger_ddl = DDL("""
CREATE OR REPLACE FUNCTION process_change_monkey_friends_count()
RETURNS TRIGGER AS $change_monkey_friends_count$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            UPDATE monkeys SET friends_count = friends_count - 1
                WHERE id = OLD.monkey_id;
            RETURN OLD;
        ELSIF (TG_OP = 'INSERT') THEN
            UPDATE monkeys SET friends_count = friends_count + 1
                WHERE id = NEW.monkey_id;
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
$change_monkey_friends_count$ LANGUAGE plpgsql;

CREATE TRIGGER change_monkey_friends_count
AFTER INSERT OR DELETE ON friends
    FOR EACH ROW EXECUTE PROCEDURE process_change_monkey_friends_count();
""")

event.listen(
    friends_relationships, 'after_create',
    change_monkey_friends_count_trigger_ddl.execute_if(dialect='postgresql')
)
