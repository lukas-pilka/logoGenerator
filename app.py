from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from forms import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "abc"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
csrf = CSRFProtect(app)
db = SQLAlchemy(app)


@app.route("/", methods=["GET"])
def index():
    context = dict(logo_generator_form=LogoGeneratorForm(),)
    return render_template("index.html", **context), 200


@app.route("/get_logo_results", methods=["POST"])
def get_logo_results():
    logo_generator_form = LogoGeneratorForm()
    if logo_generator_form.validate_on_submit():
        # AI will process submitted valid form somewhere here
        return {"font": "Roboto", "icon": "pizza", "color": "red"}, 200
    else:
        return {"error": "invalid form"}, 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8800)
