from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from forms import *
import pymysql
import os
import designSelector


app = Flask(__name__)
app.config["SECRET_KEY"] = "abc"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
csrf = CSRFProtect(app)
db = SQLAlchemy(app)

# Loads cloudSQL access data for connection from localhost
db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

def cloudSqlCnx():
    # When deployed to App Engine, the `GAE_ENV` environment variable will be set to `standard`
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name)
        return cnx
    else:
        # If running locally, use the TCP connections
        host = '34.107.110.174'
        cnx = pymysql.connect(user=db_user, password=db_password, host=host, db=db_name)
        return cnx

@app.route("/", methods=["GET"])
def index():
    context = dict(logo_generator_form=LogoGeneratorForm(),)
    return render_template("index.html", **context), 200

@app.route("/get_logo_results", methods=["GET"])
def get_logo_results():
    cnx = cloudSqlCnx() # Open connection
    logos = designSelector.getLogos(cnx,5) # connection, count of logos
    cnx.close() # Close connection
    return str(logos)
    '''
    logo_generator_form = LogoGeneratorForm()
    if logo_generator_form.validate_on_submit():
        # AI will process submitted valid form somewhere here
        return {"font": "Roboto", "icon": "pizza", "color": "red"}, 200
    else:
        return {"error": "invalid form"}, 500
    '''

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)