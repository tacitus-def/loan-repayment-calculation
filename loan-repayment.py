#!/usr/bin/env -S python3

import sys, csv
import getopt

from datetime import datetime

from modules import loancalc

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
                    row_date = datetime.strptime(row[0], '%d.%m.%Y').date()
                    row_repayment = float(row[1])
                    row_type = int(row[2]) if len(row) >= 3 else 0
                    repayments.append([row_date, row_repayment, row_type])

    (total, table) = loancalc.run(debt, percent / 100, date_start, months, repayments)
    print("Debt: %9.2f" % (debt));
    print("Overpayment: %9.2f" % (total - debt));
    print("Total: %9.2f" % (total));

    if not no_print: 
        print("\n #\tDate      \t     Debt\t Interest\t Redempt.\t    Early\t  Payment\t     Over")
        for row in table:
            print("%02d\t%s\t%9.2f\t%9.2f\t%9.2f\t%9.2f\t%9.2f\t%9.2f" % (row[0], row[1].strftime('%d.%m.%Y'), row[2], row[3], row[4], row[5], row[7], row[6]))

if __name__ == "__main__":
    main(sys.argv[1:])

