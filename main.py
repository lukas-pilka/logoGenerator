from flask import Flask, render_template, json, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from forms import *
import pymysql
import os
import designSelector
from pathlib import Path

base = Path(__file__).parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "abc"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
# csrf = CSRFProtect(app)
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

@app.route("/get_logo_results", methods=["POST", "GET"]) # Must be POST, because it will accept a form
def get_logo_results():
    static = bool(request.args.get("static", False))
    length = int(request.args.get("length", 5))
    if static:
        with open(base/"static_response.json", "r") as input_file:
            data = json.load(input_file)
            data = [item for index, item in enumerate(data) if index < length]
            return jsonify(*data), 200
    else:
        cnx = cloudSqlCnx() # Open connection
        logos = designSelector.getLogos(cnx, length) # connection, count of logos
        cnx.close() # Close connection
        return jsonify(logos), 200

@app.route("/view_logos", methods=["GET"])
def view_logos():
    return render_template("view_logos.html"), 200

@app.route("/icon/<name>", methods=["GET"])
def get_icon(name):
    try:
        with open(base/"icons"/f"{name}.svg", "r") as input_file:
            return {"icon": input_file.read()}
    except:
        return {"error": "not found"}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

