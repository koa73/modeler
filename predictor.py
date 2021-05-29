import logging
import os
import cx_Oracle
import json
import numpy as np
from decimal import Decimal as D, ROUND_DOWN
import modelMaker as d


data = d.ModelMaker()

oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']

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
        logging.info('DB connection Error : '+str(ex))


def get_data_from_table(stock_exchange):

    try:
        if db_connect:
            query = "SELECT JSON_OBJECT(KEY 'symbol' VALUE symbol, KEY 'date' VALUE max(date_rw)," \
                    " KEY 'open' VALUE JSON_ARRAYAGG( open ORDER BY date_rw ASC RETURNING VARCHAR2(100))," \
                    " KEY 'high' VALUE JSON_ARRAYAGG( high ORDER BY date_rw ASC RETURNING VARCHAR2(100))," \
                    " KEY 'low' VALUE JSON_ARRAYAGG( low ORDER BY date_rw ASC RETURNING VARCHAR2(100))," \
                    " KEY 'close' VALUE JSON_ARRAYAGG( close ORDER BY date_rw ASC RETURNING VARCHAR2(100))," \
                    " KEY 'volume' VALUE JSON_ARRAYAGG( volume ORDER BY date_rw ASC RETURNING VARCHAR2(100)))" \
                    " FROM " + stock_exchange + "_STOCKS GROUP BY symbol"
            cursor = db_connect.cursor()
            cursor.execute(query)

            return cursor.fetchall()

    except cx_Oracle.Error as ex:
        logging.info('DB Error : '+str(ex))

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

    return row['symbol'], row['date'], (np.asarray(prepared_data, dtype=np.float64)).reshape(1, 24)




if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s', filename=__file__.replace('.py', '.log'),
                        level=logging.INFO)
    # Connect to DB
    db_connect = connect()
    # Load AI model
    model = data.model_loader(file_name, source_path)

    for stock_exchange_name in ['NYSE', 'NASDAQ']:
        try:
            logging.info('----------------- ' + stock_exchange_name + ' ------------------------------')
            print('----------------------------------- ' + stock_exchange_name + ' ----------------------------')
            rows = get_data_from_table(stock_exchange_name)
            for json_row in rows:
                symbol, date_rw, check_data = get_check_data(json_row)
                y_predicted = model.predict([check_data])[0]

                if(y_predicted[0] > 0 or y_predicted[2] > 0):
                    print("Stock symbol {0} \t at date {1} found signal {2}".format(symbol.rstrip(), date_rw, y_predicted))

        except Exception as ex:
            logging.info('>> ' + stock_exchange_name + ' : ' + str(ex))


