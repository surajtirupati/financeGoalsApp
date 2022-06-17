from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import FinancialDataForm, LoginForm, UserForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fefbb128d6df70ee4c3d697223e80958'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///financial_app.db"
db = SQLAlchemy(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    financial_data = db.relationship('Userfinancialdata', backref='user_financial_data', lazy=True)


class Userfinancialdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gross_salary = db.Column(db.Float, nullable=False)
    student_plan = db.Column(db.Integer)
    pension_contribution = db.Column(db.Float, nullable=False)
    fixed_costs = db.relationship('FixedCost', backref='financialdata', lazy=True)
    goals = db.relationship('Goals', backref='financialdata', lazy=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))


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


# Create database tables
db.create_all()

# Flask_Login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


def user_is_logged_in():
    return current_user.is_authenticated


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if user_is_logged_in():
        return redirect(url_for('dashboard'))

    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash("Successful sign up! Please login:", 'success')

        else:
            flash("User email already exists! Please login", 'danger')

        return redirect(url_for('login'))

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if user_is_logged_in():
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!", 'success')

                if current_user.financial_data is not None:
                    return redirect(url_for('dashboard'))

                else:
                    return redirect(url_for('setup'))

            else:
                flash("Wrong Password - Try Again!", 'danger')

        else:
            flash("That User Doesn't Exist! Try Again:", 'danger')

    return render_template('login.html', form=form)


@app.route("/setup", methods=['GET', 'POST'])
@login_required
def setup():
    if current_user.financial_data is not None:
        flash("You have already input your financial data!", 'danger')
        return redirect(url_for('dashboard'))

    form = FinancialDataForm()
    
    if form.validate_on_submit():
        flash("Setup complete!", 'success')
        return redirect(url_for('dashboard'))

    return render_template("setup.html", form=form)


@app.route("/")
@login_required
def home():
    return render_template("base.html")


@app.route("/my_finances")
@login_required
def my_finances():
    return render_template("my_finances.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/goal_progress")
@login_required
def goal_progress():
    return render_template("goal_progress.html")


@app.route("/custom_goal")
@login_required
def custom_goal():
    return render_template("custom_goal.html")


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have successfully been logged out!", 'success')
    return redirect(url_for('login'))
