#!/usr/bin/env -S python3

import sys, csv
import getopt
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta

def monthly_payment(debt, percent_month, months):
    fraction = (percent_month * (1 + percent_month) ** months) / ((1 + percent_month) ** months - 1)
    return round(debt * fraction, 2) 

def get_days_number(year):
    return 366 if year % 4 == 0 and year % 100 != 0 or year % 400 == 0 else 365

def calculate_total(debt, percent, date_start, months, repayments = []):
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
        repayment.append(date_diff)
        diff_months = date_diff.months + date_diff.years * 12
        if diff_months not in by_month.keys(): by_month[diff_months] = []
        by_month[diff_months].append(repayment)
    total = 0
    month = 1
    prev_year_days = get_days_number(date_start.year)
    while month <= months:
        rpa = by_month.get(month - 1)
        current_date = date_start + relativedelta(months = month)
        lmt = (current_date - prev_date).days
        year_days = get_days_number(current_date.year)
        dt = (year_days + (prev_year_days - year_days) / 2.38) / 12
        lday = 0
        if rpa != None:
            atl = 0
            for rp in rpa:
                lday = rp[3].days - lday
                rp_loan = round(result * percent_month * (lday) / dt, 2) - atl
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
                table.append( (month, rp[0], result, rp_loan, rp_part, rp[1]) )

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
        table.append( (month, current_date, result, loan_month, part_month, loan_month + part_month) )
        prev_date = current_date

        month += 1
        prev_year_days = year_days
    return (total, table)

def main(argv):
    repayments = []
    no_print = False
    try:
        opts, args = getopt.getopt(argv, "d:p:s:m:r:t")
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-d':
            debt = float(arg)
        elif opt == '-p':
            percent = float(arg)
        elif opt == '-s':
            date_start = datetime.strptime(arg, '%d.%m.%Y').date()
        elif opt == '-m':
            months = int(arg)
        elif opt == '-t':
            no_print = True
        elif opt == '-r':
            filename = arg
            with open(filename, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in reader:
                    row_date = datetime.strptime(row[0], '%d.%m.%Y')
                    row_repayment = float(row[1])
                    row_type = int(row[2]) if len(row) >= 3 else 0
                    repayments.append([row_date, row_repayment, row_type])

    (total, table) = calculate_total(debt, percent / 100, date_start, months, repayments)
    print("Debt: %9.2f" % (debt));
    print("Overpayment: %9.2f" % (total - debt));
    print("Total: %9.2f" % (total));

    if not no_print: 
        print("\n #\tDate      \t     Debt\t Interest\t Redempt.\t  Payment")
        for row in table:
            print("%02d\t%s\t%9.2f\t%9.2f\t%9.2f\t%9.2f" % (row[0] + 1, row[1].strftime('%d.%m.%Y'), row[2], row[3], row[4], row[5]))

if __name__ == "__main__":
    main(sys.argv[1:])

