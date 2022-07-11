from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import FinancialDataForm, LoginForm, UserForm, FixedCostForm, GoalForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from calculations import disposable_income, deduct_fixed_costs, total_fixed_costs, calculate_saving_income, \
    income_pie_chart, income_funnel, return_perc_drops, return_dashboard_cards_text, full_horizon_compound, \
    plot_compound_and_standard, linear_investing

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fefbb128d6df70ee4c3d697223e80958'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///financial_app.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    financial_data = db.relationship('Userfinancialdata', backref='user_financial_data', lazy=True)
    fixed_costs = db.relationship('FixedCost', backref='financialdata', lazy=True)
    goals = db.relationship('Goals', backref='financialdata', lazy=True)


class Userfinancialdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gross_salary = db.Column(db.Float, nullable=False)
    student_plan = db.Column(db.Integer)
    pension_contribution = db.Column(db.Float, nullable=False)
    saving_percentage = db.Column(db.Float, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disposable_income = db.Column(db.Float)
    total_fixed_costs = db.Column(db.Float)
    personal_income = db.Column(db.Float)
    saving_income = db.Column(db.Float)


class FixedCost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class Goals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    target = db.Column(db.Float)
    user = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


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


def financial_data_exists():
    return Userfinancialdata.query.filter_by(user=current_user.id).first()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if user_is_logged_in() and financial_data_exists() is not None:
        return redirect(url_for('dashboard'))

    elif user_is_logged_in():
        return redirect(url_for('setup'))

    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash("Successful sign up! Please fill in the following details to set up your account", 'success')

        else:
            flash("User email already exists! Please login", 'danger')

        return redirect(url_for('login'))

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if user_is_logged_in() and financial_data_exists() is not None:
        return redirect(url_for('dashboard'))

    elif user_is_logged_in():
        return redirect(url_for('setup'))

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
    if financial_data_exists() is not None:
        flash("You have already input your financial data!", 'danger')
        return redirect(url_for('dashboard'))

    form = FinancialDataForm()

    if form.validate_on_submit():
        financial_data = Userfinancialdata(gross_salary=form.gross_salary.data, student_plan=form.student_plan.data,
                                           pension_contribution=form.pension_contribution.data,
                                           saving_percentage=form.saving_percentage.data,
                                           user=current_user.id)

        financial_data.disposable_income = round(
            float(disposable_income(financial_data.gross_salary, financial_data.student_plan,
                                    financial_data.pension_contribution)), 2)

        for goal in form.goals:
            tmp_goal = Goals(name=goal.goal_name.data, amount=goal.amount.data, user=current_user.id)
            db.session.add(tmp_goal)

        for fixed_cost in form.fixed_costs:
            financial_data.total_fixed_costs = fixed_cost.amount.data  # only one fixed cost at this point
            tmp_fc = FixedCost(name=fixed_cost.fc_name.data, amount=fixed_cost.amount.data, user=current_user.id)
            db.session.add(tmp_fc)

        financial_data.personal_income = round(
            float((financial_data.disposable_income / 12) - financial_data.total_fixed_costs), 2)
        financial_data.saving_income = round(float(
            calculate_saving_income(financial_data.personal_income, financial_data.saving_percentage)), 2)

        db.session.add(financial_data)
        db.session.commit()

        flash("Setup complete!", 'success')
        return redirect(url_for('dashboard'))

    return render_template("setup.html", form=form)


@app.route("/")
@login_required
def home():
    return render_template("base.html")


@app.route("/my_finances", methods=['GET', 'POST'])
@login_required
def my_finances():
    financial_data = Userfinancialdata.query.filter_by(user=current_user.id).first()
    fixed_costs = FixedCost.query.filter_by(user=current_user.id).all()
    goals = Goals.query.filter_by(user=current_user.id).all()

    form = FinancialDataForm(student_plan=financial_data.student_plan)
    fc_form = FixedCostForm()
    goals_form = GoalForm()

    if goals_form.is_submitted() and goals_form.submit_goal.data:
        if type(goals_form.goal_name.data) == str and type(
                goals_form.amount.data) == float and 1 > goals_form.amount.data > 0 and type(goals_form.target.data) == float:
            tmp_goal = Goals(name=goals_form.goal_name.data, amount=goals_form.amount.data, target=goals_form.target.data, user=current_user.id)
            db.session.add(tmp_goal)
            db.session.commit()
            return redirect(url_for("my_finances"))
        else:
            flash(
                "Please ensure you enter text for goal name, a number for the target, and a number between 0 and 1 for it's % of saving income!",
                "danger")
            return redirect(url_for("my_finances"))

    if fc_form.validate_on_submit() and fc_form.submit.data:
        tmp_fc = FixedCost(name=fc_form.fc_name.data, amount=fc_form.amount.data, user=current_user.id)
        db.session.add(tmp_fc)
        db.session.commit()
        return redirect(url_for("my_finances"))

    if form.is_submitted() and form.update.data:
        financial_data.gross_salary = form.gross_salary.data
        financial_data.saving_percentage = form.saving_percentage.data
        financial_data.student_plan = form.student_plan.data
        financial_data.pension_contribution = form.pension_contribution.data
        db.session.add(financial_data)
        db.session.commit()
        return redirect(url_for("my_finances"))

    financial_data.disposable_income = round(
        float(disposable_income(financial_data.gross_salary, financial_data.student_plan,
                                financial_data.pension_contribution)), 2)
    financial_data.total_fixed_costs = total_fixed_costs(fixed_costs)
    financial_data.personal_income = round(
        float(deduct_fixed_costs(financial_data.disposable_income / 12, fixed_costs)), 2)
    financial_data.saving_income = round(float(
        calculate_saving_income(financial_data.personal_income, financial_data.saving_percentage)), 2)

    db.session.add(financial_data)
    db.session.commit()

    return render_template("my_finances.html", form=form, fc_form=fc_form, goals_form=goals_form,
                           financial_data=financial_data, fc_data=fixed_costs, goal_data=goals,
                           total_fc=financial_data.total_fixed_costs, saving_income=financial_data.saving_income)


@app.route("/dashboard")
@login_required
def dashboard():
    # variable calculation
    financial_data = Userfinancialdata.query.filter_by(user=current_user.id).first()
    taxes_and_insurance = financial_data.gross_salary - financial_data.disposable_income
    lifestyle_income = financial_data.personal_income - financial_data.saving_income

    # goal graph variable collection
    goal_to_display = Goals.query.filter_by(user=current_user.id).first()
    compound_rate = 0.08
    monthly_payment = goal_to_display.amount * financial_data.saving_income
    goal_target = goal_to_display.target

    # linear calculation
    linear_progression, time_axis = linear_investing(goal_target, monthly_payment)
    # compound calculation
    compound_progression, _, time_to_reach_goal = full_horizon_compound(monthly_payment, compound_rate, goal_target, time_axis[-1])
    # compound vs linear graph
    goal_graph = plot_compound_and_standard(goal_target, time_axis[-1], compound_rate, time_axis, linear_progression,
                                            compound_progression, time_to_reach_goal)


    # income without student debt
    inc_w_out_debt = round(
        float(disposable_income(financial_data.gross_salary, 0, financial_data.pension_contribution)), 2)

    # rendering card text
    pct_1, pct_2, pct_3 = return_perc_drops(financial_data.gross_salary, financial_data.disposable_income,
                                            12 * financial_data.personal_income, 12 * financial_data.saving_income)
    card_1_text, card_2_text, card_3_text, card_4_text = return_dashboard_cards_text(pct_1, pct_2, pct_3,
                                                                                     inc_w_out_debt,
                                                                                     financial_data.disposable_income)

    graph = income_pie_chart(taxes_and_insurance, 12 * financial_data.total_fixed_costs, 12 * lifestyle_income,
                             12 * financial_data.saving_income)
    graph2 = income_funnel(financial_data.gross_salary, financial_data.disposable_income,
                           12 * financial_data.personal_income, 12 * financial_data.saving_income)
    return render_template("dashboard.html", graphJSON=graph, graphJSON2=graph2, graphJSON3=goal_graph, c1=card_1_text,
                           c2=card_2_text, c3=card_3_text, c4=card_4_text, name_of_goal=goal_to_display.name)


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
