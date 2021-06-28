from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen
from flask import Flask, render_template, redirect, request, url_for, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from forms import brandProfile
from designSelector import *
from datetime import datetime
from connector import cloudSqlCnx
from pathlib import Path
from flask import Flask
from flaskext.mysql import MySQL
from random import randint



base = Path(__file__).parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "blue_" + "-".join([str(randint(0, 64)) for i in range(64)]) + "_ghost"
csrf = CSRFProtect(app)




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

    # Check if it receives arguments and if so it returns logo results
    if {'brandName', 'brandArchetype', 'brandField'} <= receivedArguments.keys():
        brandName = receivedArguments['brandName']
        brandArchetype = int(receivedArguments['brandArchetype'])
        brandField = int(receivedArguments['brandField'])
        voterPass = request.cookies.get('voterPass') # voterPass allows to submit vote
        cnx = cloudSqlCnx() # Open connection
        logos = getLogos(cnx, brandName, brandArchetype, brandField, 3) # gets a list of logos with their parameters

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

@app.route("/svg/<family_name>/<style_name>/<content>", methods=["GET"])
def svg(family_name: str, style_name: str, content: str):
    font = TTFont(base/"fonts"/family_name/f"{style_name}.ttf")
    cmap = font.getBestCmap()
    glyphSet = font.getGlyphSet()
    recording_pen = RecordingPen()
    offset = 0
    yMax = 0
    for index, character in enumerate(content):
        glyph_name = cmap.get(ord(character))
        glyph = glyphSet[glyph_name]
        transform_pen = TransformPen(recording_pen, (1, 0, 0, 1, offset, 0))
        glyph.draw(transform_pen)
        glyf_glyph = font["glyf"][glyph_name]
        try:
            if glyf_glyph.yMax > yMax:
                yMax = glyf_glyph.yMax
        except:
            pass
        offset += glyph.width
        if index == 0:
            left_margin = glyf_glyph.xMin

    svgpen = SVGPathPen(glyphSet)
    transform_pen = TransformPen(svgpen, (1, 0, 0, -1, -offset/2, yMax/2))
    recording_pen.replay(transform_pen)
    return {"svg": svgpen.getCommands()}, 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)