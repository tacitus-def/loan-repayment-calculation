#!/usr/bin/env -S python3

import sys, csv
import getopt
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta

def monthly_payment(debt, percent_month, months):
    abc = ((1 + percent_month) ** months - 1)
    if abc == 0: return 0

    fraction = (percent_month * (1 + percent_month) ** months) / abc 
    return debt * fraction 

def get_days_number(year):
    return 366 if year % 4 == 0 and year % 100 != 0 or year % 400 == 0 else 365

def run(debt, percent, date_start, months, repayments = []):
    percent_month = percent / 12
    part = monthly_payment(debt, percent_month, months) 
    total = part * months
    result = debt
    by_month = {};
    table = []
    prev_date = date_start
    for repayment in repayments:
        row_date = repayment[0]
        date_diff = relativedelta(row_date, date_start)
        repayment.append(relativedelta(row_date - relativedelta(days=1), date_start).days + 1 if date_diff.days == 0 else date_diff.days)
        diff_months = date_diff.months + date_diff.years * 12
        if row_date.day == date_start.day: diff_months -= 1
        if diff_months not in by_month.keys(): by_month[diff_months] = []
        by_month[diff_months].append(repayment)
    total = 0
    month = 1
    overpayment = 0
    prev_year_days = get_days_number(date_start.year)
    while month <= months:
        rpa = by_month.get(month - 1)
        current_date = date_start + relativedelta(months = month)
        lmt = (current_date - prev_date).days
        year_days = get_days_number(current_date.year)
        correction_delta = (prev_year_days - year_days) / 2.38
        dt = (year_days + correction_delta) / 12
        lday = 0
        if rpa != None:
            atl = 0
            for rp in rpa:
                lday = rp[3] - lday
                rp_loan = result * percent_month * (lday) / dt - atl
                atl += rp_loan
                total += rp[1]
                rp_part = rp[1] - rp_loan
                result = result - rp_part
                if result <= 0:
                    rp_part += result
                    total -= rp[1]
                    rp[1] = rp_part + rp_loan
                    total += rp[1]
                    result = 0
                if rp[2] == 0:
                    part = monthly_payment(result, percent_month, months - month)
                elif rp[2] == 1:
                    sub_months = math.ceil(math.log(part/(part - percent_month * result), 1 + percent_month))
                    months = month + sub_months
                overpayment += rp_loan
                table.append( (month, rp[0], result, rp_loan, rp_part, rp[1], overpayment, part) )


        loan_month = result * percent_month * (lmt - lday) / dt
        part_month = part - loan_month

        if rpa == None:
            result = result - part_month
            if result <= 0:
                part_month += result
                result = 0
        else:
            part_month = 0
        total += loan_month + part_month
        overpayment += loan_month
        if loan_month + part_month != 0:
            table.append( (month, current_date, result, loan_month, part_month, 0, overpayment, loan_month + part_month) )
        prev_date = current_date

        month += 1
        prev_year_days = year_days
    return (total, table)
