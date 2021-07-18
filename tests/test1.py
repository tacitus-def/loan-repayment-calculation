#!/usr/bin/env -S python3

import sys, csv
import getopt

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

sys.path.append("..")

from modules import loancalc

def main():
    repayments = []
    percent = 17.7
    debt = 850000
    period = 5

    for y in range(2000, 2011):
        for m in range(1,13):
            date_text = "10.{0:02d}.{1:4d}".format(m, y)
            start = datetime.strptime(date_text, "%d.%m.%Y").date()
            end = start + relativedelta(months = period)
            (total, table) = loancalc.run(debt, percent / 100, start, period, repayments)
            last = table[-1]
            print(date_text, end.toordinal() - start.toordinal(), "{0:0.2f}".format(last[2]))

if __name__ == "__main__":
    main()

