import os
import csv
from datetime import datetime

__fileDir = os.path.dirname(os.path.abspath(__file__))


def pars_micex_file(file_name):
    try:
        with open(file_name, newline='', encoding="cp1251", errors='ignore') as f:

            rows = csv.DictReader(f, delimiter=';', quotechar='|')
            for row in rows:

                if row['SECID'] != '':
                    print(row['SECID'] + ', ' + row['SHORTNAME'])
    except Exception as ex:
        print('Exception : ')
        input(ex)


if __name__ == '__main__':
    print(__fileDir)
    pars_micex_file('./download/securities_stock_shares_all.csv')
