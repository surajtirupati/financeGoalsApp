from typing import Tuple, Dict, Union
from numpy_financial import irr

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

    if plan is None:
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


def interest_required(monthly_payment: float, target: float, time_in_mths: float) -> Tuple[float, float]:
    v = [monthly_payment for i in range(time_in_mths)]
    v.append(-target)
    req_mth_ret = irr(v)
    req_ann_ret = (1 + req_mth_ret) ** 12 - 1
    return req_mth_ret, req_ann_ret


print()
