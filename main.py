from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from forms import brandProfile
from designSelector import *
from datetime import datetime
from connector import cloudSqlCnx

app = Flask(__name__)
app.config["SECRET_KEY"] = "abc"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
csrf = CSRFProtect(app)
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
    ipAddress = request.remote_addr
    requestTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    receivedArguments = request.args.to_dict(flat=True)
    if {'brandName', 'brandArchetype', 'brandField'} <= receivedArguments.keys():
        brandName = receivedArguments['brandName']
        brandArchetype = int(receivedArguments['brandArchetype'])
        brandField = int(receivedArguments['brandField'])

        voterPass = request.cookies.get('voterPass') # voterPass allows to submit vote
        cnx = cloudSqlCnx() # Open connection
        logos = getLogos(cnx,brandName,brandArchetype,brandField,10) # connection, count of logos

        # Preparing data for fitness prediction
        maxValues = getMaxValues(cnx)
        predictionInputs = []
        for logo in logos:
            fitData = [brandArchetype, brandField, logo['Font family id'], logo['Font weight id'], logo['Primary color id']]
            guessData = expandData(fitData, maxValues)
            predictionInputs.append([guessData])

        # Receiving predictions and appending logos
        predictionOutputs = predictFitness(predictionInputs)
        for i in range(len(logos)):
            logos[i]['Fitness prediction'] = predictionOutputs[i][0]

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
            print('Not voting')

        # Close connection
        cnx.close()
        return render_template("logoResults.html", logos=logos), 200
    return redirect(url_for("index"))

@app.route("/run_ml", methods=["GET"])
def runMachineLearning():
    cnx = cloudSqlCnx()  # Open connection
    print(getMlData(cnx))
    return('Done')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)