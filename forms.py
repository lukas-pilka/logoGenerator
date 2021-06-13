from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields import RadioField, StringField
from wtforms.validators import InputRequired
from wtforms.validators import DataRequired
from connector import cloudSqlCnx

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
        choices=getArchetypes(cnx),
        validators=[InputRequired()]
    )
    brandField = RadioField(
        choices=getBusinesses(cnx),
        validators=[InputRequired()]
    )
    brandName = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Generovat loga')
