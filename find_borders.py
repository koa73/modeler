import logging
import os
import sys
import cx_Oracle
import json
import requests
import numpy as np
from pathlib import Path
from datetime import datetime
from decimal import Decimal as D, ROUND_DOWN
import modelMaker as d


over = 0
if len(sys.argv) == 2:
    over = sys.argv[1]

data = d.ModelMaker()

oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']
oracle_config_dir = os.environ['TNS_ADMIN']
oracle_db = os.environ['ORACLE_DB']
oracle_lib = os.environ['LD_LIBRARY_PATH']
model_path = os.environ['MODEL_PATH']
log_path = os.environ['LOG_PATH']
model_file_name = 'weights_b25_150_3'
min_pwr_value = 1

global db_connect
# Число знаков в расчетных значениях
__accuracy = '0.00001'


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir=oracle_lib,
                                     config_dir=oracle_config_dir)
        connection = cx_Oracle.connect(oracle_login, oracle_password, oracle_db)
        return connection

    except cx_Oracle.Error as ex:
        logging.info('DB connection Error : ' + str(ex))


def change_percent(base, curr):
    try:
        return float(D((float(curr) - float(base)) / float(base)).quantize(D(__accuracy), rounding=ROUND_DOWN))

    except ZeroDivisionError:
        return 1


def get_data_from_table(stock_exchange):
    try:

        if db_connect:
            query = "SELECT aa FROM (SELECT JSON_OBJECT(KEY 'symbol' VALUE trim(symbol), " \
                    " KEY 'date' VALUE to_char(max(date_rw), 'dd/mm/yyyy')," \
                    " KEY 'open' VALUE JSON_ARRAYAGG( open ORDER BY date_rw ASC RETURNING VARCHAR2(100))," \
                    " KEY 'high' VALUE JSON_ARRAYAGG( high ORDER BY date_rw ASC RETURNING VARCHAR2(100))," \
                    " KEY 'low' VALUE JSON_ARRAYAGG( low ORDER BY date_rw ASC RETURNING VARCHAR2(100))," \
                    " KEY 'close' VALUE JSON_ARRAYAGG( close ORDER BY date_rw ASC RETURNING VARCHAR2(100))," \
                    " KEY 'volume' VALUE JSON_ARRAYAGG( volume ORDER BY date_rw ASC RETURNING VARCHAR2(100))) aa," \
                    " max(date_rw) ab FROM " + stock_exchange + "_STOCKS GROUP BY symbol) " \
                                                                "WHERE ab = (SELECT MAX(b.date_rw) FROM " + stock_exchange + "_STOCKS b)"
            cursor = db_connect.cursor()
            cursor.execute(query)

            return cursor.fetchall()

    except cx_Oracle.Error as ex:
        logging.info('DB Error : ' + str(ex))


def get_check_data(json_row):
    row = json.loads(json_row[0])
    prepared_data = []

    for i in range(1, len(row['open'])):
        prev = i - 1
        calc_row = [
            change_percent(row['close'][prev], row['open'][i]),  # C0
            change_percent(row['close'][prev], row['low'][i]),  # low_0
            change_percent(row['close'][prev], row['high'][i]),  # high_0
            change_percent(row['volume'][prev], row['volume'][i]),  # volume
            change_percent(row['open'][prev], row['open'][i]),  # C1
            change_percent(row['open'][i], row['low'][i]),  # low_1
            change_percent(row['open'][i], row['high'][i]),  # high
            change_percent(row['open'][i], row['close'][i]),  # close_current_1
        ]
        prepared_data.append(calc_row)

    return row['symbol'], row['date'], (np.asarray(prepared_data, dtype=np.float64)).reshape(1, 24), row['close'][-1], row['open'][-1]


def insert_to_prediction_log(symbol, date_rw, check_data, y_predicted, n):
    try:
        if db_connect:
            x = np.array2string(check_data, precision=5, separator=',')
            y = np.array2string(y_predicted, precision=2, separator=',')

            query = "INSERT INTO PREDICTION_LOG VALUES ('%s', to_date('%s', 'dd/mm/yyyy'), '%s', '%s', '%s')" % \
                    (symbol, date_rw, x, y, n)
            cursor = db_connect.cursor()
            cursor.execute(query)
            db_connect.commit()

    except cx_Oracle.Error as ex:
        logging.info('DB Error : ' + str(ex))


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s',
                        filename=log_path + Path(__file__).stem + '.log',
                        level=logging.INFO)
    # Connect to DB
    db_connect = connect()
    # Load AI model
    model = data.model_loader(model_file_name, model_path)
    result = {}
    for stock_exchange_name in ['NYSE', 'NASDAQ', 'AMEX', 'MOEX']:
        rows = get_data_from_table(stock_exchange_name)
        for json_row in rows:
            try:
                symbol, date_rw, check_data, last_cost, last_open = get_check_data(json_row)
                y_predicted = model.predict([check_data])[0]
                if (y_predicted[0] > 0):
                    result = data.find_zone_border_buy(model,last_open, last_cost, check_data)
                elif (y_predicted[2] > 0):
                    result = data.find_zone_border_sell(model, last_open, last_cost, check_data)
                #insert_to_prediction_log(symbol, date_rw, check_data, y_predicted, over)
                if (y_predicted[0] > 0 or y_predicted[2] > 0):
                    print('--------------------------------'+symbol+'---------------------------')
                    print(result)
            except Exception as ex:
                print(ex)
                continue
