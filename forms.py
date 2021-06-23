from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields import RadioField, StringField
from wtforms.validators import InputRequired
from wtforms.validators import DataRequired
from connector import cloudSqlCnx
from widgets import radio_input_widget

cnx = cloudSqlCnx() # Open connection
def getArchetypes(cnx):
    with cnx.cursor() as cursor:
        cursor.execute('select * from brand_archetypes;')
        allArchetypes = cursor.fetchall()
    return allArchetypes

def getBusinesses(cnx):
    with cnx.cursor() as cursor:
        cursor.execute('select * from business_categories;')
        allBusinesses = cursor.fetchall()
    return allBusinesses


class brandProfile(FlaskForm):
    brandArchetype = RadioField(
        label="Charakter firmy",
        widget=radio_input_widget,
        choices=getArchetypes(cnx),
        validators=[InputRequired()]
    )
    brandField = RadioField(
        label="Zaměření firmy",
        widget=radio_input_widget,
        choices=getBusinesses(cnx),
        validators=[InputRequired()]
    )
    brandName = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Generovat loga')
