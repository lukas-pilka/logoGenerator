from flask import Flask, render_template, redirect, request, url_for, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from forms import brandProfile
from designSelector import *
from datetime import datetime
from connector import cloudSqlCnx
from pathlib import Path

base = Path(__file__).parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "abc"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
# csrf = CSRFProtect(app)
db = SQLAlchemy(app)



def writeLogoView(cnx,brandName, brandArchetypeId, brandFieldId, fontFamilyId, fontWeightId, primaryColorId, ipAddress, requestTime):
    # Write logo view into logo_views table
    with cnx.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `logo_views` (`brand_name`,`brand_archetype_id`,`brand_field_id`,`font_family_id`, `font_weight_id`, `primary_color_id`, `user_ip`,`created`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (brandName,
                             brandArchetypeId,
                             brandFieldId,
                             fontFamilyId,
                             fontWeightId,
                             primaryColorId,
                             ipAddress,
                             requestTime))
    # connection is not autocommit by default. So you must commit to save your changes.
    cnx.commit()


def writeLogoVote(cnx,brandName, brandArchetypeId, brandFieldId, fontFamilyId, fontWeightId, primaryColorId, ipAddress, requestTime):
    # Write logo vote into logo_votes table
    with cnx.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `logo_votes` (`brand_name`,`brand_archetype_id`,`brand_field_id`,`font_family_id`, `font_weight_id`, `primary_color_id`, `user_ip`,`created`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (brandName,
                             brandArchetypeId,
                             brandFieldId,
                             fontFamilyId,
                             fontWeightId,
                             primaryColorId,
                             ipAddress,
                             requestTime))
    # connection is not autocommit by default. So you must commit to save your changes.
    cnx.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = brandProfile()
    if form.validate_on_submit():
        brandName = form.brandName.data
        brandArchetype = form.brandArchetype.data
        brandField = form.brandField.data
        return redirect(url_for("get_logo_results", brandName=brandName, brandArchetype=brandArchetype, brandField=brandField))
    return render_template('index.html', form=form)

@app.route("/get_logo_results", methods=["GET","POST"])
def get_logo_results():
    # Honza's testing
    static = bool(request.args.get("static", False))
    length = int(request.args.get("length", 5))
    if static:
        with open(base/"static_response.json", "r") as input_file:
            data = json.load(input_file)
            data = [item for index, item in enumerate(data) if index < length]
            return jsonify(*data), 200

    ipAddress = request.remote_addr
    requestTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    receivedArguments = request.args.to_dict(flat=True)

    # Check if it receives arguments and if so it returns logo results
    if {'brandName', 'brandArchetype', 'brandField'} <= receivedArguments.keys():
        brandName = receivedArguments['brandName']
        brandArchetype = int(receivedArguments['brandArchetype'])
        brandField = int(receivedArguments['brandField'])
        voterPass = request.cookies.get('voterPass') # voterPass allows to submit vote
        cnx = cloudSqlCnx() # Open connection
        logos = getLogos(cnx,brandName,brandArchetype,brandField,10) # gets a list of logos with their parameters
        for logo in logos:
            print(logo)

        # Adds logo views to database
        for logo in logos:
            writeLogoView(cnx,
                          brandName,
                          brandArchetype,
                          brandField,
                          logo['Font family id'],
                          logo['Font weight id'],
                          logo['Primary color id'],
                          ipAddress,
                          requestTime)

        # Check if it has voterPass
        if voterPass:
            print('Voting for: ' + str(receivedArguments))
            writeLogoVote(cnx,
                          brandName,
                          brandArchetype,
                          brandField,
                          receivedArguments['fontFamily'],
                          receivedArguments['fontWeight'],
                          receivedArguments['primaryColor'],
                          ipAddress,
                          requestTime)
        else:
            print('No cookie, no voting')

        # Close connection
        cnx.close()
        return render_template("logoResults.html", logos=logos), 200
    return redirect(url_for("index"))

@app.route("/run_ml", methods=["GET"])
def runMachineLearning():
    cnx = cloudSqlCnx()  # Open connection
    print(getMlData(cnx))
    return('Done')

@app.route("/view_logos", methods=["GET"])
def view_logos():
    return render_template("view_logos.html")

@app.route("/icon/<name>", methods=["GET", "POST"]) # no post
def icon(name):
    with open(base/"icons"/f"{name}.svg", "r") as input_file:
        return {"icon": input_file.read()}, 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

