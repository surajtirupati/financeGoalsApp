from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import FinancialDataForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fefbb128d6df70ee4c3d697223e80958'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///financial_app.db"
db = SQLAlchemy(app)


class UserFinancialData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gross_salary = db.Column(db.Float, nullable=False)
    student_plan = db.Column(db.Integer)
    pension_contribution = db.Column(db.Float, nullable=False)
    fixed_costs = db.relationship('FixedCost', backref='financialdata', lazy=True)
    goals = db.relationship('Goals', backref='financialdata', lazy=True)


class FixedCost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    earnings_id = db.Column(db.Integer, db.ForeignKey("userfinancialdata.id"), nullable=False)


class Goals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    earnings_id = db.Column(db.Integer, db.ForeignKey("userfinancialdata.id"), nullable=False)


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
