from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen
from flask import Flask, render_template, redirect, request
from flask_wtf.csrf import CSRFProtect
from forms import brandProfile
from designSelector import *
from datetime import datetime
from connector import cloudSqlCnx
from pathlib import Path
from flask import Flask
from random import randint
from requests import get



base = Path(__file__).parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "blue_" + "-".join([str(randint(0, 64)) for i in range(64)]) + "_ghost"
csrf = CSRFProtect(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = brandProfile()
    if form.validate_on_submit():
        brand_name = form.brandName.data
        brand_archetypes_id = form.brandArchetype.data
        brand_archetypes = dict(form.brandArchetype.choices)[int(brand_archetypes_id)]
        business_categories_id = form.brandField.data
        business_categories = dict(form.brandField.choices)[int(business_categories_id)]
        return redirect(url_for("get_logo_results", brand_name=brand_name, brand_archetypes_id=brand_archetypes_id,
                                brand_archetypes=brand_archetypes, business_categories_id=business_categories_id,
                                business_categories=business_categories))
    return render_template('index.html', form=form)

@app.route("/get_logo_results", methods=["GET","POST"])
def get_logo_results():

    print("""
============================
NEW REQUEST FOR LOGO RESULTS
============================
    """)

    ipAddress = get('https://api.ipify.org').text
    requestTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    receivedArguments = request.args.to_dict(flat=True)
    voterPass = request.cookies.get('voterPass')  # voterPass allows to submit vote
    cnx = cloudSqlCnx()  # Open connection

    # If it receives brand parameters in attributes it generates logos
    if {'brand_name','brand_archetypes','business_categories'} <= receivedArguments.keys():
        brandName = receivedArguments['brand_name']
        brandArchetype = (int(receivedArguments['brand_archetypes_id']), receivedArguments['brand_archetypes'])
        businessCategories = (int(receivedArguments['business_categories_id']), receivedArguments['business_categories'])

        # If it receives previous logo parameters in attributes it ads them into previousLogo
        if {'font_weights','font_families','primary_colors'} <= receivedArguments.keys():
            # it ads them into previousLogo
            previousLogo = receivedArguments

            # Check if it has voterPass cookie and if so, it calls writeLogoVote
            if voterPass:
                print('Voting for: ' + str(receivedArguments))
                writeLogoVote(brandName,
                              receivedArguments['brand_archetypes_id'],
                              receivedArguments['business_categories_id'],
                              receivedArguments['font_families_id'],
                              receivedArguments['font_weights'],
                              receivedArguments['text_transforms_id'],
                              receivedArguments['primary_colors_id'],
                              receivedArguments['shapes_id'],
                              ipAddress,
                              requestTime)
            else:
                print('No cookie, no voting')

        else:
            previousLogo = None

        logos = generateLogos(brandName, brandArchetype, businessCategories, 6, ipAddress, requestTime, previousLogo)

        # Close connection
        cnx.close()
        return render_template("logoResults.html", logos=logos), 200
        # return redirect(logo['vote_url'])

    else:
        return redirect(url_for("index"))


@app.route("/run_ml", methods=["GET"])
def runMachineLearning():
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