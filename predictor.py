import logging
import os
import sys
import cx_Oracle
import json
import requests
import numpy as np
from pathlib import Path
from decimal import Decimal as D, ROUND_DOWN
import modelMaker as d

if len(sys.argv) < 2:
    print("Argument not found ")
    exit(0)
else:
    array_arg = sys.argv[1].split(',')

data = d.ModelMaker()

oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']
bot_url = 'http://localhost:8080/rest/data'
min_pwr_value = 5

global db_connect
# Число знаков в расчетных значениях
__accuracy = '0.00001'
source_path = '/models/archive/complex/best/'
file_name = 'weights_b25_150_3'


def change_percent(base, curr):
    try:
        return float(D((float(curr) - float(base)) / float(base)).quantize(D(__accuracy), rounding=ROUND_DOWN))

    except ZeroDivisionError:
        return 1


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir="/usr/local/src/instantclient_21_1",
                                     config_dir="/usr/local/src/instantclient_21_1/network/admin")
        connection = cx_Oracle.connect(oracle_login, oracle_password, "db202105041827_tp")
        return connection

    except cx_Oracle.Error as ex:
        logging.info('DB connection Error : ' + str(ex))


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

    return row['symbol'], row['date'], (np.asarray(prepared_data, dtype=np.float64)).reshape(1, 24), row['close'][-1]


def insert_signal_to_db(symbol, stock_exchange_name, date_rw, pwr, last_cost) -> str:
    query = ''
    descr = [[]]
    try:

        query = "SELECT a.descr FROM " + stock_exchange_name + "_DICT a WHERE a.symbol = '%s'" % symbol
        cursor = db_connect.cursor()
        cursor.execute(query)
        descr = cursor.fetchall()

        query = "INSERT INTO ADVISER_LOG VALUES ('%s', '%s', to_date('%s', 'dd/mm/yyyy'), %d, %f)" % \
                (symbol, stock_exchange_name, date_rw, pwr, last_cost)
        cursor.execute(query)
        db_connect.commit()

    except FileNotFoundError:
        logging.info("Can't insert : " + query)

    except cx_Oracle.Error as ex:
        logging.info('DB Error : ' + str(ex) + query)

    finally:
        if len(descr) > 0:
            return descr[0][0]
        else:
            return ''


def send_data_to_bot(d):
    try:
        response = requests.post(bot_url, json=d, timeout=5, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        print(json.dumps(d))
        logging.info('Data sent to bot successfuly. Status code : '+str(response.status_code))
        # Code here will only run if the request is successful
    except Exception as ex:
        logging.info("Can't sent data to bot : " + ex)
        exit(1)


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s', filename=__file__.replace('.py', '.log'),
                        level=logging.INFO)
    # Connect to DB
    db_connect = connect()
    # Load AI model
    model = data.model_loader(file_name, source_path)
    data = {}
    #for stock_exchange_name in array_arg:
    for stock_exchange_name in ['MOEX']:
        data = {}
        try:
            data_set = {'UP': [], 'DOWN': []}
            logging.info('----------------- ' + stock_exchange_name + ' ------------------------------')
            print('----------------------------------- ' + stock_exchange_name + ' ----------------------------')
            rows = get_data_from_table(stock_exchange_name)
            for json_row in rows:
                try:
                    symbol, date_rw, check_data, last_cost = get_check_data(json_row)
                except Exception as ex:
                    continue
                y_predicted = model.predict([check_data])[0]
                if y_predicted[0] > 0:
                    '''
                    print("Stock symbol {0} \t at date {1} found signal {2} recommended price {3}"
                          .format(symbol.rstrip(), date_rw, y_predicted, last_cost))
                    '''
                    symbol_description = insert_signal_to_db(symbol, stock_exchange_name, date_rw, y_predicted[0],
                                                             last_cost)

                    if y_predicted[0] > min_pwr_value:
                        data_set['UP'].append({'symbol': symbol, 'date': str(date_rw), 'pwr': int(y_predicted[0]),
                                               'price': str(last_cost), 'discr': symbol_description})
                elif y_predicted[2] > 0:
                    '''
                    print("Stock symbol {0} \t at date {1} found signal {2} recommended price {3}"
                          .format(symbol.rstrip(), date_rw, y_predicted, last_cost))
                    '''
                    symbol_description = insert_signal_to_db(symbol, stock_exchange_name, date_rw, y_predicted[2] * -1,
                                                             last_cost)

                    if y_predicted[2] > min_pwr_value:
                        data_set['DOWN'].append(
                            {'symbol': symbol, 'date': str(date_rw), 'pwr': int(y_predicted[2]) * -1,
                             'price': str(last_cost), 'discr': symbol_description})

            if len(data_set['UP']) > 0 or len(data_set['DOWN']) > 0:
                data["stock_exchange"] = stock_exchange_name
                data_set['DOWN'] = sorted(data_set['DOWN'], key=lambda k: k['pwr'])
                data_set['UP'] = sorted(data_set['UP'], key=lambda k: k['pwr'], reverse=True)
                data["data"] = data_set
                send_data_to_bot(data)

        except Exception as ex:
            logging.info('>> ' + stock_exchange_name + ' : ' + ex + ' : ')
            exit(1)
