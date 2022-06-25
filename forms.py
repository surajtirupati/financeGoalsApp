from flask_wtf import FlaskForm
from wtforms import Form, StringField, FloatField, SelectField, FormField, FieldList, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, EqualTo


# Create Fixed Cost Sub-Form
class FixedCostForm(FlaskForm):
    fc_name = StringField("Fixed Cost Name e.g. Rent", validators=[DataRequired()])
    amount = FloatField("Fixed Cost Monthly Amount e.g. 800", validators=[DataRequired()])
    submit = SubmitField('Add')


# Create Goal Sub-Form
class GoalForm(FlaskForm):
    goal_name = StringField("What are you saving for?", validators=[DataRequired()])
    amount = FloatField("What percentage of your savings would you like to allocate to this goal? e.g. 0.25 for 25%",
                        validators=[DataRequired(), NumberRange(min=0, max=1, message='Enter number between 0 and 1')])
    submit_goal = SubmitField('Add')


# Create Financial Data Form
class FinancialDataForm(FlaskForm):
    gross_salary = FloatField('Gross Salary', validators=[DataRequired(),
                                                          NumberRange(min=0,
                                                                      max=26500000000,
                                                                      message='Please enter a valid number')])
    student_plan = SelectField("Student Loan Plan Type", choices=[(0, "None"), (1, "Plan 1"), (2, "Plan 2")],
                               validators=[DataRequired()])
    pension_contribution = FloatField("Salary Contribution to Pension e.g. 0.05 for 5%", validators=[DataRequired(),
                                                                                                     NumberRange(min=-0.000001,
                                                                                                                 max=1,
                                                                                                                 message='Enter number between 0 and 1')])
    fixed_costs = FieldList(FormField(FixedCostForm), min_entries=1)
    saving_percentage = FloatField("What percentage of your income after monthly fixed costs are deducted would you "
                                   "like to save? e.g. 0.25 for 25%", validators=[DataRequired(), NumberRange(min=-0.000001,
                                                                                                              max=1,
                                                                                                              message='Enter number between 0 and 1')])
    goals = FieldList(FormField(GoalForm), min_entries=1)
    submit = SubmitField('Submit')
    update = SubmitField('Update')


# Create Login Form
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create User Form
class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(),
                                                          EqualTo('password_hash2', message='Passwords must match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
