import cx_Oracle
import os
import logging
import datetime
import sqlite3
import uuid
import re
from pathlib import Path
from itertools import *

oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']
oracle_config_dir = "/usr/local/src/instantclient_21_1/network/admin/clone_db"
oracle_db = "db202106201548_tp"
archive_db = os.environ['ARCHIVE_DB']


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir="/usr/local/src/instantclient_21_1", config_dir=oracle_config_dir)
        connection = cx_Oracle.connect(oracle_login, oracle_password, oracle_db)
        return connection

    except cx_Oracle.Error as ex:
        print(ex)
        logging.info('DB connection Error : ' + str(ex))


# Create condition date range for select, and start monday  date
# input any date
def this_week_range(d):
    star_date = (d - datetime.timedelta(d.weekday())).strftime('%d-%b-%Y')
    end_date = (d + datetime.timedelta(7 - d.weekday())).strftime('%d-%b-%Y')
    return "AND date_rw > '{start}' AND date_rw < '{end}'".format(start=star_date, end=end_date), star_date


# Return all mondays between start and end date
def next_monday(start, end):
    result = [start - datetime.timedelta(start.weekday())]
    while result[-1] < end:
        result.append(result[-1]+datetime.timedelta(7))
    return result


# condition : "> 0" or "< 0" or "<> 0"
def get_all_pwr(pwr_cond, date_range):
    query = "SELECT pwr, count(pwr) from ARCHIVE where pwr {pwr_cond} {date_range} GROUP BY pwr ORDER BY pwr ASC"\
        .format(pwr_cond=pwr_cond,date_range=date_range)
    try:
        cursor = db_connect.cursor()
        cursor.execute(query)
        return dict(cursor.fetchall())

    except cx_Oracle.Error as ex:
        logging.info('DB Error : ' + str(ex) + query)


def get_combination(input_list, chain_size):
    result = []

    for i in combinations(input_list, chain_size):
        result.append(i)
        #print(i, end=' ')  # ab ac ad bc bd cd
    return result


def get_archive_values(r, date_range):
    if len(r) != 1:
        query = "SELECT pwr, last, open, close, high, low FROM ARCHIVE WHERE pwr in {range} {date_range}"\
            .format(range=r, date_range=date_range)
    else:
        query = "SELECT pwr, last, open, close, high, low FROM ARCHIVE WHERE pwr = %s %s" % (r[0], date_range)

    try:
        cursor = db_connect.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    except cx_Oracle.Error as ex:

        logging.info('DB Error : ' + str(ex) + query)


def count_profit(base, close, pwr):
    if pwr > 0:
        result = (close/base-1)*100
    else:
        result = (base/close-1)*100
    return result


def save_to_db(start, rows):

    for row in rows:

        query = "INSERT INTO ANALYZE_m3 VALUES ('%s', '%s', %f, %f, %d, '%s')" % \
                (start, row[0], row[1], row[2], row[3], uuid.uuid5(uuid.NAMESPACE_DNS, start + row[0]))
        try:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            cur.close()

        except sqlite3.Error as ex:
            logging.info('Access to Sqlite DB error : ' + str(ex))



def get_top_value(row, inp_array, column, end):
    inp_array.append(row)
    return sorted(inp_array, key=lambda inp: inp[column],reverse=True)[:end]


def get_top_pwr_values(condition):

    last_array = []
    open_array = []
    pwr_list = get_all_pwr(condition, date_range)
    chain_size = len(pwr_list)
    if chain_size > 5:
        chain_size = 5
    for i in range(1, chain_size):
        pwr_comb = get_combination(pwr_list.keys(), i)
        print("count %d, value : %d" % (i, len(pwr_comb)))
        for j in pwr_comb:
            rows = get_archive_values(j, date_range)
            sum_last = 0
            sum_open = 0
            count = len(rows)
            for row in rows:
                sum_last = sum_last + count_profit(row[1], row[3], row[0])
                sum_open = sum_open + count_profit(row[2], row[3], row[0])

            pwr_row = (re.sub(r'[()]|,\)$', '', str(j)), sum_last / count, sum_open / count, count)
            last_array = get_top_value(pwr_row, last_array, 1, 10)
            open_array = get_top_value(pwr_row, open_array, 2, 10)
            # save_to_db(re.sub(r'[()]|,\)$','', str(j)), sum_last / count, sum_open / count, count)
            # print("PWR: %s, Sum_last : %f, Sum_open : %f, Count : %d" % (re.sub(r'[()]|,\)$','', str(j)), sum_last / count, sum_open / count, count))
    return last_array, open_array


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s',
                        # filename='/usr/local/src/data_receiver/log/' + Path(__file__).stem + '.log',
                        filename='./log/' + Path(__file__).stem + '.log',
                        level=logging.INFO)

    try:

        db_connect = connect()
        conn = sqlite3.connect(archive_db)

        monday_list = next_monday(datetime.date(2021, 5, 26), datetime.date(2021, 7, 12))
        for monday in monday_list:
            date_range, start_date = this_week_range(monday)
            print(">>>>>> "+monday.strftime('%d-%b-%Y'))

            # date_range, start_date = '', 'All'
            for c in (">0", "<0"):
                pwr_last_array, pwr_open_array = get_top_pwr_values(c)
                save_to_db(start_date, pwr_last_array)
                save_to_db(start_date, pwr_open_array)

                print("------------------ Last ----------------------")
                print(pwr_last_array)
                print("-------------------Open ----------------------")
                print(pwr_open_array)

    except Exception as ex:
        logging.info('>> Unsuccessful exit. Reason: ' + str(ex))
        exit(1)




