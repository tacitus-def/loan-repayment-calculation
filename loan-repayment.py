#!/usr/bin/env -S python3

import sys, csv
import getopt
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta

def monthly_payment(debt, percent_month, months):
    fraction = (percent_month * (1 + percent_month) ** months) / ((1 + percent_month) ** months - 1)
    return round(debt * fraction, 2) 

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
        by_month[diff_months] = repayment
    total = 0
    for month in range(months):
        rp = by_month.get(month)
        current_date = date_start + relativedelta(months = month + 1)
        lmt = (current_date - prev_date).days
        dt = lmt
        if rp != None:
            rp_loan = round(loan_month * (rp[2].days) / dt, 2)
            total += rp[1]
            rp_part = rp[1] - rp_loan
            result = result - rp_part
            if result <= 0:
                rp_part += result
                total -= rp[1]
                rp[1] = rp_part + rp_loan
                total += rp[1]
                result = 0
            lmt -= rp[2].days
            part = monthly_payment(result, percent_month, months - month - 1)
            table.append( (month, rp[0], result, rp_loan, rp_part, rp[1]) )

        loan_month = round(result * percent_month * lmt / dt, 2)
        part_month = part - loan_month
        if rp == None:
            result = result - part_month
        else:
            part_month = 0
        total += loan_month + part_month
        table.append( (month, current_date, result, loan_month, part_month, loan_month + part_month) )
        prev_date = current_date
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
                    repayments.append([row_date, row_repayment])

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

