from flask import Flask, render_template, request, redirect, url_for, flash
from forms import FinancialDataForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'fefbb128d6df70ee4c3d697223e80958'

@app.route("/")
def home():
    return render_template("base.html")


@app.route("/my_finances")
def my_finances():
    return render_template("my_finances.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/goal_progress")
def goal_progress():
    return render_template("goal_progress.html")


@app.route("/custom_goal")
def custom_goal():
    return render_template("custom_goal.html")


@app.route("/setup", methods=['GET', 'POST'])
def setup():
    form = FinancialDataForm()
    if form.validate_on_submit():
        flash("Setup complete!", 'success')
        return redirect(url_for('dashboard'))
    return render_template("setup.html", form=form)
