from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields import RadioField
from wtforms.validators import InputRequired
import widgets

__all__ = ["LogoGeneratorForm"]


class LogoGeneratorForm(FlaskForm):
    archetype = RadioField(
        widget=widgets.radio_input,
        choices=["mudrc", "objevitel", "klaun"],
        validators=[InputRequired()],
    )
    specialization = RadioField(
        widget=widgets.radio_input,
        choices=["gastro", "móda", "umění"],
        validators=[InputRequired()],
    )
    submit = SubmitField()
