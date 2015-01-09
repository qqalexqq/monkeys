from flask.ext.wtf import Form
from wtforms import (
    TextField, IntegerField, HiddenField, SubmitField, validators
)


class MonkeyForm(Form):
    id = HiddenField()
    name = TextField('Name', validators=[validators.InputRequired()])
    age = IntegerField(
        'Age', validators=[
            validators.InputRequired(message='Age should be an integer.'),
            validators.NumberRange(min=0)
        ]
    )
    email = TextField(
        'Email', validators=[validators.InputRequired(), validators.Email()]
    )

    submit_button = SubmitField('Submit')
