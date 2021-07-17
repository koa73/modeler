import cx_Oracle
import os
import logging
from pathlib import Path
import re
from itertools import *

oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']
oracle_config_dir = "/usr/local/src/instantclient_21_1/network/admin/clone_db"
oracle_db = "db202106201548_tp"


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir="/usr/local/src/instantclient_21_1", config_dir=oracle_config_dir)
        connection = cx_Oracle.connect(oracle_login, oracle_password, oracle_db)
        return connection

    except cx_Oracle.Error as ex:
        print(ex)
        logging.info('DB connection Error : ' + str(ex))


# condition : "> 0" or "< 0" or "<> 0"
def get_all_pwr(condition):
    query = "SELECT pwr, count(pwr) from ARCHIVE where pwr %s GROUP BY pwr ORDER BY pwr ASC" % condition
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


def get_archive_values(r):
    if len(r) != 1:
        query = "SELECT pwr, last, open, close, high, low FROM ARCHIVE WHERE pwr in {range}".format(range=r)
    else:
        query = "SELECT pwr, last, open, close, high, low FROM ARCHIVE WHERE pwr = %s" % r

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


def save_to_db(pwr_str, sum_last, sum_open, count):

    query = "INSERT INTO ANALYZE VALUES ('%s', %f, %f, %d)" % \
            (pwr_str, sum_last, sum_open, count)
    try:
        cursor = db_connect.cursor()
        cursor.execute(query)
        db_connect.commit()

    except cx_Oracle.Error as ex:
        logging.info('DB Error : ' + str(ex) + query)


def get_top_value(row, inp_array, column, end):
    inp_array.append(row)
    return sorted(inp_array, key=lambda inp: inp[column],reverse=True)[:end]


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s',
                        filename='/usr/local/src/data_receiver/' + Path(__file__).stem + '.log',
                        level=logging.INFO)
    db_connect = connect()

    pwr_last_array = []
    pwr_open_array = []
    for condition in (">0", "<0"):
        pwr_list = get_all_pwr(condition)
        for i in pwr_list:
            pwr_comb = get_combination(pwr_list.keys(), i)
            for j in pwr_comb:

                # print("count %d, value : %d" % (i, len(pwr_comb)))

                rows = get_archive_values(j)
                sum_last = 0
                sum_open = 0

                count = len(rows)
                for row in rows:
                    sum_last = sum_last + count_profit(row[1], row[3], row[0])
                    sum_open = sum_open + count_profit(row[2], row[3], row[0])

                pwr_row = (re.sub(r'[()]|,\)$', '', str(j)), sum_last / count, sum_open / count, count)
                pwr_last_array = get_top_value(pwr_row, pwr_last_array, 1, 10)
                pwr_open_array = get_top_value(pwr_row, pwr_open_array, 2, 10)
                # save_to_db(re.sub(r'[()]|,\)$','', str(j)), sum_last / count, sum_open / count, count)
                # print("PWR: %s, Sum_last : %f, Sum_open : %f, Count : %d" % (re.sub(r'[()]|,\)$','', str(j)), sum_last / count, sum_open / count, count))
        print("------------------ Last ----------------------")
        print(pwr_last_array)
        print("-------------------Open ----------------------")
        print(pwr_open_array)

