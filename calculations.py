from typing import Tuple, Dict, Union
from numpy_financial import irr
import plotly.express as px
import plotly.graph_objects as go
import plotly
import json
from math import log10, floor, ceil

PLAN_1_MNTHLY_THRES = 1682
PLAN_2_MNTHLY_THRES = 2274
NI_PRIMARY_THRESH = 823


def calculate_income_less_tax(gross: float) -> Tuple[float, float]:
    inc_less_tax = 12570

    if gross <= inc_less_tax:
        inc_less_tax = gross
        annual_tax = 0
        return inc_less_tax, annual_tax

    if 50270 >= gross > 12570:
        inc_less_tax += 0.8 * (gross - 12570)

    elif 150000 >= gross > 50270:
        inc_less_tax += 0.8 * (50270 - 12570)
        inc_less_tax += 0.6 * (gross - 50270)

    elif gross > 150000:
        inc_less_tax += 0.8 * (50270 - 12570)
        inc_less_tax += 0.6 * (150000 - 50270)
        inc_less_tax += 0.55 * (gross - 150000)

    annual_tax = gross - inc_less_tax

    return inc_less_tax, annual_tax


def less_ni_contributions(gross: float) -> float:
    if gross < 12 * NI_PRIMARY_THRESH:
        ni_cont = 0

    elif gross <= 50270:
        ni_cont = 0.1325 * (gross - 12 * NI_PRIMARY_THRESH)

    else:
        ni_cont = 0.1325 * (50270 - 12 * NI_PRIMARY_THRESH)
        ni_cont += 0.0325 * (gross - 50270)

    return ni_cont


def less_student_loan(gross: float, plan: Union[int, None]) -> float:
    annual_student_loan = 0

    if plan is None or plan == 0:
        return annual_student_loan

    if plan == 1:
        if gross > 12 * PLAN_1_MNTHLY_THRES:
            annual_student_loan = 0.09 * (gross - 12 * PLAN_1_MNTHLY_THRES)

    elif plan == 2:
        if gross > 12 * PLAN_2_MNTHLY_THRES:
            annual_student_loan = 0.09 * (gross - 12 * PLAN_2_MNTHLY_THRES)

    return annual_student_loan


def less_pension_contributions(gross: float, pension_perc: float) -> float:
    pension_cont = gross * pension_perc
    return pension_cont


def disposable_income(gross: float, plan: Union[int, None], pension_perc: float) -> float:
    d_income = calculate_income_less_tax(gross)[0] - less_ni_contributions(gross) - less_student_loan(gross, plan) - \
               less_pension_contributions(gross, pension_perc)
    return d_income


def total_fixed_costs(fixed_costs):
    total_fc = 0
    for fc in fixed_costs:
        total_fc += fc.amount

    return total_fc


def deduct_fixed_costs(disposable: float, fixed_costs) -> float:
    personal_income = disposable - total_fixed_costs(fixed_costs)

    return personal_income


def calculate_saving_income(personal_inc: float, saving_perc: float) -> float:
    return personal_inc * saving_perc


def calculate_goal_targets(saving_inc: float, goals: Dict[str, float]) -> Dict[str, float]:
    goal_amount_dict = {}
    for k, v in goals:
        goal_amount_dict[k] = saving_inc * v

    return goal_amount_dict


def interest_required(monthly_payment: float, target: float, time_in_mths: int) -> Tuple[float, float]:
    v = [monthly_payment for i in range(time_in_mths)]
    v.append(-target)
    req_mth_ret = irr(v)
    req_ann_ret = (1 + req_mth_ret) ** 12 - 1
    return req_mth_ret, req_ann_ret


def round_sig(x, sig=3):
    return round(x, sig - int(floor(log10(abs(x)))) - 1)


def income_funnel(gross, disposable, personal, saving, annual=True):
    if annual:
        money = [gross, round_sig(disposable, 3), round_sig(personal, 3), round_sig(saving, 3)]

    else:
        money = [gross / 12, round(disposable / 12, 2), round(personal / 12, 2), round(saving / 12, 2)]

    data = dict(
        money=money,
        stage=["Gross Salary", "Take Home Pay", "Spending Money", "Income Saved"])

    fig = px.funnel(data, x='money', y='stage')

    fig.update_layout(
        font=dict(
            family="Verdana",
            size=18,
            color="Black"
        ),
        yaxis={'visible': False, 'showticklabels': True}
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def income_funnel_perc(gross, disposable, personal, saving):
    data = dict(
        money=[100, 100 * round(disposable / gross, 3), 100 * round(personal / gross, 3),
               100 * round(saving / gross, 3)],
        stage=["Gross salary", "% of Gross taken home", "% of Gross for personal spending", "% of Gross for saving"])

    fig = px.funnel(data, x='money', y='stage')

    fig.update_layout(
        yaxis_title="Your Income Funnel , % View",
        font=dict(
            family="Verdana",
            size=18,
            color="Black"
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def income_pie_chart(taxes_and_insurance, fixed_costs, personal, saving):
    values = [taxes_and_insurance, fixed_costs, personal, saving]
    labels = ["Taxes", "Expenses", "Spending Money", "Savings"]
    fig = px.pie(labels, values=values, hole=0.4,
                 names=labels, color=labels,
                 color_discrete_map={'Spending Money': 'seablue',
                                     'Taxes': 'darkred',
                                     'Expenses': 'magenta',
                                     'Savings': 'green'
                                     })
    fig.update_traces(
        title_font=dict(size=25, family='Verdana',
                        color='darkred'),
        hoverinfo='label+percent',
        textinfo='percent', textfont_size=20)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def return_perc_drops(gross, disposable, personal, saving):
    drop_one = round((1 - disposable / gross) * 100, 1)
    drop_two = round((1 - personal / disposable) * 100, 1)
    drop_three = round((1 - saving / personal) * 100, 1)
    return drop_one, drop_two, drop_three


def return_dashboard_cards_text(d1, d2, d3, inc_no_debt, inc_debt):
    c1_text = "After deducting taxes, national insurance contributions, and student loan repayments; your disposable income " \
              "is {}% of your gross income.".format(100 - round(d1, 2))

    c2_text = "{}% of your disposable income (take home pay) is used up on your monthly fixed expenses such as rent, utilities " \
              "and any other fixed expenses you've input on the My Finances page.".format(round(d2, 2))

    c3_text = "Out of the remaining income you have to spend on your lifestyle and save; {}% is being used up on your lifestyle " \
              "while the remaining {}% is saved.".format(round(d3, 2), 100 - round(d3, 2))

    c4_text = "Your disposable income with your current student debt is {}. If your debt was completely paid off your disposable " \
              "income would be {}. This is an increase of {}%.".format(inc_debt, inc_no_debt, round(100*((inc_no_debt/inc_debt) - 1), 2))

    return c1_text, c2_text, c3_text, c4_text


def linear_investing(goal, monthly_payment):
    linear_progression = [i * monthly_payment for i in range(1, ceil(goal / monthly_payment) + 1)]
    time_axis = [i for i in range(1, ceil(goal / monthly_payment) + 1)]
    return linear_progression, time_axis


def full_horizon_compound(monthly, interest, goal, total_horizon, annual=True):

    if annual:
        interest = (1 + interest)**(1/12) - 1

    progress = [monthly*(1+interest)]
    total = monthly

    month_count = 2

    while month_count <= total_horizon:
        donation = monthly * (1 + interest)**month_count
        progress.append(donation + progress[-1])
        total += donation
        month_count += 1

        if progress[-1] > goal > progress[-2]:
            time_to_reach_goal = len(progress)

    months = [i for i in range(1, len(progress)+1)]

    return progress, months, time_to_reach_goal


def plot_compound_and_standard(goal, total_horizon, interest, months, linear_progression, compound_progression, time_to_reach):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=linear_progression, fill='tozeroy'))  # fill down to xaxis
    fig.add_trace(go.Scatter(x=months, y=compound_progression, fill='tonexty'))  # fill to trace0 y
    fig.add_trace(go.Scatter(x=(0, total_horizon), y=(goal, goal)))  # fill to trace0 y
    fig.add_trace(go.Scatter(x=(time_to_reach, time_to_reach), y=(0, goal)))  # fill to trace0 y

    fig['data'][0]['showlegend']=True
    fig['data'][1]['showlegend']=True
    fig['data'][2]['showlegend']=True
    fig['data'][3]['showlegend'] = True
    fig['data'][0]['name']='With no interest'
    fig['data'][1]['name']='With {}% interest'.format(100 * interest)
    fig['data'][2]['name']='Target'
    fig['data'][3]['name'] = 'Time to reach goal'

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
